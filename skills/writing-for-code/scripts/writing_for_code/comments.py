"""Extract source comments without changing their character positions."""

import ast
import io
import re
import tokenize
from pathlib import Path

from .prose import _blank, finding, lint, mask


EXTENSIONS = {".py", ".pyi", ".swift", ".kt", ".kts", ".rs", ".go", ".java",
              ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".c", ".h", ".cpp", ".hpp"}
DIRECTIVE = re.compile(r"(?:SPDX-License|copyright|licensed under|noqa|type:\s*ignore|"
                       r"eslint|prettier-ignore|swiftlint:|nolint|go:build|MARK:|#pragma|"
                       r"@ts-(?:ignore|expect-error)|<reference\b)", re.I)
FLAGS = {
    "comment-change": r"\b(?:now|newly|updated to|changed from|as requested|per the ticket)\b",
    "comment-cross-ref": r"\b(?:mirrors|same pattern as|matches the implementation|ported from)\b",
    "comment-story": r"\b(?:we found|we discovered|turned out|after hours|after a long debug)\b",
}


def extract(path, text):
    """Return (start, end, docstring) spans from supported source text at path.

    Raises ValueError for unsupported files or invalid Python syntax.
    """
    ext = Path(path).suffix.lower()
    if ext not in EXTENSIONS:
        raise ValueError("Unsupported source file: " + str(path))
    spans = []
    if ext in {".py", ".pyi"}:
        starts = [0]
        starts.extend(m.end() for m in re.finditer("\n", text))
        try:
            tree = ast.parse(text)
            docs = set()
            for node in ast.walk(tree):
                if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    if node.body and isinstance(node.body[0], ast.Expr):
                        value = node.body[0].value
                        if isinstance(value, ast.Constant) and isinstance(value.value, str):
                            line = text.splitlines()[value.lineno - 1]
                            col = len(line.encode("utf-8")[:value.col_offset].decode("utf-8"))
                            docs.add((value.lineno, col))
            for token in tokenize.generate_tokens(io.StringIO(text).readline):
                if token.type not in (tokenize.COMMENT, tokenize.STRING):
                    continue
                start = starts[token.start[0] - 1] + token.start[1]
                end = starts[token.end[0] - 1] + token.end[1]
                if token.type == tokenize.COMMENT:
                    if not token.string.startswith("#!"):
                        spans.append((start + 1, end, False))
                elif token.type == tokenize.STRING and token.start in docs:
                    opener = re.match(r"(?i)[ru]*(\"\"\"|'''|\"|')", token.string)
                    if opener:
                        spans.append((start + opener.end(), end - len(opener[1]), True))
        except (SyntaxError, tokenize.TokenError, IndentationError) as exc:
            raise ValueError("Cannot scan Python source: " + str(exc)) from exc
        return spans
    i, size = 0, len(text)
    while i < size:
        if text.startswith("//", i):
            end = text.find("\n", i)
            end = size if end < 0 else end
            width = 3 if text.startswith(("///", "//!"), i) else 2
            spans.append((i + width, end, width == 3))
            i = end
        elif text.startswith("/*", i):
            start, depth = i, 1
            i += 2
            nested = ext in {".rs", ".swift", ".kt", ".kts"}
            while i < size and depth:
                if text.startswith("*/", i):
                    depth -= 1
                    i += 2
                elif nested and text.startswith("/*", i):
                    depth += 1
                    i += 2
                else:
                    i += 1
            doc = text.startswith(("/**", "/*!"), start)
            spans.append((start + (3 if doc else 2), i - (2 if not depth else 0), doc))
        else:
            raw = None
            if ext == ".rs":
                raw = re.match(r'(?:br|r)(#{0,255})"', text[i:])
                close = '"' + raw[1] if raw else None
            elif ext == ".swift":
                raw = re.match(r'(#+)("""|")', text[i:])
                close = raw[2] + raw[1] if raw else None
            elif ext in {".cpp", ".hpp", ".c", ".h"}:
                raw = re.match(r'(?:u8|u|U|L)?R"([^\s()\\]{0,16})\(', text[i:])
                close = ")" + raw[1] + '"' if raw else None
            if raw:
                end = text.find(close, i + raw.end())
                i = size if end < 0 else end + len(close)
            elif text[i] in "\"'`":
                if ext == ".rs" and text[i] == "'" and not re.match(r"'(?:\\.|[^'\n])'", text[i:]):
                    i += 1
                    continue
                quote = text[i]
                delimiter = quote * 3 if text.startswith(quote * 3, i) else quote
                i += len(delimiter)
                while i < size:
                    if text.startswith(delimiter, i):
                        i += len(delimiter)
                        break
                    if text[i] == "\\" and not (ext == ".go" and delimiter == "`"):
                        i += 2
                    else:
                        i += 1
            else:
                i += 1
    return spans


def analyze(path, text, surface=None, mode=None):
    """Return advisory findings for source text at path, with source coordinates."""
    spans = extract(path, text)
    groups = []
    for start, end, doc in spans:
        if DIRECTIVE.search(text[start:end]):
            continue
        if groups and groups[-1][2] == doc and re.fullmatch(r"\s*(?://[/!]?)?", text[groups[-1][1]:start]):
            groups[-1][1] = end
            groups[-1][3].append((start, end))
        else:
            groups.append([start, end, doc, [(start, end)]])
    out = []
    for start, end, doc, parts in groups:
        chars = list(_blank(text))
        for left, right in parts:
            chars[left:right] = text[left:right]
        block = "".join(chars)
        block = re.sub(r"(?m)^([ \t]*)\*( ?)", lambda m: _blank(m[0]), block)
        kind = surface or ("docstring" if doc else "comment")
        findings = lint(block, kind, mode, source=True)
        visible = mask(block, indented_code=False)
        for code, pattern in FLAGS.items():
            for match in re.finditer(pattern, visible, re.I):
                findings.append(finding(text, code, match.start(), start, end, mode, kind))
        if not doc and text[start:end].count("\n") >= 3:
            findings.append(finding(text, "comment-long", start, start, end, mode, kind))
        for item in findings:
            item["level"] = "warning"
        out.extend(findings)
    return sorted(out, key=lambda item: (item["line"], item["column"], item["code"]))
