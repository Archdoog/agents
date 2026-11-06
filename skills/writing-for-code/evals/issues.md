# Issue cases

### issue-no-repro-rewrite

- surface: issue
- pass: rewrite
- expect: has the observed result, the expected result, numbered steps, the environment, and a label on the guess

```input
The app is broken when you open some routes, probably because of the new decoder. Please fix ASAP!!
```

- why: The surface file asks for steps and for a label on each guess.

### clean-issue

- surface: issue
- pass: lint
- expect: clean

```input
The app crashes when I open a route with no points.

1. Open the app.
2. Open route r_123.

Expected: an empty map. Observed: a crash.
```

- why: Observed, expected, and steps. A clean case.
