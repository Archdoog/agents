"""Comment syntax for each file type."""

from __future__ import annotations

import os
import re
from typing import Dict, List, Optional, Pattern, Tuple

# Syntax family -> (line comment prefixes, block comment (open, close) pairs).
STYLES: Dict[str, Tuple[List[str], List[Tuple[str, str]]]] = {
    "c-family": (["//"], [("/*", "*/")]),
    "hash": (["#"], []),
    "python": (["#"], [('"""', '"""'), ("'''", "'''")]),
    "html": ([], [("<!--", "-->")]),
    "css": ([], [("/*", "*/")]),
    "sql": (["--"], [("/*", "*/")]),
    "lua": (["--"], [("--[[", "]]")]),
}

EXTENSIONS = {
    "c-family": [
        ".c", ".h", ".cc", ".cpp", ".hpp", ".m", ".mm", ".java", ".kt", ".kts",
        ".swift", ".go", ".rs", ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx",
        ".scala", ".dart", ".cs", ".groovy", ".gradle", ".proto",
    ],
    "hash": [
        ".sh", ".bash", ".zsh", ".yml", ".yaml", ".toml", ".rb", ".pl", ".r",
        ".conf", ".ini", ".mk", ".nix", ".tf", ".hcl", ".ps1",
    ],
    "python": [".py", ".pyi"],
    "html": [".html", ".htm", ".xml", ".svg", ".vue"],
    "css": [".css", ".scss", ".less"],
    "sql": [".sql"],
    "lua": [".lua"],
}

FILENAMES = {
    "Makefile": "hash", "Dockerfile": "hash", "Justfile": "hash",
    "justfile": "hash", ".gitignore": "hash", ".env": "hash",
}

EXT_TO_STYLE = {ext: style for style, exts in EXTENSIONS.items() for ext in exts}

# Words that name a sibling platform, by the extension of the file they are in.
PLATFORM_WORDS: Dict[Tuple[str, ...], Pattern] = {
    (".swift", ".m", ".mm"): re.compile(r"\b(android|kotlin|jetpack|gradle)\b", re.I),
    (".kt", ".kts", ".java"): re.compile(r"\b(ios|ipados|swift|swiftui|uikit|xcode)\b", re.I),
}

SKIP_DIRS = {
    ".git", "node_modules", "build", "dist", "target", "vendor", ".gradle",
    "Pods", "DerivedData", "__pycache__", ".venv", "venv", ".claude",
}


def style_for(path: str) -> Optional[str]:
    base = os.path.basename(path)
    if base in FILENAMES:
        return FILENAMES[base]
    return EXT_TO_STYLE.get(os.path.splitext(base)[1].lower())


def platform_words(path: str) -> Optional[Pattern]:
    ext = os.path.splitext(path)[1].lower()
    for exts, pattern in PLATFORM_WORDS.items():
        if ext in exts:
            return pattern
    return None
