"""Fail-closed CI regression guard for historical six failures.

This verifies coverage of parser/import and JSON boolean/parity regressions,
without triggering GitLab, mirroring a ref or reading any credentials.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/trusted-gitlab-ci-preflight.yml"

def test_secretless_preflight_executes_historical_regressions():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    for path in (
        "tests/test_git_mirror_parity.py",
        "tests/test_ci_provider_evidence.py",
        "tests/test_gitlab_pipeline_contract.py",
        "tests/test_trusted_gitlab_ci_gate.py",
        "tests/test_ci_regression_preflight_contract.py",
    ):
        assert path in workflow, f"preflight omits regression suite: {path}"
    assert "python -m pytest -q" in workflow

def test_secretless_preflight_installs_minimal_test_dependencies():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "pytest==8.4.1" in workflow
    assert "jsonschema==4.25.1" in workflow
    assert "PyYAML==6.0.2" in workflow

def test_emergency_gate_cannot_dispatch_live_or_access_credentials():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "persist-credentials: false" in workflow
    assert "contents: read" in workflow
    assert "workflow_dispatch:" not in workflow
    assert "secrets." not in workflow
    assert "GITLAB_MIRROR_TOKEN" not in workflow
    assert "GITLAB_MIRROR_SIGNING_KEY" not in workflow
    assert "git push" not in workflow
    assert "environment:" not in workflow

def test_original_root_causes_remain_rejected():
    module = (ROOT / "pipeline/git_mirror_parity.py").read_text(encoding="utf-8")
    evidence = (ROOT / "pipeline/ci_provider_evidence.py").read_text(encoding="utf-8")
    test_evidence = (ROOT / "tests/test_ci_provider_evidence.py").read_text(encoding="utf-8")
    assert "github_available=_require_json_bool(" in module
    assert "gitlab_available=_require_json_bool(" in module
    assert "from pathlib import Path" in evidence
    assert "from pathlib import Path" in test_evidence
    pipeline = (ROOT / ".gitlab-ci.yml").read_text(encoding="utf-8")
    assert "compare_provider_evidence(" in pipeline
    assert '"github_repository": "WhiteChronos/ChatGPT"' in pipeline
