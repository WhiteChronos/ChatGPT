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

## Question presentation contract
Any user-facing batch of Automation compatibility questions SHALL use the same standard visual model as the report.

Mandatory behavior:
- render through `/visualize` using the best interactive surface available;
- do not present the primary question batch as a plain Markdown/list-only response when an interactive visualization surface is available;
- keep questions in a dedicated module visually separated from confirmed findings and engineering problems;
- every question card SHALL show: question ID, severity/priority, discipline/area, objective question, why the question is needed, project documents involved, completed source checks, current status, and a writable answer field;
- when an answer can be selected from a bounded engineering choice, show the options explicitly without steering the user;
- provide a generated response block so the user can return all answers to the analysis;
- preserve answered questions in a separate resolved-questions module rather than deleting their audit trail;
- unanswered questions remain `NOT_VERIFIABLE` / pending and SHALL NOT be visually styled as confirmed errors;
- after user answers, re-run Protocol Zero and source verification before promoting any question to a finding;
- when @Build Web Data Visualization later becomes executable, upgrade the same question/report view without changing technical content.

This contract applies both when the user asks for the full report and when the user asks only to “generate the questions”.

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

Before an unanswered question is escalated to the user, the review SHALL first perform owning-document routing (identify the project document class most likely to contain the answer), then record that the routed project documents were checked and that at least one applicable external authority was checked when relevant: corporate/national/international standard, official authority, official manufacturer, or specialist reference.

A missing answer is never a confirmed error. A question resolved by its owning project document SHALL be removed from the user-question queue and retained as source-derived evidence.

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

## Evidence-before-assumption gate
The report SHALL apply `governance/AUTOMATION_EVIDENCE_RESEARCH_GOLDEN_RULE_v1_0.md`.

A suspected relationship between project objects remains a question/NOT_VERIFIABLE until evidence establishes the link. Quantity matching alone is never evidence of one-to-one mapping.

For component/interface questions, the reviewer SHALL check the project baseline first and then seek supporting material from official standards/manufacturers and, when useful, open educational books, GitHub/open-source repositories and research plugins. The discovery mechanism is not itself the evidence.

The technical knowledge base is `datacenter/AUTOMATION_TECHNICAL_KNOWLEDGE_BASE.json`.

## Evidence classes
The report SHALL distinguish:
- project source fact;
- project decision;
- applicable normative requirement;
- reference-only normative guidance;
- official authority source;
- official manufacturer source;
- open educational book;
- specialist reference;
- open-source reference implementation;
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

## Compact Excel export profile
For XLSX circulation/review, the default export profile is `AUTOMATION_COMPACT_XLSX_V1`, governed by `governance/AUTOMATION_COMPACT_EXCEL_EXPORT_MODEL_v1_0.md` and `datacenter/AUTOMATION_REPORT_EXPORT_PROFILES.json`.

The XLSX presentation SHALL be compact by default: decisions + Release Gate in Summary; confirmed findings consolidated by document/action; Pendings in one organized sheet; answered Protocol Zero questions in a separate audit-history sheet. Standalone evidence, standalone decisions, standalone findings, standalone Release Gate, external-evaluation forms and responsible/owner sheets are excluded unless explicitly requested.

This compact projection must preserve traceability and must not weaken the comprehensive /visualize report model.

## Elaboration and execution control
The report SHALL apply `AUTOMATION_ELABORATION_EXECUTION_CONTROL_V1_0` from `governance/AUTOMATION_ELABORATION_EXECUTION_CONTROL_GOLDEN_RULE_v1_0.md`.

Every confirmed finding or material pending item SHALL be converted into an owning-document action with priority, objective required action, basis, related IDs, closure criterion and execution status. A revised document is not closed until it is rechecked.

When network/IP/cybersecurity scope exists, the review SHALL check topology, interconnections, switch/uplinks, port map, IP/subnets, VLAN/segmentation, control-to-supervisory boundary, zones/conduits, firewall/DMZ decision, protocol/register/data-quality mapping, communication-loss behavior, FAT/SAT and cybersecurity-reference applicability. IEC 62443-related controls remain applicability-driven and cannot create automatic nonconformity without project/applicability basis.

## Document fidelity and interpretation gate
Before promoting any document-format, pagination, sheet-location or layout discrepancy, apply `DOCUMENT_FIDELITY_INTERPRETATION_V1_0`.

The reviewer SHALL separate native source structure, semantic extraction and visual rendering. For Word documents, external render page counts are non-authoritative when they conflict with native metadata/foliation. Record such cases as `RENDER_MISMATCH`; do not create a source-document finding until confirmed natively. Audit font substitutions before using external rendering for layout conclusions.
