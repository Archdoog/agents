"""Check the shape of each case in evals/, and run each `lint` case."""

import glob
import os
import re
import unittest

from writing_for_code.lint import lint
from writing_for_code.surfaces import SURFACES

SKILL = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EVALS = os.path.join(SKILL, "evals")
PASSES = {"prune", "rewrite", "lint"}

CASE = re.compile(
    r"^### (?P<id>[a-z0-9-]+)\n\n"
    r"- surface: (?P<surface>\S+)\n"
    r"- pass: (?P<pass>\S+)\n"
    r"- expect: (?P<expect>[^\n]+)\n\n"
    r"```input\n(?P<input>.*?)\n```\n\n"
    r"- why: (?P<why>[^\n]+)$",
    re.M | re.S,
)


def cases():
    for path in sorted(glob.glob(os.path.join(EVALS, "*.md"))):
        if os.path.basename(path) == "README.md":
            continue
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
        headings = re.findall(r"^### ", text, re.M)
        found = [m.groupdict() for m in CASE.finditer(text)]
        yield path, len(headings), found


class Evals(unittest.TestCase):
    def test_each_case_has_the_shape(self):
        ids = set()
        for path, headings, found in cases():
            self.assertEqual(headings, len(found), f"{path}: a case does not parse")
            for case in found:
                self.assertIn(case["surface"], SURFACES, case["id"])
                self.assertIn(case["pass"], PASSES, case["id"])
                self.assertNotIn(case["id"], ids, f"duplicate id {case['id']}")
                ids.add(case["id"])

    def test_each_surface_has_a_clean_case(self):
        clean = {c["surface"] for _, _, found in cases() for c in found
                 if c["id"].startswith("clean-")}
        for name in SURFACES:
            self.assertIn(name, clean, f"no clean case for {name}")

    def test_lint_cases(self):
        for _, _, found in cases():
            for case in found:
                if case["pass"] != "lint":
                    continue
                with self.subTest(case["id"]):
                    got = sorted({f.code for f in lint(case["input"], case["surface"])})
                    want = ([] if case["expect"].strip() == "clean"
                            else sorted(c.strip() for c in case["expect"].split(",")))
                    self.assertEqual(got, want)


if __name__ == "__main__":
    unittest.main()
