# Template B: progress-table.md

> Copy this file into the task directory as `progress-table.md`, fill in the
> checklist items and batch split. Every `<...>` placeholder must be replaced.

---

# <task-name> Progress Table

> Aligned with `<manifest>`. Update the status columns after every item;
> write a self-check report and request review after every batch.
> Constraints live in `execution-brief.md` and `acceptance-spec.md`.

---

## Status characters

- `[ ]` not started
- `[~]` in progress
- `[x]` done
- `[!]` blocked / escalated
- `[-]` skipped / not applicable

---

## Stage column design

> Defined by the orchestrator per task type. Generic frame plus common
> examples below.

### Generic frame

Each item's stage columns cover this chain:

```text
precheck → core execution → [task-specific stages…] → self-check → approval
```

- **Precheck** and **self-check/approval** are fixed anchors for every task.
- Middle columns depend on the task; 2–4 columns work best.

### Reference columns by task type

**File operations** (migration, reorganization, cleanup):

| precheck | execute | count | naming | self-check | approval |

- count: target file count = source file count
- naming: naming convention applied

**Code refactoring** (API migration, dependency upgrades):

| precheck | refactor | tests | lint | self-check | approval |

**Content work** (doc restructuring, content review):

| precheck | execute | fidelity | format | self-check | approval |

- fidelity: meaning unchanged

**Data processing** (cleaning, format conversion):

| precheck | execute | count | schema | self-check | approval |

**Research synthesis** (literature review, knowledge base):

| precheck | execute | sources | coverage | self-check | approval |

- sources: every claim cited

**Custom tasks**: define 2–4 middle columns; each needs a meaning and a pass
condition.

---

## Batch 1

**Batch goal**: <what this batch delivers>
**Self-check report**: `reports/<date>_batch01_self-check.md`

### <category A>

| # | Item | precheck | <stage-2> | <stage-3> | self-check | approval | Notes |
|---|------|----------|-----------|-----------|------------|----------|-------|
| <1.1.1> | <summary> | [ ] | [ ] | [ ] | [ ] | [ ] | <notes> |
| <1.1.2> | <summary> | [ ] | [ ] | [ ] | [ ] | [ ] | <notes> |

### Batch 1 wrap-up
- [ ] All stage columns checked for every item
- [ ] Self-check report written to `reports/<date>_batch01_self-check.md`
- [ ] Review requested
- [ ] **Review verdict: <PASS / CONDITIONAL PASS / FAIL>**

### Batch 1 remediation list (if any)
- [ ] **R<#>**: <remediation item>

---

## Batch 2

<!-- repeat the Batch 1 format -->

---

## Batch N (final)

<!-- repeat the Batch 1 format -->

### Final verdict
- [ ] **Remediation passed**
- [ ] **All approval columns checked**
- [ ] **Whole-task final acceptance run and passed**

---

## Held items (outside this task's execution scope)

| # | Item | Reason |
|---|------|--------|
| <id> | <summary> | <why held, who picks it up> |

---

## Conflict queue

Conflicts/ambiguities found during execution land here for the reviewer to
adjudicate.

| # | Item | Conflict | Evidence/context | Proposed resolution | Reviewer ruling |
|---|------|----------|------------------|--------------------|-----------------|
| C1 | <item> | <description> | <evidence> | <proposal> | <ruling> |

---

## Clarification queue

Questions found during execution land here for the reviewer to answer.

| # | Raised | Item | Question | Proposal | Answer |
|---|--------|------|----------|----------|--------|
| Q1 | <date> | <id> | <question> | <proposal> | <answer> |

---

## Revision log

- <date> v1: initial

---

### Filling guide

| Field | Required | Notes |
|---|---|---|
| Batch count | yes | 2–5 batches by item count and priority |
| Items per batch | yes | Extracted from the manifest, grouped by batch |
| Stage columns | yes | Defined per task type (see "Stage column design") |
| Held items | as needed | Out of scope but must not be forgotten |
| Both queues | keep | Conflict + clarification, even if initially empty |
| Remediation list | as needed | Filled after CONDITIONAL PASS / FAIL |
