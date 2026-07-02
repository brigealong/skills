#!/usr/bin/env python3
"""Draft and validate structured agent handoff envelopes."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path.cwd().resolve()
SKILL_DIR = Path(__file__).resolve().parents[1]
TEMPLATE = SKILL_DIR / "assets" / "handoff-template.md"
PLACEHOLDER_RE = re.compile(r"__(?:FILL|FILL_OR_NONE)__")

REQUIRED_FRONTMATTER = {
    "schema",
    "schema_version",
    "handoff_id",
    "created_at",
    "source_agent",
    "target_agent",
    "handoff_reason",
}

REQUIRED_HEADINGS = [
    "# Agent Handoff:",
    "## Git Checkpoint",
    "## Objective",
    "## Success Criteria",
    "## State",
    "### Completed",
    "### Current State",
    "### Remaining",
    "### Blockers",
    "## Decisions",
    "## Constraints",
    "## Evidence",
    "### Changed Files",
    "### Important Files Read",
    "### Commands Run",
    "### Verification",
    "### Artifacts",
    "## Next",
    "### Recommended Action",
    "### Resume Prompt",
    "## Omitted",
]


def run_git(args: list[str], default: str = "unknown") -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return default
    value = result.stdout.strip()
    return value if value else default


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", value)
    value = value.strip("-")
    return value or "handoff"


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def format_block(value: str) -> str:
    return value.strip() if value and value != "unknown" else "clean"


def format_changed_files(status: str) -> str:
    if status == "unknown" or not status.strip():
        return "- none"
    lines = []
    for line in status.splitlines():
        marker = line[:2].strip() or "?"
        path = line[3:].strip() if len(line) > 3 else line.strip()
        lines.append(f"- `{path}` ({marker})")
    return "\n".join(lines) if lines else "- none"


def read_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    fields: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, raw_value = line.split(":", 1)
        fields[key.strip()] = raw_value.strip().strip('"')
    return fields


def draft(args: argparse.Namespace) -> int:
    output_dir = (ROOT / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    now = dt.datetime.now().astimezone()
    stamp = now.strftime("%Y%m%d-%H%M")
    slug = slugify(args.slug)
    handoff_id = f"{stamp}-{slug}"
    output = output_dir / f"{handoff_id}.md"
    relative_output = rel(output)

    if output.exists() and not args.force:
        print(f"refusing to overwrite existing file: {relative_output}", file=sys.stderr)
        return 2

    status = run_git(["status", "--short"], default="")
    content = TEMPLATE.read_text(encoding="utf-8").format(
        handoff_id=handoff_id,
        created_at=now.isoformat(timespec="seconds"),
        source_agent=args.source_agent,
        target_agent=args.target_agent,
        handoff_reason=args.reason,
        title=args.slug.strip() or "handoff",
        cwd=ROOT.as_posix(),
        branch=run_git(["branch", "--show-current"]),
        base_commit=run_git(["rev-parse", "HEAD"]),
        dirty_state=format_block(status),
        objective=args.objective.strip() or "__FILL__",
        changed_files=format_changed_files(status),
        relative_output_path=relative_output,
    )
    output.write_text(content, encoding="utf-8")
    print(relative_output)
    return 0


def validate(args: argparse.Namespace) -> int:
    path = Path(args.file)
    if not path.is_absolute():
        path = ROOT / path
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []

    fields = read_frontmatter(text)
    missing = sorted(REQUIRED_FRONTMATTER - set(fields))
    if missing:
        errors.append(f"missing frontmatter fields: {', '.join(missing)}")
    if fields.get("schema") != "agent-handoff-envelope":
        errors.append("frontmatter schema must be agent-handoff-envelope")
    if fields.get("schema_version") != "0.1":
        errors.append("frontmatter schema_version must be 0.1")

    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            errors.append(f"missing heading: {heading}")

    placeholders = sorted(set(PLACEHOLDER_RE.findall(text)))
    if placeholders:
        errors.append(f"unfilled placeholders remain: {', '.join(placeholders)}")

    if "raw_transcript: omitted" not in text:
        errors.append("omitted section must state raw_transcript: omitted")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"OK: {rel(path)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    draft_cmd = sub.add_parser("draft", help="create a handoff draft")
    draft_cmd.add_argument("--slug", required=True, help="short topic for filename")
    draft_cmd.add_argument("--source-agent", required=True)
    draft_cmd.add_argument("--target-agent", required=True)
    draft_cmd.add_argument("--reason", required=True)
    draft_cmd.add_argument("--objective", default="")
    draft_cmd.add_argument("--output-dir", default="admin/handoffs")
    draft_cmd.add_argument("--force", action="store_true")
    draft_cmd.set_defaults(func=draft)

    validate_cmd = sub.add_parser("validate", help="validate a filled handoff")
    validate_cmd.add_argument("file")
    validate_cmd.set_defaults(func=validate)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
