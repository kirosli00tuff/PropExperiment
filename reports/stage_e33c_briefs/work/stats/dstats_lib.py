"""Stage E.33c Part D statistics (StatsCoder): pure functions, no file I/O.

Independent of select33.py (frozen pipeline): the gates of P8 are re-implemented here from the protocol text
(reports/stage_e32_discovery_protocol_v0.3.md P6.2, P7.2, P8) and the readings P01-P08
(reports/stage_e33_protocol_readings.md). Statistics of daily series use the program's moments() and t_stat()
(protocol 0.3), passed in by the caller, so this module imports nothing from the repo and is testable alone.
"""
from __future__ import annotations

import math
from statistics import NormalDist
from typing import Callable, Sequence

Z = NormalDist()
EULER_GAMMA = 0.5772156649015329

# ---------------------------------------------------------------- declared numbers (protocol 0.3)
T_DISC = 796
FOLD_SIZES = (133, 133, 133, 133, 132, 132)          # P6.1
F_SELECTION = 0.528                                  # P0.3 / P6.2: Topstep, ticks per round trip
FEES = {                                             # P6.4 and the brief's D1 list (ticks per round trip)
    "Topstep": 0.528, "Lucid": 0.560, "Lucid_not_all_in": 0.920,
    "Bulenox": 0.572, "MFFU": 0.612, "Tradeify": 0.920,
}
G1_MIN_PER_DATE, G1_MIN_SHARE = 1.0, 0.5
G2_MIN_NET = 0.50
G3_DSR = 0.95
G5A_MIN_Q, G5B_MAX_SHARE, G5C_MIN_T = 9, 0.25, 2.5
SIGMA_1M = 3.15                                      # P0.4 standard number (power only)
DECISION_MINUTES = {5: 273, 15: 263, 30: 248, 60: 218}
SET_INDEX = {"S1": 1, "S2": 2, "S3": 3, "S4": 4, "S5": 5}
LABEL_KEY = {"F05": (5, 0), "F15": (15, 0), "F30": (30, 0), "F60": (60, 0), "T15": (15, 1), "T30": (30, 1)}
GRID_ORDER = ("L001A", "L001E", "L010A", "L010E", "L100A", "L100E", "G2050", "G2200", "G3050", "G3200")


def all_ids() -> list:
    """The 300 E33 ids in the P5 run order (sets S5, S1, S3, S2, S4)."""
    return [f"E33-{s}{lab}{g}" for s in ("S5", "S1", "S3", "S2", "S4")
            for lab in ("F15", "F30", "F05", "F60", "T15", "T30") for g in GRID_ORDER]


def parse_id(cid: str) -> dict:
    body = cid.split("-", 1)[1]
    st, lab, grid = body[:2], body[2:5], body[5:]
    if st not in SET_INDEX or lab not in LABEL_KEY or grid not in GRID_ORDER:
        raise ValueError(f"not a P7.1 id: {cid!r}")
    return {"set": st, "label": lab, "grid": grid, "h": LABEL_KEY[lab][0],
            "family": "LOGIT" if grid[0] == "L" else "LGBM"}


# ---------------------------------------------------------------- calendar groupings
def quarter_key(d: str) -> str:
    """P8 G5 (a): calendar quarters Dec-Feb, Mar-May, Jun-Aug, Sep-Nov, named by their first month."""
    y, m = int(d[:4]), int(d[5:7])
    if m == 12:
        return f"{y:04d}-12"
    if m <= 2:
        return f"{y - 1:04d}-12"
    return f"{y:04d}-{3 * (m // 3):02d}"


def group_indices(dates: Sequence[str], keyf: Callable[[str], str]) -> dict:
    out: dict = {}
    for j, d in enumerate(dates):
        out.setdefault(keyf(d), []).append(j)
    return out


def fold_slices(n: int = T_DISC) -> list:
    """P6.1 contiguous blocks of 133, 133, 133, 133, 132, 132 dates."""
    if sum(FOLD_SIZES) != n:
        raise ValueError(f"fold sizes sum to {sum(FOLD_SIZES)}, not {n}")
    out, start = [], 0
    for size in FOLD_SIZES:
        out.append(list(range(start, start + size)))
        start += size
    return out


def tercile_slices(dates: Sequence[str], sigma: Sequence[float]) -> list:
    """P8 G5 (d): dates sorted by sigma_ZM(D) ascending, ties by date; ranks 1-265, 266-530, 531-796."""
    order = sorted(range(len(dates)), key=lambda j: (float(sigma[j]), dates[j]))
    n3 = len(dates) // 3
    return [order[:n3], order[n3:2 * n3], order[2 * n3:]]


# ---------------------------------------------------------------- gates (P8)
def se_sharpe_g4(sr: float, skew: float, kurt: float, t: int) -> float | None:
    """P8 G4 se; None when the radicand is not positive (reading P04: G4 fails)."""
    rad = 1.0 - skew * sr + (kurt - 1.0) / 4.0 * sr * sr
    return math.sqrt(rad / (t - 1)) if rad > 0 else None


def largest_month(x: Sequence[float], dates: Sequence[str]) -> dict:
    """The largest calendar month's net and its share of the total (defined only when the total is > 0)."""
    sums = {k: math.fsum(x[j] for j in idx) for k, idx in group_indices(dates, lambda d: d[:7]).items()}
    k_max = max(sums, key=lambda k: (sums[k], k))
    total = math.fsum(x)
    return {"month": k_max, "max_month_sum": sums[k_max], "total": total,
            "share": sums[k_max] / total if total > 0 else None}


def g5_parts(x: Sequence[float], dates: Sequence[str], sigma: Sequence[float],
             moments: Callable, t_stat: Callable) -> dict:
    """P8 G5 (a)-(d) with every value used (readings P05: an undefined leave-one-month-out t fails (c))."""
    quarters = group_indices(dates, quarter_key)
    months = group_indices(dates, lambda d: d[:7])
    q_means = {k: math.fsum(x[j] for j in idx) / len(idx) for k, idx in quarters.items()}
    q_pos = sum(1 for v in q_means.values() if v > 0)
    lm = largest_month(x, dates)
    lomo = {}
    for k, idx in months.items():
        drop = set(idx)
        rest = [x[j] for j in range(len(x)) if j not in drop]
        lomo[k] = t_stat(moments(rest)) if len(rest) >= 2 else None
    lomo_def = [v for v in lomo.values() if v is not None]
    terc = [math.fsum(x[j] for j in s) / len(s) for s in tercile_slices(dates, sigma)]
    a = q_pos >= G5A_MIN_Q
    b = lm["total"] > 0 and lm["max_month_sum"] <= G5B_MAX_SHARE * lm["total"]
    c = all(v is not None and v >= G5C_MIN_T for v in lomo.values())
    d = all(v > 0 for v in terc)
    return {"a": a, "quarters_positive": q_pos, "n_quarters": len(quarters), "b": b, "total": lm["total"],
            "max_month": lm["month"], "max_month_sum": lm["max_month_sum"], "max_month_share": lm["share"],
            "c": c, "min_lomo_t": min(lomo_def) if lomo_def else None,
            "lomo_undefined": sum(1 for v in lomo.values() if v is None), "d": d, "tercile_means": terc,
            "pass": a and b and c and d}


def evaluate(x: Sequence[float], n_trades: Sequence[int], dates: Sequence[str], sigma: Sequence[float],
             n_trials: int, b_test: float, moments: Callable, t_stat: Callable, dsr_fn: Callable) -> dict:
    """Every P8 gate for one configuration with a series. dsr_fn = funnel's deflated_sharpe_ratio."""
    t = len(dates)
    x = [float(v) for v in x]
    nt = [int(v) for v in n_trades]
    mom = moments(x)
    tt = t_stat(mom)
    count, with_trade, total = sum(nt), sum(1 for k in nt if k > 0), math.fsum(x)
    mnpt = total / count if count else None
    dsr = None
    if mom["sd"] > 0:
        try:
            dsr = dsr_fn(mom["sharpe"], t, n_trials, 1.0 / (t - 1), mom["skew"],
                         mom["kurtosis"])["deflated_sharpe_ratio"]
        except ValueError:
            dsr = None
    se = se_sharpe_g4(mom["sharpe"], mom["skew"], mom["kurtosis"], t) if mom["sd"] > 0 else None
    g5 = g5_parts(x, dates, sigma, moments, t_stat)
    gates = {"G1": count >= G1_MIN_PER_DATE * t and with_trade >= G1_MIN_SHARE * t,
             "G2": mnpt is not None and mnpt >= G2_MIN_NET,
             "G3": dsr is not None and dsr > G3_DSR,
             "G4": se is not None and mom["sharpe"] - se >= b_test,
             "G5": g5["pass"]}
    return {"moments": mom, "sharpe": mom["sharpe"], "t": tt, "constant": mom["sd"] == 0,
            "trade_count": count, "trades_per_date": count / t, "dates_with_trade": with_trade,
            "share_dates_with_trade": with_trade / t, "total_net": total, "mean_net_per_trade": mnpt,
            "dsr": dsr, "se": se, "sr_lower": None if se is None else mom["sharpe"] - se, "g5": g5,
            "gates": gates}


def funnel(gate_rows: Sequence[dict]) -> dict:
    names = ("G1", "G2", "G3", "G4", "G5")
    alone = {g: sum(1 for r in gate_rows if r[g]) for g in names}
    in_order, alive = {}, list(gate_rows)
    for g in names:
        alive = [r for r in alive if r[g]]
        in_order["G1" if g == "G1" else f"G1..{g}"] = len(alive)
    return {"alone": alone, "in_order": in_order}


def rank_key(cid: str, sharpe: float, trade_count: int) -> tuple:
    """P8 total order: round(SR_d, 4) descending; fewer trades; LOGIT first; lower set; shorter h, FH first;
    earlier grid point."""
    p = parse_id(cid)
    lab = LABEL_KEY[p["label"]]
    return (-round(sharpe, 4), trade_count, 0 if p["family"] == "LOGIT" else 1, SET_INDEX[p["set"]],
            lab[0], lab[1], GRID_ORDER.index(p["grid"]))


# ---------------------------------------------------------------- reports (never gates)
def firm_net(mean_net_topstep: float | None, fee: float) -> float | None:
    """Mean net per trade at market, L = 1 s, under another fee: the fills are the selection variant's, so only
    the fee changes: net_firm = net_Topstep + 0.528 - fee."""
    return None if mean_net_topstep is None else mean_net_topstep + F_SELECTION - fee


def one_sided_p(t: float | None) -> float:
    """Reading P07: p = 1 - Phi(daily t); no t -> p = 1 (counted in m)."""
    return 1.0 if t is None else 1.0 - Z.cdf(t)


def bh_count(pvals: Sequence[float], q: float = 0.05) -> int:
    """Benjamini-Hochberg step-up: the largest rank k with p_(k) <= k q / m."""
    ps, m, k_max = sorted(pvals), len(pvals), 0
    for k, p in enumerate(ps, 1):
        if p <= k * q / m:
            k_max = k
    return k_max


def holm_count(pvals: Sequence[float], alpha: float = 0.05) -> int:
    """Holm step-down: reject while p_(k) <= alpha / (m - k + 1)."""
    ps, m, n = sorted(pvals), len(pvals), 0
    for k, p in enumerate(ps, 1):
        if p <= alpha / (m - k + 1):
            n += 1
        else:
            break
    return n


def expected_max_normal(n: int, mean: float, sd: float) -> float:
    """E[max of n iid N(mean, sd^2)], Bailey and Lopez de Prado (2014) eq. (3) form (the program's
    expected_max_sharpe with a location): mean + sd ((1 - g) Phi^-1(1 - 1/n) + g Phi^-1(1 - 1/(n e)))."""
    if n < 2:
        return mean
    term = (1 - EULER_GAMMA) * Z.inv_cdf(1 - 1.0 / n) + EULER_GAMMA * Z.inv_cdf(1 - 1.0 / (n * math.e))
    return mean + sd * term


def se_normal(sr: float, t: int) -> float:
    """se of a daily Sharpe at normal moments (p7_final.se_sharpe with skew 0, kurtosis 3)."""
    return math.sqrt(max(1e-12, 1 + 0.5 * sr * sr) / (t - 1))


def s80_at_bar(bar: float, t: int, power: float = 0.80) -> float:
    """p7_final's convention for '80% power' (its s80 line): bar + z_power se(bar)."""
    return bar + Z.inv_cdf(power) * se_normal(bar, t)


def s80_exact(bar: float, t: int, power: float = 0.80) -> float:
    """The true daily Sharpe s with P(SR_hat >= bar) = power, se evaluated at s (bisection)."""
    lo, hi = bar, bar + 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if mid - Z.inv_cdf(power) * se_normal(mid, t) >= bar:
            hi = mid
        else:
            lo = mid
    return hi


def mde_random_walk(sr: float, h: int, n_per_date: float, sigma_1m: float = SIGMA_1M) -> float:
    """P7.2 per-trade line (p7_final 'Net edge per trade implied'): mu = SR sigma_h / sqrt(n), sigma_h =
    3.15 sqrt(h) ticks, n independent trades every date (daily SR = mu sqrt(n) / sigma_h)."""
    return sr * sigma_1m * math.sqrt(h) / math.sqrt(n_per_date)


def mde_measured(sr: float, sd_daily: float, trades_per_date: float) -> float | None:
    """Per-trade shift e that gives a configuration's measured daily series a true daily Sharpe sr from a zero
    mean: the daily mean moves by e x trades per date, the daily SD is the measured one."""
    if trades_per_date <= 0 or not sd_daily > 0:
        return None
    return sr * sd_daily / trades_per_date


def quantiles(xs: Sequence[float], qs: Sequence[float] = (0.0, 0.05, 0.25, 0.5, 0.75, 0.95, 1.0)) -> dict:
    """Linear-interpolation quantiles (numpy's default method), stdlib only."""
    s = sorted(float(v) for v in xs)
    if not s:
        return {}
    out = {}
    for q in qs:
        pos = q * (len(s) - 1)
        lo = int(math.floor(pos))
        hi = min(lo + 1, len(s) - 1)
        out[f"q{q:g}"] = s[lo] + (s[hi] - s[lo]) * (pos - lo)
    return out
