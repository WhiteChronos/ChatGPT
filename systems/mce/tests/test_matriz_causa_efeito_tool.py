"""Real MCE pre-analysis integration tests using synthetic documents only."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest
from openpyxl import Workbook

ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = ROOT / "scripts" / "matriz_causa_efeito_tool.py"
WORKFLOW = ROOT / ".agents" / "skills" / "engenharia-mce-projeto" / "scripts" / "mce_workflow.py"
MEMORY = ROOT / "scripts" / "mce_memory.py"
SPEC = importlib.util.spec_from_file_location("matriz_tool_test", TOOL_PATH)
tool = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tool)


def cli(script: Path, *args, expected=0):
    p = subprocess.run([sys.executable, str(script), *map(str, args)],
                       capture_output=True, text=True, timeout=60)
    assert p.returncode == expected, (p.stdout, p.stderr)
    return p


def setup(tmp_path: Path, *, all_three=True, with_io=False):
    wb = Workbook()
    wb.active.title = "CONTROLE"
    wb.active["A1"] = "MODELO DE TESTE NAO APROVADO"
    master = tmp_path / "modelo.xlsx"
    wb.save(master)
    azure = tmp_path / "export-azure.json"
    azure.write_text(json.dumps({"assets": [
        {"id": "v1", "label": "valve", "text_associated": "XV-101", "connections": [{"id": "p1"}]},
        {"id": "p1", "label": "pump", "text_associated": "P-101", "connections": []}]}), encoding="utf-8")
    houston = tmp_path / "houston.csv"
    houston.write_text('filename,consolidated_text\n"pid-sheet-1","=HYPERLINK(1)"\n', encoding="utf-8")
    industrial = tmp_path / "industrial.json"
    industrial.write_text(json.dumps({"causes": ["C1"], "effects": ["E1", "E2"],
                                      "interlock_matrix": {"C1": ["E1"]}}), encoding="utf-8")
    io = tmp_path / "io.csv"
    io.write_text("tag\nXV-101\nPT-555\n", encoding="utf-8")
    sources = [azure, houston, industrial] + ([io] if with_io else [])
    workspace = tmp_path / "workspace"
    cli(WORKFLOW, "init", "--workspace", workspace, "--master", master,
        "--sources", *sources)
    rows = [
        {"adapter": "azure", "source_name": azure.name,
         "document": "PI-001", "revision": "R00", "location": "sheet 1"},
        {"adapter": "houston", "source_name": houston.name,
         "document": "PI-001", "revision": "R00", "location": "sheet 1"},
        {"adapter": "industrial", "source_name": industrial.name,
         "document": "REF-EXAMPLE", "revision": "R00", "location": "educational sample"},
    ]
    if not all_three:
        rows = rows[:1]
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"schema": tool.FORMAT, "run_id": "R001",
                                    "sources": rows, "io_source_name": io.name if with_io else None}),
                        encoding="utf-8")
    db = tmp_path / "mce.sqlite3"
    cli(MEMORY, "--db", db, "init")
    return workspace, manifest, db, master


def test_github_adapter_contract_exact_and_rea_independent():
    assert set(tool.ALLOWED) == {"azure", "houston", "industrial"}
    assert all("/" in v for v in tool.ALLOWED.values())
    assert "systems/rea" not in TOOL_PATH.read_text(encoding="utf-8")
    assert "mce_memory" in TOOL_PATH.read_text(encoding="utf-8")


def test_plan_is_read_only_and_no_false_workflow_status(tmp_path):
    workspace, manifest, db, master = setup(tmp_path)
    result = cli(TOOL_PATH, "plan", "--workspace", workspace, "--manifest", manifest,
                 "--db", db)
    report = json.loads(result.stdout)
    assert report["status"] == "PRECHECK_PASS"
    assert report["adapters"] == ["azure", "houston", "industrial"]
    assert report["memory_verified"] is True
    assert not (workspace / "derived").exists()
    assert json.loads((workspace / "state.json").read_text())["status"] == "INVENTARIADO"
    assert hashlib.sha256(master.read_bytes()).hexdigest() == hashlib.sha256((workspace / "base" / "modelo.xlsx").read_bytes()).hexdigest()


def test_three_repositories_datasheet_memory_and_workflow_stops(tmp_path):
    workspace, manifest, db, master = setup(tmp_path, with_io=True)
    original_sha = hashlib.sha256(master.read_bytes()).hexdigest()
    result = cli(TOOL_PATH, "run", "--workspace", workspace, "--manifest", manifest,
                 "--db", db)
    status = json.loads(result.stdout)
    assert status["status"] == "PRE_ANALISE_PENDENTE_REVISAO"
    assert status["event_seq"] == 1 and status["human_review_required"]
    sheet = json.loads(Path(status["datasheet"]).read_text(encoding="utf-8"))
    assert sheet["schema"] == tool.SHEET_FORMAT
    assert sheet["product"] == "MCE_INDEPENDENTE"
    assert [x["adapter"] for x in sheet["sources"]] == ["azure", "houston", "industrial", "io_compare"]
    assert not sheet["missing_adapters"]
    assert sheet["cause_effect_relations_documented"] == 0
    assert sheet["cause_effect_relations_approved"] == 0
    assert sheet["matrix_edit_authorized"] is False
    assert sheet["production_complete"] is False
    assert not (workspace / "output" / "MCE_PRELIMINAR.xlsx").exists()
    assert hashlib.sha256(master.read_bytes()).hexdigest() == original_sha
    assert hashlib.sha256((workspace / "base" / "modelo.xlsx").read_bytes()).hexdigest() == original_sha
    state = json.loads((workspace / "state.json").read_text(encoding="utf-8"))
    assert state["status"] == "INVENTARIADO"
    assert len(state["pid_integrations"]) == 4
    assert all(not x["eligible_to_edit_matrix"] for x in state["pid_integrations"])
    history = json.loads(cli(MEMORY, "--db", db, "search", "--text", "MCE_TOOL_MATRIZ_CAUSA_EFEITO").stdout)
    assert len(history["matches"]) == 1 and history["matches"][0]["kind"] == "STATUS"
    analysis = tmp_path / "analysis.json"
    analysis.write_text(json.dumps({"project": "NAO IDENTIFICADO", "ss": "NAO IDENTIFICADA",
                                   "summary": "Synthetic test", "findings": [], "gaps": ["Not verified"]}))
    p = cli(WORKFLOW, "understand", "--workspace", workspace, "--analysis", analysis, expected=2)
    assert "revisao humana" in p.stderr.lower()


def test_missing_sources_are_explicit_not_invented(tmp_path):
    workspace, manifest, db, _ = setup(tmp_path, all_three=False)
    result = cli(TOOL_PATH, "run", "--workspace", workspace, "--manifest", manifest, "--db", db)
    ds = json.loads(Path(json.loads(result.stdout)["datasheet"]).read_text(encoding="utf-8"))
    assert ds["missing_adapters"] == ["houston", "industrial"]
    assert len(ds["sources"]) == 1
    assert ds["cause_effect_relations_approved"] == 0


def test_db_must_exist_before_any_write(tmp_path):
    workspace, manifest, db, _ = setup(tmp_path)
    db.unlink()
    r = cli(TOOL_PATH, "run", "--workspace", workspace, "--manifest", manifest, "--db", db, expected=2)
    assert json.loads(r.stdout)["status"] == "BLOCKED"
    assert not (workspace / "derived").exists()


def test_wrong_product_db_refused(tmp_path):
    import sqlite3
    workspace, manifest, db, _ = setup(tmp_path)
    with sqlite3.connect(db) as connection:
        connection.execute("UPDATE system_meta SET value='OTHER' WHERE key='product'")
    assert cli(TOOL_PATH, "run", "--workspace", workspace, "--manifest", manifest, "--db", db, expected=2)
    assert not (workspace / "derived").exists()


@pytest.mark.parametrize("field", ["adapter", "source_name", "document", "revision", "location"])
def test_invalid_sources_fail_closed(tmp_path, field):
    workspace, manifest, db, _ = setup(tmp_path)
    obj = json.loads(manifest.read_text())
    bad = {"adapter": "bad", "source_name": "../outside", "document": "", "revision": "", "location": ""}[field]
    obj["sources"][0][field] = bad
    manifest.write_text(json.dumps(obj))
    response = cli(TOOL_PATH, "run", "--workspace", workspace, "--manifest", manifest, "--db", db, expected=2)
    assert json.loads(response.stdout)["status"] == "BLOCKED"
    assert not (workspace / "derived").exists()


def test_duplicate_adapter_refused(tmp_path):
    workspace, manifest, db, _ = setup(tmp_path)
    obj = json.loads(manifest.read_text())
    obj["sources"][1]["adapter"] = "azure"
    manifest.write_text(json.dumps(obj))
    cli(TOOL_PATH, "run", "--workspace", workspace, "--manifest", manifest, "--db", db, expected=2)


def test_manifest_duplicate_fields_and_invalid_runid_refused(tmp_path):
    workspace, manifest, db, _ = setup(tmp_path)
    obj = json.loads(manifest.read_text())
    obj["run_id"] = "../../bad"
    manifest.write_text(json.dumps(obj))
    cli(TOOL_PATH, "run", "--workspace", workspace, "--manifest", manifest, "--db", db, expected=2)


def test_tampered_source_refused_before_write(tmp_path):
    workspace, manifest, db, _ = setup(tmp_path)
    (workspace / "sources" / "export-azure.json").write_text("{}", encoding="utf-8")
    cli(TOOL_PATH, "run", "--workspace", workspace, "--manifest", manifest, "--db", db, expected=2)
    assert not (workspace / "derived").exists()


def test_prevalidate_bad_industrial_mapping_does_not_write_state(tmp_path):
    workspace, manifest, db, _ = setup(tmp_path)
    source = workspace / "sources" / "industrial.json"
    source.write_text(json.dumps({"causes": ["C"], "effects": ["E"], "interlock_matrix": {"C": ["MISSING"]}}))
    # re-hash state to simulate a *properly inventoried* but semantically invalid export
    state = json.loads((workspace / "state.json").read_text())
    for x in state["sources"]:
        if x["name"] == "industrial.json":
            x["sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
    (workspace / "state.json").write_text(json.dumps(state))
    cli(TOOL_PATH, "run", "--workspace", workspace, "--manifest", manifest, "--db", db, expected=2)
    assert "pid_integrations" not in json.loads((workspace / "state.json").read_text())
    assert list((workspace / "derived").iterdir()) == []


def test_duplicate_run_does_not_overwrite_datasheet(tmp_path):
    workspace, manifest, db, _ = setup(tmp_path, all_three=False)
    first = cli(TOOL_PATH, "run", "--workspace", workspace, "--manifest", manifest, "--db", db)
    sha = hashlib.sha256(Path(json.loads(first.stdout)["datasheet"]).read_bytes()).hexdigest()
    cli(TOOL_PATH, "run", "--workspace", workspace, "--manifest", manifest, "--db", db, expected=2)
    assert hashlib.sha256(Path(json.loads(first.stdout)["datasheet"]).read_bytes()).hexdigest() == sha


def test_preanalysis_after_understand_is_blocked(tmp_path):
    workspace, manifest, db, _ = setup(tmp_path)
    state = json.loads((workspace / "state.json").read_text())
    state["status"] = "ANALISADO_AGUARDANDO_DECISAO"
    (workspace / "state.json").write_text(json.dumps(state))
    cli(TOOL_PATH, "run", "--workspace", workspace, "--manifest", manifest, "--db", db, expected=2)


def test_data_sheet_private_contains_no_ocr_or_alarm_commands(tmp_path):
    workspace, manifest, db, _ = setup(tmp_path, all_three=False)
    p = cli(TOOL_PATH, "run", "--workspace", workspace, "--manifest", manifest, "--db", db)
    data = Path(json.loads(p.stdout)["datasheet"]).read_text(encoding="utf-8")
    assert 'XV-101' not in data and 'HYPERLINK' not in data
    assert 'TRIP' not in data and 'SIF-' not in data


def test_duplicate_manifest_json_key_is_rejected(tmp_path):
    workspace, manifest, db, _ = setup(tmp_path)
    original = manifest.read_text(encoding="utf-8")
    manifest.write_text(original.replace('"schema":', '"schema": "wrong", "schema":', 1))
    cli(TOOL_PATH, "run", "--workspace", workspace, "--manifest", manifest, "--db", db, expected=2)
    assert not (workspace / "derived").exists()