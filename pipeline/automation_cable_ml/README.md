# Automation Cable ML Pipeline

## Objective
Build a traceable engineering assistant for automation/instrumentation cable calculations.

## Architecture
```
project data / datasheets / approved calculations
        |
        v
normalization + source trace
        |
        +--> deterministic engineering engine --> compliance result
        |
        +--> feature store --> ML recommendation / anomaly detection
                                  |
                                  v
                         engineer review gate
                                  |
                                  v
                         approved training record
```

## Phase 1 - rules first
Implement calculators for:
- 24 Vdc voltage drop and terminal-voltage budget.
- 4-20 mA loop resistance / voltage budget.
- RTD lead-wire configuration checks.
- Thermocouple extension/compensation cable compatibility.
- RS-485/Modbus physical-layer constraints.
- CAN/CANopen physical-layer constraints.
- Profibus cable family and segment constraints.
- Industrial Ethernet cable category, shielding and environment checks.

## Phase 2 - dataset
Each approved calculation becomes one immutable training record. Required labels:
- selected cable family;
- selected section;
- shielding;
- number of pairs/cores;
- approval result;
- rejection reason when not approved.

## Phase 3 - model
Start with interpretable tabular models:
1. Gradient boosted trees or Random Forest for cable-family recommendation.
2. Isolation Forest for anomaly detection.
3. Only after enough validated history, consider ranking models for approved alternatives.

## Guardrails
- Model cannot bypass deterministic rule failures.
- Unknown manufacturer data must remain unknown.
- Every output records model version, rule version and source references.
- Human engineering approval remains mandatory for production documents.

## Data split
Split by project, not random rows, to reduce leakage from repeated cable types inside the same project.

## Metrics
- Top-1 and Top-3 recommendation accuracy.
- False-negative rate for noncompliant selections.
- Calibration of confidence.
- Agreement with final engineer-approved section/family.
- Drift by project type and protocol.
