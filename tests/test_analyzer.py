from pathlib import Path
import unittest

from skill_router_auditor.analyzer import analyze, tokenize
from skill_router_auditor.models import Skill


class AnalyzerTest(unittest.TestCase):
    def test_tokenize_removes_generic_terms(self):
        self.assertNotIn("automation", tokenize("automation browser click repository"))
        self.assertIn("browser", tokenize("automation browser click repository"))

    def test_analyze_reports_missing_negative_guidance(self):
        skill = Skill(
            name="github-automation",
            description="Use for GitHub repository pull request review and issue triage.",
            path=Path("SKILL.md"),
        )

        report = analyze((skill,))

        messages = [finding.message for finding in report.findings]
        self.assertIn("No negative-trigger guidance found.", messages)

    def test_analyze_builds_categories(self):
        skill = Skill(
            name="spreadsheet-cleanup",
            description="Use for Excel and CSV spreadsheet cleanup.",
            path=Path("SKILL.md"),
            body="Do not use for database migrations.",
        )

        report = analyze((skill,))

        self.assertEqual(report.categories["data"], ("spreadsheet-cleanup",))


if __name__ == "__main__":
    unittest.main()
