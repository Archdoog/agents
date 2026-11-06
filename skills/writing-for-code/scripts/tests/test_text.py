"""Masking: quoted material must never produce a finding."""

import unittest

from .helpers import codes


class Masking(unittest.TestCase):
    def test_fenced_code(self):
        self.assertEqual(codes("Text is fine.\n\n```\nutilize; didn't\n```\n"), [])

    def test_tilde_fence(self):
        self.assertEqual(codes("Text is fine.\n\n~~~\nutilize; didn't\n~~~\n"), [])

    def test_inline_code(self):
        self.assertEqual(codes("Prefer `utilize` over nothing."), [])

    def test_inline_code_wrapped_across_lines(self):
        self.assertEqual(codes("Write `perform an\nanalysis of the log` here."), [])

    def test_blockquote(self):
        text = "Our note is fine.\n\n> It is important to note that it didn't work.\n"
        self.assertEqual(codes(text), [])

    def test_frontmatter(self):
        text = "---\nname: thing\ndescription: Utilize the seamless parser\n---\n\nFine.\n"
        self.assertEqual(codes(text), [])

    def test_frontmatter_only_at_top(self):
        self.assertIn("STE005", codes("Fine here.\n\n---\n\nUtilize the parser.\n"))

    def test_url_and_link_target(self):
        self.assertEqual(codes("See [the spec](https://example.com/utilize-seamless) here."), [])

    def test_bare_url(self):
        self.assertEqual(codes("Read https://example.com/it-didnt-commence now."), [])

    def test_html_comment(self):
        self.assertEqual(codes("<!-- utilize; didn't -->\nFine.\n"), [])

    def test_html_tag(self):
        self.assertEqual(codes('<img src="seamless.png" alt="logo">\n\nFine.\n'), [])

    def test_indented_code_block(self):
        text = "Run the gate:\n\n    just pre-pr --utilize; didn't\n\nThen push.\n"
        self.assertEqual(codes(text), [])

    def test_wrapped_list_item_is_not_code(self):
        self.assertIn("STE005", codes("- The parser reads it\n  and utilizes the cache.\n"))

    def test_off_switch(self):
        for name in ("writing-for-code", "ste-lint"):
            text = f"<!-- {name}: off -->\nUtilize the seamless thing.\n<!-- {name}: on -->\n"
            self.assertEqual(codes(text), [], name)

    def test_github_actions_expression(self):
        self.assertEqual(codes("Run for ${{ matrix.utilize }} now."), [])

    def test_quoted_text(self):
        self.assertEqual(codes('Do not write "I hope this helps" or “didn\'t”.'), [])
        self.assertIn("STE003", codes('The "parser" didn\'t start.'))

    def test_command_line_is_quoted(self):
        self.assertEqual(codes("Usage:\n./install.sh --utilize; didn't\n"), [])

    def test_aligned_columns_are_a_table_not_a_sentence(self):
        text = "\n".join(f"--flag-{n}     " + " ".join(["word"] * 10) for n in range(4))
        self.assertNotIn("STE001", codes(text))

    def test_double_space_after_a_period_stays_prose(self):
        text = "First sentence.  " + " ".join(["word"] * 30) + "."
        self.assertIn("STE001", codes(text))


if __name__ == "__main__":
    unittest.main()
