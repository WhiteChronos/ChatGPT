"""Test golden checks for v4.4 compliance."""

import json
from pathlib import Path


def test_governance_schema_exists():
    """Verify governance schema file exists."""
    repo_root = Path(__file__).parent.parent
    schema_path = repo_root / "schemas" / "governance_v4_4.schema.json"
    assert schema_path.exists(), f"governance_v4_4.schema.json not found at {schema_path}"


def test_governance_schema_has_constants():
    """Verify schema contains required golden constants."""
    repo_root = Path(__file__).parent.parent
    schema_path = repo_root / "schemas" / "governance_v4_4.schema.json"
    schema = json.loads(schema_path.read_text())
    
    # Check external_mm constant
    assert "properties" in schema, "Missing 'properties' in schema"
    assert "external_mm" in schema["properties"], "Missing 'external_mm' in properties"
    
    # Check aspect_ratio constant
    assert "aspect_ratio" in schema["properties"], "Missing 'aspect_ratio' in properties"


def test_prompt_mestre_contains_requirements():
    """Verify prompt file contains required specifications."""
    repo_root = Path(__file__).parent.parent
    prompt_path = repo_root / "governance" / "PROMPT_MESTRE_AUTOMACAO_v4_4.md"
    assert prompt_path.exists(), f"Prompt file not found at {prompt_path}"
    
    content = prompt_path.read_text(encoding="utf-8")
    
    # Check for required constants
    assert "12 mm" in content, "Missing '12 mm' specification"
    assert "CMD" in content, "Missing 'CMD' state"
    assert "RUN" in content, "Missing 'RUN' state"
    assert "FAULT" in content, "Missing 'FAULT' state"


def test_memory_policy_exists():
    """Verify memory policy file exists."""
    repo_root = Path(__file__).parent.parent
    policy_path = repo_root / "memory" / "MEMORY_POLICY.md"
    assert policy_path.exists(), f"MEMORY_POLICY.md not found at {policy_path}"


def test_regra_de_ouro_exists():
    """Verify golden rules document exists."""
    repo_root = Path(__file__).parent.parent
    rules_path = repo_root / "governance" / "REGRA_DE_OURO.md"
    assert rules_path.exists(), f"REGRA_DE_OURO.md not found at {rules_path}"


def test_ci_lesson_exists():
    """Verify CI lesson documentation exists."""
    repo_root = Path(__file__).parent.parent
    lesson_path = repo_root / "memory" / "LESSON_CI_PYTHONPATH_2026-08-24.md"
    assert lesson_path.exists(), f"LESSON_CI_PYTHONPATH_2026-08-24.md not found at {lesson_path}"


def test_ci_expression_lesson_exists():
    """Verify CI expression interpolation lesson exists."""
    repo_root = Path(__file__).parent.parent
    lesson_path = repo_root / "memory" / "LESSON_CI_EXPRESSION_INTERPOLATION_2026-08-24.md"
    assert lesson_path.exists(), f"LESSON_CI_EXPRESSION_INTERPOLATION_2026-08-24.md not found at {lesson_path}"
