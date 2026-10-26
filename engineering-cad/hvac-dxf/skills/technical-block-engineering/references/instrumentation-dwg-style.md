# Instrumentation DWG Style Reference

Use this reference when the user supplies a DWG/DXF that defines project instrumentation symbology.

## Precedence
For schematic/project instrumentation symbols, the user-supplied base drawing controls graphical convention. Manufacturer datasheets control physical equipment geometry only.

## Base-drawing intake
1. Identify DWG/DXF version.
2. Extract text styles, block names, layer names, ByLayer/ByBlock usage, linetypes and color table when a native CAD reader is available.
3. Preserve confirmed names exactly.
4. If the runtime cannot read a DWG layer table, do not invent colors. Mark color mapping pending/provisional and keep entities BYLAYER.
5. Record base file name/revision.

## Current project evidence from INDICAÇÕES INSTRUMENTAÇÃO-R1.dwg
Confirmed by direct inspection:
- AC1032 DWG;
- metadata includes AutoCAD 2026 and GstarCAD/ODA;
- Arial references;
- ByLayer references;
- names recovered: G-SYM--5, G-SYM02, GSM-I-01, GSM-I, G-SYM-015A, DIM01, DT-AP, NIVEL B.

Color indices were not natively recoverable in the current runtime. Any ACI mapping remains provisional until a native DWG layer table is read.

## Level rule
- LSH: high marker above symbol + LSH tag.
- LSL: low marker below symbol + LSL tag.
- Do not make the symbols identical.
- Preserve project layer/color convention from the base drawing.

## PIT / TTU
- Pressure indicating transmitter: PIT when project convention supports it.
- Combined temperature/humidity transmission: preserve TTU when explicitly requested; subtitle T / UR is project annotation, not manufacturer identity.
