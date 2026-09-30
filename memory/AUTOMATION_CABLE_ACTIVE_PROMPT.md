# Automation Cable Active Prompt

## Mission
Build a traceable engineering system for automation/instrumentation cable calculation, selection, validation, and learning from engineer-approved historical records.

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

## Current architecture
Engineering sources -> normalized datacenter records -> deterministic rule engine -> ML advisory layer -> engineer review -> approved training record -> memory/retrieval index.

## Current cable classes
4-20 mA, 0-10 V, 24 Vdc DI/DO, low-power 24 Vdc field supply, RTD, thermocouple, pulse/encoder, RS-485/Modbus RTU, CAN/CANopen, Profibus, Industrial Ethernet and safety signals.

## Memory architecture
Primary: GitHub commits + action ledger + active prompt + process state.
Secondary candidates: Mem0, Graphiti, Cognee, Hindsight, Letta, OpenMemory, memU.

## Last completed action
Created and validated the `automation-process-memory` skill and established the checkpoint/prompt-evolution protocol.

## Current objective
Implement deterministic automation-cable calculators and continuously capture approved engineering decisions as structured training records.

## Unresolved
- Select which secondary memory backend(s) will be activated first.
- Implement deterministic calculation code and tests.
- Define manufacturer/protocol source ingestion rules.
- Define minimum approved dataset threshold before first production ML model.

## Next action
Implement the first deterministic calculator module for 24 Vdc and 4-20 mA, with unit tests and checkpoint integration.

## Checkpoint protocol
After every substantive action: recover state -> execute -> validate -> append action checkpoint -> update this prompt -> update machine-readable process state -> confirm persistence.
