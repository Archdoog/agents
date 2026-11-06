"""The git queries that the diff and commit checks need."""

from __future__ import annotations

import os
import re
import subprocess
from typing import Dict, List, Optional, Set, Tuple

HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", re.M)


class GitError(Exception):
    pass


def run(*args: str) -> str:
    proc = subprocess.run(["git", *args], capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise GitError(proc.stderr.strip() or f"git {' '.join(args)} failed")
    return proc.stdout


def default_base() -> str:
    """The upstream default branch, or `main` if git cannot tell."""
    try:
        ref = run("symbolic-ref", "--quiet", "refs/remotes/origin/HEAD").strip()
        return ref.replace("refs/remotes/", "", 1)
    except GitError:
        pass
    for candidate in ("origin/main", "origin/master", "main", "master"):
        try:
            run("rev-parse", "--verify", "--quiet", candidate)
            return candidate
        except GitError:
            continue
    return "main"


def merge_base(base: str) -> str:
    try:
        return run("merge-base", base, "HEAD").strip()
    except GitError:
        return base


def _untracked() -> Set[str]:
    return set(filter(None, run("ls-files", "--others", "--exclude-standard").split("\n")))


def changed_files(base: str) -> Dict[str, Optional[Set[int]]]:
    """Map each added, changed, or untracked file to its added line numbers.

    The value is `None` for an untracked file: every line is new.
    """
    mb = merge_base(base)
    names = set(filter(None, run("diff", "--name-only", "--diff-filter=AM", mb).split("\n")))
    untracked = _untracked()
    out: Dict[str, Optional[Set[int]]] = {}
    for name in sorted(names | untracked):
        if not os.path.isfile(name):
            continue
        if name in untracked:
            out[name] = None
            continue
        added: Set[int] = set()
        for m in HUNK.finditer(run("diff", "-U0", mb, "--", name)):
            start = int(m.group(1))
            count = int(m.group(2)) if m.group(2) is not None else 1
            added.update(range(start, start + count))
        out[name] = added
    return out


def commit_messages(base: str) -> List[Tuple[str, str]]:
    """Return (short sha, message) for each commit on HEAD that is not on
    `base`. The list does not include merge commits."""
    raw = run("log", "--no-merges", "--format=%h%x00%B%x01", f"{merge_base(base)}..HEAD")
    out = []
    for entry in raw.split("\x01"):
        entry = entry.strip("\n")
        if "\x00" in entry:
            sha, message = entry.split("\x00", 1)
            out.append((sha.strip(), message.rstrip("\n")))
    return out
