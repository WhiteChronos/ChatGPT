from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from pipeline.xlsx_layout_guard import compare_layout


def make_xlsx(path: Path, value: str, style_id: str = "1", width: str = "12") -> None:
    parts = {
        "[Content_Types].xml": "<Types xmlns='http://schemas.openxmlformats.org/package/2006/content-types'/>",
        "xl/workbook.xml": "<workbook xmlns='http://schemas.openxmlformats.org/spreadsheetml/2006/main'><sheets><sheet name='A' sheetId='1'/></sheets></workbook>",
        "xl/styles.xml": "<styleSheet xmlns='http://schemas.openxmlformats.org/spreadsheetml/2006/main'><fonts count='1'><font><sz val='8'/><name val='Arial'/></font></fonts></styleSheet>",
        "xl/worksheets/sheet1.xml": (
            "<worksheet xmlns='http://schemas.openxmlformats.org/spreadsheetml/2006/main'>"
            f"<cols><col min='1' max='1' width='{width}' customWidth='1'/></cols>"
            f"<sheetData><row r='1' ht='15' customHeight='1'><c r='A1' s='{style_id}' t='inlineStr'><is><t>{value}</t></is></c></row></sheetData>"
            "<mergeCells count='1'><mergeCell ref='A1:B1'/></mergeCells>"
            "<pageMargins left='0.5' right='0.5' top='0.5' bottom='0.5' header='0.2' footer='0.2'/>"
            "</worksheet>"
        ),
    }
    with ZipFile(path, "w", ZIP_DEFLATED) as archive:
        for name, text in parts.items():
            archive.writestr(name, text)


def test_text_change_does_not_change_layout_signature(tmp_path):
    baseline = tmp_path / "a.xlsx"
    candidate = tmp_path / "b.xlsx"
    make_xlsx(baseline, "TEXTO A")
    make_xlsx(candidate, "TEXTO B")
    assert compare_layout(baseline, candidate).match is True


def test_column_width_change_is_detected(tmp_path):
    baseline = tmp_path / "a.xlsx"
    candidate = tmp_path / "b.xlsx"
    make_xlsx(baseline, "TEXTO", width="12")
    make_xlsx(candidate, "TEXTO", width="13")
    report = compare_layout(baseline, candidate)
    assert report.match is False
    assert "xl/worksheets/sheet1.xml" in report.differing_parts


def test_style_change_is_detected(tmp_path):
    baseline = tmp_path / "a.xlsx"
    candidate = tmp_path / "b.xlsx"
    make_xlsx(baseline, "TEXTO", style_id="1")
    make_xlsx(candidate, "TEXTO", style_id="2")
    assert compare_layout(baseline, candidate).match is False
