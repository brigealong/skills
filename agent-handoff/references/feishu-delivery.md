# Feishu Delivery Notes

Use the CC Connect Feishu app identity matched to the current workspace.

## Identity Selection

- Read `~/.cc-connect/config.toml`.
- Match the current working directory to `projects[].agent.options.work_dir`.
- Require that exact project to contain a complete Feishu identity.
- Never fall back to the first Feishu project when the workspace does not match.

The global helper `~/.cc-connect/bin/create_feishu_group.py` already selects the matching workspace identity and applies the configured group-name prefix.

## Delivery Format

The default implementation sends:

1. One launch message.
2. The working-state handoff in numbered chunks.
3. The redacted source transcript/material in numbered chunks.
4. One completion marker.

Chunked text uses the same bot identity as group creation and avoids depending on workspace-specific `lark-cli` profiles.

## Safety

- Do not send app secrets, tokens, cookies, private keys, or `.env` values.
- If the transcript may contain secrets, create a redacted copy and say redaction was applied.
- Do not print app IDs or app secrets in dry-run output.
- Do not claim delivery succeeded unless every Feishu API call returns success.
