---
name: task-orchestration
description: >-
  Use when a complex, risky, or multi-batch task should be executed by another
  agent (often a cheaper model) without the user babysitting every step. The
  orchestrating model writes a constraint document good enough to run
  unattended; an executor runs it batch by batch; an independent reviewer
  verifies with commands, not by reading reports. Includes dispatch tiering,
  three artifact templates, and a three-state acceptance verdict.
---

# Task Orchestration

**The smart model writes the constraints; the cheap model runs the whole
batch.** The quality of the constraint document — not the size of the
executing model — decides the quality of the execution.

The goal of every constraint document: the executor can finish the entire
task **without stopping to ask the user**. That means you, the orchestrator,
must write down:

| What to pin down | What happens if you don't |
|---|---|
| Goal and acceptance criteria | The executor doesn't know what "correct" looks like |
| Concrete items per batch | The executor guesses the scope — misses or overshoots |
| Hard constraints (red lines) | Discovered only after they're crossed |
| Runnable command templates | The executor invents commands — wrong platform, wrong flags |
| Escalation triggers + what to do | Ambiguity gets resolved by improvisation |
| Stage columns and pass criteria | Nobody knows when an item is "done" |
| Sampling verification method | Self-reports say PASS without a command ever running |

Anti-pattern: the orchestrator writes a rough sketch → the executor guesses →
the user gets pulled back in every batch → the automation was pointless.

## Dispatch tiers: pick the weight class first

Spec effort should be proportional to **complexity × blast radius × how cheap
(and literal-minded) the executing model is**. This skill is the heavy tier —
not a mandatory gate for every dispatch.

| Tier | When | Payload |
|---|---|---|
| **0 — direct** | Light, low-risk, self-evident | A one-line prompt |
| **1 — handoff** | Crosses agents/runtimes but the work is simple | A handoff envelope with a *minimal embedded contract*: goal, in/out scope, hard constraints, acceptance, stop/escalate conditions, completion signal |
| **2 — full orchestration** | Complex, batchable, risky, needs an execute+review loop | The three artifacts of this skill |

Default light; escalate to Tier 2 when side effects are irreversible or the
blast radius is wide. But under-speccing a cheap executor usually burns more
tokens in rework than the spec would have cost.

**Contract admission for Tier 2**: a user-facing contract (see the
`making-contract` skill) must exist before orchestration. Consume its end
state: `READY` → proceed; `READY WITH ACCEPTED RISKS` → proceed, but copy the
risk register (approver, owner, deadline) into the execution brief — never
silently drop it; `BLOCKED` → do not build templates or dispatch anything.

## The three artifacts

Create a task directory and instantiate the three templates from
`references/`:

```text
<task-dir>/
├── execution-brief.md    ← Template A: how to do it (references/template-execution.md)
├── progress-table.md     ← Template B: how far along it is (references/template-progress.md)
├── acceptance-spec.md    ← Template C: how to judge it (references/template-acceptance.md)
├── reports/              ← self-check reports
└── logs/                 ← execution logs (if applicable)
```

The command templates inside the brief must be directly runnable. "Choose an
appropriate command" is not a template.

## The execution loop

```text
Executor works batch by batch
  → each item: complete every stage column
  → each batch: self-check → write report → request review
Reviewer verifies by running commands (not by reading the report)
  → verdict: PASS / CONDITIONAL PASS / FAIL
  → on CONDITIONAL PASS or FAIL: issue a remediation list
Executor remediates → reviewer re-checks
Last batch passes → whole-task final acceptance → sign-off
```

Verdict semantics (aligned with the upstream contract — do not drift):

- **PASS** — every Must in the contract holds.
- **CONDITIONAL PASS** — leftovers fall *within* what the contract explicitly
  allows to remain open, and the approver, owner, and deadline are recorded.
  It is an approvable exception, **not** "needs rework".
- **FAIL** — non-compliant. Fixable leftovers *outside* the allowed range go
  here (with a remediation list) — do not stretch CONDITIONAL PASS to cover
  them.

Not every finding means rework:

| Finding | Test | Action |
|---|---|---|
| Wrong result | Target state incorrect | Rework |
| Right result, process deviated | Target correct, path off | Record the lesson, don't rework |
| Docs inconsistent | Report/index ≠ reality | Fix the docs, not the output |
| Governance artifact missing | README/index not built | Just build it |

## Guardrails

- **High-risk gate** (the only user touchpoints): actual deletion of data,
  changes outside the task's scope, skipping ahead across batches, expanding
  the original scope.
- **Deletion safety**: all deletions go to the system trash/recycle bin —
  never permanent. If trash support can't be confirmed, stop and ask.
- **Safe defaults**: never overwrite existing outputs; conflicts go to a
  queue, not auto-resolved; held items stay held; anything critical belongs
  in hard constraints — soft constraints get skipped.
- **Spawn boundary**: don't auto-spawn sub-agents unless the user asked for
  multi-agent execution; otherwise play executor and reviewer sequentially
  yourself. Spawned agents inherit all guardrails.
- **Completion signaling is a first-class decision.** Before dispatching,
  decide how you'll know the work is done: prefer your runtime's structured
  completion event or a background wait that wakes you — never a foreground
  polling loop. If your environment provides specific dispatch backends
  (sub-agents, terminal panes, a kanban, CI jobs), their routing details
  belong in a `references/` backend file, not in this core.

## References

- [references/templates.md](references/templates.md) — template index and workflow
- [references/template-execution.md](references/template-execution.md) — Template A: execution brief
- [references/template-progress.md](references/template-progress.md) — Template B: progress table
- [references/template-acceptance.md](references/template-acceptance.md) — Template C: acceptance spec
- [references/check-commands.md](references/check-commands.md) — verification command patterns (bash + PowerShell)
- [references/anti-patterns.md](references/anti-patterns.md) — nine failure modes from real multi-agent runs; read before starting
