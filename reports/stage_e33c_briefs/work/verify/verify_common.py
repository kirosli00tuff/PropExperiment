"""Shared constants, loaders and statistics for the E.33c Part D4 independent verification.

Independent of pipeline/search33.py, pipeline/select33.py and work/stats/. Reads the search
root, the label store and the feature store's _day files directly (pyarrow, numpy, json), and
uses pipeline/cal33.py only for the 796 OOF dates. Every date read is asserted to lie inside
the discovery span 2020-12-01..2024-02-29 (no test-window data, nothing from 2024-03-01 on).
"""
from __future__ import annotations

import json
import math
import os
import sys
from datetime import date
from pathlib import Path
from statistics import NormalDist

import numpy as np
import pyarrow.parquet as pq

os.nice(10)

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
DERIVED = Path("/mnt/large-storage/market_data/PropExperiment/derived/e33")
SEARCH = DERIVED / "search"
LABELS = DERIVED / "labels" / "b15c4ca10d68"
DAY = DERIVED / "features" / "2b30cb0e953b" / "_day"
OUT = DERIVED / "verify_c"
WORK = REPO / "reports" / "stage_e33c_briefs" / "work"

SPAN_FIRST, SPAN_LAST = date(2020, 12, 1), date(2024, 2, 29)
N_TRIALS = 838          # trial_registry.current_n() after r009-E33 (addendum)
T_DISC = 796
T_TEST = 870            # p7_final.py: 890 program trade dates minus 20 burn-in
K_FOLDS = 6
ENTRY_CAP = 20          # P3.8
DSR_TARGET = 0.95       # G3
G1_TRADES_PER_DATE, G1_SHARE_DATES = 1.0, 0.5
G2_MEAN_NET = 0.50
G5A_QUARTERS = 9
G5B_MONTH_SHARE = 0.25
G5C_T = 2.5
CORR_MAX = 0.70
NEAR_FRAC = 0.10

SETS = ["S1", "S2", "S3", "S4", "S5"]
LABEL_TYPES = ["F05", "F15", "F30", "F60", "T15", "T30"]
LABEL_H = {"F05": 5, "F15": 15, "F30": 30, "F60": 60, "T15": 15, "T30": 30}
LABEL_KIND = {"F05": 0, "F15": 0, "F30": 0, "F60": 0, "T15": 1, "T30": 1}  # FH before TB at equal h
GRIDS = ["L001A", "L001E", "L010A", "L010E", "L100A", "L100E", "G2050", "G2200", "G3050", "G3200"]
CLASSES = (-1, 0, 1)

LABEL_COLS = ["i", "t_ns", "entry_ok", "row_ok", "y", "n_long", "n_short",
              "long_made", "long_net", "long_entry_ns", "long_exit_ns", "long_flags",
              "short_made", "short_net", "short_entry_ns", "short_exit_ns", "short_flags",
              "mid_move"]

_ND = NormalDist()


def log(*parts: object) -> None:
    print(*parts, flush=True)


def all_config_ids() -> list[str]:
    out = []
    for s in SETS:
        for lab in LABEL_TYPES:
            for g in GRIDS:
                out.append(f"E33-{s}{lab}{g}")
    assert len(out) == 300
    return out


def parse_config(cid: str) -> dict:
    assert cid.startswith("E33-") and len(cid) == 4 + 2 + 3 + 5, cid
    s, lab, g = cid[4:6], cid[6:9], cid[9:]
    assert s in SETS and lab in LABEL_TYPES and g in GRIDS, cid
    return {"set": s, "set_idx": SETS.index(s), "label": lab, "h": LABEL_H[lab],
            "kind": LABEL_KIND[lab], "grid": g, "grid_idx": GRIDS.index(g),
            "family": "LOGIT" if g.startswith("L") else "LGBM"}


def oof_dates() -> list[str]:
    sys.path.insert(0, str(REPO / "reports" / "stage_e33_briefs" / "work" / "pipeline"))
    import cal33  # noqa: PLC0415  (allowed reader module)
    ds = cal33.oof_dates()
    assert len(ds) == T_DISC
    for d in ds:
        assert SPAN_FIRST <= d <= SPAN_LAST, d
    return [d.isoformat() for d in ds]


def check_in_span(ds: str) -> None:
    d = date.fromisoformat(ds)
    if not (SPAN_FIRST <= d <= SPAN_LAST):
        raise RuntimeError(f"date {ds} outside the discovery span; refusing to read")


def load_label_table(label: str, dates: list[str]) -> dict[str, dict[str, np.ndarray]]:
    """All 796 dates of one label type: date -> {col: array}."""
    out = {}
    for ds in dates:
        check_in_span(ds)
        t = pq.read_table(LABELS / label / f"{ds}.parquet", columns=LABEL_COLS)
        cols = {c: t.column(c).to_numpy(zero_copy_only=False) for c in LABEL_COLS}
        n = len(cols["i"])
        if not np.array_equal(cols["i"], np.arange(n, dtype=cols["i"].dtype)):
            raise RuntimeError(f"label {label} {ds}: i is not 0..n-1")
        out[ds] = cols
    return out


def load_sigma_zm(dates: list[str]) -> dict[str, float]:
    out = {}
    for ds in dates:
        check_in_span(ds)
        v = json.load(open(DAY / f"{ds}.json"))["sigma_zm"]
        if v is None or not math.isfinite(v) or v <= 0:
            raise RuntimeError(f"sigma_zm undefined on {ds}")
        out[ds] = float(v)
    return out


def tercile_of_dates(dates: list[str], sigma: dict[str, float]) -> dict[str, int]:
    """P8 G5 (d): sorted by sigma_ZM(D) ascending, ties by date; ranks 1-265, 266-530, 531-796."""
    order = sorted(dates, key=lambda d: (sigma[d], d))
    n = len(order)
    assert n == T_DISC
    bounds = [(0, 265), (265, 530), (530, 796)]
    out = {}
    for k, (a, b) in enumerate(bounds, start=1):
        for d in order[a:b]:
            out[d] = k
    return out


def quarter_key(ds: str) -> str:
    """G5 (a) quarters Dec-Feb, Mar-May, Jun-Aug, Sep-Nov keyed by the start month (S06)."""
    y, m = int(ds[:4]), int(ds[5:7])
    if m == 12:
        return f"{y}-12"
    if m <= 2:
        return f"{y - 1}-12"
    start = 3 * ((m - 3) // 3) + 3
    return f"{y}-{start:02d}"


def month_key(ds: str) -> str:
    return ds[:7]


# ---- statistics (own implementations of screening/stage_e_verdict.py moments() and t_stat()) ----

def moments(xs: np.ndarray) -> dict:
    xs = np.asarray(xs, dtype=np.float64)
    n = int(xs.size)
    mean = math.fsum(xs.tolist()) / n
    dev = xs - mean
    var = math.fsum((dev * dev).tolist()) / n
    sd = math.sqrt(var)
    if sd == 0.0:
        return {"n": n, "mean": mean, "sd": 0.0, "skew": 0.0, "kurtosis": 3.0, "sharpe": 0.0}
    skew = math.fsum((dev ** 3).tolist()) / n / sd ** 3
    kurt = math.fsum((dev ** 4).tolist()) / n / sd ** 4
    return {"n": n, "mean": mean, "sd": sd, "skew": skew, "kurtosis": kurt, "sharpe": mean / sd}


def t_stat(mom: dict) -> float | None:
    if mom["sd"] <= 0 or mom["n"] < 2:
        return None
    return mom["mean"] / (mom["sd"] / math.sqrt(mom["n"]))


EULER_GAMMA = 0.5772156649015329


def own_expected_max_sharpe(n_trials: int, variance: float) -> float:
    """Bailey & Lopez de Prado eq. (3) with Python's NormalDist (AS241 inverse CDF)."""
    g = EULER_GAMMA
    term = (1 - g) * _ND.inv_cdf(1 - 1.0 / n_trials) + g * _ND.inv_cdf(1 - 1.0 / (n_trials * math.e))
    return math.sqrt(variance) * term


def own_dsr(sr: float, t: int, n_trials: int, variance: float, skew: float, kurt: float) -> dict:
    """DSR from the formula: z = (SR - SR0) sqrt(T-1) / sqrt(1 - g3 SR + (g4-1)/4 SR^2); DSR = Phi(z)."""
    sr0 = own_expected_max_sharpe(n_trials, variance)
    den = 1.0 - skew * sr + 0.25 * (kurt - 1.0) * sr * sr
    if den <= 0:
        return {"dsr": None, "sr0": sr0, "z": None, "degenerate": True}
    z = (sr - sr0) * math.sqrt(t - 1) / math.sqrt(den)
    return {"dsr": _ND.cdf(z), "sr0": sr0, "z": z, "degenerate": False}


def program_dsr(sr: float, t: int, n_trials: int, variance: float, skew: float, kurt: float) -> dict:
    """The program's function, as G3 names it."""
    sys.path.insert(0, str(REPO))
    from funnel.multiple_comparisons import deflated_sharpe_ratio  # noqa: PLC0415
    try:
        r = deflated_sharpe_ratio(sr, t, n_trials, variance, skew, kurt)
        return {"dsr": r["deflated_sharpe_ratio"], "sr0": r["expected_max_sharpe_under_null"],
                "z": r["z"], "degenerate": False}
    except ValueError as e:
        return {"dsr": None, "sr0": None, "z": None, "degenerate": True, "error": str(e)}


def se_sharpe(sr: float, t: int, skew: float, kurt: float) -> float | None:
    """P8 G4: sqrt((1 - g3 SR + (g4-1)/4 SR^2)/(T-1)); None when the radicand is not positive (P04 a)."""
    rad = 1.0 - skew * sr + 0.25 * (kurt - 1.0) * sr * sr
    if rad <= 0:
        return None
    return math.sqrt(rad / (t - 1))


def bisect_increasing(f, target: float, lo: float = 0.0, hi: float = 1.0, iters: int = 200) -> float:
    for _ in range(iters):
        mid = (lo + hi) / 2
        if f(mid) >= target:
            hi = mid
        else:
            lo = mid
    return hi


def b_test_values() -> dict:
    """b_test = max(3/sqrt(T_test), SR with DSR = 0.95 at N, V = 1/(T_test-1), normal moments)."""
    v = 1.0 / (T_TEST - 1)
    t_bar = 3.0 / math.sqrt(T_TEST)
    prog = bisect_increasing(lambda s: program_dsr(s, T_TEST, N_TRIALS, v, 0.0, 3.0)["dsr"], DSR_TARGET)
    own = bisect_increasing(lambda s: own_dsr(s, T_TEST, N_TRIALS, v, 0.0, 3.0)["dsr"], DSR_TARGET)
    # G3-implied SR threshold at discovery, normal moments (P7.2: 0.1724), for information only
    vd = 1.0 / (T_DISC - 1)
    g3_prog = bisect_increasing(lambda s: program_dsr(s, T_DISC, N_TRIALS, vd, 0.0, 3.0)["dsr"], DSR_TARGET)
    g3_own = bisect_increasing(lambda s: own_dsr(s, T_DISC, N_TRIALS, vd, 0.0, 3.0)["dsr"], DSR_TARGET)
    return {"t_bar": t_bar, "dsr_test_program": prog, "dsr_test_own": own,
            "b_test_program": max(t_bar, prog), "b_test_own": max(t_bar, own),
            "g3_sr_threshold_normal_program": g3_prog, "g3_sr_threshold_normal_own": g3_own}


def rel_equal(a, b, rel: float = 1e-9, abs_: float = 1e-12) -> bool:
    if a is None or b is None:
        return a is None and b is None
    if isinstance(a, bool) or isinstance(b, bool):
        return a == b
    a, b = float(a), float(b)
    if math.isnan(a) or math.isnan(b):
        return math.isnan(a) and math.isnan(b)
    return abs(a - b) <= max(abs_, rel * max(abs(a), abs(b)))


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, sort_keys=True, default=_default)


def _default(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.bool_,)):
        return bool(o)
    raise TypeError(str(type(o)))
