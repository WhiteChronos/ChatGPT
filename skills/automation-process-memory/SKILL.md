---
name: automation-process-memory
description: Persist and recover engineering work for automation/instrumentation projects by checkpointing every substantive action to GitHub, maintaining a living master prompt, structured action ledger, source provenance, and optional open-source memory backends. Use for automation cable calculations, engineering document workflows, GitHub-backed project memory, datacenter synchronization, prompt evolution, checkpointing, process recovery, or any task where the user asks to never lose progress or to save/update state after each action.
---

# Automation Process Memory

## Core contract

Treat `WhiteChronos/ChatGPT` as the durable system of record unless the user explicitly selects another repository.

After every substantive action, create a checkpoint before finishing the turn. A substantive action includes research, engineering decision, calculation-rule change, source addition, code/file edit, schema change, prompt change, model change, document decision, validation result, or new pending item.

Do not claim background or automatic persistence outside the current turn. Persist through explicit GitHub connector writes performed in the turn.

## Required state files

Maintain:
- `memory/AUTOMATION_CABLE_ACTIVE_PROMPT.md`
- `memory/AUTOMATION_CABLE_ACTION_LOG.jsonl`
- `datacenter/AUTOMATION_CABLE_PROCESS_STATE.json`
- `datacenter/AUTOMATION_CABLE_MODEL.json`
- `memory/AUTOMATION_CABLE_MEMORY.md`

## Per-action workflow

1. Recover state from the active prompt, process state, action log, and repository governance.
2. Perform the requested action while preserving engineering provenance and deterministic-rule authority.
3. Create a structured checkpoint containing intent, decisions, outputs, files, sources, validations, unresolved items, next action, prompt delta, and versions.
4. Update the living prompt as compact state, not a transcript.
5. Update machine-readable process state.
6. Confirm GitHub writes succeeded before claiming persistence.

## Prompt evolution

Keep mission, repository/branch, invariants, architecture, current task, last completed action, accepted sources, versions, unresolved items, next action, and checkpoint protocol. Remove superseded temporary instructions from the active prompt while preserving history in the ledger.

## Open-source memory strategy

GitHub history is the primary audit trail. Mem0, Graphiti, Cognee, Hindsight, Letta, OpenMemory, memU and related systems are secondary indexes/retrieval layers only. Engineering calculations must not depend on a single memory backend.

## Engineering/ML separation

Machine learning may recommend, rank, retrieve similar approved cases, or detect anomalies. It may not override deterministic engineering-rule failures or manufacturer/protocol limits.

## Completion gate

Before ending a substantive turn, verify requested work, relevant file updates, checkpoint persistence, prompt update, unresolved issues, and next action. If no substantive state changed, do not create a noisy checkpoint.
