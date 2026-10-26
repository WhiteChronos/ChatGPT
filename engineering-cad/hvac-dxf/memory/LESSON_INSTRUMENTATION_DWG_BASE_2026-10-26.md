# Lesson — Instrumentation DWG Base — 2026-10-26

## Trigger
User supplied `INDICAÇÕES INSTRUMENTAÇÃO-R1.dwg` and reported that high/low level symbols were identical and that layers/colors must follow the project base drawing.

## Verified evidence
Direct inspection of the AC1032 DWG recovered:
- Arial references;
- ByLayer behavior;
- names: G-SYM--5, G-SYM02, GSM-I-01, GSM-I, G-SYM-015A, DIM01, DT-AP, NIVEL B;
- metadata referencing AutoCAD 2026 and GstarCAD/ODA.

The current runtime does not expose a native AC1032 layer-table reader, so exact layer color indices were not verified.

## Correction
- Added project instrumentation-symbol mode to technical-block-engineering.
- LSH and LSL must differ graphically as well as by tag.
- Base DWG controls schematic symbol layers/colors/text convention.
- Manufacturer sources remain authoritative for physical equipment geometry.
- Unverified colors must be marked provisional/pending; entities remain BYLAYER for central correction.

## Regression cases
- LSH: high marker above symbol.
- LSL: low marker below symbol.
- PIT: distinct instrumentation layer.
- TTU: preserve project tag and temperature/relative-humidity meaning.
