# agents

Agent skills and the tools that they use. Each skill is a directory in
`skills/` that Claude Code, or any agent that reads `SKILL.md` files, can
load.

| Skill | What it does |
|---|---|
| [writing-for-code](skills/writing-for-code/SKILL.md) | Writes and prunes the prose for code: comments, docstrings, READMEs, guides, error messages, commits, PRs, issues, and reviews. Has a CLI that lints the prose and the comments in a diff. |

## Install

Link each skill into `~/.claude/skills/`:

```sh
git clone https://github.com/Archdoog/agents.git
cd agents
./install.sh
```

`install.sh --dry-run` shows the links before it makes them. The script
does not replace a skill of the same name that is already installed.

## Use

The agent loads `writing-for-code` when it writes one of the surfaces in
the table above. To make it apply each time, add this block to
`~/.claude/CLAUDE.md`, or run `./install.sh --claude-md`:

```markdown
## Writing for code

Before you write or edit a code comment, docstring, README, doc page, error
message, commit message, PR body, issue, or review comment, read
`~/.claude/skills/writing-for-code/SKILL.md` and the file for that surface.
Before you commit or open a PR, run
`~/.claude/skills/writing-for-code/scripts/writing-for-code check`.
```

The CLI needs only `python3`:

```sh
skills/writing-for-code/scripts/writing-for-code check
```

```text
== comments on new lines since main
src/upload.ts:2: [line new] change
    | Now retries once on a timeout.
    > await retry(upload, 1)

1 comment block(s), 1 flagged. change 1

== changed docs

== commit messages

0 error(s), 0 warning(s) in 1 file(s) and 1 commit(s)
Comment flags are leads. Read each flagged block against surfaces/comments.md.
```

## Credits

`writing-for-code` adapts work under the MIT License:

- **unslop** by Jean-Luc Winkler (<https://github.com/jlwin/unslop_ai>,
  commit `d65241e`). The universal rule, the patterns of generated text,
  and the eval shape come from it.
- **asd-ste100** by Ege Chelebi
  (<https://github.com/woosal1337/blog/tree/e2bc85f/videos/ep01-the-cure-for-ai-slop/asd-ste100>).
  The ASD-STE100 rule card and its modes come from it, through the
  `ste-writing` skill in Rallista/agents.

The ASD-STE100 standard is at <https://asd-ste100.org>. It is not free to
copy.

```text
MIT License

Copyright (c) 2026 Jean-Luc Winkler

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

```text
MIT License

Copyright (c) 2026 Ege Chelebi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## License

See [LICENSE](LICENSE).
