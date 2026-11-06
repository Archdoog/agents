"""The command line: exit codes, JSON shape, and `check` on a real git repo."""

import io
import json
import os
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

from writing_for_code import rules
from writing_for_code.cli import main
from writing_for_code.surfaces import SURFACES


def run(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        try:
            rc = main(argv)
        except SystemExit as exc:
            rc = exc.code
    return rc, out.getvalue()


class Lint(unittest.TestCase):
    def write(self, text, suffix=".md"):
        handle = tempfile.NamedTemporaryFile("w", suffix=suffix, delete=False)
        handle.write(text)
        handle.close()
        self.addCleanup(os.unlink, handle.name)
        return handle.name

    def test_errors_exit_one(self):
        self.assertEqual(run(["lint", self.write("It didn't work.\n")])[0], 1)

    def test_warnings_alone_exit_zero(self):
        path = self.write("The scout is reading the board.\n")
        self.assertEqual(run(["lint", path])[0], 0)
        self.assertEqual(run(["lint", path, "-W"])[0], 1)

    def test_missing_file_exits_two(self):
        self.assertEqual(run(["lint", "/nonexistent/nope.md"])[0], 2)

    def test_no_files_exits_two(self):
        self.assertEqual(run(["lint"])[0], 2)

    def test_no_command_exits_two(self):
        self.assertEqual(run([])[0], 2)

    def test_json(self):
        path = self.write("It didn't work.\n")
        rc, out = run(["lint", path, "--json"])
        payload = json.loads(out)
        self.assertEqual(payload["errors"], 1)
        self.assertEqual(payload["files"][path]["surface"], "doc")
        self.assertEqual(payload["files"][path]["findings"][0]["code"], "STE003")

    def test_surface_from_file_name(self):
        path = os.path.join(tempfile.mkdtemp(), "README.md")
        with open(path, "w") as handle:
            handle.write("Fine.\n")
        self.addCleanup(os.unlink, path)
        payload = json.loads(run(["lint", path, "--json"])[1])
        self.assertEqual(payload["files"][path]["surface"], "readme")


class Comments(unittest.TestCase):
    def test_lint_runs_on_comment_text(self):
        path = os.path.join(tempfile.mkdtemp(), "a.py")
        with open(path, "w") as handle:
            handle.write("x = 1\n# We utilize this; it didn't work.\ny = 2\n")
        self.addCleanup(os.unlink, path)
        rc, out = run(["comments", path, "--json"])
        block = json.loads(out)[0]
        self.assertEqual(rc, 1)
        self.assertEqual(block["line"], 2)
        self.assertIn("STE002", [f["code"] for f in block["lint"]])
        self.assertEqual({f["line"] for f in block["lint"]}, {2})

    def test_flags_alone_exit_zero(self):
        path = os.path.join(tempfile.mkdtemp(), "a.py")
        with open(path, "w") as handle:
            handle.write("# ==========\nx = 1\n")
        self.addCleanup(os.unlink, path)
        self.assertEqual(run(["comments", path])[0], 0)


class Rules(unittest.TestCase):
    def test_every_surface_prints(self):
        for name in SURFACES:
            self.assertEqual(run(["rules", "--surface", name])[0], 0, name)

    def test_each_surface_has_its_guide(self):
        skill = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        for name, surface in SURFACES.items():
            path = os.path.join(skill, "surfaces", surface.guide)
            self.assertTrue(os.path.isfile(path), f"{name}: {path}")

    def test_codes_are_unique_and_surfaces_exist(self):
        for code, r in rules.REGISTRY.items():
            self.assertEqual(code, r.code)
            for surface in r.surfaces or ():
                self.assertIn(surface, SURFACES, code)


class Check(unittest.TestCase):
    def setUp(self):
        self.repo = tempfile.mkdtemp()
        self.cwd = os.getcwd()
        os.chdir(self.repo)
        self.addCleanup(os.chdir, self.cwd)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.write("old.py", "# It didn't work; old comment.\nx = 1\n")
        self.write("README.md", "Old text didn't change.\n")
        self.git("add", ".")
        self.git("commit", "-q", "-m", "Start")
        self.git("checkout", "-q", "-b", "feature")

    def git(self, *args):
        subprocess.run(["git", *args], check=True, capture_output=True)

    def write(self, name, text):
        with open(name, "w") as handle:
            handle.write(text)

    def test_only_new_lines_and_branch_commits_count(self):
        self.write("old.py", "# It didn't work; old comment.\nx = 1\n# Fine comment.\ny = 2\n")
        self.write("README.md", "Old text didn't change.\n\nNew text is fine.\n")
        self.git("commit", "-q", "-am", "Added things.")
        rc, out = run(["check", "--diff", "main", "--json"])
        payload = json.loads(out)
        self.assertEqual(rc, 1)
        self.assertEqual([b["line"] for b in payload["comments"]], [3])
        self.assertEqual(payload["files"]["README.md"]["findings"], [])
        (commit_findings,) = payload["commits"].values()
        self.assertIn("COMMIT002", [f["code"] for f in commit_findings])

    def test_clean_branch_exits_zero(self):
        self.write("new.py", "# Retry once on a timeout.\nx = 1\n")
        self.git("add", ".")
        self.git("commit", "-q", "-m", "Retry once on a timeout")
        self.assertEqual(run(["check", "--diff", "main"])[0], 0)

    def test_bad_ref_exits_two(self):
        self.assertEqual(run(["check", "--diff", "no-such-ref"])[0], 2)


if __name__ == "__main__":
    unittest.main()
