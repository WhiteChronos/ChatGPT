# Engineering Source Governance v1.0

## Status
MANDATORY / BLOCK_ON_FAILURE

## Canonical registry
The machine-readable source inventory is `datacenter/ENGINEERING_REFERENCE_REGISTRY.json`.

## Authority hierarchy
1. Approved project source controls project-specific facts and design decisions.
2. Official standards/specifications control external normative requirements within their applicable scope.
3. Official guidance supports interpretation where it does not conflict with project requirements or applicable standards.
4. Open-source repositories are supporting implementation/test references only.

## Mandatory rules
- Never use a GitHub repository as normative engineering authority.
- Never use a public repository as evidence that a project drawing, list, datasheet or philosophy contains a fact.
- Every `EXTERNAL_KNOWLEDGE` finding claim must identify at least one registered authoritative source ID.
- Datasheet reference IDs must resolve against the canonical registry.
- Project evidence retains its own document/revision/location/SHA-256 provenance and is never replaced by an external standard citation.
- Standards with restricted copyright remain metadata-only in this public repository. Licensed text is not copied into repository memory or generated datasheets.
- ISA standard content must not be entered into AI tooling without express ISA permission; retain only public bibliographic metadata and official links here.
- Adoption of an open-source implementation requires license, maintenance, cybersecurity, protocol/version and project-fit review plus regression tests.

## Current registered domains
- PLC programming: IEC 61131-3:2025.
- instrumentation identification: ANSI/ISA-5.1-2024.
- HMI: ISA-101.01-2015.
- alarm management: ANSI/ISA-18.2-2016.
- functional safety/SIS: IEC 61511-1:2016+AMD1:2017.
- IACS cybersecurity governance: IEC 62443-2-1:2024.
- OT cybersecurity guidance: NIST SP 800-82 Rev. 3 (final; Rev. 4 is draft as of 2026-09-25).
- OPC UA: OPC Foundation Unified Architecture specification.
- Modbus: MODBUS Application Protocol V1.1b3.
- BACnet: ANSI/ASHRAE 135-2024, including applicable published addenda/errata.
- repository data contracts: JSON Schema Draft 2020-12.

## Release invariant
A package cannot PASS if it references an unknown source/repository ID, uses an undeclared authoritative source, uses external-knowledge claims without an authoritative reference, or fails the canonical Hyperfocus stage inventory.
