"""Stage E.32b F3: volatility statistics at horizons (spec section 2.2 and 2.3). Pure functions, no file access.

Trade dates, scheduled grid, main session and EARLY_HALT handling are copied from E.28's
reports/stage_e28_briefs/work/A0/A0_stats.py (trade_dates, session_spec, scheduled_minutes, pt_minutes,
early_halt_days). Prices and the tick are passed in the same units (the driver passes vendor fixed-point integers
as float64 and the vendor tick in the same units, so every change is an exact multiple of a tick).

Volatility statistics only: SD, mean |x|, median |x|, p99 |x| and counts. Nothing signed or conditional.
"""
from __future__ import annotations

import importlib
from datetime import date, timedelta

import numpy as np
import pandas as pd

HORIZONS: tuple[int, ...] = (1, 2, 5, 15, 30, 60, 120, 240)
MAIN_PT: tuple[int, int] = (6 * 60 + 30, 13 * 60)  # [06:30, 13:00) America/Vancouver, minutes after midnight
NS_MIN = 60_000_000_000
EMPTY = np.array([], dtype="float64")


# ---- copied from E.28 A0 (unchanged logic) -------------------------------------------------------------------
def trade_dates(ts: np.ndarray) -> np.ndarray:
    """CME trade date: CT time >= 17:00 belongs to the next day; Sat/Sun roll to Monday."""
    ct = pd.to_datetime(ts.astype("int64"), utc=True).tz_convert("America/Chicago")
    days = ct.tz_localize(None).normalize().values.astype("datetime64[D]")
    days = days + (ct.hour.values >= 17).astype("int64")
    wd = (days.astype("int64") + 3) % 7  # Monday = 0
    days = days + np.where(wd == 5, 2, np.where(wd == 6, 1, 0))
    return days


def session_spec(group: str, day: date):
    mod = importlib.import_module(f"data.calendars.{group}")
    for s in mod.SESSIONS:
        if s.valid_from <= day and (s.valid_to is None or day <= s.valid_to):
            return s
    raise LookupError(f"no session spec for {group} {day}")


def scheduled_minutes(group: str, day: date) -> np.ndarray:
    """UTC ns of every scheduled minute start of trade date ``day`` (CT segments)."""
    spec = session_spec(group, day)
    out = []
    for seg in spec.segments:
        s = pd.Timestamp.combine(day + timedelta(days=seg.start_offset_days), seg.start_ct)
        e = pd.Timestamp.combine(day + timedelta(days=seg.end_offset_days), seg.end_ct)
        s = s.tz_localize("America/Chicago").tz_convert("UTC").value
        e = e.tz_localize("America/Chicago").tz_convert("UTC").value
        out.append(np.arange(s, e, NS_MIN, dtype="int64"))
    return np.concatenate(out)


def pt_minutes(ns: np.ndarray) -> np.ndarray:
    pt = pd.to_datetime(ns, utc=True).tz_convert("America/Vancouver")
    return pt.hour.values * 60 + pt.minute.values


def calendar_module(group: str) -> str:
    return "data.cme_calendar" if group == "equity" else f"data.calendars.{group}"


def early_halt_days(group: str) -> set:
    """EARLY_HALT dates of the group's calendar (holiday sessions and business early closes)."""
    mod = importlib.import_module(calendar_module(group))
    return {d for d, h in mod.HOLIDAYS.items() if h.kind.name == "EARLY_HALT"}


# ---- F3 -------------------------------------------------------------------------------------------------------
def main_session_from_calendar(group: str, day: date) -> tuple[int, list[str]]:
    """L_main and [start, end) in PT from the group's scheduled grid on a regular trade date."""
    grid = scheduled_minutes(group, day)
    ptm = pt_minutes(grid)
    sel = (ptm >= MAIN_PT[0]) & (ptm < MAIN_PT[1])
    first, last = int(ptm[sel][0]), int(ptm[sel][-1]) + 1
    return int(sel.sum()), [f"{first // 60:02d}:{first % 60:02d}", f"{last // 60:02d}:{last % 60:02d}"]


def day_record(group: str, day: date, ts: np.ndarray, close: np.ndarray, hi: np.ndarray, lo: np.ndarray,
               inst: np.ndarray, tick: float) -> dict:
    """One trade date's raw pieces. ``ts`` sorted ascending; all arrays are that trade date's bars only."""
    dom = inst == inst[-1]  # R_d: the instrument traded in the day's last bar (E.28 definition)
    rec = {"rng": float((hi[dom].max() - lo[dom].min()) / tick), "D": {h: EMPTY for h in HORIZONS},
           "a0_md": EMPTY, "oc": None, "first": None, "last": None, "main_rng": None, "n_main": 0}
    grid = scheduled_minutes(group, day)
    grid = grid[(grid >= ts[0]) & (grid <= ts[-1])]  # cut to the day's first and last bar (early closes)
    if grid.size == 0:
        return rec
    pos = np.searchsorted(ts, grid, side="right") - 1  # last bar at or before the minute (carry forward)
    has = pos >= 0
    p0 = np.maximum(pos, 0)
    gclose = np.where(has, close[p0], np.nan)
    ginst = np.where(has, inst[p0], -1)
    is_main = (lambda m: (m >= MAIN_PT[0]) & (m < MAIN_PT[1]))(pt_minutes(grid))
    # A0's sigma_1m convention (change ending at a main minute), kept only for the regression check
    step = np.diff(grid) == NS_MIN
    same = (ginst[1:] == ginst[:-1]) & (ginst[1:] >= 0)
    ok = step & same & is_main[1:] & ~np.isnan(gclose[:-1])
    rec["a0_md"] = ((gclose[1:] - gclose[:-1]) / tick)[ok]
    mi = np.nonzero(is_main)[0]
    rec["n_main"] = int(mi.size)
    if mi.size == 0:
        return rec
    gm = grid[mi]
    for h in HORIZONS:  # D_h(t) = close(t+h) - close(t), t and t+h both main grid minutes of this trade date
        tgt = gm + h * NS_MIN
        j = np.searchsorted(gm, tgt)
        jc = np.minimum(j, gm.size - 1)
        hit = (j < gm.size) & (gm[jc] == tgt)
        a, b = mi[hit], mi[jc[hit]]
        okh = (ginst[a] == ginst[b]) & (ginst[a] >= 0)
        rec["D"][h] = (gclose[b[okh]] - gclose[a[okh]]) / tick
    f, last = mi[0], mi[-1]
    if ginst[f] >= 0:
        rec["first"] = (float(gclose[f]), int(ginst[f]))
    if ginst[last] >= 0:
        rec["last"] = (float(gclose[last]), int(ginst[last]))
    if rec["first"] and rec["last"] and rec["first"][1] == rec["last"][1]:
        rec["oc"] = float((gclose[last] - gclose[f]) / tick)
    bm = np.isin(ts, gm)  # actual bars starting on a main grid minute
    if bm.any():
        sel = bm & (inst == inst[bm][-1])
        rec["main_rng"] = float((hi[sel].max() - lo[sel].min()) / tick)
    return rec


def summarize(x: np.ndarray, full: bool = True) -> dict:
    """sigma (SD, ddof 1), m (mean |x|), and with ``full`` median |x| and p99 |x|; n = count."""
    x = np.asarray(x, dtype="float64")
    n = int(x.size)
    ax = np.abs(x)
    out = {"sigma": float(np.std(x, ddof=1)) if n > 1 else None, "m": float(ax.mean()) if n else None}
    if full:
        out["median_abs"] = float(np.median(ax)) if n else None
        out["p99_abs"] = float(np.percentile(ax, 99)) if n else None
    out["n"] = n
    return out


def overnight_changes(dated: list[tuple[date, dict]], excluded: set) -> dict:
    """cc and on between consecutive sample trade dates (regular dates; excluded dates are not in ``dated``)."""
    valid = [(d, r) for d, r in dated if r["first"] is not None and r["last"] is not None]
    cc, on, spans = [], [], 0
    for (d0, r0), (d1, r1) in zip(valid, valid[1:]):
        crossed = any(d0 < x < d1 for x in excluded)
        used = False
        if r0["last"][1] == r1["last"][1]:
            cc.append(r1["last"][0] - r0["last"][0])
            used = True
        if r0["last"][1] == r1["first"][1]:
            on.append(r1["first"][0] - r0["last"][0])
            used = True
        spans += int(crossed and used)
    return {"cc": np.array(cc, dtype="float64"), "on": np.array(on, dtype="float64"), "pairs_span_excluded": spans}


def aggregate(dated: list[tuple[date, dict]], excluded: set, tick: float, price_to_exchange: float) -> dict:
    """Root statistics over regular trade dates. Overnight changes are converted to ticks with ``tick``."""
    recs = [r for _, r in dated]
    h_out = {}
    for h in HORIZONS:
        x = np.concatenate([r["D"][h] for r in recs]) if recs else EMPTY
        h_out[str(h)] = summarize(x)
    oc = np.array([r["oc"] for r in recs if r["oc"] is not None], dtype="float64")
    ov = overnight_changes(dated, excluded)
    rng = np.array([r["rng"] for r in recs], dtype="float64")
    mrng = np.array([r["main_rng"] for r in recs if r["main_rng"] is not None], dtype="float64")
    closes = np.array([r["last"][0] for r in recs if r["last"] is not None], dtype="float64")
    a0 = np.concatenate([r["a0_md"] for r in recs]) if recs else EMPTY
    n_main = [r["n_main"] for r in recs if r["n_main"]]
    return {
        "n_dates": len(recs),
        "h": h_out,
        "OC": summarize(oc, full=False),
        "overnight": {"cc": summarize(ov["cc"] / tick, full=False), "on": summarize(ov["on"] / tick, full=False)},
        "overnight_pairs_span_excluded_date": ov["pairs_span_excluded"],
        "R_d": {"median": float(np.median(rng)) if rng.size else None,
                "p99": float(np.percentile(rng, 99)) if rng.size else None, "n": int(rng.size)},
        "main_range_median": float(np.median(mrng)) if mrng.size else None,
        "median_close": float(np.median(closes) * price_to_exchange) if closes.size else None,
        "diag_a0_sigma_1m": float(np.std(a0, ddof=1)) if a0.size > 1 else None,
        "diag_a0_n_changes": int(a0.size),
        "diag_main_minutes_mode": int(pd.Series(n_main).mode().iloc[0]) if n_main else None,
    }


TICK_FIELDS_H = ("sigma", "m", "median_abs", "p99_abs")


def transfer_oc1(src: dict, factor: float) -> dict:
    """OC-1: the sibling's tick statistics times (sibling tick / own tick). Counts and prices are not scaled."""
    def scale(v):
        return None if v is None else v * factor

    h = {k: {**{f: scale(v[f]) for f in TICK_FIELDS_H}, "n": v["n"]} for k, v in src["h"].items()}
    oc = {"sigma": scale(src["OC"]["sigma"]), "m": scale(src["OC"]["m"]), "n": src["OC"]["n"]}
    ov = {k: {"sigma": scale(v["sigma"]), "m": scale(v["m"]), "n": v["n"]} for k, v in src["overnight"].items()}
    rd = {"median": scale(src["R_d"]["median"]), "p99": scale(src["R_d"]["p99"]), "n": src["R_d"]["n"]}
    return {"n_dates": src["n_dates"], "h": h, "OC": oc, "overnight": ov, "R_d": rd,
            "main_range_median": scale(src["main_range_median"]), "median_close": src["median_close"]}
