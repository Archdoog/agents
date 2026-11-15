---
name: test-value
description: Evaluate agent-written tests by behavior, failure detection, unique coverage, and maintenance cost. Use for test-value reviews, test audits, or removal of weak tests. Supports check and fix modes.
---

# Test Value

Judge each test by the failures it can detect and the cost of keeping it useful.
Agent authorship defines the review scope. It does not imply poor quality.

## Modes and scope

- **Check:** Inspect and report. Do not edit files or post review comments. This is the default mode.
- **Fix:** Complete the check phase, apply supported changes, and verify the result. Use this mode when the user requests fixes.

Use the requested repository, range, or test paths.
Without a stated scope, use the current change, including committed branch changes when the base is clear.
Identify agent-written tests from session context, supplied paths, or explicit commit evidence.
Do not infer authorship from style, volume, or the commit author alone.
When authorship is unknown, review candidate tests and label their provenance as unknown.
For a whole-repository audit, inventory all candidate tests before selecting any for detailed review.
If the scope has no useful boundary, ask for the repository, range, or paths.

Include new tests, changed tests, generated cases, fixtures, snapshots, and test helpers in the scope.
Inspect existing tests at other layers when they can establish overlap or missing coverage.
Account for every scoped test. Group parameterized cases only when they share the same value and cost.
If limits prevent a complete review, list the unreviewed paths. Do not claim full coverage.

## Classification

Assign one primary class per test or justified group.
Record maintenance cost separately as low, medium, or high, with evidence.
Record confidence separately as high, medium, or low.

| Class | Meaning | Default action |
| --- | --- | --- |
| Load bearing | Protects essential behavior. Its loss creates a high risk of serious failure without equivalent protection. | Keep the protection. Simplify expensive structure when possible. |
| Valid coverage | Detects a credible regression in a supported behavior, boundary, or failure path. | Keep. Improve only when the benefit supports the cost. |
| Ok | Has some distinct value, but that value may not justify its continued maintenance. | Keep by default. Draft a short maintainer note for the PR. |
| Overburdened | Provides useful coverage, but its setup, coupling, runtime, or instability creates excessive maintenance cost. | Simplify, consolidate, or move the coverage to a suitable layer. |
| Delete | Adds little distinct protection, repeats equivalent coverage, or checks details without a supported behavioral reason. | Remove when evidence supports the decision. |
| Repair | Cannot reliably detect the claimed failure because its assertions, execution, or expectations are defective. | Repair if the behavior matters. Otherwise, justify deletion. |

Use **Needs context** as a review status when missing requirements or evidence prevent a supported classification.
Keep it separate from the value classes. Uncertainty is not evidence for deletion.

Check test validity first. A false pass or incorrect expectation takes the Repair class.
Record the importance of its intended behavior even when the test needs repair.
For valid tests, essential protection takes the Load bearing class even when maintenance cost is high.
Use Overburdened for other useful tests whose cost justifies a change.
Do not use a numeric score to replace these decisions.

## Check phase

### Establish the behavior

Read the requirements, relevant production code, test conventions, and existing regression history when available.
Map each test to a supported behavior and an observable failure.
Separate contract checks from assertions about private implementation details.
An internal assertion can be valid when it protects a documented invariant or an otherwise hidden failure.

### Examine failure detection

Identify a plausible defect that the test would detect.
Check whether the assertion observes the result through the real boundary that matters.
Look for missing assertions, skipped execution, swallowed failures, and asynchronous work that the test does not await.
Check whether mocks return the expected answer without exercising meaningful production behavior.
Check whether snapshots expose a meaningful contract or merely preserve incidental output.

Treat timing, randomness, environmental dependence, and shared state as evidence to investigate.
Do not call a test flaky from one unexplained failure.

Use red/green checks when inspection leaves important uncertainty about failure detection.
Apply this technique when practical for critical protection, Repair findings, and replacement coverage.
Do not require a full TDD workflow or mutation testing for every classification.

1. Confirm that the test passes with the supported behavior intact.
2. Introduce a representative defect or reproduce a known regression. Expect red: the test fails for the intended behavioral reason.
3. Restore correct behavior. Expect green: the test passes without weakening its assertions.

A setup error, syntax error, or unrelated timeout does not establish meaningful red evidence.
A test that stays green with the defect present may need repair or may protect a different behavior.
One detected defect does not prove protection against every relevant failure.

In check mode, use a disposable copy for probes that need file changes.
If you perform a temporary probe, isolate it from user edits and remove it before completion.

Record the defect, expected failure, actual result, and restored green result for each executed probe.
Distinguish executed red/green evidence from conclusions based on inspection.
A passing suite alone does not establish test value.

### Compare unique protection and cost

Compare the behavior, inputs, assertions, and execution boundary with related tests.
Shared lines of code do not prove duplication.
Boundary values, failure paths, platform differences, and past regressions can justify similar cases.
Use coverage data as supporting evidence. Coverage percentage alone does not establish value.

Before recommending deletion for overlap, name the retained test and explain which failures it still detects.
For another layer, verify that it exercises the same relevant behavior and observes the same failure.
A unit test may miss wiring failures. An end-to-end test may miss precise failure paths.
Prefer the least costly layer that preserves the required protection.

When overlap is uncertain, compare the tests against the same representative defects when practical.
Check whether each test fails for the intended reason and returns to green after restoration.
If only the test proposed for deletion detects a relevant defect, the retained coverage is not equivalent.
If both detect one defect, check other relevant boundaries before concluding that they are duplicates.
For example, both layers may detect a wrong total, while only an integration test detects incorrect request wiring.

Consider setup size, fixture ownership, dependency count, implementation coupling, runtime, and failure diagnosis.
Separate measured costs from estimates.
Do not penalize test length, mocks, snapshots, or a test layer without a concrete reason.

### Report the decisions

Give the reviewed scope, provenance evidence, and completeness first.
Use a compact table with these fields:

| Test or group | Protected behavior | Class or status | Cost | Confidence | Evidence and action |
| --- | --- | --- | --- | --- | --- |

Cite test names and file locations so maintainers can find each decision.
Keep routine Keep decisions brief. Give concrete evidence for Repair, Overburdened, Delete, and Needs context findings.
State the retained protection for each proposed deletion or consolidation.
Report validation results and any limits on the evidence.
For Ok tests, draft a PR note that states the limited benefit and the maintenance tradeoff.
Do not post the note or change a PR unless the user authorized that action.

## Fix phase

Use the check findings as the change plan. Do not treat each class as an automatic edit command.
Preserve existing user edits and required behavioral protection.

1. Repair false passes and incorrect expectations where the intended behavior is clear.
2. Simplify expensive tests while preserving their meaningful assertions and execution boundaries.
3. Remove tests with supported Delete findings.
4. Remove fixtures, snapshots, or helpers only after checking their remaining uses.
5. Run the affected tests and the relevant required repository checks.
6. Compare the final diff with the original behavior map.

Leave Load bearing and Valid coverage tests in place unless a specific improvement preserves their protection.
Keep Ok tests unless the user requests removal and the evidence supports it.
Leave Needs context items unchanged until the missing evidence supports an action.
If a test contains both useful and redundant assertions, preserve the useful assertions.
If replacement coverage is necessary, verify the replacement before removing the original test.

Do not remove useful coverage merely because moving it would require more work.
Do not weaken production behavior to justify a test change.
Report product defects separately unless the requested scope includes their repair.

For a false pass, keep the representative defect present while repairing the test. Confirm that the repaired test turns red.
Then restore correct behavior and confirm green.
For an incorrect expectation, establish the intended contract before changing the assertion.
For consolidation or layer changes, verify the retained tests against the claimed failure paths using the red/green checks above.
Simplify from a green baseline and confirm green after each meaningful change.
Repeat the relevant defect probe when a change could weaken failure detection.

If verification is unavailable, state the limit and retain protection that you cannot safely replace.
Do not delete an unexplained failing test to make the suite pass.

Report the edits, retained protection, check results, and unresolved decisions.
Include before and after classes for changed tests when the class changes.
Include the draft PR notes for remaining Ok tests.
