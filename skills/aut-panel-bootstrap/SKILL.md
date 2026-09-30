---
name: aut-panel-bootstrap
description: Bootstrap and reconcile the canonical context for an industrial automation panel project before any engineering work. Use when starting a new PN panel, resuming an existing PN, changing revisions, loading project documents, or when conflicting panel IDs, dimensions, LI/BOM revisions, memories, or visual baselines must be resolved before downstream work.
---

# AUT Panel Bootstrap

Load and reconcile the project before engineering. Fail closed on conflicts.

## Workflow
1. Load canonical project premises, Data Center, Data Sheet, current LI/BOM, pipeline, Golden Rules, MODEL 001, image directive, and project memory.
2. Identify PANEL_ID and revision. Never mix panel-scoped state.
3. Compare dimensions, quantities, topology, selected models, HOLDs, and revision status across sources.
4. Apply authority order: controlled project document -> canonical premises -> target Data Sheet -> LI/BOM -> calculations -> official manufacturer data -> visual model.
5. Record conflicts explicitly. Do not let image or chat memory override canonical engineering data.
6. Produce a bootstrap manifest with canonical inputs, SHAs when available, unresolved conflicts, and downstream invalidations.
7. Stop with HOLD when a material conflict remains.

## Critical rules
- MODEL 001 is visual structure only, never a source of target-panel dimensions.
- For new panels, enclosure H/W/D are engineering outputs.
- For existing frozen revisions, enclosure changes require controlled revision.
- Never silently reuse another panel's quantities or dimensions.

## Output
Return: PANEL_ID, REVISION, authoritative sources, current enclosure, current LI/BOM, active HOLDs, invalidated downstream artifacts, and next executable stage.
