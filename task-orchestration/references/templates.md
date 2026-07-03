# Template Index

This skill ships three complete templates. Copy them into the task directory
and fill in the placeholders.

## The templates

| Template | Source file | Copy into task dir as | Governs |
|---|---|---|---|
| A | `references/template-execution.md` | `execution-brief.md` | *How* to do it |
| B | `references/template-progress.md` | `progress-table.md` | *How far along* it is |
| C | `references/template-acceptance.md` | `acceptance-spec.md` | *Whether it's right* |

## Workflow

0. **Admission check (first):** confirm the upstream contract's end state —
   `BLOCKED` means no templates and no dispatch; Tier 2 requires an
   independent contract. Record `contract_ref` + `contract_status`. See
   "Contract admission" in SKILL.md.
1. Create the task directory (path chosen by the orchestrator).
2. Copy Template A → `execution-brief.md`. Fill the top section
   ("0. Upstream contract & admission": contract_ref / contract_status /
   design_spec_ref) **first**, then the rest. Hand it to the executor.
3. Copy Template B → `progress-table.md`. Fill in the checklist items and
   batch split; define the stage columns.
4. Copy Template C → `acceptance-spec.md`. Adjust the checks to the task.
5. Create supporting files as needed: rule files, item manifests.

## How the three relate

```text
Execution brief (A) ── constrains "how"
    │
    ├── Progress table (B) ── tracks "how far"
    │       ├── conflict queue ── adjudicates "what about conflicts"
    │       └── clarification queue ── answers "what about questions"
    │
    └── Acceptance spec (C) ── judges "is it right"
            ├── §1 self-check ── the executor's own evidence
            ├── §2 final review ── the reviewer's independent falsification
            └── §3 final acceptance ── whole-task sign-off
```

## Common placeholders

All templates use `<...>` placeholders:

| Placeholder | Meaning |
|---|---|
| `<task-name>` | Short name for the task |
| `<rules-file>` | Task-specific rules document |
| `<manifest>` | Complete list of items to execute |
| `<date>` | Date in YYYYMMDD |
| `<NN>` | Batch number (01, 02, …) |
| `<item-id>` | Checklist item id (e.g. 1.1.1) |
| `<threshold>` | Escalation threshold (default 20%) |
| `<platform>` | Execution environment (windows / macos / linux) |
| `<stage-N>` | Stage column name (defined by the orchestrator) |
