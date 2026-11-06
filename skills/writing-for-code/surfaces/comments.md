# Comments

Inline and block comments in source code, in every language. Docstrings
have their own file: `docstrings.md`. Mode: flavored.

Reviewers can tell agent-written code by its comments. The comments cite
other code, compare it to other platforms, describe the diff, and tell
stories. This file names those patterns and sets the bar for a comment.

It bans only what it names. You can write a comment that it does not name
if the comment is short and clears the bar.

## Out of scope

- Tool directives: lint suppressions, `// MARK:`, `//go:build`,
  `// SAFETY:`, and other comments that a compiler, linter, or IDE reads.
  Follow the tool.
- License and copyright headers.
- Comments on lines that your change does not touch. Do not rewrite,
  reflow, or delete them.

## Banned

1. **Code as the reason.** Do not cite other code to justify a decision:
   "matches `SyncManager`", "same pattern as the parser". A reader can read
   the code. A comment can name code when it does a job of its own, such as
   a debugging hint that names the function to check.
2. **Other platforms.** Do not name a sibling platform or its code: "as
   Android does", "parity with iOS", "ported from the Kotlin version". This
   applies also when the task is a parity task. The PR body links the task.
3. **The change.** Write about the code as it is. Do not write "now",
   "no longer", "new", "updated to", "changed from", "as requested", or
   "per the ticket". Git and the PR hold the change.
4. **This repo's issues.** Do not link an issue or a PR of this repo,
   except in a `TODO` for functionality that is missing. A link to a
   third-party tracker is a doc link, and you can use it.

## The bar for an inline comment

An inline comment needs a strong reason. These reasons are strong:

- **A nonstandard solution.** Say why in one line. Do not say what the
  code does.
- **A better fix that you did not choose.** Write a `TODO` that names the
  better fix and, if you know it, the condition to use it.
- **A debugging hint.** State a symptom that a reader can see, and its
  cause, in the present tense.
- **A workaround for a third-party bug.** Link the upstream bug. Say when
  to remove the workaround.
- **A guard.** Warn against an edit that looks safe but is not.

Before you keep a comment, ask: can a competent reader find this fast in
the code, the library docs, or git? If yes, delete the comment.

Keep an inline comment to one or two lines. If it needs more, the content
belongs in a doc or in the PR body.

## Upstream mode

Use upstream mode when the PR goes to a repo that your team does not own,
such as a PR from your fork.

- Do not use the conventions of your own team. That means no pointers to
  your decision records, no custom comment markers, and no links to your
  tracker or internal docs.
- Link only to public pages, and only to issues on the upstream tracker.
- The upstream `CONTRIBUTING.md` and code style come first.

## Examples

Cites other code as the reason. Delete it:

```swift
// Matches the retry logic in SyncManager so both paths behave the same.
let delay = backoff(attempt)
```

Describes the change. Delete it:

```kotlin
// Now uses the shared client instead of creating one per request.
val response = client.get(url)
```

Tells the debug story:

```kotlin
// After a long debug session we found the observer fired twice because it
// was registered on a background thread, so we moved it to main.
```

Rewritten as a debugging hint:

```kotlin
// If this fires twice, the observer was registered off the main thread.
```

A better fix that you did not choose, with the condition to use it:

```ts
// TODO: Use a streaming parser if responses grow past a few MB.
```

A guard:

```rust
// Constant-time compare. Do not replace with `==`.
```

A workaround, with the upstream bug and the condition to remove it:

```python
# Work around https://bugs.example.com/4006. Remove this when the minimum
# supported version of the library has the fix.
```

## Check the diff

Do this before you commit, before you open a PR, and before you push to an
open PR. It covers only the comments on lines that your branch adds.

1. Run the tool:

   ```sh
   scripts/writing-for-code comments --diff origin/main --new-only
   ```

   Use the default branch of the repo in place of `origin/main`.
   `scripts/writing-for-code check` runs the same scan, and it also checks
   the changed docs and the commit messages.

2. For each flagged block, read the block and the code below it. Do the
   action in the table.
3. Read each comment that you added against the self-check below, flagged
   or not.
4. Run the tool again. Stop when you decided to keep each flag that
   remains.

| Flag | Action |
|---|---|
| `cross-ref`, `platform` | Delete the reference. Keep the rest only if it clears the bar. |
| `change`, `history` | Delete. Git and the PR hold the change. |
| `issue-ref` | Delete the link. The PR body links the issue. |
| `story` | Rewrite as a debugging hint: a symptom and its cause. If no hint remains, delete it. |
| `decision` | Move the reason to the PR body. Keep only the contract or the one-line why. |
| `narration`, `restates` | Delete. If the name of the symbol misled you, rename the symbol. |
| `sequence` | Delete. If the order is not clear from the code, extract named steps. |
| `hedge` | Delete, or replace with a fact: a measurement or a `TODO` that names the better fix. |
| `dead-code`, `banner` | Delete. |
| `todo-no-link` | For missing functionality, link the issue. For a better fix that you did not choose, keep it. |
| `long` | Shorten. An inline comment is rarely over two lines. Ignore it on a docstring that has standard sections. |
| `suppress`, `keep` | Leave it. A tool directive, a license, or a link. |

The flags are leads. The tool cannot tell a guard from narration. The
self-check is the requirement.

## Self-check

Ask these questions of each comment that you added or edited:

1. Does it cite other code as the reason for a decision?
2. Does it name another platform or its code?
3. Does it describe the change in place of the code?
4. Does it link an issue of this repo outside a `TODO` for missing work?
5. Does it tell a story, or give reasons and alternatives?
6. Can a competent reader find it fast in the code, the docs, or git?
7. Did you fetch each link that you wrote?

If the answer to any of 1 through 6 is yes, cut or delete the comment.
