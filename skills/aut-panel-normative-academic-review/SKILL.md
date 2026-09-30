---
name: aut-panel-normative-academic-review
description: Review industrial automation-panel projects against applicable standards, regulations, academic studies, technical books, and bibliographic references. Use after project/panel definition is frozen and before detailed engineering is finalized, especially when norms, editions, applicability, literature evidence, bibliographic traceability, controlled document copies, or conflicts between project documents and external references must be established and archived.
---

# AUT Panel Normative & Academic Review

Use this skill as Step 3 of the AUT Panel methodology, after `STEP1_SCOPE_FROZEN` and `STEP2_PANEL_DEFINITION_FROZEN`.

## Workflow
1. Load PROJECT_NUMBER, project/panel manifests, parameter registry, Data Center, memory and normative registry.
2. Decompose project documents into technical review topics.
3. Search official normative sources first, then peer-reviewed academic literature and recognized technical books/reference works.
4. Distinguish applicability from existence. Record jurisdiction, contractual adoption, scope, edition and exclusions.
5. Register every source using `references/source-registry.md`.
6. Archive a controlled local copy only when lawful access/copying permits it. Never bypass paywalls, DRM or access controls.
7. For restricted standards/books/papers, store metadata, official URL/DOI/ISBN, citation, consulted date, pages/sections used, permitted short excerpts and controlled summary. If user supplies a licensed copy, hash and index that copy.
8. Store binaries/full documents in the Data Center; memory stores pointers, hashes, extracted rules/parameters, applicability decisions, conflicts and conclusions.
9. Build normative applicability, academic evidence and conflict matrices.
10. Return HOLD_NORMATIVE_CONFLICT/HOLD_NORMATIVE_EDITION when release-critical issues remain unresolved.
11. Synchronize Data Center and project memory.

## Required outputs
- NORMATIVE_APPLICABILITY_MATRIX
- ACADEMIC_EVIDENCE_MATRIX
- BIBLIOGRAPHIC_REFERENCE_REGISTER
- CONTROLLED_SOURCE_ARCHIVE_INDEX
- NORMATIVE_CONFLICT_REGISTER
- STEP3_REVIEW_SUMMARY
- MEMORY_SYNC_RECORD

Pass only as `STEP3_NORMATIVE_ACADEMIC_BASE_FROZEN`.

## Tool routing
- Scite/Consensus: academic discovery and synthesis.
- Tavily/Firecrawl: official-source discovery and controlled extraction.
- GitHub/Data Center: canonical auditable storage.
- Engram: supplemental memory only.
- Wolfram: calculations, never normative applicability.

## Control statement
RESEARCH MORE, ASK LESS, ASSUME NOTHING. ARCHIVE THE EVIDENCE, NOT JUST THE ANSWER.
