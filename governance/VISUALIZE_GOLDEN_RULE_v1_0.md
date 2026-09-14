# VISUALIZE Golden Rule v1.0

## Status
MANDATORY / BLOCK_ON_FAILURE

## Purpose
Establish the default presentation and review model for engineering documentation, multidisciplinary compatibility reviews, feasibility studies, audits, design reviews and technical reports.

## Golden Rule
`/visualize` means **complete technical content presented visually**. It MUST NOT be used as a synonym for summarization.

A compliant output preserves all relevant evidence, assumptions, divergences, impacts, solutions, dependencies and closure criteria while organizing them into a visual hierarchy that is easy to inspect.

## Mandatory analysis stack
Every engineering compatibility review SHALL apply, when relevant:

1. `/factcheck` — confirm each claim against documentary evidence.
2. `/thenvsnow` — compare prior and current revision/baseline.
3. `/comparison` — compare disciplines, documents, TAGs and values.
4. `/deepdive` — reconstruct functional intent and engineering logic.
5. `/rootcause` + `/fivewhys` — identify the real origin of the discrepancy.
6. `/audit` — verify coverage, traceability and missing evidence.
7. `/redteam` + `/premortem` — search for hidden failure modes and execution risks.
8. `/viability` — compare simpler, safer, cheaper or more maintainable alternatives.
9. `/actionplan` — define correction, owner, priority, dependency and closure evidence.
10. `/visualize` — present the full result in a clear visual structure.

## Mandatory visual structure
Every technical finding SHALL expose, without hiding information behind a short summary:

- ID and severity;
- discipline(s);
- document number, revision, sheet/page and TAG/location;
- exact evidence found;
- compared evidence from related documents;
- classification: VERIFIED / PARTIAL / DIVERGENT / NOT_VERIFIABLE / NOT_APPLICABLE;
- technical explanation of the discrepancy;
- root cause;
- impact on design, procurement, fabrication, programming, commissioning, operation, maintenance, safety, cost and schedule as applicable;
- recommended solution;
- alternative solutions and feasibility assessment when applicable;
- primary document to adjust;
- secondary documents affected;
- proposed insertion/correction text when applicable;
- dependency;
- owner/discipline;
- closure criterion;
- confidence and evidence quality.

## Mandatory visual conventions
Use consistent severity encoding:

- CRITICAL: red
- HIGH: orange
- MEDIUM: yellow
- LOW / NOT_VERIFIABLE: blue
- VERIFIED / COMPATIBLE: green
- NOT_APPLICABLE: neutral gray

The presentation SHOULD use cards, matrices, side-by-side comparisons, process flows, dependency trees, progress/gate panels and expandable detail sections. Color must support meaning, never decoration alone.

## Compatibility calculation
Compatibility and coverage are separate metrics.

Compatibility MUST exclude NOT_APPLICABLE and NOT_VERIFIABLE from the denominator unless a project-specific rule states otherwise.

Coverage SHALL measure how much of the identified scope was effectively verifiable.

No global percentage may be published without:
- calculation method;
- denominator definition;
- coverage value;
- list of blocking missing documents.

## Feasibility and value engineering
Every discrepancy with architectural or system-design impact SHALL evaluate at least:
- current solution;
- simpler alternative;
- distributed vs centralized architecture when relevant;
- maintainability;
- cabling/interfaces;
- lifecycle cost;
- commissioning complexity;
- expansion margin;
- failure modes;
- impact on other disciplines.

## Release gate
A technical package SHALL be blocked when any of the following is true:
- open CRITICAL divergence;
- unresolved discipline interface that can invalidate fabrication/programming;
- missing mandatory source document;
- compatibility below project threshold;
- evidence/coverage below project threshold;
- current baseline not reconciled with the latest approved revisions.

## Data-center rule
Raw source documents are immutable and versioned. Normalized facts, findings and compatibility records are derived artifacts and must retain provenance back to the raw source.

## Codex rule
Codex or any coding agent modifying this repository SHALL read this file before changing compatibility-analysis code, schemas, reports, pipelines or documentation. Generated outputs must satisfy this Golden Rule before merge.