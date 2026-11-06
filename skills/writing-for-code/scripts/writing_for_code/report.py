"""Text and JSON output."""

from __future__ import annotations

import json
from typing import Dict, List, TextIO

from .model import ERROR, WARNING, CommentBlock, Finding


def count(findings: List[Finding], level: str) -> int:
    return sum(1 for f in findings if f.level == level)


def findings_text(label: str, findings: List[Finding], out: TextIO) -> None:
    for f in findings:
        out.write(f"{label}:{f.line}:{f.col}: {f.level} {f.code} {f.rule}: "
                  f"{f.message}\n")


def summary(findings: List[Finding], files: int, out: TextIO, note: str = "") -> None:
    out.write(f"\n{count(findings, ERROR)} error(s), {count(findings, WARNING)} "
              f"warning(s) in {files} file(s){note}\n")


def blocks_text(blocks: List[CommentBlock], show_all: bool, out: TextIO) -> None:
    counts: Dict[str, int] = {}
    for b in blocks:
        if not show_all and not b.flags and not b.lint:
            continue
        for flag in b.flags:
            counts[flag] = counts.get(flag, 0) + 1
        span = str(b.line) if b.line == b.end else f"{b.line}-{b.end}"
        tag = " new" if b.new else ""
        out.write(f"{b.path}:{span}: [{b.kind}{tag}] {', '.join(b.flags) or '-'}\n")
        lines = b.text.splitlines()
        for ln in lines[:6]:
            out.write(f"    | {ln}\n")
        if len(lines) > 6:
            out.write("    | ...\n")
        if b.next_code:
            out.write(f"    > {b.next_code[:100]}\n")
        for f in b.lint:
            out.write(f"    ! {f.level} {f.code} {f.rule}: {f.message}\n")
        out.write("\n")
    flagged = sum(1 for b in blocks if b.flags)
    detail = ", ".join(f"{k} {v}" for k, v in sorted(counts.items()))
    out.write(f"{len(blocks)} comment block(s), {flagged} flagged"
              f"{'. ' + detail if detail else ''}\n")


def dump(payload: object, out: TextIO) -> None:
    json.dump(payload, out, indent=2)
    out.write("\n")
