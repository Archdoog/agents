# Kotlin doc comments (KDoc)

Sources, checked on 2026-11-06:

- KDoc: <https://kotlinlang.org/docs/kotlin-doc.html>
- Coding conventions, documentation comments:
  <https://kotlinlang.org/docs/coding-conventions.html#documentation-comments>

## Syntax

`/** ... */`. A leading `*` on a line is not content. A short comment can
fit on one line: `/** Returns the cached route. */`.

## The summary

The first paragraph, up to the first blank line, is the summary.

## Parameters, returns, and errors

The coding conventions say: "Generally, avoid using `@param` and `@return`
tags." Name the parameters in the sentence, as links:

```kotlin
/**
 * Returns the route between [start] and [end], or `null` if no road
 * connects them.
 *
 * @throws IOException when the device has no network.
 */
fun route(start: Stop, end: Stop): Route?
```

- Use `@param name` only when a parameter needs a long description.
- Use `@throws Class` for an exception that a caller must handle. Kotlin
  has no checked exceptions, so you do not have to list each one.
- Other tags: `@receiver`, `@property name`, `@constructor`, `@sample`,
  `@see`, `@since`.

## Deprecation

KDoc does not support `@deprecated`. Use the `@Deprecated` annotation, with
a `ReplaceWith` if a replacement exists.

## Links

`[name]`, `[label][name]`, or a qualified name such as
`[kotlin.collections.List]`. A qualified name uses `.` also before a
function name. A link cannot pick one overload.
