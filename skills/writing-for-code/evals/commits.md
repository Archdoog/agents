# Commit message cases

### commit-bad-shape

- surface: commit
- pass: lint
- expect: COMMIT002, COMMIT003, COMMIT004

```input
Updated the upload code.
Also fixed tests.
```

- why: Past tense, a period, and no blank line before the body.

### clean-commit

- surface: commit
- pass: lint
- expect: clean

```input
Retry a failed upload once

Uploads on a slow network fail about 2% of the time.
```

- why: An imperative subject and a body that gives the reason. A clean case.
