# AUT Panel Agent System V1

## Objective

Add a governed agent, database, memory, machine-learning and controlled-evolution layer without weakening the existing engineering pipeline or approved panel standards.

## Architecture

The canonical engineering flow remains authoritative:

`BOOTSTRAP -> DATACENTER -> DATASHEET -> SELECT -> LI_QUANTITY -> LOAD_BALANCE -> BOM -> LAYOUT -> RENDER_IMAGE -> QA -> MEMORY_SYNC -> RELEASE`

The learning loop is separate:

`OBSERVE -> FEATURE_EXTRACT -> TRAIN -> EVALUATE -> PROPOSE -> SANDBOX_SIMULATE -> HUMAN_GATE -> APPLY -> VERSION`

Machine learning ranks risk and improvement opportunities. It does not create engineering facts, approve missing evidence, replace manufacturer documentation, or bypass deterministic QA.

## Agents

The registry `agents/AUT_PANEL_AGENT_SYSTEM.yaml` defines fourteen agents with isolated Data Center and memory namespaces. Source validation is intentionally split into Validator A and Validator B.

## Database

`database/aut_panel_schema.sql` defines the local SQLite baseline. The schema covers panels, component catalog, references, suppliers, I/O, agent runs, memory events, QA, render metrics, training data, models, improvement proposals, plugins, skills and artifacts.

SQLite is the offline baseline. PostgreSQL/Supabase may later be used as deployment targets while keeping the logical schema.

## Controlled autoevolution

`pipeline/evolution_engine.py` only creates proposals. A proposal records the problem, evidence, affected files, expected benefit, risk, tests, rollback plan and confidence.

If a proposal touches Golden Rules, Data Center, Data Sheet, LI, templates, prompts, conversation memory, or the canonical pipeline, human approval is mandatory and automatic application is disabled.

## ML cold start

The project starts in `LEARNING_COLD_START`. At least 25 human-reviewed examples are required before the online model is allowed to enter trained advisory mode.

The deterministic baseline remains active even after ML training.

## Image quality

The preferred improvement chain is deterministic:

1. validated BOM and dimensions;
2. constraint-based placement;
3. vector drawing;
4. rasterization;
5. OpenCV/Pillow visual QA;
6. comparison with approved template.

Generative images remain supplemental and cannot become the engineering authority.

## Open source

`plugins/aut_panel_open_source_registry.json` records discovered repositories. Discovery alone does not activate a dependency. Every dependency requires version/commit pinning, license review, security review and controlled integration tests.
