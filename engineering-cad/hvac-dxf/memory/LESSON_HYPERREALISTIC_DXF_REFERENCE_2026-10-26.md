# Lesson — Hyper-realistic DXF reference — 2026-10-26

## Failure
Earlier generated instrument DXFs used simplified boxes/prisms and did not resemble the manufacturer object.

## User correction
The supplied DXFs 3D135205A0, 3D135206A0 and FXAQ20~63AVM are the required visual/detail standard.

## Root cause
The workflow validated file structure and dimensions but did not enforce geometric fidelity/density against a real manufacturer CAD reference.

## Improvement
- add hyper-realistic DXF standard;
- require all available orthographic views + ISO;
- preserve curve/detail entities;
- prohibit generic envelopes as final object blocks;
- separate real object from schematic symbol;
- add CAD toolchain for native CAD/STEP/DWG workflows;
- use reference DXFs as regression benchmarks.

## Regression gate
A future instrument block must not be approved if it visually collapses to a generic enclosure when the manufacturer source exposes more detail.
