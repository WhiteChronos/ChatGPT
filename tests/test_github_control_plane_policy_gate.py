from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
POLICY = REPO / "governance" / "GITHUB_CONTROL_PLANE_POLICY.json"
GATE = REPO / "pipeline" / "github_control_plane_policy_gate.py"


def _load_gate():
    spec = importlib.util.spec_from_file_location("github_control_plane_policy_gate", GATE)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GitHub control-plane policy gate")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _desired_policy() -> dict:
    return {
        "schema_version": "whitechronos-github-control-plane/v1",
        "ruleset": {
            "id": 21770911,
            "name": "Chronos",
            "target": "branch",
            "enforcement": "active",
        },
        "protected_refs": [
            "~DEFAULT_BRANCH",
            "refs/heads/spec/**",
            "refs/heads/release/**",
        ],
        "excluded_refs": [],
        "bypass_actors": [],
        "review_mode": "solo",
        "pull_request": {
            "required_approving_review_count": 0,
            "require_code_owner_review": False,
            "require_last_push_approval": False,
            "required_review_thread_resolution": True,
            "dismiss_stale_reviews_on_push": False,
            "allowed_merge_methods": ["squash", "rebase"],
        },
        "required_status_checks": ["github-control-plane-policy"],
        "desired_rules": [
            "deletion",
            "non_fast_forward",
            "required_linear_history",
            "pull_request",
            "required_status_checks",
        ],
        "forbidden_rules": [
            "creation",
            "update",
            "required_signatures",
            "required_deployments",
        ],
    }


def _live_from_policy(policy: dict) -> dict:
    return {
        "id": policy["ruleset"]["id"],
        "name": policy["ruleset"]["name"],
        "target": policy["ruleset"]["target"],
        "enforcement": policy["ruleset"]["enforcement"],
        "conditions": {
            "ref_name": {
                "include": list(policy["protected_refs"]),
                "exclude": list(policy["excluded_refs"]),
            }
        },
        "bypass_actors": list(policy["bypass_actors"]),
        "rules": [
            {"type": "deletion"},
            {"type": "non_fast_forward"},
            {"type": "required_linear_history"},
            {
                "type": "pull_request",
                "parameters": dict(policy["pull_request"]),
            },
            {
                "type": "required_status_checks",
                "parameters": {
                    "strict_required_status_checks_policy": True,
                    "do_not_enforce_on_create": True,
                    "required_status_checks": [
                        {"context": context}
                        for context in policy["required_status_checks"]
                    ],
                },
            },
        ],
    }


def test_policy_pins_phase1_chronos_state():
    gate = _load_gate()
    policy = gate.load_policy(POLICY)
    assert policy["ruleset"]["id"] == 21770911
    assert policy["ruleset"]["name"] == "Chronos"
    assert policy["ruleset"]["target"] == "branch"
    assert policy["ruleset"]["enforcement"] == "active"
    assert policy["protected_refs"] == [
        "~DEFAULT_BRANCH",
        "refs/heads/spec/**",
        "refs/heads/release/**",
    ]
    assert policy["review_mode"] == "solo"


def test_policy_forbids_lockout_rules_in_phase1():
    gate = _load_gate()
    policy = gate.load_policy(POLICY)
    assert gate.validate_policy(policy) == []
    assert set(policy["forbidden_rules"]) == {
        "creation",
        "update",
        "required_signatures",
        "required_deployments",
    }


def test_policy_requires_only_existing_slice_check():
    gate = _load_gate()
    policy = gate.load_policy(POLICY)
    assert policy["required_status_checks"] == ["github-control-plane-policy"]


@pytest.mark.parametrize(
    ("mutator", "expected"),
    [
        (lambda p: p.update(protected_refs=[]), "protected_refs"),
        (
            lambda p: p.update(protected_refs=["~ALL"]),
            "~ALL",
        ),
        (
            lambda p: p.update(
                protected_refs=[
                    "~DEFAULT_BRANCH",
                    "refs/heads/spec/**",
                    "refs/heads/spec/**",
                    "refs/heads/release/**",
                ]
            ),
            "duplicate protected ref",
        ),
        (
            lambda p: p.update(
                protected_refs=[
                    "refs/heads/spec/**",
                    "refs/heads/release/**",
                ]
            ),
            "~DEFAULT_BRANCH",
        ),
        (
            lambda p: p["pull_request"].update(
                required_approving_review_count=1
            ),
            "required_approving_review_count",
        ),
        (
            lambda p: p["pull_request"].update(
                require_code_owner_review=True
            ),
            "require_code_owner_review",
        ),
        (
            lambda p: p["pull_request"].update(
                require_last_push_approval=True
            ),
            "require_last_push_approval",
        ),
        (
            lambda p: p["pull_request"]["allowed_merge_methods"].append("merge"),
            "merge",
        ),
        (
            lambda p: p.update(required_status_checks=[]),
            "github-control-plane-policy",
        ),
        (
            lambda p: p["desired_rules"].append("required_signatures"),
            "forbidden rule",
        ),
    ],
)
def test_static_policy_rejects_unsafe_phase1_variants(mutator, expected):
    gate = _load_gate()
    policy = _desired_policy()
    mutator(policy)
    errors = gate.validate_policy(policy)
    assert errors
    assert any(expected in error for error in errors)


def test_live_ruleset_matching_policy_passes():
    gate = _load_gate()
    policy = _desired_policy()
    assert gate.verify_live_ruleset(policy, _live_from_policy(policy)) == []


def test_live_ruleset_disabled_is_failure():
    gate = _load_gate()
    policy = _desired_policy()
    live = _live_from_policy(policy)
    live["enforcement"] = "disabled"
    errors = gate.verify_live_ruleset(policy, live)
    assert any("enforcement" in error and "disabled" in error for error in errors)


def test_live_ruleset_empty_ref_include_is_failure():
    gate = _load_gate()
    policy = _desired_policy()
    live = _live_from_policy(policy)
    live["conditions"]["ref_name"]["include"] = []
    errors = gate.verify_live_ruleset(policy, live)
    assert any("protected refs" in error for error in errors)


@pytest.mark.parametrize(
    "rule_type",
    ("creation", "update", "required_signatures", "required_deployments"),
)
def test_live_ruleset_forbidden_or_deferred_rule_is_failure(rule_type):
    gate = _load_gate()
    policy = _desired_policy()
    live = _live_from_policy(policy)
    live["rules"].append({"type": rule_type})
    errors = gate.verify_live_ruleset(policy, live)
    assert any(rule_type in error for error in errors)


def test_live_ruleset_missing_policy_check_is_failure():
    gate = _load_gate()
    policy = _desired_policy()
    live = _live_from_policy(policy)
    status_rule = next(
        rule for rule in live["rules"] if rule["type"] == "required_status_checks"
    )
    status_rule["parameters"]["required_status_checks"] = []
    errors = gate.verify_live_ruleset(policy, live)
    assert any("github-control-plane-policy" in error for error in errors)


def test_policy_file_round_trips_as_json():
    data = json.loads(POLICY.read_text(encoding="utf-8"))
    assert data["schema_version"] == "whitechronos-github-control-plane/v1"



def test_github_control_plane_workflow_contract():
    workflow = REPO / ".github" / "workflows" / "github-control-plane-policy.yml"
    text = workflow.read_text(encoding="utf-8")

    assert "name: GitHub Control Plane Policy" in text
    assert "github-control-plane-policy:" in text
    assert "name: github-control-plane-policy" in text
    assert "pull_request:" in text
    assert "- main" in text
    assert '- "spec/**"' in text
    assert '- "release/**"' in text
    assert "workflow_dispatch:" in text
    assert "permissions:" in text
    assert "contents: read" in text
    assert 'python-version: "3.11"' in text
    assert (
        "python pipeline/github_control_plane_policy_gate.py "
        "--policy governance/GITHUB_CONTROL_PLANE_POLICY.json"
    ) in text
    assert "python -m pytest -q tests/test_github_control_plane_policy_gate.py" in text
    assert "python -m pytest -q tests/test_github_path_policy.py" in text
    assert "python pipeline/github_path_policy.py" in text

    assert "\n    paths:" not in text
    for forbidden in (
        "pull_request_target:",
        "contents: write",
        "actions: write",
        "OPENAI_API_KEY",
        "CODEX_ACCESS_TOKEN",
        "git push",
    ):
        assert forbidden not in text


def test_agents_requires_github_control_plane_validation_commands():
    text = (REPO / "AGENTS.md").read_text(encoding="utf-8")
    assert "## GitHub Control Plane merge gate" in text
    assert (
        "python pipeline/github_control_plane_policy_gate.py "
        "--policy governance/GITHUB_CONTROL_PLANE_POLICY.json"
    ) in text
    assert "python -m pytest -q tests/test_github_control_plane_policy_gate.py" in text
    assert "python -m pytest -q tests/test_github_path_policy.py" in text
    assert "live ruleset verification" in text.lower()



def test_chronos_admin_runbook_contract():
    path = REPO / "docs" / "github-control-plane-admin.md"
    text = path.read_text(encoding="utf-8")

    for required in (
        "21770911",
        "enforcement: disabled",
        "~DEFAULT_BRANCH",
        "refs/heads/spec/**",
        "refs/heads/release/**",
        "creation",
        "update",
        "required_signatures",
        "required_deployments",
        "required_approving_review_count: 0",
        "require_code_owner_review: false",
        "require_last_push_approval: false",
        "required_review_thread_resolution: true",
        "github-control-plane-policy",
        "Rollback",
        "rulesets/21770911",
        "--require-live",
        "PR #57",
        "DRAFT",
    ):
        assert required in text

    assert "do not add a broad bypass" in text.lower()
    assert "feat/cloud-runtime-foundation" in text
    assert "spec/whitechronos-cloud-control-plane" in text
