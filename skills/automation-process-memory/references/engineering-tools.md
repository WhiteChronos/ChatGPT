# Engineering tool routing

## Calculation
- Use project deterministic formulas and rules as the primary engineering authority.
- When connected, use Wolfram for independent algebraic, numerical, symbolic, unit, statistical, and sanity-check verification.
- Never allow a generic computation plugin to override manufacturer, protocol, project, or normative constraints.
- Checkpoint formulas, units, inputs, outputs, assumptions, tolerances, and verifier identity.

## Images and technical drawings
- Use built-in vision first for uploaded technical images, diagrams, nameplates, screenshots and datasheets.
- Use connected image/document tools for cleanup, enhancement, conversion or document-integrated editing where useful.
- Use OpenCV-style deterministic processing for edge/line/contour/perspective/geometry comparison tasks when repeatability is required.
- Never infer real dimensions from pixels without a trustworthy scale/reference.

## PDF
- Prefer Adobe Acrobat when available for page manipulation, OCR, conversion, merge/split, reorder, redaction and scan extraction.
- Preserve page number, document identifier, revision, sheet, source hash/provenance and evidence location.
- Open-source parsing references: `pymupdf/PyMuPDF` and `jsvine/pdfplumber`.

## DWG / DXF / CAD
No dedicated trustworthy DWG ChatGPT plugin is assumed.

Preferred open-source references:
- `LibreDWG/libredwg` for DWG read/write/conversion.
- `LibreCAD/LibreCAD` for 2D CAD/DXF inspection/editing.
- DXF Python tooling such as the ezdxf ecosystem for programmatic DXF creation/manipulation.
- `opencv/opencv` only for raster preprocessing or geometry-assistance, not as CAD authority.

Rules:
- Preserve original DWG as source evidence whenever possible.
- Use DXF as an interoperable derivative when generation/editing is required.
- Never silently alter units, UCS/coordinates, layers, blocks, text styles, linetypes, scales or insertion points.
- Validate entities, blocks, layers, units, extents, text and geometry after conversion.
- Record source hash, tool/converter version, output hash, warnings and conversion notes.

## Diagramming
- tldraw may be used for explanatory diagrams, process maps and image annotation when connected.
- tldraw output is not a substitute for native CAD geometry or DWG/DXF validation.
