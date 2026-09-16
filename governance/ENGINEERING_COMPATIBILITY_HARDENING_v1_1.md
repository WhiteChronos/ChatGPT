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
| H-38 | Duplicate criterion/scope records could evade duplicate detection by changing only classification | Assessment identity excludes producer-selected `classification`; the same criterion/scope/evidence cannot be counted twice with different outcomes. |
| H-39 | Negative configurable release thresholds could disable all percentage gates | Coverage, global compatibility and interface compatibility thresholds must be finite percentages in the inclusive range 0-100. |
| H-40 | Discipline aliases differing only by whitespace/case could fabricate multidisciplinary interfaces | Discipline identifiers are normalized for uniqueness/interface counting and leading/trailing whitespace is rejected. |
| H-41 | JSON exponent overflow such as `1e999` could enter evidence as infinity | Loaded JSON is recursively checked for non-finite floating-point values, including exponent-overflow infinities. |

## Release invariants

A `PASS` package must satisfy all of the following:

1. Baseline documents exist, have unique IDs, provenance and valid disciplines.
2. Baseline discipline identifiers are nonblank, trimmed and unique after whitespace/case normalization.
3. The baseline is reconciled.
4. Every required document has an eligible current/approved status; `blocking_missing_documents` equals the computed missing/non-current set and is empty.
5. `assessment_records` are the authoritative complete criterion inventory and cannot contain duplicate semantic content under different IDs or classifications.
6. Every assessment record carries provenance-bearing source evidence and structured evidence quality; evidence is tied to declared assessment documents and baseline revisions/hashes.
7. Assessment evidence covers every declared discipline and every declared document before the record contributes to compatibility scores.
8. Every `PARTIAL`, `DIVERGENT` or `NOT_VERIFIABLE` assessment has a corresponding complete finding.
9. Every multidisciplinary assessment is treated as an interface; normalized discipline identity must prove at least two distinct disciplines.
10. `scope_summary` exactly matches classifications derived from `assessment_records`.
11. Coverage is recomputed from that inventory and the recomputed value meets a finite release threshold in the range 0-100.
12. Compatibility global, interface, discipline and document scores are recomputed from the same inventory and disclosed status weights; global and interface thresholds are finite percentages in the range 0-100 and are applied to recomputed values.
13. Every baseline discipline and document has a computed score.
14. `NOT_VERIFIABLE` reduces coverage and is excluded from the compatibility denominator.
15. Findings reference valid assessment records and cannot invent disciplines or classifications.
16. Finding evidence preserves document identity, revision and SHA-256 provenance; hexadecimal case is semantically irrelevant.
17. Every finding exposes evidence quality, confidence, comparison, root cause, lifecycle impacts, solution and objective closure criterion.
18. Open CRITICAL findings block release.
19. WAIVED findings require a trusted external human approval record.
20. Architecture-impact findings include alternatives and viability.
21. Mandatory governance blockers are non-configurable release invariants; project configuration cannot disable them.
22. Visualization color semantics are fixed, including `NOT_VERIFIABLE = blue`.
23. JSON input contains no non-finite numeric values, including exponent-overflow infinities; metrics are finite and schema + semantic validation return zero errors.

## Coverage formula

Let `V`, `P`, `D`, `NV`, `NA` be counts derived from `assessment_records`.

`coverage = 100 * (V + P + D) / (V + P + D + NV)`

`NA` is excluded from the coverage denominator. `NV` remains in the denominator and therefore reduces coverage. The release threshold is evaluated against this recomputed value; a declared value is informational only after it has been checked against the recomputation within tolerance.

## Compatibility formula

For applicable assessment records only (`VERIFIED`, `PARTIAL`, `DIVERGENT`):

`compatibility = 100 * sum(status_weight) / applicable_record_count`

Default mandatory weights:

- VERIFIED = 1.0
- PARTIAL = 0.5
- DIVERGENT = 0.0

The same calculation is performed globally and for each discipline, document and interface subset. Declared values must match recomputed values within the configured tolerance, while release thresholds are applied to the recomputed global and interface values.

## Trusted waiver authorization

`waiver.approval_record_id` must resolve to `waiver_authorization.trusted_approval_records` in the trusted configuration and that record must contain `human_approved=true`. Datasheet-authored approver names, timestamps or evidence strings do not create authorization by themselves.

## CI expectations

The compatibility workflow shall compile both compatibility modules, validate JSON syntax and schema, exercise the permanent positive fixture, exercise the report wrapper, run regression tests, validate every project datasheet found, preserve the empty-project discovery guard, and verify the Codex/Golden Rule contract.