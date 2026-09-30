---
name: aut-panel-li-load-quantification
description: Create the Step 4 material list and per-panel electrical load workbook for industrial automation panels after project scope, panel definition, and normative/academic review are frozen. Use when ChatGPT must quantify every physical panel item, internal wiring, DIN rail, ducts, terminals, accessories, connection hardware, panel assembly materials, links to official manufacturer documentation/suppliers, and electrical load for each PN with deterministic geometric and electrical calculations. The workbook must contain only one MATERIALS sheet and one LOAD sheet per PN.
---

# AUT Panel Step 4 — LI + Load Quantification

Execute only after STEP1_SCOPE_FROZEN, STEP2_PANEL_DEFINITION_FROZEN, and STEP3_NORMATIVE_ACADEMIC_BASE_FROZEN.

## Core output contract
Create a single workbook with exactly two sheets per panel and no other sheets:
- <PANEL_ID>_MATERIAIS
- <PANEL_ID>_CARGA

For N panels, create exactly 2N sheets.

Read references/workbook-contract.md before building the workbook.

## Workflow
1. Load PROJECT_NUMBER, panel register, parameter registry, Step 3 evidence, current Data Sheet, I/O/communication inventories, manufacturer catalogs, and exact component candidates.
2. Build the connection graph before calculating internal wiring. Every conductor must have origin, destination, signal/power class, section, color/ID rule, route and termination points.
3. Build the physical layout geometry in millimetres before calculating linear materials. Use official dimensions/clearances.
4. Quantify every physical item used in the panel. Do not omit small assembly items.
5. Calculate internal wiring and other linear materials from actual geometry/routes, not rules of thumb.
6. Calculate electrical load per PN from official current/power data and validated duty/diversity rules.
7. Reconcile quantities against connection graph, layout, terminal plan and component accessory requirements.
8. Insert official product, datasheet/manual, and supplier/authorized-channel links directly in the material sheet.
9. Run deterministic QA. Do not create image/layout release artifacts from an unclosed LI.

## Quantity rule
Follow references/quantity-rules.md.

For each internal conductor:
cut_length = routed_path + origin_termination + destination_termination + service_loop

Procurement quantity may add only an explicit project/manufacturing allowance stored as a parameter. Never hide a default waste factor.

Aggregate wire by exact family/section/color/voltage class or other project-controlled procurement code.

Use scripts/quantify_internal_wiring.py when a route JSON is available.

## Mandatory material coverage
Include, when used:
- enclosure, mounting plate, doors/panels and accessories;
- PLC/CPU, I/O, communication modules, gateways, switch, HMI;
- power supplies, UPS, batteries, DC/DC converters;
- breakers, fuses, fuse holders, disconnects, SPD and protection accessories;
- relays, contactors, interface modules and sockets;
- terminals, PE terminals, shield terminals, jumpers, bridges, end stops and separators;
- DIN rail and all rail accessories;
- cable duct/trunking, covers and fittings;
- internal conductors by section/color/type with calculated metres;
- PE/bonding conductors and door bonding braids;
- Ethernet/fieldbus/internal communication cables and connectors;
- ferrules, lugs, ring/fork terminals, heat-shrink and markers;
- cable glands, blanking plugs, grommets and cable-entry systems;
- labels, device markers, terminal markers and wire markers;
- cooling/heating/thermostat/hygrostat equipment and mounting kits;
- screws, nuts, washers, spacers, brackets and manufacturer mounting kits;
- any other item physically consumed by the assembly.

If an item is required by a manufacturer's installation/accessory chain, include it even if absent from a conceptual diagram.

## Load sheet rule
Create one load sheet per PN only. Include each powered device/load with official voltage, current or power, quantity, UPS-critical flag, duty/diversity rule if applicable, raw load, design load, heat loss where available, source REF_ID, and official link.

Do not merge different PN loads into one sheet.

## Tool routing
Read references/toolchain.md.

Use deterministic tools in this order:
- manufacturer CAD/dimensions -> physical geometry;
- QElectroTech/WireViz/QetWireManager or equivalent governed tooling -> connection/wire list support;
- NetworkX -> connection graph validation;
- OR-Tools -> optional routing optimization;
- FreeCAD/CadQuery/build123d -> real-scale geometry and measured paths;
- Wolfram -> independent arithmetic, area, volume, length, fill and load cross-checks;
- spreadsheet engine -> final workbook formulas and traceability.

Diagram/whiteboard plugins may support review but never define quantities.

## Sources and learning material
Use Step 3 sources plus manufacturer installation manuals, official training material, recognized academic/technical references, and assembly videos as secondary procedural evidence. Manufacturer documentation and applicable standards outrank videos.

A video may teach an assembly method; it may not establish a product rating, conductor ampacity, protection setting, enclosure rating or normative requirement.

## QA gates
Reject or hold when:
- quantity has no mathematical/documentary basis;
- wire metres are estimated without connection graph + layout route;
- exact accessory chain is incomplete;
- product link/model mismatch exists;
- materials sheet and load sheet refer to different revisions;
- powered item appears in materials but is missing from load without a documented reason;
- route geometry or panel dimensions are stale;
- another sheet is added to the workbook.

## Outputs
- LI_LOAD_WORKBOOK
- MATERIAL_QUANTITY_TRACE
- INTERNAL_WIRE_CUTLIST
- LOAD_CALCULATION_TRACE
- STEP4_LI_LOAD_FROZEN

The workbook is a controlled output. If any exact quantity changes, create a new revision and invalidate dependent layout/image artifacts.
