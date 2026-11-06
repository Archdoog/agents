# Pull requests

PR titles and bodies. Mode: flavored, with `--surface pr`.

The readers are the reviewer now and an engineer who finds the PR from
`git blame` a year from now. The PR body is also the place for the design
reasons that the comments rules keep out of the code.

Generated PR bodies are the longest and emptiest text of all the surfaces.
Run the fresh-eyes prune pass in `PRUNE.md` on a body over about 150 words.

## Find the convention first

1. Read the PR template: `.github/pull_request_template.md` or
   `.github/PULL_REQUEST_TEMPLATE/`.
2. Read two or three merged PRs of the repo.
3. Keep each section that the template requires. Do not add sections that
   it does not have, except the three below when they are missing.

## The title

Use the rules for a commit subject in `commits.md`. If the repo squashes
PRs, the title becomes the commit subject.

## The default body

Three short parts:

1. **What** changed, in one to three sentences. Write about behavior, not
   files.
2. **Why**, with a link to the issue or the ticket. Give the design reason
   here if a reviewer will ask for it. Name the alternative that you did
   not take, in one sentence, only if a reviewer is likely to suggest it.
3. **How you verified it**: the commands that you ran, the tests that you
   added, or the manual steps and what you saw. "Tested locally" is not
   verification.

Add these only when they apply:

- **Breaking changes**, and what a user must do.
- **Screenshots** for a visual change.
- **Follow-up work** that is out of scope, with links.

## Leave out

- "This PR ...". Start with the change.
- A walkthrough of each changed file. The diff shows it.
- A summary at the end that repeats the body.
- A checklist that you copied but did not check.
- Praise of the change: "clean", "robust", "elegant".

## Example

```markdown
Retries a failed upload once, after 500 ms.

Uploads on a slow network fail about 2% of the time with a timeout
(#412). One retry fixes most of them. A retry queue would also cover
long outages, but no user report needs that yet.

Verified:
- `npm test` passes, with a new test for the retry path.
- On a throttled network (Chrome "Slow 3G"), 50 uploads gave 0 failures.
  Before the change, 50 uploads gave 2 failures.
```

## Before you open the PR

1. Run `scripts/writing-for-code check`.
2. Put the body in a file and run
   `scripts/writing-for-code lint --surface pr BODY_FILE`.
3. Run the prune pass on the body.
