#!/usr/bin/env python3
"""AUT Panel Standard pipeline v1.3.

Production contract:
1. Data Center + Data Sheet
2. Freeze LI with exact panel quantities
3. Generate BOM from LI
4. Validate layout quantities against LI
5. Render panel drawing only after LI/BOM parity passes

Golden Rules:
- GR-034: LI/BOM before drawing
- GR-035: exact quantitative parity LI <-> Data Sheet/layout/drawing
- GR-036: any LI quantity change invalidates previous BOM/layout/drawing
- GR-037: HMI stays on the cabinet door
- GR-038: never distort components to make them fit
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Mapping

try:
    from .aut_panel_control import (
        HOLD, REPROVADO, Resultado, avaliar, carregar_json, gerar_datasheet,
        gerar_relatorio, gerar_sqlite, gerar_svg, indice_catalogo, manifesto,
        salvar_json, sha256, status_final, validar_schema, verificar_manifesto,
    )
except ImportError:
    from aut_panel_control import (
        HOLD, REPROVADO, Resultado, avaliar, carregar_json, gerar_datasheet,
        gerar_relatorio, gerar_sqlite, gerar_svg, indice_catalogo, manifesto,
        salvar_json, sha256, status_final, validar_schema, verificar_manifesto,
    )

GR034 = "GR-034"
GR035 = "GR-035"
GR036 = "GR-036"
GR037 = "GR-037"
MANDATORY_POWER_CATEGORIES = {"power_supply", "dc_ups", "battery"}


def _panel_standard(pipeline: Mapping[str, Any], panel_id: str) -> Mapping[str, Any]:
    return (pipeline.get("panel_standards") or {}).get(panel_id) or {}


def _li_map(li: Mapping[str, Any], *, render_only: bool = False) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for line in li.get("lines", []):
        if render_only and line.get("render_required") is not True:
            continue
        tag = str(line.get("tag") or "")
        out[tag] = {
            "catalog_id": str(line.get("catalog_id") or ""),
            "quantity": line.get("quantity"),
            "unit": str(line.get("unit") or ""),
            "render_required": bool(line.get("render_required")),
        }
    return out


def _placement_map(projeto: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for p in projeto.get("placements", []):
        out[str(p.get("li_tag") or "")] = {
            "catalog_id": str(p.get("catalog_id") or ""),
            "quantity": p.get("quantity"),
            "surface": str(p.get("surface") or ""),
        }
    return out


def validar_li(
    projeto: Mapping[str, Any],
    catalogo: Mapping[str, Any],
    pipeline: Mapping[str, Any],
    li: Mapping[str, Any],
    quantity_registry: Mapping[str, Any],
) -> list[Resultado]:
    resultados: list[Resultado] = []
    indice = indice_catalogo(catalogo)
    panel_id = str((projeto.get("project") or {}).get("id") or "")
    padrao = _panel_standard(pipeline, panel_id)

    if not padrao:
        return [Resultado("STD-001", "HOLD", HOLD, f"Painel {panel_id!r} sem padrão cadastrado.", {})]

    ext = (projeto.get("enclosure") or {}).get("external_mm") or {}
    plate = (projeto.get("enclosure") or {}).get("mounting_plate_mm") or {}
    dims_ok = ext == (padrao.get("enclosure_external_mm") or {}) and plate == (padrao.get("mounting_plate_mm") or {})
    resultados.append(Resultado("STD-002", "PASS" if dims_ok else "HOLD", "INFO" if dims_ok else HOLD,
        "Dimensões seguem o padrão cadastrado." if dims_ok else "Dimensões divergem do padrão cadastrado.",
        {"external_mm": ext, "mounting_plate_mm": plate}))

    identity_ok = str(li.get("project_id")) == panel_id and li.get("status") == "QUANTITY_FROZEN"
    resultados.append(Resultado(GR034, "PASS" if identity_ok else "HOLD", "INFO" if identity_ok else HOLD,
        "LI quantitativa congelada antes da BOM/desenho." if identity_ok else "LI ausente, não congelada ou de outro painel.",
        {"li_id": li.get("li_id"), "li_project_id": li.get("project_id"), "li_status": li.get("status")}))

    registry_panel = ((quantity_registry.get("panels") or {}).get(panel_id) or {})
    registry_quantities = registry_panel.get("quantities") or {}
    li_lines = li.get("lines") or []
    issues: list[str] = []
    categories: set[str] = set()
    for line in li_lines:
        tag = str(line.get("tag") or "")
        cid = str(line.get("catalog_id") or "")
        qty = line.get("quantity")
        unit = str(line.get("unit") or "")
        if not tag:
            issues.append("linha sem tag")
            continue
        if not isinstance(qty, int) or qty < 1:
            issues.append(f"{tag}: quantidade inválida {qty!r}")
        item = indice.get(cid)
        if item is None:
            issues.append(f"{tag}: catalog_id {cid} ausente do Data Center")
        else:
            categories.add(str(item.get("category")))
            if not str(item.get("model") or "").strip():
                issues.append(f"{tag}: modelo de referência ausente")
        reg = registry_quantities.get(tag)
        if not reg:
            issues.append(f"{tag}: ausente do registro quantitativo do Data Center")
        else:
            expected = (str(reg.get("catalog_id")), reg.get("quantity"), str(reg.get("unit")), bool(reg.get("render_required")))
            actual = (cid, qty, unit, bool(line.get("render_required")))
            if expected != actual:
                issues.append(f"{tag}: LI diverge do registro quantitativo")

    registry_ok = (
        registry_panel.get("li_id") == li.get("li_id")
        and registry_panel.get("revision") == li.get("revision")
        and not issues
        and len(registry_quantities) == len(li_lines)
    )
    resultados.append(Resultado("STD-LI-001", "PASS" if registry_ok else "HOLD", "INFO" if registry_ok else HOLD,
        "LI e Data Center quantitativo estão sincronizados." if registry_ok else "LI e Data Center quantitativo divergem.",
        {"issues": issues}))

    missing_power = sorted(MANDATORY_POWER_CATEGORIES - categories)
    resultados.append(Resultado("STD-003", "PASS" if not missing_power else "HOLD", "INFO" if not missing_power else HOLD,
        "Fonte 24 Vcc + DC-UPS + bateria presentes." if not missing_power else "Cadeia de alimentação incompleta.",
        {"missing_categories": missing_power}))
    mandatory = set(padrao.get("mandatory_categories") or [])
    missing_categories = sorted(mandatory - categories)
    resultados.append(Resultado("STD-004", "PASS" if not missing_categories else "HOLD", "INFO" if not missing_categories else HOLD,
        "Categorias obrigatórias presentes." if not missing_categories else "Categorias obrigatórias ausentes.",
        {"missing_categories": missing_categories}))

    li_render = _li_map(li, render_only=True)
    placements = _placement_map(projeto)
    parity_issues: list[str] = []
    for tag, expected in li_render.items():
        actual = placements.get(tag)
        if actual is None:
            parity_issues.append(f"{tag}: ausente do Data Sheet/layout")
            continue
        if actual.get("catalog_id") != expected.get("catalog_id") or actual.get("quantity") != expected.get("quantity"):
            parity_issues.append(f"{tag}: quantidade/catalog_id do layout diverge da LI")
    extra = sorted(set(placements) - set(li_render))
    for tag in extra:
        parity_issues.append(f"{tag}: está no layout mas não está marcado para desenho na LI")
    parity_ok = not parity_issues
    resultados.append(Resultado(GR035, "PASS" if parity_ok else "FAIL", "INFO" if parity_ok else REPROVADO,
        "Paridade quantitativa LI ↔ Data Sheet/layout validada." if parity_ok else "Paridade quantitativa LI ↔ layout violada.",
        {"issues": parity_issues}))

    contract = projeto.get("production_contract") or {}
    contract_ok = (
        GR034 in (contract.get("golden_rules") or [])
        and GR035 in (contract.get("golden_rules") or [])
        and GR036 in (contract.get("golden_rules") or [])
        and contract.get("li_before_bom") is True
        and contract.get("li_is_quantity_source") is True
        and contract.get("bom_before_render") is True
        and contract.get("bom_quantity_must_match_li") is True
        and contract.get("layout_quantity_must_match_li") is True
        and contract.get("image_must_match_li") is True
        and contract.get("li_change_invalidates_bom_layout_image") is True
    )
    resultados.append(Resultado(GR036, "PASS" if contract_ok else "HOLD", "INFO" if contract_ok else HOLD,
        "Contrato de invalidação por mudança da LI ativo." if contract_ok else "Contrato LI→BOM→layout→imagem incompleto.",
        {"production_contract": contract}))

    hmi_tags = [tag for tag, rec in li_render.items() if (indice.get(rec["catalog_id"]) or {}).get("category") == "hmi"]
    hmi_ok = bool(hmi_tags) and all((placements.get(tag) or {}).get("surface") == "door" for tag in hmi_tags)
    resultados.append(Resultado(GR037, "PASS" if hmi_ok else "FAIL", "INFO" if hmi_ok else REPROVADO,
        "IHM posicionada na porta/tampa." if hmi_ok else "IHM deve estar na porta/tampa do quadro.",
        {"hmi_tags": hmi_tags}))
    return resultados


def gerar_bom(li: Mapping[str, Any], catalogo: Mapping[str, Any], saida: Path) -> tuple[Path, Path]:
    indice = indice_catalogo(catalogo)
    linhas: list[dict[str, Any]] = []
    for line in li.get("lines", []):
        cid = str(line.get("catalog_id"))
        item = indice.get(cid)
        if item is None:
            raise RuntimeError(f"BOM bloqueada: {cid} não existe no Data Center.")
        model = str(item.get("model") or "").strip()
        if not model:
            raise RuntimeError(f"BOM bloqueada: {cid} sem modelo de referência.")
        refs = item.get("references") or []
        linhas.append({
            "item": line.get("item"), "li_tag": line.get("tag"), "catalog_id": cid,
            "quantity": line.get("quantity"), "unit": line.get("unit"),
            "render_required": bool(line.get("render_required")),
            "category": item.get("category"), "manufacturer": item.get("manufacturer"),
            "family": item.get("family"), "reference_model": model,
            "engineering_status": item.get("engineering_status"),
            "lifecycle_status": item.get("lifecycle_status"),
            "reference_ids": [r.get("reference_id") for r in refs if r.get("reference_id")],
        })
    bom_json = saida / "AUT_PANEL_BOM.json"
    salvar_json(bom_json, {
        "schema_version": "1.2", "project_id": li.get("project_id"), "li_id": li.get("li_id"),
        "li_revision": li.get("revision"), "golden_rules": [GR034, GR035, GR036],
        "quantity_source": "LI", "must_precede_render": True, "lines": linhas,
    })
    bom_csv = saida / "AUT_PANEL_BOM.csv"
    fields = ["item","li_tag","catalog_id","quantity","unit","render_required","category","manufacturer","family","reference_model","engineering_status","lifecycle_status","reference_ids"]
    with bom_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for row in linhas:
            x = dict(row); x["reference_ids"] = ";".join(row["reference_ids"]); w.writerow(x)
    return bom_json, bom_csv


def _bom_render_map(bom: Mapping[str, Any]) -> dict[str, tuple[str, int]]:
    return {
        str(x.get("li_tag")): (str(x.get("catalog_id")), int(x.get("quantity")))
        for x in bom.get("lines", []) if x.get("render_required") is True
    }


def _li_render_pairs(li: Mapping[str, Any]) -> dict[str, tuple[str, int]]:
    return {
        str(x.get("tag")): (str(x.get("catalog_id")), int(x.get("quantity")))
        for x in li.get("lines", []) if x.get("render_required") is True
    }


def _project_render_pairs(projeto: Mapping[str, Any]) -> dict[str, tuple[str, int]]:
    return {
        str(x.get("li_tag")): (str(x.get("catalog_id")), int(x.get("quantity")))
        for x in projeto.get("placements", [])
    }


def gerar_imagem_pos_li(projeto: Mapping[str, Any], catalogo: Mapping[str, Any], li: Mapping[str, Any], bom_path: Path, image_path: Path) -> None:
    if not bom_path.exists():
        raise RuntimeError("GR-034: BOM deve existir antes do desenho.")
    bom = carregar_json(bom_path)
    if bom.get("li_id") != li.get("li_id") or bom.get("li_revision") != li.get("revision"):
        raise RuntimeError("GR-036: BOM pertence a revisão diferente da LI.")
    expected = _li_render_pairs(li)
    if _bom_render_map(bom) != expected:
        raise RuntimeError("GR-035: BOM não possui as mesmas quantidades desenháveis da LI.")
    if _project_render_pairs(projeto) != expected:
        raise RuntimeError("GR-035: Data Sheet/layout não possui as mesmas quantidades da LI.")
    gerar_svg(projeto, catalogo, image_path)
    with image_path.open("a", encoding="utf-8") as f:
        f.write("\n<!-- GR-035 LI_QUANTITIES " + json.dumps(expected, ensure_ascii=False, sort_keys=True) + " -->\n")


def executar(args: argparse.Namespace) -> int:
    project_path, catalog_path, pipeline_path = Path(args.project), Path(args.catalog), Path(args.pipeline)
    schema_path, li_path, q_path = Path(args.schema), Path(args.li), Path(args.quantity_standard)
    output = Path(args.output_dir); output.mkdir(parents=True, exist_ok=True)
    projeto, catalogo, pipeline = carregar_json(project_path), carregar_json(catalog_path), carregar_json(pipeline_path)
    li, qreg = carregar_json(li_path), carregar_json(q_path)
    resultados = validar_schema(projeto, carregar_json(schema_path)) + avaliar(projeto, catalogo) + validar_li(projeto, catalogo, pipeline, li, qreg)

    qa_json, qa_md = gerar_relatorio(output, projeto, resultados)
    ds = gerar_datasheet(projeto, catalogo, resultados, sha256(project_path), sha256(catalog_path))
    ds_path = output / "AUT_PANEL_DATASHEET.json"; salvar_json(ds_path, ds)
    db_path = output / "AUT_PANEL_DATACENTER.sqlite3"; gerar_sqlite(catalogo, db_path)
    li_snapshot = output / "AUT_PANEL_LI.json"; salvar_json(li_snapshot, li)

    bom_json, bom_csv = gerar_bom(li, catalogo, output)
    image_path = output / "AUT_PANEL_LAYOUT.svg"
    gerar_imagem_pos_li(projeto, catalogo, li, bom_json, image_path)

    estado = status_final(resultados)
    man = manifesto(output, [project_path,catalog_path,pipeline_path,schema_path,li_path,q_path],
        [qa_json,qa_md,ds_path,db_path,li_snapshot,bom_json,bom_csv,image_path], estado)
    verificar_manifesto(man, output)
    print(json.dumps({"status":estado,"project_id":(projeto.get("project") or {}).get("id"),
        "sequence":["AUT_PANEL_LI.json","AUT_PANEL_BOM.json","AUT_PANEL_BOM.csv","AUT_PANEL_LAYOUT.svg"],"manifest":str(man)},ensure_ascii=False))
    if estado == REPROVADO: return 1
    if estado == HOLD and not args.allow_hold: return 2
    return 0


def principal() -> int:
    p = argparse.ArgumentParser()
    for flag in ("project","catalog","pipeline","schema","li","quantity-standard","output-dir"):
        p.add_argument("--"+flag, required=True)
    p.add_argument("--allow-hold", action="store_true")
    try:
        return executar(p.parse_args())
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"ERRO: {exc}", file=sys.stderr); return 3

if __name__ == "__main__":
    raise SystemExit(principal())
