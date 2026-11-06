"""Run the registered rules over one piece of text."""

from __future__ import annotations

import bisect
import re
from typing import List, Optional

from . import rules, text
from .model import Finding
from .rules import Context
from .surfaces import SURFACES, mode_for

GIT_COMMENT = re.compile(r"^#")


def _prepare(raw: str, surface: str) -> str:
    if surface == "commit":
        # Git drops these lines from the message, so the rules skip them.
        return text.blank_lines(raw, lambda line: bool(GIT_COMMENT.match(line)))
    return raw


def _document_text(raw: str, kinds: List[str]) -> str:
    """The input with quoted lines and code spans blanked. URLs stay."""
    out = []
    for line, kind in zip(raw.split("\n"), kinds):
        if kind == text.SKIP:
            out.append("")
        else:
            out.append(re.sub(r"`[^`\n]*`", lambda m: " " * len(m.group(0)), line))
    return "\n".join(out)


def lint(raw: str, surface: str = "doc", mode: Optional[str] = None) -> List[Finding]:
    """Return the findings for `raw`, sorted by position.

    `mode` overrides the mode of the surface.
    """
    if surface not in SURFACES:
        raise ValueError(f"unknown surface {surface!r}")
    mode = mode or mode_for(surface)
    ctx = Context(mode=mode, surface=surface)
    raw = _prepare(raw, surface)
    segs, _, kinds = text.segments(raw)
    active = rules.active(surface, mode)

    findings: List[Finding] = []

    def add(r, line, col, message):
        findings.append(Finding(line, col, r.code, r.name, r.level(mode), message))

    for r in active:
        if r.scope == "document":
            doc = _document_text(raw, kinds)
            starts = [0] + [m.end() for m in re.finditer("\n", doc)]
            for offset, message in r.check(doc, ctx):
                n = bisect.bisect_right(starts, offset) - 1
                add(r, n + 1, offset - starts[n] + 1, message)
            continue
        for seg in segs:
            if r.scope == "text" and seg.kind in ("block", "table"):
                for offset, message in r.check(seg.text, ctx):
                    add(r, *seg.locate(offset), message)
            elif r.scope == "sentence" and seg.kind == "block":
                for sentence in seg.sentences:
                    for _, message in r.check(sentence.text, ctx):
                        add(r, sentence.line, sentence.col, message)
            elif r.scope == "paragraph" and seg.kind == "paragraph":
                for offset, message in r.check(seg.text, ctx):
                    add(r, *seg.locate(offset), message)

    findings.sort(key=lambda f: (f.line, f.col, f.code))
    return findings
