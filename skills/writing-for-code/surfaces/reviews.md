# Review comments

Comments on a pull request, and review summaries. Mode: flavored, with
`--surface review`.

The reader is the author of the change. They must decide fast what to fix,
and how.

## Find the convention first

If the repo uses severity prefixes such as `nit:`, `blocking:`, or
Conventional Comments (<https://conventionalcomments.org/>), use them. If it
does not, do not add them.

## One comment, one finding

Each comment has four parts, in this order:

1. **Where.** Put the comment on the line. If the finding covers many
   lines, name the range or the function.
2. **The problem.** What is wrong, as a fact.
3. **The effect.** What goes wrong, and when: the input, the state, or the
   user action.
4. **The fix.** A specific change. Use a suggestion block if the platform
   has one.

| Bad | Good |
|---|---|
| Have you considered error handling here? | `decode` throws on an empty string, and `load` does not catch it. A route with no points crashes the list screen. Return an empty array for `""`. |
| This could be cleaner. | (do not post) |

Rules:

- Write a question only when you do not know the answer.
- Do not open with praise, and do not close with "LGTM" or "Great work".
- Do not post a comment that has no finding.
- Do not repeat a finding that the author resolved or declined, unless you
  have new evidence.
- If a finding is a preference, not a defect, say so, or do not post it.

## The review summary

- If the review has findings, list the ones that block the merge first.
- Keep it short. The comments on the lines hold the detail.
- If the review has no findings, post nothing, unless the platform needs
  an approval.

## Self-check

1. Does each comment have one finding, with the effect and the fix?
2. Did you delete each comment that has no finding?
3. Is each question a real question?
