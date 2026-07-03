# Template C: acceptance-spec.md

> Copy this file into the task directory as `acceptance-spec.md` and adjust
> the checks to the task. Every `<...>` placeholder must be replaced.

---

# Acceptance Spec

> Two gates:
> 1. **Executor self-check** (every batch) — §1
> 2. **Final review** (by the reviewer) — §2

---

## 1. Executor self-check (every batch)

### 1.1 Trigger

All items in a batch processed, with precheck-through-execution columns
checked off. **Don't write the report before the columns are done.**

### 1.2 The six checks

Each check gets `PASS / FAIL / N/A` plus concrete evidence:

1. **Completeness** — every item in the batch processed; output count matches
   expectation. <task-specific verification>
2. **Constraint compliance** — walk the hard constraints in
   `execution-brief.md` §4 one by one, each with command-output evidence.
3. **Quality standards** — output meets quality/format specs. <file ops →
   sample naming compliance; refactoring → tests+lint green; content →
   structure consistent>
4. **Side effects** — nothing outside scope was touched. <task-specific check>
5. **Documentation sync** — README / indexes / changelogs reflect reality
   (N/A if no doc outputs).
6. **Logs & queues** — logs clean; conflicts/questions logged in the progress
   table; table status accurate.

### 1.3 Blocking rule

Any FAIL → **no PASS report**. Fixable → fix and re-check. Not fixable →
clarification queue.

### 1.4 Self-check report template

Path: `reports/<YYYYMMDD>_batch<NN>_self-check.md`

```markdown
---
created: <YYYY-MM-DD>
type: self-review-report
batch: <NN>
status: pass | fail | partial
executing-agent: <agent id>
---

# Batch <NN> Self-Check Report

## Verdict
- Status: PASS / FAIL / PARTIAL
- Items covered: <list>
- Blocked items: <list or "none">

## Six checks
### 1 Completeness
- <verification and result>
### 2 Constraint compliance
- [x] <constraint> (evidence: <command output>)
### 3 Quality standards
- <sampling/verification result>
### 4 Side effects
- <result>
### 5 Documentation sync
- <status>
### 6 Logs & queues
- Logs: <path or "none">; conflicts: <n>; questions: <n>

## Sample verification
Random sample of <N> items:
| # | Item | Expected | Actual | Match | Quality |
|---|------|----------|--------|-------|---------|
| 1 | ... | ... | ... | ✓/✗ | ✓/✗ |

## Known leftovers
- <if any>

## Requesting final review
Requesting reviewer sampling per acceptance-spec §2.
```

---

## 2. Final review (by the reviewer)

### 2.1 Trigger
- Executor submitted a PASS self-check report for the batch
- The batch's self-check column is checked

### 2.2 Review checklist

1. **Report credibility** — the six checks carry re-runnable evidence; key
   verification commands re-run in the reviewer's environment match the
   report.
2. **Random sampling** (≥ 10% per batch) — sampled outputs exist, are
   accessible, and meet the quality bar.
3. **Command-driven constraint re-check** — the reviewer independently runs
   verification commands (see `references/check-commands.md`).
   **Never just read the numbers in the report — run the commands.**

   ```
   <verification commands filled in by the orchestrator>
   <typical: count checks, integrity checks, constraint-leak scans>
   ```

4. **Consistency** — naming/format/path conventions uniform; docs match
   reality.
5. **Edge matters** — conflict queue has rulings; clarification queue has
   answers; held items still held.

### 2.3 Verdict

The reviewer appends to the batch's self-check report:

```markdown
---

## Final Review Verdict (reviewer)

- Reviewer: <id>
- Date: <YYYY-MM-DD>
- Verdict: **PASS / CONDITIONAL PASS / FAIL**

> Semantics aligned with the upstream contract's Evaluation:
> - **PASS**: every contract Must holds.
> - **CONDITIONAL PASS**: only when leftovers fall within what the contract
>   explicitly allows to remain open, and the approval block below is filled.
>   An approvable exception — **not** "needs rework".
> - **FAIL**: non-compliant. Fixable leftovers outside the allowed range go
>   here with a remediation list — do not stretch CONDITIONAL PASS.

### Sampling
- Sample size: <N>
- Non-conforming: <list>

### Approval block (required for CONDITIONAL PASS)
- Allowed leftovers: <explicit list>
- Approver: <id>
- Remediation owner: <id>
- Deadline: <YYYY-MM-DD>

### Remediation required (CONDITIONAL PASS or FAIL)
- <items>

### Next actions
- [ ] Approval column checked for the batch
- [ ] Next batch unlocked
```

### 2.4 After PASS

The reviewer updates the progress table: approval columns checked, batch
wrap-up checked, next batch unlocked.

---

## 3. Whole-task final acceptance

After the last batch passes, the final reviewer additionally runs:

1. **Global consistency sweep** — supporting docs don't contradict each
   other; indexes/summaries are complete.
2. **Regression check** — existing systems/data undamaged; earlier batches'
   outputs not overwritten.
3. **Sign-off** — progress table status → `completed`; rules and manifest
   docs → `accepted`.

---

### Filling guide

| Field | Required | Notes |
|---|---|---|
| Six self-checks | keep all | Completeness/constraints/quality/side-effects/docs/logs cover the core risks |
| Report template | yes | Keeps executor reports structurally comparable |
| Five review items | keep all | Credibility/sampling/commands/consistency/edges |
| Verification commands | as needed | Per platform and task type (check-commands.md) |
| Final acceptance | after last batch | Consistency sweep + regression + sign-off |
| Three-state verdict | keep | More precise than binary pass/fail |
