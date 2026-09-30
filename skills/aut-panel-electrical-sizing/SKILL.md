---
name: aut-panel-electrical-sizing
description: Perform deterministic electrical sizing for PN automation panels, including AC feeder, 24 Vdc load, protection, UPS, batteries, voltage drop, thermal losses, enclosure current rating, and release checks. Use after exact component selection and before physical layout or Excel release.
---

# AUT Panel Electrical Sizing

Size from exact loads and documented conditions.

## Workflow
1. Load exact component consumption and field-loop loads.
2. Calculate 24 Vdc raw load and frozen reserve.
3. Check PSU/UPS continuous capacity and transient requirements.
4. Size battery for autonomy, aging, temperature, allowable DoD, and manufacturer discharge data.
5. Calculate AC design current, protection, conductor ampacity, voltage drop, and PE.
6. Verify breaker rating/curve and breaking capacity against available short-circuit evidence; do not equate Icu with installation Ik.
7. Sum internal heat losses and select thermal management.
8. Verify enclosure/assembly rating, IP constraints, bonding, and applicable Icw/Ipk/InA requirements.
9. Keep A DO QUADRO blocked until the complete sizing gate passes.

Use Wolfram or deterministic scripts for calculation support when available; calculations never replace missing manufacturer ratings.
