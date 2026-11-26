# Design: MCE closure skill, independent of REA

Goal: deliver a portable Skill that helps assess project evidence for the standalone MCE engineering system, never auto-authorizing Excel changes or impersonating an engineer.

Acceptance: explicit trusted SHA inventory, path containment, no symlinks, no duplicates, read-only validation, deterministic JSON, negative cases, preservation of the master workbook. External GitHub merge, real model approval and human FAT/SAT are independent and cannot be inferred from an inventory check. The skill uses the existing production_readiness.py and release_integrity.py when an authorized workspace exists.

Scope: skills/mce-fechamento-operacional with one fail-closed evidence checker. Existing MCE engine remains untouched. Publish in PR #118 only. Package an installable skill.zip for ChatGPT and Codex.
