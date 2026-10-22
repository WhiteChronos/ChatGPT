# Architecture — Decisions Board

## Components
- UI: local read-only Markdown viewer or CLI preview.
- Domain: Decision(id, title, rationale, date).
- Storage: example-only structured Markdown in an authorized workspace.
- Export: deterministic Markdown generation.

## Interfaces
REQ-01 uses add_decision; REQ-02 uses list_decisions; REQ-03 uses export_markdown. Explicitly no external network boundary.

## Security and tradeoffs
Sanitized examples only; no secrets, no external persistence. Start from a simple domain module and avoid unnecessary frameworks. Evidence of actual code execution is not claimed.
