# Template A: execution-brief.md

> Copy this file into the task directory as `execution-brief.md`, fill in the
> blanks, and hand it to the executing agent. Every `<...>` placeholder must
> be replaced with real content.

---

## 0. Upstream contract & admission

> Required for Tier 2. Tier 0/1 embed a minimal contract instead of a file.

- `contract_ref`: `<path to the contract produced by making-contract; for Tier 0/1 write "embedded — see Scope/Acceptance below">`
- `contract_status`: `<READY / READY_WITH_ACCEPTED_RISKS / BLOCKED>` (**BLOCKED must not be dispatched**)
- `design_spec_ref`: `<path to the verified design/spec; "none" if absent>`
- If `READY_WITH_ACCEPTED_RISKS`: copy the risk register (approver / owner /
  deadline) into "6. Accepted risks" below (add the section if missing).

---

## 1. Process overview

```text
[this file + <rules-file> + <manifest> + progress-table.md]
        │
        ▼
Executor works through progress-table batches
        │
        ▼
Executor self-checks (acceptance-spec §1) → writes self-check report
        │
        ▼
Final reviewer (user / review agent) samples per acceptance-spec §2
        │
        ▼
Pass → next batch; fail → back to execution
```

The executor's responsibility ends at the self-check report. **Never**
self-declare "all done".

---

## 2. Domains of authority (not one linear ranking)

Different questions have different authoritative sources. **No single
ordering covers everything:**

| Domain | Who decides | Source |
|---|---|---|
| Goals: Intent / Scope / Acceptance | The user-confirmed contract | `<contract_ref>` |
| Facts: technical facts / design conclusions | The verified design/spec | `<design_spec_ref>` |
| State: current batch runtime state | The progress table | `progress-table.md` |
| Process: workflow and hard constraints | This file + rules | this file, `<rules-file>` |
| Items: concrete items and paths | The manifest | `<manifest>` |

**Cross-domain conflicts require stopping and escalating — never silently
pick a side.** In particular: the contract cannot override technical facts,
and technical facts cannot rewrite user-confirmed goals. Stop and escalate to
the orchestrator/user.

The executor must **not** modify upstream artifacts in the goal / fact /
item domains. Found a problem? Log it in the progress table's clarification
queue and wait for the reviewer.

---

## 3. Scope

### In scope
- <actions the executor is allowed to take>
- <maintaining required outputs/indexes>
- <post-execution self-check and reporting>

### Out of scope
- <explicitly excluded work>
- <responsibilities belonging to other tasks>

---

## 4. Hard constraints (violation = execution failure)

> **Universal hard constraints** (keep for every task):

1. **Batch order**: follow the progress table's batch order; no skipping ahead.
2. **Self-check every batch**: finish a batch → self-check passes → write the
   report → then request the next batch.
3. **Never unilaterally edit sources of truth**: problems in supporting files
   go to the clarification queue, not fixed in place.
4. **Stop on escalation triggers**: any condition in §7 halts execution.

> **Task-specific hard constraints** (filled in by the orchestrator):

5. **<constraint 1>**: <description>
6. **<constraint 2>**: <description>

> **Reference constraints by task type** (pick what applies):
>
> | Task type | Recommended hard constraints |
> |---|---|
> | File operations | Don't damage sources; don't overwrite targets; conflicts queue, not self-resolved |
> | Code refactoring | Tests green after change; no behavior change (unless required); no files outside scope |
> | Content work | Don't alter meaning; preserve original metadata |
> | Data processing | No lost records; schema changes need approval |
> | Research synthesis | Every claim has a source; no fabricated citations |

---

## 5. Soft constraints (strongly recommended)

- **Precheck first**: verify preconditions before each item.
- **Resumable progress**: update the progress table after every single item.
- **No silent inference**: imprecise manifest fields must be replaced with
  actual values at self-check time.
- <task-specific additions>

---

## 6. Command / operation templates

> Filled in by the orchestrator for the actual platform and task type.
> See `references/check-commands.md` for patterns. For code projects, use the
> project's own test/lint/build commands.

### 6.1 Precheck (verify preconditions)

```
<commands verifying input existence, counts, state>
```

### 6.2 Core execution

```
<the actual operational steps>
```

### 6.3 Post-execution verification

```
<commands confirming the result matches expectations>
```

> Templates are a runnable starting point; the executor may adapt them.
> The bar: the executor can run them without guessing.

---

## 7. Escalation triggers (stop and ask)

On any of the following, **stop** and log to the clarification queue:

1. Input/source paths missing or inconsistent with the docs
2. Declared count vs precheck count differs by > `<threshold>`% (default 20%)
3. Conflicts/ambiguities exceed `<limit>` (default 5)
4. Undocumented related sub-items or sub-scopes discovered
5. Edge cases requiring judgment calls
6. Any hard constraint becomes hard to satisfy
7. Review verdict comes back negative

**Forbidden**: guessing intent, expanding/narrowing scope, editing manifests
or rules files.

### Precheck hard gate (critical constraints need forced stops)

> A documented constraint is not an enforcement gate. "Should escalate" reads
> as optional to an executing agent (see anti-patterns AP4). Critical
> escalation conditions must be executable checks that abort on failure.

```
# Precheck script skeleton (bash or PowerShell per platform)
#
# 1. Verify inputs exist        → exit 1 if not
# 2. Verify count deviation     → exit 1 if over threshold
# 3. Other preconditions        → exit 1 if unmet
#
# Rule: wherever the docs say "must", the script has a matching exit 1.
```

---

## 8. Deliverables per batch

1. **Progress table updated**: all status columns for the batch checked off
2. **Self-check report**: `reports/<date>_batch<NN>_self-check.md`
3. **Execution log** (if applicable): `logs/`
4. **Conflict queue**: appended to the progress table, if any
5. **Clarification queue**: appended to the progress table, if any

---

## 9. Directory layout

```text
<task-dir>/
├── reports/          ← self-check reports
├── logs/             ← execution logs (if applicable)
└── (supporting .md files)
```

---

### Filling guide

| Field | Required | Notes |
|---|---|---|
| `<rules-file>` | yes | Task-specific rules document |
| `<manifest>` | yes | The concrete item list |
| Universal constraints 1–4 | keep | Apply to all governed tasks |
| Task-specific constraints | as needed | Use the task-type reference table |
| Command templates | yes | Must run without guessing |
| Escalation triggers | as needed | Tune thresholds to risk level |
