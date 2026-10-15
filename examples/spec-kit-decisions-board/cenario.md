# Scenarios and validation

## SC-01 / REQ-01 / AC-01
Given a synthetic decision with unique ID, when recorded, then all four fields are retained.

## SC-02 / REQ-02 / AC-02
Given multiple saved decisions, when listed, then entries are ordered deterministically by date and ID.

## SC-03 / REQ-03 / AC-03
Given a set of synthetic decisions, when exporting, then valid Markdown is returned without secrets.

## Adversarial scenarios
Reject duplicate IDs, missing rationale and malformed dates; do not expose credentials or modify originals.
