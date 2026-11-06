# Issues

Issue bodies and issue comments. Mode: flavored, with `--surface issue`.

The reader is the person who will pick up the issue, maybe weeks later,
with no context from your session.

## Find the convention first

1. Read the issue templates in `.github/ISSUE_TEMPLATE/`.
2. Fill in each field that the template has. Do not delete its headings.

If the repo has no template, use the default below.

## A bug

1. **What happened.** The observed result. Quote the error message or the
   log line exactly, in a code block.
2. **What you expected.**
3. **Steps to reproduce.** A numbered list, from a clean start. Give the
   smallest input that shows the bug.
4. **Environment.** Versions, platform, and configuration that matter.

Do not give a cause or a fix unless you know it. If you have a guess, label
it: "Possible cause: ...".

## A task or a feature

1. **The goal.** The problem for the user, not the solution.
2. **Done when.** The conditions that a reviewer can check.
3. **Out of scope**, if a reader will ask.

Add a proposed solution only if you have one, and keep it apart from the
goal.

## An issue comment

- Add new information only: a new reproduction, a measurement, a link, or
  a decision.
- Do not post "+1", "Any update?", or a summary of the thread.
- If the comment closes the issue, say what fixed it and link the PR.

## Self-check

1. Can a person with no context reproduce the bug, or check that the task
   is done?
2. Is each guess labeled as a guess?
3. Did you quote each error exactly?
