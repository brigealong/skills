# Readiness Gate

Decides whether the material is sufficient for the contract to hold. The core
trap: **a contract with all five sections filled in looks done but may be
semantically empty.** Intent stated but Scope doesn't cover it; every Must
checkable but the key success condition missing; decision cases present but
all trivial; three result states titled but no thresholds. All of
these pass a structure check and fail in reality. So the gate has two layers,
and both must pass.

## Layer 1 — Structural readiness (rule-checkable)

Pure boolean checks; no model judgment needed:

| Section | Condition |
|---|---|
| Intent | non-empty |
| Scope | both In and Out subsections exist |
| Acceptance | at least one Must |
| Examples | 1 Target Example + Good / Bad / Boundary decision cases (a missing Boundary case needs a stated reason) |
| Evaluation | PASS / CONDITIONAL PASS / FAIL all present |

A structural miss is a gap. A structural pass means nothing yet — continue.

## Layer 2 — Semantic readiness (judgment)

- **Intent↔Scope consistency** — Scope covers the stated purpose; no drift,
  no omission.
- **Acceptance covers Intent** — every key outcome has a Must; you didn't
  just write the easy-to-check ones.
- **Must → Evaluation mapping** — each Must maps to at least one check that
  names *who runs it, on what evidence, with what decision rule*. "Check it"
  is not a check.
- **Must is triggerable** — the planned execution must *necessarily produce*
  the evidence for each Must. A Must that only becomes checkable on a
  conditional branch ("only if the external loop fires") needs an explicit
  forcing step (fixture / drill / minimal trigger case); if you can't write
  one, demote it to Should or rewrite it. Otherwise early convergence leaves
  the Must dangling with no evidence and the audit cannot decide it.
- **Examples → Acceptance mapping** — each decision case maps to a key
  criterion, the three cases differ decisively enough to flip a verdict, and
  every sample carries a source and an authority label. `reference-only` and
  `candidate` samples must not serve as hard acceptance bases.
- **Executable three states** — the states are mutually exclusive and cover
  expected outcomes. CONDITIONAL PASS must define *what may remain open, who
  approves, and by when* — otherwise it's just a fuzzy escape hatch. Per-Must
  verdicts may be UNKNOWN ("cannot verify right now") — but every UNKNOWN you
  can foresee at drafting time means that Must's trigger path is underspecified:
  fix the trigger, don't accept the UNKNOWN.
- **Out of Scope carries information** — if plausible adjacent scope exists,
  it is explicitly excluded. "Nothing unrelated" is filler and doesn't pass.
  If genuinely nothing needs excluding, write that and say why.
- **No unresolved contradictions, ambiguities, or unauthorized assumptions.**

## Who judges what

- **Rules** check structure and reference integrity (layer 1, plus whether
  each Must has a paired check).
- **The model (or a human reviewer)** checks the semantic layer.
- **The user** authorizes purpose, preferences, risk acceptance, and the
  acceptance bar. No rule or model can substitute for this.

## The loop is not monotonic

The five sections depend on each other. Fixing Scope can invalidate an
Acceptance that previously passed; adding a bad sample can expose a flaw in
the Intent. A checkmark records current state, not permanent state.

```text
Each round:
  1. Run both layers.
  2. For each gap, route by root cause (below).
  3. After a fix, re-judge not just that gap but every section the answer
     touches, plus global consistency.
  4. Repeat until you reach an end state.
```

Budget the loop: at most ~6 rounds total, at most 2 rounds on the same gap.
When the budget runs out, stop negotiating and land on an end state.

## Routing gaps by root cause

| Root cause | Action |
|---|---|
| Fuzzy terminology, unclear domain model, hidden assumptions, internal contradictions in an input doc | Interrogate the document first (e.g. a grilling-style skill), then re-gate |
| Unknown user preference, goal, scope, or success bar | Narrow clarification inside this skill: one question at a time, multiple choice preferred, only blocking gaps |
| The design itself is undecided | Hand the task back to your design/brainstorming step — don't design inside the contract |
| Missing examples only | Search prior work, or generate candidates for the user to confirm |

## Three end states

- **READY** — both layers pass, nothing outstanding. Draft and proceed.
- **READY WITH ACCEPTED RISKS** — only *degradable* gaps remain (auxiliary
  samples, Should-level criteria, non-critical boundaries), each recorded in
  the contract and **explicitly accepted by the user**.
- **BLOCKED** — a *non-waivable* gap remains. Stop downstream routing and
  output the list of unresolved decisions.

Non-waivable means the contract cannot mean anything without it: Intent, core
Scope, a Must, or a Must→check mapping. Never re-label a non-waivable gap as
a "sample coverage risk" and proceed — an unknown goal is not a missing
example, it's an unknown goal.
