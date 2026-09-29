from __future__ import annotations

import copy
import json
from pathlib import Path

from pipeline.li_technical_dossier import enrich_li

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def test_dossier_covers_every_line_of_both_frozen_lis():
    dossier = load_json("datacenter/AUT_PANEL_LI_TECHNICAL_DOSSIER.json")
    covered = {x["catalog_id"] for x in dossier["records"]}
    for li_path in ("li/PN-AUT-01_LI.json", "li/PN-AUT-02_LI.json"):
        li = load_json(li_path)
        assert li["status"] == "QUANTITY_FROZEN"
        assert {x["catalog_id"] for x in li["lines"]} <= covered


def test_enriched_li_preserves_quantities_and_adds_documentation():
    li = load_json("li/PN-AUT-01_LI.json")
    dossier = load_json("datacenter/AUT_PANEL_LI_TECHNICAL_DOSSIER.json")
    out = enrich_li(li, dossier)
    assert [(x["tag"], x["quantity"]) for x in out["lines"]] == [
        (x["tag"], x["quantity"]) for x in li["lines"]
    ]
    assert all("technical_documentation" in x for x in out["lines"])


def test_current_baseline_is_hold_when_exact_datasheet_is_missing():
    li = load_json("li/PN-AUT-01_LI.json")
    dossier = load_json("datacenter/AUT_PANEL_LI_TECHNICAL_DOSSIER.json")
    out = enrich_li(li, dossier)
    assert out["status"] == "HOLD"
    codes = {x["code"] for x in out["holds"]}
    assert "HOLD_LI_TECHNICAL_DOCUMENTATION" in codes
    assert out["release_state_label"].startswith("ELÉTRICO INTEGRADO")


def test_family_document_does_not_close_exact_model_hold():
    li = {"li_id":"TEST","project_id":"TEST","revision":"R00","status":"QUANTITY_FROZEN","lines":[
        {"tag":"PLC-01","catalog_id":"SIEMENS-S7-1500-REF","quantity":1}
    ]}
    dossier = load_json("datacenter/AUT_PANEL_LI_TECHNICAL_DOSSIER.json")
    out = enrich_li(li, dossier)
    assert out["status"] == "HOLD"
    assert out["lines"][0]["technical_documentation"]["release_eligible"] is False


def test_all_exact_and_verified_docs_can_pass_the_dossier_gate():
    li = {"li_id":"TEST","project_id":"TEST","revision":"R00","status":"QUANTITY_FROZEN","lines":[
        {"tag":"XT-01","catalog_id":"PHOENIX-PT25-3209510","quantity":1}
    ]}
    dossier = load_json("datacenter/AUT_PANEL_LI_TECHNICAL_DOSSIER.json")
    local = copy.deepcopy(dossier)
    rec = next(x for x in local["records"] if x["catalog_id"]=="PHOENIX-PT25-3209510")
    rec["release_eligible"] = True
    out = enrich_li(li, local)
    assert out["status"] == "PASS"
    assert not out["holds"]
