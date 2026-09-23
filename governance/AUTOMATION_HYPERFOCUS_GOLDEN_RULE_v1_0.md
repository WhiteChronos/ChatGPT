# Automation Hyperfocus Golden Rule v1.0

## Status
MANDATORY / BLOCK_ON_FAILURE

## Purpose
Define the default internal engineering elaboration model for multidisciplinary compatibility reviews with hyperfocus on Automation and Data.

This rule extends `governance/VISUALIZE_GOLDEN_RULE_v1_0.md`. It does not replace source evidence, approved discipline baselines, or the canonical compatibility gate.

## Protocol Zero — question before finding
Every suspected discrepancy SHALL begin as an explicit technical question.

The required sequence is:

```text
QUESTION -> SOURCE CHECK -> ANSWER -> RED TEAM -> CLASSIFICATION -> FINDING -> ACTION
```

Rules:
- A difference between documents is not automatically an error.
- If the question is unanswered, classify the matter as `NOT_VERIFIABLE` / pending.
- An unanswered question SHALL NOT be promoted to a confirmed finding.
- A finding may be promoted only after the technical doubt is answered or the evidence proves a direct contradiction.
- Conservative electrical values, minimum-versus-higher protection classes, reserve capacity, and alternative design bases SHALL be tested before being classified as errors.
- Project decisions and documentary facts must remain distinguishable.

## Hyperfocus Automation + Data
The primary review perspective is the complete automation chain:

```text
PROCESS / HVAC REQUIREMENT
-> EQUIPMENT / TAG
-> POWER / PROTECTION
-> COMMAND / FEEDBACK
-> I/O
-> PLC / RTU
-> CONTROL LOGIC
-> INDUSTRIAL NETWORK
-> PROTOCOL / REGISTER
-> DATA QUALITY
-> HMI / SCADA
-> ALARM / HISTORY
-> FAT / SAT / OPERATION
```

For each applicable equipment or TAG, verify:
- physical function and location;
- power supply and source panel;
- local/manual/automatic command authority;
- DI/DO/AI/AO;
- network endpoint and protocol;
- register/point mapping, datatype, scale and engineering unit;
- feedback, alarms and failure detection;
- permissives, interlocks and safe state;
- loss of network, loss of PLC, loss of power and return-to-service behavior;
- HMI/SCADA presentation;
- historical/trend requirements;
- FAT/SAT testability and maintenance behavior.

## Data lineage
Critical data SHALL be traceable from authoritative source to final consumer:

```text
SOURCE DOCUMENT
-> NORMALIZED MASTER DATA
-> CONTROL POINT
-> PLC TAG
-> NETWORK REGISTER
-> HMI / SCADA TAG
-> ALARM / TREND / HISTORY
```

For relevant variables, record source, timestamp or revision context, quality, value, unit, range, scale, status, ownership and destination.

## Baseline hierarchy
A discipline designated as master for a physical attribute SHALL be treated as the authoritative source for that attribute until a later approved revision changes the baseline.

Derived disciplines SHALL not silently overwrite master values.

## Functional-state review
When applicable, test:
- NORMAL;
- MANUAL;
- OFF;
- AUTOMATIC;
- LOCAL;
- REMOTE;
- MAINTENANCE;
- STARTING;
- STOPPING;
- FAILED;
- NETWORK LOST;
- POWER LOST;
- POWER RESTORED;
- EMERGENCY;
- EQUIPMENT UNAVAILABLE.

## Red Team
Before accepting a solution, challenge at least:
- loss of Ethernet/fieldbus;
- loss of 24 Vdc;
- PLC restart;
- HMI/SCADA loss;
- invalid or stale data;
- equipment non-response;
- selector left in MANUAL/OFF;
- feedback mismatch;
- incompatible motor/drive/interface;
- exhausted switch ports;
- vendor point-map mismatch;
- replacement equipment with different interface.

## Value engineering
Architecture-impact questions SHALL compare, when relevant:
- current solution;
- simplest valid solution;
- more robust solution;
- lower-CAPEX option;
- lower-OPEX option;
- centralized vs distributed control;
- lifecycle maintainability and commissioning complexity.

No hardware is retained only because it appears in an older drawing.

## Visualization
`/visualize` remains the presentation layer. It SHALL preserve complete technical depth and expose:
- resolved questions;
- unanswered questions;
- verified facts;
- confirmed findings;
- non-errors / justified differences;
- solutions;
- document actions;
- release gate.

Questions must be readable and, in interactive reports, must provide a simple answer field when user input is expected.

## Compatibility scoring
Do not publish a compatibility percentage before:
- denominator and method are explicit;
- baseline is current/reconciled;
- unresolved questions are separated from confirmed findings;
- NOT_VERIFIABLE reduces coverage but is excluded from compatibility denominator per repository policy.

A deliberately superseded document SHALL not be used to create a misleadingly low score for a replacement baseline.

## Release gate
A package SHALL remain BLOCK when an unresolved question can materially change:
- equipment inventory;
- automation architecture;
- I/O;
- network/protocol;
- control philosophy;
- electrical protection or supply;
- safety/interlock behavior;
- FAT/SAT acceptance criteria.

## Repository memory
Repository memory is maintained in `memory/ENGINEERING_COMPATIBILITY_MEMORY.md`.
It is engineering-process memory, not personal account memory, and SHALL contain no confidential project source content in this public repository.
