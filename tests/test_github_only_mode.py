"""GitHub is the only active repository, issue tracker and CI authority."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REMOVED_LEGACY_PATHS = (
    ".gitlab-ci.yml",
    "governance/GITLAB_CONTINGENCY_CI_POLICY.json",
    "schemas/gitlab_contingency_ci.schema.json",
    "schemas/ci_provider_evidence.schema.json",
    "pipeline/gitlab_contingency_policy.py",
    "pipeline/git_mirror_parity.py",
    "pipeline/git_mirror_observation.py",
    "pipeline/contingency_ci_gate.py",
    "pipeline/ci_provider_evidence.py",
    "plugins/whitechronos-control-plane/scripts/sync_gitlab_mirror.py",
    "plugins/whitechronos-control-plane/tests/test_gitlab_mirror_sync.py",
    "requirements-mirror.txt",
    "tests/test_gitlab_contingency_policy.py",
    "tests/test_gitlab_pipeline_contract.py",
    "tests/test_git_mirror_parity.py",
    "tests/test_git_mirror_observation.py",
    "tests/test_contingency_ci_gate.py",
    "tests/test_ci_provider_evidence.py",
    ".agents/skills/setup-matt-pocock-skills/issue-tracker-gitlab.md",
    "docs/runbooks/gitlab-contingency-ci.md",
    "docs/runbooks/gitlab-contingency-drill.md",
    "docs/superpowers/reviews/2026-10-05-whitechronos-gitlab-contingency-ci-review.md",
)


def test_legacy_provider_files_are_absent_from_active_tree():
    for relative in REMOVED_LEGACY_PATHS:
        assert not (ROOT / relative).exists(), f"retired provider file still in tree: {relative}"


def test_github_policy_and_required_workflow_are_preserved():
    import json
    policy = json.loads((ROOT / "governance/GITHUB_CONTROL_PLANE_POLICY.json").read_text(encoding="utf-8"))
    assert policy["ruleset"]["enforcement"] == "active"
    assert "github-control-plane-policy" in policy["required_status_checks"]
    assert (ROOT / ".github/workflows/github-control-plane-policy.yml").is_file()


def test_deks_pages_is_not_autodeployed_from_legacy_doc_removal():
    workflow = (ROOT / ".github/workflows/deks-pages.yml").read_text(encoding="utf-8")
    assert "on:\n  workflow_dispatch:" in workflow
    assert "  push:" not in workflow
    assert "actions/deploy-pages@" in workflow  # still manual and separately authorized


def test_first_party_runtime_does_not_refer_to_retired_provider():
    paths = [
        ROOT / "runbooks/github-only-ci.md",
        ROOT / "plugins/whitechronos-control-plane/README.md",
        ROOT / "docs/runbooks/codex-subagent-runtime.md",
        ROOT / ".agents/skills/setup-matt-pocock-skills/SKILL.md",
        ROOT / ".agents/skills/code-review/SKILL.md",
    ]
    for path in paths:
        assert path.is_file()
        assert "gitlab" not in path.read_text(encoding="utf-8").lower(), path
