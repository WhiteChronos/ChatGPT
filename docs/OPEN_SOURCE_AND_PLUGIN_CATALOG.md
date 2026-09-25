# Open-source and Plugin Assistance Catalog

## Purpose
Curated discovery catalog for engineering automation/data compatibility work. This is not an allow-list and does not auto-install, vendor-lock, or approve any dependency. Every adoption requires license, maintenance, cybersecurity, protocol and project-fit review.

## Open-source repositories discovered

### PLC I/O semantics and reference implementations
- `Autonomy-Logic/openplc-runtime` — upstream OpenPLC runtime; use as an open-source IEC 61131-3/I-O mapping reference implementation, never as project authority.
- `CONTROLLINO-PLC/OpenPLC_examples` — OpenPLC examples showing IEC-style digital output mapping to hardware, including platforms that distinguish digital outputs and relay outputs.
- `HilscherAutomation/netPI-openplc` — open-source OpenPLC integration example with explicit %IX/%QX digital I/O mapping.

### Industrial protocols / PLC integration
- `pymodbus-dev/pymodbus` — Modbus client/server tooling.
- `pymodbus-dev/modbus-simulator` — Modbus simulation/test support.
- `sourceperl/pyModbusTCP` — compact Modbus TCP tooling.
- `Autonomy-Logic/openplc-runtime` — OpenPLC runtime.
- `Autonomy-Logic/openplc-editor` — OpenPLC editor.
- `eclipse-milo/milo` — OPC UA stack for Java.

### Flow, integration and observability
- `node-red/node-red` — flow-based integration and prototyping.
- `grafana/grafana` — dashboards/observability.
- `grafana/mcp-grafana` — MCP integration for Grafana.
- `prometheus/prometheus` — monitoring/time-series metrics.
- `prometheus/alertmanager` — alert routing.
- `timescale/timescaledb` — time-series extension for PostgreSQL.

### Data/schema quality
- `python-jsonschema/jsonschema` — JSON Schema validation.
- `python-jsonschema/check-jsonschema` — schema CLI checks.
- `unionai-oss/pandera` — dataframe/data-contract validation.

### Diagrams / engineering visualization
- `mermaid-js/mermaid` — text-to-diagram.
- `mermaid-js/mermaid-cli` — CI rendering for Mermaid.
- `excalidraw/mermaid-to-excalidraw` — editable visual conversion.

### Open technical books / learning references
- Tony R. Kuphaldt, `Lessons In Industrial Instrumentation` — open educational reference for relay control systems, interposing relays and PLC I/O.
- Control.com textbook chapter `Interposing Relays in PLCs` — supporting explanation of when an interposing relay is used between mismatched controller/field circuits.

These sources explain general concepts only. They do not prove project-specific wiring.

## ChatGPT plugins / connected tools
Already useful in this environment:
- GitHub — repository inspection, PRs, CI and publishing.
- Adobe Acrobat — PDF transformation/extraction workflows.
- Figma — diagrams/design collaboration.
- MindMap — interactive structured maps.
- Coda — structured work tracking.

Suggested optional connectors:
- Scite — research-paper discovery and citation-context checks for technical literature; discovery aid only, underlying source remains the evidence.
- Firecrawl — web/document research and change monitoring.
- Miro — architecture, sequence and review boards.
- Whimsical — flowcharts, sequence diagrams and technical visualizations.

## Adoption rules
Before adding any external repository or plugin to production workflow:
1. verify license and redistribution terms;
2. verify active maintenance and release cadence;
3. review security posture and dependency surface;
4. confirm protocol/version compatibility;
5. isolate experiments from authoritative project evidence;
6. pin versions where reproducibility matters;
7. add regression tests before release-gate dependency;
8. never allow an external tool to silently rewrite raw Data Center evidence.

## Research rule
This catalog is intentionally curated rather than claiming to enumerate every public repository on GitHub. GitHub is dynamic and effectively unbounded; discovery should be repeated for a concrete engineering need.

## Evidence-before-assumption research workflow
For an ambiguous component relationship:
1. search project baseline and wiring/interconnection evidence;
2. search applicable standards and official manufacturer documentation;
3. consult open educational books/specialist references;
4. search GitHub/open-source repositories for reference implementations;
5. use research plugins/connectors to discover additional sources;
6. explicitly separate generic concept evidence from project-specific evidence;
7. if the project link remains unproven, keep the item as NOT_VERIFIABLE/question.

Never infer one-to-one mappings from counts, names, prefixes or adjacent rows. In particular, DO count does not imply external relay count.

### Codex workflow and repository-governance references
- `openai/codex` — official open-source Codex CLI/harness. Relevant patterns: repository `AGENTS.md`, project `.codex/config.toml`, app-server/SDK/exec integration surfaces, bounded context, explicit verification and repository-scoped instructions.
- `duduaguiaarr-source/miniguia-estudos-sistemas-operacionais` — small public study project whose useful pattern is source curation before AI synthesis: define source set, specify answer format/level, require source-bounded answers, and surface uncertainties instead of silently filling gaps.
- `crisxuan/agent-workflow-kit` — evaluation-first workflow kit: inspect repository risk first, choose the smallest workflow level, and require verification before claiming completion.
- `dev-hara0004/codex-agent-workflow-template` — reusable Codex project structure with `AGENTS.md`, `.codex/`, workflow modes, templates, test plans and traceability; useful principle: avoid duplicating the same information across documents and keep one source of truth.
- `hdtinh57/codex-orchestrated-project-template` — orchestration-focused template using thin agents, skills, prompt packs, rules and hooks; useful principle: keep reusable domain knowledge in skills/rules instead of bloating one global prompt.

Adoption note: non-OpenAI repositories are reference-only patterns. Review license, maintenance, security and fit before adopting any files or automation.

Secondary tutorial reference:
- DataCamp, `OpenAI Codex: um guia passo a passo com 3 exemplos práticos` — useful onboarding overview of GitHub-connected tasks, sandboxes, pull requests and `AGENTS.md`; not an authority source for Codex behavior. Prefer official OpenAI docs for current product semantics.

### Document fidelity, parsing and engineering-document interpretation
- `docling-project/docling` — layout-aware multi-format parsing with reading order, tables, page structure, images and structured document representation; strong candidate for cross-checking complex engineering documents.
- `microsoft/markitdown` — lightweight semantic conversion of Word/PDF/Office files to Markdown for LLM pipelines; useful for text structure, explicitly not a high-fidelity layout renderer.
- `pymupdf/PyMuPDF` — native PDF page count/page tree, text geometry, rendering and image extraction; use for PDF-grounded page identity and coordinates.
- `python-openxml/python-docx` — DOCX paragraphs/tables/styles; combine with direct OOXML ZIP inspection for `docProps/app.xml`, headers/fields and other package metadata.
- `decalage2/olefile` — legacy OLE/Word .doc property streams, including metadata used for native document inspection.
- `LibreOffice/core` — cross-platform Office renderer/converter; use for visual QA but not as authoritative Word pagination when reflow/font substitution changes layout.
- `PaddlePaddle/PaddleOCR` — OCR plus structure-aware document parsing for scans/images, tables and complex layouts.
- `ocrmypdf/OCRmyPDF` — adds searchable OCR text to scanned PDFs while preserving the PDF artifact; useful before semantic extraction.
- `Unstructured-IO/unstructured` — multi-format partitioning/chunking for semantic pipelines; use as a supporting extraction layer, not layout authority.

Document-tool adoption rule: compare at least source-native structure + semantic extraction + visual rendering for material engineering claims. A tool output describes that tool's interpretation and does not silently replace the source artifact.
