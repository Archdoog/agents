"""Provide read-only prose, comment, and branch checks."""

import argparse
import glob
import json
import os
from pathlib import Path
import sys

from . import comments, git, prose


PROSE = {".md", ".markdown", ".txt", ".rst"}
SKIP = {".git", "__pycache__", "node_modules", ".venv", "venv", "vendor", "dist", "build"}


class UsageError(ValueError):
    """Identify invalid command arguments."""


class Parser(argparse.ArgumentParser):
    """Report argument errors through the CLI output contract."""

    def error(self, message):
        """Raise UsageError for an invalid argument message."""
        raise UsageError(message)


def _paths(inputs):
    paths, errors = [], []
    for item in inputs:
        if item == "-":
            paths.append(item)
            continue
        matches = glob.glob(item, recursive=True) if glob.has_magic(item) else [item]
        if not matches:
            errors.append({"path": item, "message": "No paths match the pattern."})
        for match in matches:
            path = Path(match)
            if not path.exists():
                errors.append({"path": match, "message": "The path does not exist."})
            elif path.is_dir():
                def onerror(exc):
                    errors.append({"path": str(exc.filename), "message": str(exc)})
                for root, dirs, files in os.walk(path, onerror=onerror):
                    dirs[:] = sorted(d for d in dirs if d not in SKIP)
                    paths.extend(str(Path(root) / name) for name in sorted(files)
                                 if Path(name).suffix.lower() in PROSE | comments.EXTENSIONS)
            else:
                paths.append(str(path))
    return list(dict.fromkeys(paths)), errors


def _surface(path):
    name = Path(path).name.lower()
    if name.startswith("readme"):
        return "readme"
    if name.startswith("changelog"):
        return "changelog"
    return "doc"


def main(argv=None):
    """Run argv and return 0 for success, 1 for findings, or 2 for input errors."""
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = Parser(prog="writing-for-code", description="Check prose without changing files.")
    sub = parser.add_subparsers(dest="command", required=True, parser_class=Parser)
    for name in ("lint", "comments", "check", "rules"):
        cmd = sub.add_parser(name, help={
            "lint": "Check prose files or stdin.", "comments": "Inspect source comments.",
            "check": "Check changed prose, comments, and branch commits.", "rules": "List the rule definitions.",
        }[name])
        cmd.add_argument("--json", action="store_true", help="Write JSON output.")
        cmd.add_argument("--surface", choices=prose.SURFACES, help="Select the text type. Default: infer from the input.")
        cmd.add_argument("--strict", action="store_true", help="Use strict prose rules.")
        cmd.add_argument("--warnings-as-errors", "-W", action="store_true", help="Fail on advisory findings. Default: off.")
        if name in {"lint", "comments"}:
            cmd.add_argument("paths", nargs="*", help="Read files, directories, globs, or stdin with -.")
        if name == "comments":
            cmd.add_argument("--diff", help="Inspect source files changed since this ref's merge base.")
            cmd.add_argument("--new-only", action="store_true", help="With --diff, report only changed prose spans.")
        if name == "check":
            cmd.add_argument("--diff", "--base", dest="base", help="Compare with this ref's merge base. Default: the upstream default branch.")
            cmd.add_argument("--skip-commits", "--no-commits", action="store_true", help="Do not check branch commit messages. Default: check them.")
    findings, errors = [], []
    try:
        args = parser.parse_args(argv)
        if args.command in {"lint", "comments"} and not args.paths and not getattr(args, "diff", None):
            raise UsageError("Give an input path, or use '-' for prose on stdin.")
        if args.command == "comments" and args.new_only and not args.diff:
            raise UsageError("Use --diff REF with --new-only.")
        mode = "strict" if args.strict else None
        if args.command == "rules":
            rules = [{"id": code, "strict": values[0], "flavored": values[1], "message": values[2],
                      "surfaces": ["commit"] if code == "commit-subject" else
                      ["comment", "docstring"] if code.startswith("comment-") else list(prose.SURFACES),
                      "advisory_in_comments": True}
                     for code, values in prose.RULES.items()
                     if not args.surface or args.surface in (
                         ["commit"] if code == "commit-subject" else
                         ["comment", "docstring"] if code.startswith("comment-") else prose.SURFACES)]
            if args.json:
                print(json.dumps({"rules": rules, "surfaces": list(prose.SURFACES),
                                  "strict_surfaces": sorted(prose.STRICT_SURFACES)}, ensure_ascii=True))
            else:
                for rule in rules:
                    print(rule["id"] + ": " + rule["message"])
            return 0
        if args.command == "check" or (args.command == "comments" and args.diff):
            root, merge, changed = git.changes(args.base if args.command == "check" else args.diff)
            paths = list(changed)
            if args.command == "comments":
                paths = [p for p in paths if Path(p).suffix.lower() in comments.EXTENSIONS]
                if args.paths:
                    raise UsageError("Use paths or --diff, not both.")
                if not args.new_only:
                    changed = None
        else:
            paths, errors = _paths(args.paths)
            changed, root = None, Path.cwd()
        stdin = None
        for path in paths:
            ext = Path(path).suffix.lower()
            if args.command == "check" and ext not in PROSE | comments.EXTENSIONS:
                continue
            if args.command != "check" and (root / path).is_file():
                if args.command == "comments" and ext not in comments.EXTENSIONS:
                    # Explicit source files must not disappear from the report.
                    errors.append({"path": path, "message": "Unsupported source file."})
                    continue
            try:
                if path == "-":
                    if args.command == "comments":
                        raise ValueError("Use a source file path for comment checks.")
                    if stdin is None:
                        stdin = sys.stdin.read()
                    text = stdin
                else:
                    with (root / path).open(encoding="utf-8", newline="") as stream:
                        text = stream.read()
                source = args.command == "comments" or (args.command == "check" and ext in comments.EXTENSIONS)
                items = comments.analyze(path, text, args.surface, mode) if source else prose.lint(
                    text, args.surface or _surface(path), mode)
                for item in items:
                    if changed is not None and not any(
                            line in changed[path] for line in range(item["start_line"], item["end_line"] + 1)):
                        continue
                    findings.append({"path": path, **{k: v for k, v in item.items() if not k.startswith("_")}})
            except (OSError, UnicodeError, ValueError) as exc:
                errors.append({"path": path, "message": str(exc)})
        if args.command == "check" and not args.skip_commits:
            for commit, text in git.commits(root, merge):
                for item in prose.lint(text, args.surface or "commit", mode):
                    findings.append({"path": "commit:" + commit,
                                     **{k: v for k, v in item.items() if not k.startswith("_")}})
    except (UsageError, OSError, UnicodeError, ValueError) as exc:
        errors.append({"path": None, "message": str(exc)})
    as_json = "--json" in argv
    if as_json:
        print(json.dumps({"findings": findings, "errors": errors}, ensure_ascii=True))
    else:
        for item in findings:
            print(f'{item["path"]}:{item["line"]}:{item["column"]}: {item["level"]} {item["code"]}: {item["message"]}')
        for error in errors:
            print((error["path"] or "writing-for-code") + ": " + error["message"], file=sys.stderr)
    if errors:
        return 2
    return int(any(item["level"] == "error" or args.warnings_as_errors for item in findings))
