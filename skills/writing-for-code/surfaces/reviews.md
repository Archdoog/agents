# Code Reviews

Use flavored mode. Read the repository's review conventions and the relevant code before writing findings.
Lead with defects, ordered by their effect or severity.
For each finding, identify a location, the triggering condition, and the observable consequence.
Give enough evidence for the author to check the claim.

Distinguish defects, questions, and preferences. Do not present a personal wording preference as a correctness requirement.
Suggest a concrete correction when the evidence supports one.
Keep uncertainty explicit. Do not invent a failing execution path or claim reproduction without a run.
Review behavior and contracts, not the author's identity or presumed tools.

Keep summaries brief. Do not restate the diff or dilute findings with generic praise.
If no findings remain, say so and name relevant testing gaps.
For prose review, propose specific cuts or replacements and check them against [PRUNE.md](../PRUNE.md).
