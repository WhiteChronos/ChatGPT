# Deterministic Quantity Rules

## Internal wiring
For each wire/net segment:
L_cut_mm = L_route_mm + L_origin_term_mm + L_destination_term_mm + L_service_loop_mm
L_procurement_mm = L_cut_mm * (1 + manufacturing_allowance)

manufacturing_allowance must be an explicit project/manufacturing parameter. Do not invent a hidden percentage.

Aggregate only wires with the same controlled procurement identity.

## Routed path
Prefer measured orthogonal path along approved duct/route graph. Do not use straight-line Euclidean distance when the wire is routed through ducts.
Door wiring must include the approved flexible/service loop.

## DIN rail
Sum actual cut segments from layout. Add procurement allowance only if explicitly parameterized. Include end brackets/stops separately.

## Cable duct
Sum each installed duct body length and matching cover length. Include fittings when used. Validate fill using conductor bundle cross-sectional area and manufacturer/normative fill rules.

## Terminals
Derive from connection topology and field/interface requirements. Count PE/shield terminals separately. Include bridges, jumpers, separators, end plates and markers.

## Ferrules/lugs/markers
Derive from conductor endpoints and termination technology. Do not assume ferrules on terminals that prohibit or do not require them.

## Cable glands
Derive from cable-entry schedule and outside diameter ranges.

## Fasteners/mounting kits
Use manufacturer accessory requirements first. For custom mounting, derive screw/nut/washer/spacer quantities from actual mounting points.

## Panel volume/area checks
Volume and area calculations support enclosure/layout validation; they do not replace collision/clearance checks.

## Electrical load
Use official current or power at actual supply voltage. Apply diversity only when documented. Add project reserve exactly once.
