# GitHub Toolchain — AUT Panel Engineering

This reference extends the AUT Panel Engineering Skill with the curated GitHub toolchain registry.

Canonical registry:
- `plugins/AUT_PANEL_GITHUB_TOOLCHAIN_V2.json`

Visual composition registry:
- `datacenter/AUT_PANEL_VISUAL_STANDARD_V2.yaml`

## Mandatory use order

1. Canonical project evidence and manufacturer documentation.
2. Deterministic engineering engines.
3. CAD/schematic/render tooling.
4. Protocol simulators and integration test tools.
5. QA/document tooling.
6. ML/evolution tooling only as advisory support.

No GitHub repository, Skill, plugin or generated artifact may override LI, BOM, Data Center, Data Sheet, validated dimensions, manufacturer evidence or Golden Rules.

## Tool families

- Schematics: Schemdraw, QElectroTech.
- CAD/geometry: FreeCAD, CadQuery, build123d, pythonOCC, DXF tooling.
- Layout: OR-Tools, NetworkX.
- PLC/IEC 61131-3: Beremiz, Structured Text parser/reference tooling.
- Protocols: Pymodbus, BAC0/BACpypes3, OPC UA, python-snap7.
- Rendering/QA: CairoSVG, OpenCV, Pillow-compatible imaging.
- PDF/documents: pikepdf, PyMuPDF, PDF conversion support.
- Data/contracts: Pydantic, DuckDB, SQLAlchemy.
- ML/evolution: River, MLflow, DVC, Evidently, Optuna, Prefect.

All integrations are opt-in and governed by pin/license/security/regression requirements.
