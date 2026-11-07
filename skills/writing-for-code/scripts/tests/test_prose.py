"""Check prose rules, exclusions, and source coordinates."""

import unittest

from writing_for_code import prose


class ProseTests(unittest.TestCase):
    def codes(self, text, **kwargs):
        return {f['code'] for f in prose.lint(text, **kwargs)}

    def test_semicolon_coordinates(self):
        items = prose.lint('First line.\n\n    Text; here.', source=True)
        self.assertEqual((items[0]['line'], items[0]['column']), (3, 9))

    def test_mask_preserves_offsets(self):
        text = 'Read `a;b` at https://example.test/a;b.\n\nText; here.'
        masked = prose.mask(text)
        self.assertEqual(len(masked), len(text))
        self.assertEqual(masked.count('\n'), text.count('\n'))
        self.assertEqual([(f['line'], f['column']) for f in prose.lint(text)], [(3, 5)])

    def test_exclusions(self):
        cases = [
            '```python\na;b\n```', '~~~\na;b\n~~~', '    a;b\n', '\ta;b\n',
            '> a;b\n', '> a;b\ncontinuation; here\n', '"A; quote."', "'A; quote.'",
            '`a;b`', '`` a`b;c ``', '[label](https://test/a;b)',
            '<!-- comment; -->', '---\nname: a;b\n---\n',
            '<!-- writing-for-code: off -->\na;b\n<!-- writing-for-code: on -->',
            '<!-- ste-lint: off -->\na;b\n<!-- ste-lint: on -->',
        ]
        for text in cases:
            with self.subTest(text=text):
                self.assertEqual(prose.lint(text), [])

    def test_link_label_is_prose(self):
        self.assertIn('word-choice', self.codes('[utilize](https://example.test)'))

    def test_enabled_region_is_checked(self):
        self.assertIn('semicolon', self.codes('<!-- writing-for-code: off -->\na;b\n'
                                             '<!-- writing-for-code: on -->\nc;d'))

    def test_strict_sentence_limit(self):
        text = ' '.join(['word'] * 21) + '.'
        self.assertNotIn('sentence-length', self.codes(text))
        self.assertIn('sentence-length', self.codes(text, surface='procedure'))

    def test_flavored_limit(self):
        self.assertIn('sentence-length', self.codes(' '.join(['word'] * 26) + '.'))

    def test_wrapped_phrase_span(self):
        item = next(f for f in prose.lint('Read this prior\nto the next step.') if f['code'] == 'word-choice')
        self.assertEqual((item['line'], item['column'], item['start_line'], item['end_line']), (1, 11, 1, 2))

    def test_wrapped_sentence_span(self):
        text = ' '.join(['word'] * 15) + '\n' + ' '.join(['word'] * 11) + '.'
        item = prose.lint(text)[0]
        self.assertEqual((item['start_line'], item['end_line']), (1, 2))

    def test_word_choice_modes(self):
        self.assertEqual(prose.lint('Utilize the cache.')[0]['level'], 'warning')
        self.assertEqual(prose.lint('Utilize the cache.', surface='error')[0]['level'], 'error')

    def test_contraction_and_possessive(self):
        self.assertIn('contraction', self.codes("Do not wait if it's empty."))
        self.assertNotIn('contraction', self.codes("The cache's size is fixed."))

    def test_subject_length(self):
        self.assertNotIn('commit-subject', self.codes('x' * 72, surface='commit'))
        self.assertIn('commit-subject', self.codes('x' * 73, surface='commit'))

    def test_paragraph(self):
        self.assertIn('paragraph-length', self.codes(' '.join(['One sentence.'] * 7)))

    def test_clean_surfaces(self):
        for surface in prose.SURFACES:
            with self.subTest(surface=surface):
                self.assertEqual(prose.lint('Return the cached value.', surface), [])

    def test_invalid_mode(self):
        with self.assertRaises(ValueError):
            prose.lint('Text.', mode='invalid')

    def test_invalid_surface(self):
        with self.assertRaises(ValueError):
            prose.lint('Text.', surface='invalid')

    def test_no_em_dash_budget(self):
        self.assertEqual(self.codes('The cache\u2014not the client\u2014owns the value.'), set())
