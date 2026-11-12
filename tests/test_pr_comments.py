import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPTS = Path(__file__).resolve().parents[1] / 'skills/resolve-pr-comments/scripts'
FAKE_GH = '''#!/usr/bin/env python3
import json
import os
from pathlib import Path
import sys

args = sys.argv[1:]
with open(os.environ['GH_LOG'], 'a') as log:
    log.write(json.dumps(args) + '\\n')

def emit(value):
    print(json.dumps(value))

def value(prefix):
    return next((arg[len(prefix):] for arg in args if arg.startswith(prefix)), '')

if args[:2] == ['repo', 'view']:
    emit({'nameWithOwner': 'public/project', 'url': 'https://github.example/public/project'})
elif args[:2] == ['pr', 'view']:
    print('42')
elif 'graphql' in args:
    query = value('query=')
    if os.environ.get('FAIL_API'):
        print('API permission error', file=sys.stderr)
        sys.exit(1)
    if 'resolveReviewThread' in query:
        emit({'data': {'resolveReviewThread': {'thread': {
            'isResolved': not bool(os.environ.get('FALSE_RESOLUTION'))}}}})
    elif 'viewer{login}' in query:
        emit({'data': {'viewer': {'login': 'contributor'}, 'repository': {'pullRequest': {
            'url': 'https://github.example/public/project/pull/42',
            'author': {'login': 'contributor'}, 'baseRefName': 'stable',
            'headRefName': 'fix', 'headRefOid': 'abc123',
            'baseRepository': {'nameWithOwner': 'public/project'},
            'headRepository': {'nameWithOwner': 'contributor/project'}}}}})
    else:
        assert '--paginate' in args and '--slurp' in args
        if 'node(id:' in query:
            if os.environ.get('FAIL_NESTED'):
                sys.exit(1)
            emit([{'data': {'node': {'comments': {'nodes': [
                {'databaseId': 100 + n, 'author': None, 'body': f'comment {n}',
                 'url': f'https://github.example/comment/{n}'}]}}}} for n in range(2)])
        else:
            if 'reviewThreads(first:' in query:
                field = 'reviewThreads'
                nodes = [{'id': 'PRRT_first', 'isResolved': False, 'isOutdated': True,
                          'path': 'a.py', 'line': None},
                         {'id': 'PRRT_resolved', 'isResolved': True},
                         {'id': 'PRRT_last', 'isResolved': False, 'isOutdated': False,
                          'path': 'b.py', 'line': 12}]
            elif 'reviews(first:' in query:
                field = 'reviews'
                nodes = [{'author': {'login': 'reviewer'}, 'body': 'Please fix this.',
                          'url': 'https://github.example/review/1', 'state': 'CHANGES_REQUESTED',
                          'commit': {'oid': 'abc123'}}]
            else:
                field = 'comments'
                nodes = [{'author': {'login': 'reader'}, 'body': f'question {n}',
                          'url': f'https://github.example/issuecomment/{n}'} for n in range(2)]
            emit([{'data': {'repository': {'pullRequest': {field: {'nodes': [node]}}}}}
                  for node in nodes])
else:
    print('https://github.example/comment/new')
'''


class ScriptTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        fake = self.root / 'gh'
        fake.write_text(FAKE_GH)
        fake.chmod(0o755)
        self.log = self.root / 'calls.jsonl'
        self.env = dict(os.environ, PATH=f'{self.root}:{os.environ["PATH"]}', GH_LOG=str(self.log))

    def run_script(self, name, *args, **env):
        return subprocess.run(['bash', str(SCRIPTS / name), *args], cwd=self.root,
                              env=dict(self.env, **env), capture_output=True, text=True)

    def calls(self):
        return [json.loads(line) for line in self.log.read_text().splitlines()] if self.log.exists() else []

    def test_full_feedback_and_fork_metadata(self):
        result = self.run_script('pr-threads.sh')
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data['pr'], 42)
        self.assertEqual(data['base_ref'], 'stable')
        self.assertEqual(data['head_repository'], 'contributor/project')
        self.assertEqual(len(data['unresolved_threads']), 2)
        self.assertEqual(data['unresolved_threads'][-1]['thread_id'], 'PRRT_last')
        self.assertEqual(len(data['unresolved_threads'][0]['comments']), 2)
        self.assertEqual(data['unresolved_threads'][0]['reply_to'], 100)
        self.assertIsNone(data['unresolved_threads'][0]['comments'][0]['author'])
        self.assertEqual(len(data['top_level_comments']), 2)
        self.assertEqual(data['reviews'][0]['state'], 'CHANGES_REQUESTED')
        for call in self.calls():
            if call[0] == 'api':
                self.assertEqual(call[1:3], ['--hostname', 'github.example'])

    def test_api_failure_has_no_partial_output(self):
        for env in ({'FAIL_API': '1'}, {'FAIL_NESTED': '1'}):
            result = self.run_script('pr-threads.sh', '42', **env)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, '')

    def test_inline_body_file_is_literal(self):
        body = 'Use `value` and $(touch injected).\nSecond line with "quotes".'
        path = self.root / 'reply.txt'
        path.write_text(body)
        result = self.run_script('reply.sh', '42', '123', '--body-file', str(path))
        self.assertEqual(result.returncode, 0, result.stderr)
        call = self.calls()[-1]
        self.assertIn('repos/public/project/pulls/42/comments/123/replies', call)
        self.assertIn('body=' + body, call)
        self.assertFalse((self.root / 'injected').exists())

    def test_top_level_reply(self):
        result = self.run_script('reply.sh', '--top', '42', 'An answer.')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('repos/public/project/issues/42/comments', self.calls()[-1])

    def test_invalid_arguments_do_not_call_github(self):
        cases = [('pr-threads.sh', 'not-a-number'), ('pr-threads.sh', '1', '2'),
                 ('reply.sh', '42', '1', ''), ('reply.sh', '--top', '-1', 'text'),
                 ('reply.sh', '--top', '1', '  '), ('reply.sh', '1'),
                 ('reply.sh', '1', '2', '--body-file', '/missing'),
                 ('resolve.sh', 'wrong'), ('resolve.sh', 'PRRT_one', 'extra')]
        for case in cases:
            with self.subTest(case=case):
                result = self.run_script(*case)
                self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.calls(), [])

    def test_resolution_requires_true_state(self):
        result = self.run_script('resolve.sh', 'PRRT_example')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), 'true')
        result = self.run_script('resolve.sh', 'PRRT_example', FALSE_RESOLUTION='1')
        self.assertNotEqual(result.returncode, 0)
        result = self.run_script('resolve.sh', 'PRRT_example', FAIL_API='1')
        self.assertNotEqual(result.returncode, 0)


if __name__ == '__main__':
    unittest.main()
