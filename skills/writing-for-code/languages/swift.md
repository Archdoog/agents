# Swift doc comments

Sources, checked on 2026-11-06:

- Swift API Design Guidelines: <https://www.swift.org/documentation/api-design-guidelines/>
- DocC, "Writing Symbol Documentation in Your Source Files":
  <https://www.swift.org/documentation/docc/writing-symbol-documentation-in-your-source-files>
- DocC, "Linking to Symbols and Other Content":
  <https://www.swift.org/documentation/docc/linking-to-symbols-and-other-content>

The DocC pages need JavaScript to show their text. If a fetch shows an empty
page, fetch the same path under `/documentation/docc/data/` with the
extension `.json`.

## Syntax

`///` on each line, or `/** ... */`. A blank `///` line starts a new
paragraph.

## The summary

- One sentence fragment that ends with a period. Keep it to 150 characters
  or fewer, with no links and no symbol names.
- A function or a method: say what it does and what it returns.
- An initializer: say what it creates.
- A subscript: say what it accesses.
- Any other declaration: say what it is.

## Parameters, returns, and errors

```swift
/// Returns the route between two stops.
///
/// - Parameters:
///   - start: The first stop.
///   - end: The last stop. It must differ from `start`.
/// - Returns: The route, or `nil` if no road connects the stops.
/// - Throws: `RoutingError.offline` if the device has no network.
func route(from start: Stop, to end: Stop) throws -> Route?
```

- Use `- Parameters:` with one nested item for each parameter, or
  `- Parameter name:` for one parameter.
- Use the internal name of the parameter, not the argument label.
- Use one `- Returns:` and one `- Throws:` at most. More than one gives
  undefined results.
- Other callouts: `- Complexity:`, `- Precondition:`, `- Important:`,
  `- Note:`, `- Warning:`.

## Links

Link to a symbol with double backticks: ``` ``Route`` ```,
``` ``Route/distance`` ```, ``` ``Router/route(from:to:)`` ```. Use a link,
not code voice, for another symbol.

## Do not

- Do not use the Apple "Markup Formatting Reference" in the Documentation
  Archive. It was last updated in 2017. Use the DocC pages.
- Do not repeat the types of the signature in the prose.
