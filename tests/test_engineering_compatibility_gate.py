from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from pipeline.engineering_compatibility_gate import validate_semantics


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "engineering_compatibility.schema.json"
CONFIG = ROOT / "datacenter" / "ENGINEERING_COMPATIBILITY_CONFIG.json"
EXAMPLE = ROOT / "datasheet" / "projects" / "example-project.json"
WORKFLOW = ROOT / ".github" / "workflows" / "engineering-compatibility-visualize.yml"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_example_project_is_permanent_positive_regression_case() -> None:
    """Option 1: the repository must always contain a known-good PASS datasheet."""
    assert EXAMPLE.exists(), "Permanent positive example datasheet is missing"

    schema = load_json(SCHEMA)
    config = load_json(CONFIG)
    data = load_json(EXAMPLE)

    schema_errors = list(Draft202012Validator(schema).iter_errors(data))
    assert schema_errors == [], [error.message for error in schema_errors]

    semantic_errors = validate_semantics(data, config)
    assert semantic_errors == []
    assert data["release_gate"] == "PASS"
    assert data["visualization"]["model"] == "VISUALIZE_GOLDEN_RULE_v1_0"
    assert data["visualization"]["complete_not_summary"] is True


def test_workflow_keeps_no_project_datasheet_protection() -> None:
    """Option 2: an empty project directory must remain a non-failing condition."""
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "shopt -s nullglob globstar" in workflow
    assert "files=(datasheet/projects/**/*.json)" in workflow
    assert "if [ ${#files[@]} -eq 0 ]; then" in workflow
    assert "No project compatibility datasheets found; semantic gate skipped." in workflow
    assert "exit 0" in workflow
