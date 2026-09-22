"""Stage D.1d Task 3: Family G stylized facts at 5, 15, 30 and 60-minute bars.

Implements ONLY reports/stage_d1d_timeframe_declaration.md sections 3-5 (sha256
07a906328a2aae2097ae30ea02e5b547cf37247245e1cd91b63808809619c745): five declared event
statistics (G1-G5) at four timeframes, M = 28 tested statistics, plus the descriptive G0
continuity check against Family F's F1.1. No strategy, no entries, no P&L, no backtest.

    uv run python -m strategy.research.g_timeframe._stylized_facts

One workstream per timeframe (a forked process each), writing its own full result set to
reports/stage_d1d_family_g_facts_<tf>m.json; the lead then merges the four, applies
Benjamini-Hochberg once across all 28, applies the declared selection rule, and writes
reports/stage_d1d_family_g_facts.json. The inference (day-block bootstrap, CI, p, sub-block
agreement) is Family F's ``compute_result``, imported and called as is.

Implementation choices, logged rather than hidden:
- A day's segment layout (ETH end, RTH end) comes from the ``limit`` of its own-day bars
  (session minute >= 420); a date with no own-day bars has no RTH segment.
- Slot arrays are nominal length (ETH 930/tf, RTH 390/tf) with absent slots as NaN, so a
  slot past an early close is simply absent and can never supply a forward move.
- G3's P_end is the close of the last 1-minute bar opening before the RTH segment end.
- G4's VWAP at slot j is over all RTH 1-minute bars opening before slot j's end.
- Trailing same-slot baselines (G1, G4) are the nanmean over the previous 20 EDA dates of
  that slot's measure, requiring >= 10 of them present; EDA dates 1-20 are warm-up.
- Q80 is the 80th percentile (numpy linear interpolation) of the relative measure pooled
  over all defined observations of that (fact, segment, tf); frozen thereafter.
- |t| for ranking is estimate / std of the 2,000 bootstrap replicates (the same seed and
  draws as the CI); it is not a separate test.
"""

from __future__ import annotations

import hashlib
import json
import math
import multiprocessing as mp
from dataclasses import dataclass
from datetime import date

import numpy as np
import pandas as pd

from data.config import REPO_ROOT
from strategy.research.f_data_native._stylized_facts import (
    DayObs,
    TestedStat,
    _sanitize,
    bh_flags,
    bootstrap_replicates,
    compute_result,
    pearson_r,
    resolve_eda_dates,
    split_equal,
)
from strategy.research.g_timeframe.resample import (
    DEFAULT_LIMIT,
    ETH_NOMINAL_END,
    MIDNIGHT_SESSION_MINUTE,
    RTH_NOMINAL_END,
    RTH_START,
    SEGMENTS,
    TICK,
    TIMEFRAMES,
    annotate_session,
    coarse_bars,
    missing_minute_share,
)

DECLARATION_PATH = REPO_ROOT / "reports" / "stage_d1d_timeframe_declaration.md"
DECL_SHA256 = "07a906328a2aae2097ae30ea02e5b547cf37247245e1cd91b63808809619c745"
F_FACTS_PATH = REPO_ROOT / "reports" / "stage_d1b_family_f_facts.json"
OUTPUT_PATH = REPO_ROOT / "reports" / "stage_d1d_family_g_facts.json"
BASELINE_DAYS = 20
MIN_BASELINE_OBS = 10
TOP_QUANTILE = 0.80
BH_Q = 0.10
M_STATS = 28
COST_BAR_TICKS = 2.11  # $2.64 modelled market round turn at $1.25 per tick
MIN_EVENTS = 30
MIN_SUBBLOCKS_AGREE = 3
FORMALIZATION_CAP = 8
INELIGIBLE = frozenset({"G1.RTH.5", "G1.ETH.5", "G3.RTH.5"})  # the re-tests' own grid
_NOMINAL_SLOTS = {"ETH": ETH_NOMINAL_END, "RTH": RTH_NOMINAL_END - RTH_START}


def per_tf_path(tf: int):
    return REPO_ROOT / "reports" / f"stage_d1d_family_g_facts_{tf}m.json"


# ============================================================================= data ====
@dataclass(frozen=True)
class DayData:
    obs_date: date
    seg: dict[str, dict[str, np.ndarray]]  # segment -> open/high/low/close/volume/present/end
    rth_end: int | None
    p_end: float | None
    eth_high: float | None
    eth_low: float | None
    vwap: np.ndarray  # per RTH slot, NaN where undefined


def _segment_arrays(coarse_day: pd.DataFrame, tf: int) -> dict[str, dict[str, np.ndarray]]:
    out = {}
    for segment in SEGMENTS:
        n = _NOMINAL_SLOTS[segment] // tf
        arrays = {k: np.full(n, np.nan) for k in ("open", "high", "low", "close", "volume")}
        arrays["present"] = np.zeros(n, dtype=bool)
        start = 0 if segment == "ETH" else RTH_START
        arrays["end"] = start + (np.arange(n) + 1) * tf
        rows = coarse_day[coarse_day["segment"] == segment]
        idx = rows["slot"].to_numpy(dtype=int)
        for k in ("open", "high", "low", "close", "volume"):
            arrays[k][idx] = rows[k].to_numpy(dtype=float)
        arrays["present"][idx] = True
        out[segment] = arrays
    return out


def _vwap_at_slot_ends(rth_bars: pd.DataFrame, ends: np.ndarray) -> np.ndarray:
    if not len(rth_bars):
        return np.full(len(ends), np.nan)
    sm = rth_bars["session_minute"].to_numpy()
    typical = (rth_bars["high"] + rth_bars["low"] + rth_bars["close"]).to_numpy() / 3.0
    volume = rth_bars["volume"].to_numpy(dtype=float)
    cum_tv, cum_v = np.cumsum(typical * volume), np.cumsum(volume)
    k = np.searchsorted(sm, ends, side="left")  # bars opening before each slot end
    out = np.full(len(ends), np.nan)
    ok = k > 0
    out[ok] = np.where(cum_v[k[ok] - 1] > 0, cum_tv[k[ok] - 1] / cum_v[k[ok] - 1], np.nan)
    return out


def build_days(bars: pd.DataFrame, coarse: pd.DataFrame, tf: int,
               eda_dates: list[date]) -> list[DayData]:
    by_date = {d: g for d, g in bars.groupby("trade_date_obj", sort=True)}
    coarse_by_date = {d: g for d, g in coarse.groupby("trade_date", sort=True)}
    empty = coarse.iloc[0:0]
    days = []
    for d in eda_dates:
        g = by_date[d]
        own = g[g["session_minute"] >= MIDNIGHT_SESSION_MINUTE]
        limit = int(own["limit"].iloc[0]) if len(own) else DEFAULT_LIMIT
        eth_end = min(ETH_NOMINAL_END, limit)
        rth_end = min(RTH_NOMINAL_END, limit) if len(own) else None
        seg = _segment_arrays(coarse_by_date.get(d, empty), tf)
        eth = g[g["session_minute"] < eth_end]
        rth = g[(g["session_minute"] >= RTH_START) & (g["session_minute"] < (rth_end or 0))]
        days.append(DayData(
            d, seg, rth_end if rth_end and rth_end > RTH_START else None,
            float(rth["close"].iloc[-1]) if len(rth) else None,
            float(eth["high"].max()) if len(eth) else None,
            float(eth["low"].min()) if len(eth) else None,
            _vwap_at_slot_ends(rth, seg["RTH"]["end"]),
        ))
    return days


# ======================================================================= statistics ====
def _forward(close: np.ndarray, present: np.ndarray, j: int) -> float | None:
    if j + 1 < len(close) and present[j + 1]:
        return float((close[j + 1] - close[j]) / TICK)
    return None


def _trailing_baseline(measure: np.ndarray, i: int) -> np.ndarray:
    """Per-slot nanmean over rows i-20..i-1, NaN where fewer than 10 are present."""
    window = measure[i - BASELINE_DAYS:i]
    counts = np.sum(~np.isnan(window), axis=0)
    with np.errstate(invalid="ignore"):
        means = np.where(counts > 0, np.nansum(window, axis=0) / np.maximum(counts, 1), np.nan)
    return np.where(counts >= MIN_BASELINE_OBS, means, np.nan)


def _relative_events(days: list[DayData], segment: str, measure_fn) -> tuple[list[DayObs], float]:
    """G1/G4 shared machinery: signed measure per slot -> relative size -> Q80 events."""
    signed = np.array([measure_fn(d) for d in days])  # (n_days, n_slots), NaN where absent
    absolute = np.abs(signed)
    rel = np.full_like(signed, np.nan)
    for i in range(BASELINE_DAYS, len(days)):
        baseline = _trailing_baseline(absolute, i)
        with np.errstate(invalid="ignore", divide="ignore"):
            rel[i] = np.where(baseline > 0, absolute[i] / baseline, np.nan)
    pooled = rel[np.isfinite(rel)]
    q80 = float(np.percentile(pooled, TOP_QUANTILE * 100)) if len(pooled) else math.nan
    obs = []
    for i in range(BASELINE_DAYS, len(days)):
        d = days[i]
        close, present = d.seg[segment]["close"], d.seg[segment]["present"]
        xs = []
        for j in np.flatnonzero(np.isfinite(rel[i])):
            if rel[i, j] < q80 or signed[i, j] == 0:
                continue
            fwd = _forward(close, present, j)
            if fwd is not None:
                xs.append(np.sign(signed[i, j]) * fwd)
        obs.append(DayObs(d.obs_date, {"x": np.asarray(xs, dtype=float)}))
    return obs, q80


def g1_body(segment: str):
    def measure(d: DayData) -> np.ndarray:
        s = d.seg[segment]
        return np.where(s["present"], s["close"] - s["open"], np.nan)
    return measure


def g4_vwap_deviation(d: DayData) -> np.ndarray:
    s = d.seg["RTH"]
    with np.errstate(invalid="ignore"):
        return np.where(s["present"] & np.isfinite(d.vwap), (s["close"] - d.vwap) / TICK, np.nan)


def g2_events(days: list[DayData], segment: str) -> list[DayObs]:
    obs = []
    for d in days:
        s = d.seg[segment]
        xs, run_high, run_low = [], -math.inf, math.inf
        for j in np.flatnonzero(s["present"]):
            if run_high > -math.inf:
                close = s["close"][j]
                direction = 1 if close > run_high else (-1 if close < run_low else 0)
                fwd = _forward(s["close"], s["present"], j) if direction else None
                if fwd is not None:
                    xs.append(direction * fwd)
            run_high, run_low = max(run_high, s["high"][j]), min(run_low, s["low"][j])
        obs.append(DayObs(d.obs_date, {"x": np.asarray(xs, dtype=float)}))
    return obs


def g3_events(days: list[DayData]) -> list[DayObs]:
    obs = []
    for d in days:
        s = d.seg["RTH"]
        xs = []
        if s["present"][0] and d.p_end is not None and d.rth_end is not None:
            or_high, or_low = s["high"][0], s["low"][0]
            for j in np.flatnonzero(s["present"])[1:]:
                direction = 1 if s["close"][j] > or_high else (-1 if s["close"][j] < or_low else 0)
                if not direction:
                    continue
                if s["end"][j] < d.rth_end:
                    xs.append(direction * (d.p_end - s["close"][j]) / TICK)
                break
        obs.append(DayObs(d.obs_date, {"x": np.asarray(xs, dtype=float)}))
    return obs


def g5_events(days: list[DayData]) -> list[DayObs]:
    obs = []
    for d in days:
        s = d.seg["RTH"]
        xs = []
        if d.eth_high is not None:
            for direction, hit in ((1, s["close"] > d.eth_high), (-1, s["close"] < d.eth_low)):
                firsts = np.flatnonzero(s["present"] & hit)
                if len(firsts):
                    fwd = _forward(s["close"], s["present"], int(firsts[0]))
                    if fwd is not None:
                        xs.append(direction * fwd)
        obs.append(DayObs(d.obs_date, {"x": np.asarray(xs, dtype=float)}))
    return obs


def g0_autocorrelation(days: list[DayData], segment: str) -> dict:
    first, second = [], []
    for d in days:
        s = d.seg[segment]
        close, present = s["close"], s["present"]
        with np.errstate(invalid="ignore", divide="ignore"):
            r = np.where(present[1:] & present[:-1], np.log(close[1:] / close[:-1]), np.nan)
        pair = np.isfinite(r[1:]) & np.isfinite(r[:-1])
        first.extend(r[:-1][pair])
        second.extend(r[1:][pair])
    x, y = np.asarray(first), np.asarray(second)
    return {"segment": segment, "n_pairs": int(len(x)), "lag1_autocorrelation": pearson_r(x, y)}


def _mean_x(p: dict[str, np.ndarray]) -> float:
    return float(np.mean(p["x"])) if len(p["x"]) else math.nan


def _tested(stat_id: str, description: str, obs: list[DayObs]) -> TestedStat:
    return TestedStat(id=stat_id, family="G", description=description, directional=True,
                      null=0.0, days=obs, keys=("x",), estimate_fn=_mean_x,
                      n_fn=lambda p: int(len(p["x"])), edge_equals_estimate=True)


def build_statistics(days: list[DayData], tf: int) -> tuple[list[TestedStat], dict[str, float]]:
    stats, q80s = [], {}
    for segment in SEGMENTS:
        obs, q80 = _relative_events(days, segment, g1_body(segment))
        sid = f"G1.{segment}.{tf}"
        q80s[sid] = q80
        stats.append(_tested(sid, f"large-body follow-through, {segment}, {tf}-min bars: "
                             "sign(body) x next-bar move, ticks, |body| >= Q80 of its "
                             "trailing same-slot relative size", obs))
        stats.append(_tested(f"G2.{segment}.{tf}", f"session-extreme breakout, {segment}, "
                             f"{tf}-min bars: close beyond the segment's earlier high/low, "
                             "signed next-bar move, ticks", g2_events(days, segment)))
    stats.append(_tested(f"G3.RTH.{tf}", f"opening-range breakout, RTH, {tf}-min bars: first "
                         "close beyond slot 0's range, signed move to the RTH end, ticks",
                         g3_events(days)))
    obs, q80 = _relative_events(days, "RTH", g4_vwap_deviation)
    q80s[f"G4.RTH.{tf}"] = q80
    stats.append(_tested(f"G4.RTH.{tf}", f"VWAP deviation, RTH, {tf}-min bars: sign(close - "
                         "VWAP) x next-bar move, ticks, |deviation| >= Q80 of its trailing "
                         "same-slot relative size (negative = reversion)", obs))
    stats.append(_tested(f"G5.RTH.{tf}", f"overnight-range break, RTH, {tf}-min bars: first "
                         "close beyond the ETH high/low, signed next-bar move, ticks",
                         g5_events(days)))
    return stats, q80s


# ======================================================================== workstream ====
def _subblock_map(eda_dates: list[date]) -> tuple[dict[date, int], list[int]]:
    sizes = split_equal(len(eda_dates), 4)
    mapping, pos = {}, 0
    for b, size in enumerate(sizes):
        for d in eda_dates[pos:pos + size]:
            mapping[d] = b
        pos += size
    return mapping, sizes


def run_timeframe(tf: int) -> dict:
    """One workstream: every declared statistic at this timeframe, written to its own file."""
    eda_dates, excluded, bars = resolve_eda_dates()
    bars = annotate_session(bars)
    bars["trade_date_obj"] = pd.to_datetime(bars["trade_date"].astype(str)).dt.date
    coarse = coarse_bars(bars, tf)
    days = build_days(bars, coarse, tf, eda_dates)
    subblock_map, sizes = _subblock_map(eda_dates)
    stats, q80s = build_statistics(days, tf)
    records = []
    for stat in stats:
        record = compute_result(stat, subblock_map)
        reps = bootstrap_replicates(stat)
        sd = float(np.std(reps)) if len(reps) > 1 else math.nan
        est = record["estimate"]
        record.update({
            "tf": tf, "segment": stat.id.split(".")[1], "fact": stat.id.split(".")[0],
            "n_events": record["n"], "q80": q80s.get(stat.id),
            "t_boot": (est / sd) if est is not None and sd and sd > 0 else None,
            "eligible": stat.id not in INELIGIBLE,
        })
        records.append(record)
    out = {
        "meta": {"declaration_sha256": DECL_SHA256, "tf": tf,
                 "n_eda_dates": len(eda_dates), "excluded_dates": excluded,
                 "sub_block_sizes": sizes,
                 "missing_minute_share": missing_minute_share(coarse, tf),
                 "n_coarse_bars": {s: int((coarse["segment"] == s).sum()) for s in SEGMENTS}},
        "g0_descriptive": [g0_autocorrelation(days, s) for s in SEGMENTS],
        "tested_statistics": records,
    }
    per_tf_path(tf).write_text(json.dumps(_sanitize(out), indent=2))
    return out


# ========================================================================= selection ====
def _reject_reason(r: dict) -> str | None:
    if not r["eligible"]:
        return "ineligible by declaration (the re-tests' own mechanism and grid)"
    if not r["bh_reject"]:
        return f"not BH-significant at FDR 10% across M={M_STATS} (p={r['p_boot']})"
    if r["sub_block_sign_agree"] < MIN_SUBBLOCKS_AGREE:
        return f"sign agrees in only {r['sub_block_sign_agree']}/4 sub-blocks"
    if r["estimate"] is None or abs(r["estimate"]) < COST_BAR_TICKS:
        return f"|edge| {abs(r['estimate'] or 0):.2f} ticks < {COST_BAR_TICKS} cost bar"
    if r["n_events"] < MIN_EVENTS:
        return f"only {r['n_events']} events < {MIN_EVENTS}"
    return None


def select(records: list[dict]) -> dict:
    bh_flags(records, BH_Q)
    decisions = []
    for r in records:
        reason = _reject_reason(r)
        r["selection"] = "qualifies" if reason is None else reason
        decisions.append(r)
    qualifiers = [r for r in decisions if r["selection"] == "qualifies"]
    qualifiers.sort(key=lambda r: -abs(r["t_boot"] or 0) * abs(r["estimate"] or 0))
    formalized = qualifiers[:FORMALIZATION_CAP]
    return {"n_bh_significant": sum(1 for r in records if r["bh_reject"]),
            "qualifiers": [r["id"] for r in qualifiers],
            "formalized": [r["id"] for r in formalized],
            "cap": FORMALIZATION_CAP}


def _g0_vs_f11(per_tf: list[dict]) -> list[dict]:
    f = {r["id"]: r for r in json.loads(F_FACTS_PATH.read_text())["tested_statistics"]}
    rows = []
    for out in per_tf:
        tf = out["meta"]["tf"]
        for g in out["g0_descriptive"]:
            ref = f.get(f"F1_1_h{tf}_{g['segment']}")
            rows.append({"tf": tf, **g, "f1_1_estimate": ref["estimate"] if ref else None,
                         "f1_1_n": ref["n"] if ref else None})
    return rows


def main() -> None:
    actual = hashlib.sha256(DECLARATION_PATH.read_bytes()).hexdigest()
    if actual != DECL_SHA256:
        raise SystemExit(f"declaration hash {actual} != {DECL_SHA256}: the list is closed")
    with mp.get_context("fork").Pool(processes=len(TIMEFRAMES)) as pool:
        per_tf = pool.map(run_timeframe, TIMEFRAMES, chunksize=1)
    records = [r for out in per_tf for r in out["tested_statistics"]]
    if len(records) != M_STATS:
        raise AssertionError(f"expected {M_STATS} tested statistics, got {len(records)}")
    selection = select(records)
    out = {
        "meta": {"declaration_sha256": DECL_SHA256, "timeframes": list(TIMEFRAMES),
                 "m_tested_statistics": M_STATS, "bh_fdr_q": BH_Q,
                 "cost_bar_ticks": COST_BAR_TICKS, "per_timeframe_files":
                 [str(per_tf_path(tf).relative_to(REPO_ROOT)) for tf in TIMEFRAMES],
                 "per_timeframe_meta": [o["meta"] for o in per_tf]},
        "g0_vs_family_f_f1_1": _g0_vs_f11(per_tf),
        "tested_statistics": records,
        "selection": selection,
    }
    OUTPUT_PATH.write_text(json.dumps(_sanitize(out), indent=2))
    print(f"wrote {OUTPUT_PATH}: {len(records)} statistics, "
          f"{selection['n_bh_significant']} BH-significant, "
          f"{len(selection['qualifiers'])} qualify, {len(selection['formalized'])} formalized")
    for r in sorted(records, key=lambda r: (r['p_boot'] if r['p_boot'] is not None else 1.0)):
        print(f"  {r['id']:<12} n={r['n_events']:>5} edge={r['estimate']!s:>8} "
              f"p={r['p_boot']} agree={r['sub_block_sign_agree']}/4 -> {r['selection']}")


if __name__ == "__main__":
    main()
