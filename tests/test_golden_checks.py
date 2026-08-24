"""Test golden checks for v4.4 compliance."""

import json
from pathlib import Path


def test_governance_schema_exists():
    """Verify governance schema file exists."""
    schema_path = Path("schemas/governance_v4_4.schema.json")
    assert schema_path.exists(), "governance_v4_4.schema.json not found"


def test_governance_schema_has_constants():
    """Verify schema contains required golden constants."""
    schema_path = Path("schemas/governance_v4_4.schema.json")
    schema = json.loads(schema_path.read_text())
    
    # Check external_mm constant
    assert "properties" in schema
    assert "external_mm" in schema["properties"]
    
    # Check aspect_ratio constant
    assert "aspect_ratio" in schema["properties"]


def test_prompt_mestre_contains_requirements():
    """Verify prompt file contains required specifications."""
    prompt_path = Path("governance/PROMPT_MESTRE_AUTOMACAO_v4_4.md")
    content = prompt_path.read_text()
    
    # Check for required constants
    assert "12 mm" in content, "Missing '12 mm' specification"
    assert "CMD" in content, "Missing 'CMD' state"
    assert "RUN" in content, "Missing 'RUN' state"
    assert "FAULT" in content, "Missing 'FAULT' state"


def test_memory_policy_exists():
    """Verify memory policy file exists."""
    policy_path = Path("memory/MEMORY_POLICY.md")
    assert policy_path.exists(), "MEMORY_POLICY.md not found"


def test_regra_de_ouro_exists():
    """Verify golden rules document exists."""
    rules_path = Path("governance/REGRA_DE_OURO.md")
    assert rules_path.exists(), "REGRA_DE_OURO.md not found"


def test_ci_lesson_exists():
    """Verify CI lesson documentation exists."""
    lesson_path = Path("memory/LESSON_CI_PYTHONPATH_2026-08-24.md")
    assert lesson_path.exists(), "LESSON_CI_PYTHONPATH_2026-08-24.md not found"
