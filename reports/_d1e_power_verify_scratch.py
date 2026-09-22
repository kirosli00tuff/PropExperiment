"""SCRATCH: independent recomputation behind reports/stage_d1e_power_verification.md.

Stage D.1e Task 3b verification worker (fable, xhigh). This file is scratch: it is
kept so the verification can be re-run, it is not part of the pipeline and nothing
imports it.

It does NOT import strategy.research._d1e_power, _d1e_power_stats,
_d1e_power_report or _d1e_calendar. The only project import is
funnel.null_generator.stationary_bootstrap_indices, because the program's own
inference uses it and the point is to check the power code's use of it.

Run:
    uv run python reports/_d1e_power_verify_scratch.py            # deterministic part
    uv run python reports/_d1e_power_verify_scratch.py --sim      # + re-simulation (4 procs)
    uv run python reports/_d1e_power_verify_scratch.py --sim --procs 2 --reps 2000

Everything is printed as markdown to stdout; nothing is written to disk.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:  # so pool workers can import funnel.null_generator
    sys.path.insert(0, str(ROOT))
POWER_JSON = ROOT / "reports/stage_d1e_power.json"
POWER_MD = ROOT / "reports/stage_d1e_power.md"
TRIALS_JSON = ROOT / "reports/stage_d1e_members_trials.json"
EVENTS_JSON = ROOT / "reports/stage_d1e_members_events.json"
GATE_JSON = ROOT / "reports/power_gate.json"
GATE_EXT_JSON = ROOT / "reports/stage_d1e_gate_extension.json"

USD_PER_TICK_2_MICROS = 2.5
TICK_USD_1_MICRO = 1.25
COST_TICKS_MARKET = 2.11
COST_TICKS_PASSIVE = 0.98
HOLM_M = 58
ALPHA = 0.05
MEAN_BLOCK = 5.0
RENEWAL_P = 1.0 / MEAN_BLOCK
K_MAX = 20
VIF_FLOOR = 0.2
END_DATE = date(2024, 2, 29)
STARTS = [
    date(2019, 5, 6),
    date(2019, 7, 1),
    date(2020, 1, 2),
    date(2021, 1, 4),
    date(2022, 1, 3),
    date(2023, 1, 3),
]
HOLDOUT2 = (date(2024, 4, 1), date(2025, 3, 31))
# Degraded dates read from reports/stage_d1e_quotes.md section 1 (Databento
# dataset condition, 2019-04-01..2025-04-01).
DEGRADED = [
    date(2020, 2, 27),
    date(2020, 2, 28),
    date(2020, 5, 5),
    date(2020, 6, 30),
    date(2020, 7, 1),
    date(2021, 12, 5),
    date(2022, 1, 2),
    date(2024, 9, 18),
]
# Family H proxy rule, reports/stage_d1e_coverage.md section 5.
# V1: the first issue of the map (per-trade SD 100 / 115, read off the half-scale table).
# V2: after the unit correction (Task 5d review, finding R-1): 200 / 230.
_H_F = [
    ("H1 NR4 opening-range breakout", 0.25 * 0.9),
    ("H2 NR7 opening-range breakout", (1.0 / 7.0) * 0.9),
    ("H3 inside-day opening-range breakout", 0.25 * 0.9),
    ("H4 bottom-tercile prior range, breakout", (1.0 / 3.0) * 0.9),
    ("H5 top-tercile prior range, opening-range fade", (1.0 / 3.0) * 0.9),
    ("H6 prior-close location follow-through", 0.4),
]
FAMILY_H_V1 = [(n, 115.0 if n.startswith("H6") else 100.0, f) for n, f in _H_F]
FAMILY_H_V2 = [(n, 230.0 if n.startswith("H6") else 200.0, f) for n, f in _H_F]
FAMILY_H = FAMILY_H_V1
SNAPSHOT_DEFAULT = (
    "/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/"
    "fbadc349-fea7-48e6-b228-64f8d81e2cc2/lead-scratch/power_eps34_micros2_SNAPSHOT.json"
)


# ------------------------------------------------------------------ helpers ---
def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def norm_ppf(p: float) -> float:
    """Phi^-1 by Newton on math.erfc (independent of statistics.NormalDist)."""
    if not 0.0 < p < 1.0:
        raise ValueError(p)
    # Acklam-style crude start, then Newton to machine precision.
    z = math.sqrt(2.0) * _erfinv_crude(2.0 * p - 1.0)
    for _ in range(60):
        cdf = 0.5 * math.erfc(-z / math.sqrt(2.0))
        pdf = math.exp(-0.5 * z * z) / math.sqrt(2.0 * math.pi)
        step = (cdf - p) / pdf
        z -= step
        if abs(step) < 1e-16:
            break
    return z


def _erfinv_crude(x: float) -> float:
    # Winitzki approximation; only a starting point for Newton.
    a = 0.147
    ln = math.log(1.0 - x * x)
    t = 2.0 / (math.pi * a) + ln / 2.0
    return math.copysign(math.sqrt(math.sqrt(t * t - ln / a) - t), x)


def rel(a: float, b: float) -> float:
    """(recomputed - reported) / reported, in percent; inf-safe."""
    if b == 0:
        return 0.0 if a == 0 else float("inf")
    return 100.0 * (a - b) / b


def autocov(x: np.ndarray, k: int) -> float:
    n = len(x)
    c = x - x.mean()
    if k >= n:
        return 0.0
    return float(np.dot(c[: n - k], c[k:]) / n)


def vif_boot(x: np.ndarray) -> tuple[float, bool]:
    g0 = autocov(x, 0)
    if g0 <= 0:
        return 1.0, False
    s = g0 + 2.0 * sum(((1.0 - RENEWAL_P) ** k) * autocov(x, k) for k in range(1, K_MAX + 1))
    vif = s / g0
    if vif < VIF_FLOOR:
        return VIF_FLOOR, True
    return vif, False


def lag1(x: np.ndarray) -> float:
    g0 = autocov(x, 0)
    return autocov(x, 1) / g0 if g0 > 0 else 0.0


def n_days(z_level: float, z_b: float, sd: float, vif: float, eps: float) -> int:
    return int(math.ceil((((z_level + z_b) * sd * math.sqrt(vif)) / eps) ** 2))


def eps_min(z_level: float, z_b: float, sd: float, vif: float, n: int) -> float:
    return (z_level + z_b) * sd * math.sqrt(vif) / math.sqrt(n)


# ----------------------------------------------------------------- calendar ---
def easter(year: int) -> date:
    """Anonymous Gregorian algorithm (Meeus/Jones/Butcher)."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    d = date(year, month, 1)
    d += timedelta(days=(weekday - d.weekday()) % 7)
    return d + timedelta(weeks=n - 1)


def last_weekday(year: int, month: int, weekday: int) -> date:
    d = date(year, month + 1, 1) - timedelta(days=1) if month < 12 else date(year, 12, 31)
    return d - timedelta(days=(d.weekday() - weekday) % 7)


def observed(d: date) -> date | None:
    """Sunday -> Monday; Saturday -> no weekday closure (the stated rule)."""
    if d.weekday() == 6:
        return d + timedelta(days=1)
    if d.weekday() == 5:
        return None
    return d


def cme_full_closures(year: int, rule: str = "stated") -> set[date]:
    """rule='stated': the ten full-closure holidays of the brief.
    rule='pipeline': only the closures data/cme_calendar.py treats as FULL_CLOSURE
    (Good Friday, Christmas, New Year's); the other US holidays are early-halt
    trade dates there."""
    fixed = [observed(date(year, 1, 1)), observed(date(year, 12, 25)), easter(year) - timedelta(days=2)]
    if rule == "pipeline":
        return {d for d in fixed if d is not None}
    more = [
        nth_weekday(year, 1, 0, 3),  # MLK
        nth_weekday(year, 2, 0, 3),  # Presidents
        last_weekday(year, 5, 0),  # Memorial
        observed(date(year, 7, 4)),  # Independence
        nth_weekday(year, 9, 0, 1),  # Labor
        nth_weekday(year, 11, 3, 4),  # Thanksgiving
    ]
    if year >= 2022:
        more.append(observed(date(year, 6, 19)))  # Juneteenth from 2022
    return {d for d in fixed + more if d is not None}


def weekday_open_dates(start: date, end: date, rule: str = "stated") -> list[date]:
    closures = set()
    for y in range(start.year, end.year + 1):
        closures |= cme_full_closures(y, rule)
    d, out = start, []
    while d <= end:
        if d.weekday() < 5 and d not in closures:
            out.append(d)
        d += timedelta(days=1)
    return out


def quarterly_rolls(start: date, end: date) -> int:
    """Number of quarterly roll events (Mar/Jun/Sep/Dec) whose roll date falls in
    [start, end]. The MES volume roll happens about a week before the third
    Friday; we count the third Friday minus 7 days as the roll date."""
    n = 0
    for y in range(start.year, end.year + 1):
        for m in (3, 6, 9, 12):
            third_friday = nth_weekday(y, m, 4, 3)
            roll = third_friday - timedelta(days=7)
            if start <= roll <= end:
                n += 1
    return n


def supplied_days(start: date, end: date, rule: str = "stated") -> dict:
    opens = weekday_open_dates(start, end, rule)
    open_set = set(opens)
    rolls = quarterly_rolls(start, end)
    months = (end.year - start.year) * 12 + (end.month - start.month) + 1
    degraded_in_range = [d for d in DEGRADED if start <= d <= end]
    degraded_weekday_open = [d for d in degraded_in_range if d in open_set]
    return {
        "weekday_open_dates": len(opens),
        "rolls_exact": rolls,
        "blackout_exact": 3 * rolls,
        "blackout_pro_rata_months": months,  # 3 per 3 months = months
        "degraded_in_range": len(degraded_in_range),
        "degraded_weekday_open": len(degraded_weekday_open),
        "degraded_dates": [d.isoformat() for d in degraded_in_range],
        "days_exact": len(opens) - 3 * rolls - len(degraded_weekday_open),
        "days_stated_method": len(opens) - months - len(degraded_in_range),
    }


# ------------------------------------------------------------------ epsilon ---
def epsilon_cells() -> dict:
    gate = json.loads(GATE_JSON.read_text())
    ext = json.loads(GATE_EXT_JSON.read_text())
    cost_usd = {int(k): float(v) for k, v in gate["mean_round_turn_cost_usd_per_micro_by_segments"].items()}
    cells = []
    for r in gate["rows"]:
        T = int(r["segments_per_day"])
        rt_ticks = cost_usd[T] / TICK_USD_1_MICRO
        net_t = r["expected_gross_edge_ticks_per_trade_per_micro"] - rt_ticks
        cells.append(
            {
                "file": "power_gate.json",
                "path": r["path"],
                "T": T,
                "p": r["win_probability"],
                "R": r["win_loss_ratio"],
                "net_ticks_trade": net_t,
                "net_usd_day": net_t * T * 2 * TICK_USD_1_MICRO,
                "verdict": r["robust_c80_verdict"],
                "power": r["robust_c80_power"],
                "lower95": r["robust_c80_power_lower95"],
            }
        )
    ext_mismatch = 0
    for r in ext["rows"]:
        T = int(r["segments_per_day"])
        net_t = r["expected_gross_edge_ticks_per_trade_per_micro"] - r["rt_cost_ticks"]
        usd = net_t * T * 2 * TICK_USD_1_MICRO
        if abs(usd - r["net_edge_usd_per_day_at_2_micros"]) > 1e-6:
            ext_mismatch += 1
        cells.append(
            {
                "file": "stage_d1e_gate_extension.json",
                "path": r["path"],
                "T": T,
                "p": r["win_probability"],
                "R": r["win_loss_ratio"],
                "net_ticks_trade": net_t,
                "net_usd_day": usd,
                "verdict": r["robust_c80_verdict"],
                "power": r["robust_c80_power"],
                "lower95": r["robust_c80_power_lower95"],
            }
        )
    passing = sorted((c for c in cells if c["verdict"] == "pass"), key=lambda c: c["net_usd_day"])
    marginal = sorted((c for c in cells if c["verdict"] == "marginal"), key=lambda c: c["net_usd_day"])
    # verdict rule re-check: pass iff lower95 >= 0.80; marginal iff power >= 0.80
    rule_bad = [
        c
        for c in cells
        if (c["verdict"] == "pass") != (c["lower95"] >= 0.80 - 1e-12)
        or (c["verdict"] == "marginal") != (c["lower95"] < 0.80 - 1e-12 and c["power"] >= 0.80 - 1e-12)
    ]
    eps_exact = passing[0]["net_usd_day"] / USD_PER_TICK_2_MICROS
    ext_meta = ext["meta"]
    return {
        "ext_version": {
            "generated_utc": ext_meta.get("generated_utc"),
            "rows": len(ext["rows"]),
            "T_values": sorted(set(int(r["segments_per_day"]) for r in ext["rows"])),
            "verdicts": {v: sum(1 for r in ext["rows"] if r["robust_c80_verdict"] == v) for v in ("pass", "marginal", "fail")},
            "smallest_pass_by_T": {
                T: min((c["net_usd_day"] for c in cells if c["file"] != "power_gate.json" and c["T"] == T and c["verdict"] == "pass"), default=None)
                for T in sorted(set(int(r["segments_per_day"]) for r in ext["rows"]))
            },
        },
        "grid_rows": len(gate["rows"]),
        "n_cells": len(cells),
        "n_pass": len(passing),
        "n_marginal": len(marginal),
        "ext_net_usd_mismatch": ext_mismatch,
        "verdict_rule_violations": rule_bad,
        "smallest_pass": passing[:5],
        "smallest_marginal": marginal[:3],
        "largest_fail": sorted((c for c in cells if c["verdict"] == "fail"), key=lambda c: -c["net_usd_day"])[:3],
        "eps_exact_ticks_day": eps_exact,
        "eps_day": math.floor(eps_exact),
        "cost_ticks_by_T": {T: v / TICK_USD_1_MICRO for T, v in cost_usd.items()},
    }


# ------------------------------------------------------------------ members ---
def per_micro_series_from_trips(rec: dict) -> np.ndarray:
    """Rebuild daily net ticks per micro from the trip lists: trips are in date
    order and daily_n_trips says how many close on each date; each trip is
    divided by its OWN quantity, trip_pnl_usd / (1.25 x trip_micros)."""
    pnl = np.asarray(rec["trip_pnls_usd"], dtype=float)
    q = np.asarray(rec["trip_micros"], dtype=float)
    counts = np.asarray(rec["daily_n_trips"], dtype=int)
    if counts.sum() != len(pnl) or len(q) != len(pnl):
        raise ValueError(f"trip bookkeeping mismatch: {counts.sum()} vs {len(pnl)} vs {len(q)}")
    per_trip = pnl / (TICK_USD_1_MICRO * q)
    bounds = np.concatenate([[0], np.cumsum(counts)])
    return np.array([per_trip[bounds[i] : bounds[i + 1]].sum() for i in range(len(counts))])


def load_members(v2: bool = False) -> list[dict]:
    """Build every member's daily series independently of the code under test.

    v2 (after the unit correction): the trial series is the file's
    daily_net_ticks_per_micro, checked against a rebuild from the trip lists and
    against daily_net_usd / 1.25 (the 1-micro reading)."""
    trials = json.loads(TRIALS_JSON.read_text())
    events = json.loads(EVENTS_JSON.read_text())
    out = []
    for name, rec in trials["members"].items():
        trips = np.asarray(rec["daily_n_trips"], dtype=float)
        usd = np.asarray(rec["daily_net_usd"], dtype=float)
        if v2:
            d = np.asarray(rec["daily_net_ticks_per_micro"], dtype=float)
            extra = {
                "series_from_trips": per_micro_series_from_trips(rec),
                "series_usd_over_1p25": usd / TICK_USD_1_MICRO,
                "series_usd_over_2p5": usd / USD_PER_TICK_2_MICROS,
                "trip_micros": np.asarray(rec["trip_micros"], dtype=float),
                "coded_micros": rec.get("coded_micros"),
                "mean_trip_micros_file": rec.get("mean_trip_micros"),
                "per_day_per_micro_sd_file": (rec.get("per_day_per_micro") or {}).get("sd_ticks_per_micro"),
                "per_trade_sd_ticks": (rec.get("per_trade_per_micro") or rec["per_trade"])["sd_ticks_per_micro"],
            }
        else:
            d = usd / USD_PER_TICK_2_MICROS
            extra = {"per_trade_sd_ticks": rec["per_trade"]["sd_ticks_per_micro"]}
        out.append(
            {
                "id": name,
                "kind": "trial",
                "series": d,
                "r": float(trips.sum() / len(d)),
                "r_alt": rec["trades_per_day"],
                "n_window": len(d),
                **extra,
            }
        )
    for group in ("statistics", "coverage_statistics"):
        for name, rec in events[group].items():
            s = int(rec["recorded_direction"])
            sums = np.asarray(rec["daily_sum_ticks"], dtype=float)
            cnt = np.asarray(rec["daily_count"], dtype=float)
            d = s * sums - COST_TICKS_MARKET * cnt
            out.append(
                {
                    "id": name,
                    "kind": "statistic",
                    "series": d,
                    "r": float(cnt.sum() / len(d)),
                    "r_alt": rec["events_per_eda_day"],
                    "n_window": len(d),
                    "n_events": rec["n_events"],
                }
            )
    return out


def compute_member(m: dict, z: dict, eps: float, supplied: dict[str, int]) -> dict:
    d = m["series"]
    sd = float(np.std(d, ddof=1))
    vif, floored = vif_boot(d)
    res = {
        "id": m["id"],
        "kind": m["kind"],
        "r": m["r"],
        "sd_day": sd,
        "lag1": lag1(d),
        "vif_boot": vif,
        "floored": floored,
        "eps_trade": eps / m["r"],
        "n_a": n_days(z["a"], z["b"], sd, vif, eps),
        "n_b": n_days(z["95"], z["b"], sd, vif, eps),
        "n_a_exact": (((z["a"] + z["b"]) * sd * math.sqrt(vif)) / eps) ** 2,
        "n_b_exact": (((z["95"] + z["b"]) * sd * math.sqrt(vif)) / eps) ** 2,
        "eps_min": {
            S: {
                "per_day": eps_min(z["95"], z["b"], sd, vif, N),
                "per_trade": eps_min(z["95"], z["b"], sd, vif, N) / m["r"],
            }
            for S, N in supplied.items()
        },
        "eps_ref": {
            "eps_day_ref": m["r"] * 1.0,
            "n_a": n_days(z["a"], z["b"], sd, vif, m["r"] * 1.0),
            "n_b": n_days(z["95"], z["b"], sd, vif, m["r"] * 1.0),
        },
        "n_b_sens": {str(int(e)): n_days(z["95"], z["b"], sd, vif, float(e)) for e in (30, 32, 34, 36, 38, 40)},
    }
    if m["kind"] == "trial":
        var_trade = m["per_trade_sd_ticks"] ** 2
        res["cluster_vif"] = sd**2 / (m["r"] * var_trade) if var_trade > 0 else None
    return res


def compute_projected(name: str, sd_trade: float, f: float, z: dict, eps: float, supplied: dict[str, int]) -> dict:
    sd = sd_trade * math.sqrt(f)
    vif = 1.0
    return {
        "id": name,
        "kind": "projected",
        "r": f,
        "sd_day": sd,
        "lag1": 0.0,
        "vif_boot": vif,
        "floored": False,
        "eps_trade": eps / f,
        "n_a": n_days(z["a"], z["b"], sd, vif, eps),
        "n_b": n_days(z["95"], z["b"], sd, vif, eps),
        "n_a_exact": (((z["a"] + z["b"]) * sd) / eps) ** 2,
        "n_b_exact": (((z["95"] + z["b"]) * sd) / eps) ** 2,
        "eps_min": {
            S: {"per_day": eps_min(z["95"], z["b"], sd, vif, N), "per_trade": eps_min(z["95"], z["b"], sd, vif, N) / f}
            for S, N in supplied.items()
        },
        "eps_ref": {
            "eps_day_ref": f,
            "n_a": n_days(z["a"], z["b"], sd, vif, f),
            "n_b": n_days(z["95"], z["b"], sd, vif, f),
        },
        "n_b_sens": {str(int(e)): n_days(z["95"], z["b"], sd, vif, float(e)) for e in (30, 32, 34, 36, 38, 40)},
    }


# --------------------------------------------------------------- simulation ---
def simulate_member(args: tuple) -> dict:
    """Re-simulate power curves for one member with my own seed.

    Design (lead): stationary bootstrap resamples of the centred series at length n,
    shifted by eps (a) or 0 (b); SE_hat = sqrt(var(x, ddof=1) * VIF_source / n);
    reject (a) if mean/SE > z_a; success (b) if mean + z_95 SE < eps.
    """
    from funnel.null_generator import stationary_bootstrap_indices  # program's own function

    name, series, vif_source, eps, z_a, z_95, grid, reps, seed = args
    c = np.asarray(series, dtype=float)
    c = c - c.mean()
    n_src = len(c)
    curve = {}
    zero_var_total = 0
    for j, n in enumerate(grid):
        rng = np.random.default_rng([seed, j, n])
        idx = np.empty((reps, n), dtype=np.int64)
        for rep in range(reps):
            idx[rep] = stationary_bootstrap_indices(rng, n_src, n, MEAN_BLOCK)
        x = c[idx]
        g0 = x.var(axis=1, ddof=1)
        se = np.sqrt(g0 * vif_source / n)
        mean_b = x.mean(axis=1)
        zero = se == 0.0
        zero_var_total += int(zero.sum())
        # arm b: null true (shift 0): success if UCB95 < eps
        succ_b = mean_b + z_95 * se < eps
        # arm a: shift eps: reject if mean/SE > z_a; SE == 0 with mean > 0 -> +inf -> reject
        mean_a = mean_b + eps
        with np.errstate(divide="ignore", invalid="ignore"):
            t_a = np.where(zero, np.where(mean_a > 0, np.inf, -np.inf), mean_a / se)
        rej_a = t_a > z_a
        pa, pb = float(rej_a.mean()), float(succ_b.mean())
        curve[n] = {
            "power_a": pa,
            "se_a": math.sqrt(pa * (1 - pa) / reps),
            "power_b": pb,
            "se_b": math.sqrt(pb * (1 - pb) / reps),
            "zero_var": int(zero.sum()),
        }
    return {"id": name, "curve": curve, "zero_var_total": zero_var_total, "grid": list(grid)}


def cross(curve: dict, arm: str, target: float = 0.80) -> tuple[float | None, bool, float | None]:
    """Log-linear interpolation of the first crossing of `target`.
    Returns (n_cross, censored_below_grid, mc_se_of_n)."""
    ns = sorted(curve)
    ps = [curve[n][f"power_{arm}"] for n in ns]
    ses = [curve[n][f"se_{arm}"] for n in ns]
    if ps[0] >= target:
        return float(ns[0]), True, None
    for i in range(1, len(ns)):
        if ps[i - 1] < target <= ps[i]:
            lo, hi = ns[i - 1], ns[i]
            frac = (target - ps[i - 1]) / (ps[i] - ps[i - 1])
            n_cross = math.exp(math.log(lo) + frac * (math.log(hi) - math.log(lo)))
            slope = (ps[i] - ps[i - 1]) / (math.log(hi) - math.log(lo))  # d power / d ln n
            se_p = math.sqrt(max(ses[i - 1], ses[i]) ** 2)  # conservative: the larger of the two
            se_n = n_cross * se_p / slope if slope > 0 else None
            return n_cross, False, se_n
    return None, False, None


def chosen_rule(analytic: int, sim: float | None, censored: bool) -> tuple[int, float | None, list[str], str]:
    """The lead's chosen-figure rule (correction 1), arm-agnostic."""
    if sim is None:
        return analytic, None, [], "no_crossing"
    diff = 100.0 * (sim - analytic) / analytic
    if censored:
        return analytic, diff, ["censored"], "censored"
    if abs(diff) > 15.0:
        if sim > analytic:
            return int(math.ceil(sim)), diff, ["used_larger"], "used_larger"
        return analytic, diff, ["smaller_ignored"], "smaller_ignored"
    return analytic, diff, [], "within_band"


# --------------------------------------------------------------------- main ---
def fmt(x, nd=3):
    if x is None:
        return "-"
    if isinstance(x, float):
        if math.isinf(x):
            return "inf"
        return f"{x:,.{nd}f}"
    return f"{x:,}" if isinstance(x, int) else str(x)


def parse_md_member_table(md_text: str) -> dict[str, dict]:
    """Parse section 3 of stage_d1e_power.md (member rows) for a JSON<->md check."""
    rows = {}
    in_sec = False
    for line in md_text.splitlines():
        if line.startswith("## 3."):
            in_sec = True
            continue
        if in_sec and line.startswith("## "):
            break
        if in_sec and line.startswith("| C"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 18:
                continue
            rows[cells[2]] = {
                "class": cells[0],
                "tier": cells[1],
                "r": cells[4],
                "sd": cells[5],
                "vif": cells[7],
                "n_a": cells[9].replace(",", ""),
                "n_b": cells[10].replace(",", ""),
                "chosen_a": cells[15].replace(",", ""),
                "chosen_b": cells[16].replace(",", ""),
                "flags": cells[17],
            }
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sim", action="store_true")
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--reps", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=7771)
    ap.add_argument("--members", nargs="*", default=None, help="restrict simulation to these ids")
    ap.add_argument("--v2", action="store_true", help="unit-corrected inputs: per-micro trial series, H proxies 200/230")
    ap.add_argument("--snapshot", default=None, help="earlier power JSON to compare the statistic rows against (v2)")
    a = ap.parse_args()
    global FAMILY_H
    FAMILY_H = FAMILY_H_V2 if a.v2 else FAMILY_H_V1

    P = json.loads(POWER_JSON.read_text())
    meta = P["meta"]
    eps = float(meta["eps_day"])
    z = {"a": norm_ppf(1.0 - ALPHA / HOLM_M), "b": norm_ppf(0.80), "95": norm_ppf(0.95)}
    rep_members = {m["id"]: m for m in P["members"]}
    supplied_rep = {S: v["confirmation_days"] for S, v in P["supplied_days"].items()}

    print("# Scratch recomputation output\n")
    print("input sha256:")
    for f in (POWER_JSON, TRIALS_JSON, EVENTS_JSON, GATE_JSON, GATE_EXT_JSON):
        print(f"- {f.relative_to(ROOT)}: {sha256(f)}")
    print()

    # ---- 0. quantiles
    print("## 0. Normal quantiles (Newton on math.erfc)\n")
    print("| quantity | reported | recomputed | abs diff |")
    print("|---|---|---|---|")
    for key, rep_key in (("a", "z_a"), ("b", "z_b"), ("95", "z_95")):
        print(f"| {rep_key} | {meta[rep_key]!r} | {z[key]!r} | {abs(meta[rep_key]-z[key]):.1e} |")
    print(f"| alpha_holm | {meta['alpha_holm']!r} | {ALPHA/HOLM_M!r} | {abs(meta['alpha_holm']-ALPHA/HOLM_M):.1e} |\n")

    # ---- 1. epsilon
    E = epsilon_cells()
    print("## 1. Epsilon derivation\n")
    print(f"cells: {E['n_cells']} ({E['grid_rows']} grid + {E['ext_version']['rows']} extension); robust_c80 pass: {E['n_pass']}, marginal: {E['n_marginal']}")
    print(f"extension file version read: {json.dumps(E['ext_version'])}")
    print(f"extension net_usd_day field vs formula mismatches: {E['ext_net_usd_mismatch']}")
    print(f"verdict-rule violations (pass iff lower95>=0.80; marginal iff 0.80<=power, lower95<0.80): {len(E['verdict_rule_violations'])}")
    print(f"cost ticks by T (power_gate.json): {E['cost_ticks_by_T']}")
    print(f"**min passing net $/day = {E['smallest_pass'][0]['net_usd_day']:.4f} -> {E['eps_exact_ticks_day']:.4f} ticks/day -> floor = {E['eps_day']}** (reported eps_day = {eps})\n")
    print("Five smallest passing cells:\n")
    print("| file | path | T | p | R | net ticks/trade | net $/day | robust power | lower95 |")
    print("|---|---|---|---|---|---|---|---|---|")
    for c in E["smallest_pass"]:
        print(f"| {c['file']} | {c['path']} | {c['T']} | {c['p']} | {c['R']} | {c['net_ticks_trade']:.3f} | {c['net_usd_day']:.3f} | {c['power']:.4f} | {c['lower95']:.4f} |")
    print("\nSmallest marginal cells (excluded by the rule) and largest failing cells:\n")
    print("| file | path | T | p | R | net $/day | verdict | robust power | lower95 |")
    print("|---|---|---|---|---|---|---|---|---|")
    for c in E["smallest_marginal"] + E["largest_fail"]:
        print(f"| {c['file']} | {c['path']} | {c['T']} | {c['p']} | {c['R']} | {c['net_usd_day']:.3f} | {c['verdict']} | {c['power']:.4f} | {c['lower95']:.4f} |")
    print()

    # ---- 2. members
    raw = load_members(v2=a.v2)
    mine = {m["id"]: compute_member(m, z, eps, supplied_rep) for m in raw}
    if a.v2:
        print("## 2c. Unit correction: the per-micro trial series (item 1)\n")
        print("| trial | trips | coded_micros | distinct trip_micros | mean_trip_micros file / mine | max abs diff file vs rebuilt from trips | max abs diff file vs usd/1.25 | max abs diff file vs usd/2.5 | SD_day usd/2.5 (old) | SD_day per-micro (new) | ratio |")
        print("|---|---|---|---|---|---|---|---|---|---|---|")
        n_equal_1p25, n_differ, rebuilt_bad = 0, [], []
        for m in raw:
            if m["kind"] != "trial":
                continue
            d = m["series"]
            d_rebuilt = m["series_from_trips"]
            d_usd = m["series_usd_over_1p25"]
            e_rebuilt = float(np.max(np.abs(d - d_rebuilt)))
            e_usd = float(np.max(np.abs(d - d_usd)))
            e_old = float(np.max(np.abs(d - m["series_usd_over_2p5"])))
            if e_rebuilt > 1e-9:
                rebuilt_bad.append(m["id"])
            if e_usd < 1e-9:
                n_equal_1p25 += 1
            else:
                n_differ.append(m["id"])
            qs = sorted(set(int(x) for x in m["trip_micros"]))
            sd_old = float(np.std(m["series_usd_over_2p5"], ddof=1))
            sd_new = float(np.std(d, ddof=1))
            print(
                f"| {m['id']} | {len(m['trip_micros'])} | {m['coded_micros']} | {qs} | {m['mean_trip_micros_file']} / {float(np.mean(m['trip_micros'])):.6f} | {e_rebuilt:.1e} | {e_usd:.1e} | {e_old:.1e} | {sd_old:.4f} | {sd_new:.4f} | {sd_new / sd_old:.4f} |"
            )
        print(f"\nrebuild-from-trips mismatches (> 1e-9): {rebuilt_bad or 'none'}")
        print(f"trials whose per-micro series equals daily_net_usd / 1.25: {n_equal_1p25}; differing: {n_differ}\n")
    for name, sd_t, f in FAMILY_H:
        mine[name] = compute_projected(name, sd_t, f, z, eps, supplied_rep)
    missing = set(rep_members) - set(mine)
    extra = set(mine) - set(rep_members)
    print("## 2. Per-member recomputation\n")
    print(f"members reported: {len(rep_members)}; recomputed: {len(mine)}; missing from mine: {sorted(missing)}; extra: {sorted(extra)}\n")
    print("| member | kind | r rep | r mine | d% | SD rep | SD mine | d% | VIF rep | VIF mine | d% | lag1 rep | lag1 mine | n_a rep | n_a mine | n_b rep | n_b mine | eps/trade rep | mine | status |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    worst = {"r": 0.0, "sd": 0.0, "vif": 0.0}
    n_mismatch = []
    floored_mine = []
    for mid in rep_members:
        R, M = rep_members[mid], mine.get(mid)
        if M is None:
            continue
        dr, dsd, dv = rel(M["r"], R["r"]), rel(M["sd_day"], R["sd_day"]), rel(M["vif_boot"], R["vif_boot"])
        worst = {"r": max(worst["r"], abs(dr)), "sd": max(worst["sd"], abs(dsd)), "vif": max(worst["vif"], abs(dv))}
        if M["floored"]:
            floored_mine.append(mid)
        status = []
        if abs(dr) > 0.5 or abs(dsd) > 0.5 or abs(dv) > 0.5:
            status.append("STAT>0.5%")
        if M["n_a"] != R["n_a_analytic"]:
            status.append(f"n_a {M['n_a']} vs {R['n_a_analytic']} (exact {M['n_a_exact']:.3f})")
            n_mismatch.append((mid, "a", M["n_a"], R["n_a_analytic"], M["n_a_exact"]))
        if M["n_b"] != R["n_b_analytic"]:
            status.append(f"n_b {M['n_b']} vs {R['n_b_analytic']} (exact {M['n_b_exact']:.3f})")
            n_mismatch.append((mid, "b", M["n_b"], R["n_b_analytic"], M["n_b_exact"]))
        if abs(rel(M["eps_trade"], R["eps_trade"])) > 0.01:
            status.append("eps_trade")
        print(
            f"| {mid} | {R['kind']} | {R['r']:.4f} | {M['r']:.4f} | {dr:+.3f} | {R['sd_day']:.3f} | {M['sd_day']:.3f} | {dsd:+.3f} | "
            f"{R['vif_boot']:.4f} | {M['vif_boot']:.4f} | {dv:+.3f} | {R['lag1']:+.4f} | {M['lag1']:+.4f} | {R['n_a_analytic']} | {M['n_a']} | "
            f"{R['n_b_analytic']} | {M['n_b']} | {R['eps_trade']:.3f} | {M['eps_trade']:.3f} | {'; '.join(status) or 'ok'} |"
        )
    print(f"\nworst |rel diff| over members: r {worst['r']:.4f}%, SD {worst['sd']:.4f}%, VIF {worst['vif']:.4f}%")
    print(f"analytic n mismatches: {n_mismatch if n_mismatch else 'none'}")
    print(f"members my VIF floored: {floored_mine or 'none'}; reported floor_hits: {meta['floor_hits']}")
    vmin = min(M["vif_boot"] for M in mine.values())
    print(f"smallest VIF_boot (mine): {vmin:.4f} at {min(mine, key=lambda k: mine[k]['vif_boot'])}\n")

    # secondary fields: eps_min, eps_ref, n_b_sensitivity, cluster_vif
    print("### 2b. Secondary per-member fields (max |rel diff| over all members)\n")
    worst_epsmin, worst_ref, sens_bad, cl_bad = 0.0, 0, [], []
    for mid, R in rep_members.items():
        M = mine[mid]
        for S in supplied_rep:
            for k in ("per_day", "per_trade"):
                worst_epsmin = max(worst_epsmin, abs(rel(M["eps_min"][S][k], R["eps_min_at_supplied"][S][k])))
        for k in ("n_a", "n_b"):
            worst_ref = max(worst_ref, abs(M["eps_ref"][k] - R["eps_ref_days"][k]))
        if abs(M["eps_ref"]["eps_day_ref"] - R["eps_ref_days"]["eps_day_ref"]) > 1e-9:
            print(f"eps_day_ref mismatch {mid}")
        for e, v in R["n_b_sensitivity"].items():
            if M["n_b_sens"][str(int(float(e)))] != v:
                sens_bad.append((mid, e, M["n_b_sens"][str(int(float(e)))], v))
        if R["kind"] == "trial" and R.get("cluster_vif") is not None and M.get("cluster_vif") is not None:
            if abs(rel(M["cluster_vif"], R["cluster_vif"])) > 0.5:
                cl_bad.append((mid, M["cluster_vif"], R["cluster_vif"]))
    print(f"- eps_min_at_supplied: max |rel diff| = {worst_epsmin:.2e}%")
    print(f"- eps_ref_days (n_a, n_b at 1 tick/trade): max |abs diff| in days = {worst_ref}")
    print(f"- n_b_sensitivity mismatches: {sens_bad or 'none'}")
    print(f"- cluster_vif (trials) mismatches >0.5%: {cl_bad or 'none'}\n")

    # ---- 3. chosen-figure rule and diff_pct, every member with a simulation
    print("## 3. Chosen-figure rule and diff_pct, every simulated member\n")
    print("| member | arm | analytic | sim | diff rep | diff mine | censored flag | chosen rep | chosen by rule | flags rep | rule outcome | ok |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    rule_bad = []
    for mid, R in rep_members.items():
        if R["kind"] == "projected":
            continue
        for arm in ("a", "b"):
            sim = R[f"n_{arm}_sim"]
            an = R[f"n_{arm}_analytic"]
            cens = f"sim_censored_below_grid_{arm}" in R["flags"]
            ch, diff, fl, outcome = chosen_rule(an, sim, cens)
            rep_flags_arm = sorted(f for f in R["flags"] if f.endswith(f"_{arm}"))
            exp_flags = []
            if outcome == "censored":
                exp_flags = [f"sim_censored_below_grid_{arm}"]
            elif outcome == "used_larger":
                exp_flags = [f"sim_used_larger_{arm}"]
            elif outcome == "smaller_ignored":
                exp_flags = [f"sim_smaller_ignored_{arm}"]
            ok = ch == R[f"chosen_{arm}"] and (diff is None or abs(diff - R[f"diff_{arm}_pct"]) < 1e-6) and rep_flags_arm == sorted(exp_flags)
            if not ok:
                rule_bad.append((mid, arm, an, sim, R[f"chosen_{arm}"], ch, rep_flags_arm, exp_flags))
            print(
                f"| {mid} | {arm} | {an} | {fmt(sim, 4)} | {fmt(R[f'diff_{arm}_pct'], 3)} | {fmt(diff, 3)} | {cens} | {R[f'chosen_{arm}']} | {ch} | {','.join(rep_flags_arm) or '-'} | {outcome} | {'ok' if ok else 'MISMATCH'} |"
            )
    print(f"\nchosen-figure rule violations: {rule_bad or 'none'}\n")

    # ---- 4. Family H
    print("## 4. Family H projections\n")
    print("| member | SD_trade | f | SD_day rep | SD_day mine | r rep | r mine | n_a rep | mine | n_b rep | mine | eps/trade rep | mine |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for name, sd_t, f in FAMILY_H:
        R, M = rep_members[name], mine[name]
        print(f"| {name} | {sd_t} | {f:.6f} | {R['sd_day']:.4f} | {M['sd_day']:.4f} | {R['r']:.6f} | {M['r']:.6f} | {R['n_a_analytic']} | {M['n_a']} | {R['n_b_analytic']} | {M['n_b']} | {R['eps_trade']:.3f} | {M['eps_trade']:.3f} |")
    print()

    # ---- 5. classes
    print("## 5. Class tables\n")
    classes = P["classes"]
    class_of = {m["id"]: m["class"] for m in P["members"]}
    print("| class | n members | typical_r rep | mine | eps_trade rep | mine | gross rep | mine | binding_a rep | mine | binding_b rep | mine | achievable flags ok |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    class_bad = []
    for c, C in classes.items():
        ids = C["members"]
        if c == "C7":
            rs = [mine[i]["r"] for i in ids]
        else:
            rs = [mine[i]["r"] for i in ids if rep_members[i]["kind"] == "trial"]
        typ = float(np.median(rs)) if rs else float("nan")
        eps_t = eps / typ
        gross = eps_t + COST_TICKS_MARKET
        ba = max(ids, key=lambda i: (rep_members[i]["chosen_a"], 0))
        bb = max(ids, key=lambda i: (rep_members[i]["chosen_b"], 0))
        ba_days, bb_days = rep_members[ba]["chosen_a"], rep_members[bb]["chosen_b"]
        ach_ok = all(C["null_power_achievable_at"][S] == (supplied_rep[S] >= C["binding_b"]["days"]) for S in supplied_rep)
        members_ok = sorted(ids) == sorted(i for i, cc in class_of.items() if cc == c)
        ok = (
            abs(rel(typ, C["typical_r"])) < 1e-9
            and abs(rel(eps_t, C["eps_trade"])) < 1e-9
            and abs(rel(gross, C["gross_equivalent_trade"])) < 1e-9
            and C["binding_a"]["days"] == ba_days
            and C["binding_b"]["days"] == bb_days
            and ach_ok
            and members_ok
            and C["supplied_days"] == supplied_rep
        )
        if not ok:
            class_bad.append(c)
        print(
            f"| {c} | {len(ids)} | {C['typical_r']:.6f} | {typ:.6f} | {C['eps_trade']:.4f} | {eps_t:.4f} | {C['gross_equivalent_trade']:.4f} | {gross:.4f} | "
            f"{C['binding_a']['id']} ({C['binding_a']['days']}) | {ba} ({ba_days}) | {C['binding_b']['id']} ({C['binding_b']['days']}) | {bb} ({bb_days}) | {ach_ok and members_ok} |"
        )
    print(f"\nclass-block mismatches: {class_bad or 'none'}\n")

    print("### 5a. resolution_range recomputed from members' eps_min_at_supplied (reported fields) and from my own eps_min\n")
    print("| class | S | basis | min/trade rep | from rep fields | from mine | max/trade rep | from rep fields | from mine | min/day rep | mine | max/day rep | mine | ok |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    rr_bad = []
    for c, C in classes.items():
        ids = C["members"]
        basis = "projected" if c == "C7" else "measured"
        pool = [i for i in ids if (rep_members[i]["kind"] == "projected") == (c == "C7")]
        for S in supplied_rep:
            RR = C["resolution_range"][S]
            rep_pt = {i: rep_members[i]["eps_min_at_supplied"][S]["per_trade"] for i in pool}
            rep_pd = {i: rep_members[i]["eps_min_at_supplied"][S]["per_day"] for i in pool}
            my_pt = {i: mine[i]["eps_min"][S]["per_trade"] for i in pool}
            my_pd = {i: mine[i]["eps_min"][S]["per_day"] for i in pool}
            f_min_pt, f_max_pt = min(rep_pt, key=rep_pt.get), max(rep_pt, key=rep_pt.get)
            f_min_pd, f_max_pd = min(rep_pd, key=rep_pd.get), max(rep_pd, key=rep_pd.get)
            m_min_pt, m_max_pt = min(my_pt, key=my_pt.get), max(my_pt, key=my_pt.get)
            ok = (
                RR["basis"] == basis
                and RR["members"] == len(pool)
                and RR["min_per_trade"]["member"] == f_min_pt == m_min_pt
                and RR["max_per_trade"]["member"] == f_max_pt == m_max_pt
                and RR["min_per_day"]["member"] == f_min_pd
                and RR["max_per_day"]["member"] == f_max_pd
                and abs(rel(RR["min_per_trade"]["value"], my_pt[m_min_pt])) < 1e-6
                and abs(rel(RR["max_per_trade"]["value"], my_pt[m_max_pt])) < 1e-6
                and abs(rel(RR["min_per_day"]["value"], my_pd[f_min_pd])) < 1e-6
                and abs(rel(RR["max_per_day"]["value"], my_pd[f_max_pd])) < 1e-6
            )
            if not ok:
                rr_bad.append((c, S))
            print(
                f"| {c} | {S} | {RR['basis']}/{RR['members']} vs {basis}/{len(pool)} | {RR['min_per_trade']['value']:.4f} ({RR['min_per_trade']['member']}) | {rep_pt[f_min_pt]:.4f} ({f_min_pt}) | {my_pt[m_min_pt]:.4f} ({m_min_pt}) | "
                f"{RR['max_per_trade']['value']:.4f} ({RR['max_per_trade']['member']}) | {rep_pt[f_max_pt]:.4f} ({f_max_pt}) | {my_pt[m_max_pt]:.4f} ({m_max_pt}) | "
                f"{RR['min_per_day']['value']:.4f} ({RR['min_per_day']['member']}) | {my_pd[f_min_pd]:.4f} | {RR['max_per_day']['value']:.4f} ({RR['max_per_day']['member']}) | {my_pd[f_max_pd]:.4f} | {'ok' if ok else 'MISMATCH'} |"
            )
    print(f"\nresolution_range mismatches: {rr_bad or 'none'}\n")

    # ---- 5b. members whose per-trade eps_min at the earliest start is below the cost bar
    S0 = "2019-05-06"
    measured = [i for i, R in rep_members.items() if R["kind"] != "projected"]
    below_rep = sorted(i for i in measured if rep_members[i]["eps_min_at_supplied"][S0]["per_trade"] < COST_TICKS_MARKET)
    below_mine = sorted(i for i in measured if mine[i]["eps_min"][S0]["per_trade"] < COST_TICKS_MARKET)
    print(f"### 5b. Measured members with per-trade eps_min < {COST_TICKS_MARKET} at S = {S0}\n")
    print(f"- from the reported eps_min fields: {len(below_rep)} of {len(measured)}")
    print(f"- from my recomputed eps_min: {len(below_mine)} of {len(measured)}; same set: {below_rep == below_mine}")
    by_class = {}
    for i in below_mine:
        by_class.setdefault(rep_members[i]["class"], []).append(i)
    for c in sorted(by_class):
        print(f"- {c} ({len(by_class[c])}): " + ", ".join(by_class[c]))
    near = sorted(measured, key=lambda i: abs(mine[i]["eps_min"][S0]["per_trade"] - COST_TICKS_MARKET))[:4]
    print("- nearest to the bar: " + "; ".join(f"{i} {mine[i]['eps_min'][S0]['per_trade']:.3f}" for i in near) + "\n")

    # ---- 6. supplied days
    print("## 6. Supplied days recount\n")
    print("| S | rep weekday open | mine (stated rule) | mine (pipeline closures) | rep blackout | rolls exact x3 | pro-rata months | rep degraded | degraded in range | of which weekday-open | rep days | mine: stated method | mine: exact rolls, weekday degraded | mine: pipeline closures, exact |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for S in STARTS:
        key = S.isoformat()
        R = P["supplied_days"][key]
        A = supplied_days(S, END_DATE, "stated")
        B = supplied_days(S, END_DATE, "pipeline")
        print(
            f"| {key} | {R['weekday_open_dates']} | {A['weekday_open_dates']} | {B['weekday_open_dates']} | {R['roll_blackout_days']} | {A['blackout_exact']} ({A['rolls_exact']} rolls) | {A['blackout_pro_rata_months']} | {R['vendor_degraded_days']} | {A['degraded_in_range']} | {A['degraded_weekday_open']} | **{R['confirmation_days']}** | {A['days_stated_method']} | {A['days_exact']} | {B['days_exact']} |"
        )
    H = P["holdout2_detail"]
    A = supplied_days(HOLDOUT2[0], HOLDOUT2[1], "stated")
    B = supplied_days(HOLDOUT2[0], HOLDOUT2[1], "pipeline")
    print(
        f"| holdout-2 {HOLDOUT2[0]}..{HOLDOUT2[1]} | {H['weekday_open_dates']} | {A['weekday_open_dates']} | {B['weekday_open_dates']} | {H['roll_blackout_days']} | {A['blackout_exact']} ({A['rolls_exact']} rolls) | {A['blackout_pro_rata_months']} | {H['vendor_degraded_days']} | {A['degraded_in_range']} | {A['degraded_weekday_open']} | **{H['confirmation_days']}** | {A['days_stated_method']} | {A['days_exact']} | {B['days_exact']} |"
    )
    print("\nDegraded dates in the 2019-05-06..2024-02-29 range and their weekday:")
    for d in DEGRADED:
        if STARTS[0] <= d <= END_DATE:
            print(f"- {d} ({d.strftime('%A')})")
    print("\nFull closures counted per year under the stated rule:")
    for y in range(2019, 2025):
        cl = sorted(cme_full_closures(y, "stated"))
        print(f"- {y}: {len(cl)}: " + ", ".join(d.isoformat() for d in cl))
    try:
        from dateutil import easter as _de  # only to cross-check my Easter

        bad = [y for y in range(2019, 2026) if _de.easter(y) != easter(y)]
        print(f"\nEaster cross-check against dateutil: mismatches {bad or 'none'}")
    except Exception as exc:  # noqa: BLE001
        print(f"\nEaster cross-check: dateutil unavailable ({exc})")
    print()

    # ---- 7. JSON internal consistency
    print("## 7. JSON internal consistency\n")
    issues = []
    for mid, R in rep_members.items():
        if R["kind"] == "projected":
            continue
        for arm in ("a", "b"):
            ns = sorted(int(k) for k in R["curve"])
            ps = [R["curve"][str(n)][f"power_{arm}"] for n in ns]
            ses = [R["curve"][str(n)][f"se_{arm}"] for n in ns]
            for i in range(1, len(ns)):
                drop = ps[i - 1] - ps[i]
                tol = 3.0 * math.sqrt(ses[i - 1] ** 2 + ses[i] ** 2) + 1e-12
                if drop > tol:
                    issues.append(f"{mid} arm {arm}: power drops {ps[i-1]:.4f}@{ns[i-1]} -> {ps[i]:.4f}@{ns[i]} (> 3 MC se {tol:.4f})")
            # analytic n present in the curve grid?
            an = R[f"n_{arm}_analytic"]
            if str(max(an, 2)) not in R["curve"]:
                issues.append(f"{mid}: analytic n_{arm}={an} not in curve grid")
            # se consistent with binomial
            for n in ns:
                p_, s_ = R["curve"][str(n)][f"power_{arm}"], R["curve"][str(n)][f"se_{arm}"]
                if abs(s_ - math.sqrt(p_ * (1 - p_) / meta["replications"])) > 1e-9:
                    issues.append(f"{mid} n={n} arm {arm}: se not binomial")
                    break
        if abs(R["eps_trade"] - eps / R["r"]) > 1e-9:
            issues.append(f"{mid}: eps_trade != eps/r")
        if R["spot_check"] and R["spot_check"]["n"] != R["chosen_b"]:
            issues.append(f"{mid}: spot_check n {R['spot_check']['n']} != chosen_b {R['chosen_b']}")
        if R["spot_check"] and str(R["spot_check"]["n"]) in R["curve"]:
            cf = R["curve"][str(R["spot_check"]["n"])]["power_b"]
            if abs(cf - R["spot_check"]["closed_form_power_b"]) > 1e-9:
                issues.append(f"{mid}: spot_check closed_form_power_b {R['spot_check']['closed_form_power_b']} != curve power_b {cf}")
        if R.get("sim_source_vif_floored"):
            issues.append(f"{mid}: sim_source_vif_floored true")
        if R["vif_boot"] < VIF_FLOOR - 1e-12:
            issues.append(f"{mid}: vif below floor")
        if bool(R["sim_zero_variance_draws"]) != ("zero_variance_draws" in R["flags"]):
            issues.append(f"{mid}: zero_variance_draws flag inconsistent with count {R['sim_zero_variance_draws']}")
    # class membership vs coverage counts
    exp_counts = {"C1": 6, "C2": 31, "C3": 40, "C4": 13, "C5": 4, "C6": 1, "C7": 6}
    for c, n in exp_counts.items():
        if len(classes[c]["members"]) != n:
            issues.append(f"class {c}: {len(classes[c]['members'])} members, coverage.md implies {n}")
    tiers = {"A": 0, "B": 0, "H": 0}
    for R in rep_members.values():
        tiers[R["tier"]] += 1
    if tiers != {"A": 52, "B": 43, "H": 6}:
        issues.append(f"tier counts {tiers} != A 52 (31 trials + 21 near-misses), B 43, H 6")
    if meta["floor_hits"] != 0:
        issues.append("floor_hits != 0")
    # md vs json
    md_rows = parse_md_member_table(POWER_MD.read_text())
    md_bad = []
    for mid, R in rep_members.items():
        row = md_rows.get(mid)
        if row is None:
            md_bad.append(f"{mid}: not in md table")
            continue
        if int(row["n_a"]) != R["n_a_analytic"] or int(row["n_b"]) != R["n_b_analytic"]:
            md_bad.append(f"{mid}: md n_a/n_b {row['n_a']}/{row['n_b']} vs json {R['n_a_analytic']}/{R['n_b_analytic']}")
        if int(row["chosen_a"]) != R["chosen_a"] or int(row["chosen_b"]) != R["chosen_b"]:
            md_bad.append(f"{mid}: md chosen {row['chosen_a']}/{row['chosen_b']} vs json {R['chosen_a']}/{R['chosen_b']}")
        if abs(float(row["sd"]) - R["sd_day"]) > 0.006 or abs(float(row["vif"]) - R["vif_boot"]) > 0.0006:
            md_bad.append(f"{mid}: md SD/VIF {row['sd']}/{row['vif']} vs json {R['sd_day']:.3f}/{R['vif_boot']:.4f}")
        if row["class"] != R["class"] or row["tier"] != R["tier"]:
            md_bad.append(f"{mid}: md class/tier {row['class']}/{row['tier']} vs json {R['class']}/{R['tier']}")
    print(f"md section-3 rows parsed: {len(md_rows)}; md-vs-json mismatches: {md_bad or 'none'}")
    print("issues:")
    for s in issues or ["none"]:
        print(f"- {s}")
    print()

    # ---- 7b. snapshot comparison (item 5 of the re-verification)
    if a.snapshot:
        snap_path = Path(a.snapshot)
        S = json.loads(snap_path.read_text())
        s_members = {m["id"]: m for m in S["members"]}
        print("## 7b. Comparison with the earlier run (snapshot)\n")
        print(f"snapshot: {snap_path} sha256 {sha256(snap_path)}; generated {S['meta'].get('generated_utc')}, eps_day {S['meta'].get('eps_day')}")
        print(f"member order identical: {[m['id'] for m in S['members']] == [m['id'] for m in P['members']]}")
        stat_diff, trial_same = [], []
        for mid, R in rep_members.items():
            if mid not in s_members:
                stat_diff.append((mid, ["missing in snapshot"]))
                continue
            same = json.dumps(R, sort_keys=True) == json.dumps(s_members[mid], sort_keys=True)
            if R["kind"] == "statistic" and not same:
                keys = [k for k in R if json.dumps(R[k], sort_keys=True) != json.dumps(s_members[mid].get(k), sort_keys=True)]
                stat_diff.append((mid, keys))
            if R["kind"] != "statistic" and same:
                trial_same.append(mid)
        n_stat = sum(1 for R in rep_members.values() if R["kind"] == "statistic")
        print(f"statistic rows: {n_stat}; byte-identical to the snapshot (json.dumps, sorted keys): {n_stat - len(stat_diff)}; differing: {stat_diff or 'none'}")
        print(f"trial / projected rows unexpectedly identical to the snapshot: {trial_same or 'none'}")
        meta_diff = [k for k in P["meta"] if k not in ("generated_utc", "runtime_seconds", "notes", "source_sha256") and P["meta"].get(k) != S["meta"].get(k)]
        print(f"meta fields differing (excluding timestamps, runtime, notes, source hashes): {meta_diff or 'none'}")
        print(f"supplied_days identical: {P['supplied_days'] == S['supplied_days']}; holdout2 identical: {P['holdout2_detail'] == S['holdout2_detail']}")
        # scale check on the trials that changed: SD ratio and n ratio
        print("\n| trial | SD_day snapshot | SD_day now | ratio | n_b snapshot | n_b now | n_a snapshot | n_a now | VIF same | lag1 same |")
        print("|---|---|---|---|---|---|---|---|---|---|")
        for mid, R in rep_members.items():
            if R["kind"] != "trial":
                continue
            Sm = s_members[mid]
            print(
                f"| {mid} | {Sm['sd_day']:.4f} | {R['sd_day']:.4f} | {R['sd_day'] / Sm['sd_day']:.6f} | {Sm['n_b_analytic']} | {R['n_b_analytic']} | {Sm['n_a_analytic']} | {R['n_a_analytic']} | {abs(R['vif_boot'] - Sm['vif_boot']) < 1e-12} | {abs(R['lag1'] - Sm['lag1']) < 1e-12} |"
            )
        print()

    # ---- 8. simulation
    if a.sim:
        from multiprocessing import Pool

        targets = a.members or [
            "A-H4 rth leg",
            "G3.RTH.5",
            "F1_1_h1_RTH",
            "F2_4_15min_vol_tercile_top",
            "E-H1 scheduled macro drift",
            "C-H4 passive-fill reversal",
            "E-H3 quarterly witching short",
            "C-H1 magnitude-conditioned reversal",
            "F3_2_bucket04_bucket05",
            "G1.RTH.5",
            "G4.RTH.30",
            "F4_4_round_number_multiples_of_100",
            "G1.RTH.15",
        ]
        series_by_id = {m["id"]: m["series"] for m in raw}
        jobs = []
        for t in targets:
            R = rep_members[t]
            grid = sorted(set(int(k) for k in R["curve"]))  # the code's own grid incl. analytic n's
            # refined local grid around the reported simulated figures (both arms)
            extra = set()
            for arm in ("a", "b"):
                s = R[f"n_{arm}_sim"]
                if s and not (f"sim_censored_below_grid_{arm}" in R["flags"]):
                    for f_ in (0.75, 0.87, 1.0, 1.15, 1.3):
                        extra.add(max(2, int(round(s * f_))))
            grid_all = sorted(set(grid) | extra)
            # VIF_source: my own recomputation (agrees with the reported one to <0.5%)
            jobs.append((t, series_by_id[t], mine[t]["vif_boot"], eps, z["a"], z["95"], grid_all, a.reps, a.seed))
        with Pool(processes=max(1, a.procs)) as pool:
            results = pool.map(simulate_member, jobs)
        print(f"## 8. Re-simulation ({a.reps} reps, seed {a.seed}, {a.procs} procs)\n")
        print("Grid-matched = crossing interpolated on the code's own grid (the reported method); refined = crossing on the grid plus five local points around the reported figure.\n")
        print("| member | arm | analytic | reported sim | censored rep | mine grid-matched | mine refined | MC se (n) | rel diff grid-matched % | rel diff refined % | tolerance % | verdict | rule outcome mine (refined) vs rep chosen |")
        print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        for res in results:
            R = rep_members[res["id"]]
            grid_code = set(int(k) for k in R["curve"])
            curve_grid = {n: v for n, v in res["curve"].items() if n in grid_code}
            for arm in ("a", "b"):
                rep_sim = R[f"n_{arm}_sim"]
                rep_cens = f"sim_censored_below_grid_{arm}" in R["flags"]
                n_g, cens_g, se_g = cross(curve_grid, arm)
                n_r, cens_r, se_r = cross(res["curve"], arm)
                an = R[f"n_{arm}_analytic"]
                if rep_sim is None or n_g is None:
                    verdict = "no crossing (rep or mine)"
                    d_g = d_r = None
                    tol = None
                elif rep_cens or cens_g:
                    verdict = "consistent (both censored at grid floor)" if (rep_cens and cens_g) else "CENSOR MISMATCH"
                    d_g = rel(n_g, rep_sim)
                    d_r = rel(n_r, rep_sim) if n_r else None
                    tol = None
                else:
                    d_g = rel(n_g, rep_sim)
                    d_r = rel(n_r, rep_sim) if n_r else None
                    tol = max(10.0, 100.0 * 2.0 * (se_g or 0.0) / rep_sim)
                    verdict = "consistent" if abs(d_g) <= tol else "DISCREPANCY"
                ch, diff, fl, outcome = chosen_rule(an, n_r if n_r else n_g, cens_r if n_r else cens_g)
                print(
                    f"| {res['id']} | {arm} | {an} | {fmt(rep_sim, 2)} | {rep_cens} | {fmt(n_g, 2)}{' (cens)' if cens_g else ''} | {fmt(n_r, 2)}{' (cens)' if cens_r else ''} | {fmt(se_g, 2)} | {fmt(d_g, 1)} | {fmt(d_r, 1)} | {fmt(tol, 1)} | {verdict} | {outcome} -> {ch} vs rep {R[f'chosen_{arm}']} |"
                )
        print("\n### 8b. Power at the reported chosen n (both arms), mine vs the reported curve\n")
        print("| member | n (chosen_b) | rep power_b | mine power_b | n (chosen_a) | rep power_a | mine power_a | zero-var draws mine (all lengths) | rep sim_zero_variance_draws |")
        print("|---|---|---|---|---|---|---|---|---|")
        for res in results:
            R = rep_members[res["id"]]
            nb, na = max(R["chosen_b"], 2), max(R["chosen_a"], 2)
            rb = R["curve"].get(str(nb), {}).get("power_b")
            ra = R["curve"].get(str(na), {}).get("power_a")
            mb = res["curve"].get(nb, {}).get("power_b")
            ma = res["curve"].get(na, {}).get("power_a")
            print(f"| {res['id']} | {nb} | {fmt(rb, 4)} | {fmt(mb, 4)} | {na} | {fmt(ra, 4)} | {fmt(ma, 4)} | {res['zero_var_total']} | {R['sim_zero_variance_draws']} |")
        print("\n### 8c. Full curves (mine), power_a / power_b by n\n")
        for res in results:
            R = rep_members[res["id"]]
            line = ", ".join(
                f"{n}: {v['power_a']:.3f}/{v['power_b']:.3f}" + (f" (rep {R['curve'][str(n)]['power_a']:.3f}/{R['curve'][str(n)]['power_b']:.3f})" if str(n) in R["curve"] else "")
                for n, v in sorted(res["curve"].items())
            )
            print(f"- {res['id']}: {line}")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
