# Inline Comments

Use flavored mode. Explain what a maintainer cannot readily infer from the nearby code.
Keep constraints, surprising behavior, safety risks, workarounds, and useful debugging clues.
State a symptom and its cause, not the story of the investigation.

A reference to other code is useful only if it explains a dependency or constraint.
"Matches the other client" is not a reason. State the shared requirement if it matters.
Do not ban platform names or issue links when they identify a real compatibility requirement or an active workaround.
Follow repository conventions for TODOs and tracker links.

Remove comments that restate assignments, announce obvious steps, or describe the editing session.
Prefer one or two lines, but retain a longer explanation when a shorter version would hide an important constraint.
Keep necessary rationale beside the code it protects. A link can add detail but must not replace the local warning.

For a workaround, name the affected condition and its removal condition when known.
Fetch new external references before citing them. Prefer versioned documentation or commit permalinks.

Preserve tool directives, suppression comments, copyright headers, and license notices.
Review only comments within the requested scope. A checker flag is not proof that a comment should disappear.
