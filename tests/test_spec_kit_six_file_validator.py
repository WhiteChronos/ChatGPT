import tempfile
import unittest
from pathlib import Path
from tools.spec_kit_six_file_validator import FILES, validate

class SixFileTests(unittest.TestCase):
    def test_repo_example(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(validate(root / "examples/spec-kit-decisions-board")["status"], "PASS")

    def test_missing_file_fails(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(validate(Path(t))["status"], "FAIL")

    def test_missing_traceability_fails(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            for file in FILES:
                (root / file).write_text("# Placeholder\n", encoding="utf-8")
            (root / "prd.md").write_text("# PRD\nREQ-01 and AC-01\n", encoding="utf-8")
            result = validate(root)
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("REQ-01" in x["problem"] for x in result["findings"]))

if __name__ == "__main__":
    unittest.main()
