---
name: writing-for-code
description: >-
  Write, review, or revise technical prose in comments, docstrings, documentation,
  procedures, errors, logs, CLI help, changelogs, commits, PRs, issues, and reviews.
  Use for plain technical English, removal of filler, and checks for useful context.
  Do not rewrite code or infer authorship from writing patterns.
---

# Writing for Code

Read [CORE.md](CORE.md) and [PRUNE.md](PRUNE.md). Then load only the surface that matches the task.

| Surface | Guidance | Mode |
|---|---|---|
| Inline comments | [comments](surfaces/comments.md) | Flavored |
| API, module, and package docs | [docstrings](surfaces/docstrings.md) | Flavored |
| README | [readmes](surfaces/readmes.md) | Flavored |
| Tutorials, how-to guides, references, explanations | [guides](surfaces/guides.md) | Flavored |
| Architecture decision records | [adrs](surfaces/adrs.md) | Flavored |
| Procedures and runbooks | [procedures](surfaces/procedures.md) | Strict |
| Error messages | [errors](surfaces/errors.md) | Strict |
| Log messages | [logs](surfaces/logs.md) | Strict |
| CLI help | [cli-help](surfaces/cli-help.md) | Strict |
| Changelogs and release notes | [changelogs](surfaces/changelogs.md) | Flavored |
| Commit messages | [commits](surfaces/commits.md) | Flavored |
| Pull requests | [prs](surfaces/prs.md) | Flavored |
| Issues | [issues](surfaces/issues.md) | Flavored |
| Code reviews | [reviews](surfaces/reviews.md) | Flavored |

For docstrings, also load the matching language note from `languages/`.
For mixed documents, apply strict mode to operational steps and diagnostics.
Do not load every surface or language note for one task.

Repository instructions, templates, and established terminology take precedence over these defaults.
Stay within the requested scope. A review request produces findings, not edits.
For rewrite-only requests, return only the revised text. If the text needs no change, return it unchanged.
