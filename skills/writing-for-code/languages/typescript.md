# TypeScript and JavaScript doc comments (TSDoc, JSDoc)

Sources, checked on 2026-11-06:

- TSDoc: <https://tsdoc.org/>, and the tag pages for
  [`@param`](https://tsdoc.org/pages/tags/param/),
  [`@returns`](https://tsdoc.org/pages/tags/returns/),
  [`@throws`](https://tsdoc.org/pages/tags/throws/), and
  [`{@link}`](https://tsdoc.org/pages/tags/link/)
- TypeScript handbook, "JSDoc Reference":
  <https://www.typescriptlang.org/docs/handbook/jsdoc-supported-types.html>

If the repo uses JSDoc tags or TypeDoc, follow the repo.

## Syntax

`/** ... */` on the line before the declaration.

## The summary

The text before the first block tag. Make the first sentence say what the
item does.

## Parameters, returns, and errors

```ts
/**
 * Returns the route between two stops.
 *
 * @param start - The first stop.
 * @param end - The last stop. It must differ from `start`.
 * @returns The route, or `undefined` if no road connects the stops.
 * @throws {@link OfflineError} if the device has no network.
 */
export function route(start: Stop, end: Stop): Route | undefined
```

- `@param name - description`. The hyphen after the name is part of the
  format.
- `@returns`, not `@return`.
- Other tags: `@remarks` for details after the summary, `@example`,
  `@deprecated` with the replacement, `@see`.

## Links

`{@link Route}`, `{@link Route | the route}`, or `{@link pkg#Route}`.

## TypeScript and JavaScript differ

- In a `.ts` file, do not write types in the tags. The signature has them.
  TypeScript reads only the documentation tags in a `.ts` file.
- In a `.js` file, JSDoc type tags such as `@param {string} name` and
  `@type` give the types. Use them if the repo checks JavaScript with
  TypeScript.
