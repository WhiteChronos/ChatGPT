from pathlib import Path
import zipfile

from pipeline.font_fidelity_gate import evaluate_fonts, document_fonts, load_manifest


def _write_docx(path: Path) -> None:
    document = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:body>
<w:p><w:r><w:rPr><w:rFonts w:ascii="Petrobras Sans" w:hAnsi="Petrobras Sans"/></w:rPr><w:t>A</w:t></w:r></w:p>
<w:p><w:r><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/></w:rPr><w:t>B</w:t></w:r></w:p>
</w:body></w:document>"""
    styles = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:style w:type="paragraph" w:styleId="Normal"><w:rPr><w:rFonts w:ascii="Times New Roman"/></w:rPr></w:style>
</w:styles>"""
    font_table = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:fonts xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:font w:name="Petrobras Sans"/><w:font w:name="Arial"/><w:font w:name="Times New Roman"/>
</w:fonts>"""
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("word/document.xml", document)
        zf.writestr("word/styles.xml", styles)
        zf.writestr("word/fontTable.xml", font_table)


def test_docx_font_inventory_reads_source_families(tmp_path: Path) -> None:
    path = tmp_path / "fixture.docx"
    _write_docx(path)
    manifest = load_manifest()
    fonts = document_fonts(path, manifest)
    assert {"Petrobras Sans", "Arial", "Times New Roman"} <= fonts


def test_missing_exact_font_blocks_layout_fidelity() -> None:
    manifest = load_manifest()
    result = evaluate_fonts(
        {"Petrobras Sans", "Arial"},
        {"Arial", "Trebuchet MS"},
        manifest,
    )
    assert "Petrobras Sans" in result["missing_exact_fonts"]
    assert result["layout_fidelity_status"] == "NOT_VERIFIABLE_FROM_RENDER"
    row = next(item for item in result["fonts"] if item["family"] == "Petrobras Sans")
    assert row["support_fallback"] == "Trebuchet MS"
    assert row["support_fallback_available"] is True


def test_exact_fonts_allow_layout_fidelity() -> None:
    manifest = load_manifest()
    result = evaluate_fonts(
        {"Petrobras Sans", "Arial"},
        {"Petrobras Sans", "Arial"},
        manifest,
    )
    assert result["missing_exact_fonts"] == []
    assert result["layout_fidelity_status"] == "READY"


def test_public_manifest_forbids_font_binary_redistribution() -> None:
    manifest = load_manifest()
    assert manifest["policy"]["proprietary_font_binaries_must_not_be_committed"] is True
    for source in manifest["sources"]:
        if source["classification"].startswith(("MICROSOFT", "PROPRIETARY")):
            assert source["redistribution_in_public_repo"] is False
