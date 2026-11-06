"""The `writing-for-code` command line.

Exit status on every command: 0 clean, 1 at least one error, 2 bad usage or
an unreadable input. Warnings and comment flags do not fail a run unless you
pass `--warnings-as-errors`.
"""

from __future__ import annotations

import argparse
import glob
import sys
from typing import List, Optional

from . import __version__, git, report, rules
from .comments import analyze, source_files, style_for
from .comments.flags import MEANINGS
from .lint import lint
from .model import ERROR, WARNING, CommentBlock, Finding
from .surfaces import SURFACES, for_path, mode_for

PROSE_EXTENSIONS = (".md", ".markdown", ".txt", ".rst")


def _exit(findings: List[Finding], warnings_as_errors: bool) -> int:
    if report.count(findings, ERROR):
        return 1
    if warnings_as_errors and report.count(findings, WARNING):
        return 1
    return 0


def _expand(specs: List[str]) -> List[str]:
    out = []
    for spec in specs:
        if spec != "-" and any(c in spec for c in "*?["):
            out.extend(sorted(glob.glob(spec, recursive=True)))
        else:
            out.append(spec)
    return out


def _read(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    with open(path, encoding="utf-8", errors="replace") as handle:
        return handle.read()


def _lint_block(block: CommentBlock, strict: bool) -> List[Finding]:
    surface = "docstring" if block.kind == "doc" else "comment"
    found = lint(block.text, surface, mode_for(surface, strict))
    # A finding in a block points at a line of the source file.
    for f in found:
        f.line += block.line - 1
    return found


def _scan_comments(targets, new_only: bool, do_lint: bool, strict: bool):
    blocks: List[CommentBlock] = []
    for path, added in targets:
        style = style_for(path)
        if not style:
            continue
        try:
            text = _read(path)
        except OSError as exc:
            print(f"writing-for-code: {path}: {exc.strerror}", file=sys.stderr)
            continue
        if added is None and new_only:
            added = set(range(1, text.count("\n") + 2))
        for block in analyze(path, text, style, added):
            if new_only and not block.new:
                continue
            if do_lint:
                block.lint = _lint_block(block, strict)
            blocks.append(block)
    return blocks



def cmd_lint(args) -> int:
    if not args.files:
        print("writing-for-code lint: give a file, or '-' for stdin", file=sys.stderr)
        return 2
    results = {}
    unreadable = []
    for path in _expand(args.files):
        surface = args.surface or (for_path(path) if path != "-" else "doc")
        try:
            text = _read(path)
        except OSError as exc:
            unreadable.append(f"{path}: {exc.strerror}")
            continue
        results[path] = (surface, lint(text, surface, mode_for(surface, args.strict)))

    every = [f for _, fs in results.values() for f in fs]
    if args.json:
        report.dump({
            "files": {p: {"surface": s, "findings": [f.as_dict() for f in fs]}
                      for p, (s, fs) in results.items()},
            "errors": report.count(every, ERROR),
            "warnings": report.count(every, WARNING),
            "unreadable": unreadable,
        }, sys.stdout)
    else:
        for path, (_, fs) in results.items():
            report.findings_text("<stdin>" if path == "-" else path, fs, sys.stdout)
        for problem in unreadable:
            print(f"writing-for-code: cannot read {problem}", file=sys.stderr)
        report.summary(every, len(results), sys.stdout)
    if unreadable:
        return 2
    return _exit(every, args.warnings_as_errors)



def cmd_comments(args) -> int:
    if not args.paths and not args.diff:
        print("writing-for-code comments: give paths or --diff REF", file=sys.stderr)
        return 2
    targets = []
    if args.diff:
        try:
            targets.extend(git.changed_files(args.diff).items())
        except git.GitError as exc:
            print(f"writing-for-code: {exc}", file=sys.stderr)
            return 2
    targets.extend((p, None) for p in source_files(args.paths))
    blocks = _scan_comments(targets, args.new_only and bool(args.diff),
                            not args.no_lint, args.strict)
    every = [f for b in blocks for f in b.lint]
    if args.json:
        report.dump([b.as_dict() for b in blocks], sys.stdout)
    else:
        report.blocks_text(blocks, args.all, sys.stdout)
    return _exit(every, args.warnings_as_errors)



def cmd_check(args) -> int:
    base = args.diff or git.default_base()
    try:
        changed = git.changed_files(base)
        commits = [] if args.no_commits else git.commit_messages(base)
    except git.GitError as exc:
        print(f"writing-for-code: {exc}", file=sys.stderr)
        return 2

    source = [(p, a) for p, a in changed.items() if style_for(p)]
    blocks = _scan_comments(source, True, True, False)

    prose = {}
    for path, added in changed.items():
        if not path.lower().endswith(PROSE_EXTENSIONS):
            continue
        surface = for_path(path)
        found = lint(_read(path), surface)
        if added is not None:
            found = [f for f in found if f.line in added]
        prose[path] = (surface, found)

    messages = {sha: lint(msg, "commit") for sha, msg in commits}

    every = ([f for b in blocks for f in b.lint]
             + [f for _, fs in prose.values() for f in fs]
             + [f for fs in messages.values() for f in fs])

    if args.json:
        report.dump({
            "base": base,
            "comments": [b.as_dict() for b in blocks],
            "files": {p: {"surface": s, "findings": [f.as_dict() for f in fs]}
                      for p, (s, fs) in prose.items()},
            "commits": {sha: [f.as_dict() for f in fs] for sha, fs in messages.items()},
            "errors": report.count(every, ERROR),
            "warnings": report.count(every, WARNING),
        }, sys.stdout)
    else:
        out = sys.stdout
        out.write(f"== comments on new lines since {base}\n")
        report.blocks_text(blocks, False, out)
        out.write("\n== changed docs\n")
        for path, (_, fs) in prose.items():
            report.findings_text(path, fs, out)
        out.write("\n== commit messages\n")
        for sha, fs in messages.items():
            report.findings_text(f"commit {sha}", fs, out)
        report.summary(every, len(source) + len(prose), out,
                       f" and {len(messages)} commit(s)")
        if blocks:
            out.write("Comment flags are leads. Read each flagged block against "
                      "surfaces/comments.md.\n")
    return _exit(every, args.warnings_as_errors)



def cmd_rules(args) -> int:
    surfaces = [args.surface] if args.surface else list(SURFACES)
    payload = {}
    for name in surfaces:
        mode = mode_for(name, args.strict)
        payload[name] = {
            "mode": mode,
            "guide": f"surfaces/{SURFACES[name].guide}",
            "rules": [{"code": r.code, "rule": r.name, "level": r.level(mode),
                       "summary": r.summary} for r in rules.active(name, mode)],
        }
    if args.json:
        report.dump({"surfaces": payload, "comment_flags": MEANINGS}, sys.stdout)
        return 0
    if not args.surface:
        print(f"{'surface':10} {'mode':9} guide")
        for name, s in SURFACES.items():
            print(f"{name:10} {mode_for(name, args.strict):9} surfaces/{s.guide}  ({s.summary})")
        print("\nRun `rules --surface NAME` for the rules of one surface.")
        print("The em dash is not checked. ASD-STE100 does not ban it.")
        return 0
    info = payload[args.surface]
    print(f"{args.surface}: {info['mode']} mode. Guide: {info['guide']}\n")
    for r in info["rules"]:
        print(f"{r['code']:10} {r['level']:8} {r['rule']:22} {r['summary']}")
    if args.surface in ("comment", "docstring"):
        print("\nComment flags (leads, never errors):")
        for name, meaning in MEANINGS.items():
            print(f"  {name:13} {meaning}")
    return 0



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="writing-for-code",
        description="Check the prose that developers write for code.",
        epilog="Exit 0 clean, 1 errors found, 2 bad usage.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    def common(p, surface=True):
        if surface:
            p.add_argument("--surface", choices=list(SURFACES),
                           help="the kind of prose. Sets the mode and the rules.")
        p.add_argument("--strict", action="store_true",
                       help="use strict mode on every surface")
        p.add_argument("--json", action="store_true", help="machine-readable output")
        p.add_argument("--warnings-as-errors", "-W", action="store_true",
                       help="exit 1 on warnings too")

    p = sub.add_parser("lint", help="check prose in files or on stdin")
    p.add_argument("files", nargs="*", metavar="FILE", help="'-' reads stdin")
    common(p)
    p.set_defaults(func=cmd_lint)

    p = sub.add_parser("comments", help="find, flag, and lint code comments")
    p.add_argument("paths", nargs="*", help="files or directories")
    p.add_argument("--diff", metavar="REF", help="scan files changed since REF")
    p.add_argument("--new-only", action="store_true",
                   help="with --diff: only blocks on added lines")
    p.add_argument("--no-lint", action="store_true", help="flags only")
    p.add_argument("--all", action="store_true", help="show blocks with no finding")
    common(p, surface=False)
    p.set_defaults(func=cmd_comments)

    p = sub.add_parser("check", help="the pre-PR check: new comments, changed "
                                     "docs, and branch commit messages")
    p.add_argument("--diff", metavar="REF",
                   help="base ref. The default is the upstream default branch.")
    p.add_argument("--no-commits", action="store_true",
                   help="do not check commit messages")
    p.add_argument("--json", action="store_true", help="machine-readable output")
    p.add_argument("--warnings-as-errors", "-W", action="store_true",
                   help="exit 1 on warnings too")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("rules", help="print the surfaces and their rules")
    p.add_argument("--surface", choices=list(SURFACES))
    p.add_argument("--strict", action="store_true")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_rules)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        parser.print_help(sys.stderr)
        return 2
    return args.func(args)
