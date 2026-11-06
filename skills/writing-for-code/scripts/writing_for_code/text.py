"""Split markdown or plain text into the prose that the rules read.

The masks replace quoted material with spaces and keep every newline, so each
line and column in a finding points at the real source. The masks cover code
blocks, code spans, command lines, blockquotes, quoted text, YAML
frontmatter, HTML, URLs, link targets, and the text between `<!-- writing-for-code: off -->` and
`<!-- writing-for-code: on -->`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, List, Tuple

PROSE = "prose"
TABLE = "table"
BLANK = "blank"
SKIP = "skip"

OFF_SWITCH = re.compile(r"<!--\s*(?:writing-for-code|ste-lint):\s*off\s*-->")
ON_SWITCH = re.compile(r"<!--\s*(?:writing-for-code|ste-lint):\s*on\s*-->")

INLINE_MASKS = [
    re.compile(r"`[^`\n]*`"),                    # code span
    re.compile(r"<!--.*?-->"),                   # HTML comment on one line
    re.compile(r"\]\([^)]*\)"),                  # link target
    re.compile(r"<https?://[^>\s]*>"),           # autolink
    re.compile(r"https?://\S+"),                 # bare URL
    re.compile(r"^\s*\[[^\]]+\]:\s*\S+", re.M),  # link reference definition
    re.compile(r"\$\{\{[^}]*\}\}"),              # GitHub Actions expression
    re.compile(r"\{\{[^}]*\}\}"),                # template placeholder
    re.compile(r"<[^>\n]+>"),                    # HTML tag
    re.compile(r'(?<![\w"])"[^"\n]{1,160}"(?![\w"])'),  # quoted text
    re.compile(r"“[^”\n]{1,160}”"),             # quoted text, curly quotes
]

# A code span in flowed markdown can wrap onto the next line.
WRAPPED_CODE = re.compile(r"`[^`]{0,400}`", re.S)

LEAD = re.compile(r"^\s*(?:#{1,6}\s+|(?:[-*+]|\d+[.)])\s+)")
# A full stop splits before any word, except after "e.g.", "i.e.", or "vs.".
# A colon splits only before a capital, so "Usage: run it" stays whole.
SENTENCE_SPLIT = re.compile(
    r"(?<!\be\.g\.)(?<!\bi\.e\.)(?<!\bvs\.)(?<=[.!?])\s+(?=\S)"
    r"|(?<=:)\s+(?=[A-Z0-9\"'(\[])"
)
WORD = re.compile(r"[A-Za-z0-9][A-Za-z0-9'’\-/]*")
INDENTED = re.compile(r"^(?: {4,}|\t)")
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
# Two or more spaces inside a line, not after a full stop, align columns.
ALIGNED = re.compile(r"\S(?<![.!?:]) {2,}\S")
COMMAND = re.compile(r"^\s*(?:\$ |\./|python3? |git |npm |npx |cargo |swift |go )")

Locate = Callable[[int], Tuple[int, int]]


@dataclass
class Sentence:
    text: str
    line: int
    col: int

    def word_count(self) -> int:
        return len(WORD.findall(self.text))


@dataclass
class Segment:
    """A run of prose lines joined into one string.

    `locate` maps an offset in `text` to a 1-based (line, column).

    `kind` is one of:

    - `block`: a paragraph or one list item.
    - `table`: one table row, or one line of aligned columns.
    - `paragraph`: prose lines between blank lines. A list is not a paragraph.
    """

    kind: str
    text: str
    locate: Locate
    sentences: List[Sentence]
    first_line: int


def _blank(match: re.Match) -> str:
    return " " * (match.end() - match.start())


def _blank_keep_newlines(match: re.Match) -> str:
    return "".join("\n" if ch == "\n" else " " for ch in match.group(0))


def classify(lines: List[str]) -> List[str]:
    """Tag each line as prose, table, blank, or skip."""
    kinds: List[str] = []
    in_fence = False
    fence_char = ""
    in_frontmatter = False
    in_html_comment = False
    off = False

    for i, raw in enumerate(lines):
        stripped = raw.strip()

        if i == 0 and stripped == "---":
            in_frontmatter = True
            kinds.append(SKIP)
            continue
        if in_frontmatter:
            kinds.append(SKIP)
            if stripped == "---":
                in_frontmatter = False
            continue

        if not off and OFF_SWITCH.match(stripped):
            off = True
            kinds.append(SKIP)
            continue
        if off:
            kinds.append(SKIP)
            if ON_SWITCH.match(stripped):
                off = False
            continue

        fence = re.match(r"^\s*(`{3,}|~{3,})", raw)
        if in_fence:
            kinds.append(SKIP)
            if fence and fence.group(1)[0] == fence_char:
                in_fence = False
            continue
        if fence:
            in_fence = True
            fence_char = fence.group(1)[0]
            kinds.append(SKIP)
            continue

        if in_html_comment:
            kinds.append(SKIP)
            if "-->" in raw:
                in_html_comment = False
            continue
        if stripped.startswith("<!--") and "-->" not in raw:
            in_html_comment = True
            kinds.append(SKIP)
            continue

        if not stripped:
            kinds.append(BLANK)
        elif stripped.startswith(">"):
            kinds.append(SKIP)
        elif stripped.startswith("|"):
            kinds.append(TABLE)
        elif re.match(r"^\s*[-*_]{3,}\s*$", raw):
            kinds.append(BLANK)
        elif COMMAND.match(raw):
            kinds.append(SKIP)
        elif ALIGNED.search(raw.strip()):
            kinds.append(TABLE)
        else:
            kinds.append(PROSE)

    # An indented run after a blank line is a code sample, unless it opens
    # with a list marker. Two-space wrapped list items stay prose.
    i = 0
    while i < len(lines):
        if kinds[i] == PROSE and INDENTED.match(lines[i]):
            prev = kinds[i - 1] if i > 0 else BLANK
            if prev == BLANK and not LIST_ITEM.match(lines[i]):
                while i < len(lines) and (
                    kinds[i] == BLANK
                    or (kinds[i] == PROSE and INDENTED.match(lines[i]))
                ):
                    if kinds[i] == PROSE:
                        kinds[i] = SKIP
                    i += 1
                continue
        i += 1
    return kinds


def mask(lines: List[str], kinds: List[str]) -> List[str]:
    """Return the lines with skipped lines emptied and quoted spans blanked."""
    out = []
    for line, kind in zip(lines, kinds):
        if kind == SKIP:
            out.append("")
            continue
        for pattern in INLINE_MASKS:
            line = pattern.sub(_blank, line)
        out.append(line)
    # A backtick that is still open here starts a span that wraps lines.
    return WRAPPED_CODE.sub(_blank_keep_newlines, "\n".join(out)).split("\n")


def join(lines: List[str], indices: List[int]) -> Tuple[str, Locate]:
    """Join lines into one string, with a map from offset to (line, column).

    A sentence or a two-word phrase can wrap onto the next line, so the rules
    read the joined string.
    """
    joined = ""
    index = []  # (offset in joined, line index, column in line)
    for n, i in enumerate(indices):
        text = lines[i]
        lead = LEAD.match(text)
        start = lead.end() if lead else len(text) - len(text.lstrip())
        if n:
            joined += " "
        index.append((len(joined), i, start))
        joined += text[start:].rstrip()

    def locate(offset: int) -> Tuple[int, int]:
        line_no, col = index[0][1], index[0][2]
        for off, ln, c in index:
            if off > offset:
                break
            line_no, col = ln, c + (offset - off)
        return line_no + 1, col + 1

    return joined, locate


def split_sentences(text: str, locate: Locate) -> List[Sentence]:
    out = []
    offset = 0
    for part in SENTENCE_SPLIT.split(text):
        offset = text.find(part, offset)
        if part.strip():
            lead = len(part) - len(part.lstrip())
            line, col = locate(offset + lead)
            out.append(Sentence(part.strip(), line, col))
        offset += len(part)
    return out


def _segment(kind: str, lines: List[str], indices: List[int]) -> Segment:
    text, locate = join(lines, indices)
    sentences = split_sentences(text, locate) if kind != "table" else []
    return Segment(kind, text, locate, sentences, indices[0] + 1)


def segments(raw: str) -> Tuple[List[Segment], List[str], List[str]]:
    """Split text into segments. Return the segments, the masked lines, and
    the line kinds."""
    lines = raw.split("\n")
    kinds = classify(lines)
    masked = mask(lines, kinds)
    out: List[Segment] = []

    # Blocks: a heading or a list item starts a new block, so a wrapped
    # sentence never joins the bullet above it.
    current: List[int] = []
    for i, kind in enumerate(kinds):
        if kind != PROSE:
            if current:
                out.append(_segment("block", masked, current))
                current = []
            continue
        if current and LEAD.match(lines[i]):
            out.append(_segment("block", masked, current))
            current = []
        current.append(i)
    if current:
        out.append(_segment("block", masked, current))

    for i, kind in enumerate(kinds):
        if kind == TABLE:
            out.append(_segment("table", masked, [i]))

    # Paragraphs: prose runs between blank lines. A list is not a paragraph.
    run: List[int] = []
    for i, kind in enumerate(kinds + [BLANK]):
        if kind == PROSE:
            run.append(i)
            continue
        if run and not any(LEAD.match(lines[n]) for n in run):
            out.append(_segment("paragraph", masked, run))
        run = []

    return out, masked, kinds


def blank_lines(raw: str, drop: Callable[[str], bool]) -> str:
    """Empty each line for which `drop` is true. Line numbers stay the same."""
    return "\n".join("" if drop(line) else line for line in raw.split("\n"))
