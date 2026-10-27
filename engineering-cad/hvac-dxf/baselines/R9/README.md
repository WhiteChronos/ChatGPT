# R9 Isometric DXF Baseline

## Status
R9 is the canonical regression baseline for the current isometric-DXF workflow.

## Canonical geometry
- AutoCAD-style true-length isometric drawing.
- +X axis = 30 degrees.
- +Z axis = 90 degrees vertical.
- +Y axis = 150 degrees.
- True-length projected axis scale = 1.0.
- Fixed projector frame: normal (-1,-1,+1), in-plane XDirection (+1,-1,0).
- No arbitrary camera roll or post-projection visual rotation.

## R9 validation set
- EICOS LA32N2-40
- Rosemount 3051T
- E+E EE300Ex-M1 T1
- Vaisala HMT370EX/HMP374

All four local R9 validations recorded:
- axis QA: PASS;
- layout collisions: 0;
- DXF structural audit errors: 0;
- iso scale mode: true_length.

## Artifact provenance
Local artifact SHA-256 values at the time this baseline was recorded:
- DXF_INSTRUMENTOS_3D_R9_FIXED.zip: `e2c96026831ae4bd30e3a97d1490239b399b6dba6a91e0f27495c2c088dd8a3c`
- QA_FINAL_R9.json: `3ad83a27ac66118d2b002623ad3699e18833c66d116b5a2ac0ca9c6989996f7e`
- isometric-dxf-engineering skill.zip: `f2e28dea9ee4318909f1ab4a225ffcbdfeeab56641c77a6b4fd2433ae618596e`
- technical-block-engineering skill.zip: `c05d6181c9a8f347ce9ada79dc63959259fd252110b790fe88373457aa59a5cc`

The ZIP/DXF binary package is not stored in this GitHub text baseline. The canonical source of truth in the repository is the generator, workflow, standards, and QA record.

## Regression rule
Any future change to the isometric projector, HLR selection, true-length scaling, isoplane handling, layout, or DXF export must be tested against this baseline or an explicitly superseding baseline. A regression is present if:
- X/Y/Z projected axes deviate from 30/150/90 degrees beyond configured tolerance;
- true-length axis scale deviates from 1.0;
- any of the four baseline models gains layout collisions or DXF audit errors;
- the view changes because of arbitrary camera roll;
- circles/conics no longer follow the intended isoplane projection.

## Supersession
A future baseline may replace R9 only with:
1. documented reason;
2. comparison against R9;
3. regression evidence;
4. workflow and skill updates;
5. human review for any change to the canonical isometric convention.
