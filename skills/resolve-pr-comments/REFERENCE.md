# Python CLI reference

Run the CLI from the target repository checkout.
Use the installed path to `scripts/pr_comments.py`.
The examples use a repository-local installation at `skills/resolve-pr-comments`.

```sh
uv run skills/resolve-pr-comments/scripts/pr_comments.py --help
uv run skills/resolve-pr-comments/scripts/pr_comments.py list 42
uv run skills/resolve-pr-comments/scripts/pr_comments.py reply 42 --comment 123456 --body-file /tmp/reply.md
uv run skills/resolve-pr-comments/scripts/pr_comments.py reply 42 --top --body 'An answer.'
uv run skills/resolve-pr-comments/scripts/pr_comments.py resolve PRRT_example
```

## Dependencies and authentication

Use Python 3.11 or later and an authenticated GitHub CLI (`gh`) on `PATH`.
[uv](https://docs.astral.sh/uv/guides/scripts/) installs the dependency declared in the script's inline metadata.
No manual virtual environment setup is necessary.
You can also run the script with Python in an environment that has `httpx>=0.28,<1`.

The CLI uses Python's standard `argparse`, `json`, and `subprocess` modules.
[HTTPX](https://www.python-httpx.org/quickstart/) handles HTTPS requests, JSON bodies, timeouts, and HTTP errors.
`gh repo view` selects the repository and host from the current checkout.
`gh auth token --hostname HOST` supplies the credentials for that host.
The CLI uses GitHub.com or GitHub Enterprise Server API paths as appropriate.
Check the target with `gh repo view` before use.

Read access is sufficient for inspection.
Posting and resolution need the permissions that GitHub requires for those actions.
Credentials stay in memory and request headers.
The CLI does not print credentials or GitHub CLI error output.

## Read feedback

`list [PR_NUMBER]` defaults to the current branch's PR.
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
`reply_to` is the first comment's REST database ID, or null for an empty thread.
`thread_id` is the GraphQL node ID.
Each comment includes its author, body, and URL.
Deleted authors appear as null.
The CLI follows pagination for threads, nested comments, conversation comments, and reviews.

If any API request fails, the CLI exits without a partial feedback object.
Review summary bodies can contain requests that do not appear in inline threads.
Reply to these with a conversation comment that identifies the review URL.
GitHub does not support thread resolution for conversation comments or review summaries.

## Reply

```sh
uv run /path/to/pr_comments.py reply 42 --comment 123456 --body 'Fixed in abc1234.'
uv run /path/to/pr_comments.py reply 42 --top --body-file /tmp/reply.md
```

Choose exactly one target: `--comment COMMENT_ID` or `--top`.
Choose exactly one body source: `--body TEXT` or `--body-file PATH`.
The CLI reads body files as UTF-8 and preserves their content, including trailing newlines.
Use a file for multiline text or text with shell syntax.
The reply body must contain non-whitespace text.

An inline reply uses the review comment reply endpoint.
A conversation reply uses the issue comment endpoint for the PR number.
A successful reply prints the comment URL.

## Resolve

```sh
uv run /path/to/pr_comments.py resolve PRRT_example
```

The CLI prints `true` after a successful resolution.
It exits with an error if GitHub returns a false or missing resolution state.
It cannot verify that you replied, pushed the fix, or ran the checks.
Follow the skill workflow before you call it.

## Errors and limits

The CLI uses exit code 0 for success, 1 for request failures, and 2 for argument errors.
Invalid arguments and empty bodies fail before authentication or an API request.
Network, API, permission, rate limit, and GraphQL errors stop the command.
Requests have a 30-second inactivity timeout.
The CLI does not automatically retry writes, which could duplicate replies.
If a comment ID is stale, read the feedback again before retrying.

The CLI does not edit code, push commits, merge branches, or wait for reviews.
It takes a snapshot of feedback through several requests.
If the head changes during a pass, inspect the new code and feedback before resolving affected threads.
