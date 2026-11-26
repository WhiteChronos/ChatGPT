import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

from openpyxl import Workbook, load_workbook

ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / "scripts" / "mce_delivery_guard.py"
spec = importlib.util.spec_from_file_location("mce_delivery_guard", GUARD)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


def scenario(tmp_path):
    w = tmp_path / "case"
    (w / "base").mkdir(parents=True)
    (w / "output").mkdir()
    wb = Workbook()
    ws = wb.active
    ws.title = "FOLHA 1"
    ws["I5"] = "ALARME"
    ws["C8"] = "Nivel baixo"
    wb.save(w / "base" / "modelo.xlsx")
    wb.save(w / "output" / "MCE_PRELIMINAR.xlsx")
    state = {
        "status": "MCE_PRELIMINAR_PARA_REVISAO",
        "template_classification": "MODELO_APROVADO",
        "template_sha256": mod.digest(w / "base" / "modelo.xlsx"),
        "output_sha256": mod.digest(w / "output" / "MCE_PRELIMINAR.xlsx"),
        "source_manifest_sha256": "manifest",
        "approval": {"decision": "AUTORIZO_ELABORACAO_MCE", "source_manifest_sha256": "manifest"},
        "sources": [{"name": "md.txt", "sha256": "sourcehash", "extension": ".txt"}],
    }
    change = {
        "sheet": "FOLHA 1", "cell": "I8", "old_text": None,
        "new_text": "X", "evidence_status": "DOCUMENTADO",
        "source_name": "md.txt", "source_sha256": "sourcehash",
        "verbatim_excerpt": "nivel baixo aciona alarme",
        "source_location": "secao 8", "reference_revision": "D",
    }
    (w / "contract.json").write_text(json.dumps({"model_approved": True, "template_sha256": state["template_sha256"]}))
    (w / "AUDITORIA_MCE.json").write_text(json.dumps({"passed": True}))
    (w / "ALTERACOES_MCE.json").write_text(json.dumps([{"sheet": "FOLHA 1", "cell": "I8", "before": None, "after": "X"}]))
    return w, state, change


def save(w, state, change):
    (w / "state.json").write_text(json.dumps(state))
    (w / "changes.json").write_text(json.dumps([change]))


def put_x(w, state):
    path = w / "output" / "MCE_PRELIMINAR.xlsx"
    wb = load_workbook(path)
    wb.active["I8"] = "X"
    wb.save(path)
    state["output_sha256"] = mod.digest(path)


def test_zero_x_is_blocked(tmp_path):
    w, s, ch = scenario(tmp_path)
    save(w, s, ch)
    assert "MATRIZ_SEM_X" in mod.inspect(w, w / "changes.json")["errors"]


def test_canonical_state_is_required(tmp_path):
    w, s, ch = scenario(tmp_path)
    put_x(w, s)
    s["status"] = "ANALISADO_AGUARDANDO_DECISAO"
    save(w, s, ch)
    assert "EXECUTOR_CANONICO_NAO_CONCLUIDO" in mod.inspect(w, w / "changes.json")["errors"]


def test_hash_tampering_is_blocked(tmp_path):
    w, s, ch = scenario(tmp_path)
    put_x(w, s)
    s["output_sha256"] = "incorrect"
    save(w, s, ch)
    assert "MCE_XLSX_HASH_DIVERGENTE" in mod.inspect(w, w / "changes.json")["errors"]


def test_pending_relation_is_blocked(tmp_path):
    w, s, ch = scenario(tmp_path)
    put_x(w, s)
    ch["evidence_status"] = "PENDENTE"
    save(w, s, ch)
    assert "X_SEM_EVIDENCIA_INDIVIDUAL" in mod.inspect(w, w / "changes.json")["errors"]


def test_binary_source_needs_manual_evidence(tmp_path):
    w, s, ch = scenario(tmp_path)
    put_x(w, s)
    s["sources"][0]["extension"] = ".pdf"
    save(w, s, ch)
    assert "X_SEM_EVIDENCIA_INDIVIDUAL" in mod.inspect(w, w / "changes.json")["errors"]


def test_documented_x_passes_structural_only(tmp_path):
    w, s, ch = scenario(tmp_path)
    put_x(w, s)
    save(w, s, ch)
    assert mod.inspect(w, w / "changes.json")["status"] == "PASS_ESTRUTURAL_PRELIMINAR"
