---
name: aut-panel-engineering
description: Governed engineering workflow for industrial automation panels, including technical research, source validation, per-panel Data Center/Data Sheet control, LI/BOM, PLC/RTU I/O, load balance, deterministic layout/rendering, QA, database persistence, agent memory, and machine-learning-assisted improvement proposals. Use when creating, reviewing, revising, validating, or evolving automation-panel deliverables that must remain traceable to official sources and approved baselines.
---

# AUT Panel Engineering

Operate as a governed multi-agent engineering system. Preserve approved standards and require explicit authorization before changing locked geometry, templates, quantities, pipeline order, or Golden Rules.

## Canonical workflow

1. Bootstrap rules, panel memory, Data Center, Data Sheet, LI baseline, and approved visual template.
2. Ingest project drawings, manuals, datasheets, I/O lists, LI/BOM, and official manufacturer sources.
3. Validate sources and register reference metadata.
4. Select exact components only when compatibility and lifecycle are supported by evidence.
5. Freeze LI quantities.
6. Calculate 24 Vdc, 127 Vac, and 220 Vac load balance.
7. Generate BOM strictly from frozen LI.
8. Produce layout from BOM and real dimensions.
9. Render one image per panel without distortion.
10. Run structural, semantic, visual, source, and cross-artifact QA.
11. Update memory/database after QA.
12. Release only with no critical HOLD or REPROVADO.

Never derive engineering quantity from a generated image.

## Evidence hierarchy

Use manufacturer site, official manual/datasheet, manufacturer technical portal, official standards, authorized distributor, official representative/integrator, approved internal engineering documents, then secondary sources only as labeled support.

Register document code/revision/date, page or section, official link, consultation date, lifecycle, project application, and validation status.

## Multi-agent model

Use the repository registry `agents/AUT_PANEL_AGENT_SYSTEM.yaml`. Keep each agent inside its declared read/write scope and logical Data Center/memory namespace. Source validation A and B must remain independent.

## Learning loop

Use:

`OBSERVE -> FEATURE_EXTRACT -> TRAIN/EVALUATE -> PROPOSE -> SANDBOX_SIMULATE -> QA -> HUMAN_GATE -> APPLY -> VERSION`

ML is advisory. Deterministic gates always have precedence. Never let ML alter Golden Rules, locked templates, LI baselines, or exact component selections automatically. Use `LEARNING_COLD_START` until enough human-reviewed labels exist.

## Database

Use SQLite as the offline baseline via `database/aut_panel_schema.sql` and `pipeline/aut_panel_db.py`. PostgreSQL/Supabase may be optional deployment targets without changing the logical schema. Keep released history append-only.

## Image quality

Prefer deterministic vector generation and constraint optimization before generative images. Keep the front/door view as master geometry, one physical scale, real component dimensions, no distortion, and no item outside the validated BOM.

## Status

Use `VALIDADO`, `REFERENCIA`, `HOLD`, and `REPROVADO`. Software CI success does not clear an engineering HOLD.

## Final QA

Verify source traceability, dual validation when required, LI/BOM/layout/render parity, exact model/lifecycle, load traceability, geometry, database/memory consistency, artifact hashes, ML provenance when used, and absence of unauthorized standard mutation.

Read `references/architecture.md`, `references/quality-contract.md`, and `references/database-schema.md` when those topics are needed. Use `scripts/validate_bundle.py` for lightweight local manifest checks.
