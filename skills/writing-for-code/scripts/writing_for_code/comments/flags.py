"""Flags for comment blocks. A flag is a lead for the author, not a verdict.

`surfaces/comments.md` gives the action for each flag.
"""

from __future__ import annotations

import re
from typing import List, Optional, Pattern

# name -> (pattern, meaning). The order is the report order.
FLAGS = [
    ("decision", re.compile(
        r"\b(ADR-?\d+|RFC-?\d+|RFD-?\d+|we (chose|decided|picked|went with)|"
        r"rationale|trade-?off|instead of|rather than|the reason (we|this)|"
        r"design decision|chosen because)\b", re.I),
     "carries a design reason. The reason goes in the PR body."),
    ("history", re.compile(
        r"\b(previously|used to|no longer|legacy|originally|migrated from|"
        r"was (removed|added|renamed|moved)|old (way|approach|version|code)|"
        r"as of (v|version|\d)|deprecated in favou?r|"
        r"before (this|the) (change|refactor))\b", re.I),
     "carries history. Git holds the history."),
    ("sequence", re.compile(
        r"(\bstep\s*\d|^\s*\d+[.)]\s|\bfirst,|\bthen,|\bfinally,|\bnext,|"
        r"\bafter that\b|\bonce (we|this|that)\b|\bat this point\b)", re.I),
     "narrates an order of steps. The code order is the order."),
    ("narration", re.compile(
        r"(^\s*(this (function|method|class|file|module|helper|block|loop)|"
        r"here we|we (now|then|first|also|just|simply)|now we|the following|"
        r"note that|it is worth noting|basically|essentially|simply)\b|"
        r"^\s*(ensur|handl|check|process|initializ|loop|iterat|creat|updat|"
        r"return|call|set|get|mak)\w*ing\b)", re.I),
     "says what the next line already says."),
    ("hedge", re.compile(
        r"\b(should work|probably|hopefully|might be|maybe|for now|hack|"
        r"temporary|temp fix|quick fix|not sure|i think|"
        r"(?<!each )(?<!a )(?<!one )(?<!the )(?<!this )(?<!that )(?<!what )"
        r"(?<!any )(?<!every )(?<!which )(?<!some )(?<!same )(?:kind|sort) of|"
        r"a bit|somewhat|fine for now|good enough)\b", re.I),
     "hedges. A reader cannot act on a guess."),
    ("banner", re.compile(r"([=\-#*/~_]){8,}"),
     "a banner. The file layout gives the structure."),
    ("todo", re.compile(r"\b(TODO|FIXME|XXX|HACK|BUG)\b"),
     "a task marker."),
    ("suppress", re.compile(
        r"(eslint-disable|@ts-ignore|@ts-expect-error|noqa|pylint:|type: ?ignore|"
        r"swiftlint:|@Suppress|#pragma|prettier-ignore|rubocop:|nolint|"
        r"@SuppressWarnings|checkstyle|detekt)", re.I),
     "a tool directive. Keep it with the rule name and the reason."),
    ("keep", re.compile(
        r"(SPDX-License|Copyright|Licensed under|https?://\S+|"
        r"#\d{2,}\b|[A-Z]{2,}-\d+\b)", re.I),
     "has a license header or a link."),
    ("cross-ref", re.compile(
        r"\b(mirrors (how|what|\w+'s|the( \w+)? (behaviou?r|logic|implementation|pattern))|"
        r"parity( with)?|ported from|port of|consistent with|"
        r"same (pattern|approach|logic|behaviou?r|way) as|"
        r"matches (the )?(\w+ )?(behaviou?r|logic|implementation|pattern|approach)|"
        r"as \w+ does)\b", re.I),
     "cites other code as the reason. The reader can read the code."),
    ("change", re.compile(
        r"\b(now|newly|updated to|changed (from|to)|as requested|"
        r"per the (ticket|issue|request|task|spec)|"
        r"the user (asked|wants|wanted|requested))\b", re.I),
     "describes the change. Write about the code as it is."),
    ("story", re.compile(
        r"\b(turned out|it turns out|we (found|discovered|noticed|realized|realised|tracked)|"
        r"after (hours|days|a long|much)|took (hours|days|a while)|spent (hours|days)|"
        r"root cause was|the culprit)\b", re.I),
     "tells the debug story. State the symptom and the cause."),
]

MEANINGS = {name: meaning for name, _, meaning in FLAGS}
MEANINGS.update({
    "todo-no-link": "a task marker with no link.",
    "issue-ref": "links an issue of this repo outside a TODO.",
    "platform": "names a sibling platform.",
    "dead-code": "looks like code that was commented out.",
    "restates": "repeats the words of the next line of code.",
    "long": "is over three lines.",
})

TODO = dict((name, pattern) for name, pattern, _ in FLAGS)["todo"]

# Tool directives that look like banners.
DIRECTIVE = re.compile(
    r"^\s*(MARK:|#?pragma mark|(end)?region\b|<editor-fold|</editor-fold)", re.I)
ISSUE_LINK = re.compile(r"(https?://\S+|#\d{2,}\b|[A-Z]{2,}-\d+\b)")
# A bare issue number. Standards and external IDs with the same shape are not
# issues.
ISSUE_REF = re.compile(
    r"((?<![\w/&])#\d+\b|\b(?!(?:RFC|ISO|UTF|SHA|AES|RSA|ADR|RFD|CVE|HTTP|TLS|"
    r"SSL|IEEE|ECMA|PEP|JSR|KEP|SE|ES|MD|FB)-)[A-Z]{2,}-\d+\b)")

CODE_SIGNALS = [
    re.compile(r"[;{}]\s*$"),
    re.compile(r"^\s*(if|for|while|return|const|let|var|def|class|import|from|"
               r"val|fun|func|public|private|static|else|try|catch|switch|case|"
               r"print|console\.|self\.|this\.)\b"),
    re.compile(r"\w+\s*\(.*\)"),
    re.compile(r"\w+\s*(==|!=|\+=|-=|=>|->|::)\s*\w+"),
    re.compile(r"^\s*[\w.]+\s*=\s*\S"),
]

STOPWORDS = {
    "a", "an", "the", "of", "to", "for", "in", "on", "and", "or", "is", "are",
    "it", "this", "that", "with", "as", "by", "at", "from", "if", "then",
    "we", "our", "be", "into", "up", "out", "not", "no", "so", "do", "does",
}

LONG_LINES = 3


def looks_like_code(text: str) -> bool:
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        return False
    if len(lines) == 1:
        # One line needs two signals. "call parse() first" has one.
        return sum(1 for sig in CODE_SIGNALS if sig.search(lines[0])) >= 2
    hits = sum(1 for ln in lines if any(sig.search(ln) for sig in CODE_SIGNALS))
    return hits * 2 > len(lines)


def _words(text: str) -> set:
    out = set()
    for part in re.findall(r"[A-Za-z][A-Za-z0-9]*", text):
        for w in re.findall(r"[A-Z]?[a-z0-9]+|[A-Z]+(?![a-z])", part):
            w = w.lower()
            if w not in STOPWORDS and len(w) > 1:
                out.add(w.rstrip("s"))
    return out


def restates(text: str, next_code: str) -> bool:
    comment = _words(text)
    if not next_code or len(comment) < 2:
        return False
    return len(comment & _words(next_code)) / len(comment) >= 0.7


def flags_for(text: str, kind: str, line_count: int, next_code: str,
              platform: Optional[Pattern]) -> List[str]:
    """Return the flag names for one comment block."""
    found = [name for name, pattern, _ in FLAGS if pattern.search(text)]
    lines = text.splitlines()
    if "todo" in found and any(TODO.search(ln) and not ISSUE_LINK.search(ln)
                               for ln in lines):
        found.append("todo-no-link")
    if "banner" in found and DIRECTIVE.search(text):
        found.remove("banner")
    if any(ISSUE_REF.search(ln) and not TODO.search(ln) for ln in lines):
        found.append("issue-ref")
    if platform and platform.search(text):
        found.append("platform")
    if looks_like_code(text) and "keep" not in found:
        found.append("dead-code")
    if kind != "doc" and restates(text, next_code):
        found.append("restates")
    if line_count > LONG_LINES and "keep" not in found:
        found.append("long")
    return found
