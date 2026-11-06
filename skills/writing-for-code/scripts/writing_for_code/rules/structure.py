"""Paragraph and document-shape rules."""

from __future__ import annotations

import re

from ..model import WARNING
from ..text import SENTENCE_SPLIT
from . import rule

PARAGRAPH_CAP = 6

META_LEAD = re.compile(
    r"\bthis\s+(?:section|document|doc|guide|page|readme|file|article|tutorial|"
    r"chapter)\s+(?:describes|explains|covers|outlines|provides|contains|"
    r"shows|walks|will|aims|is\s+about)\b"
    r"|\bin\s+this\s+(?:section|guide|document|article|tutorial|readme|page),?\s+"
    r"(?:we|you)(?:\s+will|'ll)\b"
    r"|\bthe\s+following\s+sections?\s+(?:describes?|explains?|covers?|outlines?)\b",
    re.I,
)

# A change description that opens on itself in place of the change.
SELF_REFERENCE = re.compile(
    r"^\s*this\s+(?:pr|pull\s+request|mr|merge\s+request|commit|change|patch|diff)\b",
    re.I,
)


@rule("STE011", "long-paragraph", "Paragraph is over six sentences. Split it.",
      scope="paragraph", strict=WARNING)
def long_paragraph(text, ctx):
    count = len([s for s in SENTENCE_SPLIT.split(text) if s.strip()])
    if count > PARAGRAPH_CAP:
        yield 0, (f"Paragraph is {count} sentences. The cap is {PARAGRAPH_CAP}. "
                  f"Split it.")


@rule("SLOP004", "meta-lead-in",
      "Says what the text is about in place of saying it. Delete the lead-in.",
      strict=WARNING)
def meta_lead_in(text, ctx):
    for match in META_LEAD.finditer(text):
        yield match.start(), (f"{match.group(0)!r} announces the text. Delete it "
                              f"and start with the content.")


@rule("SLOP009", "self-reference",
      "Opens on 'This PR' or 'This commit'. Start with what changed.",
      strict=WARNING, surfaces=("commit", "pr"))
def self_reference(text, ctx):
    match = SELF_REFERENCE.match(text)
    if match:
        yield len(text) - len(text.lstrip()), (
            f"Opens on {match.group(0).strip()!r}. Start with what changed.")
