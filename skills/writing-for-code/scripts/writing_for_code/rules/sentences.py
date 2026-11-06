"""Sentence and verb rules from ASD-STE100."""

from __future__ import annotations

import re

from ..model import WARNING
from ..text import WORD
from . import rule
from ._match import find_phrases

WORD_CAP = {"strict": 20, "flavored": 25}

HEDGE = [
    "it is important to note", "it should be noted", "it is worth noting",
    "please note that", "as mentioned above", "as noted above",
    "it is worth mentioning", "needless to say", "it goes without saying",
]

# "'s" is a contraction after a pronoun or a demonstrative. Everywhere else it
# is a possessive, so the rule matches only those words.
CONTRACTION = re.compile(
    r"\b(?:\w+['’](?:t|re|ve|ll|d|m)"
    r"|(?:it|that|there|here|what|who|he|she|let|one|this)['’]s)\b",
    re.I,
)

NOMINALIZATION = re.compile(
    r"\b(?:perform(?:s|ed|ing)?|conduct(?:s|ed|ing)?|carry out|carries out|"
    r"carried out|make use of|makes use of|made use of)\s+(?:a|an|the)?\s*"
    r"\w*(?:tion|sis|ment|ance|ence)\b",
    re.I,
)

BE = r"(?:am|is|are|was|were|be|been|being)"
IRREGULAR_PARTICIPLE = (
    r"(?:done|made|sent|read|built|kept|held|set|put|run|written|shown|given|"
    r"taken|found|gotten|seen|known|thrown|drawn|lost|left|meant|split)"
)
PASSIVE = re.compile(
    rf"\b{BE}\s+(\w+ed|{IRREGULAR_PARTICIPLE})\b(?!\s+(?:to|that)\b)", re.I)
# Adjectives with the form of a participle. "A reader who is tired" has no
# actor to name.
PASSIVE_EXEMPT = {
    "tired", "based", "related", "unrelated", "involved", "detailed", "limited",
    "advanced", "complicated", "interested", "concerned", "supposed", "dedicated",
    "experienced", "qualified", "motivated", "outdated", "deprecated", "required",
    "allowed", "enabled", "disabled", "expected", "needed", "installed",
}

MODAL = r"(?:may|might|must|can|could|will|would|shall|should)"
# Python has no lookbehind of variable width, so the modal is an optional
# group. A match with a modal is a modal progressive and is not reported.
ING_MAIN_VERB = re.compile(rf"\b(?:({MODAL})\s+)?({BE}\s+(\w+ing))\b", re.I)
ING_ALLOWED = {"missing", "nothing", "during", "being", "willing", "outstanding",
               "pending", "something", "anything", "everything", "string"}


@rule("STE001", "long-sentence", "Sentence is over the word cap. Split it.",
      scope="sentence")
def long_sentence(sentence, ctx):
    count = len(WORD.findall(sentence))
    cap = WORD_CAP[ctx.mode]
    if count > cap:
        yield 0, f"Sentence is {count} words. The cap is {cap}. Split it."


@rule("STE002", "semicolon", "Semicolon. Write two sentences.")
def semicolon(text, ctx):
    for match in re.finditer(";", text):
        yield match.start(), "Semicolon. Write two sentences."


@rule("STE003", "contraction", "Contraction. Expand it.")
def contraction(text, ctx):
    for match in CONTRACTION.finditer(text):
        yield match.start(), f"Contraction {match.group(0)!r}. Expand it."


@rule("STE006", "hedge", "Filler that delays the claim. Delete it.")
def hedge(text, ctx):
    for offset, phrase in find_phrases(text, HEDGE):
        yield offset, f"Filler {phrase!r}. Delete it and state the claim."


# The rest are heuristics with real false positives, so they never fail a run.
@rule("STE007", "passive-voice",
      "Possible passive voice. If you know the actor, name it.", strict=WARNING)
def passive(text, ctx):
    for match in PASSIVE.finditer(text):
        if match.group(1).lower() in PASSIVE_EXEMPT:
            continue
        yield match.start(), (f"Possible passive voice {match.group(0)!r}. If you "
                              f"know the actor, name it and make the verb active.")


@rule("STE008", "nominalization", "Verb hidden in a noun. Use the verb.",
      strict=WARNING)
def nominalization(text, ctx):
    for match in NOMINALIZATION.finditer(text):
        yield match.start(), f"{match.group(0)!r} hides a verb. Use the verb."


@rule("STE010", "ing-main-verb",
      "'-ing' main verb where a simple tense reads the same.", strict=WARNING)
def ing_main_verb(text, ctx):
    for match in ING_MAIN_VERB.finditer(text):
        modal, phrase, verb = match.group(1), match.group(2), match.group(3)
        if modal or verb.lower() in ING_ALLOWED:
            continue
        yield match.start(2), f"{phrase!r}: a simple tense reads the same."
