# Log Messages

Keep each sentence to at most 20 words. Use consistent operational wording.
Preserve event names, field names, and machine-readable values.
Name the event or failed operation and its outcome.
Include safe context that helps an operator distinguish this occurrence from others.
Follow the repository's severity levels and structured logging conventions.

Do not label an expected retry as a fatal failure or report success before the operation completes.
State the observed cause when known. Keep speculation out of the event message.
Give an operator action only when you know it is useful and safe.

Log secrets or personal data only after the developer explicitly verifies the specific data and its logging purpose.
Do not dump requests, credentials, or raw payloads as diagnostic context.
Prefer approved redacted identifiers and correlation fields.
Avoid repeated messages that add no diagnostic information. Do not remove distinct failure evidence merely to shorten output.
