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

## Memory architecture
Primary: GitHub commits + action ledger + active prompt + process state.
Secondary candidates: Mem0, Graphiti, Cognee, Hindsight, Letta, OpenMemory, memU.

## Last completed action
Expanded the persistence skill with engineering tool routing for calculation, image analysis, PDF and DWG/DXF/CAD; registered open-source CAD/PDF/image references and plugin candidates.

## Current objective
Implement deterministic automation-cable calculators and continuously capture approved engineering decisions and evidence from PDFs/images/CAD drawings as structured records.

## Unresolved
- Connect Wolfram if desired for independent calculation verification.
- Connect tldraw if desired for diagramming/annotation.
- Implement deterministic calculation code and tests.
- Define manufacturer/protocol source ingestion rules.
- Define native DWG conversion/validation test fixtures.
- Define minimum approved dataset threshold before first production ML model.

## Next action
Implement the first deterministic calculator module for 24 Vdc and 4-20 mA, with unit tests, optional Wolfram verification hooks, and checkpoint integration.

## Checkpoint protocol
After every substantive action: recover state -> execute -> validate -> append action checkpoint -> update this prompt -> update machine-readable process state -> confirm persistence.
