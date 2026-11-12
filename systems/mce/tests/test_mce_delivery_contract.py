"""Fail-closed regression: MCE must be approved P09 XLSX, not PDF/JSON."""
import hashlib
import importlib.util
from pathlib import Path

import pytest
from openpyxl import Workbook

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "mce_delivery_contract.py"
SPEC = importlib.util.spec_from_file_location("mce_delivery_gate", SCRIPT)
GATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GATE)


def blocked():
    return {
        "schema": "mce.delivery.v1", "request_kind": "MCE_XLSX",
        "state": GATE.BLOCKED, "artifacts": [],
        "blockers": ["model approval is missing"],
    }


def preliminary(root):
    workbook = Workbook()
    workbook.active.title = "FOLHA 1"
    workbook.active["C8"] = "Synthetic documented cause"
    path = root / "DE-000.00-0000-000-ABC-001-B - PV 01.xlsx"
    workbook.save(path)
    baseline = root / "source_approved_baseline.xlsx"
    workbook.save(baseline)
    return {
        "schema": "mce.delivery.v1", "request_kind": "MCE_XLSX",
        "state": GATE.PRELIMINARY,
        "artifacts": [{"role": "PRIMARY_MCE", "path": "DE-000.00-0000-000-ABC-001-B - PV 01.xlsx",
                       "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}],
        "preliminary_version": {"document_name": "DE-000.00-0000-000-ABC-001-B", "number": 1},
        "baseline": {"path": "source_approved_baseline.xlsx",
                     "sha256": hashlib.sha256(baseline.read_bytes()).hexdigest()},
        "approved_layout_profile": "P09_L50_APROVADO_VISUALMENTE",
        "gates": {key: True for key in GATE.REQUIRED_GATES},
        "coverage": {"causes_total": 1, "causes_reviewed": 1,
                     "observations_verified": 1, "x_total": 1, "x_verified": 1,
                     "pending_relations": 0, "all_applicable_effects_reviewed": True},
    }


def test_blocked_is_explicit_and_never_claims_matrix(tmp_path):
    assert GATE.validate(blocked(), tmp_path) == "PASS_BLOCKED_DECLARED"
    data = blocked()
    data["artifacts"] = [{"role": "AUXILIAR_NAO_E_MATRIZ", "path": "audit.json"}]
    assert GATE.validate(data, tmp_path) == "PASS_BLOCKED_DECLARED"


@pytest.mark.parametrize("role", ["PRIMARY_MCE", "PDF_PREVIEW"])
def test_blocked_cannot_offer_matrix_or_pdf_preview(tmp_path, role):
    data = blocked()
    data["artifacts"] = [{"role": role, "path": "audit.pdf"}]
    with pytest.raises(GATE.DeliveryBlocked, match="FAIL_FORMAT_CONTRACT"):
        GATE.validate(data, tmp_path)


@pytest.mark.parametrize("filename", ["audit.pdf", "analysis.json", "matriz.md"])
def test_non_xlsx_cannot_be_primary_mce(tmp_path, filename):
    data = preliminary(tmp_path)
    (tmp_path / filename).write_bytes(b"not an xlsx")
    data["artifacts"][0].update(path=filename, sha256=hashlib.sha256(b"not an xlsx").hexdigest())
    with pytest.raises(GATE.DeliveryBlocked, match="FAIL_FORMAT_CONTRACT"):
        GATE.validate(data, tmp_path)


def test_pdf_report_alone_never_satisfies_mce_request(tmp_path):
    data = preliminary(tmp_path)
    data["artifacts"] = [{"role": "AUXILIAR_NAO_E_MATRIZ", "path": "auditoria.pdf"}]
    with pytest.raises(GATE.DeliveryBlocked, match="FAIL_FORMAT_CONTRACT"):
        GATE.validate(data, tmp_path)


def test_missing_authorization_or_observation_blocks(tmp_path):
    data = preliminary(tmp_path)
    data["gates"]["authorization_recorded"] = False
    with pytest.raises(GATE.DeliveryBlocked, match="FAIL_ENGINEERING_GATE"):
        GATE.validate(data, tmp_path)
    data = preliminary(tmp_path)
    data["coverage"]["observations_verified"] = 0
    with pytest.raises(GATE.DeliveryBlocked, match="FAIL_ENGINEERING_GATE"):
        GATE.validate(data, tmp_path)


def test_unverified_x_and_pending_relations_block(tmp_path):
    data = preliminary(tmp_path)
    data["coverage"]["x_verified"] = 0
    with pytest.raises(GATE.DeliveryBlocked, match="FAIL_ENGINEERING_GATE"):
        GATE.validate(data, tmp_path)
    data = preliminary(tmp_path)
    data["coverage"]["pending_relations"] = 1
    with pytest.raises(GATE.DeliveryBlocked, match="FAIL_ENGINEERING_GATE"):
        GATE.validate(data, tmp_path)


def test_generic_sheet_and_corrupted_xlsx_rejected(tmp_path):
    data = preliminary(tmp_path)
    wb = Workbook()
    wb.active.title = "CONTROLE"
    wb.save(tmp_path / "DE-000.00-0000-000-ABC-001-B - PV 01.xlsx")
    data["artifacts"][0]["sha256"] = hashlib.sha256((tmp_path / "DE-000.00-0000-000-ABC-001-B - PV 01.xlsx").read_bytes()).hexdigest()
    with pytest.raises(GATE.DeliveryBlocked, match="FAIL_FORMAT_CONTRACT"):
        GATE.validate(data, tmp_path)
    (tmp_path / "DE-000.00-0000-000-ABC-001-B - PV 01.xlsx").write_bytes(b"bogus")
    data["artifacts"][0]["sha256"] = hashlib.sha256(b"bogus").hexdigest()
    with pytest.raises(GATE.DeliveryBlocked, match="FAIL_FORMAT_CONTRACT"):
        GATE.validate(data, tmp_path)


def test_requested_pdf_must_be_preview_and_equivalent(tmp_path):
    data = preliminary(tmp_path)
    data["pdf_requested"] = True
    with pytest.raises(GATE.DeliveryBlocked, match="FAIL_FORMAT_CONTRACT"):
        GATE.validate(data, tmp_path)
    (tmp_path / "DE-000.00-0000-000-ABC-001-B - PV 01.pdf").write_bytes(b"%PDF-1.7\nsynthetic")
    data["artifacts"].append({"role": "PDF_PREVIEW", "path": "DE-000.00-0000-000-ABC-001-B - PV 01.pdf"})
    with pytest.raises(GATE.DeliveryBlocked, match="FAIL_ENGINEERING_GATE"):
        GATE.validate(data, tmp_path)
    data["gates"]["pdf_equivalence_verified"] = True
    assert GATE.validate(data, tmp_path) == "PASS_MCE_DELIVERY_PREFLIGHT_ONLY"


def test_only_preliminary_status_permitted_and_workspace_bounded(tmp_path):
    data = preliminary(tmp_path)
    assert GATE.validate(data, tmp_path) == "PASS_MCE_DELIVERY_PREFLIGHT_ONLY"
    data["state"] = "PRODUCTION_COMPLETE"
    with pytest.raises(GATE.DeliveryBlocked, match="FAIL_FORMAT_CONTRACT"):
        GATE.validate(data, tmp_path)
    data = preliminary(tmp_path)
    data["artifacts"][0]["path"] = "../not_in_workspace.xlsx"
    with pytest.raises(GATE.DeliveryBlocked, match="FAIL_FORMAT_CONTRACT"):
        GATE.validate(data, tmp_path)


def test_version_identity_mismatch_is_rejected(tmp_path):
    data = preliminary(tmp_path)
    data["preliminary_version"]["number"] = 2
    with pytest.raises(GATE.DeliveryBlocked, match="FAIL_FORMAT_CONTRACT"):
        GATE.validate(data, tmp_path)


def test_old_filename_without_pv_is_rejected(tmp_path):
    data = preliminary(tmp_path)
    original = tmp_path / data["artifacts"][0]["path"]
    old_name = tmp_path / "MCE_PRELIMINAR.xlsx"
    old_name.write_bytes(original.read_bytes())
    data["artifacts"][0]["path"] = old_name.name
    with pytest.raises(GATE.DeliveryBlocked, match="FAIL_FORMAT_CONTRACT"):
        GATE.validate(data, tmp_path)


def test_pdf_must_match_pv_filename(tmp_path):
    data = preliminary(tmp_path)
    data["gates"]["pdf_equivalence_verified"] = True
    other = tmp_path / "outro_nome.pdf"
    other.write_bytes(b"%PDF-1.7\nsynthetic")
    data["artifacts"].append({"role": "PDF_PREVIEW", "path": other.name})
    with pytest.raises(GATE.DeliveryBlocked, match="FAIL_FORMAT_CONTRACT"):
        GATE.validate(data, tmp_path)

def test_legacy_preliminary_version_name_is_rejected(tmp_path):
    data = preliminary(tmp_path)
    original = tmp_path / data["artifacts"][0]["path"]
    legacy = tmp_path / "DE-000.00-0000-000-ABC-001-B (PRELIMINAR VERSÃO 01) PV 01.xlsx"
    legacy.write_bytes(original.read_bytes())
    data["artifacts"][0]["path"] = legacy.name
    with pytest.raises(GATE.DeliveryBlocked, match="FAIL_FORMAT_CONTRACT"):
        GATE.validate(data, tmp_path)


def test_document_revision_must_match_filename(tmp_path):
    data = preliminary(tmp_path)
    data["preliminary_version"]["document_name"] = "DE-000.00-0000-000-ABC-001-A"
    with pytest.raises(GATE.DeliveryBlocked, match="FAIL_FORMAT_CONTRACT"):
        GATE.validate(data, tmp_path)


def test_missing_baseline_bytes_never_delivers_pv(tmp_path):
    data = preliminary(tmp_path)
    del data["baseline"]
    with pytest.raises(GATE.DeliveryBlocked, match="FAIL_ENGINEERING_GATE"):
        GATE.validate(data, tmp_path)
    data = preliminary(tmp_path)
    (tmp_path / data["baseline"]["path"]).unlink()
    with pytest.raises(GATE.DeliveryBlocked, match="FAIL_FORMAT_CONTRACT"):
        GATE.validate(data, tmp_path)


def test_baseline_sha_mismatch_rejected(tmp_path):
    data = preliminary(tmp_path)
    data["baseline"]["sha256"] = "0" * 64
    with pytest.raises(GATE.DeliveryBlocked, match="FAIL_FORMAT_CONTRACT"):
        GATE.validate(data, tmp_path)


def test_pv_cannot_be_its_own_baseline(tmp_path):
    data = preliminary(tmp_path)
    data["baseline"] = {
        "path": data["artifacts"][0]["path"],
        "sha256": data["artifacts"][0]["sha256"],
    }
    with pytest.raises(GATE.DeliveryBlocked, match="FAIL_ENGINEERING_GATE"):
        GATE.validate(data, tmp_path)


def test_baseline_cannot_be_generic_tabular_workbook(tmp_path):
    data = preliminary(tmp_path)
    base = tmp_path / data["baseline"]["path"]
    generic = Workbook()
    generic.active.title = "CONTROLE"
    generic.save(base)
    data["baseline"]["sha256"] = hashlib.sha256(base.read_bytes()).hexdigest()
    with pytest.raises(GATE.DeliveryBlocked, match="FAIL_FORMAT_CONTRACT"):
        GATE.validate(data, tmp_path)


def test_baseline_cannot_be_hardlink_to_derived_pv(tmp_path):
    data = preliminary(tmp_path)
    primary = tmp_path / data["artifacts"][0]["path"]
    baseline = tmp_path / data["baseline"]["path"]
    baseline.unlink()
    baseline.hardlink_to(primary)
    data["baseline"]["sha256"] = data["artifacts"][0]["sha256"]
    assert baseline.resolve() != primary.resolve()
    assert baseline.samefile(primary)
    with pytest.raises(GATE.DeliveryBlocked, match="FAIL_ENGINEERING_GATE"):
        GATE.validate(data, tmp_path)
