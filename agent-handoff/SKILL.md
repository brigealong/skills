---
name: agent-handoff
description: >-
  Create a structured handoff envelope when work must move from one agent,
  runtime, or interaction surface to another — Codex to/from Claude Code,
  quota/context compaction, role change, reviewer/executor transfer, or
  continuing the conversation in Feishu/Lark via CC Connect. Produces one
  compact, resumable envelope and then delivers it over a chosen transport
  (transport=file-git: a handoff file plus an explicit git checkpoint;
  transport=feishu: a CC Connect continuation package sent to a Feishu group).
  Do not use for normal task narration, raw transcript dumping, or Hermes Kanban
  card dispatch.
argument-hint: What will the next session focus on?
disable-model-invocation: true
---

# Agent Handoff

Use this skill to create a compact, evidence-backed handoff that another agent or
session can resume from without rereading the whole conversation.

A handoff has two separable parts:

- **Envelope (transport-agnostic)**: the working-state content — what was done,
  current state, what's left, constraints, evidence, and one usable resume prompt.
- **Transport (how it's delivered)**: where the envelope lands and what marks the
  transfer boundary.

Chat messages are narration. The delivered envelope — committed file or sent
package — is the transfer boundary.

## Transport Selection

| `transport=` | When | Transfer boundary |
|---|---|---|
| `file-git` (default) | Same machine / repo; handing to another agent or runtime that can read the repo (Codex↔Claude Code, quota/context compaction, role change, reviewer/executor). | The handoff `.md` + the git commit containing it. |
| `feishu` | Continue the conversation in Feishu/Lark through CC Connect (non-realtime cross-channel compact/resume), or when a repo-local file is not the right surface. | The CC Connect continuation package delivered to a Feishu group. |

Pick the transport from the user's intent. If unstated and the work lives in a
repo, default to `file-git`. Both transports carry the **same envelope content**;
they differ only in delivery and boundary.

## Envelope Content (both transports)

The envelope must include:

- source and target agent/runtime/surface;
- reason for transfer;
- objective and success criteria;
- completed work, current state, remaining work, and blockers;
- decisions and constraints that the next agent must preserve;
- evidence pointers: changed files, important files read, commands run,
  verification, and artifacts;
- one directly usable `resume_prompt`;
- a **suggested skills** list: which skills the resuming agent should load to
  continue (reference them by name; omit if none apply);
- an explicit note that raw transcript is omitted unless the user asks for it.

Keep the main body around 800–1500 Chinese characters or equivalent. Use paths,
commit references, and artifact links instead of copying diffs or logs.

### Compression Rules

- Inline conclusions and next action; reference evidence by path.
- Preserve constraints, decisions, and verification results more aggressively
  than conversational background.
- List failed commands only when they affect the next action.
- Treat dirty workspace state as evidence. If it is unrelated, state that it was
  left unstaged.
- If a required fact is unknown, write `unknown` with a short reason. Do not
  invent paths, commits, test results, or agent capabilities.

### Resume Prompt

The `resume_prompt` should be directly pasteable into the target. It must name
the handoff (file or package), the expected boundary (git checkpoint or Feishu
group), and the first concrete step.

Example (file-git):

```text
Read admin/handoffs/20260617-2130-agent-handoff.md first. Treat the git commit
containing that file as the checkpoint. Continue from `next.recommended_action`;
do not redo completed work unless verification contradicts the handoff.
```

---

## Transport: `file-git` (default)

A file-first checkpoint inside the repo.

### Output Contract

Create one Markdown handoff file. In this task directory, default to:

```text
admin/handoffs/YYYYMMDD-HHMM-<slug>.md
```

For other repositories, prefer a project-local `admin/handoffs/` or `handoffs/`
directory. Do not write stable reusable knowledge into the handoff; promote that
later to `docs/` or the local knowledge track.

### Workflow

1. Inspect current state:

   ```bash
   git status --short
   git branch --show-current
   git rev-parse HEAD
   ```

2. Draft the envelope:

   ```bash
   SKILL_DIR="${AGENT_HANDOFF_SKILL_DIR:-$HOME/.agents/skills/agent-handoff}"
   python3 "$SKILL_DIR/scripts/handoff_envelope.py" draft \
     --slug <short-topic> \
     --source-agent <codex|claude-code|hermes|other> \
     --target-agent <codex|claude-code|hermes|other> \
     --reason <quota_exhausted|context_compaction|role_change|review|parallel_delegate|surface_switch|manual> \
     --objective "<one sentence objective>" \
     --output-dir admin/handoffs
   ```

3. Fill every `__FILL__` placeholder. Keep only high-signal facts. Do not paste
   raw trace unless the user explicitly asks.

4. Validate the handoff file:

   ```bash
   python3 "$SKILL_DIR/scripts/handoff_envelope.py" validate \
     admin/handoffs/<file>.md
   ```

5. Create the git checkpoint. Stage only the handoff and the files that are part
   of this transfer; do not stage unrelated workspace changes.

   ```bash
   git status --short
   git add <handoff-file> <intentional-work-files>
   git commit -m "handoff: <handoff_id>"
   ```

6. Record the checkpoint for the user:

   ```bash
   git log -n1 --format=%H -- <handoff-file>
   ```

   The returned commit is the `handoff_commit`. The file itself intentionally
   does not self-record that hash to avoid amend-only workflows.

---

## Transport: `feishu`

Deliver the envelope as a CC Connect continuation package to a Feishu/Lark group.
Treat this as a **cross-channel compact/resume**, not as realtime process attach.

Produce two layers:

1. **Working-state handoff** — the envelope above, in a form a new CC Connect
   session can immediately use.
2. **Source materials** — as-complete-as-available transcript, links, files, and
   caveats for traceability. Never claim a full transcript if the current surface
   does not expose one; say exactly what coverage is included.

### Default Command

Use the end-to-end helper:

```bash
SKILL_DIR="${AGENT_HANDOFF_SKILL_DIR:-$HOME/.agents/skills/agent-handoff}"
python3 "$SKILL_DIR/scripts/handoff_to_feishu.py" \
  --title "短标题" \
  --transcript path/to/transcript.md \
  --summary "当前目标与已定方案" \
  --next-action "新会话首先要做的动作"
```

The script:

- Matches the current working directory to an exact CC Connect project and uses
  that project's Feishu app identity (refuses unknown workspaces — no fallback to
  another app identity).
- Calls `~/.cc-connect/bin/create_feishu_group.py` to create a group unless
  `--existing-chat-id` is supplied.
- Builds the package and sends the launch message, handoff, and redacted source
  material in ordered chunks.

Use `--dry-run` before the first real delivery from a workspace: it builds the
package and reports the selected project, resolved group name, and message count
without network writes. Use `scripts/build_handoff_package.py` only when the user
wants a local package without sending it.

If no transcript file exists, first write the best available conversation
material to a file inside the current workspace, clearly marking gaps, then run
the helper.

### Workflow

1. Capture the available conversation (prefer an exposed raw transcript;
   otherwise write the visible turns plus a precise coverage note).
2. Confirm the destination: existing Feishu group if the user names one; a new
   group if they ask to create one or say "continue in Feishu" without a target.
3. Run a dry-run when this workspace has not been verified before.
4. Build and deliver the package: `handoff.md` (envelope), `transcript.md`
   (source material), `launch-message.md` (short bot message), `manifest.json`
   (metadata + caveats).
5. Preserve security: redact secrets, tokens, cookies, app secrets, private keys,
   and `.env` values; do not enable yolo/danger/bypass permissions; do not modify
   `~/.cc-connect/config.toml` unless explicitly asked.

### CC Connect Notes

- A Feishu group is a continuation container; this transport does **not** attach
  to an already-running Codex Desktop process. The reliable MVP is: new CC Connect
  session + compact state + traceable material package.
- Agent Workspace and Academy Workspace may use different CC Connect Feishu app
  identities — always select by the exact current `work_dir`.
- If upstream CC Connect gains stable active-session attach for the relevant
  agent, prefer that for true same-session continuation; otherwise use this.

### References

- `references/feishu-delivery.md` — when actually sending through Feishu or
  deciding between message, document, and file delivery.
- `references/package-format.md` — when changing the package shape.
