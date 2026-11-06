# Prune cases

The prune pass can fail in two ways. It can keep true text that nobody
needs, or it can cut a short block that carries a constraint. These cases
cover both.

### readme-architecture-section

- surface: readme
- pass: prune
- expect: score 0 for the whole section, delete it

```input
## Architecture

The project is organized into several directories. The `src/` directory
contains the source code. The `tests/` directory contains the tests. The
`docs/` directory contains the documentation. This structure makes it easy
to find what you need.
```

- why: Each sentence is true, but `ls` shows all of it. No reader makes a mistake without it.

### readme-closing-summary

- surface: readme
- pass: prune
- expect: score 0, delete the paragraph

```input
## Summary

In summary, polyline gives you a fast and simple way to decode route
strings in your app. Whether you are building a maps app or a fitness
tracker, it has you covered.
```

- why: It repeats the opening and adds no fact.

### comment-debug-hint-looks-like-a-story

- surface: comment
- pass: prune
- expect: score 4, keep

```input
// If the list flickers on scroll, the diffable data source got a
// snapshot with duplicate identifiers.
```

- why: A symptom and its cause. Without it, a maintainer debugging a flicker looks in the wrong layer.

### comment-guard-looks-like-narration

- surface: comment
- pass: prune
- expect: score 4, keep

```input
// Compare in constant time. Do not replace with `==`.
```

- why: The edit looks safe and is not. A maintainer who simplifies the code adds a timing leak.

### comment-restates-the-code

- surface: comment
- pass: prune
- expect: score 0, delete

```input
// Increment the retry counter
retryCount += 1
```

- why: The code says the same thing.

### comment-design-reason

- surface: comment
- pass: prune
- expect: score 2, move the reason to the PR body. Keep nothing in the comment.

```input
// We use a plain dictionary instead of NSCache because NSCache evicts
// entries under memory pressure, and we decided the cache must survive
// backgrounding. We considered a disk cache but it was too slow.
let cache: [RouteID: Route] = [:]
```

- why: A design reason with alternatives belongs to the PR. The comment surface does not hold reasoning.

### pr-body-file-walkthrough

- surface: pr
- pass: prune
- expect: score 0 for the file list and the closing paragraph, delete both. Keep the first paragraph and the verification.

```input
Retries a failed upload once, after 500 ms.

Changes:
- `Uploader.swift`: added a retry.
- `UploaderTests.swift`: added a test.
- `Constants.swift`: added `retryDelay`.

Verified: `swift test` passes, with a new test for the retry path.

Overall, this change makes uploads more robust and improves the user
experience on slow networks.
```

- why: The diff shows the files. The last paragraph repeats the first with marketing words.

### docstring-unit-is-load-bearing

- surface: docstring
- pass: prune
- expect: score 4, keep

```input
/// The distance to the next maneuver, in meters.
var distanceToManeuver: Double
```

- why: The type does not show the unit. A caller can show kilometers as meters.

### docstring-verbose-but-real

- surface: docstring
- pass: prune
- expect: score 3, replace with "Returns the cached route for `id`, or fetches it on a miss. Thread-safe."

```input
/// This function is responsible for returning the route that corresponds
/// to the given identifier. It first checks the cache, and if the route is
/// not found in the cache, it fetches the route from the network. It is
/// important to note that this function is safe to call from any thread.
func route(for id: RouteID) async throws -> Route
```

- why: The contract is real: cache then network, and thread safety. The words around it are not.

### clean-runbook-step

- surface: procedure
- pass: prune
- expect: no cuts

```input
1. Stop the worker: `systemctl stop route-worker`.
2. If `systemctl status route-worker` shows `active`, wait 30 seconds and
   run it again.
3. Delete the lock file: `rm /var/run/route-worker.lock`.
4. Start the worker: `systemctl start route-worker`.
```

- why: Each step is one action that the on-call engineer needs. A clean case.

### clean-readme

- surface: readme
- pass: prune
- expect: no cuts

```input
# polyline

Encodes and decodes Google polyline strings in Swift.

## Install

Add the package to `Package.swift`:

    .package(url: "https://github.com/example/polyline", from: "2.0.0")

## Use

    let points = try Polyline.decode("_p~iF~ps|U")
    // [Coordinate(latitude: 38.5, longitude: -120.2)]

See the [API reference](https://example.github.io/polyline/) for the
encoder options.
```

- why: It answers the four README questions and nothing more. A clean case.
