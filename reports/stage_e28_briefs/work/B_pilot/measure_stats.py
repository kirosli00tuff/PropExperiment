"""Spec section 4: per-cell statistics, the Kaplan-Meier fill curve and the day-block bootstrap.

Cells: placement type (T, I) x session (MAIN, OVERNIGHT), buy and sell pooled, and each side
separately. Also per cell (review fixes): fills by trigger and the trigger trade's aggressor
side (RS-04), the stale-placement share (RS-06), the share of fills whose headline markout was
dropped, and the no-drop markout variant with its net mean and VPO (RS-05).
Per cell and fill rule: placements, fills (inside the life, which includes the 50 ms cancel
latency after j + 60 s; those late fills are also counted on their own), the fill rate,
the Kaplan-Meier curve of time to fill from j with censoring at 60 s (P(fill by 1, 10, 60 s)
and the median), the touch rate, and among fills per horizon h: the mean, median and share of
positive markouts, the mean net markout (markout - FEE_SIDE) and VPO_h = fill rate x (mean
markout_h - FEE_SIDE) for h = 10 and 60 s. Frozen spec section 0: net markouts are also
reported at a second, conservative fee per side (QM: 0.296 tick = 3.70 USD / 12.50 beside the
primary 0.1368); ``fee_side_alt`` adds, per fee, the mean net markout and VPO (headline and
no-drop variants) under ``mean_net_alt`` / ``vpo_alt`` / ``vpo_nodrop_alt``, keyed by the fee.

Confidence intervals: 95% percentile intervals of a day-block bootstrap: trade dates drawn with
replacement, 2,000 replicates, numpy default_rng(28); ONE draw matrix (replicates x days) is
shared by every cell, side, rule and statistic, so all intervals come from the same resampled
day sets. A replicate whose denominator is 0 gives NaN and is left out (``boot_valid`` counts
the rest). Labels (spec 3): "positive" if the lower bound is above 0, "negative" if the upper
bound is below 0, else "not distinguishable from 0". No interval is computed for medians.
"""
# ruff: noqa: I001 - pilot_common is imported first on purpose (sys.path)

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Any

import numpy as np

from measure_core import NONE, TYPES
from pilot_common import HORIZONS_S, NS, SESSIONS

BOOT_REPLICATES = 2000
BOOT_SEED = 28
KM_CENSOR_S = 60.0
KM_POINTS_S = (1, 10, 60)
VPO_HORIZONS_S = (10, 60)
SIDE_LABELS = (("pooled", 0), ("buy", 1), ("sell", -1))
POSITIVE, NEGATIVE, NOT_DIST = "positive", "negative", "not distinguishable from 0"


# ------------------------------------------------------------------ Kaplan-Meier ----
def kaplan_meier(durations: np.ndarray, events: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Event times and the survival S(t) just after each (product-limit estimator). At a time
    with both events and censorings, events are counted first (the usual convention)."""
    d = np.asarray(durations, dtype=float)
    e = np.asarray(events, dtype=bool)
    times = np.unique(d[e])
    surv, s = [], 1.0
    for t in times:
        at_risk = int(np.count_nonzero(d >= t))
        deaths = int(np.count_nonzero((d == t) & e))
        s *= 1.0 - deaths / at_risk
        surv.append(s)
    return times, np.array(surv, dtype=float)


def km_cdf(times: np.ndarray, surv: np.ndarray, t: float) -> float:
    """1 - S(t): the fill probability by time t."""
    k = int(np.searchsorted(times, t, side="right")) - 1
    return 0.0 if k < 0 else float(1.0 - surv[k])


def km_median(times: np.ndarray, surv: np.ndarray) -> float | None:
    hit = np.flatnonzero(surv <= 0.5)
    return float(times[hit[0]]) if len(hit) else None


def km_inputs(ttf_s: np.ndarray, filled: np.ndarray,
              censor_s: float = KM_CENSOR_S) -> tuple[np.ndarray, np.ndarray]:
    """Durations and events with censoring at ``censor_s``: a non-fill, and a fill after it
    (inside the cancel latency), is censored there."""
    event = filled & (ttf_s <= censor_s)
    return np.where(event, ttf_s, censor_s), event


# ------------------------------------------------------------------ bootstrap ----
def bootstrap_weights(n_days: int, replicates: int = BOOT_REPLICATES,
                      seed: int = BOOT_SEED) -> np.ndarray:
    """W[r, d] = how often trade date d is drawn in replicate r."""
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, n_days, size=(replicates, n_days))
    w = np.zeros((replicates, n_days), dtype=np.int64)
    np.add.at(w, (np.repeat(np.arange(replicates), n_days), draws.ravel()), 1)
    return w


def _ratio(num: np.ndarray, den: np.ndarray) -> np.ndarray:
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(den > 0, num / np.where(den > 0, den, 1), np.nan)


def interval(point: float, boot: np.ndarray, *, label: bool = False) -> dict[str, Any]:
    finite = boot[np.isfinite(boot)]
    lo, hi = (float(np.percentile(finite, 2.5)), float(np.percentile(finite, 97.5))) \
        if len(finite) else (None, None)
    out: dict[str, Any] = {"value": None if not np.isfinite(point) else float(point),
                           "ci95": [lo, hi], "boot_valid": int(len(finite))}
    if label:
        out["label"] = classify(lo, hi)
    return out


def classify(lo: float | None, hi: float | None) -> str | None:
    if lo is None or hi is None:
        return None
    if lo > 0:
        return POSITIVE
    if hi < 0:
        return NEGATIVE
    return NOT_DIST


def ratio_stat(num_d: np.ndarray, den_d: np.ndarray, w: np.ndarray, *,
               label: bool = False) -> dict[str, Any]:
    point = float(_ratio(np.array([num_d.sum()]), np.array([den_d.sum()]))[0])
    return interval(point, _ratio(w @ num_d, w @ den_d), label=label)


# ------------------------------------------------------------------ orders table ----
_FLOAT_KEY = re.compile(r"[mn]\d+")
_OBJECT_KEYS = ("trigger", "trigger_side")


def order_table(days: Sequence[dict[str, Any]], rules: Sequence[str],
                horizons: Sequence[int] = HORIZONS_S) -> dict[str, np.ndarray]:
    """Flat arrays over the orders of the included day files (day index = position in days)."""
    keys = ("type", "session", "side", "j_ns", "touch_ns", "stale")
    cols: dict[str, list[Any]] = {"day": [], **{k: [] for k in keys}}
    rule_keys = ["fill_ns", *_OBJECT_KEYS, *[f"{p}{h}" for h in horizons
                                             for p in ("m", "drop", "n", "ndrop")]]
    rule_cols = {r: {k: [] for k in rule_keys} for r in rules}
    for i, day in enumerate(days):
        orders = day["orders"]
        cols["day"].extend([i] * len(orders["type"]))
        for key in keys:
            cols[key].extend(orders[key])
        for r in rules:
            for key, values in rule_cols[r].items():
                values.extend(orders["rules"][r][key])
    out: dict[str, Any] = {}
    for k, v in cols.items():
        if k in ("type", "session"):
            out[k] = np.array(v, dtype=object)
        elif k == "stale":  # 1 stale, 0 not, -1 unknown
            out[k] = np.array([-1 if x is None else int(bool(x)) for x in v], dtype=np.int64)
        else:
            out[k] = np.array(v, dtype=np.int64)
    for r in rules:
        for key, values in rule_cols[r].items():
            if _FLOAT_KEY.fullmatch(key):
                out[f"{r}:{key}"] = np.array([np.nan if x is None else x for x in values],
                                             dtype=float)
            elif key == "fill_ns":
                out[f"{r}:{key}"] = np.array(values, dtype=np.int64)
            else:
                out[f"{r}:{key}"] = np.array(values, dtype=object)
    return out


def _by_day(day: np.ndarray, mask: np.ndarray, n_days: int,
            weights: np.ndarray | None = None) -> np.ndarray:
    w = None if weights is None else weights[mask]
    return np.bincount(day[mask], weights=w, minlength=n_days).astype(float)


def fee_key(fee: float) -> str:
    """The JSON key of a fee per side in ticks (0.296 -> "0.296")."""
    return f"{fee:g}"


def cell_stats(tab: dict[str, np.ndarray], mask: np.ndarray, rule: str, n_days: int,
               w: np.ndarray, fee_side: float, horizons: Sequence[int] = HORIZONS_S,
               fee_side_alt: Sequence[float] = ()) -> dict[str, Any]:
    day = tab["day"]
    fill_ns = tab[f"{rule}:fill_ns"]
    filled = mask & (fill_ns != NONE)
    ttf = np.where(fill_ns != NONE, (fill_ns - tab["j_ns"]) / NS, np.inf)
    touched = mask & (tab["touch_ns"] != NONE)
    n_d = _by_day(day, mask, n_days)
    fill_d = _by_day(day, filled, n_days)
    out: dict[str, Any] = {
        "placements": int(n_d.sum()), "fills": int(fill_d.sum()),
        "fills_in_cancel_latency": int(np.count_nonzero(filled & (ttf > KM_CENSOR_S))),
        "fill_rate": ratio_stat(fill_d, n_d, w),
        "touch_rate": ratio_stat(_by_day(day, touched, n_days), n_d, w)}
    times, surv = kaplan_meier(*km_inputs(ttf[mask], filled[mask]))
    km: dict[str, Any] = {"median_ttf_s": km_median(times, surv), "censor_s": KM_CENSOR_S}
    for t in KM_POINTS_S:
        stat = ratio_stat(_by_day(day, filled & (ttf <= t), n_days), n_d, w)
        stat["value"] = km_cdf(times, surv, float(t)) if mask.any() else None
        km[f"p_fill_by_{t}s"] = stat
    out["km"] = km
    out["fills_by_trigger"] = _trigger_counts(tab, filled, rule)
    known = mask & (tab["stale"] >= 0)
    out["stale_share"] = ratio_stat(_by_day(day, known & (tab["stale"] == 1), n_days),
                                    _by_day(day, known, n_days), w)
    for key, prefix in (("markouts", "m"), ("markouts_nodrop", "n")):
        out[key] = {str(h): _markout_stats(tab, filled, rule, h, n_days, w, fee_side, prefix,
                                           fee_side_alt)
                    for h in horizons}
    for key, prefix in (("vpo", "m"), ("vpo_nodrop", "n")):
        out[key] = {str(h): _vpo(tab, filled, n_d, fill_d, rule, h, n_days, w, fee_side, prefix)
                    for h in VPO_HORIZONS_S if h in horizons}
        if fee_side_alt:
            out[f"{key}_alt"] = {
                fee_key(fee): {str(h): _vpo(tab, filled, n_d, fill_d, rule, h, n_days, w, fee,
                                            prefix)
                               for h in VPO_HORIZONS_S if h in horizons}
                for fee in fee_side_alt}
    return out


def _trigger_counts(tab: dict[str, np.ndarray], filled: np.ndarray, rule: str) -> dict[str, int]:
    """Fills by trigger (queue, through, at, quote) and the trigger trade's aggressor side."""
    pairs = zip(tab[f"{rule}:trigger"][filled], tab[f"{rule}:trigger_side"][filled],
                strict=True)
    out: dict[str, int] = {}
    for trig, side in pairs:
        key = f"{trig}/{side or '-'}"
        out[key] = out.get(key, 0) + 1
    return dict(sorted(out.items()))


def _markout_stats(tab: dict[str, np.ndarray], filled: np.ndarray, rule: str, h: int,
                   n_days: int, w: np.ndarray, fee_side: float,
                   prefix: str = "m", fee_side_alt: Sequence[float] = ()) -> dict[str, Any]:
    """``prefix`` "m": the headline markouts; "n": the no-drop variant (RS-05).
    ``fee_side_alt``: further fees per side at which the mean net markout is also given."""
    m = tab[f"{rule}:{prefix}{h}"]
    ok = filled & np.isfinite(m)
    cnt_d = _by_day(tab["day"], ok, n_days)
    sum_d = _by_day(tab["day"], ok, n_days, np.where(np.isfinite(m), m, 0.0))
    pos_d = _by_day(tab["day"], ok & (m > 0), n_days)
    mean = ratio_stat(sum_d, cnt_d, w, label=True)
    boot_mean = _ratio(w @ sum_d, w @ cnt_d)
    net_point = np.nan if mean["value"] is None else mean["value"] - fee_side
    dropped = filled & ~np.isfinite(m)
    drop_key = "drop" if prefix == "m" else "ndrop"
    drops = tab[f"{rule}:{drop_key}{h}"][dropped]
    reasons, counts = np.unique(drops.astype(str), return_counts=True) if len(drops) else ([], [])
    out = {"n": int(cnt_d.sum()), "dropped": {str(r): int(c) for r, c in zip(reasons, counts,
                                                                                strict=True)},
           "dropped_share": ratio_stat(_by_day(tab["day"], dropped, n_days),
                                       _by_day(tab["day"], filled, n_days), w),
           "mean": mean, "median": float(np.median(m[ok])) if ok.any() else None,
           "share_positive": ratio_stat(pos_d, cnt_d, w),
           "mean_net": interval(net_point, boot_mean - fee_side, label=True)}
    if fee_side_alt:
        point = np.nan if mean["value"] is None else mean["value"]
        out["mean_net_alt"] = {fee_key(fee): interval(point - fee, boot_mean - fee, label=True)
                               for fee in fee_side_alt}
    return out


def _vpo(tab: dict[str, np.ndarray], filled: np.ndarray, n_d: np.ndarray, fill_d: np.ndarray,
         rule: str, h: int, n_days: int, w: np.ndarray, fee_side: float,
         prefix: str = "m") -> dict[str, Any]:
    m = tab[f"{rule}:{prefix}{h}"]
    ok = filled & np.isfinite(m)
    cnt_d = _by_day(tab["day"], ok, n_days)
    sum_d = _by_day(tab["day"], ok, n_days, np.where(np.isfinite(m), m, 0.0))
    point = _vpo_values(np.array([fill_d.sum()]), np.array([n_d.sum()]),
                        np.array([sum_d.sum()]), np.array([cnt_d.sum()]), fee_side)[0]
    boot = _vpo_values(w @ fill_d, w @ n_d, w @ sum_d, w @ cnt_d, fee_side)
    return interval(point, boot, label=True)


def _vpo_values(fills: np.ndarray, n: np.ndarray, m_sum: np.ndarray, m_cnt: np.ndarray,
                fee_side: float) -> np.ndarray:
    """fill rate x (mean markout - fee); 0 where there are placements but no fill (an order
    that never fills earns nothing); NaN with no placements, or fills whose markouts were all
    dropped."""
    vpo = _ratio(fills, n) * (_ratio(m_sum, m_cnt) - fee_side)
    return np.where((n > 0) & (fills == 0), 0.0, vpo)


def all_cells(tab: dict[str, np.ndarray], rules: Sequence[str], n_days: int, fee_side: float,
              horizons: Sequence[int] = HORIZONS_S,
              fee_side_alt: Sequence[float] = ()) -> dict[str, Any]:
    w = bootstrap_weights(n_days) if n_days > 0 else np.zeros((BOOT_REPLICATES, 0))
    out: dict[str, Any] = {}
    for rule in rules:
        per_rule: dict[str, Any] = {}
        for kind in TYPES:
            for session in SESSIONS:
                base = (tab["type"] == kind) & (tab["session"] == session)
                per_rule[f"{kind}|{session}"] = {
                    label: cell_stats(tab, base if side == 0 else base & (tab["side"] == side),
                                      rule, n_days, w, fee_side, horizons, fee_side_alt)
                    for label, side in SIDE_LABELS}
        out[rule] = per_rule
    return out


# ------------------------------------------------------------------ markdown ----
def _fmt(stat: dict[str, Any] | None, digits: int = 4) -> str:
    if stat is None or stat.get("value") is None:
        return "n/a"
    lo, hi = stat["ci95"]
    ci = "" if lo is None else f" [{lo:.{digits}f}, {hi:.{digits}f}]"
    tag = f" {stat['label']}" if stat.get("label") else ""
    return f"{stat['value']:.{digits}f}{ci}{tag}"


def _rows(cell: dict[str, Any]) -> list[tuple[str, list[str]]]:
    sides = [cell[label] for label, _ in SIDE_LABELS]
    rows = [("placements", [str(s["placements"]) for s in sides]),
            ("fills (of which in cancel latency)",
             [f"{s['fills']} ({s['fills_in_cancel_latency']})" for s in sides]),
            ("fills by trigger/aggressor", [", ".join(f"{k} {v}" for k, v in
                                                      s["fills_by_trigger"].items()) or "none"
                                            for s in sides]),
            ("fill rate", [_fmt(s["fill_rate"]) for s in sides]),
            ("touch rate", [_fmt(s["touch_rate"]) for s in sides]),
            ("stale share (best price at g differs from j)",
             [_fmt(s["stale_share"]) for s in sides])]
    for t in KM_POINTS_S:
        rows.append((f"KM P(fill by {t} s)", [_fmt(s["km"][f"p_fill_by_{t}s"]) for s in sides]))
    rows.append(("KM median time to fill (s)",
                 ["not reached" if s["km"]["median_ttf_s"] is None
                  else f"{s['km']['median_ttf_s']:.3f}" for s in sides]))
    for h in sides[0]["markouts"]:
        rows.append((f"markouts {h} s: n (dropped)",
                     [f"{s['markouts'][h]['n']} ({sum(s['markouts'][h]['dropped'].values())})"
                      for s in sides]))
        rows.append((f"mean markout {h} s (ticks)",
                     [_fmt(s["markouts"][h]["mean"]) for s in sides]))
        rows.append((f"median markout {h} s", ["n/a" if s["markouts"][h]["median"] is None else
                                               f"{s['markouts'][h]['median']:.4f}" for s in sides]))
        rows.append((f"share positive {h} s", [_fmt(s["markouts"][h]["share_positive"])
                                               for s in sides]))
        rows.append((f"mean NET markout {h} s", [_fmt(s["markouts"][h]["mean_net"])
                                                 for s in sides]))
        for fee in sides[0]["markouts"][h].get("mean_net_alt", {}):
            rows.append((f"mean NET markout {h} s at fee {fee} tick/side",
                         [_fmt(s["markouts"][h]["mean_net_alt"][fee]) for s in sides]))
        rows.append((f"dropped share {h} s (of fills)",
                     [_fmt(s["markouts"][h]["dropped_share"]) for s in sides]))
        nd = [s["markouts_nodrop"][h] for s in sides]
        rows.append((f"no-drop variant {h} s: n (dropped)",
                     [f"{x['n']} ({sum(x['dropped'].values())})" for x in nd]))
        rows.append((f"no-drop mean markout {h} s", [_fmt(x["mean"]) for x in nd]))
        rows.append((f"no-drop mean NET markout {h} s", [_fmt(x["mean_net"]) for x in nd]))
        for fee in nd[0].get("mean_net_alt", {}):
            rows.append((f"no-drop mean NET markout {h} s at fee {fee} tick/side",
                         [_fmt(x["mean_net_alt"][fee]) for x in nd]))
    for h in sides[0]["vpo"]:
        rows.append((f"VPO {h} s (ticks per resting order)", [_fmt(s["vpo"][h]) for s in sides]))
        rows.append((f"no-drop VPO {h} s", [_fmt(s["vpo_nodrop"][h]) for s in sides]))
        for fee in sides[0].get("vpo_alt", {}):
            rows.append((f"VPO {h} s at fee {fee} tick/side",
                         [_fmt(s["vpo_alt"][fee][h]) for s in sides]))
            rows.append((f"no-drop VPO {h} s at fee {fee} tick/side",
                         [_fmt(s["vpo_nodrop_alt"][fee][h]) for s in sides]))
    return rows


def render_cells_markdown(results: dict[str, Any]) -> str:
    lines: list[str] = []
    for rule, cells in results.items():
        lines.append(f"## Fill rule: {rule}\n")
        for cell_name, cell in cells.items():
            lines.append(f"### Cell {cell_name} (rule {rule})\n")
            lines.append("| statistic | pooled | buy | sell |")
            lines.append("|---|---|---|---|")
            lines.extend(f"| {name} | {' | '.join(vals)} |" for name, vals in _rows(cell))
            lines.append("")
    return "\n".join(lines) + "\n"
