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

Follow nearby documentation examples and inspect the repository's documentation generator configuration.
Preserve annotations that carry type information and caller obligations that affect safety or correct use.
Do not invent guarantees or tags by analogy with another language.

When syntax, tags, or version support are uncertain, check official documentation for the repository's language and generator versions.
Use available documentation builds or example tests when they can verify the affected syntax or behavior.

If you cannot fetch a required reference, state that limit and separate unverified syntax from checked guidance.
Do not claim that a documentation build or example test passed unless you ran it.
