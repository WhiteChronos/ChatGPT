# MCE release archive attestation — design

Goal: add a read-only integrity gate for an independently packaged MCE release; do not alter MCE engineering logic, the XLSX original or REA.

## Approaches reviewed (Arena)

- **CI means production**: rejected; CI cannot certify a real project/SS, process hazards, or acceptance.
- **Automatic archive extraction/install**: rejected; unsafe ZIP and workbook mutation risks.
- **Fail-closed SHA-256 ZIP preflight**: selected; readable by an operator, no filesystem writes, no auto-approval.

## Contract

The ZIP contains one `MCE_INDEPENDENTE/` root with a `manifest.json` whose `files` map declares every payload member and its SHA-256. Duplicate names, unsafe paths, symlinks, unexpected members, invalid hashes, excessive decompressed sizes and corrupt archives must fail with exit 2. Success means `INTEGRITY_PASS` and `production_complete=false`, never owner approval. Operators compare the ZIP SHA to the approved release SHA before installation.

## Boundaries

No dependency on REA, HTTP, MCP or external services. No real project documentation or customer files are part of test fixtures or GitHub commits. Engineering and human release gates remain separate.
