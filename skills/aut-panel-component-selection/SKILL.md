---
name: aut-panel-component-selection
description: Select exact automation-panel components from validated requirements and manufacturer evidence. Use for PLC CPUs, I/O modules, gateways, switches, power supplies, UPS/batteries, breakers, SPDs, terminals, enclosures, cooling, transmitters, and equivalent substitutions that must satisfy electrical, communication, dimensional, lifecycle, and reserve constraints.
---

# AUT Panel Component Selection

Select exact models only after requirements and evidence are explicit.

## Workflow
1. Load target requirements, I/O, loads, communication topology, ambient conditions, IP requirement, reserve policy, and official evidence.
2. Build a requirement-to-candidate matrix.
3. Validate voltage, current/power, protocol, device capacity, channel count, lifecycle, environmental rating, physical dimensions, mounting, and accessories.
4. Check the entire accessory chain: base units, adapters, bus couplers, memory cards, connectors, power modules, batteries, terminals, and cables.
5. Check capacity numerically. Never confuse one gateway with sufficient addressed-device capacity.
6. Prefer manufacturer-native integration when it provides verified compatibility and adequate capacity.
7. Freeze the exact catalog number only when the evidence supports it. Otherwise keep REFERENCE/HOLD.
8. Any model change invalidates affected load, layout, render, and QA.

## Equivalents
An equivalent must meet or exceed every mandatory project property. Do not accept visual similarity or marketing language as equivalence.
