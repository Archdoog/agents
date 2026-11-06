# Changelogs

`CHANGELOG.md` entries and release notes. Mode: flavored.

The reader is a user of the code who wants to know what changed for them,
and if they must do something.

## Find the convention first

1. Read the existing `CHANGELOG.md`. Use its headings, its order, and its
   style of entry.
2. If the repo has no changelog, use Keep a Changelog 1.1.0
   (<https://keepachangelog.com/en/1.1.0/>). Its headings are `Added`,
   `Changed`, `Deprecated`, `Removed`, `Fixed`, and `Security`.
3. If the repo generates the changelog from commits or from PR labels, do
   not edit the file by hand. Write a good commit or PR title.

## Each entry

- Write for the user, not for the author. Say what changed in behavior,
  not which files changed.
- Start with the area, then the change: "Parser: accepts a trailing comma
  in arrays."
- For a breaking change, say what the user must do. Put it first in the
  release.
- Link the PR or the issue if the changelog does that already.
- Leave out internal changes that do not change behavior: refactors, test
  changes, and CI changes. Include them only if the repo does.

| Bad | Good |
|---|---|
| Updated `parser.ts` and `lexer.ts` | Parser: accepts a trailing comma in arrays |
| Various bug fixes and improvements | Fixed: `decode` no longer drops the last point of a route |
| Refactored the cache layer | (leave out) |

## Self-check

1. Does each entry say what changed for the user?
2. Does each breaking change say what the user must do?
3. Did you use the format of the existing file?
