---
name: making-contract
description: >-
  Use when a goal, design, or plan is about to move into implementation or be
  handed to another agent, and "done" is not yet verifiable. Turns intent into
  a minimal one-page contract — Intent, Scope, Acceptance, Examples,
  Evaluation — anchored by at least one good and one bad example. Runs after
  brainstorming/design, and gates before writing plans or orchestrating agents.
---

# Making Contract

An agent can build the wrong thing *correctly* — follow the plan, pass its own
checks, and still miss what the user actually wanted. A plan says **how to
build**. A contract pins down **what "done" means**, before any plan exists.

Before writing an implementation plan or dispatching work to another agent,
write a one-page contract with exactly these five sections. Keep it short,
hard, and checkable. Do not add more sections.

1. **Intent** — the user's purpose, never the solution. "Give the research
   workflow a traceable source-discovery entry point", not "build a
   Playwright CLI".
2. **Scope** — In Scope *and* Out of Scope. Out of Scope must exclude real
   adjacent work the agent might wander into; placeholder text doesn't count.
3. **Acceptance** — Must / Should criteria. Every Must is checkable by a
   command, a human, or an LLM judge. "Experience should be good" is not a
   criterion.
4. **Examples** — at least one good and one bad example. Examples are the
   anchor of the contract: they draw the decision boundary that abstract
   criteria can't.
5. **Evaluation** — how each Must gets checked, and three result states:
   PASS, CONDITIONAL PASS (what may remain open, who approves, by when), and
   FAIL.

Use the template in [references/contract-template.md](references/contract-template.md).

## Process

1. Gather what exists: the user's request, any design doc or brainstorm
   output, prior work the user has praised or rejected.
2. Fill every section you can reliably infer from that material. Do not ask
   about things the material already answers.
3. For gaps that block the contract, ask the user **one question at a time**,
   multiple choice when possible. This is narrow clarification, not a second
   brainstorm: if the *design itself* is undecided, stop and send the task
   back to your design step — don't design inside the contract.
4. If you lack examples, propose candidates and mark them "pending user
   confirmation". A reference found on the web can inspire; only an example
   the user confirms can serve as acceptance.
5. Run the readiness gate in
   [references/readiness-gate.md](references/readiness-gate.md). A contract
   with all five sections filled in is *structurally* complete but can still
   be semantically empty — the gate exists to catch exactly that.
6. End in one of three states — never a vague "looks good":
   - **READY** — proceed to planning or orchestration.
   - **READY WITH ACCEPTED RISKS** — only degradable gaps remain (a missing
     boundary example, a soft Should), each recorded in the contract and
     explicitly accepted by the user.
   - **BLOCKED** — a gap the contract can't stand without (unknown intent, an
     unverifiable Must). Say so and stop. Never silently downgrade a blocking
     gap into an "accepted risk".
7. Get the user's confirmation, save the contract as its own file (e.g.
   `docs/contracts/<topic>-contract.md`), then hand off: to your planning
   skill for implementation, or to your orchestration workflow for
   multi-agent execution. Downstream work must reference the contract and may
   not rewrite it. If the design later changes anything the user confirmed,
   the confirmation is void — re-gate and re-confirm.

## When to use it

The cost of a contract is one page; the cost of skipping it is an agent
optimizing for the wrong target. Use it when acceptance is subjective
(content, taste, research quality), when side effects are hard to reverse
(bulk writes, publishing, data migration), or when work will run unattended —
a clear contract is what makes it safe to hand execution to a cheaper model
or an autonomous agent.

Skip it for small, low-risk changes where the user already stated the one
observable outcome that settles the question.

Common failure modes are catalogued in
[references/anti-patterns.md](references/anti-patterns.md).
