"""Find the comment blocks in source files.

The scanner is a tokenizer, not a parser. It tracks string literals, so a
`//` inside a URL string is not a comment. It joins adjacent line comments
into one block. It knows nothing more about the language.
"""

from __future__ import annotations

import os
import sys
from typing import Iterator, List, Optional, Set

from ..model import CommentBlock
from .flags import flags_for
from .languages import SKIP_DIRS, STYLES, platform_words, style_for


def _clean_block(body: str) -> str:
    cleaned = []
    for line in body.lstrip("*!").splitlines():
        s = line.strip()
        if s.startswith("*"):
            s = s[1:].strip()
        cleaned.append(s)
    while cleaned and not cleaned[0]:
        cleaned.pop(0)
    while cleaned and not cleaned[-1]:
        cleaned.pop()
    return "\n".join(cleaned)


def scan(text: str, style: str) -> List[dict]:
    """Return the raw comments as dicts: line, end, kind, text, trailing."""
    line_prefixes, block_pairs = STYLES[style]
    n = len(text)
    i = 0
    line = 1
    line_start = 0
    out: List[dict] = []

    def code_before(pos: int) -> bool:
        return text[line_start:pos].strip() != ""

    while i < n:
        ch = text[i]
        if ch == "\n":
            line += 1
            i += 1
            line_start = i
            continue

        matched = False
        for open_tok, close_tok in block_pairs:
            if not text.startswith(open_tok, i):
                continue
            end = text.find(close_tok, i + len(open_tok))
            if style == "python" and code_before(i):
                # A triple-quoted string inside a statement is data.
                end = n if end < 0 else end + len(close_tok)
                line += text.count("\n", i, end)
                i = end
                matched = True
                break
            end = n if end < 0 else end
            body = text[i + len(open_tok):end]
            is_doc = style == "python" or body.startswith(("*", "!"))
            out.append({
                "line": line,
                "end": line + body.count("\n"),
                "kind": "doc" if is_doc else "block",
                "text": _clean_block(body),
                "trailing": code_before(i),
            })
            line += text.count("\n", i, end)
            i = end + len(close_tok)
            matched = True
            break
        if matched:
            continue

        for prefix in line_prefixes:
            if text.startswith(prefix, i) and (
                prefix != "#" or i == line_start or text[i - 1] in " \t"
            ):
                end = text.find("\n", i)
                end = n if end < 0 else end
                raw = text[i + len(prefix):end]
                marker = raw[:1] if raw[:1] in ("/", "!") else ""
                if i == 0 and prefix == "#" and raw.startswith("!"):
                    kind = "shebang"
                elif marker and style == "c-family":
                    kind = "doc"
                else:
                    kind = "line"
                out.append({
                    "line": line,
                    "end": line,
                    "kind": kind,
                    "text": raw.lstrip("/!").strip(),
                    "trailing": code_before(i),
                    "indent": i - line_start,
                    "marker": marker,
                })
                i = end
                matched = True
                break
        if matched:
            continue

        # A quote opens a string only when it closes on the same line.
        # Backticks and triple quotes can span lines.
        if (ch in "\"'`" and style != "hash") or (style == "hash" and ch in "\"'"):
            if style == "python" and text.startswith(ch * 3, i):
                i += 3
                continue
            eol = text.find("\n", i)
            eol = n if eol < 0 else eol
            j = i + 1
            closed = -1
            while j < (n if ch == "`" else eol):
                if text[j] == "\\":
                    j += 2
                    continue
                if text[j] == ch:
                    closed = j
                    break
                j += 1
            if closed >= 0:
                line += text.count("\n", i, closed)
                i = closed + 1
                continue
        i += 1
    return out


def group(raw: List[dict]) -> List[dict]:
    """Join adjacent line comments with the same indent and marker."""
    blocks: List[dict] = []
    for c in raw:
        prev = blocks[-1] if blocks else None
        if (
            prev is not None
            and c["kind"] in ("line", "doc") and c["kind"] == prev["kind"]
            and "indent" in c and "indent" in prev
            and not c["trailing"] and not prev["trailing"]
            and c["line"] == prev["end"] + 1
            and c["indent"] == prev["indent"]
            and c["marker"] == prev["marker"]
        ):
            prev["end"] = c["line"]
            prev["text"] = prev["text"] + "\n" + c["text"]
            continue
        blocks.append(dict(c))
    return blocks


def _next_code(lines: List[str], end: int, comment_lines: Set[int]) -> str:
    for idx in range(end, min(end + 5, len(lines))):
        if idx + 1 in comment_lines:
            continue
        s = lines[idx].strip()
        if s:
            return s
    return ""


def analyze(path: str, text: str, style: str,
            added: Optional[Set[int]] = None) -> List[CommentBlock]:
    """Return the flagged comment blocks of one file.

    `added` is the set of added line numbers in a diff scan, or `None`.
    """
    blocks = group(scan(text, style))
    lines = text.split("\n")
    platform = platform_words(path)
    comment_lines: Set[int] = set()
    for b in blocks:
        if not b["trailing"]:
            comment_lines.update(range(b["line"], b["end"] + 1))

    out = []
    for b in blocks:
        if b["kind"] == "shebang":
            continue
        body = b["text"].strip()
        nxt = _next_code(lines, b["end"], comment_lines)
        block = CommentBlock(
            path=path, line=b["line"], end=b["end"], kind=b["kind"],
            trailing=b["trailing"], text=body, next_code=nxt,
            flags=flags_for(body, b["kind"], b["end"] - b["line"] + 1, nxt, platform),
        )
        if added is not None:
            block.new = any(n in added for n in range(b["line"], b["end"] + 1))
        out.append(block)
    return out


def source_files(paths: List[str]) -> Iterator[str]:
    """Yield the source files under `paths` that have a known comment style."""
    for p in paths:
        if os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
                for f in sorted(files):
                    fp = os.path.join(root, f)
                    if style_for(fp):
                        yield fp
        elif os.path.isfile(p):
            yield p
        else:
            print(f"writing-for-code: no such path: {p}", file=sys.stderr)
