from pathlib import Path
import unittest

from skill_router_auditor.redactor import redact_text


class RedactorTest(unittest.TestCase):
    def test_redacts_paths_and_secret_like_values(self):
        root = Path("D:/example/skills")
        fake_token = "ghp_" + ("a" * 32)
        text = (
            "path=D:/example/skills/demo/SKILL.md "
            "email=person@example.com "
            f"token={fake_token} "
            "url=https://example.test/callback?signature=abcdef"
        )

        redacted = redact_text(text, roots=[root])

        self.assertIn("<SKILL_ROOT>", redacted)
        self.assertIn("<EMAIL>", redacted)
        self.assertIn("<TOKEN>", redacted)
        self.assertIn("signature=<REDACTED>", redacted)
        self.assertNotIn("person@example.com", redacted)


if __name__ == "__main__":
    unittest.main()
