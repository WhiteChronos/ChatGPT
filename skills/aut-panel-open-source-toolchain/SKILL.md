---
name: aut-panel-open-source-toolchain
description: Curate, evaluate, and govern open-source repositories and ChatGPT plugins for industrial automation-panel engineering. Use when adding or reviewing CAD/3D, geometry QA, layout optimization, schematic rendering, workflow orchestration, research, memory, calculations, image tooling, or agent frameworks that may extend the AUT Panel system without weakening source authority or deterministic engineering gates.
---

# AUT Panel Open-Source Toolchain

Treat external tools as candidates until they pass governance.

## Workflow
1. Read `references/toolchain-registry.md` and the repository registries in GitHub.
2. Map the requested capability to the smallest viable tool class.
3. Prefer existing validated project tooling before adding another dependency.
4. For every new repository/tool, record repository, role, active/archived state, default branch, proposed use, and evidence source.
5. Require version or commit pinning, license review, security review, sandbox validation, reproducibility test, and regression coverage before promotion.
6. Never auto-install a new core dependency or grant it engineering authority.
7. Keep generative/image/3D reconstruction tools downstream of deterministic geometry.
8. Record approved, optional, rejected, and superseded tools separately.

## Capability routing
- CAD/solid geometry: manufacturer STEP/IGES first, then FreeCAD, OpenCascade, CadQuery, build123d.
- Geometry QA: trimesh, Open3D.
- BIM/IFC: IfcOpenShell; pyRevit only with an authorized Revit environment.
- Render: Blender after geometry lock.
- Layout optimization: OR-Tools.
- Schematic/vector: SchemDraw and approved SVG/PDF tooling.
- Graph/topology: NetworkX.
- Research: Tavily, Firecrawl, Scite, Consensus.
- Mathematical checks: Wolfram.
- Structured operational memory: Airtable/Coda/Notion; Engram only as supplemental long-term memory.
- Agent frameworks: AutoGen, LangGraph, CrewAI may be studied as architecture references; do not replace the project agent registry automatically.

## Promotion gate
A candidate becomes ACTIVE only after:
`DISCOVER -> PIN -> LICENSE -> SECURITY -> SANDBOX -> TEST -> REGRESSION -> HUMAN_GATE -> VERSION`.

Generated outputs and plugin results never outrank controlled project documents, Data Center, target Data Sheet, LI/BOM, calculations, official manufacturer data, or standards.
