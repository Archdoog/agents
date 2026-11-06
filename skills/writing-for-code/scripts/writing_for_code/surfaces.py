"""The surfaces: each kind of prose this tool checks, and its mode.

This table is the only place that maps a surface to a mode. A rule limits
itself to surfaces with `surfaces=` in its `@rule` call.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict

STRICT = "strict"
FLAVORED = "flavored"


@dataclass(frozen=True)
class Surface:
    name: str
    mode: str
    guide: str      # the file in surfaces/ that covers it
    summary: str


SURFACES: Dict[str, Surface] = {s.name: s for s in [
    Surface("comment", FLAVORED, "comments.md", "inline and block code comments"),
    Surface("docstring", FLAVORED, "docstrings.md", "docstrings and module docs"),
    Surface("readme", FLAVORED, "docs.md", "README files"),
    Surface("doc", FLAVORED, "docs.md", "guides, docs/ pages, ADRs, CONTRIBUTING"),
    Surface("procedure", STRICT, "docs.md", "runbooks and numbered procedures"),
    Surface("error", STRICT, "errors.md", "error messages, log lines, CLI help"),
    Surface("changelog", FLAVORED, "changelog.md", "CHANGELOG entries"),
    Surface("commit", FLAVORED, "commits.md", "commit messages"),
    Surface("pr", FLAVORED, "pull-requests.md", "pull request titles and bodies"),
    Surface("issue", FLAVORED, "issues.md", "issue bodies and comments"),
    Surface("review", FLAVORED, "reviews.md", "review comments and summaries"),
]}

DEFAULT = "doc"


def for_path(path: str) -> str:
    """Guess the surface of a markdown or text file from its name."""
    name = os.path.basename(path).lower()
    if name.startswith("readme"):
        return "readme"
    if name.startswith(("changelog", "changes", "history", "news")):
        return "changelog"
    if "runbook" in path.lower() or "playbook" in path.lower():
        return "procedure"
    return DEFAULT


def mode_for(surface: str, strict: bool = False) -> str:
    return STRICT if strict else SURFACES[surface].mode
