# Automation Cable Engineering Memory

## Scope
This memory is exclusively for automation and instrumentation cables. It must not reuse power-cable sizing logic as the primary decision model.

## Governing design principle
1. Deterministic engineering rules and manufacturer limits are authoritative.
2. Machine learning is advisory: recommendation, anomaly detection, similarity retrieval, and prioritization.
3. Every generated calculation must preserve source traceability and revision history.
4. A cable recommendation is not accepted until all applicable engineering checks pass.

## Cable classes
- Analog instrumentation: 4-20 mA, 0-10 V.
- Digital I/O: 24 Vdc DI/DO.
- Low-power 24 Vdc field supply.
- Temperature: RTD and thermocouple.
- Pulse, frequency, encoder and high-speed discrete signals.
- Serial fieldbus: RS-485/Modbus RTU, CAN/CANopen, Profibus.
- Industrial Ethernet.
- Functional safety signals.

## Calculation logic
For copper DC circuits, the baseline conductor loop resistance estimate is:

R_loop = 2 * L * rho / S

and:

DeltaV = I * R_loop

where L is one-way length, rho is conductor resistivity corrected for temperature when required, and S is conductor cross-sectional area.

For 4-20 mA loops, verify the available voltage budget across cable resistance plus all series devices. For communication cables, protocol-specific impedance, capacitance, shielding, topology, termination, baud rate, and maximum segment length take precedence over generic ampacity logic.

## ML policy
The first production model should be supervised classification/ranking trained only from engineer-reviewed and approved historical records. Suggested baseline: gradient-boosted trees or random forest because their feature importance and decision paths are inspectable. Add anomaly detection separately to flag selections that differ materially from approved historical patterns.

## Required features
Signal/protocol, voltage/current, route length, cable resistance/capacitance, conductor section, shielding, pair count, EMC environment, installation method, ambient temperature, hazardous-area requirement, manufacturer/family, project class, and approval state.

## Required output
The system shall return the deterministic calculation, ML recommendation, confidence, detected anomalies, applicable rule checks, and source trace. The ML output must never silently alter the engineering result.

## Initial external references
- IEC 61158 / IEC 61784 family for industrial fieldbus concepts and profiles.
- IEC 60228 for conductor resistance and standardized conductor construction where applicable.
- Manufacturer datasheets for electrical parameters and protocol-qualified cable families.

## Learning loop
Only engineer-approved final selections become training labels. Rejected designs remain available as negative examples, with the rejection reason preserved.
