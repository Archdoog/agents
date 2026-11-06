"""The comment scanner and its flags, ported from the comment-extract suite."""

import unittest

from writing_for_code.comments import analyze, style_for


def blocks(text, style, path="x"):
    return [b.as_dict() for b in analyze(path, text, style)]


def flags_at(text, style, line):
    for b in blocks(text, style):
        if b["line"] == line:
            return b["flags"]
    raise AssertionError(f"no block at line {line}")


class Tokenizer(unittest.TestCase):
    def test_slashes_inside_string_are_not_a_comment(self):
        out = blocks('const u = "https://x.io//y";\n// real\n', "c-family")
        self.assertEqual([b["line"] for b in out], [2])

    def test_escaped_quote_does_not_open_a_string(self):
        out = blocks("const s = 'it\\'s';\n// after\n", "c-family")
        self.assertEqual([b["text"] for b in out], ["after"])

    def test_rust_lifetime_is_not_a_string(self):
        out = blocks("fn f<'a>(s: &'a str) {\n    // note\n}\n", "c-family")
        self.assertEqual([b["text"] for b in out], ["note"])

    def test_shell_hash_inside_braces_is_not_a_comment(self):
        out = blocks('echo "${#var}" # count\n', "hash")
        self.assertEqual([b["text"] for b in out], ["count"])
        self.assertTrue(out[0]["trailing"])

    def test_shebang_is_dropped(self):
        out = blocks("#!/bin/bash\n# body\n", "hash")
        self.assertEqual([b["text"] for b in out], ["body"])

    def test_python_docstring_is_doc_and_inline_triple_quote_is_data(self):
        src = 'def f():\n    """Doc."""\n    x = """data"""\n    # c\n'
        out = blocks(src, "python")
        self.assertEqual([(b["kind"], b["text"]) for b in out], [("doc", "Doc."), ("line", "c")])

    def test_adjacent_line_comments_group_by_indent(self):
        src = "// a\n// b\n  // c\n"
        out = blocks(src, "c-family")
        self.assertEqual([b["text"] for b in out], ["a\nb", "c"])

    def test_block_comment_star_prefix_is_stripped(self):
        out = blocks("/**\n * Doc line.\n */\n", "c-family")
        self.assertEqual(out[0]["kind"], "doc")
        self.assertEqual(out[0]["text"], "Doc line.")

    def test_triple_slash_doc_lines_group_into_one_doc_block(self):
        src = "/// Parses `s`.\n///\n/// # Errors\n/// Returns Err on empty input.\npub fn parse() {}\n"
        out = blocks(src, "c-family")
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["kind"], "doc")
        self.assertEqual(out[0]["text"], "Parses `s`.\n\n# Errors\nReturns Err on empty input.")
        self.assertIn("long", out[0]["flags"])

    def test_rust_inner_doc_on_line_one_is_not_a_shebang(self):
        out = blocks("//! Crate docs.\nfn f() {}\n", "c-family")
        self.assertEqual([(b["kind"], b["text"]) for b in out], [("doc", "Crate docs.")])

    def test_inner_block_doc_strips_the_bang(self):
        out = blocks("/*! inner */\nfn f() {}\n", "c-family")
        self.assertEqual(out[0]["text"], "inner")

    def test_swift_doc_line_and_plain_line_do_not_merge(self):
        out = blocks("/// Returns the count.\n// plain\nfunc f() {}\n", "c-family")
        self.assertEqual([b["kind"] for b in out], ["doc", "line"])

    def test_html_comment(self):
        out = blocks("<p>x</p>\n<!-- note -->\n", "html")
        self.assertEqual([b["text"] for b in out], ["note"])


class Flags(unittest.TestCase):
    def test_decision_history_sequence(self):
        src = '"""Per ADR-001 we chose regex. Previously a loop. First, strip. Then, split."""\n'
        f = flags_at(src, "python", 1)
        for name in ("decision", "history", "sequence"):
            self.assertIn(name, f)

    def test_restates_next_line(self):
        self.assertIn("restates", flags_at("# strip the header\nheader = text.strip()\n", "python", 1))

    def test_next_code_skips_full_comment_lines_but_not_trailing_ones(self):
        src = "/* loop */\nfor (x of xs) y += x; // trailing\nreturn y;\n"
        b = blocks(src, "c-family")[0]
        self.assertTrue(b["next_code"].startswith("for (x of xs)"))

    def test_dead_code(self):
        src = "# x = re.split(',', s);\n# return x\n"
        self.assertIn("dead-code", flags_at(src, "python", 1))

    def test_prose_with_a_call_is_not_dead_code(self):
        self.assertNotIn("dead-code", flags_at("# call parse() before use\nx = 1\n", "python", 1))

    def test_banner_and_hedge(self):
        f = flags_at("# ========== helpers ==========\n# should work for now\n", "python", 1)
        self.assertIn("banner", f)
        self.assertIn("hedge", f)

    def test_todo_without_link_is_flagged_even_next_to_a_linked_one(self):
        src = "# TODO handle quotes\n# TODO(#123) handle escapes\n"
        f = flags_at(src, "python", 1)
        self.assertIn("todo", f)
        self.assertIn("todo-no-link", f)

    def test_todo_with_link_is_not_flagged_as_missing(self):
        self.assertNotIn("todo-no-link", flags_at("# TODO(#123) escapes\n", "python", 1))

    def test_keep_markers(self):
        self.assertIn("keep", flags_at("# Copyright 2026 Example\n", "python", 1))
        self.assertIn("keep", flags_at("# See https://example.com/spec\nx = 1\n", "python", 1))
        self.assertIn("keep", flags_at("// SPDX-License-Identifier: MIT\n", "c-family", 1))

    def test_suppress(self):
        self.assertIn("suppress", flags_at("x = 1  # noqa: E501\n", "python", 1))

    def test_long_block(self):
        src = "# a\n# b\n# c\n# d\n"
        self.assertIn("long", flags_at(src, "python", 1))

    def test_cross_ref(self):
        self.assertIn("cross-ref", flags_at("// Mirrors the retry logic in SyncManager.\nx()\n", "c-family", 1))
        self.assertIn("cross-ref", flags_at("// Same pattern as the parser.\nx()\n", "c-family", 1))

    def test_change(self):
        self.assertIn("change", flags_at("// Now uses the shared client.\nx()\n", "c-family", 1))
        self.assertIn("change", flags_at("# Per the ticket, skip drafts.\nx = 1\n", "python", 1))

    def test_story(self):
        src = "// It turned out the observer was registered twice.\nx()\n"
        self.assertIn("story", flags_at(src, "c-family", 1))

    def test_issue_ref_outside_todo(self):
        self.assertIn("issue-ref", flags_at("// Fixes the crash in #412.\nx()\n", "c-family", 1))
        self.assertIn("issue-ref", flags_at("// See APP-77.\nx()\n", "c-family", 1))

    def test_issue_ref_in_todo_or_standard_is_not_flagged(self):
        self.assertNotIn("issue-ref", flags_at("// TODO(#412) handle quotes\nx()\n", "c-family", 1))
        self.assertNotIn("issue-ref", flags_at("// CRLF per RFC-4180, UTF-8 only.\nx()\n", "c-family", 1))

    def test_platform_depends_on_the_file(self):
        src = "/// Same as on Android.\nfunc f() {}\n"
        self.assertIn("platform", analyze("a.swift", src, "c-family")[0].flags)
        self.assertNotIn("platform", analyze("a.kt", src, "c-family")[0].flags)
        src = "/** Matches iOS. */\nfun f() {}\n"
        self.assertIn("platform", analyze("a.kt", src, "c-family")[0].flags)

    def test_mark_and_region_are_not_banners(self):
        self.assertNotIn("banner", flags_at("// MARK: - ----------------\nfunc f() {}\n", "c-family", 1))
        self.assertNotIn("banner", flags_at("// region ==========\nfun f() {}\n", "c-family", 1))

    def test_plain_doc_comment_has_no_flags(self):
        self.assertEqual(flags_at("/** Returns the count. */\nfunction f() {}\n", "c-family", 1), [])


class Styles(unittest.TestCase):
    def test_style_for(self):
        for path in ("a.swift", "a.kt", "a.rs", "a.js", "a.ts", "a/b.kt"):
            self.assertEqual(style_for(path), "c-family", path)
        self.assertEqual(style_for("Makefile"), "hash")
        self.assertEqual(style_for("x.py"), "python")
        self.assertIsNone(style_for("x.bin"))



class FalsePositives(unittest.TestCase):
    def test_kind_of_as_a_noun_is_not_a_hedge(self):
        self.assertNotIn("hedge", flags_at("# Each kind of prose has a mode.\nx = 1\n", "python", 1))
        self.assertIn("hedge", flags_at("# This is kind of slow.\nx = 1\n", "python", 1))

    def test_team_markers_are_not_special(self):
        self.assertNotIn("keep", flags_at("# ponytail: naive split\nx = 1\n", "python", 1))


if __name__ == "__main__":
    unittest.main()
