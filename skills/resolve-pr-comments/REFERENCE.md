# Script reference

Run these scripts from the target repository checkout.
Use the scripts from their installed directory.
The examples use a repository-local installation at `skills/resolve-pr-comments`.

```sh
skills/resolve-pr-comments/scripts/pr-threads.sh 42
skills/resolve-pr-comments/scripts/reply.sh 42 123456 --body-file /tmp/reply.md
skills/resolve-pr-comments/scripts/resolve.sh PRRT_example
skills/resolve-pr-comments/scripts/reply.sh --top 42 --body-file /tmp/reply.md
```

The scripts require `gh` and `jq` on `PATH`.
They use the repository and host that `gh repo view` selects for the current checkout.
Check that selection with `gh repo view` before use.
The scripts pass the selected host to each API call.
Read access is sufficient for inspection.
Posting and resolution need the permissions that GitHub requires for those actions.

## Read feedback

`pr-threads.sh [PR_NUMBER]` defaults to the current branch's PR.
It prints one JSON object with these fields:

| Field | Content |
| --- | --- |
| `pr`, `url` | PR number and URL |
| `author`, `viewer` | PR author and authenticated account |
| `base_ref`, `head_ref` | Branch names |
| `base_repository`, `head_repository` | Repository names with owners. A deleted head repository can be null |
| `head_oid` | Current PR head commit |
| `unresolved_threads` | Unresolved inline threads with all comments |
| `top_level_comments` | All PR conversation comments |
| `reviews` | Review summaries, states, and commit IDs |

Each inline thread includes `thread_id`, `reply_to`, `path`, `line`, `outdated`, and `comments`.
`reply_to` is the first comment's REST database ID.
`thread_id` is the GraphQL node ID.
Each comment includes its author, body, and URL.
Deleted authors appear as null.
The script follows pagination for threads, nested comments, conversation comments, and reviews.
If any API request fails, the script exits without a partial feedback object.

Review summary bodies can contain requests that do not appear in inline threads.
Reply to these with a conversation comment that identifies the review URL.
GitHub does not support thread resolution for conversation comments or review summaries.

## Reply

```sh
reply.sh PR_NUMBER REPLY_TO_COMMENT_ID 'Fixed in abc1234.'
reply.sh --top PR_NUMBER 'The documented behavior is intentional.'
reply.sh PR_NUMBER REPLY_TO_COMMENT_ID --body-file /tmp/reply.md
reply.sh --top PR_NUMBER --body-file /tmp/reply.md
```

A reply prints the comment URL.
Use `--body-file` for multiline text or text with shell syntax.
The file must contain nonempty text.
A quoted body argument remains available for short replies.
An inline reply uses the review comment reply endpoint.
A conversation reply uses the issue comment endpoint for the PR number.

## Resolve

```sh
resolve.sh THREAD_ID
```

The script prints `true` after a successful resolution.
It exits with an error if GitHub returns a false or missing resolution state.
It cannot verify that you replied, pushed the fix, or ran the checks.
Follow the skill workflow before you call it.

## Errors and limits

Invalid arguments fail before an API request.
API, permission, and rate limit errors stop the script.
If a comment ID is stale, read the feedback again before retrying.
If permissions are insufficient, report the blocked action and leave the thread open.

These scripts do not edit code, push commits, merge branches, or wait for reviews.
They take a snapshot of feedback through several requests.
If the head changes during a pass, inspect the new code and feedback before resolving affected threads.
