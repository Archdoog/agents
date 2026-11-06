# Rust doc comments (rustdoc)

Sources, checked on 2026-11-06:

- The rustdoc book, "How to write documentation":
  <https://doc.rust-lang.org/rustdoc/how-to-write-documentation.html>
- The rustdoc book, "Linking to items by name":
  <https://doc.rust-lang.org/rustdoc/write-documentation/linking-to-items-by-name.html>
- Rust API Guidelines, "Documentation":
  <https://rust-lang.github.io/api-guidelines/documentation.html>

## Syntax

`///` documents the next item. `//!` documents the crate or module that
contains it.

## Structure

1. A summary of one line that says what the item is. Search shows the text
   before the first blank line.
2. A longer explanation, if one is necessary.
3. At least one example.
4. Advanced details, if any.

## Sections

Use these headings, spelled exactly:

| Heading | When |
|---|---|
| `# Examples` | Every public item ([C-EXAMPLE](https://rust-lang.github.io/api-guidelines/documentation.html#all-items-have-a-rustdoc-example-c-example)) |
| `# Errors` | The function returns `Result` |
| `# Panics` | The function can panic |
| `# Safety` | The function is `unsafe`. List each invariant that the caller must keep. |

The guideline for errors and panics also covers trait methods
([C-FAILURE](https://rust-lang.github.io/api-guidelines/documentation.html#function-docs-include-error-panic-and-safety-considerations-c-failure)).

```rust
/// Decodes a polyline string into coordinates.
///
/// # Errors
///
/// Returns [`DecodeError::Truncated`] if the string ends inside a value.
///
/// # Examples
///
/// ```
/// let points = polyline::decode("_p~iF~ps|U")?;
/// assert_eq!(points.len(), 1);
/// # Ok::<(), polyline::DecodeError>(())
/// ```
pub fn decode(encoded: &str) -> Result<Vec<Point>, DecodeError>
```

## Links

Intra-doc links use the path of the item: ``[`Vec`]``,
``[`Self::push`]``, ``[`crate::Point`]``, or ``[label](Vec)``. Backticks
inside the brackets are optional.

## Do not

- Do not write the types in the prose. rustdoc links the types of the
  signature.
- Do not use `unwrap` in an example. Use `?`
  ([C-QUESTION-MARK](https://rust-lang.github.io/api-guidelines/documentation.html#examples--not-try-not-unwrap-c-question-mark)).
