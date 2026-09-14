# Engineering Compatibility Hardening v1.1

## Purpose

This hardening release closes the review findings raised against the initial engineering compatibility implementation and converts them into machine-enforced validation rules.

The canonical release validator is:

`pipeline/engineering_compatibility_gate.py`

The secondary helper `pipeline/engineering_compatibility.py` MUST delegate to the canonical validator and MUST NOT carry independent release thresholds or blocker logic.

## Control matrix

| ID | Review finding | Mandatory control in v1.1 |
|---|---|---|
| H-01 | Semantic gate could be skipped when no project datasheets existed | Permanent known-good fixture is executed directly with the no-argument canonical gate; empty-directory protection remains for project discovery. |
| H-02 | Unreconciled baseline could still PASS | `baseline.reconciled` is mandatory and `block_on_unreconciled_baseline` is enforced semantically. |
| H-03 | Workflow did not trigger on every compatibility validator | Workflow paths cover `pipeline/engineering_compatibility*.py`. |
| H-04 | SHA-256 provenance was optional | Baseline document `sha256` and evidence `source_hash` are mandatory, formatted and cross-checked. |
| H-05 | CRITICAL findings could self-waive | `WAIVED` requires reason, approver, date/time and approval evidence. Open CRITICAL is based on status, not classification. |
| H-06 | Severity colors could be remapped | Schema uses fixed constants: red/orange/yellow/blue/green/gray. |
| H-07 | Lifecycle impacts could be blank | Every impact field is mandatory and non-empty; `NONE` is the explicit no-impact value. |
| H-08 | Secondary validator used a hard-coded compatibility threshold | Secondary validator delegates to the canonical gate and therefore uses configured thresholds only. |
| H-09 | Finding comparison was optional | `comparison` is mandatory and non-empty. |
| H-10 | Compatibility denominator was not reproducible | `compatibility.method` is a structured object with formula, denominator definition, exclusions and status weights. |
| H-11 | CRITICAL blocker logic ignored finding status | Canonical gate blocks severity CRITICAL with status `OPEN` or `IN_REVIEW` regardless of classification. |
| H-12 | Discipline-level compatibility could omit in-scope disciplines | `compatibility.by_discipline` keys must exactly match `baseline.disciplines`. |
| H-13 | NOT_VERIFIABLE did not reduce coverage | Coverage is recomputed from `scope_summary`; NOT_VERIFIABLE remains in the applicable denominator. |
| H-14 | Failed validation could write a PASS summary | Summary release gate is derived from the complete validation error set. |
| H-15 | Interface compatibility could fail while overall gate passed | Dedicated configured interface threshold is enforced. |
| H-16 | PASS was possible with no source baseline | `baseline.documents` has at least one document and PASS requires baseline integrity. |
| H-17 | Evidence identities could be empty | Evidence document ID, revision, location, statement and source hash are non-empty schema requirements. |
| H-18 | Mandated no-argument gate command always failed | No-argument canonical gate now validates the permanent positive fixture. |
| H-19 | NaN/Infinity could bypass numeric thresholds | Strict JSON loading rejects non-standard numeric constants; semantic validation also requires finite metrics. |
| H-20 | Architecture findings could omit viability | `architecture_impact=true` conditionally requires alternatives and viability analysis. |
| H-21 | Baseline documents did not have individual compatibility assessments | `compatibility.by_document` is mandatory and must exactly cover all baseline document IDs. |

## Release invariants

A `PASS` package must satisfy every invariant below:

1. At least one baseline source document exists.
2. Baseline document IDs are unique.
3. Every baseline source has revision, discipline, source and SHA-256 provenance.
4. The baseline is explicitly reconciled.
5. Mandatory document inventory and `blocking_missing_documents` are consistent.
6. Coverage is reproducible from `scope_summary`.
7. NOT_VERIFIABLE reduces coverage.
8. Global compatibility meets the configured threshold.
9. Interface compatibility meets the configured threshold.
10. Every in-scope discipline has a compatibility score.
11. Every baseline document has a compatibility score.
12. Calculation method, denominator and status weights are explicit.
13. Severity colors retain mandatory semantics.
14. Open CRITICAL findings block release.
15. WAIVED findings contain recorded human approval metadata.
16. Evidence hashes match baseline source hashes.
17. Evidence revisions match baseline document revisions.
18. Lifecycle impact fields are explicit and non-empty.
19. Architecture-impact findings include alternatives and viability analysis.
20. Metrics are finite.
21. Schema and semantic validation have zero errors.

## Coverage formula

Let:

- `V` = VERIFIED count
- `P` = PARTIAL count
- `D` = DIVERGENT count
- `NV` = NOT_VERIFIABLE count
- `NA` = NOT_APPLICABLE count

Coverage is:

`100 * (V + P + D) / (V + P + D + NV)`

`NA` is excluded from the coverage denominator. `NV` is included and therefore reduces coverage.

## Compatibility denominator

The default compatibility policy excludes NOT_APPLICABLE and NOT_VERIFIABLE from the compatibility denominator and uses status weights:

- VERIFIED = 1.0
- PARTIAL = 0.5
- DIVERGENT = 0.0

Project reports must publish the formula and denominator definition used.

## CI expectations

The compatibility workflow SHALL:

- compile both compatibility Python modules;
- validate JSON syntax;
- validate the datasheet template against the schema;
- execute the permanent positive fixture through the canonical semantic gate;
- execute the report-wrapper path;
- run permanent regression tests;
- validate every project datasheet when project files exist;
- preserve the non-failing empty-directory guard for project discovery;
- verify the Codex/Golden Rule machine contract.
