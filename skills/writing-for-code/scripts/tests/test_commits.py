"""Commit message rules."""

import unittest

from .helpers import codes, first


def commit(text):
    return codes(text, "commit")


class Commits(unittest.TestCase):
    def test_clean_commit(self):
        msg = ("Cache decoded routes for one hour\n\n"
               "Decoding is the slowest step on cold start.\n\n"
               "Co-Authored-By: Someone <someone@example.com>\n")
        self.assertEqual(commit(msg), [])

    def test_subject_length(self):
        self.assertIn("COMMIT001", commit("Add " + "x" * 80))

    def test_subject_period(self):
        self.assertIn("COMMIT002", commit("Add the cache."))
        self.assertNotIn("COMMIT002", commit("Add the cache..."))

    def test_subject_mood(self):
        for subject in ("Added the cache", "Fixes the crash", "Updating docs",
                        "parser: simplified the loop", "fix(parser): removed dead code"):
            self.assertIn("COMMIT003", commit(subject), subject)
        for subject in ("Add the cache", "parser: fix the loop", "feat!: drop Python 3.7",
                        "Embed the font"):
            self.assertNotIn("COMMIT003", commit(subject), subject)

    def test_subject_separator(self):
        self.assertIn("COMMIT004", commit("Add the cache\nBody line.\n"))

    def test_body_line_length(self):
        long_line = " ".join(["word"] * 16) + "."
        self.assertIn("COMMIT005", commit(f"Add the cache\n\n{long_line}\n"))

    def test_body_exemptions(self):
        url = "https://example.com/" + "a" * 80
        trailer = "Co-Authored-By: " + "N" * 70 + " <n@example.com>"
        self.assertNotIn("COMMIT005", commit(f"Add the cache\n\nSee {url}\n\n{trailer}\n"))

    def test_git_comment_lines_are_ignored(self):
        msg = "Add the cache\n\n# Please enter the commit message; didn't.\n"
        self.assertEqual(commit(msg), [])

    def test_self_reference(self):
        self.assertIn("SLOP009", commit("This commit adds a cache"))

    def test_commit_rules_stay_on_the_commit_surface(self):
        self.assertNotIn("COMMIT002", codes("Add the cache.", "doc"))

    def test_position(self):
        f = first("Add the cache.", "COMMIT002", "commit")
        self.assertEqual((f.line, f.col), (1, 14))


if __name__ == "__main__":
    unittest.main()
