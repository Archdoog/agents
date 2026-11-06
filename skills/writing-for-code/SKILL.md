---
name: writing-for-code
description: Write and prune the prose that developers write for code — code comments, docstrings, module docs, READMEs, guides, runbooks, ADRs, error messages, log lines, CLI help, changelogs, commit messages, PR bodies, issues, and review comments. Sets what to put in and what to leave out, applies ASD-STE100 Simplified Technical English, follows the official docstring guide of each language, and runs a deletion pass that scores every block from 0 to 4 and cuts what the reader does not need. Ships a CLI that lints prose, flags agent-style comments in a diff, and checks commit messages. Use whenever you write or edit any of these surfaces, before you commit or open a PR, when asked to cut, prune, tighten, or de-slop text, when text "reads like AI", or when a reviewer flags AI-sounding comments. Not for writing the code itself.
---

# writing-for-code

1. Read [CORE.md](CORE.md). It applies to every surface.
2. Read the file for your surface.
3. Write the text.
4. Run the prune pass in [PRUNE.md](PRUNE.md).
5. Run the tool, and fix what it finds.

| Surface | File | `--surface` | Mode |
|---|---|---|---|
| Code comments | [surfaces/comments.md](surfaces/comments.md) | `comment` | flavored |
| Docstrings, module docs | [surfaces/docstrings.md](surfaces/docstrings.md), then `languages/` | `docstring` | flavored |
| README | [surfaces/docs.md](surfaces/docs.md) | `readme` | flavored |
| Guides, `docs/`, ADRs, `CONTRIBUTING.md` | [surfaces/docs.md](surfaces/docs.md) | `doc` | flavored |
| Runbooks, procedures | [surfaces/docs.md](surfaces/docs.md) | `procedure` | strict |
| Error messages, log lines, CLI help | [surfaces/errors.md](surfaces/errors.md) | `error` | strict |
| Changelogs, release notes | [surfaces/changelog.md](surfaces/changelog.md) | `changelog` | flavored |
| Commit messages | [surfaces/commits.md](surfaces/commits.md) | `commit` | flavored |
| PR titles and bodies | [surfaces/pull-requests.md](surfaces/pull-requests.md) | `pr` | flavored |
| Issues | [surfaces/issues.md](surfaces/issues.md) | `issue` | flavored |
| Review comments | [surfaces/reviews.md](surfaces/reviews.md) | `review` | flavored |

## The tool

`scripts/writing-for-code` needs only `python3`. Paths are relative to this
file.

```sh
scripts/writing-for-code lint --surface pr body.md     # prose in a file
printf '%s' "$text" | scripts/writing-for-code lint -  # prose on stdin
scripts/writing-for-code comments --diff origin/main --new-only
scripts/writing-for-code check                          # before a commit or a PR
scripts/writing-for-code rules --surface comment        # the rules for a surface
```

Exit status: 0 clean, 1 errors, 2 bad usage. Errors are rule breaks. Fix
them. Warnings and comment flags are leads. Read each one and decide.

The tool checks form only. It cannot tell if a sentence is true or
necessary. A clean report is not a good document.

To make the tool skip a region of markdown, put it between
`<!-- writing-for-code: off -->` and `<!-- writing-for-code: on -->`. The
tool skips quoted text, code, and URLs without a switch.

## When you rewrite text on request

If the user asks you to cut, tighten, or rewrite text, edit only the text
that they named. Return the text and nothing else: no preamble and no list
of changes.

## Change the skill

- Add a rule: write it in `scripts/writing_for_code/rules/`, register it
  with `@rule`, and add a test in `scripts/tests/`.
- Add a surface: add it to `scripts/writing_for_code/surfaces.py`, add its
  file to `surfaces/`, and add a case to `evals/`.
- Run the tests:

  ```sh
  python3 -m unittest discover -s scripts/tests -t scripts
  ```

- Run the cases in `evals/` by hand after a change to `CORE.md`,
  `PRUNE.md`, or a surface file.

Leave a pattern out of the tool when it cannot find it at a low rate of
false positives. An agent that learns to ignore the tool is worse than no
tool.
