# Checkpoint schema

Use one JSON object per logical checkpoint with: checkpoint_id, timestamp_utc, scope, user_intent, action_type, inputs, decisions, outputs, files_changed, sources, validation, unresolved, next_action, prompt_delta, and versions.

Rules:
- Keep each checkpoint self-contained enough to resume work.
- Store source URLs/repository refs when available.
- Store calculations by reference to durable files rather than duplicating large outputs.
- Never store secrets or credentials.
- Correct historical mistakes with a new checkpoint; do not rewrite prior meaning.
