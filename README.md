# Agent skills and tooling

Reusable agent skills for public repositories. This project uses the BSD 3-Clause license.

## Available skills

| Skill | Purpose |
| --- | --- |
| [resolve-pr-comments](skills/resolve-pr-comments/SKILL.md) | Address GitHub PR feedback, reply to reviewers, and resolve addressed inline threads |

Copy `skills/resolve-pr-comments` into your agent's skill directory.
Keep `SKILL.md`, `REFERENCE.md`, and `scripts/` together.
Run the Python CLI from a checkout of the target repository.
The skill requires Python 3.11 or later, `uv`, Git, and GitHub CLI.
`uv` installs the HTTPX dependency declared in the script.
It follows the target repository's rules and supports fork PRs.

## Development

Run `just pre-pr` to check Ruff lint, formatting, CLI behavior, and whitespace.
The checks require `just`, `uv`, and Python 3.11 or later.
`uv` installs the development dependencies from `uv.lock`.
The tests use HTTPX mock transport and do not post comments.
