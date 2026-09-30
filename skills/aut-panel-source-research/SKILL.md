---
name: aut-panel-source-research
description: Research and validate official engineering sources for automation-panel components, standards, gateways, PLCs, I/O, UPS, batteries, networking, sensors, HVAC interfaces, and enclosure systems. Use when exact models, capacities, dimensions, lifecycle, manuals, communication limits, or normative requirements must be established from manufacturers or authoritative technical sources.
---

# AUT Panel Source Research

Research exact engineering evidence before selection.

## Source hierarchy
1. Official manufacturer site/manual/datasheet/CAD.
2. Manufacturer technical portal.
3. Official standard.
4. Authorized distributor or official representative.
5. Project-controlled internal document.
6. Peer-reviewed/academic source for methodology.
7. Secondary source only as labeled support.

## Workflow
1. Define the exact technical question and target model/family.
2. Search official manufacturer sources first; use web-research plugins for discovery and crawling when available.
3. Capture document title, code, revision/date, page/section, official URL, consultation date, lifecycle, and the exact project fact supported.
4. Cross-check model identity and capacity. Distinguish physical ports, logical devices, addresses, channels, buses, and system limits.
5. Run two-source/dual-agent validation for release-critical facts.
6. Register evidence in the Data Center and preserve source provenance.
7. If exact evidence is missing, use HOLD rather than approximation.

## Plugin routing
Prefer installed Tavily/Firecrawl for current manufacturer-web discovery/crawl; Scite for academic evidence; Wolfram for rigorous calculations; Airtable/Coda/Notion only as structured project knowledge stores, never as higher authority than official sources; Acumen may surface missing-current-information risks but cannot create engineering facts.
