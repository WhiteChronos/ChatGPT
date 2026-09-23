# VISUALIZE Golden Rule v1.0

## Status
MANDATORY / BLOCK_ON_FAILURE

## Purpose
Establish the default presentation and review model for engineering documentation, multidisciplinary compatibility reviews, feasibility studies, audits, design reviews and technical reports.

## Golden Rule
`/visualize` means **complete technical content presented visually**. It MUST NOT be used as a synonym for summarization.

A compliant output preserves all relevant evidence, assumptions, divergences, impacts, solutions, dependencies and closure criteria while organizing them into a visual hierarchy that is easy to inspect.

Machine-enforced contract: `complete_not_summary = true`.

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

These color mappings are machine-enforced and SHALL NOT be reassigned.

## Compatibility calculation
Compatibility and coverage are separate metrics.

Compatibility MUST exclude NOT_APPLICABLE and NOT_VERIFIABLE from the denominator unless a project-specific rule states otherwise.

Coverage SHALL measure how much of the applicable identified scope was effectively verifiable. `NOT_VERIFIABLE` remains in the coverage denominator and therefore reduces coverage. `NOT_APPLICABLE` is excluded from the coverage denominator.

No global percentage may be published without:
- calculation method;
- explicit formula;
- denominator definition;
- status weights;
- coverage value;
- compatibility by discipline;
- compatibility by baseline document;
- interface compatibility;
- list of blocking missing documents.

## Source provenance
Every baseline document SHALL contain:
- document ID;
- discipline;
- revision;
- source location;
- SHA-256 hash;
- baseline status.

Every evidence record SHALL identify a baseline document and SHALL carry the same SHA-256 hash as that source document. Empty document IDs, revisions, locations, statements or provenance hashes are prohibited.

## Baseline reconciliation
A package may be released only when the current baseline is explicitly marked as reconciled with the latest approved revisions.

The mandatory-document inventory SHALL be explicit. `blocking_missing_documents` must be derived from that inventory rather than trusted as an independent self-declaration.

## Waiver integrity
A CRITICAL finding is blocked whenever its status is `OPEN` or `IN_REVIEW`, regardless of classification.

A finding may use status `WAIVED` only when the datasheet records:
- waiver reason;
- named human approver;
- approval date/time;
- approval evidence or reference.

An agent SHALL NOT self-waive a finding.

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

Architecture/system-design findings SHALL explicitly mark applicability and SHALL include at least one alternative plus a viability assessment.

## Lifecycle impacts
All lifecycle impact fields SHALL be non-empty. When there is no identified impact, use an explicit value such as `NONE`; blank fields are prohibited.

Required lifecycle fields are:
- design;
- procurement;
- fabrication;
- programming;
- commissioning;
- operation;
- maintenance;
- safety;
- cost;
- schedule.

## Release gate
A technical package SHALL be blocked when any of the following is true:
- open CRITICAL finding;
- unresolved discipline interface below the configured interface threshold;
- missing mandatory source document;
- compatibility below the configured global threshold;
- coverage below the configured coverage threshold;
- current baseline not reconciled with the latest approved revisions;
- baseline documents are absent;
- provenance hashes are absent or inconsistent;
- discipline or document compatibility scores are incomplete;
- calculation method or denominator is not reproducible;
- architecture-impact finding lacks viability analysis;
- waiver metadata is incomplete;
- any validation metric is NaN, Infinity or otherwise non-finite.

## Data-center rule
Raw source documents are immutable and versioned. Normalized facts, findings and compatibility records are derived artifacts and must retain provenance back to the raw source.

## Machine-enforced hardening v1.1
The implementation described in `governance/ENGINEERING_COMPATIBILITY_HARDENING_v1_1.md` is part of this Golden Rule. The canonical validator is `pipeline/engineering_compatibility_gate.py`.

Secondary validators, summary generators and report helpers SHALL delegate to the canonical gate and SHALL NOT duplicate independent thresholds or blocker logic.

A validation failure SHALL never persist or publish a `PASS` summary.

## Codex rule
Codex or any coding agent modifying this repository SHALL read this file before changing compatibility-analysis code, schemas, reports, pipelines or documentation. Generated outputs must satisfy this Golden Rule before merge.

## Automation report-model binding
Automation compatibility reports SHALL also comply with `governance/AUTOMATION_COMPATIBILITY_REPORT_MODEL_v1_0.md` and the machine-readable model at `datacenter/AUTOMATION_COMPATIBILITY_REPORT_MODEL.json`.

For Automation findings, the visualization SHALL expose the structured documents-involved groups and normative applicability state. Open questions SHALL expose recorded pre-escalation source checks and an answer field.
