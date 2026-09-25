# Open-source and Plugin Assistance Catalog

## Purpose
Curated discovery catalog for engineering automation/data compatibility work. This is not an allow-list and does not auto-install, vendor-lock, or approve any dependency. Every adoption requires license, maintenance, cybersecurity, protocol and project-fit review.


## Authoritative source hierarchy

External engineering requirements are governed by `datacenter/ENGINEERING_REFERENCE_REGISTRY.json`.

Priority is:

1. approved project source for project-specific facts;
2. official standards/specifications issued by the responsible authority;
3. official guidance;
4. open-source implementations for testing, simulation, integration and validation support only.

An open-source repository is never normative authority and must never be used as project evidence. Any finding whose claim basis is `EXTERNAL_KNOWLEDGE` must cite a registered authoritative source ID.

The canonical registry currently covers IEC 61131-3, IEC 61511-1, IEC 62443-2-1, ISA-5.1, ISA-101.01, ISA-18.2, NIST SP 800-82 Rev. 3, OPC UA, Modbus Application Protocol V1.1b3, ANSI/ASHRAE 135-2024 BACnet and JSON Schema Draft 2020-12.

## Open-source repositories discovered

### Industrial protocols / PLC integration
- `pymodbus-dev/pymodbus` — Modbus client/server tooling.
- `pymodbus-dev/modbus-simulator` — Modbus simulation/test support.
- `sourceperl/pyModbusTCP` — compact Modbus TCP tooling.
- `Autonomy-Logic/openplc-runtime` — OpenPLC runtime.
- `Autonomy-Logic/openplc-editor` — OpenPLC editor.
- `eclipse-milo/milo` — OPC UA stack for Java.
- `FreeOpcUa/opcua-asyncio` — OPC UA client/server support for Python and interoperability testing.
- `ChristianTremblay/BAC0` — BACnet test/integration support for Python.

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

## ChatGPT plugins / connected tools
Already useful in this environment:
- GitHub — repository inspection, PRs, CI and publishing.
- Adobe Acrobat — PDF transformation/extraction workflows.
- Figma — diagrams/design collaboration.
- MindMap — interactive structured maps.
- Coda — structured work tracking.

Suggested optional connectors:
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
