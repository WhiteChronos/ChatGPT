from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum
from typing import Any, Mapping


class LayoutStatus(str, Enum):
    LAYOUT_FEASIBLE = "LAYOUT_FEASIBLE"
    LAYOUT_VALIDATED = "LAYOUT_VALIDATED"
    HOLD_LAYOUT_INPUT = "HOLD_LAYOUT_INPUT"
    HOLD_LAYOUT_CAPACITY = "HOLD_LAYOUT_CAPACITY"
    HOLD_LAYOUT_SOLVER_TIMEOUT = "HOLD_LAYOUT_SOLVER_TIMEOUT"
    HOLD_LAYOUT_THERMAL = "HOLD_LAYOUT_THERMAL"
    HOLD_LAYOUT_EMC = "HOLD_LAYOUT_EMC"
    HOLD_LAYOUT_CABLE_ENTRY = "HOLD_LAYOUT_CABLE_ENTRY"
    USER_DECISION_REQUIRED = "USER_DECISION_REQUIRED"


@dataclass(frozen=True)
class RectMM:
    x: float
    y: float
    width: float
    height: float

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def top(self) -> float:
        return self.y + self.height

    @property
    def area_mm2(self) -> float:
        return self.width * self.height


@dataclass(frozen=True)
class ClearanceMM:
    left: float = 0.0
    right: float = 0.0
    top: float = 0.0
    bottom: float = 0.0


@dataclass(frozen=True)
class PhysicalInstance:
    instance_id: str
    source_tag: str
    catalog_id: str
    quantity_index: int
    surface: str
    width_mm: float
    height_mm: float
    depth_mm: float
    clearance: ClearanceMM = field(default_factory=ClearanceMM)
    allowed_orientations: tuple[int, ...] = (0,)
    functional_group: str | None = None
    rail_required: bool = False
    heat_loss_w: float | None = None
    connections: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def dimensions_for_rotation(self, rotation_deg: int) -> tuple[float, float]:
        if rotation_deg not in self.allowed_orientations:
            raise ValueError(f"{self.instance_id}: rotation {rotation_deg} is not allowed")
        if rotation_deg % 180 == 90:
            return self.height_mm, self.width_mm
        return self.width_mm, self.height_mm


@dataclass(frozen=True)
class PanelGeometry:
    panel_id: str
    revision: str
    enclosure_width_mm: float
    enclosure_height_mm: float
    enclosure_depth_mm: float
    plate_width_mm: float
    plate_height_mm: float
    minimum_free_reserve_percent: float = 0.0
    cable_exit_height_mm: float = 0.0
    lower_wireway_height_mm: float = 0.0
    minimum_bend_clearance_mm: float = 0.0
    terminal_zone_bottom_y_mm: float = 0.0
    cable_glands_count: int = 0

    @property
    def plate_rect(self) -> RectMM:
        return RectMM(0.0, 0.0, self.plate_width_mm, self.plate_height_mm)

    @property
    def door_rect(self) -> RectMM:
        return RectMM(0.0, 0.0, self.enclosure_width_mm, self.enclosure_height_mm)


@dataclass(frozen=True)
class LayoutConfig:
    solver_seed: int = 17
    max_time_seconds: float = 10.0
    coordinate_resolution_mm: float = 1.0
    objective_weights: Mapping[str, int] = field(default_factory=lambda: {
        "occupied_envelope": 100,
        "connection_distance": 10,
        "bottom_zone_margin": 1,
    })
    rail_edge_allowance_mm: float = 10.0
    infrastructure_gap_mm: float = 5.0


@dataclass(frozen=True)
class Placement:
    instance_id: str
    source_tag: str
    catalog_id: str
    surface: str
    x_mm: float
    y_mm: float
    width_mm: float
    height_mm: float
    rotation_deg: int = 0
    kind: str = "component"
    quantity_index: int = 1
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def rect(self) -> RectMM:
        return RectMM(self.x_mm, self.y_mm, self.width_mm, self.height_mm)


@dataclass(frozen=True)
class LayoutMetrics:
    occupied_area_mm2: float
    free_reserve_percent: float
    minimum_clearance_mm: float | None
    overlap_count: int
    rail_count: int
    wireway_count: int
    terminal_count: int
    gland_count: int
    occupied_envelope_area_mm2: float = 0.0
    routing_complexity: float = 0.0


@dataclass(frozen=True)
class CapacityAlternative:
    alternative_id: str
    alternative_type: str
    status: LayoutStatus
    panels: tuple[Mapping[str, Any], ...] = ()
    metrics: Mapping[str, Any] = field(default_factory=dict)
    impacts: Mapping[str, Any] = field(default_factory=dict)
    diagnostics: tuple[str, ...] = ()
    requires_user_decision: bool = True


def _jsonable(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {k: _jsonable(v) for k, v in asdict(value).items()}
    if isinstance(value, Mapping):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, tuple):
        return [_jsonable(v) for v in value]
    if isinstance(value, list):
        return [_jsonable(v) for v in value]
    return value


@dataclass(frozen=True)
class LayoutResult:
    panel_id: str
    panel_revision: str
    status: LayoutStatus
    placements: tuple[Placement, ...]
    metrics: LayoutMetrics
    solver_manifest: Mapping[str, Any]
    diagnostics: tuple[str, ...] = ()
    alternatives: tuple[CapacityAlternative, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "panel_id": self.panel_id,
            "panel_revision": self.panel_revision,
            "status": self.status.value,
            "placements": [_jsonable(x) for x in self.placements],
            "metrics": _jsonable(self.metrics),
            "solver_manifest": _jsonable(self.solver_manifest),
            "diagnostics": list(self.diagnostics),
            "alternatives": [_jsonable(x) for x in self.alternatives],
        }
