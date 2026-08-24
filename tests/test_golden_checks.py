"""Test golden checks for v4.4 compliance."""

import json
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def test_governance_schema_exists():
    """Verify governance schema file exists."""
    schema_path = _repo_root() / "schemas" / "governance_v4_4.schema.json"
    assert schema_path.exists(), f"governance_v4_4.schema.json not found at {schema_path}"


def test_governance_schema_has_constants():
    """Verify schema contains required AUTOMAÇÃO DM golden constants."""
    schema_path = _repo_root() / "schemas" / "governance_v4_4.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    assert "properties" in schema, "Missing 'properties' in schema"
    assert "symbol_standard" in schema["properties"], "Missing 'symbol_standard' in schema properties"

    symbol_standard = schema["properties"]["symbol_standard"]
    assert "properties" in symbol_standard, "Missing 'properties' in symbol_standard"

    symbol_props = symbol_standard["properties"]
    assert "external_mm" in symbol_props, "Missing 'external_mm' in symbol_standard properties"
    assert "aspect_ratio" in symbol_props, "Missing 'aspect_ratio' in symbol_standard properties"

    assert symbol_props["external_mm"].get("const") == 12, "external_mm must be const 12"
    assert symbol_props["aspect_ratio"].get("const") == 1, "aspect_ratio must be const 1"
    assert symbol_props["name"].get("const") == "AUTOMACAO DM R00-05", "Wrong symbol standard name"


def test_critical_signal_roles_are_independent():
    """Verify CMD/RUN/FAULT/AVAILABLE are preserved as distinct critical roles."""
    schema_path = _repo_root() / "schemas" / "governance_v4_4.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    roles = schema["properties"]["critical_signal_roles"]["const"]
    assert roles == ["CMD", "RUN", "FAULT", "AVAILABLE"]


def test_prompt_mestre_contains_requirements():
    """Verify prompt file contains required engineering specifications."""
    prompt_path = _repo_root() / "governance" / "PROMPT_MESTRE_AUTOMACAO_v4_4.md"
    assert prompt_path.exists(), f"Prompt file not found at {prompt_path}"

    content = prompt_path.read_text(encoding="utf-8")

    assert "AUTOMAÇÃO DM R00-05" in content, "Missing AUTOMAÇÃO DM R00-05 standard"
    assert "12 mm" in content, "Missing '12 mm' specification"
    assert "CMD" in content, "Missing 'CMD' role"
    assert "RUN" in content, "Missing 'RUN' role"
    assert "FAULT" in content, "Missing 'FAULT' role"
    assert "AVAILABLE" in content, "Missing 'AVAILABLE' role"


def test_memory_policy_exists():
    """Verify memory policy file exists."""
    policy_path = _repo_root() / "memory" / "MEMORY_POLICY.md"
    assert policy_path.exists(), f"MEMORY_POLICY.md not found at {policy_path}"


def test_regra_de_ouro_exists_and_preserves_engineering_contract():
    """Verify golden rules document exists and contains core engineering rules."""
    rules_path = _repo_root() / "governance" / "REGRA_DE_OURO.md"
    assert rules_path.exists(), f"REGRA_DE_OURO.md not found at {rules_path}"
    content = rules_path.read_text(encoding="utf-8")
    assert "AUTOMAÇÃO DM R00-05" in content
    assert "12 mm" in content
    assert "CMD != RUN" in content
    assert "AVAILABLE" in content


def test_ci_lesson_exists():
    """Verify CI lesson documentation exists."""
    lesson_path = _repo_root() / "memory" / "LESSON_CI_PYTHONPATH_2026-08-24.md"
    assert lesson_path.exists(), f"LESSON_CI_PYTHONPATH_2026-08-24.md not found at {lesson_path}"


def test_ci_expression_lesson_exists():
    """Verify CI expression interpolation lesson exists."""
    lesson_path = _repo_root() / "memory" / "LESSON_CI_EXPRESSION_INTERPOLATION_2026-08-24.md"
    assert lesson_path.exists(), f"LESSON_CI_EXPRESSION_INTERPOLATION_2026-08-24.md not found at {lesson_path}"
