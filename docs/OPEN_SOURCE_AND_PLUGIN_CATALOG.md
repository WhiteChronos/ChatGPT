# Open-source and Plugin Assistance Catalog

## Purpose
Curated discovery catalog for engineering automation/data compatibility work. This is not an allow-list and does not auto-install, vendor-lock, or approve any dependency. Every adoption requires license, maintenance, cybersecurity, protocol and project-fit review.

## Open-source repositories discovered

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
