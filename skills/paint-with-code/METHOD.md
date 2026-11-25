# Paint with Code

Develop code like a painting: sketch the outline, build shapes, refine their relationships, and add the detail the picture needs.
The picture is the behavior the change must communicate to a human reviewer.

These are levels of attention, not fixed stages. Move between them as the design develops.
For a small change, several levels can fit in one pass.

## Sketch the outline

Read the task, relevant code, and project decisions. Identify the goal and the behavior that must change.
Present an overview of the goal and proposed design before further development.
Use a short narrative, rough code, or both, according to what best exposes the behavior.

Recommend specific details as provisional goals. Explain how they could help develop the picture.
Keep these suggestions distinct from actual requirements. Revise or discard them when a better design emerges.

Offer to record the result in Markdown, a specification, GitHub issues, or a similar destination.
Use the user's chosen destination when authorized. An offer alone does not authorize publication or messages to others.
Follow the task's interaction mode when deciding whether to wait for feedback or continue.

## Consider a series

An artist can develop a story across a series of paintings. A change can develop its behavioral narrative across a stack of PRs.
If one PR would carry too much explanation or detail, propose a stack with coherent parts.
Choose boundaries by what a reviewer needs to understand, rather than file counts or arbitrary size limits.

Include the proposed series in the outline. Explain the overall picture, each PR's purpose, and how the parts build on one another.
Keep these boundaries provisional as the design develops.

Give each PR a coherent review purpose. It can depend on earlier PRs without delivering a complete feature alone.
Make those dependencies clear so reviewers know what each part assumes and contributes.

Apply the method within each PR and across the stack. Each part should communicate its contribution and its relationship to the whole.
Revisit the division when one part becomes overloaded or the relationships become difficult to follow.
Use a single PR when it communicates the picture clearly.

## Develop the picture

Behavioral narrative is the entry point. After the initial brainstorm, consider all four themes throughout the work:

- **Behavioral narrative:** Give readers a coherent path through the behavior, its conditions, and its consequences.
- **Visible intent:** Make design choices communicate what the change means and why its behavior makes sense.
- **Reader perspective:** Consider what a reviewer needs to understand, beyond what execution alone requires.
- **Deliberate design:** Consider how choices affect understanding before implementing them. Revisit those choices as the work develops.

Build the main shapes: responsibilities, relationships, and the path through the behavior.
Refine how those shapes fit together. Develop details where they help readers understand the whole.
Use the project's language and conventions as context for these choices.

Choose the amount of expression the behavior needs. A simple, abstract design can communicate the picture immediately.
A complex design can need more expressive detail. More code does not inherently mean greater clarity.
Before adding structure, identify what a reviewer might otherwise misunderstand. Weigh that benefit against the cost of maintaining it.

For example, a refresh operation might skip current data, refresh the implementer, or require its replacement.
A boolean could serve the parent's immediate decision while hiding distinctions an implementer needs to understand.
An enum could make that behavior clearer. This illustrates a design judgment, not a rule to prefer enums or enumerate every outcome.

Reshape existing code within the task's scope when that helps communicate the change.
If a refactor outside that scope could help, explain the concrete benefit and ask before doing that work.

## Optionally read backward

The agent often builds from the outline toward details. A reviewer often starts with details and reconstructs the picture.
When useful, read a coherent part of the code from that perspective.
Ask: What behavior would a reviewer infer, and does it match the intended picture?

If the details suggest a different picture, reconsider the details, relationships, or outline.
Do not assume the outline must survive unchanged.

Choose when to do this unless the user specifies a cadence.
Let uncertainty and the size of a design change guide the choice. Avoid interrupting every small edit.
The user or agent can defer or omit reverse reading when it would disrupt useful exploration.
This option does not remove the task's required tests or checks.

## Present the result

Complete the implementation and the verification required by the task.
When a review summary or PR is part of the task, connect the goal to the main design choices.
Explain consequential trade-offs and relevant limits. Keep the explanation proportionate to the change.
The code must communicate the behavior without depending on the summary.
