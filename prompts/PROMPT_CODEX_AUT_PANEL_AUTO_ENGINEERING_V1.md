# PROMPT CODEX — AUT PANEL AUTO ENGINEERING V1

Operate only on a governed **candidate revision** under the approved AUT Panel automatic-engineering specification.

## Required authority

Read the approved spec, implementation plans, AGENTS.md, Golden Rules, current panel baseline, validated sources, and canonical input hashes before changing engineering.

Use `pipeline/aut_panel_candidate_revision.py` to create/apply candidate changes. A successful automatic run terminates at `CANDIDATE_READY_FOR_HUMAN_REVIEW` until a human release decision exists.

## Absolute prohibitions

- You **must not overwrite** historical R02 or any released/frozen historical revision.
- You **must not weaken** deterministic gates, Golden Rules, QA thresholds, source-validation requirements, or normative controls to make a candidate pass.
- You must not auto-merge any release PR.
- You must not issue fabrication release or binding procurement.
- You must not download or deploy candidate logic to a production PLC.
- CI success is not engineering approval.

## Candidate changes allowed

When supported by validated source evidence and deterministic checks, a candidate revision may change enclosure, exact component selection, quantities, layout, electrical sizing, I/O, communication, panel split proposal, and candidate PLC logic. Every change requires a before/after candidate delta, source evidence, invalidated downstream stages, tests and rollback path.

## Required execution sequence

1. Resolve panel and source revision.
2. Load canonical input hashes and validated manufacturer/normative evidence.
3. Create a new candidate revision; never edit historical R02 in place.
4. Apply candidate changes using the authorized policy.
5. Recalculate every invalidated downstream engineering stage.
6. Generate dimensional artifacts only from validated candidate geometry/BOM.
7. Run deterministic QA and regression tests on the serialized artifacts.
8. Synchronize canonical memory; auxiliary memory remains non-authoritative.
9. Stop at `CANDIDATE_READY_FOR_HUMAN_REVIEW` unless a trusted human approval record is supplied to the release-authorization gate.

## Mandatory report

Report all of the following explicitly:

- files changed;
- canonical input hashes;
- source evidence used;
- candidate delta for every engineering modification;
- tests run and exact results;
- engineering HOLDs and REPROVADO findings;
- rollback path and rollback target;
- artifact hashes;
- statement that no auto-merge, fabrication release, binding procurement, or production PLC deployment was executed.
