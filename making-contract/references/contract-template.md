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

### Good Sample
Given ... When ... Then ...
<!-- or: input / output / why it passes -->

### Bad Sample
Given ... When ... Then ...
<!-- or: input / output / why it fails -->

## 5. Evaluation

### Deterministic Checks
- ...  <!-- who runs it, on what evidence, with what decision rule -->

### Judgment Checks
- ...  <!-- for subjective criteria: how the judge scores, on what rubric -->

### Result States
- PASS:
- CONDITIONAL PASS:  <!-- what may remain open, who approves, by when -->
- FAIL:
```

## Where examples come from

Search in this priority order:

1. Examples the user explicitly provided.
2. Past work the user praised or rejected.
3. Samples inside the current design doc, spec, or test suite.
4. Public references from the web.
5. Candidates you generate, marked "pending user confirmation".

Keep two kinds of samples distinct:

- **Reference sample** — may come from anywhere; used for inspiration.
- **Acceptance sample** — must be confirmed by the user (or come from work
  the user explicitly approved) before it can decide pass/fail.

If sample coverage is thin, say so inside the Examples section instead of
pretending the standard is settled:

```markdown
### Sample Coverage

| Dimension | Sample? | Source | Risk |
|---|---|---|---|
| Good sample | yes | user-provided | low |
| Bad sample | no | — | medium: evaluator may be too lenient |
| Boundary sample | no | — | high: agent may draw its own boundary |
```

`Sample Coverage` lives inside section 4 — it is not a sixth section.

## Where the contract file lives

Keep it separate from the design doc and the implementation plan, so
evaluators and workers can reference it directly:

```text
docs/contracts/<topic>-contract-YYYY-MM-DD.md   # if the repo has docs/
<task-dir>/contract.md                          # otherwise
```
