# REA standalone release verifier design (2026-10-28)

Goal: add independent tamper detection to the REA ZIP packaging flow without depending on MCE, before installing a private Secure MCP Tunnel client.

Alternatives: (1) reuse the MCE release verifier by importing MCE -- rejected, products must be independent; (2) trust ZIP internal hashes alone -- rejected, cannot prove origin; (3) implement a standalone stdlib validator supporting an external digest and approved Git source pin -- selected.

Deliverable: `systems/rea/scripts/release_integrity.py`, tests, README and runbook. Validate exact manifest membership, bounded size, SHA-256, safe paths, symbolic-link and duplicate rejection. Allow optional operator-trusted whole-ZIP SHA and commit pin for backward compatibility. Return only `INTEGRITY_PASS` or `BLOCKED`, never a production approval.

Security boundaries: no ZIP extraction, no execution, no outbound network, no workspace or credential access. External provenance and real ChatGPT tool discovery remain operator gates.
