---
name: aut-panel-qa-release
description: Run cross-artifact QA and release gating for PN automation-panel engineering packages. Use before Excel/PDF/image release, after component or enclosure changes, or when reconciling LI, BOM, I/O, load, datasheet, layout, geometry, image, source evidence, and memory.
---

# AUT Panel QA & Release

Release only when all deterministic and evidence gates pass.

## Workflow
1. Compare LI, BOM, load, Data Sheet, I/O, communication, layout, geometry, image, and references.
2. Verify quantities, exact catalog numbers, dimensions, tags, voltages, currents, protocols and capacities.
3. Check no stale dimensions remain after enclosure changes.
4. Check gateway capacity against field-equipment count.
5. Verify source registry: official doc, page/section, date, lifecycle, supplier/channel, validator A/B, reverification.
6. Verify MODEL 001 structure and image directive compliance.
7. Verify memory/Data Center synchronization and downstream invalidations.
8. Keep HOLD if any release-critical fact is unresolved. CI green is not engineering approval.

## Required release state
No open engineering HOLD, no quantity/dimensional conflict, validated official sources, dual validation, reverification, and user/human gate when required.
