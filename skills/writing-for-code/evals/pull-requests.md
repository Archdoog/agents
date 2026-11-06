# Pull request cases

### pr-self-reference-and-chat

- surface: pr
- pass: lint
- expect: SLOP001, SLOP009

```input
This PR adds retries. I hope this helps!
```

- why: Opens on itself and ends with chat text.

### clean-pr

- surface: pr
- pass: lint
- expect: clean

```input
Retries a failed upload once, after 500 ms.

Uploads on a slow network fail about 2% of the time with a timeout.

Verified: `npm test` passes, with a new test for the retry path.
```

- why: What changed, why, and how the author verified it. A clean case.
