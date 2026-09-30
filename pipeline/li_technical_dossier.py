#!/usr/bin/env python3
"""Join frozen LI quantities with controlled manufacturer technical documentation.

This module never mutates the source LI. It emits a derived enriched LI artifact and
fails closed when a line lacks exact, traceable technical documentation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

PASS = "PASS"
HOLD = "HOLD"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _index_dossier(dossier: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {
        str(x.get("catalog_id")): x
        for x in dossier.get("records", [])
        if x.get("catalog_id")
    }


def enrich_li(li: Mapping[str, Any], dossier: Mapping[str, Any]) -> dict[str, Any]:
    index = _index_dossier(dossier)
    enriched = []
    holds = []
    for line in li.get("lines", []):
        cid = str(line.get("catalog_id") or "")
        tag = str(line.get("tag") or "")
        doc = index.get(cid)
        if doc is None:
            holds.append({
                "code": "HOLD_LI_TECHNICAL_DOSSIER_MISSING",
                "tag": tag,
                "catalog_id": cid,
                "detail": "Linha da LI sem registro no dossiê técnico.",
            })
            technical = None
        else:
            technical = {
                "manufacturer": doc.get("manufacturer"),
                "family": doc.get("family"),
                "model": doc.get("model"),
                "category": doc.get("category"),
                "catalog_or_family_url": doc.get("catalog_or_family_url"),
                "datasheet_or_technical_page_url": doc.get("datasheet_or_technical_page_url"),
                "installation_manual_url": doc.get("installation_manual_url"),
                "communication_manual_url": doc.get("communication_manual_url"),
                "cad_or_dimension_url": doc.get("cad_or_dimension_url"),
                "document_status": doc.get("document_status"),
                "lifecycle_status": doc.get("lifecycle_status"),
                "lifecycle_note": doc.get("lifecycle_note"),
                "consultation_date": doc.get("consultation_date"),
                "release_eligible": bool(doc.get("release_eligible")),
            }
            if not technical["catalog_or_family_url"]:
                holds.append({
                    "code": "HOLD_LI_CATALOG_MISSING",
                    "tag": tag,
                    "catalog_id": cid,
                    "detail": "Catálogo/família oficial ainda não vinculado.",
                })
            if not technical["datasheet_or_technical_page_url"]:
                holds.append({
                    "code": "HOLD_LI_DATASHEET_MISSING",
                    "tag": tag,
                    "catalog_id": cid,
                    "detail": "Ficha técnica/página técnica exata ainda não vinculada.",
                })
            if not technical["release_eligible"]:
                holds.append({
                    "code": "HOLD_LI_TECHNICAL_DOCUMENTATION",
                    "tag": tag,
                    "catalog_id": cid,
                    "detail": str(technical["document_status"] or "DOCUMENT_STATUS_MISSING"),
                })

        record = dict(line)
        record["technical_documentation"] = technical
        enriched.append(record)

    return {
        "schema_version": "1.0",
        "artifact_id": f"{li.get('li_id','LI')}-TECHNICAL-DOSSIER",
        "source_li_id": li.get("li_id"),
        "project_id": li.get("project_id"),
        "revision": li.get("revision"),
        "source_li_status": li.get("status"),
        "source_li_immutable": True,
        "status": HOLD if holds else PASS,
        "release_state_label": (
            'ELÉTRICO INTEGRADO / DADOS A COMPLETAR / RELEASE HOLD / “A DO QUADRO” NÃO INVENTADO'
            if holds else
            "DOCUMENTAÇÃO TÉCNICA DA LI COMPLETA / SUJEITA AOS DEMAIS GATES DE RELEASE"
        ),
        "lines": enriched,
        "holds": holds,
        "policy": {
            "frozen_li_not_mutated": True,
            "exact_part_number_requires_exact_datasheet": True,
            "family_catalog_does_not_close_exact_model_hold": True,
            "manufacturer_primary_source_required": True,
            "two_validators_before_release": True,
            "reverify_before_release": True,
        },
    }


def build(li_path: Path, dossier_path: Path, output: Path) -> dict[str, Any]:
    li = json.loads(li_path.read_text(encoding="utf-8"))
    dossier = json.loads(dossier_path.read_text(encoding="utf-8"))
    result = enrich_li(li, dossier)
    result["source_hashes"] = {
        "li_sha256": _sha256(li_path),
        "dossier_sha256": _sha256(dossier_path),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--li", required=True)
    parser.add_argument("--dossier", default="datacenter/AUT_PANEL_LI_TECHNICAL_DOSSIER.json")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        result = build(Path(args.li), Path(args.dossier), Path(args.output))
        print(json.dumps({"status": result["status"], "output": args.output}, ensure_ascii=False))
        return 0 if result["status"] == PASS else 3
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"HOLD: {exc}")
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
