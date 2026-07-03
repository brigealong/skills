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
