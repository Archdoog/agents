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

| Surface | Guidance |
|---|---|
| Inline comments | [comments](surfaces/comments.md) |
| API, module, and package docs | [docstrings](surfaces/docstrings.md) |
| README | [readmes](surfaces/readmes.md) |
| Tutorials, how-to guides, references, explanations | [guides](surfaces/guides.md) |
| Architecture decision records | [adrs](surfaces/adrs.md) |
| Procedures and runbooks | [procedures](surfaces/procedures.md) |
| Error messages | [errors](surfaces/errors.md) |
| Log messages | [logs](surfaces/logs.md) |
| CLI help | [cli-help](surfaces/cli-help.md) |
| Changelogs and release notes | [changelogs](surfaces/changelogs.md) |
| Commit messages | [commits](surfaces/commits.md) |
| Pull requests | [prs](surfaces/prs.md) |
| Issues | [issues](surfaces/issues.md) |
| Code reviews | [reviews](surfaces/reviews.md) |

For operational steps in mixed documents, follow [procedures](surfaces/procedures.md).
Do not load every surface for one task.

Repository instructions, templates, and established terminology take precedence over these defaults.
Stay within the requested scope. A review request produces findings, not edits.
For rewrite-only requests, return only the revised text. If the text needs no change, return it unchanged.
