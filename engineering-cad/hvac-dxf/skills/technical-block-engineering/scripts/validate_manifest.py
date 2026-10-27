#!/usr/bin/env python3
import argparse
from pathlib import Path
import yaml

VALID_CLASSES={"CAD_FABRICANTE","RECONSTRUCAO_FICHA","REFERENCIA_PROJETO","BLOQUEADO"}
VALID_CONFIDENCE={"HIGH","MEDIUM","LOW","BLOCKED"}
VALID_RELATIONSHIPS={"MANUFACTURER","AUTHORIZED_DISTRIBUTOR","AUTHORIZED_PARTNER","SYSTEM_INTEGRATOR","RESELLER","UNKNOWN"}
FINAL_AUTHORITY_RELATIONSHIPS={"MANUFACTURER","AUTHORIZED_DISTRIBUTOR","AUTHORIZED_PARTNER"}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("manifest")
    a=ap.parse_args()
    d=yaml.safe_load(Path(a.manifest).read_text(encoding="utf-8")) or {}
    errors=[]

    if d.get("source_class") not in VALID_CLASSES:
        errors.append("invalid source_class")
    if d.get("confidence") not in VALID_CONFIDENCE:
        errors.append("invalid confidence")

    g=d.get("geometry") or {}
    if g.get("units")!="m":
        errors.append("geometry.units must be m")
    if g.get("modelspace_scale")!="1:1":
        errors.append("geometry.modelspace_scale must be 1:1")

    final_geometry=d.get("source_class") in {"CAD_FABRICANTE","RECONSTRUCAO_FICHA"}
    if final_geometry:
        for k in ("equipment_family","manufacturer","exact_model"):
            if not str(d.get(k,"")).strip():
                errors.append(f"{k} must be non-empty for final geometry")

        s=d.get("sources") or {}
        if not any(s.get(k) for k in ("native_cad_url","dimensional_drawing_url","datasheet_pdf_url")):
            errors.append("final geometry requires an official technical source")

        q=d.get("qa") or {}
        for k in ("identity_confirmed","units_checked","extents_checked","visual_compared","provenance_complete"):
            if q.get(k) is not True:
                errors.append(f"qa.{k} must be true for final geometry")

        sa=d.get("supplier_authority") or {}
        relationship=str(sa.get("relationship","")).strip()
        status=str(sa.get("verification_status","")).strip()
        if relationship not in VALID_RELATIONSHIPS:
            errors.append("supplier_authority.relationship is invalid")
        elif relationship not in FINAL_AUTHORITY_RELATIONSHIPS:
            errors.append("final geometry supplier authority must be MANUFACTURER, AUTHORIZED_DISTRIBUTOR, or AUTHORIZED_PARTNER")

        if status!="VERIFIED":
            errors.append("supplier_authority.verification_status must be VERIFIED for final geometry")

        for k in ("brand","supplier_name","manufacturer_official_domain","official_verification_url","country_or_region","checked_date"):
            if not str(sa.get(k,"")).strip():
                errors.append(f"supplier_authority.{k} must be non-empty for final geometry")

    if errors:
        for e in errors:
            print("ERROR:",e)
        return 1

    print("OK: manifest passes geometry and supplier-authority checks")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
