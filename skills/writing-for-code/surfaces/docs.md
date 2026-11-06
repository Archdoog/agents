# READMEs, guides, and procedures

READMEs, `docs/` pages, guides, `CONTRIBUTING.md`, ADRs, and runbooks.

| Surface | Mode | `--surface` |
|---|---|---|
| README | flavored | `readme` |
| Guide, doc page, ADR, `CONTRIBUTING.md` | flavored | `doc` |
| Runbook, numbered procedure | strict | `procedure` |

Run the fresh-eyes prune pass in `PRUNE.md` on each README and each doc
page that you write or rewrite.

## The README

The README is the entry point. It answers these questions in this order,
and nothing more:

1. **What is it?** One or two sentences, with no adjectives. Say what it
   does and for whom.
2. **How do I install or set it up?** The commands, in a code block.
3. **What is the smallest real use?** A command or a snippet that the
   reader can run, with its output if the output is short.
4. **Where do I go next?** Links to the guides, the reference, and
   `CONTRIBUTING.md`.

Add other sections only when they pass the prune test: requirements,
configuration, license, and credits.

Do not add:

- A feature list that says again what the usage section shows.
- A table of contents for a page shorter than about three screens.
- A directory tree that `ls` shows.
- A "Contributing" or "Support" section with no content of its own. Link
  `CONTRIBUTING.md` in place of it.
- An "Overview" or "Introduction" heading over the first paragraph.

Badges, logos, screenshots, and other presentation parts are out of scope
for this skill. The prune pass does not score them.

## Guides: one page, one job

Give each page one of the four types from Diátaxis
(<https://diataxis.fr/>):

| Type | The reader wants to | The page has |
|---|---|---|
| Tutorial | learn by doing | one path from start to a working result |
| How-to | do one task | the steps for that task, and only that task |
| Reference | look up a fact | complete, dry facts, in a fixed order |
| Explanation | understand why | the reasons, the context, and the trade-offs |

A page that mixes types is hard to use. Split it, or cut the part that
does not fit. The prune pass scores a block **2 (misplaced)** when it
belongs to a different type of page.

## Procedures and runbooks

The reader can be under pressure, so use strict mode.

1. Put the goal and the conditions to start at the top.
2. Write each step as a numbered item with one action, in the imperative.
3. Put the condition before the command: "If the health check fails, go to
   step 7."
4. Show the expected output after each command that has one.
5. Give the steps to go back, if the procedure changes state.

## ADRs

Use the template of the repo. An ADR is the place for the reasons and the
alternatives that you did not take. Keep the decision itself to one or two
sentences, at the top.

## Self-check

1. Does the README answer the four questions in order, and nothing more?
2. Does each guide page have one type?
3. Does each procedure step have one action?
4. Did each block pass the fresh-eyes prune pass?
