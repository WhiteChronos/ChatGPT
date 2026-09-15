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

## Release invariants

A `PASS` package must satisfy all of the following:

1. Baseline documents exist, have unique IDs, provenance and valid disciplines.
2. The baseline is reconciled.
3. Every required document has an eligible current/approved status; `blocking_missing_documents` equals the computed missing/non-current set and is empty.
4. `assessment_records` are the authoritative complete criterion inventory.
5. Every assessment record carries provenance-bearing source evidence and structured evidence quality; evidence is tied to declared assessment documents and baseline revisions/hashes.
6. Every `PARTIAL`, `DIVERGENT` or `NOT_VERIFIABLE` assessment has a corresponding complete finding.
7. Every `interface=true` assessment identifies at least two baseline disciplines and has evidence spanning at least two interface disciplines.
8. `scope_summary` exactly matches classifications derived from `assessment_records`.
9. Coverage is recomputed from that inventory and meets threshold.
10. Compatibility global, interface, discipline and document scores are recomputed from the same inventory and disclosed status weights.
11. Every baseline discipline and document has a computed score.
12. `NOT_VERIFIABLE` reduces coverage and is excluded from the compatibility denominator.
13. Findings reference valid assessment records and cannot invent disciplines or classifications.
14. Finding evidence preserves document identity, revision and SHA-256 provenance; hexadecimal case is semantically irrelevant.
15. Every finding exposes evidence quality, confidence, comparison, root cause, lifecycle impacts, solution and objective closure criterion.
16. Open CRITICAL findings block release.
17. WAIVED findings require a trusted external human approval record.
18. Architecture-impact findings include alternatives and viability.
19. Visualization color semantics are fixed, including `NOT_VERIFIABLE = blue`.
20. Metrics are finite and schema + semantic validation return zero errors.

## Coverage formula

Let `V`, `P`, `D`, `NV`, `NA` be counts derived from `assessment_records`.

`coverage = 100 * (V + P + D) / (V + P + D + NV)`

`NA` is excluded from the coverage denominator. `NV` remains in the denominator and therefore reduces coverage.

## Compatibility formula

For applicable assessment records only (`VERIFIED`, `PARTIAL`, `DIVERGENT`):

`compatibility = 100 * sum(status_weight) / applicable_record_count`

Default mandatory weights:

- VERIFIED = 1.0
- PARTIAL = 0.5
- DIVERGENT = 0.0

The same calculation is performed globally and for each discipline, document and interface subset. Declared values must match recomputed values within the configured tolerance.

## Trusted waiver authorization

`waiver.approval_record_id` must resolve to `waiver_authorization.trusted_approval_records` in the trusted configuration and that record must contain `human_approved=true`. Datasheet-authored approver names, timestamps or evidence strings do not create authorization by themselves.

## CI expectations

The compatibility workflow shall compile both compatibility modules, validate JSON syntax and schema, exercise the permanent positive fixture, exercise the report wrapper, run regression tests, validate every project datasheet found, preserve the empty-project discovery guard, and verify the Codex/Golden Rule contract.
