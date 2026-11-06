"""The rule registry.

A rule is a function that reads one piece of text and yields
`(offset, message)` pairs. The `scope` sets what text it gets:

- `text`: each prose block and each table row.
- `sentence`: each sentence. Table cells are fragments, so they are left out.
- `paragraph`: each paragraph. Lists are left out.
- `document`: the whole input, unmasked. Use it for rules about lines, such
  as a commit subject.

To add a rule, write it in the module for its group and decorate it with
`@rule`. Import a new module at the end of this file.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, FrozenSet, Iterable, List, Optional, Tuple

from ..model import ERROR, OFF, WARNING

SCOPES = ("text", "sentence", "paragraph", "document")


@dataclass(frozen=True)
class Context:
    """What a rule knows about the run."""

    mode: str      # "strict" or "flavored"
    surface: str   # a key of surfaces.SURFACES


Check = Callable[[str, Context], Iterable[Tuple[int, str]]]


@dataclass(frozen=True)
class Rule:
    code: str
    name: str
    summary: str
    scope: str
    strict: str
    flavored: str
    surfaces: Optional[FrozenSet[str]]
    check: Check

    def level(self, mode: str) -> str:
        return self.strict if mode == "strict" else self.flavored

    def applies(self, surface: str) -> bool:
        return self.surfaces is None or surface in self.surfaces


REGISTRY: Dict[str, Rule] = {}


def rule(
    code: str,
    name: str,
    summary: str,
    *,
    scope: str = "text",
    strict: str = ERROR,
    flavored: Optional[str] = None,
    surfaces: Optional[Iterable[str]] = None,
) -> Callable[[Check], Check]:
    """Register a check. `flavored` defaults to the `strict` level.

    `surfaces` limits the rule to those surfaces. `None` means every surface.
    """
    if scope not in SCOPES:
        raise ValueError(f"{code}: unknown scope {scope!r}")
    for level in (strict, flavored):
        if level not in (None, ERROR, WARNING, OFF):
            raise ValueError(f"{code}: unknown level {level!r}")

    def register(check: Check) -> Check:
        if code in REGISTRY:
            raise ValueError(f"{code} is already registered")
        REGISTRY[code] = Rule(
            code=code,
            name=name,
            summary=summary,
            scope=scope,
            strict=strict,
            flavored=flavored or strict,
            surfaces=frozenset(surfaces) if surfaces is not None else None,
            check=check,
        )
        return check

    return register


def active(surface: str, mode: str) -> List[Rule]:
    """The rules that run for a surface in a mode, in code order."""
    return [
        r for _, r in sorted(REGISTRY.items())
        if r.applies(surface) and r.level(mode) != OFF
    ]


# Each import registers the rules in that module.
from . import commits, sentences, slop, structure, words  # noqa: E402,F401
