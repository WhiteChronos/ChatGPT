from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PLUGIN = REPO / "plugins" / "whitechronos-control-plane"
CLI = PLUGIN / "scripts" / "runtime_doctor.py"
SKILL = PLUGIN / "skills" / "codex-runtime-doctor" / "SKILL.md"
RUNBOOK = REPO / "docs" / "runbooks" / "codex-subagent-runtime.md"

EXISTING_PLUGINS = {
    "github-arena@whitechronos-repo",
    "superpowers@openai-curated",
    "superpowers-controller@whitechronos-repo",
    "matt-pocock-controller@whitechronos-repo",
    "ecc@whitechronos-repo",
    "ecc-controller@whitechronos-repo",
    "subagent-broker@whitechronos-repo",
    "awesome-llm-apps-controller@whitechronos-repo",
}


def _fixture_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    shutil.copytree(REPO / "registry", repo / "registry")
    for rel in [
        ".codex/config.toml", ".agents/plugins/marketplace.json",
        "plugins/github-arena/.mcp.json", "plugins/github-arena/.codex-plugin/plugin.json",
        "plugins/github-arena/mcp-server/mcp_server.mjs",
        "plugins/subagent-broker/.mcp.json", "plugins/subagent-broker/.codex-plugin/plugin.json",
        "plugins/subagent-broker/tests/fake-codex.mjs",
    ]:
        src = REPO / rel; dst = repo / rel; dst.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(src, dst)
    shutil.copytree(REPO / "plugins/subagent-broker/mcp-server", repo / "plugins/subagent-broker/mcp-server")
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "cli@test"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "CLI Test"], cwd=repo, check=True)
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "fixture"], cwd=repo, check=True)
    return repo


def test_marketplace_registers_whitechronos_control_plane():
    data = json.loads((REPO / ".agents/plugins/marketplace.json").read_text())
    item = next(p for p in data["plugins"] if p["name"] == "whitechronos-control-plane")
    assert item["source"] == {"source": "local", "path": "./plugins/whitechronos-control-plane"}
    assert item["policy"]["installation"] == "INSTALLED_BY_DEFAULT"
    assert item["policy"]["products"] == ["CODEX"]


def test_codex_config_enables_control_plane_without_changing_existing_layers():
    with (REPO / ".codex/config.toml").open("rb") as f:
        cfg = tomllib.load(f)
    assert EXISTING_PLUGINS <= set(cfg["plugins"])
    assert cfg["agents"]["enabled"] is True
    assert cfg["features"]["multi_agent"] is True
    assert cfg["plugins"]["whitechronos-control-plane@whitechronos-repo"]["enabled"] is True


def test_plugin_manifest_exposes_runtime_doctor_skill_only_in_this_slice():
    manifest = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text())
    assert manifest["name"] == "whitechronos-control-plane"
    assert manifest["version"] == "0.1.0"
    assert manifest["skills"] == "./skills/"
    assert "mcpServers" not in manifest
    assert sorted(p.name for p in (PLUGIN / "skills").iterdir() if p.is_dir()) == ["codex-runtime-doctor"]


def test_agents_md_requires_runtime_doctor_for_runtime_claims():
    text = (REPO / "AGENTS.md").read_text()
    assert "Runtime Doctor" in text
    assert "config alone" in text.lower()
    assert "HOST_RELOAD_REQUIRED" in text
    assert "must not trigger code changes" in text


def test_skill_forbids_config_only_success_claims():
    text = SKILL.read_text()
    assert "CONFIGURED" in text
    assert "LOCAL_RUNTIME_HEALTHY" in text
    assert "HOST_DISCOVERED" in text
    assert "LIVE_VERIFIED" in text
    assert "Never treat repository configuration as runtime proof" in text


def test_skill_routes_host_reload_without_source_changes():
    text = SKILL.read_text()
    assert "HOST_RELOAD_REQUIRED" in text
    assert "fresh Codex" in text
    assert "do not change source" in text.lower()


def test_cli_json_diagnostic_succeeds_without_host_inventory(tmp_path):
    repo = _fixture_repo(tmp_path)
    fake = repo / "plugins/subagent-broker/tests/fake-codex.mjs"
    completed = subprocess.run([sys.executable, str(CLI), "--repo", str(repo), "--codex-path", str(fake), "--json"], text=True, capture_output=True)
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["live_smoke_ready"] is False
    statuses = {item["name"]: item["status"] for item in payload["checks"]}
    assert statuses["HOST_BROKER_DISCOVERY"] == "UNAVAILABLE"


def test_cli_strict_readiness_returns_two_when_host_reload_is_required(tmp_path):
    repo = _fixture_repo(tmp_path)
    fake = repo / "plugins/subagent-broker/tests/fake-codex.mjs"
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    completed = subprocess.run([
        sys.executable, str(CLI), "--repo", str(repo), "--codex-path", str(fake),
        "--runtime-kind", "trusted_remote", "--expected-commit", head,
        "--host-tool", "unrelated_tool", "--require-live-smoke-ready"
    ], text=True, capture_output=True)
    assert completed.returncode == 2, completed.stderr
    assert "fresh Codex" in completed.stdout


def test_runtime_foundation_workflow_runs_local_suite_but_not_live_smoke():
    workflow = REPO / ".github/workflows/whitechronos-runtime-foundation.yml"
    text = workflow.read_text()
    assert "python -m pytest -q plugins/whitechronos-control-plane/tests" in text
    assert "SUBAGENT_BROKER_LIVE=1" not in text
    assert "smoke_real_codex.mjs" not in text


def test_cli_can_mark_an_observed_empty_host_inventory(tmp_path):
    repo = _fixture_repo(tmp_path)
    fake = repo / "plugins/subagent-broker/tests/fake-codex.mjs"
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    completed = subprocess.run([
        sys.executable, str(CLI), "--repo", str(repo), "--codex-path", str(fake),
        "--runtime-kind", "trusted_remote", "--expected-commit", head,
        "--host-inventory-observed", "--require-live-smoke-ready"
    ], text=True, capture_output=True)
    assert completed.returncode == 2, completed.stderr
    assert "fresh Codex" in completed.stdout


def test_runtime_foundation_workflow_runs_full_repository_regression():
    workflow = REPO / ".github/workflows/whitechronos-runtime-foundation.yml"
    lines = workflow.read_text().splitlines()
    assert any(line.strip() == "run: python -m pytest -q" for line in lines)


def test_runtime_foundation_workflow_runs_doctor_in_clean_detached_worktree():
    workflow = (REPO / ".github/workflows/whitechronos-runtime-foundation.yml").read_text()
    assert 'git worktree add --detach /tmp/whitechronos-runtime-doctor-tree "$GITHUB_SHA"' in workflow
    assert '--repo /tmp/whitechronos-runtime-doctor-tree' in workflow


def test_runbook_uses_supported_local_plugin_reinstall_flow():
    text = RUNBOOK.read_text()
    assert "codex plugin marketplace upgrade whitechronos-repo" not in text
    assert "codex plugin remove subagent-broker@whitechronos-repo" in text
    assert "codex plugin add subagent-broker@whitechronos-repo" in text


def test_runbook_runtime_doctor_example_supplies_observed_native_host_tools():
    text = RUNBOOK.read_text()
    for tool in (
        "spawn_agent",
        "send_message",
        "followup_task",
        "wait_agent",
        "interrupt_agent",
        "list_agents",
    ):
        assert f"--host-tool {tool}" in text


def test_runbook_documents_current_v1_and_v2_native_contracts():
    text = RUNBOOK.read_text()
    assert "features.multi_agent" in text
    assert "Stable" in text
    assert "V1" in text
    assert "send_input" in text
    assert "resume_agent" in text
    assert "close_agent" in text
    assert "V2" in text
    assert "send_message" in text
    assert "followup_task" in text
    assert "interrupt_agent" in text
    assert "list_agents" in text
    assert "legacy setting below is forbidden" not in text


NEUTRAL_WORKFLOW = REPO / ".github" / "workflows" / "gitlab-neutral-mirror.yml"


def _neutral_workflow_text() -> str:
    assert NEUTRAL_WORKFLOW.is_file(), "trusted neutral mirror workflow missing"
    return NEUTRAL_WORKFLOW.read_text(encoding="utf-8")


def test_neutral_mirror_workflow_is_manual_only_with_required_subject_inputs():
    text = _neutral_workflow_text()
    assert "workflow_dispatch:" in text
    assert "subject_ref:" in text and "subject_sha:" in text
    assert text.count("required: true") >= 2
    assert "pull_request:" not in text
    assert "\n  push:" not in text
    assert "workflow_run:" not in text


def test_neutral_mirror_workflow_is_read_only_and_environment_gated():
    text = _neutral_workflow_text()
    assert "permissions:" in text
    assert "contents: read" in text
    assert "environment: gitlab-neutral-mirror" in text
    assert "github.ref == 'refs/heads/main'" in text
    assert "refs/heads/main" in text
    assert "group: gitlab-neutral-mirror-${{ inputs.subject_ref }}" in text
    assert "cancel-in-progress: false" in text


def test_neutral_mirror_workflow_pins_all_external_actions():
    text = _neutral_workflow_text()
    assert "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1" in text
    assert "actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97" in text
    assert "actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9" in text
    for line in text.splitlines():
        if "uses: actions/" in line:
            assert "@v" not in line


def test_neutral_mirror_workflow_treats_subject_sha_as_data_not_checkout_code():
    text = _neutral_workflow_text()
    assert "ref: ${{ github.sha }}" in text
    assert "ref: ${{ inputs.subject_sha }}" not in text
    assert "ref: ${{ inputs.subject_ref }}" not in text
    assert "--subject-sha \"$SUBJECT_SHA\"" in text
    assert "--worker-revision \"$GITHUB_SHA\"" in text


def test_neutral_mirror_secret_is_step_scoped_and_never_passed_as_argument():
    text = _neutral_workflow_text()
    assert text.count("secrets.GITLAB_MIRROR_TOKEN") == 1
    assert "GITLAB_MIRROR_TOKEN: ${{ secrets.GITLAB_MIRROR_TOKEN }}" in text
    assert "--token" not in text
    assert "--password" not in text
    assert "github_neutral_mirror.py" in text
    assert "git push --force" not in text
    assert "gh pr merge" not in text
    assert "deploy" not in text.lower()


def test_gitlab_pipeline_contract_binds_trusted_worker_revision():
    pipeline = (REPO / ".gitlab-ci.yml").read_text(encoding="utf-8")
    assert "mirror_worker_revision:" in pipeline
    assert "WHITECHRONOS_MIRROR_WORKER_REVISION" in pipeline
    assert '"worker_revision": receipt["worker_revision"]' in pipeline


def test_provider_evidence_schema_binds_trusted_worker_revision():
    schema = json.loads((REPO / "schemas" / "ci_provider_evidence.schema.json").read_text())
    assert "worker_revision" in schema["required"]
    assert schema["properties"]["worker_revision"]["pattern"] == "^[0-9a-fA-F]{40}$"
    evidence_module = (REPO / "pipeline" / "ci_provider_evidence.py").read_text()
    assert '"worker_revision"' in evidence_module


GITHUB_NEUTRAL_MIRROR_RUNBOOK = REPO / "docs" / "runbooks" / "github-neutral-mirror.md"
GITLAB_CONTINGENCY_RUNBOOK = REPO / "docs" / "runbooks" / "gitlab-contingency-ci.md"


def test_github_neutral_mirror_runbook_documents_trust_bootstrap_and_credential_scope():
    assert GITHUB_NEUTRAL_MIRROR_RUNBOOK.is_file(), "GitHub neutral mirror runbook missing"
    text = GITHUB_NEUTRAL_MIRROR_RUNBOOK.read_text(encoding="utf-8")
    for required in (
        "gitlab-neutral-mirror",
        "GITLAB_MIRROR_TOKEN",
        "write_repository",
        "protected trusted ref",
        "deployment branch",
        "subject_ref",
        "subject_sha",
        "workflow_dispatch",
    ):
        assert required in text


def test_github_neutral_mirror_runbook_rejects_broad_or_non_triggering_credentials():
    text = GITHUB_NEUTRAL_MIRROR_RUNBOOK.read_text(encoding="utf-8")
    assert "CI_JOB_TOKEN" in text
    assert "does not trigger" in text
    assert "deploy token" in text.lower()
    assert "read_repository" in text
    assert "do not broaden" in text.lower()
    assert " api " in text.lower() or "`api`" in text.lower()


def test_github_neutral_mirror_runbook_documents_rotation_recovery_and_no_shortcuts():
    text = GITHUB_NEUTRAL_MIRROR_RUNBOOK.read_text(encoding="utf-8").lower()
    for required in (
        "rotate",
        "revoke",
        "same-sha",
        "whitechronos-refresh/",
        "force-push",
        "api commit",
        "mirror_parity=healthy",
    ):
        assert required in text


def test_gitlab_contingency_runbook_routes_final_transport_through_trusted_github_worker():
    text = GITLAB_CONTINGENCY_RUNBOOK.read_text(encoding="utf-8")
    assert "GitHub Actions Neutral Mirror" in text
    assert "gitlab-neutral-mirror.yml" in text
    assert "mirror_worker_revision" in text
    assert "source=push" in text
    assert "CI_JOB_TOKEN" in text


def test_github_neutral_mirror_runbook_records_reviewed_action_pins():
    text = GITHUB_NEUTRAL_MIRROR_RUNBOOK.read_text(encoding="utf-8")
    for sha in (
        "3d3c42e5aac5ba805825da76410c181273ba90b1",
        "5fda3b95a4ea91299a34e894583c3862153e4b97",
        "cf430e030ddbb5b0abf93d22962f4752f3646cd9",
    ):
        assert sha in text
    assert "separate review before updating" in text
