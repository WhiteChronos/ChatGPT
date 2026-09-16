# Engineering Compatibility Hardening v1.1

## Purpose

This hardening release converts review findings into machine-enforced controls. The canonical release validator is `pipeline/engineering_compatibility_gate.py`; secondary compatibility CLIs must delegate to it and must not duplicate release logic.

## Control matrix

| ID | Review finding | Mandatory control in v1.1 |
|---|---|---|
| H-01 | Semantic gate could be skipped when no project datasheets existed | Permanent known-good fixture is executed directly; empty-directory protection remains only for project discovery. |
| H-02 | Unreconciled baseline could still PASS | `baseline.reconciled=true` is required for release. |
| H-03 | Workflow did not trigger on every compatibility validator | Workflow paths cover `pipeline/engineering_compatibility*.py`. |
| H-04 | SHA-256 provenance was optional | Baseline `sha256` and evidence `source_hash` are mandatory and cross-checked. |
| H-05 | CRITICAL findings could self-waive | WAIVED findings reference a trusted external approval record with `human_approved=true`; self-declared approver text is not authorization. |
| H-06 | Severity colors could be remapped | Schema fixes red/orange/yellow/blue/green/gray semantics. |
| H-07 | Lifecycle impacts could be blank | Every impact field is mandatory and nonblank; use `NONE` for no impact. |
| H-08 | Secondary validator used independent thresholds | Secondary validator delegates to canonical gate. |
| H-09 | Finding comparison was optional | `comparison` is mandatory and nonblank. |
| H-10 | Compatibility denominator was not reproducible | Method, denominator exclusions and status weights are explicit. |
| H-11 | CRITICAL blocker logic ignored status | CRITICAL with `OPEN` or `IN_REVIEW` blocks release. |
| H-12 | Discipline compatibility could omit in-scope disciplines | `by_discipline` keys must exactly match baseline disciplines. |
| H-13 | NOT_VERIFIABLE did not reduce coverage | Coverage is derived from structured assessment records; NOT_VERIFIABLE remains in the coverage denominator. |
| H-14 | Failed validation could write PASS | Summary gate is derived from the complete error set. |
| H-15 | Interface compatibility could fail independently | Interface score is separately recomputed and thresholded. |
| H-16 | PASS was possible without baseline | Non-empty source baseline is mandatory. |
| H-17 | Evidence identity fields could be empty | Evidence document/revision/location/statement/hash are mandatory and nonblank. |
| H-18 | No-argument gate always failed | No-argument gate validates the permanent positive fixture. |
| H-19 | NaN/Infinity could bypass thresholds | Strict JSON loading and finite-metric checks reject non-standard values. |
| H-20 | Architecture findings could omit viability | Architecture-impact findings require alternatives and viability analysis. |
| H-21 | Baseline documents lacked individual assessment | `by_document` must exactly cover baseline documents. |
| H-22 | Declared scores were not tied to calculation inputs | `assessment_records` are authoritative; global, interface, discipline and document scores are recomputed from their classifications and status weights. |
| H-23 | Hexadecimal hashes were compared case-sensitively | SHA-256 comparison is case-insensitive after schema validation. |
| H-24 | Mandatory document could be DRAFT/SUPERSEDED and still count as present | Required documents must have an eligible status from `baseline_policy.eligible_required_document_statuses`. |
| H-25 | Scope counts could be inflated with unsupported VERIFIED entries | `scope_summary` must exactly equal counts derived from `assessment_records`. |
| H-26 | Findings could reference disciplines outside the baseline | Finding and assessment disciplines are validated against `baseline.disciplines`. |
| H-27 | Mandatory evidence quality could not be represented | Every finding requires structured `evidence_quality.rating` and `evidence_quality.rationale`. |
| H-28 | Whitespace-only finding text passed validation | Critical textual fields use nonblank string schema and semantic checks. |
| H-29 | NOT_VERIFIABLE blue mapping was required by governance but rejected by schema | `NOT_VERIFIABLE: blue` is required by schema and configuration. |
| H-30 | Findings and structured classification inventory could diverge | Every finding references `assessment_id`; its classification and discipline set must match the referenced assessment record. |
| H-31 | Non-verified assessment records could omit complete finding detail | Every `PARTIAL`, `DIVERGENT` or `NOT_VERIFIABLE` assessment must be represented by a corresponding finding. |
| H-32 | Authoritative assessment records could classify criteria without source evidence | Every assessment requires provenance-bearing `evidence` plus structured `evidence_quality`; evidence revisions and hashes are validated against baseline documents. |
| H-33 | Single-discipline records could be self-declared as interface assessments | `interface=true` requires at least two distinct baseline disciplines and provenance evidence covering at least two interface disciplines. |
| H-34 | Duplicate assessment content could be cloned under new IDs to dilute failures | Assessment content is fingerprinted independently of `id`; semantically duplicate records block release. |
| H-35 | Threshold checks could trust a declared metric that was within tolerance but above the recomputed value | Tolerance is used only to validate declared-vs-computed consistency; release thresholds are applied to the recomputed coverage/global/interface values. |
| H-36 | A scored assessment could declare disciplines/documents without evidence for every declared scope item | Assessment evidence must cover every declared `discipline` and every declared `document_id` before the record contributes to scores. |
| H-37 | Project configuration could disable mandatory blockers | Mandatory blocker flags must remain enabled and the canonical gate enforces baseline, provenance, missing-document, waiver, architecture and open-CRITICAL controls independently of project switches. |
| H-38 | Duplicate criterion/scope records could evade duplicate detection by changing only classification | Assessment identity excludes producer-selected `classification`; the same criterion/scope cannot be counted twice with different outcomes. |
| H-39 | Negative configurable release thresholds could disable all percentage gates | Coverage, global compatibility and interface compatibility thresholds must be finite percentages in the inclusive range 0-100. |
| H-40 | Discipline aliases differing only by whitespace/case could fabricate multidisciplinary interfaces | Discipline identifiers are normalized for uniqueness/interface counting and leading/trailing whitespace is rejected. |
| H-41 | JSON exponent overflow such as `1e999` could enter evidence as infinity | Loaded JSON is recursively checked for non-finite floating-point values, including exponent-overflow infinities. |
| H-42 | Duplicate criteria could evade identity checks by changing only evidence-quality metadata | `evidence_quality` is excluded from assessment identity, so rating/rationale changes cannot create another scored criterion. |
| H-43 | Configurable metric tolerance could be enlarged to publish arbitrary declared scores | Declared-vs-computed consistency uses the canonical `0.05%` tolerance; project configuration cannot widen it. |
| H-44 | An incomplete trusted approval object could authorize a CRITICAL waiver | Trusted waiver records require `human_approved=true`, a named approver, timezone-qualified ISO-8601 approval timestamp and nonblank approval evidence/reference. |
| H-45 | Finding narratives did not state whether claims were sourced, inferred or external knowledge | Every comparison, problem, root-cause and solution narrative carries structured `claim_basis`; architecture viability carries the same metadata when present. |
| H-46 | Evidence payload variations could create duplicate scored criteria | Assessment identity is derived only from normalized criterion and declared scope (`disciplines`, `document_ids`, `interface`); evidence/evidence-quality/outcome/ID changes cannot create another scored criterion. |
| H-47 | A legitimate trusted approval could be reused for another finding or package revision | Every trusted waiver approval is bound to project, finding ID, assessment ID and a SHA-256 subject hash over the current finding plus baseline package snapshot. |
| H-48 | Architecture alternatives could use placeholder viability text without evaluating mandatory trade-off dimensions | Every architecture alternative carries structured simplicity, safety, cost and maintainability assessments (`IMPROVES`, `EQUIVALENT`, `DEGRADES`) plus nonblank rationale. |

## Release invariants

A `PASS` package must satisfy all of the following:

1. Baseline documents exist, have unique IDs, provenance and valid disciplines.
2. Baseline discipline identifiers are nonblank, trimmed and unique after whitespace/case normalization.
3. The baseline is reconciled.
4. Every required document has an eligible current/approved status; `blocking_missing_documents` equals the computed missing/non-current set and is empty.
5. `assessment_records` are the authoritative complete criterion inventory and cannot contain duplicate criterion/scope identity under different IDs, classifications, evidence payloads or evidence-quality metadata.
6. Every assessment record carries provenance-bearing source evidence and structured evidence quality; evidence is tied to declared assessment documents and baseline revisions/hashes.
7. Assessment evidence covers every declared discipline and every declared document before the record contributes to compatibility scores.
8. Every `PARTIAL`, `DIVERGENT` or `NOT_VERIFIABLE` assessment has a corresponding complete finding.
9. Every multidisciplinary assessment is treated as an interface; normalized discipline identity must prove at least two distinct disciplines.
10. `scope_summary` exactly matches classifications derived from `assessment_records`.
11. Coverage is recomputed from that inventory and the recomputed value meets a finite release threshold in the range 0-100.
12. Compatibility global, interface, discipline and document scores are recomputed from the same inventory and disclosed status weights; the canonical declared-vs-computed tolerance is fixed at 0.05 percentage point, and global/interface thresholds are applied to recomputed values.
13. Every baseline discipline and document has a computed score.
14. `NOT_VERIFIABLE` reduces coverage and is excluded from the compatibility denominator.
15. Findings reference valid assessment records and cannot invent disciplines or classifications.
16. Finding evidence preserves document identity, revision and SHA-256 provenance; hexadecimal case is semantically irrelevant.
17. Every finding exposes evidence quality, confidence, comparison, problem, root cause, lifecycle impacts, solution and objective closure criterion.
18. Finding narratives identify their claim basis as `SOURCE_DERIVED`, `INFERENCE` or `EXTERNAL_KNOWLEDGE`; architecture viability is classified when required.
19. Open CRITICAL findings block release.
20. WAIVED findings require a complete trusted external human approval record with approver identity, approval time and evidence/reference, bound to the current project/finding/assessment and exact finding+baseline subject hash.
21. Architecture-impact findings include alternatives and viability; every alternative explicitly assesses simplicity, safety, cost and maintainability with a structured rating and rationale.
22. Mandatory governance blockers are non-configurable release invariants; project configuration cannot disable them.
23. Visualization color semantics are fixed, including `NOT_VERIFIABLE = blue`.
24. JSON input contains no non-finite numeric values, including exponent-overflow infinities; metrics are finite and schema + semantic validation return zero errors.

## Coverage formula

Let `V`, `P`, `D`, `NV`, `NA` be counts derived from `assessment_records`.

`coverage = 100 * (V + P + D) / (V + P + D + NV)`

`NA` is excluded from the coverage denominator. `NV` remains in the denominator and therefore reduces coverage. The release threshold is evaluated against this recomputed value; a declared value is informational only after it has been checked against the recomputation within the canonical 0.05 percentage-point tolerance.

## Compatibility formula

For applicable assessment records only (`VERIFIED`, `PARTIAL`, `DIVERGENT`):

`compatibility = 100 * sum(status_weight) / applicable_record_count`

Default mandatory weights:

- VERIFIED = 1.0
- PARTIAL = 0.5
- DIVERGENT = 0.0

The same calculation is performed globally and for each discipline, document and interface subset. Declared values must match recomputed values within the fixed canonical tolerance of 0.05 percentage point, while release thresholds are applied to the recomputed global and interface values.

## Trusted waiver authorization

`waiver.approval_record_id` must resolve to `waiver_authorization.trusted_approval_records` in the trusted configuration. The selected record must contain `human_approved=true`, a nonblank `approver`, a timezone-qualified ISO-8601 `approved_at` timestamp and a nonblank `evidence` reference. It must also contain `project`, `finding_id`, `assessment_id` and `subject_hash`. The subject hash is the SHA-256 digest of the canonical current project/finding (excluding the waiver pointer itself) plus the baseline document snapshot, required-document inventory and reconciliation state. A trusted approval therefore cannot be replayed against another finding or a changed package. Datasheet-authored approver names, timestamps or evidence strings do not create authorization by themselves.

## Architecture trade-off contract

When `architecture_impact=true`, each alternative must include structured `tradeoffs` for `simplicity`, `safety`, `cost` and `maintainability`. Each dimension uses one of `IMPROVES`, `EQUIVALENT` or `DEGRADES` and includes a nonblank rationale. The free-text viability narrative supplements this structure; it cannot replace it.

## Claim-basis metadata

Every finding must classify the basis of `comparison`, `problem`, `root_cause` and `solution` as `SOURCE_DERIVED`, `INFERENCE` or `EXTERNAL_KNOWLEDGE`. When `architecture_impact=true`, the required `viability` narrative must also carry claim-basis metadata. This classification is descriptive provenance metadata and does not replace the mandatory evidence records.

## CI expectations

The compatibility workflow shall compile both compatibility modules, validate JSON syntax and schema, exercise the permanent positive fixture, exercise the report wrapper, run regression tests, validate every project datasheet found, preserve the empty-project discovery guard, and verify the Codex/Golden Rule contract.