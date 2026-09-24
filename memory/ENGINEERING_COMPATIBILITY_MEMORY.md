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
0. Every engineering compatibility report, re-evaluation, audit result and /visualize output must render through the native /visualize presentation layer. @Build Web Data Visualization (Plugin_40dab999fe9c8191bbc2f550371692fc) is a preferred enhancement when executable; its absence must not block visualization. Use the best interactive native visualization available and upgrade to Build Web Data Visualization later without changing engineering content.
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

## Automation compatibility report model
Permanent reusable model:
- `governance/AUTOMATION_COMPATIBILITY_REPORT_MODEL_v1_0.md`
- `datacenter/AUTOMATION_COMPATIBILITY_REPORT_MODEL.json`

Permanent rules:
- /visualize is the default rendering layer; Build Web Data Visualization is progressive enhancement.
- questions, confirmed errors and engineering problems stay separated.
- every open question records source checks before escalation and provides an answer field.
- every user-facing Automation question batch is a governed /visualize artifact; when an interactive surface is available, plain Markdown/list-only questions are non-compliant.
- each question card carries ID, severity/priority, area, rationale, project documents involved, completed source checks, status and answer field; answered questions remain in a resolved-questions module.
- every confirmed finding exposes documents involved in four groups: source/evidence, correlated/conflicting, normative/reference, and documents to correct.
- normative/reference documents require applicability state and basis. REFERENCE_ONLY guidance cannot create a confirmed nonconformity by itself.
- revised documents are rechecked before findings are closed and before Release Gate can pass.

## Evidence-before-assumption permanent rule
Permanent regression lesson:
- A DO/DQ is a controller output point/channel. An external interface/interposing relay is a separate device.
- DO quantity SHALL NOT be used to infer relay quantity.
- Relay quantity SHALL NOT be used to infer DO quantity.
- TAG name, prefix, row adjacency or equal counts do not prove electrical/functional mapping.
- DO -> relay association requires explicit project evidence: wiring/interconnection diagram, terminal plan, I/O mapping, panel schematic, cable schedule, loop diagram or specification.
- A PLC output module may itself be transistor, triac or relay technology; this is different from an external interface relay.
- If a relationship is unclear, keep it as a question/NOT_VERIFIABLE, research supporting material, and state what the external source proves versus what remains project-specific.
- Owning-document routing is mandatory before asking the user: first identify and search the project document class most likely to own the answer (network architecture, I/O/interconnection, control philosophy/C&E, HVAC/process master, electrical supply/protection, material/datasheet).
- If the user points to the owning document, reopen/recheck that document and remove the item from the user-question queue when the source resolves it.
- Mandatory support research channels include official manufacturer material, open educational books, GitHub/open-source repositories and research plugins/connectors where they materially improve understanding.
- GitHub/open-source/plugins never override the project baseline, applicable standard or official manufacturer source.

Canonical assets:
- `governance/AUTOMATION_EVIDENCE_RESEARCH_GOLDEN_RULE_v1_0.md`
- `datacenter/AUTOMATION_TECHNICAL_KNOWLEDGE_BASE.json`
- `docs/OPEN_SOURCE_AND_PLUGIN_CATALOG.md`

## Default Automation reference library
For every Automation project, consult these references before escalating a technical doubt to the user:

- PETROBRAS N-1882 Rev. F (11/2023) — `Critérios para Elaboração de Projetos de Instrumentação`.
- PETROBRAS N-1883 Rev. F (05/2024) — `Apresentação de Projeto de Instrumentação, Controle e Automação`.
- PETROBRAS N-2833 Rev. A — Annex A forms 01-14, used as the standard forms/list reference set.

Permanent applicability rule:
- these are a **reference-by-default library**, not universal mandatory requirements;
- always check contract, project basis, discipline scope and current approved revision before classifying noncompliance;
- N-1883 Rev. F item 1.4 explicitly excludes electrical-system automation, building automation and HVAC automation from its direct scope. For those projects, N-1883/N-2833 may be used only as documentary/engineering references unless another project requirement explicitly invokes them;
- reference-only differences remain questions/NOT_VERIFIABLE or engineering observations until an applicable requirement proves divergence;
- every confirmed finding must display its **documents involved**: source/evidence, correlated/conflicting project documents, normative/reference documents, and documents to correct.

## Maintenance
Update this file only when the process contract changes. Project-specific facts belong in governed project datasheets, not here.
