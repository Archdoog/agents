# Core — how to write prose for code

## Scope

Do not rewrite:

- Code: identifiers, signatures, and command syntax. The rules apply to the
  comment above the code, not to the code.
- Quoted material: logs, diffs, stack traces, and the words of a person.
  Quote them exactly.

## Precedence

1. The repo: its `CONTRIBUTING.md`, its docs, its templates, and the style
   of the nearby code or text.
2. The official guide for the language, for docstrings.
3. This skill.

## The universal rule

Replace each vague claim with a fact that the reader can check: a number, a
name, a version, a command, a path, or the mechanism.

| Vague | Checkable |
|---|---|
| Improves performance | Cuts cold start from 900 ms to 300 ms on a Pixel 6 |
| Handles edge cases | Returns `nil` for an empty string |
| Updated the docs | Documents the `--strict` flag in `README.md` |

If you do not have the fact, do not invent it. Write the gap down: "Not
measured." or "Not tested on Windows."

## What to put in

Write only what the reader needs to act correctly:

- **The contract.** Inputs, outputs, errors, units, nil or null, thread
  safety, and ownership.
- **The constraint.** A limit or a rule that the code does not show.
- **The cause.** The reason for code that looks wrong, in one line.
- **The proof.** The command or the steps that show the change works.
- **A link.** If a doc explains it, link the doc. Do not repeat it.

## What to leave out

- Text that says again what the code, the heading, or the last sentence
  says.
- The story of how you got here: the debug session, the attempts, the
  surprise.
- The alternatives that you did not take.
- Chat text: "Certainly!", "I hope this helps",
  "Let me know if you want more".
- Lead-ins that announce the text: "This section describes",
  "In this guide, we will".
- Summaries at the end that repeat the text above them.
- Words that tell the reader how to feel: "Importantly,",
  "As you can see", "The key point is".
<!-- writing-for-code: off -->
- Marketing words: seamless, robust, powerful, comprehensive, elegant.
<!-- writing-for-code: on -->

## Form

Write in ASD-STE100 Simplified Technical English. Each surface file sets a
mode.

- **Strict mode:** error messages, CLI help, runbooks, and procedures. The
  reader can be under pressure. Apply every rule, and a cap of 20 words for
  each sentence.
- **Flavored mode:** everything else. Apply every rule. The word table is a
  strong preference, not a lock. The cap is 25 words for each sentence.

The rules:

1. Use one name for one thing. Use the name that the code uses.
2. Use the short common word: `use`, not `utilize`. `start`, not
   `initiate`. `make sure`, not `ensure`. Run `writing-for-code rules` for
   the full list.
3. Use the active voice, and name the actor.
4. Use one verb for one action: "analyze the log", not
   "perform an analysis of the log".
5. Write one instruction in each sentence.
6. Do not use contractions or semicolons. The em dash is allowed.
7. Keep the articles: a, an, the.
8. Put the condition before the command: "If the check fails, stop."
9. Write a paragraph about one topic, with six sentences at most.
10. Write a sequence of actions as a numbered list, one action for each
    item.

In flavored mode, do not cut prose into a chain of very short sentences.
That chain is also a sign of generated text. Join two related clauses
with "and", "but", "because", or "so".

## Links

- Fetch each link before you write it.
- Use a stable address: a versioned page, an anchor, or a commit permalink.
  Do not link to a branch.
- In a public repo, link only to public pages.

## When you edit text that exists

- Keep each fact, number, name, date, and link that the text supports. A
  rewrite that drops one has failed.
- Do not add facts, opinions, or a voice that the text did not have.
