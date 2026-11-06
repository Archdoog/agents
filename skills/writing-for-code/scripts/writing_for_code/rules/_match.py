"""Phrase matching that the rule modules share."""

from __future__ import annotations

import re
from functools import lru_cache
from typing import Iterable, Iterator, Tuple


@lru_cache(maxsize=None)
def phrase_pattern(phrase: str) -> re.Pattern:
    """Match `phrase` as whole words. A space also matches a line break."""
    body = re.escape(phrase).replace(r"\ ", r"\s+")
    return re.compile(r"(?<![\w-])" + body + r"(?![\w-])", re.I)


def find_phrases(text: str, phrases: Iterable[str]) -> Iterator[Tuple[int, str]]:
    """Yield (offset, phrase) for each match. `phrase` is the list entry.

    Where two matches overlap, only the longest phrase is reported.
    """
    taken = []
    hits = []
    for phrase in sorted(phrases, key=len, reverse=True):
        for match in phrase_pattern(phrase).finditer(text):
            span = (match.start(), match.end())
            if any(a < span[1] and span[0] < b for a, b in taken):
                continue
            taken.append(span)
            hits.append((match.start(), phrase))
    yield from sorted(hits)
