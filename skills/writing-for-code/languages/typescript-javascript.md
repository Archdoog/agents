# TypeScript and JavaScript Documentation

Fetch the official TypeScript JSDoc reference once per session before documenting a public API.
Baseline: [TypeScript JSDoc source snapshot](https://github.com/microsoft/TypeScript-Website/blob/3b069fb7d66c9c69b590c18e5cb9f9fa92b16467/packages/documentation/copy/en/javascript/JSDoc%20Reference.md).
For exception tags, also fetch [JSDoc: `@throws`](https://jsdoc.app/tags-throws).
Check the repository's TypeScript version and documentation generator. Compiler support and rendered tag support are different concerns.

Use `/** ... */` with a behavior summary.
Follow the repository's JSDoc or TSDoc form for `@param`, `@returns`, `@throws`, and examples.
Do not repeat TypeScript types in prose or duplicate them in JSDoc type expressions.
In JavaScript, keep JSDoc type annotations that supply otherwise missing type information.
Use `@deprecated`, `@see`, and `{@link ...}` where the toolchain supports them and the content is useful.

Distinguish synchronous exceptions from promise rejections.
Describe `null`, `undefined`, omitted options, units, mutation, ownership, and cleanup obligations where relevant.
State callback ordering or concurrency guarantees only when the implementation supports them.

Follow the generator's existing module and package overview format. Do not invent a package tag from another tool's syntax.
Include imports and asynchronous setup in examples. Check generated links when a documentation build is available.
