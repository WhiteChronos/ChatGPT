# Database schema guidance

Use normalized relational records for panels, components, sources, suppliers, panel components, I/O points, agent runs, memory events, QA runs/findings, artifacts, render metrics, training examples, model registry, evolution proposals, plugin registry and skill registry.

Use foreign keys and append-only event history for released revisions. Never delete evidence needed to reconstruct an issued state.
