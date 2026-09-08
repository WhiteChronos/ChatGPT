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
    """Synthetic validation fixture for deterministic geometry/rule tests.

    Production catalog records may intentionally remain PENDING_REFERENCE/HOLD.
    Unit tests promote them synthetically so rule behavior can be tested without
    pretending production evidence is complete.
    """
    catalogo = carregar("datacenter/AUT_PANEL_COMPONENT_CATALOG.json")
    ref = {
        "reference_id": "TEST-REF",
        "document_type": "Synthetic test fixture",
        "title": "Synthetic dimensional record",
        "document_code": "TEST",
        "revision": "R00",
        "publication_date": "2026-09-08",
        "page_section": "test fixture",
        "source_tier": "INTERNAL_REFERENCE",
        "official_url": None,
        "consultation_date": "2026-09-08",
        "validation_status": "VALID"
    }
    for item in catalogo["components"]:
        item["engineering_status"] = "VALIDATED"
        item["lifecycle_status"] = "ACTIVE"
        if not item.get("references"):
            item["references"] = [copy.deepcopy(ref)]
    return catalogo


def projeto_valido():
    return carregar("datasheet/AUT_PANEL_DATA_SHEET.json")


def test_datasheet_obedece_schema():
    erros = list(Draft202012Validator(carregar("schemas/aut_panel_project_v1.schema.json")).iter_errors(carregar("datasheet/AUT_PANEL_DATA_SHEET.json")))
    assert not erros, [erro.message for erro in erros]


def test_datasheet_pn_aut_02_obedece_schema():
    erros = list(Draft202012Validator(carregar("schemas/aut_panel_project_v1.schema.json")).iter_errors(carregar("datasheet/PN-AUT-02_DATA_SHEET.json")))
    assert not erros, [erro.message for erro in erros]


def test_projeto_sintetico_completo_e_aprovado():
    assert aut.status_final(aut.avaliar(projeto_valido(), catalogo_validado())) == aut.APROVADO


def test_interno_600x600_em_gabinete_800x600_e_reprovado():
    projeto = projeto_valido()
    projeto["views"]["front_internal_mm"]["height"] = 600
    resultados = aut.avaliar(projeto, catalogo_validado())
    assert aut.status_final(resultados) == aut.REPROVADO
    assert any(x.regra == "GR-022" and x.resultado == "FAIL" for x in resultados)


def test_escala_por_vista_e_reprovada():
    projeto = projeto_valido()
    projeto["render"]["per_view_scale"] = {"front_internal": 1.0}
    resultados = aut.avaliar(projeto, catalogo_validado())
    assert aut.status_final(resultados) == aut.REPROVADO
    assert any(x.regra == "GR-024" and x.resultado == "FAIL" for x in resultados)


def test_zona_inferior_insuficiente_gera_hold():
    projeto = projeto_valido()
    projeto["layout"]["bottom_zone"]["terminal_zone_bottom_y_mm"] = 100
    resultados = aut.avaliar(projeto, catalogo_validado())
    assert aut.status_final(resultados) == aut.HOLD
    assert any(x.regra == "GR-027" and x.resultado == "HOLD" for x in resultados)


def test_colisao_e_reprovada():
    projeto = projeto_valido()
    projeto["placements"].append({"instance_id": "UPS02", "catalog_id": "ADEL-CBI2420A", "surface": "mounting_plate", "x_mm": 250, "y_mm": 580, "rotation_deg": 0})
    resultados = aut.avaliar(projeto, catalogo_validado())
    assert aut.status_final(resultados) == aut.REPROVADO
    assert any(x.regra == "GR-018" and x.resultado == "FAIL" for x in resultados)


def test_svg_preserva_dimensoes_mestres(tmp_path):
    saida = tmp_path / "layout.svg"
    aut.gerar_svg(projeto_valido(), catalogo_validado(), saida)
    texto = saida.read_text(encoding="utf-8")
    assert 'id="front-internal" data-width-mm="600.0" data-height-mm="800.0"' in texto
    assert 'id="front-external" data-width-mm="600.0" data-height-mm="800.0"' in texto
    assert 'id="side-external" data-width-mm="300.0" data-height-mm="800.0"' in texto


def test_datacenter_sqlite_e_criado(tmp_path):
    saida = tmp_path / "catalogo.sqlite3"
    aut.gerar_sqlite(carregar("datacenter/AUT_PANEL_COMPONENT_CATALOG.json"), saida)
    with sqlite3.connect(saida) as banco:
        produtos = banco.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        referencias = banco.execute("SELECT COUNT(*) FROM references_docs").fetchone()[0]
    assert produtos >= 12
    assert referencias >= 10


def test_gr034_esta_no_datasheet_e_pipeline():
    projeto = projeto_valido()
    pipeline = carregar("pipeline/AUT_PANEL_PIPELINE.json")
    contract = projeto["production_contract"]
    assert contract["golden_rule"] == "GR-034"
    assert contract["bom_before_render"] is True
    assert pipeline["golden_rules"]["GR-034"]["enforcement"]["bom_before_render"] is True
    assert pipeline["standard_sequence"].index("BOM") < pipeline["standard_sequence"].index("RENDER_IMAGE")


def test_gr034_bloqueia_imagem_sem_bom(tmp_path):
    with pytest.raises(RuntimeError, match="GR-034"):
        std.gerar_imagem_pos_bom(
            projeto_valido(),
            catalogo_validado(),
            tmp_path / "AUT_PANEL_BOM.json",
            tmp_path / "AUT_PANEL_LAYOUT.svg",
        )


def test_gr034_bom_gera_imagem_na_ordem_correta(tmp_path):
    projeto = projeto_valido()
    catalogo = catalogo_validado()
    bom_json, bom_csv = std.gerar_bom(projeto, catalogo, tmp_path)
    assert bom_json.exists()
    assert bom_csv.exists()
    image = tmp_path / "AUT_PANEL_LAYOUT.svg"
    std.gerar_imagem_pos_bom(projeto, catalogo, bom_json, image)
    assert image.exists()
    dados = json.loads(bom_json.read_text(encoding="utf-8"))
    assert dados["golden_rule"] == "GR-034"
    assert dados["must_precede_render"] is True
