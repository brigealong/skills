---
schema: agent-handoff-envelope
schema_version: "0.1"
handoff_id: "{handoff_id}"
created_at: "{created_at}"
source_agent: "{source_agent}"
target_agent: "{target_agent}"
handoff_reason: "{handoff_reason}"
---

# Agent Handoff: {title}

## Git Checkpoint

- cwd: `{cwd}`
- branch: `{branch}`
- base_commit: `{base_commit}`
- handoff_commit: commit containing this file; resolve with `git log -n1 --format=%H -- {relative_output_path}`
- dirty_state_at_draft:

```text
{dirty_state}
```

## Objective

{objective}

## Success Criteria

- __FILL__

## State

### Completed

- __FILL__

### Current State

- __FILL__

### Remaining

- __FILL__

### Blockers

- __FILL_OR_NONE__

## Decisions

- __FILL__

## Constraints

- __FILL__

## Evidence

### Changed Files

{changed_files}

### Important Files Read

- __FILL__

### Commands Run

- __FILL__

### Verification

- __FILL__

### Artifacts

- __FILL_OR_NONE__

## Next

### Recommended Action

__FILL__

### Resume Prompt

```text
Read {relative_output_path} first. Treat the git commit containing that file as the handoff checkpoint. Continue from "Next / Recommended Action"; do not redo completed work unless verification contradicts the handoff.
```

## Omitted

- raw_transcript: omitted
- reason: structured handoff is intended to reduce rediscovery cost without carrying full conversational trace
