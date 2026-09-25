# Document Fidelity & Engineering Interpretation Golden Rule v1.0

## Status
GOLDEN RULE / MANDATORY

## Purpose
Prevent document-review errors caused by confusing native document facts with parser output, re-rendered layout, OCR output, or format-conversion artifacts.

This rule applies to engineering DOC/DOCX/PDF drawings, specifications, memorials, lists, datasheets and scanned documents.

## Three-layer document model
Every material document claim SHALL distinguish:

1. **SOURCE_NATIVE_STRUCTURE** — metadata and structure stored by the authoring/native file format.
2. **SEMANTIC_EXTRACTION** — extracted text, tables and document hierarchy.
3. **VISUAL_RENDERING** — pages/images produced by a renderer for human visual QA.

No one layer may silently replace another.

## Pagination authority
Page/sheet count is a source-fidelity fact.

### DOCX
Preferred sources, in order:
1. native Microsoft Word extended property `docProps/app.xml -> Pages`, when present;
2. explicit document foliation/title-block value authored in the source;
3. native Microsoft Word rendering/export when available.

A LibreOffice/headless render count is a QA observation only. It SHALL NOT be used by itself to declare the source pagination wrong.

### Legacy DOC
Use OLE SummaryInformation / DocumentSummaryInformation metadata such as Number of Pages when available. An external conversion/render count remains secondary.

### PDF
The PDF page tree/native page count is authoritative for that PDF artifact. OCR segmentation does not redefine the PDF page count.

## Render mismatch rule
If a Word document reports one native page count and an external renderer produces another count, classify:

`RENDER_MISMATCH`

Do **not** create a document finding until the mismatch is resolved in the source-authoring environment or against an authoritative PDF/export.

Required fields:
- native_page_count;
- native_count_method;
- rendered_page_count;
- renderer;
- font_substitution_detected;
- pagination_status;
- confidence.

## Font fidelity gate
Before using a non-native renderer to make claims about page count, line wrapping, overflow, page breaks or sheet-specific placement:

1. inventory fonts requested by the source;
2. verify whether those exact fonts are installed;
3. record substitutions;
4. if material substitutions exist, layout-derived claims become `NOT_VERIFIABLE_FROM_RENDER` unless confirmed by a native export.

Metric-compatible substitutes may improve rendering but do not become source authority.

## Engineering interpretation workflow
Use a minimum three-pass review:

### Pass A — Structure & provenance
- file type;
- revision/date;
- native page/sheet count;
- authoring application metadata where available;
- document identifiers;
- section/header/footer fields;
- font inventory;
- hashes/provenance.

### Pass B — Semantic content
- headings;
- paragraphs;
- tables;
- tags;
- lists;
- cross-references;
- comments/revisions when available.

### Pass C — Visual verification
- drawings;
- title blocks;
- legends;
- tables;
- callouts;
- line routing;
- embedded images;
- page layout;
- clipping/overlap.

A finding that depends on information visible in only one layer SHALL be checked against the other relevant layers before promotion.

## Interpretation-conflict status
If structure, semantic extraction and visual rendering disagree, use:

`DOCUMENT_INTERPRETATION_CONFLICT`

The item remains pending/NOT_VERIFIABLE until resolved. Never select the most convenient representation silently.

## Page-location citation rule
When renderer pagination differs from native pagination:
- cite the authored folio/sheet identifier and section/title whenever possible;
- label renderer-only page positions as `renderer_page`;
- do not tell the user that the source document has a pagination error based only on renderer page count.

## Open-source assistance stack
Recommended supporting tools, each with a bounded role:

- `docling-project/docling` — layout-aware parsing, reading order, tables, images and structured document representation.
- `microsoft/markitdown` — lightweight semantic conversion to Markdown for LLM/text pipelines; not a high-fidelity renderer.
- `pymupdf/PyMuPDF` — native PDF page tree/count, text geometry, rendering and image inspection.
- `python-openxml/python-docx` + direct OOXML inspection — DOCX structure, paragraphs/tables plus package-level metadata.
- `decalage2/olefile` — legacy OLE/Word .doc metadata and property streams.
- `LibreOffice/core` — useful cross-platform renderer/converter, but not source authority for Word pagination when layout reflows.
- `PaddlePaddle/PaddleOCR` — structure-aware OCR/document AI for scanned pages/images.
- `ocrmypdf/OCRmyPDF` — searchable OCR layer for scanned PDFs while preserving the PDF artifact.
- `Unstructured-IO/unstructured` — document partitioning/chunking for downstream semantic pipelines.

## Tool-role guard
A tool's output is evidence about the tool's interpretation, not automatically evidence about the source artifact.

Examples:
- renderer page count != native Word page count;
- OCR text != guaranteed authored text;
- Markdown conversion != layout truth;
- parser table reconstruction != guaranteed cell geometry.

## Regression incident
Known failure mode:
- native Word document metadata says 15 pages;
- external LibreOffice-based rendering reflows to 17 pages;
- reviewer incorrectly flags `1 de 15` as a source pagination error.

Permanent prevention:
- native metadata wins for source page count;
- render mismatch is recorded separately;
- font substitutions are audited before layout conclusions.

## Confidentiality
Do not commit confidential project files or proprietary source text to a public repository. Regression tests must use synthetic fixtures only.

## Exact-font source and provisioning gate
For layout-sensitive validation of Word documents, exact font families referenced by the source must be available to the renderer.

The governed source manifest is `datacenter/DOCUMENT_FONT_FIDELITY_MANIFEST.json`.

Rules:
- proprietary font binaries must never be committed to the public repository;
- Petrobras Sans must be obtained from an authorized Petrobras/corporate brand source;
- Microsoft families such as Arial, Arial Black, Calibri, Courier New, Times New Roman, Wingdings, Tahoma and Symbol must come from a licensed Windows/Office installation or other authorized Microsoft/Monotype source;
- Trebuchet MS may be used only as a support/fallback font where the identity guidance permits it; it is not an exact-layout substitute for Petrobras Sans;
- if an exact required family is missing, page-count, line-wrap, overflow and page-break claims from an external render are `NOT_VERIFIABLE_FROM_RENDER`;
- use `pipeline/font_fidelity_gate.py` before layout-sensitive rendering and `pipeline/with_private_fonts.sh` to expose a caller-supplied licensed font directory to the renderer.
