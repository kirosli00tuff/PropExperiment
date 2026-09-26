"""Stage E.2a Task 9 runner, phase 1: r_c, q_c and rho_c per admissible contract.

``uv run python -m screening.vehicles_run sizes`` reads each contract's research parquet (built
by BarsCoder, Task 7), its group calendar, reports/stage_e2a_bars.json (roll-blackout and
vendor-degraded dates, lead ruling L-8) and reports/stage_e0_liquidity.json (tick_size,
tick_value_usd), applies ``screening.vehicles`` (readings R1-R6), and writes
reports/stage_e2a_vehicle_sizes.json and .md. From research-window bars it computes r_c and the
checks on its inputs (tick grid, flag consistency) only: no other statistic, chart or summary.
A contract whose parquet does not exist yet (MBT until the crypto build) is written as pending.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import UTC, date, datetime
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from data.calendars import GROUP_OF_PRODUCT
from data.config import REPO_ROOT
from data.group_session import load_group_calendar, trade_dates_between
from screening import vehicles as v
from screening.vehicles_md import write_md

PDT = ZoneInfo("America/Vancouver")
CT = ZoneInfo("America/Chicago")
READINGS = REPO_ROOT / "reports" / "stage_e2a_vehicle_rule_readings.md"
READINGS_SHA256 = "8c3c29dd6531782b6b98d75192071977b8caebd37c48de6cab0afd1642d6b458"
LIQUIDITY = REPO_ROOT / "reports" / "stage_e0_liquidity.json"
BARS_REPORT = REPO_ROOT / "reports" / "stage_e2a_bars.json"
COSTS = REPO_ROOT / "reports" / "stage_e2a_costs.json"
OUT_JSON = REPO_ROOT / "reports" / "stage_e2a_vehicle_sizes.json"
OUT_MD = REPO_ROOT / "reports" / "stage_e2a_vehicle_sizes.md"
COLUMNS = ["ts_event", "open", "high", "low", "close", "instrument_id", "trade_date",
           "is_roll_session", "vendor_degraded_day", "in_scheduled_closure"]
RULINGS = {
    "L-1": "D6's O values stand (CME publishes no day-session open for most groups)",
    "L-2": "early-settlement days are not early closes (rates' EARLY_SETTLEMENT_CT excludes "
           "nothing)",
    "L-4 revised": "the 2025-11-28 outage is not a calendar entry; R3's as-of reading handles "
                   "a missing open bar",
    "L-7": "the 2026-02-25 metals halt is not a calendar entry; R3's as-of reading handles it",
    "L-8": "roll-blackout dates come from each product's group calendar, as BarsCoder "
           "recorded them in reports/stage_e2a_bars.json",
    "L-9": "MBT's research window ends at trade date 2026-06-18",
    "L-10": "O_X and C_X are clock times on the trade date's own calendar day; both R3 bars "
            "lie there, never in a booked-in holiday session",
    "R1": "no D6 value was corrected by the calendar confirmations; D6's table is used as "
          "written",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def rel(path: Path) -> str:
    return str(Path(path).relative_to(REPO_ROOT))


def parquet_path(product: str) -> Path:
    return (REPO_ROOT / "data" / "processed" / product
            / f"ohlcv-1m_{product}_v_0_2025-04-01_2026-06-19_research.parquet")


def frac_str(x: Fraction) -> str:
    return f"{x.numerator}/{x.denominator}"


def _dates(values) -> list[date]:
    return sorted(date.fromisoformat(str(d)) for d in values)


def bars_vendor_factor(entry: dict) -> tuple[int, str]:
    """BarsCoder's record of the vendor price scale: an explicit vendor tick if the report
    carries one, else the grid probe (off-grid counts at 1x, 10x, 100x the E.0 tick)."""
    tick = entry.get("tick", {})
    e0 = Fraction(Decimal(tick["tick"]))
    for holder in (tick, entry):
        for key in ("vendor_tick", "vendor_unit_tick"):
            if key in holder:
                return int(Fraction(Decimal(str(holder[key]))) / e0), f"bars.json {key}"
        if "vendor_price_factor" in holder:
            return int(holder["vendor_price_factor"]), "bars.json vendor_price_factor"
    probe = entry["raw_checks"]["grid_scale_probe"]
    factor = 100 if probe["x100"] == 0 and probe["x10"] == 0 else 10 if probe["x10"] == 0 else 1
    return factor, f"bars.json grid_scale_probe {probe}"


def cost_vendor_factor(costs: dict | None, product: str) -> int | None:
    if not costs or product not in costs.get("products", {}):
        return None
    return costs["products"][product].get("vendor_price_factor")


def degraded_flag_checks(frame, degraded: set[date], open_ct, close_ct) -> dict:
    """The per-bar flag (Databento's UTC date) against the trade-date list inside every
    [O_X, C_X) window of a bar's own trade date; and trade dates off the list with a flagged
    bar elsewhere (a Sunday-evening UTC date: R2 reads the list, as BarsCoder records it)."""
    loc = pd.to_datetime(frame["ts_event"].to_numpy(np.int64), utc=True).tz_convert(CT)
    cal_day = loc.tz_localize(None).normalize().to_numpy().astype("datetime64[D]")
    td = frame["trade_date"].astype(str).to_numpy()
    td_day = td.astype("datetime64[D]")
    minute = np.asarray(loc.hour * 60 + loc.minute)
    o_min, c_min = open_ct.hour * 60 + open_ct.minute, close_ct.hour * 60 + close_ct.minute
    same_day = cal_day == td_day
    in_win = same_day & (minute >= o_min) & (minute < c_min)
    on_list = np.isin(td, sorted(str(d) for d in degraded))
    flag = frame["vendor_degraded_day"].to_numpy(bool)
    mismatch = int((in_win & (flag != on_list)).sum())
    off_list_flagged = sorted({str(d) for d in td[flag & ~on_list]})
    return {"window_bars_flag_vs_list_mismatches": mismatch,
            "trade_dates_off_list_with_flagged_bars_outside_window": off_list_flagged}


def contract_entry(product: str, liquidity: dict, bars_report: dict, costs: dict | None,
                   calendars: dict) -> dict:
    exposure = v.EXPOSURE_OF_PRODUCT[product]
    group = GROUP_OF_PRODUCT[product]
    key, open_ct, close_ct = v.session_of(product, group)
    head = {"exposure": exposure.name, "cluster": exposure.cluster, "group": group,
            "d6_session_key": key, "O_X": open_ct.strftime("%H:%M"),
            "C_X": close_ct.strftime("%H:%M")}
    path = parquet_path(product)
    entry = bars_report["products"].get(product)
    if entry is None or not path.exists():
        return {**head, "status": "pending", "q_c": None, "r_c_usd": None, "rho_c": None,
                "cap_c": v.cap_for(product).cap,
                "reason": f"research parquet {rel(path)} not built yet"}
    if group not in calendars:
        calendars[group] = load_group_calendar(group)
    cal = calendars[group]
    last = v.LAST_TRADE_DATE.get(product, v.RESEARCH_LAST)
    module_oc = module_session(cal, product, last)
    if module_oc != (open_ct, close_ct):
        raise v.VehicleRuleError(f"{product}: D6 {open_ct}-{close_ct} != calendar {module_oc}")

    liq = liquidity[product]
    e0_tick = v.parse_tick_size(str(liq["tick_size"]))
    vtick = v.vendor_tick(product, e0_tick)
    tick_value = Decimal(str(liq["tick_value_usd"]))
    frame = pq.read_table(path, columns=COLUMNS).to_pandas()
    meta = json.loads(pq.ParquetFile(path).schema_arrow.metadata[b"propexperiment"])

    prices = np.concatenate([frame[c].to_numpy(np.float64) for c in ("open", "high", "low",
                                                                      "close")])
    grid = v.tick_scale_check(prices, vtick)
    bars_factor, bars_src = bars_vendor_factor(entry)
    my_factor = v.VENDOR_PRICE_FACTOR.get(product, 1)
    if Decimal(entry["tick"]["tick"]) != e0_tick:
        raise v.VehicleRuleError(f"{product}: bars.json tick {entry['tick']['tick']} != E.0 "
                                 f"{e0_tick}")
    if not grid["passed"] or bars_factor != my_factor:
        raise v.VehicleRuleError(f"{product}: vendor tick check failed {grid}, bars {bars_factor}")
    cost_factor = cost_vendor_factor(costs, product)
    if cost_factor is not None and cost_factor != my_factor:
        raise v.VehicleRuleError(f"{product}: CostCoder factor {cost_factor} != {my_factor}")

    rolls = entry["rolls"]
    blackout = set(_dates(rolls["roll_blackout_dates_in_window"]))
    degraded = set(_dates(entry["degraded"]["on_research_trade_dates"]))
    in_win = lambda ds: {d for d in _dates(ds) if v.RESEARCH_FIRST <= d <= last}  # noqa: E731
    checks = {
        "parquet_metadata_blackout_equal": in_win(meta["roll_blackout_dates"]) == in_win(blackout),
        "parquet_metadata_degraded_equal": set(_dates(meta["degraded_on_research_trade_dates"]))
        == degraded,
    }
    splices = in_win(rolls["splice_trade_dates"])
    roll_flag_days = set(_dates(frame.loc[frame["is_roll_session"], "trade_date"].unique()))
    checks["is_roll_session_dates_equal_splice_dates"] = roll_flag_days == splices
    recomputed = v.blackout_dates(splices, cal.is_trade_date)
    checks["blackout_recomputed_from_group_calendar_equal"] = in_win(recomputed) == in_win(
        blackout)
    checks.update(degraded_flag_checks(frame, degraded, open_ct, close_ct))
    bad = [k for k, ok in checks.items() if ok is False or (k.endswith("mismatches") and ok)]
    if bad:
        raise v.VehicleRuleError(f"{product}: input checks failed: {bad} {checks}")

    days = frame["trade_date"].astype(str).to_numpy().astype("datetime64[D]")
    m = v.measure_risk(frame["ts_event"].to_numpy(np.int64), days,
                       frame["open"].to_numpy(np.float64), frame["close"].to_numpy(np.float64),
                       frame["instrument_id"].to_numpy(np.int64), open_ct=open_ct,
                       close_ct=close_ct, holidays=cal.holidays, roll_blackout=blackout,
                       degraded=degraded, tick=vtick, tick_value_usd=tick_value, last=last)
    cal_days = set(trade_dates_between(cal, v.RESEARCH_FIRST, last))
    closures = sorted(d for d in cal.holidays if v.RESEARCH_FIRST <= d <= last
                      and v.calendar_exclusion(cal.holidays[d], close_ct) == "full_closure")
    cap = v.cap_for(product)
    r_c = m.r_c_usd
    q_c, rho = v.size_contract(r_c, cap.cap)
    excluded = {c: [str(d) for d in m.excluded[c]] for c in v.CAUSES}
    return {
        **head, "status": "computed",
        "parquet": rel(path), "parquet_sha256": sha256_file(path),
        "tick_size_e0": str(e0_tick), "vendor_price_factor": my_factor,
        "vendor_tick": str(vtick), "tick_value_usd": str(tick_value),
        "vendor_tick_check": {**grid, "bars_json_factor": bars_factor,
                              "bars_json_source": bars_src, "costs_json_factor": cost_factor},
        "input_checks": checks,
        "trade_dates_in_parquet": len(m.trade_dates),
        "first_trade_date": str(m.trade_dates[0]), "last_trade_date": str(m.trade_dates[-1]),
        "calendar_trade_dates_without_bars": sorted(str(d) for d in cal_days - set(m.trade_dates)),
        "parquet_trade_dates_not_calendar_trade_dates": sorted(
            str(d) for d in set(m.trade_dates) - cal_days),
        "calendar_full_closures_in_window_not_trade_dates": [str(d) for d in closures],
        "dates_excluded_by_cause": excluded,
        "dates_excluded_count_by_cause": {c: len(x) for c, x in excluded.items()},
        "dates_excluded_total": len(m.trade_dates) - len(m.used),
        "dates_used_count": len(m.used), "dates_used": [str(d) for d in m.used],
        "exact_bar_missing": {"open_bar_at_O_X_missing": [str(d) for d in m.open_bar_missing],
                              "close_bar_at_C_X_minus_1_missing": [
                                  str(d) for d in m.close_bar_missing],
                              "either_count": len(m.exact_bar_missing)},
        "other_trade_date_bars_in_window": m.other_trade_date_bars_in_window,
        "bars_json_calendar_check": _calendar_check(entry, m.used),
        "degraded_off_list_dates_used_for_r_c": sorted(
            set(checks["trade_dates_off_list_with_flagged_bars_outside_window"])
            & {str(d) for d in m.used}),
        "sum_abs_move_ticks": m.sum_abs_ticks,
        "r_c_usd": float(r_c), "r_c_usd_exact": frac_str(r_c),
        "r_star_over_r_c": float(v.R_STAR_USD / r_c),
        "cap_c": cap.cap, "cap_source": cap.source, "cap_lot_d9_5": cap.lot_cap_d9_5,
        "cap_vol_50k_d9_11": cap.vol_cap_50k_d9_11, "cap_note": cap.note,
        "q_c": q_c, "rho_c": float(rho), "rho_c_exact": frac_str(rho),
        "r7_non_candidate": product in v.NON_CANDIDATES_BY_DECISION,
    }


def _calendar_check(entry: dict, used: tuple[date, ...]) -> dict:
    """BarsCoder's step-4b result for the product, and whether a day it questions is a date
    this file uses for r_c."""
    chk = entry.get("calendar_check", {})
    found = chk.get("discrepancies", [])
    days = sorted({str(x["day"]) for x in found})
    used_s = {str(d) for d in used}
    kinds: dict[str, int] = {}
    for x in found:
        kinds[x["kind"]] = kinds.get(x["kind"], 0) + 1
    early_used = sorted({str(x["day"]) for x in found
                         if x["kind"].startswith("early_stop") and str(x["day"]) in used_s})
    return {"passed": chk.get("passed"), "discrepancy_kinds": kinds, "discrepancy_days": days,
            "discrepancy_days_used_for_r_c": [d for d in days if d in used_s],
            "early_stop_days_used_for_r_c": early_used}


def module_session(cal, product: str, day: date):
    """The group module's own (O, C) for ``product`` on trade date ``day``: keyed by product,
    metals sub-group, group or "*" (the modules use each of these)."""
    spec = cal.spec_for(day).day_session_ct
    for key in (product, cal.subgroup_of_product.get(product), cal.group, "*"):
        if key is not None and key in spec:
            return spec[key]
    raise v.VehicleRuleError(f"{product}: no day session in {cal.group}'s module ({sorted(spec)})")


def run_sizes() -> dict:
    if sha256_file(READINGS) != READINGS_SHA256:
        raise v.VehicleRuleError("the readings file does not match its recorded sha256")
    liquidity = {r["symbol"]: r for r in json.loads(LIQUIDITY.read_text())["products"]}
    bars_report = json.loads(BARS_REPORT.read_text())
    costs = json.loads(COSTS.read_text()) if COSTS.exists() else None
    calendars: dict = {}
    contracts = {}
    for x in v.EXPOSURES:
        for product in x.products:
            contracts[product] = contract_entry(product, liquidity, bars_report, costs, calendars)
            print(f"{product}: {contracts[product]['status']} q_c={contracts[product]['q_c']}",
                  flush=True)
    now = datetime.now(UTC)
    code = [REPO_ROOT / "screening" / f for f in ("vehicles.py", "vehicles_run.py",
                                                    "vehicles_md.py")]
    return {
        "stage": "E.2a", "task": "9 phase 1 (r_c, q_c, rho_c)",
        "rule": "docs/STAGE_E_DESIGN.md D2 (frozen), read as R1-R6 of "
                "reports/stage_e2a_vehicle_rule_readings.md",
        "generated_utc": now.isoformat(),
        "generated_pdt": now.astimezone(PDT).strftime("%Y-%m-%d %H:%M %Z"),
        "r_star_usd": "360.68", "rho_band": ["0.5", "2.0"],
        "rulings_applied": RULINGS,
        "units": "r_c in USD per contract per day; moves in ticks of the contract in the "
                 "vendor's price units (ZC, ZW, ZS, ZL, HE, LE: 100 x the E.0 USD tick)",
        "inputs_sha256": {
            rel(READINGS): sha256_file(READINGS), rel(LIQUIDITY): sha256_file(LIQUIDITY),
            rel(BARS_REPORT): sha256_file(BARS_REPORT),
            **({rel(COSTS): sha256_file(COSTS)} if COSTS.exists() else {}),
            **{k: s for cal in calendars.values() for k, s in cal.module_sha256().items()},
        },
        "code_sha256": {rel(p): sha256_file(p) for p in code},
        "counts": {"contracts": len(contracts),
                   "computed": sum(c["status"] == "computed" for c in contracts.values()),
                   "pending": sorted(p for p, c in contracts.items() if c["status"] != "computed")},
        "contracts": contracts,
    }


def main(argv: list[str]) -> int:
    if argv[1:] != ["sizes"]:
        print("usage: python -m screening.vehicles_run sizes", file=sys.stderr)
        return 2
    os.nice(10)
    pa.set_cpu_count(4)
    pa.set_io_thread_count(4)
    result = run_sizes()
    OUT_JSON.write_text(json.dumps(result, indent=1) + "\n")
    write_md(result, OUT_MD)
    print(f"wrote {rel(OUT_JSON)} and {rel(OUT_MD)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
