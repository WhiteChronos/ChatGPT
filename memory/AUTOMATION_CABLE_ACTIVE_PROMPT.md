# Automation Cable Active Prompt

## Mission
Build a traceable engineering system for automation/instrumentation cable calculation, selection, validation, technical-document analysis, CAD/DWG/DXF processing, and learning from engineer-approved historical records.

## System of record
Repository: `WhiteChronos/ChatGPT`
Active branch: `feature/automation-cable-ml`
Pull request: #35

## Engineering invariants
- Scope is automation/instrumentation cables, not generic power-cable sizing.
- Deterministic engineering and manufacturer/protocol rules are authoritative.
- ML is advisory only: recommendation, ranking, similarity retrieval and anomaly detection.
- Every engineering claim must preserve source/provenance where available.
- Every substantive action must end with a durable GitHub checkpoint.
- GitHub history is the primary audit trail; external memory engines are secondary indexes.
- Calculation plugins are independent verifiers, never engineering authorities.
- PDF/image/CAD tooling must preserve document/drawing revision and provenance.
- No calculation of cable, conduit or cable tray starts before applicable project drawings are inserted, identified and registered.

## User-taught workflow
### Step 1 — Insert project drawings
Register all applicable drawings before calculations. Current registered drawings:
- DE-3501.02-8210-800-RPJ-703 Rev.0 — Automação — Planta Baixa — Térreo.
- DE-3501.02-8210-800-RPJ-704 Rev.0 — Automação — Planta Baixa — 1º Pavimento.

The drawings contain routing, cable tray/conduit information, AT/TT instruments, 4-20 mA + HART, discrete signals, network points, PN-AUT-001 and routing/detail tables. These are the current graphical basis for the next taught steps.

## Tool routing
- Calculation: deterministic rules + Wolfram verification when connected.
- PDF: Adobe Acrobat is available for PDF manipulation/OCR/extraction.
- Image analysis: built-in vision first; connected image tools for transformation/cleanup where justified.
- DWG/DXF: no dedicated trustworthy DWG plugin found; use LibreDWG, LibreCAD and DXF tooling with explicit validation.
- Diagrams/annotation: tldraw when connected; never as substitute for CAD.

## Current architecture
Engineering sources -> normalized datacenter records -> deterministic rule engine -> optional tool verification -> ML advisory layer -> engineer review -> approved training record -> memory/retrieval index.

## Current cable classes
4-20 mA, 0-10 V, 24 Vdc DI/DO, low-power 24 Vdc field supply, RTD, thermocouple, pulse/encoder, RS-485/Modbus RTU, CAN/CANopen, Profibus, Industrial Ethernet and safety signals.

## Last completed action
Captured user-taught workflow Step 1 and registered the two project automation drawings in the datacenter.

## Current objective
Learn and codify the user's step-by-step method for calculating conduits, cable trays and automation cables from the project drawings.

## Unresolved
- Await user's Step 2.
- Later implement deterministic calculation code only after the taught engineering workflow is fully captured.
- Define manufacturer/protocol source ingestion rules.
- Define native DWG conversion/validation test fixtures.

## Next action
Wait for and capture the user's Step 2 of the conduit/cable-tray/cable calculation method.

## Checkpoint protocol
After every substantive action: recover state -> execute -> validate -> append action checkpoint -> update this prompt -> update machine-readable process state -> confirm persistence.


### Step 6 — Calculate cable-tray route lengths
Use the automation panel as the common origin. For every distinct cable-tray route/path leaving the panel, create a separate route line/record and measure its path length on the project drawing.

Current taught rules:
- Every cable-tray calculation starts from the automation panel.
- Create one route line for each distinct path.
- Measure along the actual drawn route, following changes in direction.
- Convert drawing length to real project length using the drawing scale.
- For the current ground-floor plan, the user states the working scale is 1:50.
- Keep route identity separate so later loads/cables can be associated with the correct path.
- Do not yet apply occupancy, spare capacity, fitting allowance, vertical allowance or cable-count rules unless taught in a later step.

## Current learning state
Steps captured: 1 drawings, 2 automation panel, 3 routing types from legend, 4 instruments/signals/disciplines, 5 confirm symbols in legend, 6 cable-tray route measurement from the panel.
Next action: capture Step 7 from the user.


### Step 7 — Identify and calculate cable-tray reductions
After route-length measurement, inspect each cable-tray path for transitions where the tray changes section/dimensions. Treat every such transition as a distinct route component to be identified and calculated separately.

Current taught rules:
- Reductions are evaluated after the route path has been established.
- A reduction is tied to a specific route and location.
- Preserve upstream and downstream tray dimensions.
- Do not yet assign equivalent length, material code, quantity formula, fitting allowance or loss factor until explicitly taught.
- Keep reductions separate from straight cable-tray length.

Current interpretation from the project context: available tray sizes include 100x50 mm and 50x50 mm, so a transition between these sizes is a candidate reduction when actually shown in the route.

Next action: capture the user's detailed reduction calculation rule or Step 8.


### Step 8 — Continue routes between floors
Identify the project symbol that indicates a vertical rise/continuation to the next floor.

Taught rules:
- This symbol means the routing element does not terminate at that point.
- Continue tracing the same route in the drawing for the floor immediately above.
- Preserve route identity across the floor transition; do not create an unrelated new route merely because the drawing sheet changes.
- Record the origin floor, transition point, destination floor, source drawing and destination drawing.
- The next-floor drawing must be consulted to locate the corresponding continuation before the route is considered complete.
- Do not invent vertical distance, riser allowance, fitting quantity or transition length until the user teaches those rules.

Current project example:
DE-3501.02-8210-800-RPJ-703 (Térreo) -> vertical rise symbol -> DE-3501.02-8210-800-RPJ-704 (1º Pavimento).

Next action: capture Step 9 from the user.
