# Error message cases

### error-vague-apology

- surface: error
- pass: lint
- expect: ERR001, STE003

```input
Oops! Something went wrong and we couldn't save your file.
```

- why: The message does not name the file, the cause, or the next action.

### error-rewrite

- surface: error
- pass: rewrite
- expect: names routes.json, the cause, and the next action, with no apology

```input
Oops! Something went wrong and we couldn't save your file.
```

- why: Use the three questions in surfaces/errors.md. Context for the rewrite: the file is routes.json and the disk is full.

### clean-error

- surface: error
- pass: lint
- expect: clean

```input
Cannot save routes.json: the disk is full. Free 20 MB and try again.
```

- why: What failed, why, and the next action. A clean case.
