from pipeline.agents_v4_4 import AGENT_CONTRACTS, DOCUMENT_LAYOUT_POLICY, GOLDEN_CHECKS
from pipeline.validate_engineering import validate_project


def _base_doc(**overrides):
    doc = {
        "id": "MD-TEST",
        "document_type": "MD",
        "understanding_status": "APROVADO",
        "layout_immutable": True,
        "template_fingerprint": "sha256:abc",
        "changes": ["TEXT", "TOTAL_PAGES", "TOC_PAGE_REFERENCE"],
        "final_page_count": 12,
        "declared_total_pages": 12,
        "paragraph_spacing_immutable": True,
        "font_immutable": True,
        "legacy_gray_cleared": True,
        "current_revision_gray_continuous": True,
        "current_changes_marked": True,
        "toc_revision_marking_consistent": True,
        "render_all_pages": True,
        "inspect_all_pages": True,
        "current_revision_change_map": ["COMMENT-1"],
    }
    doc.update(overrides)
    return doc


def test_document_layout_policy_is_registered():
    assert GOLDEN_CHECKS["document_layout_immutable"] is True
    assert GOLDEN_CHECKS["document_text_only_edit"] is True
    assert GOLDEN_CHECKS["pagination_dynamic"] is True
    assert DOCUMENT_LAYOUT_POLICY["layout_is_immutable"] is True
    assert "PAGE_NUMBER" in DOCUMENT_LAYOUT_POLICY["dynamic_exceptions"]
    assert AGENT_CONTRACTS["DatacenterStructureAgent"]["preserve_source_template_fingerprint"] is True
    assert AGENT_CONTRACTS["DataSheetConsistencyAgent"]["preserve_internal_layout"] is True


def test_controlled_document_accepts_text_and_dynamic_pagination():
    assert validate_project({"documents": [_base_doc()]}) == []


def test_controlled_document_rejects_layout_mutation():
    findings = validate_project({"documents": [_base_doc(changes=["TEXT", "COLUMN_WIDTHS"]) ]})
    codes = {f.code for f in findings}
    assert "DOC-LAYOUT-MUTATION" in codes


def test_controlled_document_rejects_wrong_total_pages():
    findings = validate_project({"documents": [_base_doc(declared_total_pages=11)]})
    codes = {f.code for f in findings}
    assert "DOC-PAGINATION" in codes
    assert "MD_PAGINATION_MISMATCH" in codes


def test_md_rejects_spacing_mutation_and_legacy_gray():
    findings = validate_project({"documents": [_base_doc(
        paragraph_spacing_immutable=False,
        legacy_gray_cleared=False,
    )]})
    codes = {f.code for f in findings}
    assert "MD_PARAGRAPH_SPACING_MUTATION" in codes
    assert "MD_LEGACY_GRAY_PRESENT" in codes


def test_li_and_fd_require_datasheet_contract():
    li = _base_doc(
        id="LI-TEST",
        document_type="LI",
        document_subtype="OTHER",
        datasheet_layout_immutable=False,
        reference_validation_required=False,
    )
    findings = validate_project({"documents": [li]})
    codes = {f.code for f in findings}
    assert "DATASHEET-LAYOUT-LOCK" in codes
    assert "DATASHEET-REFERENCE" in codes
