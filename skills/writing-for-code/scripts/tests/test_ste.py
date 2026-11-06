"""The ASD-STE100 rules.

Most of these are false-positive tests. A checker that fires on quoted logs,
possessives, or its own examples teaches an agent to ignore it.
"""

import unittest

from .helpers import codes, first


class RulesFire(unittest.TestCase):
    def test_long_sentence(self):
        self.assertIn("STE001", codes("The " + "very " * 30 + "long sentence."))

    def test_semicolon(self):
        self.assertIn("STE002", codes("The build ran; the tests passed."))

    def test_contraction(self):
        self.assertIn("STE003", codes("The build didn't pass."))

    def test_marketing_word(self):
        self.assertIn("STE004", codes("A seamless developer experience."))

    def test_long_word(self):
        self.assertIn("STE005", codes("Utilize the parser to read it."))

    def test_hedge(self):
        self.assertIn("STE006", codes("It is important to note that this fails."))

    def test_passive(self):
        self.assertIn("STE007", codes("The file is parsed by the scout."))

    def test_nominalization(self):
        self.assertIn("STE008", codes("Perform an analysis of the log."))

    def test_phrasal_verb(self):
        self.assertIn("STE009", codes("Spin up the runner."))

    def test_ing_main_verb(self):
        self.assertIn("STE010", codes("The scout is reading the board."))

    def test_long_paragraph(self):
        para = " ".join(f"Sentence number {n} lands here." for n in range(1, 9))
        self.assertIn("STE011", codes(para))


class FalsePositives(unittest.TestCase):
    def test_possessive_is_not_a_contraction(self):
        self.assertNotIn("STE003", codes("Quote a human's own words."))
        self.assertNotIn("STE003", codes("The scout's marker is stale."))

    def test_real_s_contraction_still_fires(self):
        self.assertIn("STE003", codes("It's stale."))
        self.assertIn("STE003", codes("That's the wrong branch."))

    def test_modal_progressive_allowed(self):
        self.assertNotIn("STE010", codes("The reader may be following under pressure."))

    def test_participial_adjective_is_not_passive(self):
        self.assertNotIn("STE007", codes("A reader who is tired misreads it."))
        self.assertNotIn("STE007", codes("Python 3.8 is required."))

    def test_em_dash_never_reported(self):
        self.assertEqual(codes("The scout reads the board — then it exits."), [])

    def test_table_cell_exempt_from_sentence_cap(self):
        cell = " ".join(["word"] * 40)
        text = f"| Surface | Mode |\n|---|---|\n| {cell} | strict |\n"
        self.assertNotIn("STE001", codes(text))

    def test_table_cell_still_gets_word_rules(self):
        text = "| Surface | Mode |\n|---|---|\n| A seamless thing | strict |\n"
        self.assertIn("STE004", codes(text))

    def test_list_is_not_a_paragraph(self):
        text = "\n".join(f"{n}. Do the thing numbered {n}." for n in range(1, 11))
        self.assertNotIn("STE011", codes(text))

    def test_heading_does_not_join_following_sentence(self):
        self.assertEqual(codes("## Scope\n\nThe scout reads the board.\n"), [])


class Sentences(unittest.TestCase):
    def test_split_before_a_flag_or_a_code_span(self):
        words = " ".join(["word"] * 15)
        self.assertNotIn("STE001", codes(f"{words}. --flag {words}."))
        self.assertNotIn("STE001", codes(f"{words}. `code` {words}."))

    def test_no_split_after_an_abbreviation(self):
        words = " ".join(["word"] * 15)
        self.assertIn("STE001", codes(f"{words}, e.g. {words}."))


class Modes(unittest.TestCase):
    def test_word_cap_differs(self):
        twenty_two = " ".join(["word"] * 21) + " end."
        self.assertIn("STE001", codes(twenty_two, mode="strict"))
        self.assertNotIn("STE001", codes(twenty_two, mode="flavored"))

    def test_long_word_is_error_in_strict_warning_in_flavored(self):
        self.assertEqual(first("Utilize the parser.", "STE005", mode="strict").level, "error")
        self.assertEqual(first("Utilize the parser.", "STE005", mode="flavored").level, "warning")

    def test_marketing_is_an_error_in_both(self):
        for mode in ("strict", "flavored"):
            self.assertEqual(first("A seamless result.", "STE004", mode=mode).level, "error")

    def test_surface_sets_the_mode(self):
        twenty_two = " ".join(["word"] * 21) + " end."
        self.assertIn("STE001", codes(twenty_two, surface="error"))
        self.assertNotIn("STE001", codes(twenty_two, surface="pr"))


class Positions(unittest.TestCase):
    def test_line_and_column_point_at_the_word(self):
        text = "Line one is fine.\nThe build didn't pass.\n"
        f = first(text, "STE003")
        self.assertEqual(f.line, 2)
        self.assertEqual(text.split("\n")[1][f.col - 1:f.col + 5], "didn't")

    def test_position_survives_a_wrapped_phrase(self):
        f = first("The gate runs prior\nto the push.\n", "STE005")
        self.assertEqual((f.line, f.col), (1, 15))

    def test_position_after_masked_span(self):
        text = "Use `some code here` then utilize it.\n"
        f = first(text, "STE005")
        self.assertEqual(text[f.col - 1:f.col + 6], "utilize")


if __name__ == "__main__":
    unittest.main()
