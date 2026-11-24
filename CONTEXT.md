# Agent skill design

This context records the agreed meaning and design principles of skills in this repository.

## Language

**Paint with Code**:
A proposed skill that helps agents express behavior through code so human reviewers can understand and assess a change.

## Design intent

The skill should help agents make design decisions before implementation so human reviewers can understand the resulting behavior through the code.

The refresh example provides initial insight. It does not establish a general rule about enums, return types, or behavior contracts.

## Expressive detail

A simple or abstract design can communicate the picture immediately. A complex design can need more expressive detail to communicate its behavior.

Added code or structure must provide a concrete benefit to understanding. The agent should identify what a reviewer might otherwise misunderstand and choose a proportionate design.

The skill does not equate more detail with greater clarity. The behavior determines how much detail the picture needs.

## Scope

The skill can reshape existing code within the task's scope when that helps explain the change.

The agent can propose a refactor outside the task's scope when it could provide a concrete benefit. It explains the benefit and asks before doing that work.

## Invocation

The preferred version applies to every coding task. The amount of work should remain proportionate to the task.

A second version requires human invocation. Both versions use the same method and differ only in how they start.

Both versions scale the outline, refinement, and optional reverse reading to the task. The implementation should maintain one shared method.

## Review presentation

When a review summary or PR is part of the task, the skill also guides that presentation.

The summary connects the goal to the main design choices. The code must communicate the behavior without depending on that explanation.

## Iterative workflow

A behavioral narrative can span a stack of PRs, like a story across a series of paintings.
The agent should propose a stack when one PR would contain too much detail for a reviewer to understand clearly.
The outline describes the overall picture and the contribution of each part. The proposed PR boundaries remain provisional.
Each PR needs a coherent review purpose. It can depend on earlier PRs without delivering a complete feature alone.

The skill uses a loop, like an artist who develops a painting from rough outlines through shapes, refinement, and detail.

The initial outline gives an overview of the goal and design. It can use a short narrative, rough code, or both.

The outline recommends specific details as provisional goals that help the agent develop the design. These suggestions are not fixed requirements.

The agent presents the outline to the user before further development. The task's interaction mode determines whether the agent waits for feedback or continues.

The agent also offers to record the result in Markdown, a specification, GitHub issues, or a similar destination. The user chooses whether and where to save it.

The agent develops the behavioral narrative at increasing levels of detail. A reviewer often follows the opposite path, from details toward the overall picture.

Each detail must help the reviewer reconstruct that picture. The workflow must allow the agent to revisit earlier design choices as the implementation develops.

Reverse reading checks what behavior a reviewer would infer from the code against the intended picture.

Reverse reading is optional. The user or agent can defer or omit it so repeated checks do not interrupt useful exploration.

The loop describes how the work develops. It does not require a verification step after every small change.

The agent chooses the cadence of reverse reading unless the user specifies one. Uncertainty and the size of a design change guide that choice.

## Agreed themes

**Behavioral narrative** is the entry point. After the initial brainstorm, the agent must consider all four themes.

- **Behavioral narrative:** The code gives readers a coherent path through the behavior and its consequences.
- **Visible intent:** Code helps readers understand what the change means and why its behavior makes sense.
- **Reader perspective:** Design accounts for what a reviewer needs to understand, beyond what execution requires.
- **Deliberate design:** Agents consider how design choices affect understanding before they write the implementation.

## Example dialogue

> **Developer:** What does the refresh example teach the skill?
> **Reviewer:** Consider what the code communicates to a human. The enum illustrates that concern without prescribing a solution for other changes.
