# Review comment cases

### review-filler

- surface: review
- pass: lint
- expect: REVIEW001, SLOP003

```input
Great work! Have you considered maybe adding error handling here? Overall, LGTM.
```

- why: Praise, a question that hides a finding, and a sign-off. The prune pass also cuts the question.

### clean-review

- surface: review
- pass: lint
- expect: clean

```input
`decode` throws on an empty string, and `load` does not catch it. Return an empty array for an empty string.
```

- why: The problem, the effect, and the fix. A clean case.
