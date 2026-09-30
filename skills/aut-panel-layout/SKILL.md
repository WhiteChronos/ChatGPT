---
name: aut-panel-layout
description: Create and validate the real-scale physical layout and enclosure selection for PN automation panels. Use after LI/BOM and electrical sizing are closed, to choose project-specific enclosure H/W/D, place DIN devices, ducts, terminals, UPS/batteries, cooling, door devices, and prove maintenance/cable capacity without distortion.
---

# AUT Panel Layout

Treat enclosure size as a project output.

## Workflow
1. Load frozen target LI/BOM and official component dimensions/clearances.
2. Place components in real millimetres on their correct mounting surfaces.
3. Reserve cable-entry, gland, bend-radius, duct, terminal, PE/shield, and maintenance zones.
4. Include door-depth interference, HMI rear envelope, UPS/battery service access, and cooling cutouts.
5. Apply the frozen physical reserve.
6. Calculate required useful H/W/D and select a real manufacturer enclosure only after capacity is proven.
7. Freeze enclosure and mounting-plate dimensions in the target Data Sheet.
8. If it does not fit, choose a larger enclosure or HOLD_LAYOUT_CAPACITY. Never shrink geometry.
9. Any frozen enclosure change invalidates render and QA.

MODEL 001 never supplies enclosure dimensions.
