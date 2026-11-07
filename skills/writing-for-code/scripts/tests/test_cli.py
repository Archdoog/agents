"""Check CLI reports and input failures without changing the user's files."""

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from writing_for_code.cli import main


class CliTests(unittest.TestCase):
    def call(self, *args, stdin=''):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), patch('sys.stdin', io.StringIO(stdin)):
            status = main(list(args))
        return status, out.getvalue(), err.getvalue()

    def test_stdin_success(self):
        self.assertEqual(self.call('lint', '-', stdin='Read the value.')[0], 0)

    def test_stdin_failure(self):
        status, out, _ = self.call('lint', '-', '--json', stdin='One; two.')
        self.assertEqual(status, 1)
        self.assertEqual(json.loads(out)['findings'][0]['code'], 'semicolon')

    def test_warning_exit(self):
        self.assertEqual(self.call('lint', '-', stdin='Utilize the cache.')[0], 0)
        self.assertEqual(self.call('lint', '-', '--warnings-as-errors', stdin='Utilize the cache.')[0], 1)

    def test_invalid_usage_json(self):
        for args in [('lint',), ('lint', '-', '--surface', 'bad'), ('wrong',)]:
            with self.subTest(args=args):
                status, out, err = self.call(*args, '--json')
                self.assertEqual(status, 2)
                self.assertTrue(json.loads(out)['errors'])
                self.assertEqual(err, '')

    def test_rules_json(self):
        status, out, _ = self.call('rules', '--json')
        self.assertEqual(status, 0)
        self.assertIn('semicolon', {r['id'] for r in json.loads(out)['rules']})

    def test_missing_paths(self):
        with tempfile.TemporaryDirectory() as temp:
            for command in ['lint', 'comments']:
                status, out, _ = self.call(command, str(Path(temp) / 'missing.py'), '--json')
                self.assertEqual(status, 2)
                self.assertTrue(json.loads(out)['errors'])

    def test_unmatched_glob(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(self.call('lint', temp + '/*.missing', '--json')[0], 2)

    def test_mixed_inputs(self):
        with tempfile.TemporaryDirectory() as temp:
            file = Path(temp) / 'ok.md'
            file.write_text('One; two.')
            status, out, _ = self.call('lint', str(file), str(file) + '.missing', '--json')
            self.assertEqual(status, 2)
            result = json.loads(out)
            self.assertTrue(result['findings'])
            self.assertTrue(result['errors'])

    def test_permission_error(self):
        with tempfile.TemporaryDirectory() as temp:
            file = Path(temp) / 'locked.md'
            file.write_text('Text.')
            with patch.object(Path, 'open', side_effect=PermissionError('Denied')):
                status, out, _ = self.call('lint', str(file), '--json')
            self.assertEqual(status, 2)
            self.assertTrue(json.loads(out)['errors'])

    def test_comments_stdin_rejected(self):
        self.assertEqual(self.call('comments', '-', '--json')[0], 2)

    def test_unsupported_comments(self):
        with tempfile.TemporaryDirectory() as temp:
            file = Path(temp) / 'x.unknown'
            file.write_text('Data.')
            self.assertEqual(self.call('comments', str(file), '--json')[0], 2)

    def test_crlf_coordinates(self):
        with tempfile.TemporaryDirectory() as temp:
            file = Path(temp) / 'x.md'
            file.write_bytes(b'First.\r\n\r\nOne; two.\r\n')
            status, out, _ = self.call('lint', str(file), '--json')
            item = json.loads(out)['findings'][0]
            self.assertEqual((status, item['line'], item['column']), (1, 3, 4))
