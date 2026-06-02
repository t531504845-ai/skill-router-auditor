import json
import io
from pathlib import Path
import tempfile
import unittest
from contextlib import redirect_stderr

from skill_router_auditor.cli import main


class CliTest(unittest.TestCase):
    def test_cli_writes_json_report(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill_dir = root / "skills" / "browser"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                """---
name: browser-control
description: Use for browser click and screenshot tasks.
---

Do not use for static search.
""",
                encoding="utf-8",
            )
            output = root / "report.json"

            exit_code = main([str(root / "skills"), "--format", "json", "--output", str(output)])

            self.assertEqual(exit_code, 0)
            data = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(data["skills"][0]["name"], "browser-control")

    def test_cli_returns_two_when_gate_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill_dir = root / "skills" / "broken"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                """---
name: broken-skill
---

# Broken
""",
                encoding="utf-8",
            )
            output = root / "report.md"

            with redirect_stderr(io.StringIO()):
                exit_code = main(
                    [
                        str(root / "skills"),
                        "--output",
                        str(output),
                        "--fail-on",
                        "high",
                    ]
                )

            self.assertEqual(exit_code, 2)
            self.assertIn("Missing skill description", output.read_text(encoding="utf-8"))

    def test_cli_writes_policy_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill_dir = root / "skills" / "browser"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                """---
name: browser-control
description: Use for browser click and screenshot tasks.
---

Do not use for static search.
""",
                encoding="utf-8",
            )
            policy = root / "AGENTS.skill-routing.md"

            exit_code = main(
                [
                    str(root / "skills"),
                    "--format",
                    "policy",
                    "--output",
                    str(root / "report.md"),
                    "--policy-output",
                    str(policy),
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertIn("# Skill Routing Policy", policy.read_text(encoding="utf-8"))

    def test_cli_redacts_input_root_in_json_report(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill_dir = root / "skills" / "browser"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                """---
name: browser-control
description: Use for browser click and screenshot tasks.
---

Do not use for static search.
""",
                encoding="utf-8",
            )
            output = root / "report.json"

            exit_code = main(
                [
                    str(root / "skills"),
                    "--format",
                    "json",
                    "--output",
                    str(output),
                    "--redact",
                ]
            )

            text = output.read_text(encoding="utf-8")
            self.assertEqual(exit_code, 0)
            self.assertIn("<SKILL_ROOT>", text)
            self.assertNotIn(str(root), text)


if __name__ == "__main__":
    unittest.main()
