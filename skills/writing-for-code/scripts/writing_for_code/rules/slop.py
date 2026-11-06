"""Patterns that readers know as machine-written text.

Taken from the English lists in unslop (https://github.com/jlwin/unslop_ai,
MIT, commit d65241e). The lists leave out words with a common technical
meaning, such as "harness", "unlock", "unpack", "landscape", "realm",
"navigate", "journey", and "key".
"""

from __future__ import annotations

import re

from ..model import WARNING
from . import rule
from ._match import find_phrases

CHAT_ARTIFACTS = [
    "certainly!", "absolutely!", "great question", "i hope this helps",
    "hope this helps", "feel free to reach out", "feel free to ask",
    "don't hesitate to", "do not hesitate to", "i'd be happy to",
    "i would be happy to", "happy to help", "you're absolutely right",
    "you are absolutely right", "that's a great point", "as an ai",
    "as a large language model", "would you like me to", "should i continue",
    "let me know if you", "let me think step by step", "here's my thought process",
    "to answer your question", "happy coding", "i hope this email finds you well",
]

LEAKS = re.compile(
    r"oaicite|contentReference|turn\d+search\d+|citeturn|grok_card|"
    r"attributableIndex|\[attached_file:\d+\]|"
    r"utm_source=(?:chatgpt\.com|openai|claude\.ai|perplexity\.ai)|"
    r"\[(?:INSERT|YOUR|ADD|TODO)[^\]]*\]|\b\d{4}-XX-XX\b",
    re.I,
)

STOCK = [
    "in conclusion", "in summary", "to sum up", "to summarize",
    "the bottom line is", "at the end of the day", "only time will tell",
    "the future looks bright", "let's dive in", "let us dive in",
    "in today's fast-paced", "in the ever-evolving", "in an era of",
    "imagine a world where", "when it comes to", "at its core",
    "that being said", "here's the thing", "this begs the question",
    "without further ado", "in a nutshell", "bridge the gap", "move the needle",
    "take it to the next level", "comes into play", "low-hanging fruit",
]

# A sentence opener that adds weight but no fact.
OPENER = re.compile(
    r"(?:^|(?<=[.!?:])\s+)(Interestingly|Importantly|Indeed|Notably|Overall|"
    r"Ultimately|Essentially|Basically|Crucially|Fortunately|Simply put),",
)

STEERING = [
    "as you can see", "the key point is", "the key takeaway", "make no mistake",
    "let me be clear", "to be clear", "this distinction matters",
    "that matters more than it sounds", "what most people get wrong",
    "what nobody tells you", "the uncomfortable truth", "let that sink in",
    "read that again", "the numbers speak for themselves", "the data tells a story",
    "paints a clear picture", "speaks volumes", "key takeaways",
]

TIER_1 = [
    "delve", "delves", "delving", "tapestry", "testament to", "embark",
    "embarks", "elevate", "elevates", "streamline", "streamlines", "streamlined",
    "meticulous", "meticulously", "intricate", "holistic", "multifaceted",
    "actionable", "impactful", "learnings", "synergy", "synergies", "deep dive",
    "ever-evolving", "pivotal", "crucial", "boasts", "underscores", "showcase",
    "showcases", "foster", "fosters", "garner", "invaluable", "noteworthy",
    "serves as", "stands as", "plays a crucial role", "plays a key role",
]

TIER_2 = [
    "bolster", "spearhead", "resonate", "resonates", "catalyze", "illuminate",
    "elucidate", "cornerstone", "paramount", "poised to", "burgeoning",
    "nascent", "quintessential", "overarching", "transformative", "interplay",
    "encompass", "encompasses", "notably", "ecosystem", "vital",
]

NOT_JUST = re.compile(
    r"\bnot\s+(?:just|only|merely|simply)\b[^.;!?]{1,80}?\bbut\b"
    r"|\b(?:it|this)\s+(?:is|isn't|is not)\s+not\s+\w+[^.;!?]{0,40}?,\s*(?:it|this)\s+is\b",
    re.I,
)


@rule("SLOP001", "chat-artifact",
      "Chat reply text in a document. Delete it.")
def chat_artifact(text, ctx):
    for offset, phrase in find_phrases(text, CHAT_ARTIFACTS):
        yield offset, f"Chat reply text {phrase!r}. Delete it."


@rule("SLOP002", "leak-artifact",
      "Generator leftover or unfilled placeholder. Remove it or fill it in.",
      scope="document")
def leak(text, ctx):
    for match in LEAKS.finditer(text):
        yield match.start(), (f"Leftover {match.group(0)!r}. Remove it or fill "
                              f"it in.")


@rule("SLOP003", "stock-phrase",
      "Stock phrase. Delete it, or say the fact it stands in for.",
      strict=WARNING)
def stock_phrase(text, ctx):
    for offset, phrase in find_phrases(text, STOCK):
        yield offset, f"Stock phrase {phrase!r}. Delete it, or say the fact."
    for match in OPENER.finditer(text):
        yield match.start(1), (f"Opener {match.group(1)!r} adds weight, not a "
                               f"fact. Delete it.")


@rule("SLOP005", "reader-steering",
      "Tells the reader how to feel about a claim. State the claim.",
      strict=WARNING)
def reader_steering(text, ctx):
    for offset, phrase in find_phrases(text, STEERING):
        yield offset, f"{phrase!r} steers the reader. State the claim."


@rule("SLOP006", "ai-vocabulary",
      "Word that generated text overuses. Use the plain word or the fact.",
      strict=WARNING)
def ai_vocabulary(text, ctx):
    for offset, phrase in find_phrases(text, TIER_1):
        yield offset, f"{phrase!r} is a common generated word. Use the plain word."


@rule("SLOP007", "ai-vocabulary-cluster",
      "Two or more words that generated text overuses, in one paragraph.",
      scope="paragraph", strict=WARNING)
def ai_vocabulary_cluster(text, ctx):
    hits = sorted(find_phrases(text, TIER_2))
    if len({phrase for _, phrase in hits}) >= 2:
        names = ", ".join(sorted({phrase for _, phrase in hits}))
        yield hits[0][0], f"Cluster of generated words: {names}. Use plain words."


@rule("SLOP008", "not-just-but",
      "'Not just X, but Y' frame. Say Y.", strict=WARNING)
def not_just_but(text, ctx):
    for match in NOT_JUST.finditer(text):
        yield match.start(), "'Not just X, but Y' frame. Say Y."
