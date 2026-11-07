# API, Module, and Package Documentation

Use flavored mode. Code syntax and identifiers remain outside the writing rules.
Document public APIs that you add or whose contract you change, including modules and packages.
Use the repository's documentation generator and established language conventions.

Start with behavior, then explain inputs and results beyond what names and types reveal.
Include relevant errors, nullability, units, valid ranges, ownership, side effects, and concurrency requirements.
State cancellation behavior or resource lifetime when callers must account for it.
Describe guarantees, not incidental implementation details. Keep an algorithm explanation when callers need it to choose or use the API.

Add an example when correct use is not obvious. Include enough setup to make it valid.
Do not add empty sections or parameter descriptions that merely repeat names.
A summary and a link are enough only when they convey the complete caller contract.

Load only the matching language note:

| Language | Note |
|---|---|
| Swift | [swift.md](../languages/swift.md) |
| Kotlin | [kotlin.md](../languages/kotlin.md) |
| Rust | [rust.md](../languages/rust.md) |
| TypeScript and JavaScript | [typescript-javascript.md](../languages/typescript-javascript.md) |
| Python | [python.md](../languages/python.md) |

Before documenting a public API, fetch its official language guide once per session.
Use the pinned reference as a baseline, then check the version that the repository uses.
For another language, fetch its official documentation-comment guide before writing docstrings.
Also inspect the project's generator configuration. Do not invent tags by analogy with another language.

If you cannot fetch a required reference, state that limit and separate unverified syntax from checked guidance.
Do not claim that a documentation build or example test passed unless you ran it.
