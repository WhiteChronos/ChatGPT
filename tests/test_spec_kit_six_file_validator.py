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

    def test_missing_test_and_evidence_traceability_fails(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            for file in FILES:
                (root / file).write_text("# Document\n", encoding="utf-8")
            (root / "prd.md").write_text("# PRD\nREQ-01 and AC-01\n", encoding="utf-8")
            (root / "tarefas.md").write_text(
                "# Tasks\nTASK-01 / REQ-01 / AC-01\n", encoding="utf-8"
            )
            (root / "cenario.md").write_text(
                "# Scenarios\nSC-01 / REQ-01 / AC-01\n", encoding="utf-8"
            )

            result = validate(root)

            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(
                any(
                    finding["problem"]
                    == "missing end-to-end traceability for REQ-01 through TEST and EVIDENCE"
                    for finding in result["findings"]
                )
            )

    def test_dangling_traceability_identifiers_fail(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            for file in FILES:
                (root / file).write_text("# Document\n", encoding="utf-8")
            (root / "prd.md").write_text("# PRD\nREQ-01 and AC-01\n", encoding="utf-8")
            (root / "tarefas.md").write_text(
                "# Tasks\nTASK-01 / REQ-01 / AC-01\n", encoding="utf-8"
            )
            (root / "cenario.md").write_text(
                "# Scenarios\nSC-01 / TEST-01 / REQ-01 / AC-01\n", encoding="utf-8"
            )
            (root / "memoria.md").write_text(
                "# Memory\nEVIDENCE-01\n"
                "| Requirement | Task | Scenario | Test | Evidence |\n"
                "| --- | --- | --- | --- | --- |\n"
                "| REQ-01 | TASK-99 | SC-99 | TEST-99 | EVIDENCE-99 |\n",
                encoding="utf-8",
            )

            result = validate(root)

            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("TASK-99" in item["problem"] for item in result["findings"]))
            self.assertTrue(any("SC-99" in item["problem"] for item in result["findings"]))
            self.assertTrue(any("TEST-99" in item["problem"] for item in result["findings"]))
            self.assertTrue(any("EVIDENCE-99" in item["problem"] for item in result["findings"]))

if __name__ == "__main__":
    unittest.main()
