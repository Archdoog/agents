# Code Value Patterns

Each pattern gives a signal to find it, a check to confirm it, and the usual fix.
A signal is a reason to look. It is not a finding until the check confirms it.

## Replace: a library solves the problem

**Signal:** Arithmetic, parsing, or protocol code that is not specific to the product.
Common areas are geometry, dates and time zones, URLs, paths, encodings, retries, collections, and text formats.

**Check:** Search the project dependencies first, then the standard library and the platform SDK.
Then search for an established library. Confirm that the library covers the cases the product uses.

**Fix:** Call the library. Delete the custom code and the tests that only checked its arithmetic.

Example: a diff adds 40 lines that sum haversine distances along a polyline.
The project already depends on a geometry library with a length function. One call replaces the 40 lines.
The library also handles the antimeridian and empty input, which the custom code did not.

Never keep custom cryptography, date arithmetic, or escaping for SQL, HTML, or shell. Libraries own these areas.

The reverse case also adds surface. A new dependency that replaces three clear lines is not a reduction.

## Align: existing code can carry the change

### Parallel error surface

**Signal:** A new error enum, exception hierarchy, or result type beside one that the project already has.

**Check:** List what each caller does with each new case. Callers usually show a message, retry, or stop.
If two cases cause the same caller behavior, the callers do not need two cases.

**Fix:** Add the one or two cases that change caller behavior to the existing type. Delete the second type.

Example: a project has `AppError` with `network`, `notFound`, and `invalid(String)`.
A diff adds `UploadError` with nine cases and a mapper to `AppError`.
Every caller shows the message, and one case also triggers a retry.
One new `AppError` case for the retry and `invalid(String)` for the others keep the same control.

### Duplicate helper or model

**Signal:** A new utility, extension, or data type whose name or fields are close to an existing one.

**Check:** Search the codebase for the operation, not the name. Compare the fields and the behavior.

**Fix:** Use the existing item. If it lacks one field or option, extend it.

### Second pattern for a solved problem

**Signal:** A new way to make requests, load configuration, store state, log, or inject dependencies.

**Check:** Find how the nearest similar feature does the same job.

**Fix:** Follow the existing pattern, even when the new pattern is better alone.
Two patterns cost more than one average pattern. A migration to a better pattern is a separate change.

## Reduce: the form is larger than the purpose

### Guard against a condition that cannot occur

**Signal:** A null check on a value that the type makes non-null. Validation of input that a caller already validated.
A `catch` around code that does not throw. A default branch on a closed set of cases.

**Check:** Name the invariant that prevents the condition. Confirm it at the call sites.

**Fix:** Delete the guard. If the invariant is not visible in the types, make the type carry it.

### Fallback that hides a failure

**Signal:** A `catch` that returns a default value, an empty list, or a cached copy without a report.

**Check:** Ask what a developer sees when this path runs. If the answer is nothing, the fallback hides defects.

**Fix:** Let the error propagate to the existing error handling. Keep a fallback only where the requirement names one.

### Speculative structure

**Signal:** An interface with one implementation. A generic parameter with one type. An option that no caller sets.
A registry, builder, strategy, or feature flag for one behavior.

**Check:** Count the current users in the codebase. Plans are not users.

**Fix:** Replace the structure with the concrete code. The abstraction is easy to add when a second user appears.

### Layer that only forwards

**Signal:** A manager, service, wrapper, or coordinator whose methods call one other method with the same arguments.

**Check:** List what the layer adds: a policy, a translation, or a test seam that a test uses.

**Fix:** If the list is empty, delete the layer and call the target directly.

### Machinery without a measurement

**Signal:** A cache, pool, batch, debounce, memoization, lock, or retry loop in a change that does not report a measured problem.

**Check:** Look for the measurement or the bug report. Check whether the framework already supplies the behavior.

**Fix:** Delete the machinery. Caches and locks are a common source of defects that are hard to reproduce.

### Constants and configuration for fixed values

**Signal:** A configuration file, environment variable, or injected setting for a value with one known use.

**Fix:** Use a local constant.

## Remove: nothing depends on it

### Compatibility for callers that do not exist

**Signal:** A deprecated alias, a shim, a version check, or a migration for a format that no release shipped.

**Check:** Search for callers and for released data in the old format.

**Fix:** Delete it and change the callers in the diff directly.

### Unused code

**Signal:** A public symbol with no caller, a parameter that no caller passes, or a helper used only by its own test.

**Fix:** Delete it and its test.

### Diagnostics on every branch

**Signal:** A log line, metric, or trace on each step of a routine operation.

**Check:** Ask which line a developer would read during a real failure.

**Fix:** Keep the lines at the failure points and at the boundary. Delete the others.

## Defer: valid work for a different change

### Unrelated change

**Signal:** A rename, a reformat, a refactor, or a dependency update in files that the required behavior does not touch.

**Fix:** Revert it in this diff. Note it as a follow-up.

### Full solution for a rare case

**Signal:** A large part of the diff handles a case that the requirement does not name and that occurs rarely.

**Check:** Estimate how often the case occurs and what the user sees when it does. Name the layer that reports it.

**Fix:** Handle the case in the simplest safe way, usually an error through the existing surface. Note the limit in the PR.
