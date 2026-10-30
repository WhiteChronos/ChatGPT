# MCE Production Evidence Gates — Design (28 Oct 2026)

**Goal:** Move the standalone MCE engineering CLI toward production without weakening the Excel-master protection, document provenance, <=50 causes per sheet, human authorization, or technical review.

**Constraints:** No reliance on REA or MCP, no public Excel/P&ID project inputs in GitHub, no auto-approval. Existing `mce_workflow.py` remains authoritative for workbook-state and OOXML checks; fail closed without live evidence.

## Alternatives

- Auto-merge and claim 100% on green CI: **rejected**, source approval and actual operator environment unverified.
- Replace the CLI with a hosted Web editor: **rejected**, changes the product model and enlarges the attack surface.
- Standalone read-only technical gate + operator-engineering approval chain: **selected**, preserves the existing design and makes missing proof visible.

## Acceptance boundaries

1. The technical gate reads the existing MCE workspace and checks SHA-256, source inventory, documented project/SS, protected workbook contract, approval binding, preliminary output and recomputed OOXML audit.
2. No state, source, template or output file is modified by the gate.
3. Missing or malicious evidence fails closed with machine-readable `BLOCKED` and exit code 2.
4. `TECHNICAL_READY_FOR_ENGINEERING_ACCEPTANCE` is not `PRODUCTION_COMPLETE`; official model approval, multidisciplinary reviews, applicable FAT/SAT, release and rollout approvals remain independent.

**Non-goals:** Fabricating project/SS, installing a hosted service, claiming official homologation, merging the PR without gates.
