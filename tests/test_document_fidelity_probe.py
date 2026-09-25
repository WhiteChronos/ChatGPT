from pathlib import Path
import zipfile

from pipeline.document_fidelity_probe import probe


def _write_synthetic_docx(path: Path, pages: int = 15) -> None:
    app = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">
  <Pages>{pages}</Pages>
  <Application>Microsoft Office Word</Application>
</Properties>"""
    document = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:r><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/></w:rPr><w:t>Synthetic engineering document</w:t></w:r></w:p>
    <w:p><w:r><w:rPr><w:rFonts w:ascii="Petrobras Sans" w:hAnsi="Petrobras Sans"/></w:rPr><w:t>Source fidelity fixture</w:t></w:r></w:p>
  </w:body>
</w:document>"""
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("docProps/app.xml", app)
        zf.writestr("word/document.xml", document)


def test_native_docx_count_wins_over_external_render_count(tmp_path: Path) -> None:
    path = tmp_path / "fixture.docx"
    _write_synthetic_docx(path, pages=15)
    result = probe(path, rendered_page_count=17, renderer="LibreOffice")
    assert result["native_page_count"] == 15
    assert result["native_count_method"] == "DOCX_APP_XML_PAGES"
    assert result["rendered_page_count"] == 17
    assert result["pagination_status"] == "RENDER_MISMATCH"
    assert result["render_count_is_source_authority"] is False


def test_docx_font_inventory_is_extracted(tmp_path: Path) -> None:
    path = tmp_path / "fixture.docx"
    _write_synthetic_docx(path)
    result = probe(path)
    assert "Arial" in result["requested_fonts"]
    assert "Petrobras Sans" in result["requested_fonts"]
