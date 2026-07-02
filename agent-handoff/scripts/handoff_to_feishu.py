#!/usr/bin/env python3
"""Build a handoff package and deliver it through the matching CC Connect Feishu app."""

from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

from build_handoff_package import build_package


DEFAULT_CONFIG = Path.home() / ".cc-connect" / "config.toml"
DEFAULT_GROUP_HELPER = Path.home() / ".cc-connect" / "bin" / "create_feishu_group.py"


@dataclass(frozen=True)
class ProjectMatch:
    name: str
    work_dir: str


@dataclass(frozen=True)
class DeliveryMessage:
    kind: str
    text: str


def normalize_path(value: str | Path) -> str:
    return str(Path(value).expanduser().resolve())


def select_project(config_path: Path, cwd: Path) -> ProjectMatch:
    with config_path.open("rb") as config_file:
        config = tomllib.load(config_file)

    normalized_cwd = normalize_path(cwd)
    for project in config.get("projects", []):
        agent_options = (project.get("agent") or {}).get("options") or {}
        work_dir = str(agent_options.get("work_dir", "")).strip()
        if not work_dir or normalize_path(work_dir) != normalized_cwd:
            continue
        has_identity = any(
            platform.get("type") == "feishu"
            and bool((platform.get("options") or {}).get("app_id"))
            and bool((platform.get("options") or {}).get("app_secret"))
            and bool((platform.get("options") or {}).get("allow_from"))
            for platform in project.get("platforms", [])
        )
        if has_identity:
            return ProjectMatch(
                name=str(project.get("name", "")).strip() or normalized_cwd,
                work_dir=normalized_cwd,
            )

    raise RuntimeError(
        f"No CC Connect Feishu project exactly matches current workspace: {normalized_cwd}"
    )


def load_group_helper(path: Path) -> ModuleType:
    if not path.is_file():
        raise RuntimeError(f"CC Connect group helper not found: {path}")
    spec = importlib.util.spec_from_file_location("cc_connect_feishu_group", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load CC Connect group helper: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def default_output_dir(cwd: Path) -> Path:
    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    return cwd / "_tmp" / "feishu-handoff" / timestamp


def split_text(text: str, max_chars: int) -> list[str]:
    if max_chars < 500:
        raise ValueError("max_chars must be at least 500")
    normalized = text.strip()
    if not normalized:
        return []
    return [
        normalized[index : index + max_chars]
        for index in range(0, len(normalized), max_chars)
    ]


def labeled_chunks(kind: str, text: str, max_chars: int) -> list[DeliveryMessage]:
    chunks = split_text(text, max_chars)
    total = len(chunks)
    return [
        DeliveryMessage(kind=kind, text=f"[{kind} {index}/{total}]\n{chunk}")
        for index, chunk in enumerate(chunks, start=1)
    ]


def build_delivery_plan(package_dir: Path, max_chars: int) -> list[DeliveryMessage]:
    launch = (package_dir / "launch-message.md").read_text(encoding="utf-8").strip()
    handoff = (package_dir / "handoff.md").read_text(encoding="utf-8")
    transcript = (package_dir / "transcript.md").read_text(encoding="utf-8")

    messages = [DeliveryMessage(kind="启动", text=launch)]
    messages.extend(labeled_chunks("工作态交接", handoff, max_chars))
    messages.extend(labeled_chunks("原文材料", transcript, max_chars))
    messages.append(
        DeliveryMessage(
            kind="完成",
            text="交接包发送完毕。请基于工作态交接继续；遇到歧义时回查原文材料。",
        )
    )
    return messages


def obtain_token(helper: ModuleType, config_path: Path) -> tuple[str, str]:
    app_id, app_secret, _member_id, prefix = helper.load_project_context(config_path)
    response = helper.api_call(
        "POST",
        "/auth/v3/tenant_access_token/internal",
        body={"app_id": app_id, "app_secret": app_secret},
    )
    token = str(response.get("tenant_access_token", ""))
    if not token:
        raise RuntimeError(f"Failed to obtain tenant_access_token: {response}")
    return token, prefix


def send_text(helper: ModuleType, token: str, chat_id: str, text: str) -> None:
    response = helper.api_call(
        "POST",
        "/im/v1/messages?receive_id_type=chat_id",
        token=token,
        body={
            "receive_id": chat_id,
            "msg_type": "text",
            "content": json.dumps({"text": text}, ensure_ascii=False),
        },
    )
    if response.get("code") != 0:
        raise RuntimeError(f"Failed to send Feishu message: {response}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title", required=True)
    parser.add_argument("--group-name")
    parser.add_argument("--existing-chat-id")
    parser.add_argument("--summary", default="")
    parser.add_argument("--next-action", default="")
    parser.add_argument("--coverage", default="visible-current-conversation")
    parser.add_argument("--transcript", type=Path)
    parser.add_argument("--notes", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--max-chars", type=int, default=2800)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--group-helper", type=Path, default=DEFAULT_GROUP_HELPER)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cwd = Path.cwd()
    project = select_project(args.config, cwd)
    helper = load_group_helper(args.group_helper)
    output = args.output or default_output_dir(cwd)

    manifest = build_package(
        title=args.title,
        output=output,
        summary=args.summary,
        next_action=args.next_action,
        coverage=args.coverage,
        transcript_path=args.transcript,
        notes_path=args.notes,
    )
    messages = build_delivery_plan(output, args.max_chars)
    group_name = args.group_name or args.title

    if args.dry_run:
        _app_id, _app_secret, _member_id, prefix = helper.load_project_context(args.config)
        result = {
            "dry_run": True,
            "project": project.name,
            "work_dir": project.work_dir,
            "requested_group_name": group_name,
            "resolved_group_name": helper.apply_prefix(group_name, prefix),
            "existing_chat_id": args.existing_chat_id or "",
            "package_dir": str(output),
            "message_count": len(messages),
            "coverage": manifest["coverage"],
            "redaction_applied": manifest["redaction_applied"],
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    token, _prefix = obtain_token(helper, args.config)
    if args.existing_chat_id:
        chat_id = args.existing_chat_id
        resolved_group_name = ""
    else:
        group = helper.create_group(group_name, args.config)
        chat_id = str(group.get("chat_id", ""))
        resolved_group_name = str(group.get("name", ""))
        if not chat_id:
            raise RuntimeError(f"CC Connect group helper returned no chat_id: {group}")

    for message in messages:
        send_text(helper, token, chat_id, message.text)

    result = {
        "success": True,
        "project": project.name,
        "work_dir": project.work_dir,
        "chat_id": chat_id,
        "group_name": resolved_group_name,
        "package_dir": str(output),
        "message_count": len(messages),
        "coverage": manifest["coverage"],
        "redaction_applied": manifest["redaction_applied"],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
