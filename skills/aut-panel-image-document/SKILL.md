---
name: aut-panel-image-document
description: Compose the Step 6 engineering image document for one industrial automation panel PN after the Step 5 physical image set is frozen. Use to build the final per-panel visual document with principal-component legend, panel data, electrical architecture, communication architecture, command diagram, and dimensional block while preserving the Step 5 geometry exactly. Enforce grow-only canvas, no resizing of dimensional views, deterministic vector diagrams, consistent MODEL 001 composition, and mathematical dimension QA.
---

# AUT Panel Step 6 — Engineering Image Document

Execute only after `STEP5_PN_IMAGE_FIDELITY_FROZEN` for the same PANEL_ID and revision.

Step 6 does not regenerate the panel. It composes the already-validated Step 5 physical image set with engineering information.

## Required blocks
For each PN include:
- validated physical panel view(s) from Step 5;
- legend of principal components;
- panel/project data;
- electrical architecture;
- communication architecture;
- command diagram;
- panel dimensioning block.

Use MODEL 001 as the document-composition baseline, never as the source of physical panel dimensions.

Read `references/document-composition-contract.md` before composition.

## Geometry lock
- Import Step 5 images/geometry without re-scaling dimensional content.
- Keep H/W/D, object positions, tags and quantities unchanged.
- Never use generative editing to move, remove, add or resize engineering geometry.
- If Step 6 finds a physical error, invalidate Step 5 and return upstream; do not fix it cosmetically.

## Canvas growth rule
Engineering geometry and text blocks do not shrink to fit a fixed page.
1. Define each block at its required native size.
2. Compute all block bounding boxes.
3. Grow the canvas horizontally/vertically until all blocks fit with required margins.
4. Keep dimensional-image `scale_x = scale_y = 1.0`.
5. Never apply non-uniform scaling.

Use `scripts/plan_grow_only_canvas.py` for deterministic canvas planning.

## Dimension fidelity
Dimensioned views preserve the same project H/W/D used in Step 5.
- Generate dimension annotations from controlled values, not raster measurement.
- Front dimensions show real H and W.
- Side/depth dimensions show real D on the actual depth axis.
- 3/4 appearance never substitutes for orthographic dimension source.
- Use Wolfram or equivalent deterministic math for independent checks.

## Architecture and command diagrams
Electrical architecture is generated from validated power/load topology.
Communication architecture is generated from validated endpoint/gateway/network topology.
Command diagram is generated from approved control logic/I/O/communication basis.
Never invent devices, protocols, I/O points, interlocks or safety functions.

## Vector-first diagrams
Prefer QElectroTech/SchemDraw/SVG/CairoSVG or other governed vector tooling for electrical/command blocks and NetworkX/SVG for communication topology. Rasterize only at final composition if required.

Whiteboard/diagram plugins may assist review but do not become engineering authority.

## Legend and data blocks
Legend maps tag -> description -> manufacturer/model where appropriate. Avoid decorative manufacturer logos.

Panel data uses controlled PROJECT_NUMBER, PANEL_ID, revision, H/W/D, supply, command voltage, UPS/autonomy, IP requirement, thermal/cooling basis and other approved values required by MODEL 001.

## Consistency QA
Verify:
- Step 5 fingerprint matches inserted panel image;
- LI quantities equal depicted physical instances;
- dimensions equal controlled H/W/D;
- electrical architecture matches load/power topology;
- communication architecture matches endpoint/gateway topology;
- command diagram matches approved logic/I/O basis;
- no block was downscaled to fit;
- canvas is large enough for native-size blocks;
- text remains legible at issue resolution.

## Required outputs
Per PANEL_ID:
- STEP6_ENGINEERING_DOCUMENT_MANIFEST;
- final engineering image document;
- source vector/diagram artifacts where applicable;
- STEP6_DOCUMENT_QA_REPORT;
- STEP6_ENGINEERING_IMAGE_DOCUMENT_FROZEN.

Each PN gets a separate engineering document image.
