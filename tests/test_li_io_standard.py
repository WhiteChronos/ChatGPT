import json
from pathlib import Path

from pipeline.agents_v4_6 import AGENT_CONTRACTS, GOLDEN_CHECKS, LI_IO_MODEL_ID
from pipeline.validate_engineering import validate_project


def valid_li(**overrides):
    doc = {
        "id": "LI-TEST",
        "document_type": "LI",
        "document_subtype": "LI_IO",
        "understanding_status": "APROVADO",
        "layout_immutable": True,
        "datasheet_layout_immutable": True,
        "reference_validation_required": True,
        "template_fingerprint": "sha256:template",
        "model_fingerprint": "sha256:model",
        "source_fingerprint": "sha256:source",
        "output_fingerprint": "sha256:output",
        "model_id": LI_IO_MODEL_ID,
        "sheet_count_source": "TARGET_DOCUMENT",
        "template_sheet_count_forced": False,
        "target_sheet_count": 4,
        "final_page_count": 4,
        "declared_total_pages": 4,
        "layout_signature_match": True,
        "font_signature_match": True,
        "cell_dimensions_match": True,
        "print_settings_match": True,
        "only_authorized_cell_changes": True,
        "notes_sheet_role": "NOTES_SUMMARY_REFERENCES",
        "ad_hoc_note_on_final_sheet": False,
        "changes": ["TEXT", "TECHNICAL_VALUES", "AUTHORIZED_FORMULAS", "TOTAL_PAGES"],
        "io_summary": {
            "DI": {"used": 7, "reserve": 9, "total": 16},
            "DO": {"used": 4, "reserve": 12, "total": 16},
        },
        "reference_codes": [
            "DE-3501.01-8210-800-RPJ-1000",
            "DE-3501.01-8210-800-RPJ-1001",
            "MD-3501.01-8210-800-RPJ-1000",
        ],
    }
    doc.update(overrides)
    return doc


def codes(doc):
    return {finding.code for finding in validate_project({"documents": [doc]})}


def test_li_io_standard_registered():
    assert GOLDEN_CHECKS["li_io_model_required"] is True
    assert GOLDEN_CHECKS["sheet_count_target_driven"] is True
    assert GOLDEN_CHECKS["font_signature_required"] is True
    assert AGENT_CONTRACTS["LIInputOutputModelAgent"]["model_id"] == LI_IO_MODEL_ID
    assert AGENT_CONTRACTS["PluginRegistryAgent"]["auto_install"] is False


def test_valid_li_passes():
    assert validate_project({"documents": [valid_li()]}) == []


def test_rejects_template_sheet_count_copy():
    result = codes(valid_li(sheet_count_source="VISUAL_TEMPLATE", template_sheet_count_forced=True))
    assert "LI-IO-SHEET-SOURCE" in result
    assert "LI-IO-TEMPLATE-SHEET-COUNT" in result
    assert "DOC-TEMPLATE-SHEET-COUNT" in result


def test_rejects_font_or_layout_change():
    result = codes(valid_li(font_signature_match=False, layout_signature_match=False))
    assert "LI-IO-FONT-SIGNATURE" in result
    assert "LI-IO-LAYOUT-SIGNATURE" in result


def test_rejects_note_on_final_sheet():
    assert "LI-IO-FINAL-NOTE" in codes(valid_li(ad_hoc_note_on_final_sheet=True))


def test_rejects_wrong_io_total():
    bad = {"DI": {"used": 7, "reserve": 9, "total": 17}}
    assert "LI-IO-COUNT-MISMATCH" in codes(valid_li(io_summary=bad))


def test_registry_disables_auto_install():
    registry_path = Path("plugins/document_tooling_registry.json")
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    assert registry["policy"]["auto_install_forbidden"] is True
    assert all(item.get("auto_install") is False for item in registry["repositories"])
