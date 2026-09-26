"""Stage E.2a Task 9 phase 2: R8 cost per dollar of risk, R9-R11 per exposure, R12 epsilon.

``uv run python -m screening.vehicles_choice`` reads the phase-1 sizes
(reports/stage_e2a_vehicle_sizes.json, sha256 checked) and the frozen D8 cost table
(reports/stage_e2a_costs.json, sha256 checked, loaded by sim.product_costs), applies
``screening.vehicles`` (readings R7-R12), and writes reports/stage_e2a_vehicles.json and .md
with the arithmetic of every exposure written out. It reads no bar: r_c comes from phase 1, whose
numbers are re-derived here from the parquets (hashes checked) before anything is chosen.
Anything R1-R12 does not settle is written as a question for the lead, never decided.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

import pyarrow as pa

from data.config import REPO_ROOT
from screening import vehicles as v
from screening import vehicles_run as p1
from screening.vehicles_choice_md import write_choice_md
from sim.product_costs import load_cost_table

COSTS = REPO_ROOT / "reports" / "stage_e2a_costs.json"
COSTS_SHA256 = "f4360bb77272d0335485a9e01c0f6fc6ab99c47d52e640d95f9cd0397296df14"
SIZES = p1.OUT_JSON
SIZES_SHA256 = "280d7e9df1953069448ca1762588477146a5d3c35bc53d3e9e2df50272c47325"
DESIGN = REPO_ROOT / "docs" / "STAGE_E_DESIGN.md"
OUT_JSON = REPO_ROOT / "reports" / "stage_e2a_vehicles.json"
OUT_MD = REPO_ROOT / "reports" / "stage_e2a_vehicles.md"
LEAD_ANSWERS = {
    "Q-1": "accepted (02:42 PDT): SI and HG keep the D9.5 cap of 1; D9.11's 0 is discretionary "
           "and R5 lists only SIL and MHG",
    "Q-2": "accepted (02:42 PDT): vendor-degraded trade dates as BarsCoder lists them",
}
TRADED = ("chosen", "undersized")


def _minutes(hhmm: str) -> int:
    return int(hhmm[:2]) * 60 + int(hhmm[3:])


def _check_hash(path: Path, want: str) -> str:
    got = p1.sha256_file(path)
    if got != want:
        raise v.VehicleRuleError(f"{p1.rel(path)} sha256 {got} != the frozen {want}")
    return got


def contract_cost(size: dict, model) -> tuple[dict, Fraction]:
    """R8 for one contract: (row, exact cost per dollar of risk)."""
    product = model.product
    if model.q_c != size["q_c"]:
        raise v.VehicleRuleError(f"{product}: cost table q_c {model.q_c} != sizes {size['q_c']}")
    tv = Fraction(Decimal(size["tick_value_usd"]))
    if Fraction(Decimal(str(model.tick_value_usd))) != tv:
        raise v.VehicleRuleError(f"{product}: tick value differs between the tables")
    o_min, c_min = _minutes(size["O_X"]), _minutes(size["C_X"])
    sides = [v.BucketSides(b.start_min, b.end_min, b.side_ticks["buy"], b.side_ticks["sell"])
             for b in model.buckets]
    slip_ticks = v.one_side_slippage_ticks(sides, o_min, c_min)
    slip_usd = slip_ticks * tv
    commission = Fraction(Decimal(str(model.commission_rt_usd)))
    r_c = Fraction(size["r_c_usd_exact"])
    cpd = v.cost_per_dollar_of_risk(commission, slip_usd, r_c)
    buckets = [{"bucket": b.key, "minutes_in_window": min(b.end_min, c_min) - max(b.start_min,
                                                                                    o_min),
                "buy_ticks": b.side_ticks["buy"], "sell_ticks": b.side_ticks["sell"],
                "fallback": b.fallback}
               for b in model.buckets if max(b.start_min, o_min) < min(b.end_min, c_min)]
    row = {
        "exposure": size["exposure"], "O_X": size["O_X"], "C_X": size["C_X"],
        "r_c_usd": size["r_c_usd"], "r_c_usd_exact": size["r_c_usd_exact"],
        "q_c": size["q_c"], "cap_c": size["cap_c"], "cap_source": size["cap_source"],
        "rho_c": size["rho_c"], "rho_c_exact": size["rho_c_exact"],
        "tick_value_usd": size["tick_value_usd"],
        "commission_rt_usd": float(commission),
        "one_side_slippage_ticks": float(slip_ticks), "one_side_slippage_usd": float(slip_usd),
        "round_turn_cost_usd_per_contract": float(commission + 2 * slip_usd),
        "cost_per_dollar_of_risk": float(cpd),
        "day_session_buckets": buckets,
        "r7_non_candidate": product in v.NON_CANDIDATES_BY_DECISION,
    }
    return row, cpd


def _band(product: str, rho: Fraction) -> str:
    if product in v.NON_CANDIDATES_BY_DECISION:
        return "R7 (U7): not a candidate"
    if rho > v.RHO_MAX:
        return "rho_c > 2.0: not a candidate"
    if rho >= v.RHO_MIN_PREFERRED:
        return "0.5 <= rho_c <= 2.0: candidate, preferred"
    return "rho_c < 0.5: candidate, not preferred"


def _contract_lines(p: str, row: dict, x: v.Exposure) -> list[str]:
    r_c = Fraction(row["r_c_usd_exact"])
    rho = Fraction(row["rho_c_exact"])
    ratio = v.R_STAR_USD / r_c
    return [
        f"{p} (ADV {x.adv(p):,}): r_c = ${float(r_c):.4f}; R*/r_c = 360.68 / {float(r_c):.4f} = "
        f"{float(ratio):.4f}, round-half-up {v.round_half_up(ratio)}; q_c = min(cap {row['cap_c']}"
        f" ({row['cap_source']}), max(1, {v.round_half_up(ratio)})) = {row['q_c']}; rho_c = "
        f"{row['q_c']} x {float(r_c):.4f} / 360.68 = {float(rho):.4f}: {_band(p, rho)}",
        f"{p} cost: (commission ${row['commission_rt_usd']:.2f} + 2 x one-side "
        f"${row['one_side_slippage_usd']:.6f} [{row['one_side_slippage_ticks']:.6f} ticks x "
        f"${row['tick_value_usd']}]) / r_c ${float(r_c):.4f} = "
        f"${row['round_turn_cost_usd_per_contract']:.6f} / ${float(r_c):.4f} = "
        f"{row['cost_per_dollar_of_risk']:.8f} per dollar of risk",
    ]


def exposure_result(x: v.Exposure, rows: dict, cpds: dict) -> dict:
    facts = [v.VehicleFacts(p, rows[p]["q_c"], rows[p]["cap_c"],
                            Fraction(rows[p]["rho_c_exact"]), cpds[p], x.adv(p))
             for p in x.products]
    lines = [line for p in x.products for line in _contract_lines(p, rows[p], x)]
    try:
        choice = v.choose_vehicle(x.name, facts)
    except v.VehicleRuleError as err:
        choice = v.Choice(x.name, "question", None, (), (), (), f"not settled by R9: {err}")
    binds = None
    if x.name in v.PREFERRED_MICRO:
        plain = v.choose_vehicle(x.name, facts, apply_preference=False)
        binds = (plain.status, plain.vehicle) != (choice.status, choice.vehicle)
        lines.append(f"R9 (D9.11) {v.PREFERRED_MICRO[x.name]} sentence: without it the rule "
                     f"gives {plain.status} {plain.vehicle or ''}".rstrip()
                     + f"; the sentence {'binds' if binds else 'does not bind'}")
    lines += [f"Candidates (rho_c <= 2.0, less R7): {list(choice.candidates) or 'none'}; "
              f"excluded by R7: {list(choice.excluded_by_r7) or 'none'}",
              f"Preferred (rho_c >= 0.5): {list(choice.preferred) or 'none'}",
              f"Decides: {choice.deciding}"]
    eps = None
    if choice.status in TRADED:
        q, tv = rows[choice.vehicle]["q_c"], Decimal(rows[choice.vehicle]["tick_value_usd"])
        eps = v.translated_epsilon_ticks(q, tv)
        lines.append(f"eps_X = floor(85.00 / ({q} x ${tv})) = floor("
                     f"{float(v.EPS_BAR_USD / (q * Fraction(tv))):.4f}) = {eps} net ticks per "
                     "contract per day (R12)")
        if choice.status == "undersized":
            lines.append("R10: undersized, traded at the cap; its funnel-derived epsilon then "
                         "governs (D2, D3)")
    return {"exposure": x.name, "cluster": x.cluster, "admissible": list(x.products),
            "status": choice.status, "vehicle": choice.vehicle,
            "q_c": rows[choice.vehicle]["q_c"] if choice.vehicle else None,
            "candidates": list(choice.candidates), "preferred": list(choice.preferred),
            "excluded_by_r7": list(choice.excluded_by_r7), "deciding": choice.deciding,
            "sil_mhg_sentence_binds": binds, "eps_X_net_ticks": eps, "arithmetic": lines}


def _reproduce_phase1(sizes: dict) -> dict:
    """Re-derive r_c, q_c and rho_c from the parquets with the current code."""
    again = p1.run_sizes()["contracts"]
    keys = ("r_c_usd_exact", "q_c", "rho_c_exact", "dates_used", "parquet_sha256")
    diff = [(p, k) for p, c in sizes["contracts"].items() for k in keys if again[p][k] != c[k]]
    if diff:
        raise v.VehicleRuleError(f"phase 1 does not reproduce: {diff[:5]}")
    return {"contracts": len(again), "fields_compared": list(keys), "differences": 0}


def run_choice() -> dict:
    hashes = {p1.rel(COSTS): _check_hash(COSTS, COSTS_SHA256),
              p1.rel(SIZES): _check_hash(SIZES, SIZES_SHA256),
              p1.rel(p1.READINGS): _check_hash(p1.READINGS, p1.READINGS_SHA256)}
    sizes = json.loads(SIZES.read_text())
    reproduced = _reproduce_phase1(sizes)
    models = load_cost_table(COSTS)
    rows, cpds = {}, {}
    for product, size in sizes["contracts"].items():
        rows[product], cpds[product] = contract_cost(size, models[product])
    exposures = [exposure_result(x, rows, cpds) for x in v.EXPOSURES]
    for path in (p1.LIQUIDITY, p1.BARS_REPORT, DESIGN):
        hashes[p1.rel(path)] = p1.sha256_file(path)
    for size in sizes["contracts"].values():
        hashes[size["parquet"]] = size["parquet_sha256"]  # re-derived above, equal
    calendars = {k: p1.sha256_file(REPO_ROOT / k) for k in sizes["inputs_sha256"]
                 if k.startswith("data/")}
    changed = sorted(k for k, h in calendars.items() if h != sizes["inputs_sha256"][k])
    code = ("screening/vehicles.py", "screening/vehicles_run.py", "screening/vehicles_md.py",
            "screening/vehicles_choice.py", "screening/vehicles_choice_md.py",
            "sim/product_costs.py")
    now = datetime.now(UTC)
    by_status: dict[str, list[str]] = {}
    for e in exposures:
        by_status.setdefault(e["status"], []).append(e["exposure"])
    return {
        "stage": "E.2a", "task": "9 phase 2 (vehicle choice)",
        "rule": "docs/STAGE_E_DESIGN.md D2 (frozen), read as R1-R12 of "
                "reports/stage_e2a_vehicle_rule_readings.md",
        "generated_utc": now.isoformat(),
        "generated_pdt": now.astimezone(p1.PDT).strftime("%Y-%m-%d %H:%M %Z"),
        "lead_answers": LEAD_ANSWERS,
        "phase1_reproduced": reproduced,
        "stale_hash_note": (
            "reports/stage_e2a_vehicle_sizes.json lists reports/stage_e2a_costs.json with sha256 "
            f"{sizes['inputs_sha256'].get('reports/stage_e2a_costs.json')}: the provisional "
            "table, read in phase 1 only to cross-check the vendor price factor (q_c does not "
            f"depend on costs). Phase 2 uses only the frozen table, sha256 {COSTS_SHA256}."),
        "inputs_sha256": {**hashes, **calendars},
        "calendar_modules_changed_since_phase1": changed,
        "code_sha256": {c: p1.sha256_file(REPO_ROOT / c) for c in code},
        "counts": {"exposures": len(exposures), "contracts": len(rows),
                   "by_status": by_status},
        "exposures": exposures,
        "contracts": rows,
    }


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: python -m screening.vehicles_choice", file=sys.stderr)
        return 2
    os.nice(10)
    pa.set_cpu_count(4)
    pa.set_io_thread_count(4)
    result = run_choice()
    OUT_JSON.write_text(json.dumps(result, indent=1) + "\n")
    write_choice_md(result, OUT_MD)
    print(f"wrote {p1.rel(OUT_JSON)} and {p1.rel(OUT_MD)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
