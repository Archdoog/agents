"""Data types that the rules, the comment scanner, and the reports share."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

ERROR = "error"
WARNING = "warning"
OFF = "off"


@dataclass
class Finding:
    """One rule break at a 1-based line and column."""

    line: int
    col: int
    code: str
    rule: str
    level: str
    message: str

    def as_dict(self) -> dict:
        return {
            "line": self.line,
            "column": self.col,
            "code": self.code,
            "rule": self.rule,
            "level": self.level,
            "message": self.message,
        }


@dataclass
class CommentBlock:
    """One comment, or a run of adjacent line comments, in a source file.

    `kind` is `line`, `block`, or `doc`. `new` is `None` outside a diff scan.
    """

    path: str
    line: int
    end: int
    kind: str
    trailing: bool
    text: str
    next_code: str = ""
    flags: List[str] = field(default_factory=list)
    new: Optional[bool] = None
    lint: List[Finding] = field(default_factory=list)

    def as_dict(self) -> dict:
        out = {
            "path": self.path,
            "line": self.line,
            "end": self.end,
            "kind": self.kind,
            "trailing": self.trailing,
            "text": self.text,
            "next_code": self.next_code,
            "flags": list(self.flags),
        }
        if self.new is not None:
            out["new"] = self.new
        if self.lint:
            out["lint"] = [f.as_dict() for f in self.lint]
        return out
