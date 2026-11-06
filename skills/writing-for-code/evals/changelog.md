# Changelog cases

### changelog-vague

- surface: changelog
- pass: lint
- expect: STE004

```input
Various bug fixes and improvements to make the experience seamless.
```

- why: Says nothing that a user can check.

### clean-changelog

- surface: changelog
- pass: lint
- expect: clean

```input
Fixed: `decode` keeps the last point of a route.
```

- why: A change in behavior that a user can check. A clean case.
