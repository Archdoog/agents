# Prune — delete what the reader does not need

Generated prose is too long. Most of the extra text is true, so a check for
facts does not find it. The prune pass finds it. Its job is to delete.

Every block must earn its place. A block is a sentence, a comment, a
paragraph, a section, or a page.

## The scores

| Score | Meaning | Action |
|---|---|---|
| **0 — Noise** | It says again what the code, the heading, or the text above says. Or it is chat text, a lead-in, or a summary. | Delete |
| **1 — Findable** | It is true, but a competent reader finds it fast in the code, the types, the library docs, or `git log`. | Delete |
| **2 — Misplaced** | It is a real fact on the wrong surface. Example: a design reason in a comment belongs in the PR body. | Move it, and score it again on the new surface |
| **3 — Load-bearing, verbose** | It passes the test below, but it uses more words than it needs. | Cut it to the shortest form that still passes |
| **4 — Load-bearing** | It passes the test below, and no word can go. | Keep |

### The test for a 3 or a 4

A block scores 3 or 4 only if you can complete this sentence:

> Without this block, **(a named reader)** will **(a specific wrong
> action)**.

- A named reader: "a caller of `decode`", "an on-call engineer at 3 a.m.",
  "a reviewer of this PR". Not "the reader" or "developers".
- A specific wrong action: "pass meters where the function expects
  kilometers", "restart the wrong service". Not "be confused" or "not
  understand the design".

If you cannot complete the sentence, the block scores 0 or 1.

## How to score

1. Score each sentence.
2. Delete the sentences that score 0 or 1. Move the ones that score 2.
   Shorten the ones that score 3.
3. Score each paragraph or comment that remains, as a whole.
4. Score each section, then the page. A section can score 0 when each of
   its sentences is true. Example: a README "Architecture" section that
   lists the directories that `ls` shows.
5. Stop when each block that remains scores 4.

Do not score these. Other rules cover them:

- Tool directives, license headers, and the parts of a template that the
  repo requires.
- In a README: badges, logos, images, and HTML presentation blocks. Score
  the prose only.

## Two ways to run the pass

### The self-pass

Always run it on your own text before you return it. Run it silently. Apply
the cuts. Do not report the scores.

The self-pass is weak, because you wrote the text and you remember why
each block seemed necessary. To make it stronger, read the text as the
named reader, not as the author.

### The fresh-eyes pass

A separate agent scores the text. It does not see your conversation or
your reasons. Run it:

- On each README, guide, or `docs/` page that you write or rewrite.
- On a PR body over about 150 words.
- When the user asks for it: "prune this", "cut this down", "is all of
  this necessary".

Start a new agent. Do not fork the current agent, because a fork keeps your
reasons. Give it the brief below, the text, the surface, and the paths of
the code that the text describes. Do not give it your draft notes.

Apply the cuts that you agree with. If you keep a block that it cut, you
must be able to complete the test sentence for that block.

## The fresh-eyes brief

Copy this brief, and fill in the three fields.

```text
You are a pruning editor. Your job is to delete. Every block of the text
below must earn its place. A block is a sentence, a comment, a paragraph,
a section, or a page.

Surface: <surface>
Code that the text describes: <paths, or "none">
Text:
<text>

Score each block from 0 to 4:

0 Noise. It says again what the code, a heading, or earlier text says.
  Or it is chat text, a lead-in, or a summary.
1 Findable. It is true, but a competent reader finds it fast in the code,
  the types, the library docs, or git.
2 Misplaced. It is a real fact on the wrong surface. Name the surface.
3 Load-bearing but verbose. Give the shorter form.
4 Load-bearing. Keep it.

A block scores 3 or 4 only if you can complete: "Without this block,
<a named reader> will <a specific wrong action>." "Developers" is not a
named reader. "Be confused" is not a specific wrong action.

Score sentences first, then the paragraphs that remain, then the sections,
then the page. Read the code paths to decide what is findable.

Do not score tool directives, license headers, parts of a template that
the repo requires, or README badges, images, and HTML.

Return a list of cuts, one line each, and nothing else:

<location> · <score> · <reason> · <action>

The location is a line number or a quoted opening of the block. The action
is "delete", "move to <surface>", or "replace with: <shorter text>". Do
not rewrite the text. Do not list the blocks that score 4.
```
