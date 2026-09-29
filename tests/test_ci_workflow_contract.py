"""Contrato dos workflows de governança v4.7."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINEERING = ROOT / ".github" / "workflows" / "engineering-governance.yml"
DOCUMENT = ROOT / ".github" / "workflows" / "document-governance.yml"
DISCOVERY = ROOT / ".github" / "workflows" / "document-tooling-discovery.yml"


def test_workflows_exist():
    for path in (ENGINEERING, DOCUMENT, DISCOVERY):
        assert path.exists(), f"Workflow ausente: {path}"


def test_engineering_workflow_keeps_ci_contract():
    text = ENGINEERING.read_text(encoding="utf-8")
    assert 'PYTHONPATH: ${{ github.workspace }}' in text
    assert "Verify CI environment contract" in text
    assert "Run full regression suite" in text
    assert "PROMPT_MESTRE_AUTOMACAO_v4_7.md" in text
    assert "MD_AUTOMATION_STANDARD_v1_0.md" in text
    assert "PROMPT_MESTRE_MD_AUTOMACAO_v1_0.md" in text
    assert "LI_IO_STANDARD_v1_0.md" in text
    assert "plugins/document_tooling_registry.json" in text


def test_document_workflow_enforces_li_io_and_md_assets():
    text = DOCUMENT.read_text(encoding="utf-8")
    required = [
        "datacenter/LI_IO_STANDARD.json",
        "datasheet/LI_IO_DATA_SHEET.json",
        "pipeline/li_io_standard.py",
        "pipeline/apply_li_io_text_patch.py",
        "pipeline/xlsx_layout_guard.py",
        "datacenter/MD_AUTOMATION_STANDARD.json",
        "datasheet/MD_AUTOMATION_DATA_SHEET.json",
        "pipeline/md_revision_standard.py",
        "MD_AUTOMATION_PETROBRAS_V1_0",
        "BLOCK_ON_ANY_FAILURE",
    ]
    for item in required:
        assert item in text


def test_tool_discovery_is_scheduled_and_never_installs_candidates():
    text = DISCOVERY.read_text(encoding="utf-8")
    assert "schedule:" in text
    assert "audit_document_plugins" in text
    assert "pip install" not in text


CANDIDATE_AUT_PANEL = ROOT / ".github" / "workflows" / "aut-panel-candidate-engineering.yml"


def test_candidate_workflow_is_read_only_and_has_no_unsafe_pr_trigger():
    assert CANDIDATE_AUT_PANEL.exists()
    text = CANDIDATE_AUT_PANEL.read_text(encoding="utf-8")
    assert "permissions:\n  contents: read" in text
    assert "pull_request_target" not in text
    for forbidden in ["gh pr merge", "merge_pull_request", "PLC_PRODUCTION_DOWNLOAD", "FABRICATION_RELEASE"]:
        assert forbidden not in text


def test_candidate_workflow_executes_candidate_gates_and_regression():
    text = CANDIDATE_AUT_PANEL.read_text(encoding="utf-8")
    required = [
        "python-version: '3.12'",
        "aut_panel_candidate_runner.py",
        "aut_panel_candidate_gate.py",
        "test_aut_panel_candidate_",
        "CANDIDATE_READY_FOR_HUMAN_REVIEW",
        "github.sha",
        "candidate_id",
    ]
    for token in required:
        assert token in text


LEARNING_AUT_PANEL = ROOT / ".github" / "workflows" / "aut-panel-learning.yml"


def test_learning_workflow_covers_all_auto_engineering_surfaces_and_r02_smoke():
    assert LEARNING_AUT_PANEL.exists()
    text = LEARNING_AUT_PANEL.read_text(encoding="utf-8")
    required = [
        "pipeline/aut_panel_candidate_revision.py",
        "pipeline/aut_panel_mem0.py",
        "pipeline/aut_panel_memory_context.py",
        "pipeline/aut_panel_memory_benchmark.py",
        "pipeline/aut_panel_memory_quality_gate.py",
        "pipeline/aut_panel_artifact_verifier.py",
        "tests/test_aut_panel_codex_contract.py",
        "tests/test_aut_panel_artifact_verifier.py",
        "sha256sum li/PN-AUT-01_LI.json",
        "historical LI changed",
    ]
    for token in required:
        assert token in text
