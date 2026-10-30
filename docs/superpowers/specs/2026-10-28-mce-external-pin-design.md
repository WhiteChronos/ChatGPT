# MCE independent release external-pinning design (2026-10-28)

Goal: make standalone MCE ZIP verification distinguish SHA-256 self-consistency from external release provenance without changing original Excel or joining REA.

Alternatives: (1) trust ZIP manifest alone -- rejected, self-authentication; (2) embed checksum inside ZIP -- rejected, same trust failure; (3) optional operator-trusted whole-ZIP SHA-256 and Git commit pin -- selected for compatibility and fail-closed mismatch. Neither proves a cryptographic publisher signature or engineering acceptance.

In-scope: `systems/mce/scripts/release_integrity.py`, its tests, README and release runbook. Excluded: master workbook changes, project data, deployments, auto-merge, acceptance automation.

Inputs: existing release ZIP; optional SHA-256 from independently trusted approval source; optional 40-hex commit SHA from GitHub PR/release approved by maintainer. Errors: invalid pins or mismatches return BLOCKED and exit 2. Output always has `production_complete=false`; even a PASS is not FAT/SAT or model homologation.

Review: evidence-first, constraints, ZIP path adversarial tests and standalone maintainability. Requires real host and human acceptance for production.
