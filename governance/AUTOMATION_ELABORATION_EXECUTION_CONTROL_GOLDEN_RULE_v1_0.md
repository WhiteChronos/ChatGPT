# Automation Elaboration & Execution Control Golden Rule v1.0

## Status
GOLDEN RULE / MANDATORY

## Purpose
Define how Automation compatibility findings, decisions, pending items and review comments are converted into controlled engineering elaboration and execution actions.

This rule governs the transition:

```text
EVIDENCE / COMMENT
-> PROTOCOL ZERO
-> DECISION OR FINDING
-> DOCUMENT ACTION
-> EXECUTION
-> RECHECK
-> CLOSURE
```

The objective is to prevent technically correct analysis from becoming fragmented, ambiguous or non-executable documentation.

## Core principle
Every material correction SHALL be expressed in the document that owns the change.

A control item is not execution-ready until it identifies:
- document and revision;
- priority;
- objective required action;
- evidence/basis;
- related finding, pending or question IDs;
- closure criterion;
- execution status.

Do not distribute the same correction across multiple report tabs when a consolidated document/action record is sufficient.

## Elaboration control
Before issuing a correction package:

1. identify the owning document for each action;
2. consolidate all actions affecting the same document/revision;
3. state exactly what must be changed to solve the issue;
4. preserve the evidence and IDs behind the action;
5. distinguish project decision from normative requirement and engineering proposal;
6. record items intentionally deferred to detailed/executive design as DESIGN_PENDING, not automatic errors;
7. define what evidence will close the action after implementation;
8. recheck every revised document before closure.

## Minimum action record
Each executable document-action record SHALL contain:

- `document`
- `revision`
- `priority`
- `required_action`
- `basis`
- `related_ids`
- `closure_criterion`
- `status`

Default statuses:
- `OPEN`
- `DESIGN_PENDING`
- `READY_FOR_EXECUTION`
- `IN_EXECUTION`
- `READY_FOR_RECHECK`
- `CLOSED`
- `NOT_APPLICABLE`

`CLOSED` is allowed only after the revised document/evidence is rechecked.

## Automation network / IP / cybersecurity elaboration
When an Automation review contains network, controller, gateway, HMI, BMS/supervisory or Ethernet/fieldbus scope, the elaboration SHALL check the following as applicable:

1. topology and node roles;
2. CLP/PLC, RTU/UTR, I/O, HMI, gateway, switch and BMS/supervisory interconnections;
3. switch quantity/location and uplinks;
4. port map;
5. IP addressing plan and subnetting;
6. VLAN/subnet segmentation where applicable;
7. boundary between control network and supervisory/BMS network;
8. zones and conduits concept where applicable;
9. firewall/DMZ requirement or explicit non-applicability/deferral;
10. protocol, address/register and data-quality mapping;
11. communication-loss behavior, diagnostics and recovery;
12. network-related FAT/SAT checks;
13. cybersecurity-reference applicability, including IEC 62443 where invoked or technically relevant.

### Applicability guard
IEC 62443, firewall, DMZ, VLAN, zones and conduits SHALL NOT be treated as universal automatic nonconformities.

For each such item, record one of:
- `APPLICABLE`
- `REFERENCE_ONLY`
- `NOT_APPLICABLE`
- `PENDING`

and document the applicability basis.

If the project stage intentionally defers IP/VLAN/segmentation details to detailed/executive design, the basic design SHALL at minimum make that deferral explicit, identify the expected deliverable and preserve the architecture interfaces that the executive design must close.

## Execution control
Execution SHALL follow this sequence:

```text
OPEN / DESIGN_PENDING
-> READY_FOR_EXECUTION
-> IN_EXECUTION
-> READY_FOR_RECHECK
-> CLOSED
```

Controls:
- no execution action without an owning document;
- no silent deletion of a finding after editing;
- no closure based only on a statement that the document was revised;
- closure requires recheck against the original evidence, project decisions and applicable requirements;
- a revised document that introduces a new conflict reopens the action or creates a new governed item;
- Release Gate remains BLOCK while a blocking action is not rechecked/closed.

## Reviewer-facing XLSX
For compact XLSX exports, use `AUTOMATION_COMPACT_XLSX_V1`:
- Summary contains decisions and Release Gate;
- Documents & Actions contains the consolidated execution instructions and priority;
- Pendings contains DESIGN_PENDING and unresolved engineering work;
- Answered Questions preserves Protocol Zero history.

No separate responsible/owner sheet is required by default.

## Repository control
This rule is machine-bound through:
- `datacenter/AUTOMATION_ELABORATION_EXECUTION_CONTROL.json`
- `datacenter/ENGINEERING_COMPATIBILITY_CONFIG.json`
- `AGENTS.md`
- compatibility regression tests and CI.

Configuration overrides SHALL NOT disable this rule.

## Confidentiality
Public repository assets SHALL contain only reusable governance/process logic and synthetic examples. Do not commit project-confidential drawings, comments or project-specific engineering decisions.
