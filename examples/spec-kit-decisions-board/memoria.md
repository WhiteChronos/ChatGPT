# Project memory

## Decisions
- DEC-01: use synthetic data and no remote services in this example.
- DEC-02: keep all original Markdown records rather than replace them with summaries.

## Retained evidence
PRD requirements REQ-01..REQ-03, acceptance AC-01..AC-03, tasks TASK-01..TASK-04.

## End-to-end traceability
| Requirement | Task | Scenario | Test | Evidence |
| --- | --- | --- | --- | --- |
| REQ-01 | TASK-01 | SC-01 | TEST-01 | EVIDENCE-01 |
| REQ-02 | TASK-02 | SC-02 | TEST-02 | EVIDENCE-02 |
| REQ-03 | TASK-03 | SC-03 | TEST-03 | EVIDENCE-03 |

## EVIDENCE-01 — capture
`tests/test_spec_kit_decisions_board.py::TestDecisionsBoard.test_capture_retains_all_fields` exercises the real local domain object with synthetic data.

## EVIDENCE-02 — ordering
`tests/test_spec_kit_decisions_board.py::TestDecisionsBoard.test_list_orders_by_date_then_id` checks the literal expected chronological and ID order.

## EVIDENCE-03 — export
`tests/test_spec_kit_decisions_board.py::TestDecisionsBoard.test_export_markdown_sanitizes_fields` checks deterministic Markdown and sanitization without credentials.

## Checkpoint
Six-file specification, local behavior implementation and deterministic tests are present. Hosted skill discovery and Codex Cloud execution remain pending until verified by the target host; repository files alone are not that evidence.
