# QA Policy

Final geometry gates:
1. exact object identity confirmed;
2. official source and drawing/datasheet number recorded;
3. source unit and numeric conversion validated;
4. DXF extents checked against official dimensions;
5. mounting and connection interfaces checked when available;
6. no unresolved DXF audit errors;
7. visual comparison against official dimensional drawing/native CAD;
8. project-vs-manufacturer conflicts documented;
9. provenance manifest complete;
10. reusable rule changes regression-tested against failing and known-good cases.


## Supplier/source authority gates
For `CAD_FABRICANTE` or `RECONSTRUCAO_FICHA`:
11. supplier authority verified from the manufacturer's own official domain/locator;
12. supplier relationship is `MANUFACTURER`, `AUTHORIZED_DISTRIBUTOR`, or `AUTHORIZED_PARTNER`;
13. official verification URL, region and checked date recorded in the manifest;
14. `RESELLER`, `UNKNOWN`, marketplace, or self-declared distributor sources are blocked from final geometry;
15. when no authorized channel can be verified, use manufacturer-direct technical sources only.

## Filename/package gates
Before publishing a DXF package:
16. every DXF filename passes `scripts/validate_dxf_filename.py`;
17. filename identifies instrument/equipment type, manufacturer, exact model, artifact/view and revision;
18. symbol filenames include the real symbol code;
19. no generic/model-only filenames remain;
20. descriptive CSV and TXT indexes are present and consistent with the files in the package.
