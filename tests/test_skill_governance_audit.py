import tempfile
import unittest
from pathlib import Path
from tools.skill_governance_audit import audit


class SkillAuditTests(unittest.TestCase):
    def test_valid_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / "example"
            skill.mkdir()
            (skill / "SKILL.md").write_text("---\nname: example\ndescription: Checks examples\n---\n# Instructions\nDo it.\n", encoding="utf-8")
            self.assertEqual(audit(root)["status"], "PASS")
            self.assertEqual(audit(root)["checked_skills"], 1)

    def test_missing_description_is_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "SKILL.md").write_text("---\nname: test\n---\ninstructions", encoding="utf-8")
            result = audit(root)
            self.assertEqual(result["status"], "REVIEW_REQUIRED")
            self.assertTrue(any("description" in item["problem"] for item in result["findings"]))

    def test_vendor_excluded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            vendor = root / "vendor" / "upstream"
            vendor.mkdir(parents=True)
            (vendor / "SKILL.md").write_text("invalid", encoding="utf-8")
            self.assertEqual(audit(root)["checked_skills"], 0)

    def test_fixture_excluded_but_real_invalid_skill_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = root / "plugins" / "example" / "tests" / "fixtures" / "upstream"
            fixture.mkdir(parents=True)
            (fixture / "SKILL.md").write_text("invalid", encoding="utf-8")
            actual = root / "plugins" / "example" / "real"
            actual.mkdir()
            (actual / "SKILL.md").write_text("invalid", encoding="utf-8")
            result = audit(root)
            self.assertEqual(result["checked_skills"], 1)
            self.assertEqual(result["status"], "REVIEW_REQUIRED")
            self.assertEqual(len(result["findings"]), 1)

    def test_empty_instructions_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "SKILL.md").write_text("---\nname: example\ndescription: x\n---\n", encoding="utf-8")
            self.assertEqual(audit(root)["status"], "REVIEW_REQUIRED")

    def test_test_fixtures_are_not_active_skills(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = root / "plugins" / "example" / "tests" / "fixtures" / "upstream"
            fixture.mkdir(parents=True)
            (fixture / "SKILL.md").write_text("invalid fixture", encoding="utf-8")
            result = audit(root)
            self.assertEqual(result["checked_skills"], 0)
            self.assertEqual(result["status"], "PASS")

    def test_fixture_named_active_skill_is_still_audited(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            active = root / ".agents" / "skills" / "fixtures"
            active.mkdir(parents=True)
            (active / "SKILL.md").write_text("invalid active skill", encoding="utf-8")
            result = audit(root)
            self.assertEqual(result["checked_skills"], 1)
            self.assertEqual(result["status"], "REVIEW_REQUIRED")

    def test_non_fixture_path_with_tests_and_fixtures_is_audited(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            active = root / "tests" / "sample-plugin" / "fixtures"
            active.mkdir(parents=True)
            (active / "SKILL.md").write_text("invalid active skill", encoding="utf-8")
            result = audit(root)
            self.assertEqual(result["checked_skills"], 1)
            self.assertEqual(result["status"], "REVIEW_REQUIRED")


if __name__ == "__main__":
    unittest.main()
