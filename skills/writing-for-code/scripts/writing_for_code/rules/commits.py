"""Commit message rules. They run on the commit surface only.

The engine removes git comment lines (`#`) before these rules run. A scope
prefix (`parser:`) or a Conventional Commits type (`fix(parser):`) is allowed
and is not part of the subject text that the mood rule reads.
"""

from __future__ import annotations

import re

from ..model import WARNING
from . import rule

SUBJECT_CAP = 72
BODY_CAP = 72

PREFIX = re.compile(r"^[\w./-]+(?:\([^)]*\))?!?:\s+")
TRAILER = re.compile(r"^[A-Za-z][\w-]*:\s+\S")
URL = re.compile(r"https?://")

# Verbs that commit subjects often start with in the wrong mood.
VERBS = [
    "add", "fix", "update", "remove", "change", "move", "use", "make",
    "implement", "introduce", "refactor", "rename", "bump", "improve", "create",
    "delete", "drop", "replace", "clean", "support", "allow", "handle", "set",
    "enable", "disable", "merge", "revert", "document", "test", "split", "extract",
    "convert", "simplify", "prevent", "avoid", "ensure", "return", "show", "hide",
    "port", "migrate", "upgrade", "downgrade", "adjust", "tweak", "correct",
]
DOUBLED = {"drop": "dropp", "split": "splitt", "set": "sett", "stop": "stopp"}


def _forms(verb):
    """The third-person, past, and -ing forms of a regular verb."""
    if verb.endswith("y") and verb[-2] not in "aeiou":
        return {verb[:-1] + "ies", verb[:-1] + "ied", verb + "ing"}
    if verb.endswith("e"):
        return {verb + "s", verb + "d", verb[:-1] + "ing"}
    if verb.endswith(("s", "x", "z", "ch", "sh")):
        return {verb + "es", verb + "ed", verb + "ing"}
    stem = DOUBLED.get(verb, verb)
    return {verb + "s", stem + "ed", stem + "ing"}


NOT_IMPERATIVE = set()
for verb in VERBS:
    NOT_IMPERATIVE.update(_forms(verb))
NOT_IMPERATIVE -= set(VERBS)


def _lines(text):
    """Yield (offset, line) for each line."""
    offset = 0
    for line in text.split("\n"):
        yield offset, line
        offset += len(line) + 1


def _subject(text):
    for offset, line in _lines(text):
        if line.strip():
            return offset, line
    return 0, ""


@rule("COMMIT001", "subject-length",
      f"Subject line is over {SUBJECT_CAP} characters.", scope="document",
      surfaces=("commit",))
def subject_length(text, ctx):
    offset, subject = _subject(text)
    if len(subject.rstrip()) > SUBJECT_CAP:
        yield offset, (f"Subject is {len(subject.rstrip())} characters. The cap "
                       f"is {SUBJECT_CAP}.")


@rule("COMMIT002", "subject-period", "Subject line ends with a period.",
      scope="document", surfaces=("commit",))
def subject_period(text, ctx):
    offset, subject = _subject(text)
    stripped = subject.rstrip()
    if stripped.endswith(".") and not stripped.endswith("..."):
        yield offset + len(stripped) - 1, "Subject ends with a period. Delete it."


@rule("COMMIT003", "subject-mood",
      "Subject does not start with an imperative verb.", scope="document",
      strict=WARNING, surfaces=("commit",))
def subject_mood(text, ctx):
    offset, subject = _subject(text)
    body = subject.lstrip()
    lead = len(subject) - len(body)
    prefix = PREFIX.match(body)
    if prefix:
        lead += prefix.end()
        body = body[prefix.end():]
    first = re.match(r"[A-Za-z]+", body)
    if first and first.group(0).lower() in NOT_IMPERATIVE:
        yield offset + lead, (f"Subject starts with {first.group(0)!r}. Use the "
                              f"imperative: 'Add', 'Fix', 'Remove'.")


@rule("COMMIT004", "subject-separator",
      "No blank line between the subject and the body.", scope="document",
      surfaces=("commit",))
def subject_separator(text, ctx):
    lines = list(_lines(text))
    for n, (_, line) in enumerate(lines):
        if line.strip():
            if n + 1 < len(lines) and lines[n + 1][1].strip():
                yield lines[n + 1][0], "Put a blank line after the subject."
            return


@rule("COMMIT005", "body-line-length",
      f"Body line is over {BODY_CAP} characters.", scope="document",
      strict=WARNING, surfaces=("commit",))
def body_line_length(text, ctx):
    seen_subject = False
    for offset, line in _lines(text):
        if not seen_subject:
            seen_subject = bool(line.strip())
            continue
        if (len(line) > BODY_CAP and not URL.search(line)
                and not TRAILER.match(line) and not line.startswith(("    ", "\t"))):
            yield offset + BODY_CAP, (f"Body line is {len(line)} characters. Wrap "
                                      f"at {BODY_CAP}.")
