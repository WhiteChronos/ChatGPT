#!/usr/bin/env python3
"""Deterministic electrical-sizing gate for AUT automation panels.

The module calculates only what is supported by explicit project inputs and
traceable evidence. Missing site data or manufacturer data produces HOLD; the
module never guesses panel current, short-circuit capacity, cable size, breaker
rating, battery autonomy, or thermal compliance.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Mapping

HOLD = "HOLD"
PASS = "PASS"

REQUIRED_SITE_FIELDS = (
    "supply_voltage_v",
    "phases",
    "frequency_hz",
    "earthing_system",
    "prospective_short_circuit_ka",
    "ambient_temperature_c",
    "altitude_m",
)

REQUIRED_RELEASE_CHECKS = (
    "incoming_protection_verified",
    "conductor_ampacity_verified",
    "voltage_drop_verified",
    "short_circuit_withstand_verified",
    "selectivity_or_backup_verified",
    "thermal_rise_verified",
    "protective_bonding_verified",
)


def _num(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _hold(holds: list[dict[str, str]], code: str, detail: str) -> None:
    holds.append({"code": code, "detail": detail})


def _sum_dc_loads(panel: Mapping[str, Any], holds: list[dict[str, str]]) -> dict[str, Any]:
    voltage = _num((panel.get("dc_bus") or {}).get("nominal_voltage_v"))
    if not voltage or voltage <= 0:
        _hold(holds, "HOLD_DC_BUS_VOLTAGE", "Tensão nominal do barramento CC não definida.")
        return {"voltage_v": voltage, "continuous_current_a": None, "continuous_power_w": None}

    current_total = 0.0
    power_total = 0.0
    unresolved: list[str] = []
    for load in panel.get("dc_loads", []):
        tag = str(load.get("tag") or "UNNAMED")
        qty = _num(load.get("quantity")) or 1.0
        current = _num(load.get("current_a"))
        power = _num(load.get("power_w"))
        if current is None and power is None:
            unresolved.append(tag)
            continue
        if current is None:
            current = power / voltage
        if power is None:
            power = current * voltage
        current_total += current * qty
        power_total += power * qty

    if unresolved:
        _hold(
            holds,
            "HOLD_DC_LOAD_DATA",
            "Carga 24 Vcc sem consumo oficial: " + ", ".join(sorted(unresolved)),
        )

    reserve_pct = _num((panel.get("dc_bus") or {}).get("design_reserve_percent"))
    if reserve_pct is None:
        _hold(holds, "HOLD_DC_RESERVE_POLICY", "Reserva de projeto da alimentação 24 Vcc não definida.")
        design_current = None
        design_power = None
    else:
        factor = 1.0 + reserve_pct / 100.0
        design_current = current_total * factor
        design_power = power_total * factor

    return {
        "voltage_v": voltage,
        "continuous_current_a": round(current_total, 4),
        "continuous_power_w": round(power_total, 3),
        "design_reserve_percent": reserve_pct,
        "design_current_a": round(design_current, 4) if design_current is not None else None,
        "design_power_w": round(design_power, 3) if design_power is not None else None,
        "unresolved_loads": sorted(unresolved),
    }


def _check_power_supply(panel: Mapping[str, Any], dc: Mapping[str, Any], holds: list[dict[str, str]]) -> dict[str, Any]:
    psu = panel.get("power_supply") or {}
    rated_a = _num(psu.get("rated_output_current_a"))
    rated_w = _num(psu.get("rated_output_power_w"))
    design_a = _num(dc.get("design_current_a"))
    design_w = _num(dc.get("design_power_w"))

    if rated_a is None or rated_w is None:
        _hold(holds, "HOLD_PSU_RATING", "Corrente/potência nominal oficial da fonte não fechadas.")
    if design_a is None or design_w is None:
        return {"verified": False, "utilization_percent": None}

    utilization = None
    if rated_a and rated_a > 0:
        utilization = 100.0 * design_a / rated_a
        if design_a > rated_a + 1e-9:
            _hold(holds, "HOLD_PSU_CAPACITY", f"Carga de projeto {design_a:.3f} A excede fonte {rated_a:.3f} A.")

    if rated_w and design_w > rated_w + 1e-9:
        _hold(holds, "HOLD_PSU_POWER", f"Carga de projeto {design_w:.1f} W excede fonte {rated_w:.1f} W.")

    return {
        "model": psu.get("model"),
        "rated_output_current_a": rated_a,
        "rated_output_power_w": rated_w,
        "utilization_percent": round(utilization, 2) if utilization is not None else None,
        "verified": bool(rated_a and rated_w and design_a <= rated_a and design_w <= rated_w),
        "reference_ids": list(psu.get("reference_ids", [])),
    }


def _battery(panel: Mapping[str, Any], dc: Mapping[str, Any], holds: list[dict[str, str]]) -> dict[str, Any]:
    battery = panel.get("battery") or {}
    autonomy_h = _num(battery.get("required_autonomy_h"))
    load_a = _num(dc.get("continuous_current_a"))
    dod = _num(battery.get("max_depth_of_discharge"))
    aging = _num(battery.get("aging_factor"))
    temperature = _num(battery.get("temperature_factor"))

    missing = []
    for key, value in (
        ("required_autonomy_h", autonomy_h),
        ("max_depth_of_discharge", dod),
        ("aging_factor", aging),
        ("temperature_factor", temperature),
    ):
        if value is None:
            missing.append(key)

    if missing:
        _hold(holds, "HOLD_BATTERY_SIZING_INPUTS", "Parâmetros ausentes: " + ", ".join(missing))
        required_ah = None
    elif not load_a:
        _hold(holds, "HOLD_BATTERY_LOAD", "Carga contínua 24 Vcc ainda não fechada.")
        required_ah = None
    elif dod <= 0 or dod > 1 or aging <= 0 or temperature <= 0:
        _hold(holds, "HOLD_BATTERY_FACTORS", "Fatores de bateria fora do domínio permitido.")
        required_ah = None
    else:
        required_ah = load_a * autonomy_h * aging * temperature / dod

    installed_ah = _num(battery.get("installed_capacity_ah"))
    if required_ah is not None and installed_ah is not None and installed_ah + 1e-9 < required_ah:
        _hold(
            holds,
            "HOLD_BATTERY_CAPACITY",
            f"Capacidade instalada {installed_ah:.2f} Ah inferior à calculada {required_ah:.2f} Ah.",
        )

    return {
        "required_autonomy_h": autonomy_h,
        "required_capacity_ah": round(required_ah, 3) if required_ah is not None else None,
        "installed_capacity_ah": installed_ah,
        "series_units": battery.get("series_units"),
        "reference_ids": list(battery.get("reference_ids", [])),
    }


def _ac_panel_current(panel: Mapping[str, Any], holds: list[dict[str, str]]) -> dict[str, Any]:
    site = panel.get("site") or {}
    voltage = _num(site.get("supply_voltage_v"))
    phases = site.get("phases")
    pf = _num(site.get("design_power_factor"))
    efficiency = _num(site.get("design_efficiency"))
    demand_va = _num((panel.get("ac_load_summary") or {}).get("demand_va"))
    explicit_ib = _num((panel.get("ac_load_summary") or {}).get("design_current_a"))

    if explicit_ib is not None:
        return {"ib_a": round(explicit_ib, 4), "method": "EXPLICIT_VALIDATED_LOAD_SHEET"}

    if voltage is None or phases not in (1, 3) or demand_va is None:
        _hold(
            holds,
            "HOLD_PANEL_IB_INPUTS",
            "Não é possível calcular Ib sem tensão, número de fases e demanda aparente validada.",
        )
        return {"ib_a": None, "method": None}

    if phases == 1:
        ib = demand_va / voltage
        method = "S_OVER_V"
    else:
        if pf is None:
            pf = 1.0
        if efficiency is None:
            efficiency = 1.0
        if pf <= 0 or efficiency <= 0:
            _hold(holds, "HOLD_AC_FACTORS", "Fator de potência/eficiência inválido.")
            return {"ib_a": None, "method": None}
        # demand_va is apparent power, therefore Ib = S/(sqrt(3)*V).
        ib = demand_va / (math.sqrt(3.0) * voltage)
        method = "S_OVER_SQRT3_V"

    return {"ib_a": round(ib, 4), "method": method}


def evaluate_panel(panel_id: str, panel: Mapping[str, Any]) -> dict[str, Any]:
    holds: list[dict[str, str]] = []
    site = panel.get("site") or {}

    for field in REQUIRED_SITE_FIELDS:
        if site.get(field) is None:
            _hold(holds, f"HOLD_SITE_{field.upper()}", f"Dado de campo obrigatório ausente: {field}.")

    dc = _sum_dc_loads(panel, holds)
    psu = _check_power_supply(panel, dc, holds)
    battery = _battery(panel, dc, holds)
    ac = _ac_panel_current(panel, holds)

    protection = panel.get("protection") or {}
    ib = _num(ac.get("ib_a"))
    breaker_in = _num(protection.get("incoming_breaker_in_a"))
    conductor_iz = _num(protection.get("incoming_conductor_iz_a"))
    icu = _num(protection.get("incoming_breaker_icu_ka"))
    ik = _num(site.get("prospective_short_circuit_ka"))

    if ib is not None and breaker_in is not None and breaker_in + 1e-9 < ib:
        _hold(holds, "HOLD_IN_LT_IB", f"In {breaker_in:.2f} A menor que Ib {ib:.2f} A.")
    if breaker_in is not None and conductor_iz is not None and breaker_in > conductor_iz + 1e-9:
        _hold(holds, "HOLD_IN_GT_IZ", f"In {breaker_in:.2f} A maior que Iz {conductor_iz:.2f} A.")
    if icu is not None and ik is not None and icu + 1e-9 < ik:
        _hold(holds, "HOLD_ICU_LT_IK", f"Icu {icu:.2f} kA menor que Ik {ik:.2f} kA.")

    for check in REQUIRED_RELEASE_CHECKS:
        if protection.get(check) is not True and (panel.get("verification") or {}).get(check) is not True:
            _hold(holds, f"HOLD_{check.upper()}", f"Verificação obrigatória não concluída: {check}.")

    ina = _num(protection.get("assembly_rated_current_ina_a"))
    if ina is None:
        _hold(
            holds,
            "HOLD_ASSEMBLY_INA",
            "Corrente nominal do conjunto InA ainda não declarada/verificada conforme IEC 61439.",
        )
    elif ib is not None and ina + 1e-9 < ib:
        _hold(holds, "HOLD_INA_LT_IB", f"InA {ina:.2f} A menor que Ib {ib:.2f} A.")

    thermal = panel.get("thermal") or {}
    known_loss = 0.0
    unresolved_losses: list[str] = []
    for item in thermal.get("component_losses", []):
        qty = _num(item.get("quantity")) or 1.0
        loss = _num(item.get("loss_w"))
        if loss is None:
            unresolved_losses.append(str(item.get("tag") or "UNNAMED"))
        else:
            known_loss += qty * loss
    if unresolved_losses:
        _hold(holds, "HOLD_THERMAL_LOSS_DATA", "Perdas térmicas ausentes: " + ", ".join(sorted(unresolved_losses)))

    result = {
        "schema_version": "1.0",
        "panel_id": panel_id,
        "status": HOLD if holds else PASS,
        "a_do_quadro_a": ina if not holds and ina is not None else None,
        "calculated": {
            "ib_a": ac.get("ib_a"),
            "ib_method": ac.get("method"),
            "dc_bus": dc,
            "power_supply": psu,
            "battery": battery,
            "known_internal_losses_w": round(known_loss, 3),
        },
        "declared": {
            "assembly_rated_current_ina_a": ina,
            "incoming_breaker_in_a": breaker_in,
            "incoming_conductor_iz_a": conductor_iz,
            "prospective_short_circuit_ka": ik,
            "incoming_breaker_icu_ka": icu,
            "assembly_icw_ka_1s": _num(protection.get("assembly_icw_ka_1s")),
            "assembly_ipk_ka": _num(protection.get("assembly_ipk_ka")),
        },
        "holds": holds,
        "reference_ids": list(dict.fromkeys(panel.get("reference_ids", []))),
        "release_rule": "A_DO_QUADRO_ONLY_WHEN_ALL_ELECTRICAL_SIZING_GATES_PASS",
    }
    return result


def evaluate_document(data: Mapping[str, Any]) -> dict[str, Any]:
    panels = data.get("panels") or {}
    results = {str(pid): evaluate_panel(str(pid), p or {}) for pid, p in panels.items()}
    return {
        "schema_version": "1.0",
        "sizing_id": data.get("sizing_id"),
        "results": results,
        "status": HOLD if any(x["status"] != PASS for x in results.values()) else PASS,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    result = evaluate_document(data)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "output": str(output)}, ensure_ascii=False))
    return 0 if result["status"] == PASS else 3


if __name__ == "__main__":
    raise SystemExit(main())
