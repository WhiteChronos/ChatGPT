# MCE private web implementation plan

> Use Superpowers executing-plans inline. No subagents authorized.

Goal: expose the existing MCE workflow through a private, confined MCP adapter,
including preliminary Excel generation only after external signed approval.
Spec: ../specs/2026-10-29-mce-private-web.md, approved by the user on 2026-10-29.
Stack: Python 3.12, existing MCE CLI, official MCP SDK 2, Ed25519 verification.

Constraints: preserve originals; <=50 causes/sheet; never infer identities or
engineering approval; independent roots/keys/tunnel; no private source publication.

Review focus: path traversal/links; malicious OOXML/resource exhaustion; replay or
tampering of approvals; remote self-approval; transport discovery vs execution.

## Tasks

- [ ] Add failing tests for confined MCE adapter and external approval binding.
  Test exact-hash changes/contract/model/analysis, missing signature, tampering,
  path escape, symlink/hardlink, invalid ZIP/XML and unchanged workbook.
- [ ] Implement scripts/mce_web.py as an adapter to existing mce_workflow.py.
  Inputs are copied from an authorized inbox; workspaces are unique; only seven
  fixed operations exist. No shell, remote authorize or arbitrary file writes.
- [ ] Add operator-only signed approval CLI and official SDK stdio adapter.
  Server receives public key only; signing private key remains outside its root.
- [ ] Verify SDK lifecycle and allowlisted tools with synthetic input only.
- [ ] Add mce-operacao-web skill, update manifests/README and canonical mirrors,
  dependency group, Windows-only QA and expanded product scanner coverage.
- [ ] Run full MCE regression/security/memory gates, commit with append-only memory,
  publish PR update and inspect exact-HEAD hosted checks.
- [ ] Export/verify portable skills package and local Codex installation. Prepare
  dedicated private tunnel and account connection with concrete access approval.
  Report real ChatGPT call independently from package/transport checks.

Human project acceptance, production and SHA-specific merge/deploy remain external.

Ruling: consolidate concurrent HEAD 42e0b6485c30a5e8de80c89542afc0485af6f538,
preserve matriz-causa-efeito as the single onboarding entry and its three adapters,
SQLite and Windows-only rule. mce-operacao-web is a transport skill, not another
engineering router, database or editor. No Linux/WSL/Bash MCE execution.
