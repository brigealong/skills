# Contract Template

A contract file contains exactly these five sections. Do not let it grow into
a second design doc — keep it to roughly one page.

```markdown
# Contract: <Task Name>

## 1. Intent

What real user purpose does this task serve? (Purpose, not solution.)

## 2. Scope

### In Scope
- ...

### Out of Scope
- ...  <!-- real adjacent work being excluded, not filler -->

## 3. Acceptance

### Must
- ...  <!-- each one checkable by a command, a human, or an LLM judge -->

### Should
- ...

### Pass Line
- ...  <!-- the minimum bar that separates PASS from FAIL -->

## 4. Examples

### Target Example
- Artifact:            <!-- one complete, admirable artifact (or link) of the same kind as the deliverable -->
- Source:
- Why exemplary:
- Authority: reference-only | user-confirmed acceptance anchor

### Decision Cases

#### Good Case
- Maps to:             <!-- which key Acceptance criterion -->
- Source:
- Authority: candidate | user-confirmed acceptance anchor
- Sample:
- Expected result: PASS
- Why:

#### Bad Case
- Maps to:
- Source:
- Authority: candidate | user-confirmed acceptance anchor
- Sample:
- Expected result: FAIL
- Why:

#### Boundary Case
- Maps to:
- Source:
- Authority: candidate | user-confirmed acceptance anchor
- Sample:
- Tempting wrong judgment:
- Correct result: PASS | CONDITIONAL PASS | FAIL
- Decisive distinction:

## 5. Evaluation

### Deterministic Checks
- ...  <!-- who runs it, on what evidence, with what decision rule -->

### Judgment Checks
- ...  <!-- for subjective criteria: how the judge scores, on what rubric -->

### Result States
- PASS:
- CONDITIONAL PASS:  <!-- what may remain open, who approves, by when -->
- FAIL:
- Verdict record: per-Must machine-readable entries {id, status: PASS|FAIL|UNKNOWN, reason, evidence}.
  UNKNOWN means "cannot be verified right now" (usually an unexercised trigger path) — state it honestly, never guess.
```

## Where examples come from

**Whole first, parts second — the order is not reversible.**

*Phase 1 — grasp the whole.* First answer: "what kind of thing, as a whole, is
this deliverable?" (an article? a CLI? a report? a skill?). Get the type wrong
and every sample you collect will be misaligned. Then find **one complete
artifact of that same kind** as the Target Example — it establishes the
quality ceiling and what a *right whole* looks like.

*Phase 2 — calibrate the parts.* Decision Cases supplement the Target Example;
they are not the main body. Build them only where a key Acceptance criterion
carries a real judgment risk: find the criterion most dependent on subjective
judgment, write down the evaluator's most tempting wrong call, then look for
evidence that separates the right call from the wrong one.

Never skip Phase 1 and collect local mistakes as your examples. A contract
with only local-error cases and no whole-artifact anchor teaches the
evaluator to nitpick, not to recognize a correct whole.

Search for evidence in this priority order:

1. Examples the user explicitly provided.
2. Past work the user praised or rejected.
3. Samples inside the current design doc, spec, or test suite.
4. Public references from the web.
5. Candidates you generate, marked "pending user confirmation".

Every Target Example and Decision Case carries an authority label:

- **reference-only** — may come from anywhere; inspiration only, never a hard
  acceptance basis.
- **candidate** — generated or not yet user-confirmed; clarification only.
- **user-confirmed acceptance anchor** — confirmed by the user (or from work
  the user explicitly approved); may decide pass/fail.

If sample coverage is thin, say so inside the Examples section instead of
pretending the standard is settled:

```markdown
### Sample Coverage

| Dimension | Sample? | Source | Risk |
|---|---|---|---|
| Target Example | yes | public reference | medium: inspiration only |
| Good case | yes | user-provided | low |
| Bad case | no | — | medium: evaluator may be too lenient |
| Boundary case | no | — | high: agent may draw its own boundary |
```

`Sample Coverage` lives inside section 4 — it is not a sixth section.

## Revision log

Once a contract is confirmed, never edit Acceptance / Scope / Pass Line in
place — including mid-run bar-lowering and added waivers. Append a row instead
(the evaluator judges against the latest version; history stays traceable):

```markdown
### Revision Log

| Date | Clause (old → new) | Reason | Approved by |
|---|---|---|---|
```

Like Sample Coverage, the Revision Log is an appendix, not a sixth section.

## Where the contract file lives

Keep it separate from the design doc and the implementation plan, so
evaluators and workers can reference it directly:

```text
docs/contracts/<topic>-contract-YYYY-MM-DD.md   # if the repo has docs/
<task-dir>/contract.md                          # otherwise
```
