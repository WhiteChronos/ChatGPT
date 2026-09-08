from __future__ import annotations

import copy
import json
import sqlite3
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from pipeline import aut_panel_control as aut
from pipeline import aut_panel_standard as std

ROOT = Path(__file__).resolve().parents[1]

def carregar(relativo: str):
    return json.loads((ROOT / relativo).read_text(encoding="utf-8"))

def catalogo_validado():
    catalogo = carregar("datacenter/AUT_PANEL_COMPONENT_CATALOG_V2.json")
    ref = {"reference_id":"TEST-REF","document_type":"Synthetic test fixture","title":"Synthetic dimensional record","document_code":"TEST","revision":"R00","publication_date":"2026-09-08","page_section":"test fixture","source_tier":"INTERNAL_REFERENCE","official_url":None,"consultation_date":"2026-09-08","validation_status":"VALID"}
    for item in catalogo["components"]:
        item["engineering_status"] = "VALIDATED"
        item["lifecycle_status"] = "ACTIVE"
        if not item.get("references"):
            item["references"] = [copy.deepcopy(ref)]
    return catalogo

def projeto_valido(): return carregar("datasheet/AUT_PANEL_DATA_SHEET.json")
def li_valida(): return carregar("li/PN-AUT-01_LI.json")
def qreg(): return carregar("datacenter/AUT_PANEL_PANEL_QUANTITIES.json")
def pipeline(): return carregar("pipeline/AUT_PANEL_PIPELINE.json")

def test_datasheets_obedecem_schema():
    schema = carregar("schemas/aut_panel_project_v1.schema.json")
    for path in ("datasheet/AUT_PANEL_DATA_SHEET.json","datasheet/PN-AUT-02_DATA_SHEET.json"):
        erros = list(Draft202012Validator(schema).iter_errors(carregar(path)))
        assert not erros, [erro.message for erro in erros]

def test_gr035_li_e_layout_tem_paridade():
    resultados = std.validar_li(projeto_valido(), catalogo_validado(), pipeline(), li_valida(), qreg())
    assert any(x.regra == "GR-035" and x.resultado == "PASS" for x in resultados)

def test_gr035_quantidade_errada_reprova():
    projeto = projeto_valido()
    projeto["placements"][0]["quantity"] = 2
    resultados = std.validar_li(projeto, catalogo_validado(), pipeline(), li_valida(), qreg())
    assert any(x.regra == "GR-035" and x.resultado == "FAIL" for x in resultados)

def test_gr034_li_congelada_antes_bom():
    li = li_valida()
    assert li["status"] == "QUANTITY_FROZEN"
    assert pipeline()["standard_sequence"].index("LI_QUANTITY") < pipeline()["standard_sequence"].index("BOM") < pipeline()["standard_sequence"].index("RENDER_IMAGE")

def test_bom_usa_quantidades_da_li(tmp_path):
    li, cat = li_valida(), catalogo_validado()
    bom_json, bom_csv = std.gerar_bom(li, cat, tmp_path)
    assert bom_json.exists() and bom_csv.exists()
    bom = json.loads(bom_json.read_text(encoding="utf-8"))
    source = {x["tag"]: x["quantity"] for x in li["lines"]}
    derived = {x["li_tag"]: x["quantity"] for x in bom["lines"]}
    assert source == derived

def test_imagem_bloqueada_se_li_layout_divergirem(tmp_path):
    projeto = projeto_valido(); projeto["placements"][0]["quantity"] = 2
    bom_json, _ = std.gerar_bom(li_valida(), catalogo_validado(), tmp_path)
    with pytest.raises(RuntimeError, match="GR-035"):
        std.gerar_imagem_pos_li(projeto, catalogo_validado(), li_valida(), bom_json, tmp_path / "layout.svg")

def test_hmi_permanece_na_porta():
    projeto = projeto_valido()
    hmi = next(x for x in projeto["placements"] if x["li_tag"] == "HMI-01")
    assert hmi["surface"] == "door"

def test_interno_600x600_em_gabinete_800x600_e_reprovado():
    projeto = projeto_valido(); projeto["views"]["front_internal_mm"]["height"] = 600
    resultados = aut.avaliar(projeto, catalogo_validado())
    assert aut.status_final(resultados) == aut.REPROVADO

def test_escala_por_vista_e_reprovada():
    projeto = projeto_valido(); projeto["render"]["per_view_scale"] = {"front_internal": 1.0}
    resultados = aut.avaliar(projeto, catalogo_validado())
    assert any(x.regra == "GR-024" and x.resultado == "FAIL" for x in resultados)

def test_zona_inferior_insuficiente_gera_hold():
    projeto = projeto_valido(); projeto["layout"]["bottom_zone"]["terminal_zone_bottom_y_mm"] = 100
    resultados = aut.avaliar(projeto, catalogo_validado())
    assert any(x.regra == "GR-027" and x.resultado == "HOLD" for x in resultados)

def test_svg_preserva_dimensoes_mestres(tmp_path):
    saida = tmp_path / "layout.svg"; aut.gerar_svg(projeto_valido(), catalogo_validado(), saida)
    texto = saida.read_text(encoding="utf-8")
    assert 'id="front-internal" data-width-mm="600.0" data-height-mm="800.0"' in texto
    assert 'id="front-external" data-width-mm="600.0" data-height-mm="800.0"' in texto
    assert 'id="side-external" data-width-mm="300.0" data-height-mm="800.0"' in texto

def test_datacenter_sqlite_e_criado(tmp_path):
    saida = tmp_path / "catalogo.sqlite3"; aut.gerar_sqlite(carregar("datacenter/AUT_PANEL_COMPONENT_CATALOG_V2.json"), saida)
    with sqlite3.connect(saida) as banco:
        produtos = banco.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    assert produtos >= 30
