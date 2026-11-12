# MCE operational release candidate

Scope: prepare the complete public-code package for the reviewed MCE candidate and qualify it on Windows. Do not install, deploy, merge, ingest private sources or grant engineering approval.

1. Build from exact committed Git bytes under systems/mce, never from untracked workspace files. Produce a deterministic ZIP with the existing MCE_INDEPENDENTE manifest contract and source SHA. Refuse links, invalid commit, oversized payloads and overwrite. Reuse release_integrity.py for verification.
2. Add real Git/ZIP regression tests before implementation: deterministic build, untracked exclusion, wrong commit, linked member and overwrite refusal. Preserve production_complete=false.
3. Add Windows GitHub Actions qualification: existing product tests and skill validation, complete package, digest and verification report. Upload only public-code candidate artifacts. This workflow cannot approve a project or deploy.
4. Update release/operational instructions and canonical memory in the same commit. Test the whole product, have a native independent reviewer inspect the delta, prepare a draft PR against main, and check its exact-SHA CI.
5. Final human gates: SHA-specific integration authorization, approved original XLSX/sources/SS/contract, private restore and independent backup, platform access controls and engineering acceptance. Keep blocked evidence explicit; no synthetic substitutes.

Arena alternatives: merging immediately fails the SHA-specific authorization gate; installing on this PC conflicts with the GitHub-only target and missing project data; qualifying the committed full package resolves an actual delivery gap without changing security boundaries; claiming production from CI is rejected. Selected: qualify the full candidate and leave human/project gates intact.
