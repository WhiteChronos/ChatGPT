from __future__ import annotations

import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
POLICY = REPO / "governance" / "GITHUB_CONTROL_PLANE_POLICY.json"
GATE = REPO / "pipeline" / "github_control_plane_policy_gate.py"
PATH_POLICY = REPO / "pipeline" / "github_path_policy.py"
WORKFLOW = REPO / ".github" / "workflows" / "github-control-plane-policy.yml"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_desired_chronos_policy_is_valid():
    gate = _load(GATE, "github_control_plane_policy_gate")
    policy = gate.load_policy(POLICY)
    assert gate.validate_policy(policy) == []
    assert policy["ruleset"]["id"] == 21770911
    assert policy["ruleset"]["enforcement"] == "active"
    assert policy["required_status_checks"] == ["github-control-plane-policy"]


def test_required_check_workflow_is_always_present_for_protected_prs():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "name: GitHub Control Plane Policy" in text
    assert "github-control-plane-policy:" in text
    assert "name: github-control-plane-policy" in text
    assert "pull_request:" in text
    assert "- main" in text
    assert '- "spec/**"' in text
    assert '- "release/**"' in text
    assert "\n    paths:" not in text
    assert "pull_request_target:" not in text
    assert "contents: write" not in text
    assert "git push" not in text
    assert "actions/checkout@v4" not in text
    assert "actions/setup-python@v5" not in text
    assert "actions/checkout@11d5960a326750d5838078e36cf38b85af677262" in text
    # Dependabot may propose either audited immutable pin during the v5 -> v7 upgrade.\n    # Keep SHA pinning mandatory; do not accept mutable tags or arbitrary SHAs.\n    allowed_setup_python_pins = (\n        "actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065",  # v5\n        "actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97",  # v7.0.0\n    )\n    assert sum(pin in text for pin in allowed_setup_python_pins) == 1


def test_path_classifier_covers_control_and_runtime_surfaces():
    module = _load(PATH_POLICY, "github_path_policy")
    assert module.classify_path(".github/workflows/x.yml") == "CONTROL_PLANE_CRITICAL"
    assert module.classify_path("pipeline/x.py") == "CONTROL_PLANE_CRITICAL"
    assert module.classify_path("plugins/subagent-broker/x.mjs") == "RUNTIME_CONTROL"
    assert module.classify_path("registry/capabilities/x.json") == "DURABLE_STATE"
    assert module.classify_path("docs/x.md") == "DOCUMENTATION"
