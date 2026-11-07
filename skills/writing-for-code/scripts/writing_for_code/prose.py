"""Check prose and retain source offsets for diagnostics."""

import bisect
import re


SURFACES = ("comment", "docstring", "readme", "doc", "guide", "adr", "procedure", "error",
            "log", "cli-help", "changelog", "commit", "pr", "issue", "review")
STRICT_SURFACES = {"procedure", "error", "log", "cli-help"}
WORDY = {
    "begin": "start", "commence": "start", "initiate": "start",
    "utilize": "use", "utilizes": "uses", "utilizing": "using",
    "leverage": "use", "facilitate": "help", "ensure": "make sure",
    "prior to": "before", "subsequent to": "after", "obtain": "get",
    "acquire": "get", "demonstrate": "show", "additionally": "also",
    "furthermore": "also", "moreover": "also", "numerous": "many",
    "myriad": "many", "in order to": "to", "regarding": "about",
    "concerning": "about", "due to the fact that": "because",
}
STYLE = {
    "praise": r"\b(?:seamless(?:ly)?|robust|powerful|cutting-edge|effortless|"
              r"world-class|revolutionary|comprehensive|game-changing)\b",
    "filler": r"\b(?:it is important to note|it should be noted|needless to say|"
              r"it is worth noting|as mentioned above)\b",
    "passive": r"\b(?:is|are|was|were|been|be)\s+(?:\w+ed|written|made|sent|"
               r"built|given|shown|found|kept|read|taken)\b",
    "nominalization": r"\b(?:perform|conduct|carry out)\s+(?:an? |the )?"
                      r"\w+(?:tion|sis|ment|ance|ence)\b",
    "phrasal": r"\b(?:spin up|tear down|reach out|dive into|kick off|track down)\b",
    "progressive": r"\b(?:is|are|was|were)\s+(?!missing\b|nothing\b|willing\b)\w+ing\b",
}
RULES = {
    "sentence-length": ("error", "error", "Split sentences over 20 words in strict mode or 25 in flavored mode."),
    "semicolon": ("error", "error", "Write two sentences instead of a semicolon."),
    "contraction": ("error", "error", "Expand the contraction."),
    "word-choice": ("error", "warning", "Prefer the short common word."),
    "paragraph-length": ("warning", "warning", "Split paragraphs over six sentences."),
    "praise": ("warning", "warning", "Replace generic praise with a supported fact."),
    "filler": ("warning", "warning", "Check whether the phrase adds useful information."),
    "passive": ("warning", "warning", "If the actor matters, name it and use active voice."),
    "nominalization": ("warning", "warning", "Consider a plain verb."),
    "phrasal": ("warning", "warning", "Consider a plain verb."),
    "progressive": ("warning", "warning", "Consider a simple tense if the meaning stays the same."),
    "comment-change": ("warning", "warning", "Describe the code, not the editing session."),
    "comment-cross-ref": ("warning", "warning", "Check whether the reference explains a useful constraint."),
    "comment-story": ("warning", "warning", "State the symptom and cause without the debug history."),
    "comment-long": ("warning", "warning", "Check whether this inline comment needs more than three lines."),
    "commit-subject": ("error", "error", "Keep the commit subject at most 72 characters."),
}
CONTRACTION = re.compile(r"\b(?:\w+['\u2019](?:t|re|ve|ll|d|m)|"
                         r"(?:it|that|there|here|what|who|he|she|let|this)['\u2019]s)\b", re.I)
WORDS = re.compile(r"[^\W_]+(?:['\u2019/-][^\W_]+)*", re.UNICODE)
LEAD = re.compile(r"^[ \t]*(?:#{1,6}\s+|(?:[-*+]|\d+[.)])\s+)")


def _blank(text):
    return "".join("\n" if c == "\n" else " " for c in text)


def mask(text, indented_code=True):
    """Mask code, quotations, URLs, and disabled regions without moving characters."""
    lines = text.splitlines(keepends=True)
    off = front = indented = quote = False
    previous_blank = True
    fence = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if fence:
            marker = re.match(r"^ {0,3}(`{3,}|~{3,})\s*$", line)
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence):
                fence = None
            lines[i] = _blank(line)
            continue
        disable = re.search(r"<!--\s*(?:ste-lint|writing-for-code|wfc):\s*(off|on)\s*-->", line)
        if disable or off:
            if disable:
                off = disable[1] == "off"
            lines[i] = _blank(line)
            continue
        if i == 0 and stripped == "---":
            front = True
            lines[i] = _blank(line)
            continue
        if front:
            lines[i] = _blank(line)
            if stripped in ("---", "..."):
                front = False
            continue
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if marker:
            fence = marker[1]
            lines[i] = _blank(line)
            continue
        if stripped.startswith(">") or (quote and stripped and not LEAD.match(line)):
            lines[i] = _blank(line)
            quote = True
            continue
        quote = False
        if indented_code and re.match(r"^(?: {4}|\t)", line) and (previous_blank or indented) and not LEAD.match(line):
            lines[i] = _blank(line)
            indented = True
        elif stripped:
            indented = False
        previous_blank = not stripped
    result = "".join(lines)
    for pattern in (
        r"<!--.*?(?:-->|\Z)",
        r"(`+)(?!`)(.*?)(?<!`)\1(?!`)",
        r'"[^"\n]*"|\u201c[^\u201d]*\u201d',
        r"(?<!\w)'[^'\n]+'(?!\w)",
        r"!\[[^\]\n]*\]\([^\n)]*\)",
        r"(?<=\])\([^\n)]*\)",
        r"<https?://[^>\s]*>|https?://[^\s<>]+",
        r"(?m)^ {0,3}\[[^]\n]+\]:[^\n]*",
        r"\$?\{\{.*?\}\}",
    ):
        result = re.sub(pattern, lambda m: _blank(m[0]), result, flags=re.S)
    return result


def position(text, offset):
    """Return the one-based line and character column for offset in text."""
    return text.count("\n", 0, offset) + 1, offset - text.rfind("\n", 0, offset)


def finding(text, code, offset, start, end, mode, surface, message=None):
    """Build a diagnostic for offset and the affected span in text."""
    line, column = position(text, offset)
    end_line, _ = position(text, max(start, end - 1))
    start_line, _ = position(text, start)
    return {"line": line, "column": column, "code": code, "rule": code,
            "level": RULES[code][0 if mode == "strict" else 1],
            "message": message or RULES[code][2], "surface": surface,
            "start_line": start_line, "end_line": end_line,
            "_offset": offset, "_start": start, "_end": end}


def lint(text, surface="doc", mode=None, source=False):
    """Return findings for text on surface in strict or flavored mode."""
    if surface not in SURFACES:
        raise ValueError("Unknown surface: " + surface)
    mode = mode or ("strict" if surface in STRICT_SURFACES else "flavored")
    if mode not in ("strict", "flavored"):
        raise ValueError("Unknown mode: " + mode)
    blocks, current = [], []
    offset = 0
    for line in mask(text, indented_code=not source).splitlines(keepends=True):
        if not line.strip() or LEAD.match(line) or line.lstrip().startswith("|"):
            if current:
                blocks.append(current)
                current = []
        if line.strip():
            lead = LEAD.match(line)
            start = lead.end() if lead else len(line) - len(line.lstrip())
            current.append((offset + start, line[start:].rstrip("\r\n")))
            if line.lstrip().startswith(("|", "#")):
                blocks.append(current)
                current = []
        offset += len(line)
    if current:
        blocks.append(current)
    out = []
    for block in blocks:
        joined, offsets = "", []
        for start, line in block:
            if joined:
                joined += " "
                offsets.append(start - 1)
            joined += line
            offsets.extend(range(start, start + len(line)))
        sentences = list(re.finditer(r"\S.*?(?:[.!?](?=\s|$)|$)", joined))
        if not sentences:
            continue
        ends = [m.end() for m in sentences]

        def add(code, at, message=None, whole=False):
            sentence = sentences[min(bisect.bisect_right(ends, at), len(sentences) - 1)]
            left = 0 if whole else sentence.start()
            right = len(joined) if whole else sentence.end()
            out.append(finding(text, code, offsets[at], offsets[left],
                               offsets[right - 1] + 1, mode, surface, message))

        for code, pattern in (("semicolon", r";"), ("contraction", CONTRACTION), *STYLE.items()):
            for match in re.finditer(pattern, joined, re.I) if isinstance(pattern, str) else pattern.finditer(joined):
                if code == "passive" and match[0].split()[-1].lower() in {
                    "tired", "based", "related", "unrelated", "involved", "detailed", "limited",
                    "advanced", "complicated", "interested", "concerned", "deprecated",
                }:
                    continue
                add(code, match.start())
        for phrase, replacement in WORDY.items():
            pattern = r"(?<![\w-])" + re.escape(phrase).replace(r"\ ", r"\s+") + r"(?![\w-])"
            for match in re.finditer(pattern, joined, re.I):
                add("word-choice", match.start(), "Prefer " + repr(replacement) + " to " + repr(phrase) + ".")
        if not joined.lstrip().startswith("|"):
            cap = 20 if mode == "strict" else 25
            for sentence in sentences:
                count = len(WORDS.findall(sentence[0]))
                if count > cap:
                    add("sentence-length", sentence.start(), f"Sentence has {count} words. The limit is {cap}.")
            if len(sentences) > 6:
                add("paragraph-length", sentences[0].start(), whole=True)
    if surface == "commit" and text.splitlines() and len(text.splitlines()[0]) > 72:
        out.append(finding(text, "commit-subject", 0, 0, len(text.splitlines()[0]), mode, surface))
    return sorted(out, key=lambda f: (f["line"], f["column"], f["code"]))
