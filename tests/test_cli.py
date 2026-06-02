import json
from pathlib import Path
import tempfile
import unittest

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


if __name__ == "__main__":
    unittest.main()
