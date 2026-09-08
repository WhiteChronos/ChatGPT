#!/usr/bin/env python3
"""Standard AUT panel pipeline.

Extends ``aut_panel_control.py`` with the project-wide panel standard:
- independent canonical model per panel;
- mandatory 24 Vdc power supply + DC-UPS + battery;
- GR-034: generate and validate the canonical BOM before rendering the panel image;
- render only components already present in the BOM;
- generate BOM and image from exactly the same Data Center records;
- require a reference model on every BOM line; exact model may remain HOLD.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Mapping

from aut_panel_control import (
    HOLD,
    Resultado,
    avaliar,
    carregar_json,
    gerar_datasheet,
    gerar_relatorio,
    gerar_sqlite,
    gerar_svg,
    indice_catalogo,
    manifesto,
    salvar_json,
    sha256,
    status_final,
    validar_schema,
    verificar_manifesto,
)

MANDATORY_POWER_CATEGORIES = {"power_supply", "dc_ups", "battery"}
GOLDEN_RULE_BOM_BEFORE_IMAGE = "GR-034"


def _panel_standard(pipeline: Mapping[str, Any], panel_id: str) -> Mapping[str, Any]:
    standards = pipeline.get("panel_standards") or {}
    return standards.get(panel_id) or {}


def validar_padrao(projeto: Mapping[str, Any], catalogo: Mapping[str, Any], pipeline: Mapping[str, Any]) -> list[Resultado]:
    resultados: list[Resultado] = []
    indice = indice_catalogo(catalogo)
    panel_id = str((projeto.get("project") or {}).get("id") or "")
    padrao = _panel_standard(pipeline, panel_id)

    if not padrao:
        resultados.append(Resultado("STD-001", "HOLD", HOLD, f"Painel {panel_id!r} não possui padrão cadastrado no pipeline.", {}))
        return resultados

    ext = (projeto.get("enclosure") or {}).get("external_mm") or {}
    plate = (projeto.get("enclosure") or {}).get("mounting_plate_mm") or {}
    expected_ext = padrao.get("enclosure_external_mm") or {}
    expected_plate = padrao.get("mounting_plate_mm") or {}
    dims_ok = ext == expected_ext and plate == expected_plate
    resultados.append(Resultado(
        "STD-002", "PASS" if dims_ok else "HOLD", "INFO" if dims_ok else HOLD,
        "Dimensões do painel seguem o padrão cadastrado." if dims_ok else "Dimensões divergentes do padrão cadastrado.",
        {"actual_external_mm": ext, "expected_external_mm": expected_ext, "actual_mounting_plate_mm": plate, "expected_mounting_plate_mm": expected_plate},
    ))

    placements = projeto.get("placements") or []
    cats = []
    missing_model = []
    for p in placements:
        item = indice.get(str(p.get("catalog_id")))
        if not item:
            continue
        cats.append(str(item.get("category")))
        model = str(item.get("model") or "").strip()
        if not model or model.upper() in {"PENDENTE", "PENDING", "A DEFINIR"}:
            missing_model.append(str(p.get("instance_id")))

    missing_power = sorted(MANDATORY_POWER_CATEGORIES - set(cats))
    power_ok = not missing_power
    resultados.append(Resultado(
        "STD-003", "PASS" if power_ok else "HOLD", "INFO" if power_ok else HOLD,
        "Fonte 24 Vcc + DC-UPS + bateria presentes." if power_ok else "Cadeia de alimentação obrigatória incompleta.",
        {"missing_categories": missing_power},
    ))

    mandatory = set(padrao.get("mandatory_categories") or [])
    missing_categories = sorted(mandatory - set(cats))
    cat_ok = not missing_categories
    resultados.append(Resultado(
        "STD-004", "PASS" if cat_ok else "HOLD", "INFO" if cat_ok else HOLD,
        "Categorias obrigatórias presentes." if cat_ok else "Categorias obrigatórias ausentes.",
        {"missing_categories": missing_categories},
    ))

    model_ok = not missing_model
    resultados.append(Resultado(
        "STD-005", "PASS" if model_ok else "HOLD", "INFO" if model_ok else HOLD,
        "Todas as linhas possuem modelo de referência." if model_ok else "Há componente sem modelo de referência.",
        {"instances_without_reference_model": missing_model},
    ))

    contract = projeto.get("production_contract") or {}
    gr034_ok = (
        contract.get("golden_rule") == GOLDEN_RULE_BOM_BEFORE_IMAGE
        and contract.get("bom_before_render") is True
        and contract.get("bom_is_render_source") is True
        and contract.get("image_must_match_bom") is True
        and contract.get("bom_change_invalidates_existing_image") is True
    )
    resultados.append(Resultado(
        GOLDEN_RULE_BOM_BEFORE_IMAGE,
        "PASS" if gr034_ok else "HOLD",
        "INFO" if gr034_ok else HOLD,
        "Contrato BOM antes da imagem validado." if gr034_ok else "Data Sheet não declara integralmente a Regra de Ouro GR-034.",
        {"production_contract": contract},
    ))
    return resultados


def gerar_bom(projeto: Mapping[str, Any], catalogo: Mapping[str, Any], saida: Path) -> tuple[Path, Path]:
    """Generate the canonical BOM before any image is produced."""
    indice = indice_catalogo(catalogo)
    linhas = []
    for pos in projeto.get("placements", []):
        catalog_id = str(pos.get("catalog_id"))
        item = indice.get(catalog_id)
        if item is None:
            raise RuntimeError(f"BOM não pode ser gerada: item {catalog_id} ausente do Data Center.")
        model = str(item.get("model") or "").strip()
        if not model:
            raise RuntimeError(f"BOM não pode ser gerada: item {catalog_id} sem modelo de referência.")
        refs = item.get("references") or []
        linhas.append({
            "instance_id": pos.get("instance_id"),
            "catalog_id": catalog_id,
            "category": item.get("category"),
            "manufacturer": item.get("manufacturer"),
            "family": item.get("family"),
            "reference_model": model,
            "engineering_status": item.get("engineering_status"),
            "lifecycle_status": item.get("lifecycle_status"),
            "surface": pos.get("surface"),
            "x_mm": pos.get("x_mm"),
            "y_mm": pos.get("y_mm"),
            "reference_ids": [r.get("reference_id") for r in refs if r.get("reference_id")],
        })

    bom_json = saida / "AUT_PANEL_BOM.json"
    salvar_json(bom_json, {
        "schema_version": "1.1",
        "project_id": (projeto.get("project") or {}).get("id"),
        "golden_rule": GOLDEN_RULE_BOM_BEFORE_IMAGE,
        "must_precede_render": True,
        "catalog_sha256": None,
        "lines": linhas,
    })

    bom_csv = saida / "AUT_PANEL_BOM.csv"
    fields = ["instance_id", "catalog_id", "category", "manufacturer", "family", "reference_model", "engineering_status", "lifecycle_status", "surface", "x_mm", "y_mm", "reference_ids"]
    with bom_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in linhas:
            x = dict(row)
            x["reference_ids"] = ";".join(row["reference_ids"])
            writer.writerow(x)
    return bom_json, bom_csv


def _bom_pairs(bom: Mapping[str, Any]) -> list[tuple[str, str]]:
    return [(str(x.get("instance_id")), str(x.get("catalog_id"))) for x in bom.get("lines", [])]


def _project_pairs(projeto: Mapping[str, Any]) -> list[tuple[str, str]]:
    return [(str(x.get("instance_id")), str(x.get("catalog_id"))) for x in projeto.get("placements", [])]


def gerar_imagem_pos_bom(projeto: Mapping[str, Any], catalogo: Mapping[str, Any], bom_path: Path, image_path: Path) -> None:
    """Render only after the canonical BOM exists and exactly matches the layout source."""
    if not bom_path.exists():
        raise RuntimeError("GR-034: a Lista de Material deve existir antes da geração da imagem do quadro.")
    bom = carregar_json(bom_path)
    if bom.get("golden_rule") != GOLDEN_RULE_BOM_BEFORE_IMAGE or bom.get("must_precede_render") is not True:
        raise RuntimeError("GR-034: BOM sem contrato obrigatório de precedência sobre a imagem.")
    if str(bom.get("project_id")) != str((projeto.get("project") or {}).get("id")):
        raise RuntimeError("GR-034: BOM pertence a outro painel/projeto.")
    if _bom_pairs(bom) != _project_pairs(projeto):
        raise RuntimeError("GR-034: imagem bloqueada porque BOM e Data Sheet não possuem as mesmas instâncias/componentes.")
    gerar_svg(projeto, catalogo, image_path)


def executar(args: argparse.Namespace) -> int:
    project_path = Path(args.project)
    catalog_path = Path(args.catalog)
    pipeline_path = Path(args.pipeline)
    schema_path = Path(args.schema)
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)

    projeto = carregar_json(project_path)
    catalogo = carregar_json(catalog_path)
    pipeline = carregar_json(pipeline_path)
    resultados = validar_schema(projeto, carregar_json(schema_path)) + avaliar(projeto, catalogo) + validar_padrao(projeto, catalogo, pipeline)

    qa_json, qa_md = gerar_relatorio(output, projeto, resultados)
    ds = gerar_datasheet(projeto, catalogo, resultados, sha256(project_path), sha256(catalog_path))
    ds_path = output / "AUT_PANEL_DATASHEET.json"
    salvar_json(ds_path, ds)
    db_path = output / "AUT_PANEL_DATACENTER.sqlite3"
    gerar_sqlite(catalogo, db_path)

    # GR-034 — immutable production order: BOM first, panel image second.
    bom_json, bom_csv = gerar_bom(projeto, catalogo, output)
    image_path = output / "AUT_PANEL_LAYOUT.svg"
    gerar_imagem_pos_bom(projeto, catalogo, bom_json, image_path)

    estado = status_final(resultados)
    man = manifesto(
        output,
        [project_path, catalog_path, pipeline_path, schema_path],
        [qa_json, qa_md, ds_path, db_path, bom_json, bom_csv, image_path],
        estado,
    )
    verificar_manifesto(man, output)
    print(json.dumps({
        "status": estado,
        "project_id": (projeto.get("project") or {}).get("id"),
        "golden_rule": GOLDEN_RULE_BOM_BEFORE_IMAGE,
        "sequence": ["AUT_PANEL_BOM.json", "AUT_PANEL_BOM.csv", "AUT_PANEL_LAYOUT.svg"],
        "manifest": str(man),
    }, ensure_ascii=False))
    if estado == "REPROVADO":
        return 1
    if estado == HOLD and not args.allow_hold:
        return 2
    return 0


def principal() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--catalog", required=True)
    parser.add_argument("--pipeline", required=True)
    parser.add_argument("--schema", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--allow-hold", action="store_true")
    args = parser.parse_args()
    try:
        return executar(args)
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(principal())
