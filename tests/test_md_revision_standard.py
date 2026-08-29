from pipeline.md_revision_standard import (
    GRAY,
    normalize_revision_gray,
    validate_md_document_metadata,
    validate_structure,
)


def _doc(paragraphs: str) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:body>' + paragraphs + '<w:sectPr><w:pgSz w:w="12240" w:h="15840"/></w:sectPr></w:body></w:document>'
    )


def _p(text1: str, text2: str = "", gray_first: bool = False) -> str:
    shd = f'<w:shd w:val="clear" w:color="auto" w:fill="{GRAY}"/>' if gray_first else ""
    r1 = f'<w:r><w:rPr>{shd}</w:rPr><w:t xml:space="preserve">{text1}</w:t></w:r>'
    r2 = f'<w:r><w:t xml:space="preserve">{text2}</w:t></w:r>' if text2 else ""
    return '<w:p><w:pPr><w:spacing w:before="0" w:after="120" w:line="276"/></w:pPr>' + r1 + r2 + '</w:p>'


def test_clears_legacy_gray_and_marks_only_current_revision():
    xml = _doc(_p("LEGADO", gray_first=True) + _p("Texto ", "revisado"))
    out, stats = normalize_revision_gray(xml, {"paragraph_indices": [1]})
    assert stats["legacy_gray_removed"] == 1
    assert "LEGADO</w:t></w:r>" in out
    legacy = out.split("</w:p>")[0]
    current = out.split("</w:p>")[1]
    assert GRAY not in legacy
    assert current.count(GRAY) == 2


def test_current_revision_gray_is_continuous_across_split_runs():
    xml = _doc(_p("partida ", "exclusivamente local"))
    out, _ = normalize_revision_gray(xml, {"paragraph_indices": [0]})
    assert out.count(GRAY) == 2
    assert "partida " in out
    assert "exclusivamente local" in out


def test_gray_patch_does_not_change_paragraph_spacing_or_section_properties():
    xml = _doc(_p("Texto ", "alterado"))
    out, _ = normalize_revision_gray(xml, {"paragraph_indices": [0]})
    assert validate_structure(xml, out) == []
    assert '<w:spacing w:before="0" w:after="120" w:line="276"/>' in out


def test_md_metadata_blocks_legacy_gray_or_spacing_mutation():
    doc = {
        "id": "MD-X",
        "document_type": "MD",
        "layout_immutable": True,
        "paragraph_spacing_immutable": False,
        "font_immutable": True,
        "legacy_gray_cleared": False,
        "current_revision_gray_continuous": True,
        "current_changes_marked": True,
        "toc_revision_marking_consistent": True,
        "render_all_pages": True,
        "inspect_all_pages": True,
        "current_revision_change_map": ["C14"],
        "final_page_count": 10,
        "declared_total_pages": 10,
    }
    codes = {f.code for f in validate_md_document_metadata(doc)}
    assert "MD_PARAGRAPH_SPACING_MUTATION" in codes
    assert "MD_LEGACY_GRAY_PRESENT" in codes
