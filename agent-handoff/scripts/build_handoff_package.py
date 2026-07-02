#!/usr/bin/env python3
"""Build a Feishu handoff package from available conversation material."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path


SECRET_PATTERNS = [
    re.compile(r"(?i)(app_secret|api[_-]?key|token|password|cookie)\s*[:=]\s*([^\s`]+)"),
    re.compile(r"(?i)(sk-[A-Za-z0-9_-]{12,})"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S),
]


def redact(text: str) -> tuple[str, bool]:
    changed = False
    result = text
    for pattern in SECRET_PATTERNS:
        def replacement(match: re.Match[str]) -> str:
            if match.lastindex and match.lastindex >= 2:
                return f"{match.group(1)}=[REDACTED]"
            return "[REDACTED]"

        result, count = pattern.subn(replacement, result)
        changed = changed or count > 0
    return result, changed


def read_optional(path: Path | None) -> str:
    if not path:
        return ""
    return path.read_text(encoding="utf-8")


def make_handoff(title: str, summary: str, next_action: str, coverage: str) -> str:
    return f"""# {title}

## 工作态交接

### 当前目标

{summary.strip() or "把当前 Codex 对话迁移到飞书，通过 CC Connect 新会话继续。"}

### 已定方案

- 采用 compact/resume 思路：工作态摘要进入新会话，原文材料包用于追溯。
- 不把这次交接描述为活跃 Codex Desktop 进程的实时接管。
- 新会话遇到不确定内容时，优先查随附原文材料。

### 覆盖范围

{coverage}

### 关键约束

- 不启用 yolo / danger / bypass 权限。
- 不修改 CC Connect 配置，除非用户明确要求。
- 不声称拥有完整逐字稿，除非 transcript 来源确实完整。
- 发送前应移除 secret、token、cookie、private key 和 `.env` 值。

### 下一步

{next_action.strip() or "在飞书群中启动 CC Connect，并要求新会话先读取本交接包再继续。"}
"""


def make_launch_message(title: str) -> str:
    return f"""我们从 Codex Desktop 迁移到飞书继续：{title}

请先读取“工作态交接”，把它作为当前会话状态；完整对话记录/材料包已随附。遇到不确定时优先查原文，不要凭摘要猜。"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title", required=True)
    parser.add_argument("--summary", default="")
    parser.add_argument("--next-action", default="")
    parser.add_argument("--coverage", default="visible-current-conversation")
    parser.add_argument("--transcript", type=Path)
    parser.add_argument("--notes", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def build_package(
    *,
    title: str,
    output: Path,
    summary: str = "",
    next_action: str = "",
    coverage: str = "visible-current-conversation",
    transcript_path: Path | None = None,
    notes_path: Path | None = None,
) -> dict[str, object]:
    output.mkdir(parents=True, exist_ok=True)
    source_parts = []
    if transcript_path:
        source_parts.append(("Transcript", read_optional(transcript_path)))
    if notes_path:
        source_parts.append(("Notes", read_optional(notes_path)))
    if not source_parts:
        source_parts.append(("Coverage Note", "No raw transcript file was provided."))

    redaction_applied = False
    transcript_sections = [f"> Coverage: {coverage}\n"]
    for heading, text in source_parts:
        clean, changed = redact(text)
        redaction_applied = redaction_applied or changed
        transcript_sections.append(f"\n## {heading}\n\n{clean.strip()}\n")

    handoff = make_handoff(title, summary, next_action, coverage)
    transcript = "\n".join(transcript_sections).strip() + "\n"
    launch_message = make_launch_message(title)
    manifest = {
        "title": title,
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "coverage": coverage,
        "handoff_kind": "compact-plus-source-materials",
        "redaction_applied": redaction_applied,
        "files": ["handoff.md", "transcript.md", "launch-message.md", "manifest.json"],
    }

    (output / "handoff.md").write_text(handoff, encoding="utf-8")
    (output / "transcript.md").write_text(transcript, encoding="utf-8")
    (output / "launch-message.md").write_text(launch_message, encoding="utf-8")
    (output / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    args = parse_args()
    build_package(
        title=args.title,
        output=args.output,
        summary=args.summary,
        next_action=args.next_action,
        coverage=args.coverage,
        transcript_path=args.transcript,
        notes_path=args.notes,
    )
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
