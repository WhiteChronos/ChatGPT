# Codex Compatibility Contract v1.0

## Objective
Make engineering-document compatibility analysis deterministic, auditable and safe for Codex-assisted repository changes.

## Authority order
When Codex operates in this repository, the order of authority is:

1. approved source documents for the project;
2. `governance/VISUALIZE_GOLDEN_RULE_v1_0.md`;
3. `AGENTS.md`;
4. `datacenter/ENGINEERING_COMPATIBILITY_CONFIG.json`;
5. `schemas/engineering_compatibility.schema.json`;
6. project datasheet;
7. pipeline validation output.

## Required Codex workflow

### 1. Ingest
- identify document number, revision, discipline, status and source hash;
- never mutate raw source records;
- preserve provenance.

### 2. Normalize
Create structured records for:
- documents;
- TAGs;
- equipment;
- electrical loads;
- I/O;
- protocols;
- interlocks;
- requirements;
- document references;
- findings.

### 3. Analyze
Apply the complete analysis stack:
`/factcheck -> /thenvsnow -> /comparison -> /deepdive -> /rootcause -> /fivewhys -> /audit -> /redteam -> /premortem -> /viability -> /actionplan -> /visualize`.

### 4. Separate fact from inference
Every result must clearly distinguish:
- source-derived fact;
- engineering inference;
- external/vendor knowledge;
- unresolved assumption.

### 5. Build finding records
Every actionable finding must contain:
- severity;
- classification;
- status;
- disciplines;
- evidence;
- comparison;
- problem;
- root cause;
- lifecycle impacts;
- solution;
- alternatives;
- viability;
- primary/secondary documents;
- proposed text when applicable;
- owner;
- dependency;
- closure criterion;
- confidence.

### 6. Calculate
- compatibility and coverage are separate;
- NOT_APPLICABLE is excluded from compatibility denominator;
- NOT_VERIFIABLE is excluded from compatibility denominator but lowers coverage;
- calculation method must be explicit;
- no percentage can be presented without denominator and coverage.

### 7. Visualize
Output must comply with the Golden Rule: complete, visually structured, color-coded by severity, but never shortened to the point of losing evidence, root cause, impact, solution or closure criteria.

### 8. Gate
Run:

```bash
python pipeline/engineering_compatibility_gate.py datasheet/projects/<project>/compatibility.json
```

Codex must not recommend merge while the gate returns BLOCK, unless a human reviewer explicitly waives the finding and records the waiver in the datasheet.

## Repository change rules
Codex must use a feature branch and pull request for changes that affect:
- schemas;
- compatibility calculation;
- release thresholds;
- severity logic;
- report-generation rules;
- Data Center configuration;
- Golden Rule content.

Direct changes to `main` are not the default path.

## Review checklist for Codex
Before requesting review:

- [ ] Golden Rule read and applied
- [ ] source evidence preserved
- [ ] no silent reconciliation
- [ ] every divergence has root cause or explicit NOT_VERIFIABLE root cause
- [ ] lifecycle impacts completed
- [ ] viability alternatives evaluated where architectural
- [ ] document to adjust identified
- [ ] closure criterion objective
- [ ] compatibility method disclosed
- [ ] coverage disclosed
- [ ] semantic gate executed
- [ ] PR explains engineering impact, not only code changes
