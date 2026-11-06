# Error messages, log lines, and CLI help

Text that a program shows to a person. Mode: strict, with `--surface
error`.

The reader is often under pressure, and often reads only this one line.

## Error messages

An error message answers three questions:

1. **What failed?** Name the thing: the file, the key, the host, the value.
2. **Why?** The cause, if the program knows it.
3. **What can the reader do?** The next action, if there is one.

| Bad | Good |
|---|---|
| `Invalid input` | `Cannot read config.toml: line 12: expected a number for "port", got "80a".` |
| `Something went wrong. Please try again.` | `Upload failed: the server returned 503. Try again in a minute.` |
| `Error: ENOENT` | `Cannot open ./data/routes.json: the file does not exist. Run "make data" first.` |

Rules:

- Include the value that failed, unless it is a secret. Never print a
  token, a password, or personal data.
- Do not blame the reader: "You entered an invalid date" becomes
  "The date must use the form YYYY-MM-DD."
- Do not apologize, and do not write "Oops" or "Uh oh".
- Use the same name for a thing as the docs and the flags use.
- Keep the casing and punctuation of the codebase. Some languages have a
  convention. In Go, an error string starts with a lowercase letter and has
  no final period.

## Log lines

- Write a log line for the person who reads the log during an incident.
- Put the event first, then the context as key-value pairs:
  `route decode failed id=r_123 bytes=0`.
- Use one level for one meaning. An `error` needs action. A `warn` can
  need action later. An `info` needs no action.
- Do not log the same event at two levels.

## CLI help

- The first line of `--help` says what the command does, in one sentence.
- Give each flag one line that says what it does, and its default.
- Show one or two examples of real use.
- Say what the exit codes mean, if there is more than one error code.

## Self-check

1. Does each error message name what failed, and the next action?
2. Does any message print a secret?
3. Does each log line start with the event?
4. Does the help text give each flag its default?
