# Engineering Compatibility Repository Memory

## Purpose
Durable, repository-visible memory for the engineering compatibility process.

## Current operating model
- Hardening v1.1 is the integrated baseline on `main`; Hyperfocus v1.2 extends it and must not weaken its controls.
- Visual presentation rule: `governance/VISUALIZE_GOLDEN_RULE_v1_0.md`
- Automation/Data reasoning rule: `governance/AUTOMATION_HYPERFOCUS_GOLDEN_RULE_v1_0.md`
- Canonical release validator: `pipeline/engineering_compatibility_gate.py`
- Protocol Zero validator: `pipeline/protocol_zero_gate.py`
- Canonical configuration: `datacenter/ENGINEERING_COMPATIBILITY_CONFIG.json`
- Datasheet template: `datasheet/ENGINEERING_COMPATIBILITY_DATA_SHEET.json`

## Permanent engineering decisions
1. Question before finding.
2. Unanswered doubt = NOT_VERIFIABLE / pending, not presumed error.
3. Source fact, project decision, inference and external knowledge remain distinguishable.
4. Automation reviews use TAG -> I/O -> logic -> network -> data -> HMI/SCADA -> FAT/SAT traceability.
5. Coverage and compatibility are separate.
6. No percentage without a reproducible denominator and method.
7. Raw Data Center sources remain immutable.
8. Public repository memory must never contain confidential project documents or project-specific secrets.
9. Agents never self-waive findings and never merge automatically.
10. Architecture changes require alternatives, viability and failure-mode review.

## Maintenance
Update this file only when the process contract changes. Project-specific facts belong in governed project datasheets, not here.
