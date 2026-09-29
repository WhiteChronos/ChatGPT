# Quality and learning contract

Run deterministic validation before ML scoring. ML can prioritize review but cannot convert a deterministic failure into a pass.

Use human-reviewed labels only. Store dataset fingerprint, feature schema, model version, metrics and training time.

Suggested features include source uncertainty, lifecycle uncertainty, quantity mismatch, enclosure fill ratio, clearances, routing complexity, overlap count, template diff, reviewer corrections and historical failure frequency.

Every evolution proposal must contain problem, evidence, candidate change, affected files, expected benefit, risk, tests, rollback plan and confidence. Changes to canonical contracts always require explicit human approval.
