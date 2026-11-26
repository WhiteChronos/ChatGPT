import importlib.util
import json
import sys
from pathlib import Path
from openpyxl import Workbook, load_workbook
import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "verificar_efeitos_x.py"
spec = importlib.util.spec_from_file_location("mce_x_verifier", SCRIPT)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

def scenario(tmp_path):
    path = tmp_path / "mce.xlsx"
    w = Workbook(); s = w.active; s.title = "FOLHA 1"
    s["C7"] = "Equipamento / Servico / Zona"
    s["I5"] = "ALARME"
    s["C8"] = "Nivel baixo"; s["F8"] = "LSL-01"; s["H8"] = "1"
    w.save(path)
    return path

def ledger(tmp_path, status="APROVADO"):
    p = tmp_path / "ledger.json"
    p.write_text(json.dumps({"approved_relations":[{
        "sheet":"FOLHA 1", "cell":"I8", "index":"1", "tag":"LSL-01",
        "effect":"ALARME", "document":"MD rev D",
        "source_sha256":"a"*64, "revision":"D",
        "location":"secao 8", "verbatim_excerpt":"nivel baixo gera alarme",
        "approver":"Engenharia", "status":status
    }]}), encoding="utf-8")
    return p

def add_x(path):
    w=load_workbook(path)
    w.active["I8"]="X"
    w.save(path)

def test_zero_x_blocks(tmp_path):
    path=scenario(tmp_path)
    assert "MATRIZ_SEM_X" in mod.audit(path, expected_causes=1)["errors"]

def test_approved_new_x_does_not_false_block(tmp_path):
    path=scenario(tmp_path)
    old=tmp_path / "base.xlsx"; old.write_bytes(path.read_bytes())
    add_x(path)
    result=mod.audit(path, baseline=old, ledger=ledger(tmp_path), expected_causes=1)
    assert result["status"] == "PASS_ESTRUTURAL_COM_EVIDENCIAS"

def test_pending_new_x_blocks(tmp_path):
    path=scenario(tmp_path)
    old=tmp_path / "base.xlsx"; old.write_bytes(path.read_bytes())
    add_x(path)
    result=mod.audit(path, baseline=old, ledger=ledger(tmp_path, "PENDENTE"))
    assert any(x.startswith("X_ADICIONADO_SEM_APROVACAO") for x in result["errors"])

def test_count_mismatch_blocks(tmp_path):
    path=scenario(tmp_path); add_x(path)
    assert "QUANTIDADE_CAUSAS_DIVERGENTE" in mod.audit(path, ledger=ledger(tmp_path), expected_causes=60)["errors"]

def test_without_effect_title_blocks(tmp_path):
    path=scenario(tmp_path); add_x(path)
    w=load_workbook(path); w.active["I5"]=None; w.save(path)
    assert any(x.startswith("X_SEM_TITULO") for x in mod.audit(path)["errors"])

def test_read_only(tmp_path):
    path=scenario(tmp_path); add_x(path)
    original=path.read_bytes()
    mod.audit(path, ledger=ledger(tmp_path))
    assert path.read_bytes() == original
