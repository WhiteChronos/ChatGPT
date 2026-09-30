---
name: aut-panel-autonomous-improvement
description: Continuously analyze AUT Panel engineering workflow quality and propose safe, evidence-based improvements without automatically changing locked engineering rules. Use after QA failures, recurring errors, source conflicts, project corrections, tool discoveries, plugin changes, CI regressions, or when the user asks the system to improve itself, suggest automations, learn from mistakes, or evolve its methodology.
---

# AUT Panel Autonomous Improvement

Operate autonomously for observation and proposal, never for uncontrolled engineering mutation.

## Learning loop
1. OBSERVE project events, QA failures, HOLDs, user corrections, source changes, CI results, and plugin/tool updates.
2. CLASSIFY as data error, process error, source error, geometry error, capacity error, stale-artifact error, or improvement opportunity.
3. Identify ROOT CAUSE and affected artifacts.
4. Create a measurable proposal with expected benefit, risk, rollback, and regression test.
5. Score the proposal with `scripts/score_candidate.py`.
6. Run sandbox simulation or dry-run when possible.
7. Require deterministic QA.
8. Place the proposal in the improvement backlog.
9. Require HUMAN GATE before changing Golden Rules, locked templates, released revisions, exact component selections, or release status.
10. After approval, version the change and measure whether the original failure rate improves.

## Allowed autonomous actions
- detect inconsistencies;
- create HOLD/review proposals;
- open improvement suggestions;
- identify stale artifacts;
- compare plugin/repository capabilities;
- propose tests and new skills;
- refresh non-authoritative discovery registries;
- recommend automations.

## Forbidden autonomous actions
- clear engineering HOLD;
- approve for issue;
- change frozen LI/BOM or panel dimensions;
- change Golden Rules;
- merge PRs automatically;
- install/promote core dependencies without governance;
- convert unverified memory/plugin output into engineering fact.

## Improvement score
Prioritize high-frequency, high-severity, highly detectable failures with low implementation risk. Use the script output only as triage; human approval remains final.

## Memory
Store confirmed learning separately from panel-specific facts. Every confirmed error must generate root cause, preventive rule, affected artifacts, and a regression check.
