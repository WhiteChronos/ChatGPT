"""Verify Codex discovery entries resolve to the canonical ChatGPT skills."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLUGS = (
    "controle-elaboracao", "requisitos-prd", "arquitetura-sistema",
    "regras-desenvolvimento", "tarefas-planejamento",
    "memoria-projeto", "cenario-validacao",
)

class CodexSkillBridgeTests(unittest.TestCase):
    def test_all_skills_have_canonical_targets(self):
        for slug in SLUGS:
            with self.subTest(slug=slug):
                name = "spec-kit-" + slug
                bridge = ROOT / ".agents" / "skills" / name / "SKILL.md"
                canonical = ROOT / "skills" / name / "SKILL.md"
                self.assertTrue(bridge.is_file())
                self.assertTrue(canonical.is_file())
                body = bridge.read_text(encoding="utf-8")
                self.assertIn(f"name: {name}", body)
                expected = (bridge.parent / "../../../" / "skills" / name / "SKILL.md").resolve()
                self.assertEqual(expected, canonical.resolve())
                self.assertIn("AGENTS.md", body)
                self.assertTrue(body.startswith("---" + chr(10)))

if __name__ == "__main__":
    unittest.main()
