from __future__ import annotations

import copy
import json
import sqlite3
from pathlib import Path

from jsonschema import Draft202012Validator
from pipeline import aut_panel_control as aut

ROOT = Path(__file__).resolve().parents[1]


def carregar(relativo: str):
    return json.loads((ROOT / relativo).read_text(encoding="utf-8"))


def catalogo_validado():
    catalogo = carregar("datacenter/AUT_PANEL_COMPONENT_CATALOG.json")
    ref = {
        "reference_id": "TEST-REF",
        "document_type": "Synthetic test fixture",
        "title": "Synthetic dimensional record",
        "document_code": "TEST",
        "revision": "R00",
        "publication_date": "2026-09-07",
        "page_section": "test fixture",
        "source_tier": "INTERNAL_REFERENCE",
        "official_url": None,
        "consultation_date": "2026-09-07",
        "validation_status": "VALID"
    }
    dimensoes = {
        "PENDING-ENCLOSURE-800X600X300": {"width": 600, "height": 800, "depth": 300},
        "RTU-PENDING": {"width": 55, "height": 125, "depth": 75},
        "RTU-DI-PENDING": {"width": 30, "height": 125, "depth": 75},
        "RTU-DO-PENDING": {"width": 30, "height": 125, "depth": 75},
        "RTU-AI-PENDING": {"width": 30, "height": 125, "depth": 75},
        "RTU-RTD-PENDING": {"width": 30, "height": 125, "depth": 75}
    }
    for item in catalogo["components"]:
        item["lifecycle_status"] = "ACTIVE"
        if item["catalog_id"] in dimensoes:
            item["engineering_status"] = "VALIDATED"
            item["dimensions_mm"] = dimensoes[item["catalog_id"]]
            item["references"] = [copy.deepcopy(ref)]
    return catalogo


def projeto_valido():
    projeto = carregar("datasheet/AUT_PANEL_DATA_SHEET.json")
    projeto["enclosure"]["manufacturer"] = "Synthetic Test Manufacturer"
    projeto["enclosure"]["model"] = "TEST-800X600X300"
    return projeto


def test_datasheet_obedece_schema():
    erros = list(Draft202012Validator(carregar("schemas/aut_panel_project_v1.schema.json")).iter_errors(carregar("datasheet/AUT_PANEL_DATA_SHEET.json")))
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
    projeto["placements"].append({"instance_id": "UPS02", "catalog_id": "ADEL-CBI2420A", "surface": "mounting_plate", "x_mm": 120, "y_mm": 600, "rotation_deg": 0})
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
    assert produtos >= 9
    assert referencias >= 4
