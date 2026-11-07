# Kotlin Documentation

Fetch the official KDoc guide once per session before documenting a public API.
Baseline: [KDoc source snapshot](https://github.com/JetBrains/kotlin-web-site/blob/f51dacdc4420c6690ad88d513caf3c1a0a25b75f/docs/topics/kotlin-doc.md).
For module or package text, also fetch [Dokka module documentation](https://kotlinlang.org/docs/dokka-module-and-package-docs.html).
Check the repository's Kotlin and Dokka versions before using generator-specific features.

Use `/** ... */`. Put the summary in the first paragraph and details after a blank line.
Link parameters and symbols with `[name]` when that makes the sentence useful.
Use `@param`, `@return`, `@receiver`, `@property`, and `@constructor` where they add contract information.
Use `@throws` for relevant failure conditions. Do not list every possible unchecked exception.

KDoc does not support `@deprecated`. Describe an existing `@Deprecated` annotation rather than inventing that tag.
Use `@sample` only with a real sample function the generator can resolve.

Explain null results, units, mutable state, ownership, and resource lifetime where relevant.
For coroutine APIs, describe cancellation and concurrency requirements that callers must know.
Do not infer dispatcher behavior or thread safety from `suspend`.
Use included Markdown files with `# Module name` and `# Package qualified.name` headings for Dokka overviews.
Follow the existing Dokka configuration rather than adding a different documentation path.
