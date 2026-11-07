"""Read branch and working-tree changes without parsing quoted Git paths."""

import difflib
import os
import subprocess
from pathlib import Path


def run(root, *args):
    """Return Git output bytes for args in root, or raise ValueError on failure."""
    try:
        result = subprocess.run(["git", "-C", str(root), *args], capture_output=True)
    except OSError as exc:
        raise ValueError(str(exc)) from exc
    if result.returncode:
        raise ValueError(result.stderr.decode("utf-8", "replace").strip())
    return result.stdout


def changes(base=None):
    """Return repository root, merge base, and changed paths with changed lines.

    Paths are root-relative. Changes include the index and untracked files.
    """
    root = Path(os.fsdecode(run(Path.cwd(), "rev-parse", "--show-toplevel")).removesuffix("\n"))
    if base is None:
        try:
            base = run(root, "symbolic-ref", "refs/remotes/origin/HEAD").decode().strip()
        except ValueError:
            pass
        for candidate in (() if base else ("origin/main", "origin/master", "main", "master")):
            try:
                run(root, "rev-parse", "--verify", candidate)
                base = candidate
                break
            except ValueError:
                continue
        if base is None:
            raise ValueError("Cannot find the default branch. Pass --diff REF.")
    merge = run(root, "merge-base", base, "HEAD").decode().strip()
    entries = run(root, "diff", "--name-status", "-z", "--find-renames", merge, "--").split(b"\0")
    paths = {}
    i = 0
    while i < len(entries) and entries[i]:
        status, old = entries[i].decode(), os.fsdecode(entries[i + 1])
        i += 2
        path = old
        if status[0] in "RC":
            path = os.fsdecode(entries[i])
            i += 1
        if status[0] != "D":
            paths[path] = old if status[0] != "A" else None
    for entry in run(root, "ls-files", "--others", "--exclude-standard", "-z").split(b"\0"):
        if entry:
            paths[os.fsdecode(entry)] = None
    result = {}
    for path, old in paths.items():
        if (root / path).is_symlink():
            continue
        current = (root / path).read_bytes()
        before = run(root, "show", merge + ":" + old) if old else b""
        changed = set()
        matcher = difflib.SequenceMatcher(None, before.splitlines(), current.splitlines(), autojunk=False)
        for tag, _, _, left, right in matcher.get_opcodes():
            if tag in {"replace", "insert"}:
                changed.update(range(left + 1, right + 1))
        result[path] = changed
    return root, merge, result


def commits(root, merge):
    """Yield (commit hash, message) pairs reachable from HEAD but not merge."""
    for commit in run(root, "rev-list", "--no-merges", "--reverse", merge + "..HEAD").decode().splitlines():
        yield commit, run(root, "show", "-s", "--format=%B", commit).decode("utf-8")
