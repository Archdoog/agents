# Agent skills and tooling

Reusable agent skills for public repositories. This project uses the BSD 3-Clause license.

## Available skills

| Skill | Purpose |
| --- | --- |
| [resolve-pr-comments](skills/resolve-pr-comments/SKILL.md) | Address GitHub PR feedback, reply to reviewers, and resolve addressed inline threads |

Copy `skills/resolve-pr-comments` into your agent's skill directory.
Keep `SKILL.md`, `REFERENCE.md`, and `scripts/` together.
Run the scripts from a checkout of the target repository.
The skill requires Bash, Git, GitHub CLI, and `jq`.
It follows the target repository's rules and supports fork PRs.

## Development

Run `just pre-pr` to check shell syntax, ShellCheck findings, script behavior, and whitespace.
The checks require `just`, `shellcheck`, Python 3, and the skill's runtime dependencies.
The tests use a fake GitHub CLI and do not post comments.
