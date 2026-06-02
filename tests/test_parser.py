import tempfile
import unittest
from pathlib import Path

from skill_router_auditor.parser import parse_frontmatter, parse_skill_file


class ParserTest(unittest.TestCase):
    def test_parse_frontmatter_reads_name_and_description(self):
        metadata, body = parse_frontmatter(
            """---
name: demo
description: "Use for demo tasks."
---

# Demo
"""
        )

        self.assertEqual(metadata["name"], "demo")
        self.assertEqual(metadata["description"], "Use for demo tasks.")
        self.assertEqual(body, "# Demo")

    def test_parse_skill_file_falls_back_to_directory_name(self):
        with tempfile.TemporaryDirectory() as directory:
            skill_dir = Path(directory) / "fallback"
            skill_dir.mkdir()
            skill_file = skill_dir / "SKILL.md"
            skill_file.write_text("# No frontmatter", encoding="utf-8")

            skill = parse_skill_file(skill_file)

        self.assertEqual(skill.name, "fallback")
        self.assertEqual(skill.description, "")

if __name__ == "__main__":
    unittest.main()
