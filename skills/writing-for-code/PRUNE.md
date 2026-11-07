# The Prune Pass

Keep text that prevents a specific mistake or explains a relevant concept, constraint, or decision.
Judge usefulness for the intended reader and task. Do not assume that reader can inspect implementation details or project history.

## Score and Act

| Score | Meaning | Action |
|---|---|---|
| 0: Noise | No useful information, or an unsupported flourish | Delete |
| 1: Findable | Repeats information the reader can readily find where they need it | Delete |
| 2: Misplaced | Useful information in the wrong location | Move, then reassess there |
| 3: Useful but verbose | Helps the reader, but includes excess wording | Shorten without losing its value |
| 4: Useful as written | Helps the reader and needs no edit | Retain |

For scores 3 and 4, name the reader and the block's specific value in your working notes.
For example: "Future maintainers need this constraint to avoid invalidating active references."
A vague claim that the block "adds context" is not enough.

Findability depends on access, effort, and timing. A public API caller may never see the implementation.
History can explain a past edit, but it does not replace a current safety constraint beside code.
An example may repeat a rule while making its correct use clear. Keep that example when the reader needs it.

## Apply the Test

1. Score each sentence against the reader's task.
2. Apply its action without changing facts or qualifications.
3. Score each resulting paragraph, section, and the whole page.
4. Check moved text in its destination for usefulness, duplication, and lost context.
5. Compare the final text with the source for missing facts, warnings, examples, and required fields.

Stop when every retained block meets the retention test and further edits offer no specific benefit.
Do not keep cutting to reach a length target. An unchanged result can be correct.

Preserve useful rationale beside code when it prevents an unsafe change.
For example, keep a cache's no-eviction rule if eviction would invalidate references held by active requests.
The editing history can disappear. The constraint and its consequence must remain.

Preserve required template fields, warnings, and background the reader needs.
Exempt tool directives, license notices, and required template structure from pruning.
Skip README badges, images, and HTML presentation blocks. Do not change their markup during a prose pass.
For out-of-scope material, leave it alone rather than moving it without permission.

## Fresh-Eyes Review

Require a fresh-eyes review for every authored or revised README and guide.
Also require it for PR bodies over about 150 words and whenever the user requests it.
Use the same review for this guidance when the task requires one.

Give the reviewer the finished text, its surface, and relevant code paths.
Do not include the author's conversation, drafting history, or reasons for individual wording choices.
Use this brief:

```text
Review the attached text without rewriting unrelated material.
Surface: <surface and publication location>
Reader and task: <intended reader and their task>
Scope: <allowed text or files>
Repository requirements: <applicable instructions and template>
Relevant code, tests, and references: <paths or links>
Text: <complete text or an accessible path>

Return specific cuts or replacements with a location and a reason.
For retained context, identify the mistake it prevents or the concept it explains.
Do not assume the reader can inspect code or history.
Check factual support, contracts, required fields, and lost qualifications.
Say when no change is needed. Do not infer authorship from style.
```

Check each suggestion against the retention test before applying it.
Reject cuts that remove a useful constraint, warning, qualification, or explanation.
Recheck the resulting text after accepted edits.

If independent review is unavailable or prohibited, do not start a child or claim that review occurred.
Prepare the brief for the next reviewer and report the review gap with the work status.
For rewrite-only output, keep that status outside the revised text and use the permitted reporting channel.
