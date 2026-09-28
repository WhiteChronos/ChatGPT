# AGENTS.md — AUT PANEL CONTROL

## Scope
This branch implements AUT - Paineis de Automacao e Controle.

## Mandatory bootstrap
Before changing engineering logic, data contracts, panel layout, LI/BOM, normative data, QA, ML or evolution behavior, read:
1. prompts/PROMPT_MASTER_AUT_PANEL_GITHUB_CODEX_V1.md
2. context/AUT_PANEL_CONTEXT_MANIFEST_V1.yaml
3. datacenter/AUT_PANEL_NORMATIVE_REFERENCES.yaml
4. datacenter/AUT_PANEL_NORMATIVE_SUPPLEMENT_2026.yaml
5. datacenter/LI_MATERIAL_CONTROL.json
6. configs/layout_optimizer_v1.yaml

## Authority
Repository canonical files and approved technical evidence override chat memory.
Conflict or missing evidence => HOLD.

## Locked behavior
- Do not rewrite approved baselines in place.
- Do not mutate historical LI revisions.
- Do not alter frozen R02 quantities without explicit approved revision/evidence.
- Do not auto-change enclosure size.
- Do not auto-select panel split.
- Do not let ML override deterministic gates.
- Do not auto-merge PR #23.

## Codex execution contract
Every substantive change must report:
- files changed;
- canonical inputs and SHAs;
- tests run and results;
- engineering HOLDs;
- regressions/risks;
- rollback path.

CI green is not engineering approval.

## Routing
Known intent -> deterministic router.
Ambiguous intent -> ML_ROUTE_HINT only.
Conflict -> deterministic rules win.

## Release
RELEASE is allowed only after required deterministic gates, source validation, normative reverification, QA and human approval.
