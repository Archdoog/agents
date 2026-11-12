import contextlib
import importlib.util
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx

SCRIPT = Path(__file__).resolve().parents[1] / "skills/resolve-pr-comments/scripts/pr_comments.py"
SPEC = importlib.util.spec_from_file_location("pr_comments", SCRIPT)
cli = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cli)
HTTP_CLIENT = httpx.Client


class _CliTests(unittest.TestCase):
    def setUp(self):
        self.requests = []
        self.host = "github.com"
        self.failure = None
        self.resolved = True
        self.gh_calls = []

    def _gh(self, *args):
        self.gh_calls.append(args)
        if args[0] == "repo":
            return json.dumps(
                {
                    "nameWithOwner": "public/project",
                    "url": f"https://{self.host}/public/project",
                }
            )
        if args[0] == "auth":
            return "secret-test-token"
        if args[0] == "pr":
            return '{"number":42}'
        self.fail(f"Unexpected command: {args}")

    def _respond(self, request):
        self.requests.append(request)
        payload = json.loads(request.content)
        if self.failure == "http":
            return httpx.Response(403, json={"message": "Forbidden"})
        if self.failure == "network":
            raise httpx.ConnectError("Cannot connect", request=request)
        if "query" not in payload:
            return httpx.Response(201, json={"html_url": "https://github.com/comment/new"})
        query = payload["query"]
        variables = payload["variables"]
        if self.failure == "graphql":
            return httpx.Response(200, json={"errors": [{"message": "Denied"}], "data": {}})
        if "resolveReviewThread" in query:
            data = {"resolveReviewThread": {"thread": {"isResolved": self.resolved}}}
        elif "viewer{login}" in query:
            data = {
                "viewer": {"login": "contributor"},
                "repository": {
                    "pullRequest": {
                        "url": "https://github.com/public/project/pull/42",
                        "author": {"login": "contributor"},
                        "baseRefName": "stable",
                        "headRefName": "fix",
                        "headRefOid": "abc123",
                        "baseRepository": {"nameWithOwner": "public/project"},
                        "headRepository": None,
                    }
                },
            }
        else:
            second = variables["cursor"] is not None
            if second:
                self.assertEqual(variables["cursor"], "next-page")
            page = {"hasNextPage": not second, "endCursor": "next-page" if not second else None}
            comment = {
                "databaseId": 101 if second else 100,
                "author": None,
                "body": "Later comment" if second else "First comment",
                "url": "https://github.com/c/1",
            }
            if "node(id:" in query:
                if self.failure == "nested" and second:
                    return httpx.Response(500, json={})
                if self.failure == "cursor":
                    page = {"hasNextPage": True, "endCursor": "next-page"}
                data = {"node": {"comments": {"nodes": [comment], "pageInfo": page}}}
            else:
                if "reviewThreads(first:" in query:
                    field = "reviewThreads"
                    nodes = [
                        {
                            "id": "PRRT_last" if second else "PRRT_first",
                            "isResolved": False,
                            "isOutdated": not second,
                            "path": "a.py",
                            "line": None,
                        }
                    ]
                    if not second:
                        nodes.append({"id": "PRRT_done", "isResolved": True})
                elif "reviews(first:" in query:
                    field = "reviews"
                    nodes = [dict(comment, state="CHANGES_REQUESTED", commit={"oid": "abc123"})]
                else:
                    field = "comments"
                    nodes = [comment]
                data = {"repository": {"pullRequest": {field: {"nodes": nodes, "pageInfo": page}}}}
        return httpx.Response(200, json={"data": data})

    def _client(self, **kwargs):
        return HTTP_CLIENT(**kwargs, transport=httpx.MockTransport(self._respond))

    def _run(self, *args):
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.object(cli, "_gh", self._gh), patch.object(cli.httpx, "Client", self._client):
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                try:
                    code = cli._main(list(args))
                except SystemExit as error:
                    code = error.code
        return code, stdout.getvalue(), stderr.getvalue()

    def test_all_pages_and_deleted_authors_and_head_repository(self):
        code, output, error = self._run("list")
        self.assertEqual(code, 0, error)
        data = json.loads(output)
        self.assertEqual(data["pr"], 42)
        self.assertEqual(data["base_ref"], "stable")
        self.assertIsNone(data["head_repository"])
        self.assertEqual(len(data["unresolved_threads"]), 2)
        self.assertEqual(data["unresolved_threads"][-1]["thread_id"], "PRRT_last")
        self.assertEqual(len(data["unresolved_threads"][0]["comments"]), 2)
        self.assertEqual(data["unresolved_threads"][0]["reply_to"], 100)
        self.assertIsNone(data["unresolved_threads"][0]["comments"][0]["author"])
        self.assertEqual(len(data["top_level_comments"]), 2)
        self.assertEqual(len(data["reviews"]), 2)
        self.assertEqual(data["reviews"][0]["state"], "CHANGES_REQUESTED")
        self.assertEqual(len(self.requests), 11)

    def test_api_errors_emit_no_partial_feedback(self):
        for failure in ("http", "network", "graphql", "nested", "cursor"):
            with self.subTest(failure=failure):
                self.failure = failure
                code, output, error = self._run("list", "42")
                self.assertEqual(code, 1)
                self.assertEqual(output, "")
                self.assertNotIn("secret-test-token", error)
                self.assertTrue(error)

    def test_inline_file_body_is_literal(self):
        body = 'Use `value` and $(touch injected).\nSecond line with "quotes".\n'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "reply.txt"
            path.write_text(body, encoding="utf-8")
            code, output, error = self._run(
                "reply", "42", "--comment", "123", "--body-file", str(path)
            )
        self.assertEqual(code, 0, error)
        self.assertEqual(output.strip(), "https://github.com/comment/new")
        self.assertEqual(
            self.requests[-1].url.path, "/repos/public/project/pulls/42/comments/123/replies"
        )
        self.assertEqual(json.loads(self.requests[-1].content), {"body": body})

    def test_enterprise_rest_and_graphql_and_authentication(self):
        for host, prefix in (("github.com", ""), ("github.example", "/api/v3")):
            with self.subTest(host=host):
                self.host = host
                code, _, error = self._run("reply", "42", "--top", "--body", "An answer.")
                self.assertEqual(code, 0, error)
                self.assertEqual(
                    self.requests[-1].url.path, prefix + "/repos/public/project/issues/42/comments"
                )
                self.assertEqual(
                    self.requests[-1].headers["Authorization"], "Bearer secret-test-token"
                )
                self.assertIn(("auth", "token", "--hostname", host), self.gh_calls)
                code, output, error = self._run("resolve", "PRRT_example")
                self.assertEqual(code, 0, error)
                self.assertEqual(output.strip(), "true")
                expected = "/graphql" if host == "github.com" else "/api/graphql"
                self.assertEqual(self.requests[-1].url.path, expected)
                self.assertEqual(
                    self.requests[-1].url.host, "api.github.com" if host == "github.com" else host
                )

    def test_invalid_arguments_and_bodies_do_not_access_github(self):
        cases = [
            ("list", "bad"),
            ("reply", "0", "--top", "--body", "text"),
            ("reply", "1", "--body", "text"),
            ("resolve", "bad"),
            ("reply", "1", "--top", "--body", " "),
            ("reply", "1", "--top", "--body-file", "/missing"),
            ("reply", "1", "--top", "--comment", "2", "--body", "text"),
        ]
        for case in cases:
            with self.subTest(case=case):
                code, _, _ = self._run(*case)
                self.assertNotEqual(code, 0)
        self.assertEqual(self.gh_calls, [])
        self.assertEqual(self.requests, [])

    def test_failed_resolution_does_not_claim_success(self):
        self.resolved = False
        code, output, error = self._run("resolve", "PRRT_example")
        self.assertEqual(code, 1)
        self.assertEqual(output, "")
        self.assertIn("did not resolve", error)

    def test_authentication_failure_does_not_expose_stderr(self):
        with patch.object(
            cli, "_gh", side_effect=subprocess.CalledProcessError(1, "gh", stderr="secret")
        ):
            with (
                contextlib.redirect_stdout(io.StringIO()),
                contextlib.redirect_stderr(io.StringIO()) as stderr,
            ):
                self.assertEqual(cli._main(["list", "42"]), 1)
        self.assertNotIn("secret", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
