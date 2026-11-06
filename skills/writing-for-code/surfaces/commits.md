# Commit messages

Mode: flavored, with `--surface commit`. The tool also checks the subject
line.

A commit message describes a change, so the rule against describing the
change in a comment does not apply here. A commit message is the place for
it.

## Find the convention first

1. Read the last 20 to 30 subjects: `git log --format=%s -30`.
2. Read `CONTRIBUTING.md` and any commit template or commit lint config.
3. Use what they use: Conventional Commits (`fix(parser): ...`), a scope
   prefix (`parser: ...`), a ticket trailer, or plain sentences.

If the repo has no convention, use the default below.

## The default

The subject line:

- Starts with a verb in the imperative: "Add", "Fix", "Remove". Read it as
  "If applied, this commit will ...".
- Is 50 characters or fewer if you can, and never over 72. The git docs
  recommend 50 (<https://git-scm.com/docs/git-commit#_discussion>). The
  tool reports an error over 72.
- Has no period at the end.
- Says what changed, not how: "Retry a failed upload once", not "Add a
  loop to upload()".

The body is optional. Add one only when the reader needs it:

- **Why** the change was necessary, if the subject does not show it.
- An effect that is not obvious: a changed default, a migration, or a
  performance change with its numbers.
- What you did not do, if a reviewer will ask.

Put a blank line between the subject and the body. Wrap the body at 72
characters. Put trailers, such as `Co-Authored-By:`, at the end.

## Leave out

- A list of the changed files. The diff shows them.
- A summary of the diff, line by line.
- "This commit ...". Start with the verb.
- The story of the session: "After some investigation, I found ...".

## Examples

```text
Updated the upload code to add retries and also fixed some bugs.
```

The same change, with the default:

```text
Retry a failed upload once

Uploads on a slow network fail about 2% of the time with a timeout. One
retry after 500 ms brings the failure rate under 0.1% in the staging
logs.
```

## Check

Before you commit, put the message in a file and run:

```sh
scripts/writing-for-code lint --surface commit MESSAGE_FILE
```

`scripts/writing-for-code check` also checks each commit on the branch.
