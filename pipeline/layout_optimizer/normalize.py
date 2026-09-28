from __future__ import annotations

from typing import Any, Mapping, Sequence

from .models import ClearanceMM, LayoutConfig, PanelGeometry, PhysicalInstance


INFRASTRUCTURE_CATEGORIES = {
    "din_rail": "din_rail",
    "wireway": "wireway",
    "cable_gland": "cable_gland",
}
INFRASTRUCTURE_TAG_PREFIXES = {
    "DIN-": "din_rail",
    "WD-": "wireway",
    "CG-": "cable_gland",
}


def _catalog_index(catalog: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {
        str(item.get("catalog_id")): item
        for item in catalog.get("components", [])
        if item.get("catalog_id")
    }


def _line_tag(line: Mapping[str, Any]) -> str:
    return str(line.get("tag") or line.get("li_tag") or "")


def _assert_li_bom_parity(li: Mapping[str, Any], bom: Mapping[str, Any]) -> None:
    li_map = {
        _line_tag(line): (
            str(line.get("catalog_id") or ""),
            line.get("quantity"),
            str(line.get("unit") or ""),
        )
        for line in li.get("lines", [])
    }
    bom_map = {
        _line_tag(line): (
            str(line.get("catalog_id") or ""),
            line.get("quantity"),
            str(line.get("unit") or ""),
        )
        for line in bom.get("lines", [])
    }
    if li_map != bom_map:
        missing = sorted(set(li_map) - set(bom_map))
        extra = sorted(set(bom_map) - set(li_map))
        mismatched = sorted(
            tag for tag in set(li_map) & set(bom_map) if li_map[tag] != bom_map[tag]
        )
        raise ValueError(
            "LI_BOM_PARITY: "
            f"missing={missing}; extra={extra}; mismatched={mismatched}"
        )


def classify_line_kind(
    line: Mapping[str, Any],
    catalog_item: Mapping[str, Any] | None,
) -> str:
    category = str((catalog_item or {}).get("category") or "")
    if category in INFRASTRUCTURE_CATEGORIES:
        return INFRASTRUCTURE_CATEGORIES[category]
    tag = _line_tag(line)
    for prefix, kind in INFRASTRUCTURE_TAG_PREFIXES.items():
        if tag.startswith(prefix):
            return kind
    return "component"


def extract_infrastructure_requests(
    li: Mapping[str, Any],
    bom: Mapping[str, Any],
    catalog: Mapping[str, Any],
) -> list[dict[str, Any]]:
    _assert_li_bom_parity(li, bom)
    index = _catalog_index(catalog)
    requests: list[dict[str, Any]] = []
    for line in li.get("lines", []):
        cid = str(line.get("catalog_id") or "")
        kind = classify_line_kind(line, index.get(cid))
        if kind == "component":
            continue
        requests.append(
            {
                "kind": kind,
                "source_tag": _line_tag(line),
                "catalog_id": cid,
                "quantity": int(line.get("quantity") or 0),
                "unit": str(line.get("unit") or ""),
            }
        )
    return requests


def _positive_dimension(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0


def _surface_for(item: Mapping[str, Any], line: Mapping[str, Any]) -> str:
    explicit = line.get("surface") or item.get("surface")
    if explicit:
        return str(explicit)
    if str(item.get("category") or "") == "hmi" or _line_tag(line).startswith("HMI-"):
        return "door"
    return "mounting_plate"


def _allowed_orientations(item: Mapping[str, Any]) -> tuple[int, ...]:
    raw = item.get("allowed_orientations_deg")
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
        return (0,)
    values = tuple(int(v) for v in raw if int(v) in {0, 90, 180, 270})
    return values or (0,)


def _clearance(item: Mapping[str, Any]) -> ClearanceMM:
    raw = item.get("clearance_mm") or {}
    return ClearanceMM(
        left=float(raw.get("left", 0) or 0),
        right=float(raw.get("right", 0) or 0),
        top=float(raw.get("top", 0) or 0),
        bottom=float(raw.get("bottom", 0) or 0),
    )


def _panel_geometry(panel_id: str, project: Mapping[str, Any]) -> PanelGeometry:
    project_meta = project.get("project") or {}
    project_id = str(project_meta.get("id") or panel_id)
    if project_id != panel_id:
        raise ValueError(f"PANEL_ID_MISMATCH: expected={panel_id}; actual={project_id}")

    enclosure = project.get("enclosure") or {}
    external = enclosure.get("external_mm") or {}
    plate = enclosure.get("mounting_plate_mm") or {}
    required = {
        "enclosure.width": external.get("width"),
        "enclosure.height": external.get("height"),
        "enclosure.depth": external.get("depth"),
        "plate.width": plate.get("width"),
        "plate.height": plate.get("height"),
    }
    missing = [name for name, value in required.items() if not _positive_dimension(value)]
    if missing:
        raise ValueError(f"PANEL_GEOMETRY_INVALID: {missing}")

    bottom = ((project.get("layout") or {}).get("bottom_zone") or {})
    revision = str(project_meta.get("revision") or "")
    return PanelGeometry(
        panel_id=panel_id,
        revision=revision,
        enclosure_width_mm=float(external["width"]),
        enclosure_height_mm=float(external["height"]),
        enclosure_depth_mm=float(external["depth"]),
        plate_width_mm=float(plate["width"]),
        plate_height_mm=float(plate["height"]),
        minimum_free_reserve_percent=float(enclosure.get("minimum_free_reserve_percent", 0) or 0),
        cable_exit_height_mm=float(bottom.get("cable_exit_height_mm", 0) or 0),
        lower_wireway_height_mm=float(bottom.get("lower_wireway_height_mm", 0) or 0),
        minimum_bend_clearance_mm=float(bottom.get("minimum_bend_clearance_mm", 0) or 0),
        terminal_zone_bottom_y_mm=float(bottom.get("terminal_zone_bottom_y_mm", 0) or 0),
        cable_glands_count=int(bottom.get("cable_glands_count", 0) or 0),
    )


def normalize_inputs(
    panel_id: str,
    li: Mapping[str, Any],
    bom: Mapping[str, Any],
    catalog: Mapping[str, Any],
    project: Mapping[str, Any],
    config: LayoutConfig,
) -> tuple[PanelGeometry, list[PhysicalInstance], list[str]]:
    del config
    _assert_li_bom_parity(li, bom)

    if str(li.get("project_id") or "") != panel_id:
        raise ValueError(
            f"LI_PROJECT_MISMATCH: expected={panel_id}; actual={li.get('project_id')}"
        )
    if li.get("status") != "QUANTITY_FROZEN":
        raise ValueError(f"LI_NOT_FROZEN: {li.get('status')!r}")

    panel = _panel_geometry(panel_id, project)
    if str(li.get("revision") or "") != panel.revision:
        raise ValueError(
            f"REVISION_MISMATCH: li={li.get('revision')}; project={panel.revision}"
        )

    index = _catalog_index(catalog)
    diagnostics: list[str] = []
    diagnostic_seen: set[str] = set()
    instances: list[PhysicalInstance] = []

    for line in li.get("lines", []):
        if line.get("render_required") is not True:
            continue

        tag = _line_tag(line)
        cid = str(line.get("catalog_id") or "")
        item = index.get(cid)
        kind = classify_line_kind(line, item)
        if kind != "component":
            continue

        if item is None:
            diag = f"MISSING_CATALOG:{cid}"
            if diag not in diagnostic_seen:
                diagnostics.append(diag)
                diagnostic_seen.add(diag)
            continue

        dims = item.get("dimensions_mm")
        if not isinstance(dims, Mapping) or not all(
            _positive_dimension((dims or {}).get(k))
            for k in ("width", "height", "depth")
        ):
            diag = f"MISSING_DIMENSIONS:{cid}"
            if diag not in diagnostic_seen:
                diagnostics.append(diag)
                diagnostic_seen.add(diag)
            continue

        qty = line.get("quantity")
        if not isinstance(qty, int) or isinstance(qty, bool) or qty < 1:
            raise ValueError(f"INVALID_QUANTITY:{tag}:{qty!r}")

        surface = _surface_for(item, line)
        clearance = _clearance(item)
        allowed = _allowed_orientations(item)
        category = str(item.get("category") or "")
        rail_required = bool(item.get("rail_required", False))
        if "rail_required" not in item:
            rail_required = category not in {"battery", "hmi", "enclosure", "mounting_plate"}

        for quantity_index in range(1, qty + 1):
            instances.append(
                PhysicalInstance(
                    instance_id=f"{tag}#{quantity_index:02d}",
                    source_tag=tag,
                    catalog_id=cid,
                    quantity_index=quantity_index,
                    surface=surface,
                    width_mm=float(dims["width"]),
                    height_mm=float(dims["height"]),
                    depth_mm=float(dims["depth"]),
                    clearance=clearance,
                    allowed_orientations=allowed,
                    functional_group=str(item.get("functional_group") or category or "") or None,
                    rail_required=rail_required,
                    heat_loss_w=(
                        float(item["heat_loss_w"])
                        if _positive_dimension(item.get("heat_loss_w"))
                        else None
                    ),
                    connections=tuple(str(x) for x in item.get("connections", []) if x),
                    metadata={"category": category},
                )
            )

    return panel, instances, diagnostics
