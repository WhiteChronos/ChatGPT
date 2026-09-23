# Automation Compatibility Report Model v1.0

## Status
GOLDEN RULE / MANDATORY

## Purpose
Define the reusable report model for Automation engineering compatibility reviews. This model is project-agnostic and SHALL be used for every Automation project unless an approved project-specific rule is stricter.

It extends:
- `governance/VISUALIZE_GOLDEN_RULE_v1_0.md`
- `governance/AUTOMATION_HYPERFOCUS_GOLDEN_RULE_v1_0.md`
- `governance/ENGINEERING_COMPATIBILITY_HARDENING_v1_1.md`

## Rendering
The default renderer is `/visualize`, using the best interactive visualization surface available in the runtime.

When executable, **@Build Web Data Visualization** is the preferred enhanced renderer. Its absence SHALL NOT block visualization.

Markdown-only output does not satisfy this model when an interactive renderer is available.

## Mandatory report modules
Every report SHALL expose, at minimum:

1. Executive overview and Release Gate.
2. Source documents, revisions and baseline status.
3. Baseline architecture map.
4. TAG x TAG / equipment x signal traceability.
5. Resolved questions.
6. Open questions with answer fields.
7. Confirmed findings/errors.
8. Engineering problems and risks.
9. Compatible / VERIFIED items.
10. NOT_VERIFIABLE items and missing evidence.
11. Automation architecture.
12. Network, protocol and data.
13. Functional logic / Cause & Effect.
14. Power, 24 Vdc and UPS where applicable.
15. Solutions and alternatives.
16. Documents to correct.
17. Action plan.
18. Release Gate.

## Protocol Zero
Every suspected discrepancy SHALL follow:

```text
QUESTION
-> PROJECT SOURCE CHECK
-> STANDARD / OFFICIAL SOURCE CHECK
-> ANSWER OR NOT_VERIFIABLE
-> RED TEAM
-> CLASSIFICATION
-> FINDING
-> ACTION
```

Before an unanswered question is escalated to the user, the review SHALL record that the available project documents were checked and that at least one applicable external authority was checked when relevant: corporate/national/international standard, official authority, official manufacturer, or specialist reference.

A missing answer is never a confirmed error.

## Finding card contract
Every confirmed finding/error SHALL display:

- finding ID;
- severity;
- status and classification;
- disciplines;
- affected TAG/location;
- evidence and exact evidence location;
- objective comparison;
- problem statement;
- root cause or explicit NOT_VERIFIABLE root cause;
- lifecycle impacts;
- primary correction;
- simpler/safer/lower-cost alternative where relevant;
- owner and dependencies;
- closure criterion;
- confidence and evidence quality;
- **documents involved**, split into the machine-readable groups:
  - `source_evidence` — source/evidence documents;
  - `project_correlated_or_conflicting` — correlated or conflicting project documents;
  - `normative_or_reference` — normative/reference documents;
  - `documents_to_correct` — documents to correct.

A normative/reference document SHALL carry an applicability state:
- `APPLICABLE`
- `REFERENCE_ONLY`
- `NOT_APPLICABLE`
- `PENDING`

A reference-only document cannot, by itself, create a confirmed nonconformity.

## Evidence classes
The report SHALL distinguish:
- project source fact;
- project decision;
- applicable normative requirement;
- reference-only normative guidance;
- official authority source;
- official manufacturer source;
- specialist reference;
- engineering inference.

## Automation trace
For every applicable object:

```text
PROCESS REQUIREMENT
-> EQUIPMENT / TAG
-> LOCATION
-> POWER / PROTECTION
-> COMMAND / FEEDBACK
-> I/O
-> PLC / RTU / CONTROLLER
-> CONTROL LOGIC
-> NETWORK
-> PROTOCOL / ADDRESS / REGISTER
-> SCALE / UNIT / QUALITY
-> HMI / SCADA
-> ALARM / TREND / HISTORY
-> FAT / SAT
```

## Failure modes
Review, when applicable:
- loss of AC supply;
- loss of 24 Vdc;
- loss of PLC/RTU/controller;
- loss of Ethernet/fieldbus;
- gateway failure;
- instrument failure;
- stale/invalid data;
- equipment unavailable;
- MANUAL/OFF/AUTO;
- LOCAL/REMOTE;
- restart and power restoration;
- safe-state and recovery behavior.

## Reference library
The default Automation reference library is repository-pinned at:
`datacenter/AUTOMATION_REFERENCE_LIBRARY.json`.

The library is lookup-mandatory but applicability-controlled. Contractual/project requirements and current approved editions take precedence.

## Release integrity
Release remains BLOCK when:
- an open critical finding exists;
- a material Protocol Zero question remains unanswered;
- baseline is incomplete or unreconciled;
- source provenance is incomplete;
- a finding lacks required document involvement;
- a normative claim has no applicability basis;
- required Automation traceability cannot be demonstrated;
- architecture-impact finding lacks alternatives/viability;
- coverage/compatibility gates fail;
- final revised documents have not been rechecked after correction.

## Confidentiality
This public repository SHALL store process rules, metadata and synthetic fixtures only. Project-confidential documents, project-specific source text, drawings and secrets SHALL NOT be committed.
