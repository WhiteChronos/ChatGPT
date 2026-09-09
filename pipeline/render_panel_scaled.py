#!/usr/bin/env python3
"""Render/gate determinístico para painéis AUT sob padrão imutável.

O script NÃO redefine o padrão visual aprovado. Ele valida as baselines
(LI, Data Sheet, template e fingerprints) e só então chama o renderer
geométrico existente do projeto.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML é obrigatório: pip install pyyaml") from exc


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"YAML inválido: {path}")
    return data


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON inválido: {path}")
    return data


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def require(condition: bool, rule: str, message: str) -> None:
    if not condition:
        raise RuntimeError(f"{rule}: {message}")


def li_render_map(li: dict[str, Any]) -> dict[str, tuple[str, int]]:
    return {
        str(line["tag"]): (str(line["catalog_id"]), int(line["quantity"]))
        for line in li.get("lines", [])
        if line.get("render_required") is True
    }


def placement_map(project: dict[str, Any]) -> dict[str, tuple[str, int, str]]:
    return {
        str(p["li_tag"]): (str(p["catalog_id"]), int(p["quantity"]), str(p["surface"]))
        for p in project.get("placements", [])
    }


def validate(
    panel_id: str,
    li: dict[str, Any],
    project: dict[str, Any],
    golden: dict[str, Any],
    pipeline: dict[str, Any],
    templates: dict[str, Any],
    datacenter: dict[str, Any],
    datasheet_registry: dict[str, Any],
    approved_image_ref: Path | None,
) -> dict[str, Any]:
    require(golden.get("status") == "LOCKED_APPROVED_STANDARD" and golden.get("immutable") is True,
            "GR-041", "Golden Rules não estão bloqueadas.")
    ids = {str(x.get("id")) for x in golden.get("required_rules", [])}
    for rule_id in ("GR-034", "GR-035", "GR-036", "GR-037", "GR-038", "GR-039", "GR-040", "GR-041", "GR-042", "GR-043", "GR-044", "GR-045"):
        require(rule_id in ids, rule_id, "regra obrigatória ausente do registry.")

    seq = [str(x.get("id")) for x in pipeline.get("sequence", [])]
    expected_seq = ["DATACENTER", "DATASHEET", "SELECT", "LI_QUANTITY", "LOAD_BALANCE", "BOM", "LAYOUT", "RENDER_IMAGE", "QA", "RELEASE"]
    require(seq == expected_seq, "GR-041", f"sequência do pipeline alterada: {seq}")

    dc_panel = (datacenter.get("panels") or {}).get(panel_id) or {}
    ds_panel = (datasheet_registry.get("panels") or {}).get(panel_id) or {}
    tpl_panel = (templates.get("panels") or {}).get(panel_id) or {}
    require(bool(dc_panel and ds_panel and tpl_panel), "GR-041", f"painel {panel_id} não registrado em todos os contratos.")

    require(li.get("status") == "QUANTITY_FROZEN", "GR-034", "LI não está congelada.")
    require(li.get("li_id") == dc_panel.get("li_id") == ds_panel.get("li_id"), "GR-042", "li_id diverge da baseline.")
    require(li.get("revision") == dc_panel.get("li_revision"), "GR-042", "revisão da LI diverge da baseline.")
    require(li.get("project_id") == panel_id, "GR-042", "LI pertence a outro painel.")

    contract = project.get("production_contract") or {}
    render = project.get("render") or {}
    require(contract.get("workbook_template_id") == "XLSX-PN-AUT-01-MASTER-R02", "GR-039", "template de workbook divergente.")
    require(contract.get("standard_change_requires_explicit_authorization") is True, "GR-041", "controle de mudança desativado.")
    require(contract.get("one_panel_per_image") is True and render.get("one_panel_per_image") is True,
            "GR-040", "é obrigatório um painel por imagem.")
    require(render.get("visual_template_id") == tpl_panel.get("image_template_id") == ds_panel.get("image_template_id"),
            "GR-040", "template visual divergente da baseline.")

    require(project.get("enclosure", {}).get("external_mm") == ds_panel.get("enclosure_external_mm") == tpl_panel.get("enclosure_external_mm"),
            "GR-021", "dimensões externas divergem do template bloqueado.")
    require(project.get("enclosure", {}).get("mounting_plate_mm") == ds_panel.get("mounting_plate_mm") == tpl_panel.get("mounting_plate_mm"),
            "GR-022", "placa de montagem diverge do template bloqueado.")

    li_map = li_render_map(li)
    p_map = placement_map(project)
    require(set(li_map) == set(p_map), "GR-035", "tags desenháveis da LI e do layout divergem.")
    for tag, (cid, qty) in li_map.items():
        pcid, pqty, surface = p_map[tag]
        require((cid, qty) == (pcid, pqty), "GR-035", f"{tag}: quantidade/catalog_id diverge.")
        if tag.startswith("HMI-"):
            require(surface == "door", "GR-037", f"{tag}: IHM deve estar na porta.")

    expected_image_sha = str(tpl_panel.get("approved_reference_sha256"))
    require(expected_image_sha == dc_panel.get("approved_image_sha256") == ds_panel.get("approved_image_sha256"),
            "GR-044", "fingerprint visual divergente entre Data Center/Data Sheet/template.")
    if approved_image_ref is not None:
        require(approved_image_ref.exists(), "GR-044", "imagem de referência aprovada não encontrada.")
        require(sha256(approved_image_ref) == expected_image_sha, "GR-044", "SHA-256 da imagem aprovada não confere.")

    return {
        "panel_id": panel_id,
        "li_id": li.get("li_id"),
        "li_revision": li.get("revision"),
        "workbook_template_id": contract.get("workbook_template_id"),
        "image_template_id": render.get("visual_template_id"),
        "approved_image_sha256": expected_image_sha,
        "quantity_groups": li_map,
        "status": "VALIDATED_FOR_RENDER",
    }


def render_with_existing_engine(project_path: Path, catalog_path: Path, output: Path) -> None:
    try:
        from pipeline.aut_panel_control import carregar_json, gerar_svg
    except ImportError:
        try:
            from aut_panel_control import carregar_json, gerar_svg
        except ImportError as exc:
            raise RuntimeError("Não foi possível importar pipeline.aut_panel_control. Execute a partir da raiz do repositório.") from exc
    project = carregar_json(project_path)
    catalog = carregar_json(catalog_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    gerar_svg(project, catalog, output)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--panel-id", required=True, choices=["PN-AUT-01", "PN-AUT-02"])
    p.add_argument("--li", required=True)
    p.add_argument("--project", required=True)
    p.add_argument("--catalog", required=True)
    p.add_argument("--golden-rules", default="governance/golden_rules.yaml")
    p.add_argument("--pipeline", default="pipeline/pipeline.yaml")
    p.add_argument("--panel-template", default="templates/panel_template.yaml")
    p.add_argument("--datacenter", default="datacenter/datacenter.yaml")
    p.add_argument("--datasheet-registry", default="datasheet/datasheet.yaml")
    p.add_argument("--approved-image-ref")
    p.add_argument("--output", required=True)
    p.add_argument("--contract-output")
    args = p.parse_args()

    try:
        project_path = Path(args.project)
        catalog_path = Path(args.catalog)
        contract = validate(
            args.panel_id,
            load_json(Path(args.li)),
            load_json(project_path),
            load_yaml(Path(args.golden_rules)),
            load_yaml(Path(args.pipeline)),
            load_yaml(Path(args.panel_template)),
            load_yaml(Path(args.datacenter)),
            load_yaml(Path(args.datasheet_registry)),
            Path(args.approved_image_ref) if args.approved_image_ref else None,
        )
        render_with_existing_engine(project_path, catalog_path, Path(args.output))
        contract_output = Path(args.contract_output) if args.contract_output else Path(args.output).with_suffix(".contract.json")
        contract_output.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": "PASS", "output": args.output, "contract": str(contract_output)}, ensure_ascii=False))
        return 0
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"REPROVADO: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
