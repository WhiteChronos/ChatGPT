# Regression test

The bundled projection script was tested on a compound STEP model containing a rounded housing, cylindrical boss, probe, and side gland.

Expected and observed:
- FRONT, LEFT, RIGHT, TOP, BOTTOM, ISO generated;
- MULTIVIEW generated;
- no layout collisions;
- all generated DXFs audit with zero structural errors;
- ISO uses OpenCascade hidden-line removal from the same 3D master.


## Canonical R9 regression set
The current baseline is stored at `engineering-cad/hvac-dxf/baselines/R9/`.

Required baseline models:
- EICOS_LA32N2_40
- ROSEMOUNT_3051T
- EE_EE300EX_M1_T1
- VAISALA_HMT370EX_HMP374

Acceptance:
- X/Y/Z projected axes = 30/150/90 degrees;
- true-length projected axis scale = 1.0;
- no layout collisions;
- zero DXF structural audit errors;
- no arbitrary camera roll.
