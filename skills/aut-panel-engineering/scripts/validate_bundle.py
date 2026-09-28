#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
from pathlib import Path

REQUIRED_STATUS = {"VALIDADO", "REFERENCIA", "HOLD", "REPROVADO"}
REQUIRED_SEQUENCE = ["DATACENTER", "DATASHEET", "SELECT", "LI_QUANTITY", "LOAD_BALANCE", "BOM", "LAYOUT", "RENDER_IMAGE", "QA", "RELEASE"]

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("manifest")
    data = json.loads(Path(p.parse_args().manifest).read_text(encoding="utf-8"))
    errors = []
    if data.get("sequence") and data["sequence"] != REQUIRED_SEQUENCE:
        errors.append("canonical_sequence_mismatch")
    if data.get("engineering_status") is not None and data["engineering_status"] not in REQUIRED_STATUS:
        errors.append("invalid_engineering_status")
    if data.get("image_is_quantity_source") is True:
        errors.append("image_cannot_be_quantity_source")
    if data.get("ml", {}).get("auto_apply_locked_changes") is True:
        errors.append("ml_cannot_auto_apply_locked_changes")
    print(json.dumps({"status": "PASS" if not errors else "REPROVADO", "errors": errors}, ensure_ascii=False, indent=2))
    return 0 if not errors else 2

if __name__ == "__main__":
    raise SystemExit(main())
