from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import build_handoff_package
import handoff_to_feishu


class FeishuHandoffPackageTests(unittest.TestCase):
    def test_build_package_redacts_source_material_and_writes_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            transcript = base / "transcript-source.md"
            transcript.write_text(
                "visible turn\napp_secret: should-not-leak\napi_key=sk-testsecret123456\n",
                encoding="utf-8",
            )
            output = base / "package"

            manifest = build_handoff_package.build_package(
                title="迁移测试",
                output=output,
                summary="继续验证 Feishu handoff transport",
                next_action="先读 handoff.md",
                coverage="test coverage",
                transcript_path=transcript,
            )

            self.assertTrue(manifest["redaction_applied"])
            self.assertEqual("compact-plus-source-materials", manifest["handoff_kind"])

            rendered = (output / "transcript.md").read_text(encoding="utf-8")
            self.assertIn("> Coverage: test coverage", rendered)
            self.assertIn("app_secret=[REDACTED]", rendered)
            self.assertNotIn("should-not-leak", rendered)
            self.assertNotIn("sk-testsecret123456", rendered)

            persisted = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
            self.assertTrue(persisted["redaction_applied"])

    def test_select_project_requires_exact_workspace_and_feishu_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            workspace = base / "workspace"
            workspace.mkdir()
            config = base / "config.toml"
            config.write_text(
                f"""
[[projects]]
name = "wrong"
[projects.agent.options]
work_dir = "{base / 'other'}"
[[projects.platforms]]
type = "feishu"
[projects.platforms.options]
app_id = "app"
app_secret = "secret"
allow_from = "user"

[[projects]]
name = "right"
[projects.agent.options]
work_dir = "{workspace}"
[[projects.platforms]]
type = "feishu"
[projects.platforms.options]
app_id = "app"
app_secret = "secret"
allow_from = "user"
""".strip()
                + "\n",
                encoding="utf-8",
            )

            match = handoff_to_feishu.select_project(config, workspace)
            self.assertEqual("right", match.name)
            self.assertEqual(str(workspace.resolve()), match.work_dir)

            with self.assertRaisesRegex(RuntimeError, "exactly matches"):
                handoff_to_feishu.select_project(config, workspace / "subdir")

    def test_build_delivery_plan_numbers_handoff_and_source_chunks(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp)
            (package / "launch-message.md").write_text("launch", encoding="utf-8")
            (package / "handoff.md").write_text("h" * 1100, encoding="utf-8")
            (package / "transcript.md").write_text("t" * 1200, encoding="utf-8")

            messages = handoff_to_feishu.build_delivery_plan(package, max_chars=600)

            self.assertEqual("启动", messages[0].kind)
            self.assertEqual("完成", messages[-1].kind)
            self.assertIn("[工作态交接 1/2]", messages[1].text)
            self.assertIn("[工作态交接 2/2]", messages[2].text)
            self.assertIn("[原文材料 1/2]", messages[3].text)
            self.assertIn("[原文材料 2/2]", messages[4].text)


if __name__ == "__main__":
    unittest.main()
