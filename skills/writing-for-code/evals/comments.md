# Comment cases

### comment-change-and-marketing

- surface: comment
- pass: lint
- expect: STE002, STE003, STE004

```input
Now uses the shared client; it's faster and more robust.
```

- why: A semicolon, a contraction, and a marketing word. The surface file also bans the word "now", which the `comments` command flags.

### comment-story-rewrite

- surface: comment
- pass: rewrite
- expect: keeps the symptom and the cause, loses the story and the past tense

```input
// After a long debug session we found the observer fired twice because it
// was registered on a background thread, so we moved it to main.
```

- why: The surface file asks for a debugging hint in the present tense.

### clean-comment-guard

- surface: comment
- pass: lint
- expect: clean

```input
Constant-time compare. Do not replace with `==`.
```

- why: A guard. A clean case.
