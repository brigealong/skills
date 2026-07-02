# Feishu Handoff Package Format

The package is a directory with four files.

## `handoff.md`

Compact working state for the next agent session. Keep it direct:

- Current goal
- Decisions already made
- Important context and files
- Constraints and safety boundaries
- Known gaps
- Recommended next action

This is the part intended to enter the new CC Connect model context.

## `transcript.md`

As-complete-as-available source material. It can contain:

- Raw conversation transcript when available
- Pasted visible conversation turns
- Condensed conversation notes when raw transcript is unavailable
- Links to local files or Feishu docs

Start with a coverage note:

```md
> Coverage: visible current conversation only; earlier hidden turns are not available.
```

## `launch-message.md`

Short message to send to CC Connect:

```md
我们从 Codex Desktop 迁移到飞书继续。请先读取下面的工作态交接，把它作为当前会话状态；完整对话记录/材料包已附后。遇到不确定时优先查原文，不要凭摘要猜。
```

The end-to-end sender follows this with numbered handoff and source-material messages.

## `manifest.json`

Machine-readable metadata:

- `title`
- `created_at`
- `coverage`
- `files`
- `redaction_applied`
- `handoff_kind`

Use `handoff_kind = "compact-plus-source-materials"` for the default flow.
