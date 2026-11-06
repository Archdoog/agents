# Docstrings

Docstrings, doc comments, and module or package docs. Mode: flavored.

The bans and the self-check in `comments.md` also apply here.

## The language guide comes first

Each language has an official format: its comment syntax, its section
names, and its link syntax. Do not guess the format.

1. If the repo has a docstring style, use it.
2. If the language has a file in `languages/`, read it. For a public API,
   also fetch the official page that the file links, once in each session.
3. If the language has no file, fetch its official guide before you write.
   `languages/OTHER.md` lists the guides for the common languages.
4. If you cannot fetch the guide, write only the summary line. Tell the user
   that you could not get the guide.

| Language | File |
|---|---|
| Swift | `languages/swift.md` |
| Kotlin | `languages/kotlin.md` |
| Rust | `languages/rust.md` |
| TypeScript, JavaScript | `languages/typescript.md` |
| Python | `languages/python.md` |
| Any other language | `languages/OTHER.md` |

## What a docstring has

Each public API that you add, and each public API whose signature you
change, gets a docstring. This includes module and package docs.

1. Say what it does, and what its arguments are.
2. Add the standard sections of the language where they apply: returns,
   errors or throws, panics, safety, and deprecation.
3. Add the contract that the signature does not show: nil or null,
   ownership, thread safety, units, side effects, and complexity.
4. Add a usage example when the correct call is not obvious.

A summary line and a link to a doc is a complete docstring.

## What a docstring does not have

- The implementation or the algorithm, unless the caller must know it, for
  example the complexity.
- The history, or the reason for the design. Those go in the PR body.
- Types that the signature already shows.
- An argument description that repeats the argument name:
  "`id`: the id".

## Examples

History and design reasons, and arguments that repeat their names:

```kotlin
/**
 * Fetches the route. Added to support offline mode. We cache here rather than
 * in the repository layer because the repository is shared with sync.
 * @param id the id
 * @return the route
 */
```

Rewritten as a contract with the standard sections:

```kotlin
/**
 * Returns the cached route for [id], or fetches it when the cache misses.
 *
 * @throws IOException when the fetch fails.
 */
```

A summary line and a link in place of an explanation:

```swift
/// Encodes `coordinates` as a polyline string.
///
/// See https://developers.google.com/maps/documentation/utilities/polylinealgorithm
```

## Self-check

1. Does each public API that you added have a docstring?
2. Does it say what it does, and what its arguments are?
3. Does it have each standard section of the language that applies?
4. Did you use the section names and the link syntax of the language guide?
5. Is there history, design reasoning, or a type that the signature shows?
   Delete it.
