# Automation Evidence Research Golden Rule v1.0

## Status
MANDATORY / QUESTION-BEFORE-ASSUMPTION

## Purpose
Prevent unsupported engineering associations in Automation reviews. A technical relationship SHALL NOT be inferred from quantity, naming similarity, adjacent rows, tag prefixes, or generic industry practice when the project documents do not establish that relationship.

## Core rule
Before asserting that two project objects are functionally or electrically associated, the reviewer SHALL obtain evidence for the relationship.

Examples of prohibited assumptions:
- DO count == external relay count;
- DI count == field contact count without checking wiring/function;
- a tag beginning with RI necessarily means an interposing relay driven by a specific DO;
- a device listed near another device in a material list is electrically connected to it;
- a reference model implies a specific wiring arrangement without manufacturer evidence;
- identical quantities prove one-to-one mapping.

## Digital-output / relay invariant
A digital output (DO/DQ) is an output point/channel of a PLC/RTU/controller I/O subsystem.

An external interposing/interface relay is a separate field/panel device that MAY be driven by a DO when the documented electrical interface requires isolation, voltage conversion, current amplification, contact multiplication or another explicit interface function.

Therefore:
- existence of a DO does not imply existence of an external relay;
- existence of an external relay does not prove which DO drives it;
- relay quantity SHALL NOT be derived from DO quantity;
- a PLC output module may itself use relay contacts, transistor outputs or other switching technology;
- a DO may drive a compatible load directly;
- mapping DO -> external relay requires project evidence such as wiring diagram, loop/interconnection diagram, terminal plan, panel schematic, I/O mapping, cable schedule or explicit design specification.

## Document-routing gate before user questions
Before escalating any technical doubt to the user, the reviewer SHALL first route the question to the project document class most likely to own the answer and search that source.

Minimum routing:
- network topology, Ethernet paths, switch/uplink ports, controller interconnection, gateway paths -> Automation/network architecture drawings and network diagrams;
- I/O point destination, card/channel mapping, terminal destination -> I/O list + interconnection/wiring/loop/terminal/panel drawings;
- command priority, LOCAL/REMOTE, MANUAL/AUTO, sequences, permissives and fallback -> control philosophy / memorial / technical specification / Cause & Effect;
- field-device quantity and process location -> discipline-master process/HVAC/P&ID/layout/equipment documents;
- power feed, protection, grounding, UPS and source -> electrical one-line/panel/feeding documents;
- procurement quantity/model -> material list + datasheet + requisition/specification.

If the user explicitly points to the owning document (for example, “this is in the network architecture”), the reviewer SHALL reopen/recheck that document before keeping the item as a user question.

A question that can be answered from its owning project document is NOT a user question. It is a source-resolution task.

## Research-before-assumption sequence
For an unfamiliar, ambiguous or disputed engineering relationship, search in this order:

1. route the doubt to the likely owning project document class and search that source;
2. current project baseline and revisions;
3. contract, design basis and discipline-master document;
4. applicable corporate/national/international standard;
5. official authority;
6. official manufacturer manual/datasheet/application guide;
7. open educational book/textbook or recognized specialist reference;
8. GitHub/open-source reference implementation or repository;
9. research plugins/connectors for discovery and citation finding;
10. ask the user only after the above checks fail to resolve the project-specific question.

## GitHub / open-source rule
GitHub and open-source repositories are mandatory discovery channels when they can materially improve understanding of a technical concept, protocol, software mapping or reference implementation.

They are SUPPORTING references, not project authority. Before using a repository:
- prefer original/upstream maintainers;
- verify license, maintenance status and documentation quality;
- distinguish code behavior from engineering requirements;
- never let a repository override the project baseline, applicable standard or official manufacturer specification;
- record repository name, branch/tag/commit when reproducibility matters.

## Plugin research rule
Research plugins/connectors MAY be used to discover books, papers, manufacturer documentation, standards metadata and current technical references.

A plugin/tool is a discovery mechanism, not evidence by itself. The resulting underlying source must be identified and classified before it supports an engineering claim.

## Source classes
Use these evidence classes when applicable:
- PROJECT_SOURCE_FACT
- PROJECT_DECISION
- APPLICABLE_NORMATIVE_REQUIREMENT
- REFERENCE_ONLY_GUIDANCE
- OFFICIAL_AUTHORITY
- OFFICIAL_MANUFACTURER
- OPEN_EDUCATIONAL_BOOK
- SPECIALIST_REFERENCE
- OPEN_SOURCE_REFERENCE_IMPLEMENTATION
- ENGINEERING_INFERENCE

## Required handling of inference
If the project does not explicitly establish a relationship:
- label it as an engineering hypothesis/question;
- research supporting material;
- state what the external material proves and what it does NOT prove about this project;
- do not promote it to a project finding until project evidence or an applicable requirement closes the link.

## Regression case: DO versus relay
The historical failure mode to prevent is:
"4 DO in the I/O list + 3 relays in the material list => one relay is missing."

This conclusion is invalid unless the project explicitly maps those DO points to those external relays.

Correct treatment:
- identify each DO destination from project evidence;
- identify the purpose and wiring of each relay;
- only then compare quantities or mappings.

## Repository assets
- `datacenter/AUTOMATION_TECHNICAL_KNOWLEDGE_BASE.json`
- `datacenter/AUTOMATION_REFERENCE_LIBRARY.json`
- `docs/OPEN_SOURCE_AND_PLUGIN_CATALOG.md`
- `memory/ENGINEERING_COMPATIBILITY_MEMORY.md`

## Confidentiality
Store only public-source metadata, engineering concepts and process rules in the public repository. Never commit confidential project drawings, proprietary books, paid-standard text or private project decisions.
