---
name: aut-panel-automation-io
description: Engineer PLC, I/O, field-device, serial-bus, Ethernet, HVAC gateway, BMS, and command architectures for PN automation panels. Use when building or reviewing I/O matrices, HART loops, Modbus/PROFINET/BACnet links, gateway capacities, bus addressing, field-device counts, or HVAC integration topology.
---

# AUT Panel Automation & I/O

Build the automation architecture from signal and equipment inventories.

## Workflow
1. Count every field endpoint and classify AI/DI/DO/AO/serial/network/IR/proprietary-bus.
2. Map each endpoint to a physical or logical controller interface.
3. Validate module channel capacity and reserve.
4. For gateways, distinguish: physical connectors, bus masters, logical addresses, maximum devices per bus, maximum systems, maximum indoor/outdoor units, and protocol limits.
5. Create a topology table: controller -> interface -> bus/network -> gateway -> endpoint count -> capacity -> utilization -> reserve.
6. Build the I/O matrix and communication matrix from the same inventory.
7. Reconcile HVAC equipment counts with gateway capacity. If capacity is exceeded, redesign before BOM/layout.
8. Do not count condensers as IR-addressed indoor units unless manufacturer topology proves that architecture.
9. Freeze communication architecture before render.

## Capacity rule
Required masters = CEILING(addressed endpoints / verified endpoints-per-master), adjusted for topology-specific constraints. Use only manufacturer-verified capacities.
