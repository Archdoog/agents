# Error Messages

Use strict mode. Identify the failed operation and the affected item when safe.
If you know the cause or recovery, give a useful next action.
If the cause is unknown, state the observed failure rather than guessing.

Use the application's names for controls, files, and operations.
Avoid blame, jokes, generic apologies, and advice to "try again" without a reason.
Distinguish invalid input, unavailable resources, and internal failures when the evidence supports that distinction.
Do not promise that no data changed unless the implementation guarantees it.

Never expose secrets or personal data. Avoid raw input, tokens, connection strings, and sensitive paths.
Use safe identifiers or redacted context when needed for support.
Keep machine-readable error codes stable. Do not change a quoted diagnostic during a prose rewrite.
