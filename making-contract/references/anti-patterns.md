# Anti-Patterns

Failure modes seen in real use. Each one produces a contract that looks fine
and fails downstream.

- **The contract becomes a second design doc.** Intent describes an
  architecture, sections multiply, and the one page becomes ten. The contract
  states *what done means*; the design doc states *how*.

- **Intent written as a solution.** "Build a Playwright + Zotero CLI" is a
  solution. When the solution changes mid-implementation, a solution-shaped
  Intent gives the evaluator nothing to hold on to.

- **Must without Out of Scope.** The agent satisfies every Must and also
  "helpfully" migrates your config format. Scope creep is prevented by
  exclusions, not by criteria.

- **Abstract criteria with no samples.** "Output should be high quality" plus
  zero examples means the evaluator's taste replaces the user's. Examples are
  the anchor; without them the contract is a vibe.

- **A web reference promoted to an acceptance sample.** Something found
  online can inspire the standard, but only the user can set it. Silent
  promotion means the internet decided your acceptance bar.

- **Planning before confirmation.** The implementation plan quietly ships
  assumptions the user never saw. The contract exists precisely to surface
  them first.

- **The dispatch prompt replaces the contract.** An execution brief written
  for a worker agent serves the orchestrator; the contract serves the user.
  One cannot substitute for the other.

- **The executor fills in the user's purpose.** When the contract can't
  answer a directional question, the fix is escalation, never improvisation.

- **"All five sections filled" treated as ready.** Structural completeness is
  the cheapest thing to fake. Run the semantic layer of the
  [readiness gate](readiness-gate.md).

- **Every gap downgraded to an accepted risk.** A missing boundary sample is
  a risk; a missing Intent is a blocker. Re-labelling blockers as risks is
  how BLOCKED contracts sneak into execution.

- **Clarification balloons into a second brainstorm.** Inside this skill you
  ask narrow, blocking, one-at-a-time questions. Exploring alternatives and
  comparing architectures belongs upstream — hand the task back instead.

- **Examples collaged from local mistakes.** Collecting scattered local-error
  cases without first grasping what kind of thing the deliverable is as a
  whole — and without one complete artifact as the Target Example. The
  evaluator learns to nitpick, never to recognize a correct whole. Whole
  first, parts second.

- **A Must the planned execution never triggers.** If the evidence for a Must
  only appears on a conditional branch, early convergence leaves it dangling
  and undecidable. Write a forcing step, or demote it to Should.

- **Silent mid-run renegotiation.** Lowering the bar or adding waivers by
  editing the confirmed contract in place. The audit then judges against a
  version the user never confirmed. Every change goes through the Revision
  Log.

- **The contract is abandoned after handoff.** Execution finishes, but the
  final verdict is never written back and "promote this candidate once it
  survives the run" stays an unkept promise. Closing the loop is part of the
  contract's lifecycle: record the final verdict with evidence pointers, and
  promote or retire every candidate sample.
