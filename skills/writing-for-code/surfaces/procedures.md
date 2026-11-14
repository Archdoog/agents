# Procedures and Runbooks

Use strict mode. State the goal, prerequisites, required access, and starting state before the steps.
Name supported versions or environments when they affect the commands.

Use numbered steps in execution order, with one action per step.
Put a condition before its command. Keep warnings directly before the action they protect.
Explain destructive effects and backup requirements before execution, not after it.
Preserve command syntax and quote paths where needed.

Give an observable expected result at each important checkpoint.
For a likely failure, explain how to identify it and what recovery action is safe.
State when the operator must stop rather than retry.

If rollback is unavailable, say so. Do not invent a recovery command or promise that retry is safe.
End with a check of the final state. Report which environment and steps you actually tested.
