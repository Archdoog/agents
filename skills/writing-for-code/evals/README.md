# Evals

Cases that show what the skill must do, and what it must not do. Run them
by hand after a change to `CORE.md`, `PRUNE.md`, or a file in `surfaces/`.
`scripts/tests/test_evals.py` checks the shape of each case, and it runs
each `lint` case through the tool.

Each surface has at least one clean case. A clean case must stay clean. If
a change to the skill makes the agent cut or flag a clean case, the change
is a regression.

## The shape of a case

````markdown
### a-short-id

- surface: readme
- pass: prune
- expect: score 0, delete the section

```input
The text of the case.
```

- why: The reason for the expected result.
````

| Key | Values |
|---|---|
| `surface` | A `--surface` value: `comment`, `docstring`, `readme`, `doc`, `procedure`, `error`, `changelog`, `commit`, `pr`, `issue`, `review` |
| `pass` | `prune`: run the fresh-eyes pass. `rewrite`: rewrite with the skill. `lint`: run the tool. |
| `expect` | For `prune`: the score and the action for each block that changes. For `rewrite`: what the result must keep and lose. For `lint`: the codes, comma-separated, or `clean`. |
| `why` | One or two sentences. |

## How to run a case by hand

1. Start a new agent with the skill loaded.
2. For `prune`, give it the brief in `PRUNE.md` and the input. For
   `rewrite`, ask it to rewrite the input for the surface.
3. Compare the result to `expect`. A cut that `expect` does not list is a
   failure in a clean case.
