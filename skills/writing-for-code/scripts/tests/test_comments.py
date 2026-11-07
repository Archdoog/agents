"""Check comment extraction against string data and original positions."""

import unittest

from writing_for_code import comments


class CommentTests(unittest.TestCase):
    def semicolons(self, path, text):
        return [f for f in comments.analyze(path, text) if f['code'] == 'semicolon']

    def test_indented_comment_coordinates(self):
        items = self.semicolons('x.swift', '    // One; two.\n')
        self.assertEqual([(f['line'], f['column']) for f in items], [(1, 11)])

    def test_block_coordinates(self):
        items = self.semicolons('x.kt', '/**\n * One; two.\n */')
        self.assertEqual([(f['line'], f['column']) for f in items], [(2, 7)])

    def test_trailing_coordinates(self):
        items = self.semicolons('x.rs', 'let x = 1; // One; two.')
        self.assertEqual([(f['line'], f['column']) for f in items], [(1, 18)])

    def test_multiline_and_raw_strings(self):
        cases = {
            'x.swift': 'let x = """\n// One; two.\n"""\nlet y = #"// Three; four."#',
            'x.kt': 'val x = """\n// One; two.\n"""',
            'x.rs': 'let x = r###"\n// One; two.\n"###;',
            'x.ts': 'const x = `\n// One; two.\n`;',
            'x.go': 'var x = `\n// One; two.\n`',
            'x.cpp': 'auto x = R"data(\n// One; two.\n)data";',
            'x.py': 'x = """\n# One; two.\n"""\n',
        }
        for path, text in cases.items():
            with self.subTest(path=path):
                self.assertEqual(self.semicolons(path, text), [])

    def test_python_docstring(self):
        items = self.semicolons('x.py', 'def f():\n    """One; two."""\n    pass\n')
        self.assertEqual([(f['line'], f['column'], f['surface']) for f in items], [(2, 11, 'docstring')])

    def test_python_unicode_positions(self):
        items = self.semicolons('x.py', '"""Caf\u00e9; text."""\n')
        self.assertEqual(items[0]['column'], 8)

    def test_python_data_not_documentation(self):
        self.assertEqual(self.semicolons('x.py', 'def f():\n    x = 1\n    "One; two."\n'), [])

    def test_nested_comments(self):
        for path in ['x.rs', 'x.kt', 'x.swift']:
            with self.subTest(path=path):
                self.assertEqual(len(self.semicolons(path, '/* outer /* inner */ end; text. */')), 1)

    def test_directives(self):
        for body in ['// swiftlint: disable; all', '// Copyright 2026; author', '// SPDX-License-Identifier: MIT;']:
            with self.subTest(body=body):
                self.assertEqual(comments.analyze('x.swift', body), [])

    def test_findings_are_advisory(self):
        self.assertEqual(self.semicolons('x.ts', '// One; two.')[0]['level'], 'warning')

    def test_docstrings_have_no_length_flag(self):
        text = '/**\n * Summary.\n *\n * Returns the value.\n *\n * Raises an error.\n */'
        self.assertNotIn('comment-long', {f['code'] for f in comments.analyze('x.ts', text)})

    def test_python_no_final_newline(self):
        self.assertEqual(len(self.semicolons('x.py', '# One; two.')), 1)

    def test_invalid_python_is_input_error(self):
        with self.assertRaises(ValueError):
            comments.analyze('x.py', 'def (')

    def test_unsupported_source(self):
        with self.assertRaises(ValueError):
            comments.analyze('x.unknown', '// Text.')
