from __future__ import annotations

import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator
from pipeline.aut_panel_electrical_sizing import evaluate_document, evaluate_panel

ROOT = Path(__file__).resolve().parents[1]


def load_inputs():
    return json.loads((ROOT / "datasheet/AUT_PANEL_ELECTRICAL_SIZING_INPUTS.json").read_text(encoding="utf-8"))


def test_sizing_inputs_match_schema():
    schema = json.loads((ROOT / "schemas/aut_panel_electrical_sizing_v1.schema.json").read_text(encoding="utf-8"))
    errors = list(Draft202012Validator(schema).iter_errors(load_inputs()))
    assert not errors, [e.message for e in errors]


def test_current_baseline_fails_closed_and_does_not_invent_panel_amps():
    result = evaluate_document(load_inputs())
    assert result["status"] == "HOLD"
    for panel in result["results"].values():
        assert panel["status"] == "HOLD"
        assert panel["a_do_quadro_a"] is None
        codes = {x["code"] for x in panel["holds"]}
        assert "HOLD_ASSEMBLY_INA" in codes
        assert "HOLD_SITE_SUPPLY_VOLTAGE_V" in codes
        assert "HOLD_SITE_PROSPECTIVE_SHORT_CIRCUIT_KA" in codes


def test_dc_known_loads_are_summed_but_unknown_loads_keep_hold():
    result = evaluate_panel("PN-AUT-01", load_inputs()["panels"]["PN-AUT-01"])
    dc = result["calculated"]["dc_bus"]
    assert dc["continuous_power_w"] > 0
    assert "PLC-01" in dc["unresolved_loads"]
    assert any(x["code"] == "HOLD_DC_LOAD_DATA" for x in result["holds"])


def test_a_do_quadro_is_only_emitted_after_all_release_checks_pass():
    panel = copy.deepcopy(load_inputs()["panels"]["PN-AUT-01"])
    panel["site"].update({
        "supply_voltage_v": 220,
        "phases": 1,
        "frequency_hz": 60,
        "earthing_system": "TN-S",
        "prospective_short_circuit_ka": 6,
        "ambient_temperature_c": 35,
        "altitude_m": 50,
    })
    panel["ac_load_summary"] = {"demand_va": 1100, "design_current_a": None}
    for load in panel["dc_loads"]:
        if load.get("power_w") is None and load.get("current_a") is None:
            load["power_w"] = 1.0
    panel["battery"].update({
        "required_autonomy_h": 1,
        "max_depth_of_discharge": 0.8,
        "aging_factor": 1.25,
        "temperature_factor": 1.0,
    })
    panel["protection"].update({
        "incoming_breaker_in_a": 10,
        "incoming_conductor_iz_a": 15,
        "incoming_breaker_icu_ka": 10,
        "assembly_rated_current_ina_a": 10,
        "assembly_icw_ka_1s": 6,
        "assembly_ipk_ka": 12,
        "incoming_protection_verified": True,
        "conductor_ampacity_verified": True,
        "voltage_drop_verified": True,
        "short_circuit_withstand_verified": True,
        "selectivity_or_backup_verified": True,
    })
    panel["verification"].update({
        "thermal_rise_verified": True,
        "protective_bonding_verified": True,
    })
    for item in panel["thermal"]["component_losses"]:
        if item.get("loss_w") is None:
            item["loss_w"] = 1.0
    result = evaluate_panel("PN-AUT-01", panel)
    assert result["status"] == "PASS"
    assert result["a_do_quadro_a"] == 10
    assert result["calculated"]["ib_a"] == 5.0


def test_rejects_in_below_ib_and_icu_below_ik():
    panel = copy.deepcopy(load_inputs()["panels"]["PN-AUT-01"])
    panel["site"].update({
        "supply_voltage_v": 220,
        "phases": 1,
        "frequency_hz": 60,
        "earthing_system": "TN-S",
        "prospective_short_circuit_ka": 10,
        "ambient_temperature_c": 35,
        "altitude_m": 50,
    })
    panel["ac_load_summary"] = {"design_current_a": 12, "demand_va": None}
    panel["protection"].update({
        "incoming_breaker_in_a": 10,
        "incoming_conductor_iz_a": 16,
        "incoming_breaker_icu_ka": 6,
        "assembly_rated_current_ina_a": 16,
    })
    result = evaluate_panel("PN-AUT-01", panel)
    codes = {x["code"] for x in result["holds"]}
    assert "HOLD_IN_LT_IB" in codes
    assert "HOLD_ICU_LT_IK" in codes


def test_pipeline_load_balance_is_wired_to_electrical_sizing_engine():
    import yaml
    pipeline = yaml.safe_load((ROOT / "pipeline/pipeline.yaml").read_text(encoding="utf-8"))
    stage = next(x for x in pipeline["sequence"] if x["id"] == "LOAD_BALANCE")
    assert stage["implementation"] == "pipeline/aut_panel_electrical_sizing.py"
    assert stage["inputs"] == "datasheet/AUT_PANEL_ELECTRICAL_SIZING_INPUTS.json"
    required = set(stage["gate"])
    assert {
        "prospective_short_circuit_current_known",
        "ib_le_in_le_iz_verified",
        "breaker_icu_not_less_than_ik",
        "assembly_ina_verified",
        "temperature_rise_verified",
        "battery_autonomy_and_capacity_verified",
    } <= required
