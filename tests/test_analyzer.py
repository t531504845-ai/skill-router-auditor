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

    def test_analyze_routes_x_twitter_data_skills(self):
        skill = Skill(
            name="x-twitter-scraper",
            description=(
                "Use when the user needs X (Twitter) data through Xquik: REST API "
                "integration, MCP setup, tweet search, user lookup, timeline reads, "
                "follower export, media download, monitoring, webhooks, and bulk extraction."
            ),
            path=Path("SKILL.md"),
            body="Do not use for private reads or writes without explicit approval.",
        )

        report = analyze((skill,))

        self.assertEqual(report.categories["social-data"], ("x-twitter-scraper",))

    def test_overlap_handles_duplicate_skill_names_by_path(self):
        left = Skill(
            name="duplicate",
            description="Use for browser click screenshot and tab inspection tasks.",
            path=Path("a/SKILL.md"),
            body="Do not use for static search.",
        )
        right = Skill(
            name="duplicate",
            description="Use for browser click screenshot and tab inspection tasks.",
            path=Path("b/SKILL.md"),
            body="Do not use for static search.",
        )

        report = analyze((left, right), overlap_threshold=0.9)

        self.assertEqual(len(report.overlaps), 1)
        self.assertEqual(report.overlaps[0].left, "duplicate")


if __name__ == "__main__":
    unittest.main()
