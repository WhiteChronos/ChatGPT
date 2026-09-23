# Automation Hyperfocus Golden Rule v1.0

## Status
MANDATORY / BLOCK_ON_FAILURE

## Purpose
Define the default internal engineering elaboration model for multidisciplinary compatibility reviews with hyperfocus on Automation and Data.

This rule extends `governance/VISUALIZE_GOLDEN_RULE_v1_0.md`. It does not replace source evidence, approved discipline baselines, or the canonical compatibility gate.

## Protocol Zero — question before finding
Machine-enforced policy: `QUESTION_BEFORE_FINDING`.

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
`/visualize` remains the presentation layer and SHALL be rendered through **@Build Web Data Visualization** (`Plugin_40dab999fe9c8191bbc2f550371692fc`) for every engineering compatibility report, re-evaluation, audit result, comparison result, or interactive technical report produced for this project.

This renderer is a **Golden Rule requirement**, not a preference.

Mandatory behavior:
- use @Build Web Data Visualization as the final presentation surface;
- do not substitute Markdown-only output, generic GenUI, a different dashboard renderer, or another visualization app when the requested report is expected in this format;
- if the plugin action is unavailable in the current runtime, do not silently fall back to another renderer; state that the required renderer is unavailable and wait for the plugin capability to be exposed;
- preserve complete technical depth and do not reduce the report to a summary;
- keep questions/doubts visually separated from confirmed findings/errors and from engineering problems;
- provide a simple answer field for every open technical question;
- expose evidence location, comparison, impact, solution, affected documents and closure criterion for every confirmed finding;
- show NOT_VERIFIABLE items separately and never visually present them as confirmed errors;
- include filters for severity/status when supported;
- include the release gate as a distinct final module.

The visualization SHALL expose at least:
- executive overview;
- source documents and revisions;
- baseline map;
- TAG x TAG inventory;
- resolved questions;
- unanswered questions with answer fields;
- verified facts;
- confirmed findings/errors;
- engineering problems;
- non-errors / justified differences;
- Automation / HVAC / Electrical / Network & Data / Functional Logic views when applicable;
- solutions;
- documents to adjust;
- action plan;
- release gate.

Questions must be readable and must provide a simple answer field when user input is expected.

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
