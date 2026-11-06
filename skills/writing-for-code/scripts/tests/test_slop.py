"""The rules taken from unslop, and the structure rules."""

import unittest

from .helpers import codes, first


class SlopFires(unittest.TestCase):
    def test_chat_artifact(self):
        self.assertIn("SLOP001", codes("The parser is done. I hope this helps!"))
        self.assertIn("SLOP001", codes("Let me know if you want more tests."))

    def test_overlapping_phrases_report_once(self):
        self.assertEqual(codes("I hope this helps."), ["SLOP001"])

    def test_leak_artifact(self):
        self.assertIn("SLOP002", codes("See [docs](https://x.io/?utm_source=chatgpt.com)."))
        self.assertIn("SLOP002", codes("Set the owner to [INSERT NAME]."))

    def test_leak_in_code_is_quoted(self):
        self.assertNotIn("SLOP002", codes("Run it:\n\n```\nexport KEY=[YOUR_KEY]\n```\n"))
        self.assertNotIn("SLOP002", codes("Set `[YOUR_KEY]` in the file."))

    def test_stock_phrase_and_opener(self):
        self.assertIn("SLOP003", codes("In conclusion, the cache works."))
        self.assertIn("SLOP003", codes("The cache works. Overall, it is fast."))

    def test_meta_lead_in(self):
        self.assertIn("SLOP004", codes("This section describes the cache."))
        self.assertIn("SLOP004", codes("In this guide, we will set up the cache."))

    def test_reader_steering(self):
        self.assertIn("SLOP005", codes("As you can see, the cache is warm."))

    def test_ai_vocabulary(self):
        self.assertIn("SLOP006", codes("We delve into the parser."))

    def test_cluster_needs_two_words(self):
        self.assertNotIn("SLOP007", codes("The cornerstone of the cache is the key."))
        self.assertIn("SLOP007", codes("The cornerstone of a transformative cache."))

    def test_not_just_but(self):
        self.assertIn("SLOP008", codes("It is not just a cache, but a store."))

    def test_self_reference_only_on_change_surfaces(self):
        self.assertIn("SLOP009", codes("This PR adds a cache.", "pr"))
        self.assertNotIn("SLOP009", codes("This PR adds a cache.", "doc"))

    def test_levels(self):
        self.assertEqual(first("I hope this helps.", "SLOP001").level, "error")
        self.assertEqual(first("In conclusion, it works.", "SLOP003", mode="strict").level,
                         "warning")


class TechnicalWordsStayClean(unittest.TestCase):
    """Words that sound like slop but have a technical meaning."""

    def test_technical_words(self):
        for text in (
            "Unlock the mutex before you return.",
            "Unpack the tuple into two names.",
            "The test harness starts the server.",
            "Rotate the screen to landscape.",
            "Navigate to the settings screen.",
            "Store the API key in the keychain.",
        ):
            self.assertEqual(codes(text), [], text)

    def test_a_plain_readme_is_clean(self):
        text = (
            "# parser\n\n"
            "Parses polyline strings into coordinates.\n\n"
            "## Install\n\n"
            "```sh\nnpm install parser\n```\n\n"
            "## Use\n\n"
            "Call `decode` with the encoded string. It returns an array of\n"
            "`[lat, lng]` pairs.\n"
        )
        self.assertEqual(codes(text, "readme"), [])


if __name__ == "__main__":
    unittest.main()
