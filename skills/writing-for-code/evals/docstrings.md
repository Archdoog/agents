# Docstring cases

### docstring-filler

- surface: docstring
- pass: lint
- expect: STE005, STE006

```input
This function is responsible for returning the route. It is important to note that it utilizes the cache.
```

- why: Filler and a long word.

### docstring-kotlin-params-rewrite

- surface: docstring
- pass: rewrite
- expect: keeps the summary and the throws section, loses @param lines that repeat the names, names the parameter as [id]

```input
/**
 * Fetches the route.
 * @param id the id
 * @return the route
 * @throws IOException if it fails
 */
fun route(id: RouteId): Route
```

- why: KDoc discourages @param and @return. languages/kotlin.md says to name the parameters in the sentence.

### clean-docstring

- surface: docstring
- pass: lint
- expect: clean

```input
Returns the cached route for `id`, or fetches it when the cache misses.
```

- why: A contract in one line. A clean case.
