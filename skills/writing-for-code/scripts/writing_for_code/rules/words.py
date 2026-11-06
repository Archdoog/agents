"""Word rules from ASD-STE100: marketing words, long words, phrasal verbs."""

from __future__ import annotations

from ..model import WARNING
from . import rule
from ._match import find_phrases

MARKETING = [
    "seamless", "seamlessly", "robust", "powerful", "cutting-edge", "effortless",
    "effortlessly", "world-class", "next-generation", "revolutionary", "blazing",
    "blazingly", "lightning-fast", "delightful", "turnkey", "best-in-class",
    "state-of-the-art", "game-changing", "game-changer", "groundbreaking",
    "battle-tested", "enterprise-grade", "supercharge", "unleash", "empower",
    "empowers", "empowering", "comprehensive", "elegant",
]

WORDY = {
    "begin": "start", "begins": "starts", "commence": "start", "commences": "starts",
    "initiate": "start", "initiates": "starts", "utilize": "use", "utilizes": "uses",
    "utilizing": "using", "utilization": "use", "leverage": "use", "leverages": "uses",
    "leveraging": "using", "facilitate": "help", "facilitates": "helps",
    "ensure": "make sure", "ensures": "makes sure", "ensuring": "making sure",
    "prior to": "before", "subsequent to": "after", "obtain": "get", "obtains": "gets",
    "acquire": "get", "acquires": "gets", "demonstrate": "show",
    "demonstrates": "shows", "additionally": "also", "furthermore": "also",
    "moreover": "also", "aforementioned": "this", "henceforth": "from now on",
    "therein": "there", "whilst": "while", "amongst": "among", "numerous": "many",
    "myriad": "many", "plethora": "many", "in order to": "to",
    "a variety of": "several", "in the event that": "if",
    "due to the fact that": "because", "regarding": "about", "concerning": "about",
}

PHRASAL = {
    "spin up": "start", "spin down": "stop", "spun up": "started",
    "reach out": "ask", "reaching out": "asking", "dive into": "read",
    "dives into": "reads", "diving into": "reading", "kick off": "start",
    "kicks off": "starts", "roll out": "release", "rolls out": "releases",
    "tear down": "delete", "ramp up": "increase", "circle back": "return",
    "drill down": "examine", "track down": "find", "spin off": "separate",
}


@rule("STE004", "marketing-word",
      "Marketing word. Delete it, or give the measurement it stands in for.")
def marketing(text, ctx):
    for offset, phrase in find_phrases(text, MARKETING):
        yield offset, (f"Marketing word {phrase!r}. Delete it, or give the "
                       f"measurement it stands in for.")


# The word list is a strong preference in flavored mode, not a lock.
@rule("STE005", "long-word", "Long word where a short common word exists.",
      flavored=WARNING)
def long_word(text, ctx):
    for offset, phrase in find_phrases(text, WORDY):
        yield offset, f"{phrase!r}: write {WORDY[phrase]!r}."


@rule("STE009", "phrasal-verb", "Phrasal verb where a plain verb exists.",
      strict=WARNING)
def phrasal_verb(text, ctx):
    for offset, phrase in find_phrases(text, PHRASAL):
        yield offset, f"{phrase!r}: write {PHRASAL[phrase]!r}."
