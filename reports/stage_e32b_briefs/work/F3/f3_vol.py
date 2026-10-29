"""Stage E.32b F3 driver: spec section 2 for the 47 codes. Run from the repo root (one process, nice 10, resumable):

    flock reports/stage_e32b_briefs/work/heavy.lock nice -n 10 uv run python reports/stage_e32b_briefs/work/F3/f3_vol.py

Per-root parts go to work/F3/parts/<ROOT>.json (a restart skips finished roots). Assembly writes
reports/stage_e32b_briefs/F3_vol.json and work/F3/regression.json (against E.28's A0_contract_stats.json).
Every bar file is opened through f3_guard.BarGuard (allow-list on the resolved path, log in work/F3/opens.log).
"""
from __future__ import annotations

import hashlib
import json
import os
import resource
import sys
import time
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(HERE))

from f3_core import (aggregate, calendar_module, day_record, early_halt_days,  # noqa: E402
                     main_session_from_calendar, trade_dates, transfer_oc1)
from f3_guard import ALLOWED_MONTHS, CODES_47, BarGuard  # noqa: E402

BRIEFS = REPO / "reports/stage_e32b_briefs"
PARTS = HERE / "parts"
OUT_JSON = BRIEFS / "F3_vol.json"
REG_JSON = HERE / "regression.json"
SPEC = REPO / "reports/stage_e32b_ranking_spec.md"
SPEC_SHA = "09ebe6970fcf027009152fa81a414360a015d535b095138cdf65cf1a4eb58635"
A0_JSON = REPO / "reports/stage_e28_briefs/A0_contract_stats.json"
WIN_START, WIN_END = date(2022, 11, 1), date(2023, 10, 31)
REF_DAY = date(2023, 6, 14)  # a regular Wednesday, used only to read L_main off the group calendar
FAMILY_OF = {c: f for f, cs in {
    "crude": "MCL QM CL", "natgas": "MNG QG NG", "metals": "MGC GC SIL SI MHG HG", "fx": "M6E 6E M6A 6A",
    "crypto": "MET ETH MBT BTC", "equity": "M2K RTY MYM YM MNQ NQ", "rates": "2YY 5YY 10Y 30Y ZT ZF ZN ZB",
    "grains": "MZC MZS MZW MZL MZM XC XK XW ZC ZS ZW ZL ZM"}.items() for c in cs.split()}
OC1_SOURCE = {"QM": "CL", "MNG": "NG", "QG": "NG", "M6E": "6E", "M6A": "6A", "BTC": "MBT", "M2K": "RTY",
              "MYM": "YM", "MNQ": "NQ", "MZC": "ZC", "MZS": "ZS", "MZW": "ZW", "MZL": "ZL", "MZM": "ZM",
              "XC": "ZC", "XK": "ZS", "XW": "ZW"}
UNKNOWN_REASON = {
    "SI": "no owned standard-window bars and no owned sibling (spec 2.4)",
    "SIL": "no owned standard-window bars and no owned sibling (spec 2.4)",
    "MET": "no owned standard-window bars and no owned sibling (spec 2.4)",
    "ETH": "no owned standard-window bars and no owned sibling (spec 2.4)",
    **{c: "yield-quoted micro: no transfer from price-quoted Treasury futures (spec 2.4)"
       for c in ("2YY", "5YY", "10Y", "30Y")},
}
FIELDS = ["instrument_id", "ts_event", "high", "low", "close"]


def now_pdt() -> str:
    return datetime.now(ZoneInfo("America/Vancouver")).strftime("%Y-%m-%d %H:%M:%S %Z")


def tick_info(code: str) -> dict:
    """Exchange tick (products.py units) and its source; A1 fields (flagged) for codes products.py lacks."""
    from rules.products import PRODUCTS
    if code in PRODUCTS:
        p = PRODUCTS[code]
        return {"tick": Decimal(str(p.tick_size)), "source": "rules/products.py", "flag": None}
    fam = FAMILY_OF[code]
    rows = json.loads((REPO / f"reports/stage_e28_briefs/A1_{fam}.json").read_text())
    row = next(r for r in rows if r.get("candidate") == code)
    t = row["tick_size"]
    val = Decimal(str(t["value"]))
    unit = t.get("unit") or ""
    if unit.startswith("US cents"):
        val = val / 100  # products.py quotes grains in USD per unit; A1 in US cents
    return {"tick": val, "source": f"reports/stage_e28_briefs/A1_{fam}.json tick_size ({t['value']} {unit})",
            "flag": "tick from E.28 A1 (code absent from rules/products.py)"}


def owned_codes(guard: BarGuard) -> list[str]:
    """A code owns standard-window bars when all 12 allow-listed monthly files exist (folder listing, stat only)."""
    return [c for c in CODES_47 if all(os.path.isfile(guard.allowed_path(c, m)) for m in ALLOWED_MONTHS)]


def load_root(guard: BarGuard, code: str) -> tuple[np.ndarray, list[str]]:
    import databento

    def reader(path: str) -> np.ndarray:
        return databento.DBNStore.from_file(path).to_ndarray()[FIELDS].copy()

    parts, names = [], []
    for m in ALLOWED_MONTHS:
        path = guard.allowed_path(code, m)
        parts.append(guard.open(path, reader))
        names.append(str(path.relative_to(REPO)))
    arr = np.concatenate(parts)
    return arr[np.argsort(arr["ts_event"], kind="stable")], names


def holiday_report(group: str, sample_days: list[date], excluded: set) -> dict:
    """E.21 quirk: US holidays (data.cme_calendar) that appear as trade dates in the raw sample."""
    import importlib
    us = importlib.import_module("data.cme_calendar").HOLIDAYS
    grp = importlib.import_module(calendar_module(group)).HOLIDAYS
    in_sample = [d for d in sample_days if d in us]
    rows = [{"date": str(d), "us_name": us[d].name, "group_kind": grp[d].kind.name if d in grp else None,
             "excluded": d in excluded} for d in in_sample]
    return {"us_holiday_trade_dates_in_sample": len(rows),
            "us_holiday_dates_excluded": sum(r["excluded"] for r in rows),
            "us_holiday_dates_kept": sum(not r["excluded"] for r in rows), "rows": rows}


def root_part(guard: BarGuard, code: str) -> dict:
    from data.calendars import GROUP_OF_PRODUCT
    from rules.products import PRODUCTS
    p = PRODUCTS[code]
    group = GROUP_OF_PRODUCT[code]
    tick_fixed = float(p.vendor_tick_fixed)
    arr, names = load_root(guard, code)
    td = trade_dates(arr["ts_event"])
    keep = (td >= np.datetime64(WIN_START)) & (td <= np.datetime64(WIN_END))
    arr, td = arr[keep], td[keep]
    ts = arr["ts_event"].astype("int64")
    close, hi, lo = (arr[k].astype("float64") for k in ("close", "high", "low"))
    inst = arr["instrument_id"].astype("int64")
    halts = early_halt_days(group)
    cuts = np.flatnonzero(np.diff(td.astype("int64"))) + 1
    bounds = np.concatenate([[0], cuts, [td.size]])
    days = [td[s].astype(object) for s in bounds[:-1]]
    dated, excluded = [], set()
    for d, s, e in zip(days, bounds[:-1], bounds[1:]):
        if d in halts:
            excluded.add(d)
            continue
        dated.append((d, day_record(group, d, ts[s:e], close[s:e], hi[s:e], lo[s:e], inst[s:e], tick_fixed)))
    stats = aggregate(dated, excluded, tick_fixed, 1e-9 / p.vendor_price_factor)
    l_main, sess = main_session_from_calendar(group, REF_DAY)
    return {"code": code, "group": group, "tick_size": str(p.tick_size), "vendor_tick": str(p.vendor_tick),
            "vendor_price_factor": p.vendor_price_factor, "files_opened": names, "n_bars": int(arr.size),
            "trade_dates_all": len(days), "first_trade_date": str(days[0]), "last_trade_date": str(days[-1]),
            "early_halt_dates_excluded": sorted(str(d) for d in excluded),
            "early_halt_calendar": calendar_module(group), "L_main": l_main, "main_session_pt": sess,
            "holidays": holiday_report(group, days, excluded), **stats}


def run_parts(guard: BarGuard, owned: list[str]) -> None:
    PARTS.mkdir(parents=True, exist_ok=True)
    for code in owned:
        path = PARTS / f"{code}.json"
        if path.exists():
            print(f"{now_pdt()} {code}: part exists, skipped", flush=True)
            continue
        t0 = time.time()
        res = root_part(guard, code)
        res["seconds"] = round(time.time() - t0, 1)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(res, indent=1))
        tmp.rename(path)
        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
        print(f"{now_pdt()} {code}: done in {res['seconds']}s, n_dates {res['n_dates']}, peak RSS so far "
              f"{rss:.0f} MB", flush=True)


PUBLIC = ("n_dates", "L_main", "main_session_pt", "h", "OC", "overnight", "R_d", "main_range_median", "median_close")


def assemble(owned: list[str]) -> dict:
    from data.calendars import GROUP_OF_PRODUCT
    parts = {c: json.loads((PARTS / f"{c}.json").read_text()) for c in owned}
    roots, files = {}, []
    for c in owned:
        files += parts[c]["files_opened"]
    for code in CODES_47:
        ti = tick_info(code)
        base = {"family": FAMILY_OF[code], "tick_size": float(ti["tick"]), "tick_source": ti["source"],
                "flags": [ti["flag"]] if ti["flag"] else []}
        if code == "NQ":
            base["flags"].append("NQ excluded from scoring (V49); computed as MNQ's transfer source")
        if code in parts:
            pt = parts[code]
            roots[code] = {"status": "owned", "oc1_source": None, "oc1_factor": None, **base,
                           **{k: pt[k] for k in PUBLIC},
                           "early_halt_dates_excluded_n": len(pt["early_halt_dates_excluded"]),
                           "us_holiday_trade_dates": {k: pt["holidays"][k] for k in (
                               "us_holiday_trade_dates_in_sample", "us_holiday_dates_excluded",
                               "us_holiday_dates_kept")},
                           "overnight_pairs_span_excluded_date": pt["overnight_pairs_span_excluded_date"]}
            continue
        src = OC1_SOURCE.get(code)
        if src in parts:
            factor = tick_info(src)["tick"] / ti["tick"]
            tr = transfer_oc1({k: parts[src][k] for k in PUBLIC if k not in ("L_main", "main_session_pt")},
                              float(factor))
            own_group = GROUP_OF_PRODUCT.get(code)
            if own_group:
                l_main, sess = main_session_from_calendar(own_group, REF_DAY)
                sess_note = f"session from own group calendar ({own_group})"
            else:
                l_main, sess = parts[src]["L_main"], parts[src]["main_session_pt"]
                sess_note = f"session taken from {src} (code absent from data.calendars)"
            roots[code] = {"status": "OC1", "oc1_source": src, "oc1_factor": float(factor), **base, **tr,
                           "L_main": l_main, "main_session_pt": sess}
            roots[code]["flags"] += [f"OC1 from {src}: tick statistics x {factor} ({src} tick / own tick); "
                                     "counts are the source's; median_close is the source's price", sess_note]
            continue
        own_group = GROUP_OF_PRODUCT.get(code)
        l_main, sess = main_session_from_calendar(own_group, REF_DAY) if own_group else (None, None)
        nul_h = {"sigma": None, "m": None, "median_abs": None, "p99_abs": None, "n": 0}
        nul = {"sigma": None, "m": None, "n": 0}
        roots[code] = {"status": "unknown", "oc1_source": None, "oc1_factor": None, **base, "n_dates": 0,
                       "L_main": l_main, "main_session_pt": sess, "h": {str(h): dict(nul_h) for h in
                                                                      (1, 2, 5, 15, 30, 60, 120, 240)},
                       "OC": dict(nul), "overnight": {"cc": dict(nul), "on": dict(nul)},
                       "R_d": {"median": None, "p99": None, "n": 0}, "main_range_median": None,
                       "median_close": None}
        roots[code]["flags"].append(UNKNOWN_REASON.get(code, "no owned bars and no owned sibling"))
    for r in roots.values():  # fixed-point prices: drop float noise (1e-9 vendor units)
        if r["median_close"] is not None:
            r["median_close"] = round(r["median_close"], 10)
    sha = hashlib.sha256(SPEC.read_bytes()).hexdigest()
    return {"spec_sha256": sha, "spec_sha256_matches_frozen": sha == SPEC_SHA, "window": "2022-11-01..2023-10-31",
            "generated_pdt": now_pdt(), "generated_by": "reports/stage_e32b_briefs/work/F3/f3_vol.py",
            "units": "h, OC, overnight, R_d, main_range_median in ticks of the code's own tick (after any OC-1 "
                     "transfer); tick_size and median_close in exchange price units as rules/products.py "
                     "(USD per unit, index points, or points of par)",
            "files_opened": files, "roots": roots}


def pct(a, b) -> float | None:
    if a is None or b is None or b == 0:
        return None
    return round(100.0 * (a - b) / b, 4)


def regression(owned: list[str]) -> dict:
    a0 = {r["root"]: r for r in json.loads(A0_JSON.read_text())["roots"]}
    rows = {}
    for code in owned:
        pt, r = json.loads((PARTS / f"{code}.json").read_text()), a0.get(code)
        if r is None:
            continue
        rows[code] = {
            "n_dates": [pt["n_dates"], r["n_trade_dates"]],
            "early_halt_lists_equal": pt["early_halt_dates_excluded"] == r["early_halt_dates_excluded"],
            "sigma_1m_A0_convention": [pt["diag_a0_sigma_1m"], r["sigma_1m_ticks"],
                                       pct(pt["diag_a0_sigma_1m"], r["sigma_1m_ticks"])],
            "n_changes_A0_convention": [pt["diag_a0_n_changes"], r["sigma_1m_n_changes"]],
            "sigma_1_spec": [pt["h"]["1"]["sigma"], r["sigma_1m_ticks"], pct(pt["h"]["1"]["sigma"],
                                                                            r["sigma_1m_ticks"])],
            "n_1_spec": [pt["h"]["1"]["n"], r["sigma_1m_n_changes"]],
            "R_d_median": [pt["R_d"]["median"], r["R_d_median_ticks"], pct(pt["R_d"]["median"],
                                                                         r["R_d_median_ticks"])],
            "first_trade_date": [pt["first_trade_date"], r.get("window_first_trade_date")],
            "trade_dates_all": [pt["trade_dates_all"], r.get("window_trade_dates_all")],
        }
    return {"generated_pdt": now_pdt(), "compared_with": str(A0_JSON.relative_to(REPO)),
            "format": "[F3, A0, percent difference]", "roots": rows}


def main() -> None:
    os.nice(10)
    t0 = time.time()
    guard = BarGuard(REPO, HERE / "opens.log")
    owned = owned_codes(guard)
    print(f"{now_pdt()} start; owned codes ({len(owned)}): {' '.join(owned)}", flush=True)
    only = sys.argv[1:]
    if only:  # probe: compute the named owned roots' parts only, no assembly
        run_parts(guard, [c for c in owned if c in only])
        print(f"{now_pdt()} probe done; peak RSS {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024:.0f} MB")
        return
    run_parts(guard, owned)
    out = assemble(owned)
    OUT_JSON.write_text(json.dumps(out, indent=1))
    REG_JSON.write_text(json.dumps(regression(owned), indent=1))
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
    counts = {s: sum(r["status"] == s for r in out["roots"].values()) for s in ("owned", "OC1", "unknown")}
    print(f"{now_pdt()} wrote {OUT_JSON.relative_to(REPO)} {counts}; files opened this run {len(guard.opened)}; "
          f"total {time.time() - t0:.0f}s; peak RSS {rss:.0f} MB", flush=True)


if __name__ == "__main__":
    main()
