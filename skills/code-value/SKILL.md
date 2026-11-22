---
name: code-value
description: Evaluate the source code in a PR or branch diff by required behavior, added code surface, and maintenance cost. Finds custom code that a library replaces, new structures that existing code can carry, and protection against conditions that cannot occur. Use for code-value reviews, over-engineering checks, or reduction of a diff before review. Supports check and fix modes. Pairs with test-value, which covers the tests.
---

# Code Value

Judge each added component by the behavior it delivers and the cost of keeping it correct.
Each added line is a place for a defect and a cost for each later reader.
A small change with a known limit can often be safer in the long term than a large change that covers every case.

## Modes and scope

- **Check:** Inspect and report. Do not edit files or post review comments. This is the default mode.
- **Fix:** Complete the check phase, apply supported changes, and verify the result. Use this mode when the user requests fixes.

Use the requested PR, range, or paths.
Without a stated scope, use the current branch diff against its base, including uncommitted changes.
If the base is not clear, ask for it.

Review non-test source, configuration, and build files. Leave tests to the `test-value` skill.
Exclude generated files, lockfiles, and vendored code.
Apply the same standard to all code in scope. Do not infer authorship from style or volume.

Divide the diff into components. A component is a function, type, module, option, or logic branch with one purpose.
Account for every component. If limits prevent a complete review, list the unreviewed paths.

## Classification

Assign one primary class per component. Record added lines and confidence (high, medium, or low) separately.

| Class | Meaning | Default action |
| --- | --- | --- |
| Required | Delivers the required behavior in a form close to the smallest that fits the codebase. | Keep. |
| Replace | The standard library, the platform, or an established library solves the same problem. | Call the library. Delete the custom code. |
| Align | An existing structure in the codebase can carry the change without loss of behavioral control. | Ask the developer first. Move the change into the existing structure unless they decline. |
| Reduce | The purpose is valid, but the form is larger than the purpose needs. | Simplify to the smallest form that keeps the required behavior. |
| Remove | No required behavior depends on the component. | Delete. |
| Defer | The work is valid but is not part of the purpose of this change. | Remove from the diff. Draft a follow-up note. |

Use **Needs context** as a review status when missing requirements or evidence prevent a supported class.
Uncertainty is not evidence for removal.

## Check phase

### Establish the required behavior

Read the PR description, the linked issue, and the session context.
State the behavior that the change must deliver in one or two sentences.
Read the adjacent code: the error types, helpers, conventions, and dependencies that are already there.
Map each component to the required behavior. A component with no path to that behavior needs a different reason to stay.

### Measure the surface

Record the added lines for each component. Note each new type, public symbol, option, dependency, and branch.
Rank the components by size. Examine the largest components first.

For each large component, sketch the smallest version that delivers the required behavior.
Compare the two versions. If the sketch has 10 lines and the diff has 100, the other 90 lines need evidence.

### Examine each component

Ask these questions in sequence. The first supported answer gives the class.

1. **Does a library solve this?** Look first in the project dependencies, then the standard library and platform, then established open source.
2. **Can existing code carry this?** Look for an error type, helper, model, or convention that already does a similar job.
3. **Can the condition occur?** For each guard, fallback, and error path, name the input that reaches it.
4. **Does a caller use this now?** Options, extension points, and layers with one user are speculation.
5. **Does this change need it?** Unrelated refactors and adjacent features belong to a different change.

[PATTERNS.md](PATTERNS.md) lists the common patterns for each question, with signals, checks, and examples.

### Weigh the protection

The diff is not the only protection. Count the other layers before you call a guard necessary.
These layers are the type system, validation at the boundary, the test suite, code review, monitoring, and bug reports.
A change can leave a rare case open. A stated limit costs less than 100 lines that no one can reason about.

Keep protection, even when large, when:

- It likely fulfills a real goal of the current task.
- It likely fulfills a goal of the project and its current scope.
- An assessment of the potential risk is worth discussing with the developer. Ask the developer and decide on a solution together.

### Report the decisions

Give the reviewed scope, the required behavior, and the total added lines first.
Use a compact table, largest reduction first:

| Component | Location | Lines | Class or status | Confidence | Evidence and action |
| --- | --- | --- | --- | --- | --- |

Keep Required decisions brief. Group small Required components.
For each other class, name the replacement: the library call, the existing structure, or the smaller form.
State each case that a reduction leaves open, and the layer that will catch it.
For each Align finding, ask whether planned work needs the new structure.

Give the estimated line count after the changes.
Do not post comments or change a PR unless the user authorized that action.

## Fix phase

Use the check findings as the change plan. Preserve user edits and the required behavior.

1. Run the tests and the required repository checks. Start from a green baseline.
2. Apply the Remove and Defer findings. Then apply Align, Replace, and Reduce.
3. Change one component at a time. Run the affected tests after each change.
4. Delete tests that cover only removed code. Do not weaken a test that protects the required behavior.
5. If a required-behavior test fails, the reduction removed too much. Restore the behavior.
6. Run the full checks. Compare the final diff with the required behavior.

Ask the developer about each Align finding before you apply it. Name the new structure and the existing one.
The developer may know of planned work that needs the new structure.
If the developer declines, keep the new structure and record the reason in the report.
If the developer accepts or gives no decision, move the change.

Use a library that the project already has without a question.
A new dependency is a maintainer decision. Check its maintenance, license, and size against the code it replaces.
Then propose it and wait for approval, unless the user already authorized new dependencies.

Leave Needs context items unchanged. Do not change behavior outside the diff to make a reduction fit.
Report the edits, the added lines before and after, the check results, and the unresolved decisions.
Draft a PR note for each open case and each deferred item. Do not file issues without authorization.

## Use with test-value

The two skills cover one diff: `code-value` covers the source, and `test-value` covers the tests.
Run `code-value` first. Removed source removes the reason for some tests, which makes the test review smaller.
Then run `test-value` on the tests that remain.
