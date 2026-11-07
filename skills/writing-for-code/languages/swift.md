# Swift Documentation

Fetch the official DocC reference once per session before documenting a public API.
Baseline: [Swift 6.2 DocC: symbol documentation](https://github.com/swiftlang/swift-docc/blob/swift-6.2-RELEASE/Sources/docc/DocCDocumentation.docc/writing-symbol-documentation-in-your-source-files.md).
Check the repository's Swift and DocC versions before using version-specific markup.

Use `///` or the repository's established documentation-comment form.
Start with a short summary, followed by discussion only when callers need it.
Use `- Parameter name:` fields or `- Parameters:` with the generator's required indentation.
Use one `- Returns:` section and one `- Throws:` section where applicable.
Describe when an optional result is `nil` and what conditions cause each relevant error.

Explain units, valid ranges, mutation, ownership, and resource lifetime when the signature does not convey them.
State actor isolation, callback execution requirements, or cancellation guarantees when callers depend on them.
Do not infer thread safety from `async` or invent behavior from an annotation alone.
Put framework or package overviews in the existing DocC catalog or documentation extensions.
Include setup for examples and check links with the repository's documentation build when available.
