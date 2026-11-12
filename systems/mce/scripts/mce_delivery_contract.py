#!/usr/bin/env python3
"""Fail-closed MCE output-routing gate. NOT a substitute for engineering review.

Validates a private artifact manifest and real file types; all claims of
engineering/visual verification must be independently evidenced elsewhere.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path
from defusedxml import ElementTree as ET

SCHEMA = "mce.delivery.v1"
BLOCKED = "NAO_EMITIDO_BLOQUEADO"
PRELIMINARY = "MCE_PRELIMINAR_PARA_REVISAO"
REQUIRED_GATES = (
    "model_approved", "sources_verified", "cell_contract_approved",
    "authorization_recorded", "functional_relations_verified",
    "layout_p09_verified", "ooxml_audited", "excel_windows_qa",
)


class DeliveryBlocked(ValueError):
    pass


def fail(category: str, reason: str) -> None:
    raise DeliveryBlocked(f"{category}: {reason}")


def private_file(root: Path, value: object) -> Path:
    if not isinstance(value, str) or not value or Path(value).is_absolute():
        fail("FAIL_FORMAT_CONTRACT", "artifact must have relative path inside private workspace")
    base = root.resolve()
    target = (base / value).resolve()
    try:
        target.relative_to(base)
    except ValueError:
        fail("FAIL_FORMAT_CONTRACT", "artifact escapes the private workspace")
    if not target.is_file():
        fail("FAIL_FORMAT_CONTRACT", "declared artifact file is absent")
    return target


def inspect_xlsx(path: Path, digest: object) -> None:
    if path.suffix.lower() != ".xlsx":
        fail("FAIL_FORMAT_CONTRACT", "primary MCE must be XLSX")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        fail("FAIL_FORMAT_CONTRACT", "missing/invalid primary SHA-256")
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        fail("FAIL_FORMAT_CONTRACT", "primary SHA-256 mismatch")
    if not zipfile.is_zipfile(path):
        fail("FAIL_FORMAT_CONTRACT", "primary is not an OOXML ZIP")
    try:
        with zipfile.ZipFile(path) as archive:
            if archive.testzip() is not None or "xl/workbook.xml" not in archive.namelist():
                fail("FAIL_FORMAT_CONTRACT", "corrupt XLSX container")
            xml = ET.fromstring(archive.read("xl/workbook.xml"))
            sheets = [e.attrib["name"] for e in xml.iter() if e.tag.rsplit("}", 1)[-1] == "sheet"]
    except (zipfile.BadZipFile, RuntimeError, ET.ParseError, KeyError):
        fail("FAIL_FORMAT_CONTRACT", "invalid XLSX workbook")
    if not sheets or sheets != [f"FOLHA {n}" for n in range(1, len(sheets) + 1)]:
        fail("FAIL_FORMAT_CONTRACT", "MCE requires sequential FOLHA N sheets")


def validate(manifest: object, root: Path) -> str:
    if not isinstance(manifest, dict) or manifest.get("schema") != SCHEMA or manifest.get("request_kind") != "MCE_XLSX":
        fail("FAIL_FORMAT_CONTRACT", "missing MCE_XLSX request classification")
    state = manifest.get("state")
    artifacts = manifest.get("artifacts")
    roles = {"PRIMARY_MCE", "PDF_PREVIEW", "AUXILIAR_NAO_E_MATRIZ"}
    if not isinstance(artifacts, list) or any(not isinstance(a, dict) or a.get("role") not in roles for a in artifacts):
        fail("FAIL_FORMAT_CONTRACT", "invalid artifact list or role")
    primary = [a for a in artifacts if a["role"] == "PRIMARY_MCE"]
    previews = [a for a in artifacts if a["role"] == "PDF_PREVIEW"]
    if state == BLOCKED:
        if primary or previews:
            fail("FAIL_FORMAT_CONTRACT", "blocked request must not advertise an MCE or preview")
        blockers = manifest.get("blockers")
        if not isinstance(blockers, list) or not blockers or any(not isinstance(b, str) or not b.strip() for b in blockers):
            fail("FAIL_ENGINEERING_GATE", "state blocked without concrete reason")
        return "PASS_BLOCKED_DECLARED"
    if state != PRELIMINARY or len(primary) != 1 or len(previews) > 1:
        fail("FAIL_FORMAT_CONTRACT", "MCE must have one XLSX primary and optional PDF")
    gates = manifest.get("gates")
    if not isinstance(gates, dict) or any(gates.get(key) is not True for key in REQUIRED_GATES):
        fail("FAIL_ENGINEERING_GATE", "model, source, contract, authorization, relationship or QA gate absent")
    profile = manifest.get("approved_layout_profile")
    if not isinstance(profile, str) or not profile.startswith("P09_"):
        fail("FAIL_FORMAT_CONTRACT", "missing project-approved P09 layout profile")
    coverage = manifest.get("coverage")
    if not isinstance(coverage, dict):
        fail("FAIL_ENGINEERING_GATE", "missing coverage evidence")
    total = coverage.get("causes_total")
    if type(total) is not int or total <= 0:
        fail("FAIL_ENGINEERING_GATE", "invalid cause count")
    if any(type(coverage.get(k)) is not int or coverage[k] != total
           for k in ("causes_reviewed", "observations_verified")):
        fail("FAIL_ENGINEERING_GATE", "cause observations and review incomplete")
    x_total = coverage.get("x_total")
    if type(x_total) is not int or x_total < 0 or type(coverage.get("x_verified")) is not int or coverage["x_verified"] != x_total:
        fail("FAIL_ENGINEERING_GATE", "unverified cause/effect crosses")
    if coverage.get("all_applicable_effects_reviewed") is not True or type(coverage.get("pending_relations")) is not int or coverage["pending_relations"] != 0:
        fail("FAIL_ENGINEERING_GATE", "pending cause/effect relationships")
    p = private_file(root, primary[0].get("path"))
    # DEC-MCE-078: PV is the mandatory document name; it is not homologation.
    pat = re.fullmatch(
        r"(?P<doc>[A-Za-z0-9][A-Za-z0-9._=-]{0,159}) - PV "
        r"(?P<ver>[0-9]{2,})\.xlsx", p.name
    )
    if pat is None:
        fail("FAIL_FORMAT_CONTRACT", "primary filename must use CODIGO-REVISAO - PV NN")
    version_number = int(pat.group("ver"))
    if version_number < 1 or pat.group("ver") != f"{version_number:02d}":
        fail("FAIL_FORMAT_CONTRACT", "PV number must be canonical and positive")
    version = manifest.get("preliminary_version")
    if (not isinstance(version, dict)
            or version.get("document_name") != pat.group("doc")
            or type(version.get("number")) is not int or version["number"] != version_number):
        fail("FAIL_FORMAT_CONTRACT", "PV document identity/number not recorded consistently")
    # Independent on-disk baseline is mandatory: a self-declared boolean gate
    # cannot prove that the original industrial workbook is available.
    baseline = manifest.get("baseline")
    if not isinstance(baseline, dict):
        fail("FAIL_ENGINEERING_GATE", "baseline XLSX bytes and SHA-256 are missing")
    original = private_file(root, baseline.get("path"))
    if original.resolve() == p.resolve() or original.samefile(p):
        fail("FAIL_ENGINEERING_GATE", "baseline must be distinct from derived PV")
    inspect_xlsx(original, baseline.get("sha256"))
    inspect_xlsx(p, primary[0].get("sha256"))
    if manifest.get("pdf_requested") is True and not previews:
        fail("FAIL_FORMAT_CONTRACT", "requested PDF is not attached as a preview")
    if previews:
        preview = private_file(root, previews[0].get("path"))
        if preview.name != p.with_suffix(".pdf").name or preview.read_bytes()[:5] != b"%PDF-":
            fail("FAIL_FORMAT_CONTRACT", "invalid PDF preview")
        if gates.get("pdf_equivalence_verified") is not True:
            fail("FAIL_ENGINEERING_GATE", "PDF/XLSX equivalence not verified")
    return "PASS_MCE_DELIVERY_PREFLIGHT_ONLY"


def main() -> int:
    cli = argparse.ArgumentParser(description="MCE XLSX output format preflight")
    cli.add_argument("--manifest", type=Path, required=True)
    cli.add_argument("--root", type=Path, required=True)
    args = cli.parse_args()
    try:
        print(validate(json.loads(args.manifest.read_text(encoding="utf-8")), args.root))
    except (OSError, json.JSONDecodeError, DeliveryBlocked) as exc:
        print(str(exc) if isinstance(exc, DeliveryBlocked) else "FAIL_FORMAT_CONTRACT: missing/invalid private manifest")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
