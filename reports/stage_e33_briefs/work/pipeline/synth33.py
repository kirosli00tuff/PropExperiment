"""Stage E.33 P4.2 search-proof generator (ProofCoder): synthetic minute rows, null and planted.

Per seed, synthetic tables in the INTERFACE.md 4.1 (features) and 4.2 (labels) schemas for the 796 real OOF
dates on the real grid G_h(D) and the real P1.4 / P3.6 calendar exclusions (rules 1-4 from cal33), labels F15
and T30 only, the 59 S5 feature columns, and _day json with a synthetic sigma_ZM(D) path (the 20 burn-in dates
as history). Everything here is synthetic: no market data and no outcome is read (cal33 supplies only the trade
dates, the P1.4 exclusions, the release instants and calendar flags).

Price model (ticks of ZM, 0.10 USD/short ton; every choice is logged in ProofCoder_readings.md):
- A latent price X per date, sampled at three points per minute j (j = -60..278 on the open-time axis, j = 0 at
  08:35:00 CT): A_j = t_j (minute mark: features, sigma), B_j = t_j + L (entry fills, FH exits, TB barrier
  checks), C_j = t_j + 2L (TB exit fills at tau + L). L = 1 s, so increments A->B and B->C carry 1/60 of a
  minute's variance and drift, C->A(next) the other 58/60 (READING P-L).
- Volatility: sigma_D (ticks per minute of X) is log-normal across dates with an AR(1) in log (persistence
  LOGVOL_PHI, stationary SD LOGVOL_SD), scaled so that the 1-minute mid change SD is about 3.15 ticks (P0.4).
- Touch: spread 1 tick with probability 1 - SPREAD2_SHARE, else 2 ticks, i.i.d. per sample point. 1 tick:
  bid = floor(X), ask = bid + 1; 2 ticks: bid = round(X) - 1, ask = bid + 2 (round = floor(X + 0.5)). The mid is
  an unbiased discretisation of X. The synthetic book always has both sides and no price limits, so P3.6 rule 5
  and rule 6 never fire and P3.2's fallbacks never occur (flags 0).
- Plant: the feature F3_4 (IOFI5) is a unit-variance Gaussian AR(1) over minutes (phi = exp(-1/5)) in every
  seed. The latent drift over minute (t_j, t_j+1] is beta x z_j, z_j the F3_4 value at t_j (known at t_j). Null
  seeds: beta = 0 (no feature carries signal; F4 features come from the driftless past path, the others are
  noise independent of the path). Planted seeds: beta = PLANT_BETA, calibrated so that the oracle (P3.5 with
  the true class probabilities and class-conditional means, P3.8, f, the dead zone) has an expected daily
  Sharpe of 0.35 net at F15 (calibrate()).

Labels at minute resolution: FH: N_long = bid(B_{i+h}) - ask(B_i) - f, N_short = bid(B_i) - ask(B_{i+h}) - f
(P3.3). TB: m0 = M(B_i); barrier checks at the book updates B_j, j = i+1..i+h (the synthetic book updates once
a minute at t_j + L for this purpose, READING P-TB); tau = the first B_j with M - m0 >= b or <= -b, else
t + L + h; exit fill at tau + L = C_j (P3.4). Weights per P3.7 (intervals met by more than one second).

CLI:
  uv run python synth33.py write --seed S --root DIR [--kind null|planted] [--n-oof N]
  uv run python synth33.py calibrate --out FILE [--draws K]
  uv run python synth33.py oracle --seed S [--kind ...]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import time
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

# ---------------------------------------------------------------- declared generator constants
NS = 1_000_000_000
L_NS = NS                      # L = 1.000 s (selection; P0.3)
MIN_NS = 60 * NS
FEE = 0.528                    # f, ticks per round trip (P0.3)
N_BURN = 20                    # P1.4
N_OOF = 796
N_FEAT_MIN = 273               # feature minutes i = 0..272 (INTERFACE 4.1)
LAST_MARK = 278                # A points j = 0..278 = 08:35..13:13 (sigma_ZM intervals, P0.3)
PRE = 60                       # open-time minutes before 08:35 kept for look-backs (F4.5 needs 60)
NJ = PRE + LAST_MARK + 1       # minutes j = -60..278
SIGMA_1M_TARGET = 3.15         # P0.4 standard number: SD of 1-minute ZM mid changes, ticks
SPREAD2_SHARE = 0.10           # READING P-SPREAD: share of 2-tick touches
LOGVOL_SD, LOGVOL_PHI = 0.20, 0.90   # READING P-VOL: log sigma_D AR(1) across dates
RELEASE_PRE_NS, RELEASE_POST_NS = 2 * MIN_NS, 30 * MIN_NS   # P3.6 rule 3
PLANT_FEATURE = "F3_4"
PLANT_PHI = math.exp(-1.0 / 5.0)     # READING P-PLANT: 5-minute memory of the planted IOFI5
PLANT_BETA = 0.367                   # ticks of drift per minute per unit of F3_4; calibrate() 2026-10-27 15:28 PDT
SEED_TAG = 20261027
NULL_SEEDS = tuple(range(1, 21))
PLANTED_SEEDS = tuple(range(101, 121))
LABELS = {"F15": ("FH", 15), "T30": ("TB", 30)}
TARGET_ORACLE_SR = 0.35
SQRT_2_OVER_PI = math.sqrt(2.0 / math.pi)

_FAMILIES = (("C", 15), ("F1", 8), ("F2", 11), ("F3", 12), ("F4", 13))
FEATURE_COLUMNS = tuple(f"{fam}_{j}" for fam, n in _FAMILIES for j in range(1, n + 1))
LABEL_COLUMNS = ("i", "t_ns", "entry_ok", "row_ok", "y", "n_long", "n_short", "w", "span_end_ns") + tuple(
    f"{s}_{f}" for s in ("long", "short") for f in ("made", "net", "entry_ns", "exit_ns", "flags")) + (
    "mid_move",)                     # INTERFACE 4.2 (lead, 15:20): M(t + L + h) - M(t + L); reported only
CLIP = 5.0
# P4 G4: features clipped to [-5, 5] after their own normalisation (38); the other 21 are bounded or logs
CLIPPED = frozenset(["C_5", "F1_1", "F1_2", "F1_3", "F1_4", "F1_6", "F1_7", "F1_8"]
                    + [f"F2_{k}" for k in range(1, 12)]
                    + ["F3_1", "F3_2", "F3_3", "F3_4", "F3_10", "F3_11", "F3_12"]
                    + ["F4_1", "F4_2", "F4_3", "F4_4", "F4_5"] + [f"F4_{k}" for k in range(7, 14)])
assert len(CLIPPED) == 38 and len(FEATURE_COLUMNS) == 59


def kind_of_seed(seed: int) -> str:
    """P4.2: seeds 1-20 null, 101-120 planted; any other seed needs an explicit kind."""
    if seed in NULL_SEEDS:
        return "null"
    if seed in PLANTED_SEEDS:
        return "planted"
    raise ValueError(f"seed {seed} is not a proof seed; pass the kind explicitly")


def beta_of(kind: str) -> float:
    if kind == "null":
        return 0.0
    if kind == "planted":
        if not PLANT_BETA > 0:
            raise RuntimeError("PLANT_BETA is not calibrated")
        return PLANT_BETA
    raise ValueError(f"kind {kind!r}")


# ---------------------------------------------------------------- calendar (real dates, from cal33)
@dataclass(frozen=True)
class Calendar:
    dates: tuple            # trade dates as "YYYY-MM-DD": 20 burn-in, then the OOF dates
    t0_ns: np.ndarray       # 08:35:00 CT of each date (UTC ns)
    excluded: np.ndarray    # P1.4 (rule 4)
    releases: tuple         # P3.6 rule 3 instants R per date
    c7: np.ndarray          # synthetic C.7 proxy (trade dates to the next roll, READING P-C7)
    c8: np.ndarray          # 1 if D carries a rule-3 release
    c10: np.ndarray         # Monday or first trade date after a full closure
    c15: np.ndarray         # June, July or August
    fronts: tuple           # {"ZM", "ZS", "ZL": instrument id} per date (from cal33; labels only)

    @property
    def n_oof(self) -> int:
        return len(self.dates) - N_BURN


@lru_cache(maxsize=4)
def load_calendar(n_oof: int | None = None) -> Calendar:
    """The 816 trade dates (or the 20 burn-in dates and the first n_oof OOF dates) with cal33's P1.4
    exclusions and P3.6 rule-3 releases. Reads no market data (cal33: calendars, manifests, release CSVs)."""
    import cal33
    days = cal33.trade_dates()
    if n_oof is not None:
        if not 1 <= n_oof <= N_OOF:
            raise ValueError(f"n_oof {n_oof}")
        days = days[:N_BURN + n_oof]
    roll = np.array([cal33.REASON_ROLL in cal33.excluded(d)[1] for d in cal33.trade_dates()])
    all_days = cal33.trade_dates()
    nxt, to_roll = len(all_days) + 60, np.zeros(len(all_days))
    for k in range(len(all_days) - 1, -1, -1):
        if roll[k]:
            nxt = k
        to_roll[k] = nxt - k
    c7 = np.minimum(to_roll[:len(days)] + 10.0, 60.0) / 60.0
    return Calendar(
        dates=tuple(d.isoformat() for d in days),
        t0_ns=np.array([cal33.ct_ns(d, "08:35:00") for d in days], dtype=np.int64),
        excluded=np.array([cal33.excluded(d)[0] for d in days], dtype=bool),
        releases=tuple(tuple(int(r) for r in cal33.releases(d)) for d in days),
        c7=c7,
        c8=np.array([1.0 if cal33.releases(d) else 0.0 for d in days]),
        c10=np.array([1.0 if cal33.monday_or_after_closure(d) else 0.0 for d in days]),
        c15=np.array([1.0 if d.month in (6, 7, 8) else 0.0 for d in days]),
        fronts=tuple({k: int(v) for k, v in cal33.fronts(d).items()} for d in days))


# ---------------------------------------------------------------- random streams
_STREAMS = ("vol", "plant", "diffusion", "spread", "level", "ctx", "f1", "f2", "f3", "f4")


def streams(seed: int) -> dict:
    """Independent PCG64 streams per component, so a component's draws never depend on another's."""
    root = np.random.SeedSequence(entropy=[SEED_TAG, int(seed)])
    return {name: np.random.Generator(np.random.PCG64(child))
            for name, child in zip(_STREAMS, root.spawn(len(_STREAMS)))}


def ar1(rng: np.random.Generator, shape: tuple, phi: float) -> np.ndarray:
    """Unit-variance stationary Gaussian AR(1) along axis 1 (minutes); shape (dates, minutes[, k])."""
    eps = rng.standard_normal(shape)
    out = np.empty(shape)
    out[:, 0] = eps[:, 0]
    c = math.sqrt(1.0 - phi * phi)
    for j in range(1, shape[1]):
        out[:, j] = phi * out[:, j - 1] + c * eps[:, j]
    return out


def window_sum(x: np.ndarray, k: int) -> np.ndarray:
    """Sum of the last k values ending at each minute (axis 1); the first k-1 minutes use what exists."""
    c = np.cumsum(x, axis=1)
    out = c.copy()
    out[:, k:] = c[:, k:] - c[:, :-k]
    return out


def log_sigma_mean() -> float:
    """mu of log sigma_D: E[sigma_D^2] + 1/6 (two uniform rounding errors) = 3.15^2 (READING P-VOL)."""
    target_var = SIGMA_1M_TARGET ** 2 - 1.0 / 6.0
    return 0.5 * math.log(target_var) - LOGVOL_SD ** 2


# ---------------------------------------------------------------- the price path
@dataclass
class Path_:
    sigma: np.ndarray       # true sigma_D (ticks/min of X), per date
    z: np.ndarray           # planted F3_4 latent, (dates, NJ)
    bid: np.ndarray         # (dates, NJ, 3) integer ticks at A_j, B_j, C_j
    ask: np.ndarray
    spread_a: np.ndarray    # (dates, NJ) spread at A_j
    sigma_zm: np.ndarray    # sigma_ZM(D) from the 20 previous dates (NaN when undefined)


def make_path(seed: int, beta: float, n_dates: int, rng: dict | None = None) -> Path_:
    rng = rng or streams(seed)
    # volatility across dates (a fixed 816-length draw, so a reduced calendar is a prefix)
    a = np.empty(816)
    e = rng["vol"].standard_normal(816)
    a[0] = LOGVOL_SD * e[0]
    for d in range(1, 816):
        a[d] = LOGVOL_PHI * a[d - 1] + LOGVOL_SD * math.sqrt(1 - LOGVOL_PHI ** 2) * e[d]
    sigma = np.exp(log_sigma_mean() + a)[:n_dates]
    z = ar1(rng["plant"], (816, NJ), PLANT_PHI)[:n_dates]
    eps = rng["diffusion"].standard_normal((816, NJ, 3))[:n_dates]
    sp2 = (rng["spread"].random((816, NJ, 3)) < SPREAD2_SHARE)[:n_dates]
    level = (3500.0 + 300.0 * rng["level"].standard_normal(816) + rng["level"].random(816))[:n_dates]
    s = sigma[:, None]
    d_ab = beta * z / 60.0 + s * math.sqrt(1 / 60.0) * eps[:, :, 0]
    d_bc = beta * z / 60.0 + s * math.sqrt(1 / 60.0) * eps[:, :, 1]
    d_ca = beta * z * (58.0 / 60.0) + s * math.sqrt(58 / 60.0) * eps[:, :, 2]
    total = d_ab + d_bc + d_ca
    xa = level[:, None] + np.concatenate([np.zeros((n_dates, 1)), np.cumsum(total[:, :-1], axis=1)], axis=1)
    x = np.stack([xa, xa + d_ab, xa + d_ab + d_bc], axis=2)
    bid = np.where(sp2, np.floor(x + 0.5) - 1.0, np.floor(x)).astype(np.int64)
    ask = bid + np.where(sp2, 2, 1).astype(np.int64)
    mid2 = bid[:, :, 0] + ask[:, :, 0]
    dmid = (mid2[:, PRE + 1:PRE + LAST_MARK + 1] - mid2[:, PRE:PRE + LAST_MARK]) / 2.0  # 278 per date
    sigma_zm = np.full(n_dates, np.nan)
    for d in range(N_BURN, n_dates):
        sigma_zm[d] = float(np.std(dmid[d - N_BURN:d].ravel()))   # population SD (P0.3)
    return Path_(sigma, z, bid, ask, np.where(sp2[:, :, 0], 2.0, 1.0), sigma_zm)


# ---------------------------------------------------------------- features (INTERFACE 4.1)
def _clip(x: np.ndarray) -> np.ndarray:
    return np.clip(x, -CLIP, CLIP)


def make_features(seed: int, cal: Calendar, path: Path_, rng: dict | None = None) -> np.ndarray:
    """(OOF dates, 273, 59) float64. Noise families independent of the price path; F4 from the past path."""
    rng = rng or streams(seed)
    nd = len(cal.dates)
    oof = slice(N_BURN, nd)
    j_i = PRE + np.arange(N_FEAT_MIN)           # column of minute i in the (dates, NJ) arrays
    i = np.arange(N_FEAT_MIN, dtype=np.float64)
    out: dict = {}
    sig = path.sigma_zm[oof][:, None]

    # C context
    out["C_1"] = np.broadcast_to(i / 278.0, (nd - N_BURN, N_FEAT_MIN))
    out["C_2"] = out["C_1"] ** 2
    out["C_3"] = np.minimum(path.spread_a[oof][:, j_i], 5.0)
    ctx = rng["ctx"]
    out["C_4"] = 4.0 + 0.4 * ar1(ctx, (816, NJ), 0.90)[oof][:, j_i]
    out["C_5"] = 0.5 * ar1(ctx, (816, NJ), 0.95)[oof][:, j_i]
    out["C_6"] = np.broadcast_to(np.log(sig), (nd - N_BURN, N_FEAT_MIN))
    out["C_7"] = np.broadcast_to(cal.c7[oof][:, None], (nd - N_BURN, N_FEAT_MIN))
    out["C_8"] = np.broadcast_to(cal.c8[oof][:, None], (nd - N_BURN, N_FEAT_MIN))
    out["C_9"] = out["C_8"] * (i >= 175)[None, :]      # 11:30 = 08:35 + 175 min
    out["C_10"] = np.broadcast_to(cal.c10[oof][:, None], (nd - N_BURN, N_FEAT_MIN))
    for k in (11, 12, 13, 14):
        out[f"C_{k}"] = np.ones((nd - N_BURN, N_FEAT_MIN))  # READING P-FLAGS: every family valid
    out["C_15"] = np.broadcast_to(cal.c15[oof][:, None], (nd - N_BURN, N_FEAT_MIN))

    # F1 crush (noise with crush-like persistence)
    f1 = rng["f1"]
    z30 = ar1(f1, (816, NJ), 0.95)[oof]
    out["F1_1"] = z30[:, j_i]
    out["F1_2"] = ar1(f1, (816, NJ), 0.99)[oof][:, j_i]
    out["F1_3"] = 1.2 * ar1(f1, (816, NJ), 0.98)[oof][:, j_i]
    out["F1_4"] = z30[:, j_i] - z30[:, j_i - 5]
    out["F1_5"] = 0.3 + 0.1 * np.tanh(ar1(f1, (816, NJ), 0.90)[oof][:, j_i])
    out["F1_6"] = out["F1_1"] * out["F1_5"]
    gc = f1.standard_normal(816)[oof][:, None]
    out["F1_7"] = np.broadcast_to(gc, (nd - N_BURN, N_FEAT_MIN))
    out["F1_8"] = gc * np.exp(-i / 30.0)[None, :]

    # F2 cross-asset (independent ZS and ZL walks and order flow)
    f2 = rng["f2"]
    g_s = f2.standard_normal((816, NJ))[oof]
    g_l = f2.standard_normal((816, NJ))[oof]
    for base, g in ((0, g_s), (3, g_l)):
        for n, k in enumerate((1, 5, 15)):
            out[f"F2_{base + n + 1}"] = window_sum(g, k)[:, j_i] / math.sqrt(k)
    o_s = f2.standard_normal((816, NJ))[oof]
    o_l = f2.standard_normal((816, NJ))[oof]
    for base, o in ((8, o_s), (10, o_l)):
        for n, k in enumerate((1, 5)):
            out[f"F2_{base + n}"] = window_sum(o, k)[:, j_i] / (math.sqrt(k) * SQRT_2_OVER_PI)

    # F4 own price path (from the synthetic mids; driftless under the null)
    m = (path.bid[oof][:, :, 0] + path.ask[oof][:, :, 0]) / 2.0          # (dates, NJ) mid at A_j
    for n, k in enumerate((1, 5, 15, 30, 60)):
        out[f"F4_{n + 1}"] = (m[:, j_i] - m[:, j_i - k]) / (sig * math.sqrt(k))
    pre = m[:, PRE - 5:]                                                  # from 08:30 (j = -5)
    hi = np.maximum.accumulate(pre, axis=1)[:, 5:5 + N_FEAT_MIN]
    lo = np.minimum.accumulate(pre, axis=1)[:, 5:5 + N_FEAT_MIN]
    rng_hl = hi - lo
    out["F4_6"] = np.where(rng_hl > 0, (m[:, j_i] - lo) / np.where(rng_hl > 0, rng_hl, 1.0), 0.5)
    gap = rng["f4"].standard_normal(816)[oof][:, None]
    out["F4_7"] = np.broadcast_to(gap, (nd - N_BURN, N_FEAT_MIN))
    out["F4_8"] = gap * np.exp(-i / 30.0)[None, :]
    r_open = (m[:, j_i] - m[:, [PRE]]) / (sig * np.sqrt(np.maximum(1.0, i))[None, :])
    out["F4_9"] = r_open
    dm = np.diff(m, axis=1)                                               # dm[:, j-1] = m[j] - m[j-1]
    win = np.stack([dm[:, j_i - 1 - q] for q in range(15)], axis=2)       # the 15 changes ending at t
    out["F4_10"] = win.std(axis=2) / sig
    b2 = (m[:, 2:] - m[:, :-2])                                           # b2[:, e-2] = m[e] - m[e-2]
    bs = np.stack([b2[:, j_i - q - 2] for q in range(14)], axis=2) / (sig[:, :, None] * math.sqrt(2.0))
    # B* = largest |B(e)|, latest e on ties: q = 0 is the latest window end, argmax takes the first max
    q_star = np.argmax(np.abs(bs), axis=2)
    b_star = np.take_along_axis(bs, q_star[:, :, None], axis=2)[:, :, 0]
    db = np.where(np.abs(b_star) >= 3.0, b_star, 0.0)
    out["F4_11"] = db
    out["F4_12"] = db * np.exp(-q_star / 5.0)
    out["F4_13"] = r_open * (i >= 220)[None, :]                           # 12:15 = 08:35 + 220 min
    # F2.7 d5: implied-meal 5-minute move (ZS, ZL; noise) minus ZM's own 5-minute move, scaled
    out["F2_7"] = 0.8 * out["F2_2"] - 0.5 * out["F2_5"] - out["F4_2"]

    # F3 ZM order flow and book state; F3_4 is the planted feature (IOFI5)
    f3 = rng["f3"]
    o = f3.standard_normal((816, NJ))[oof]
    for n, k in enumerate((1, 5, 15)):
        out[f"F3_{n + 1}"] = window_sum(o, k)[:, j_i] / (math.sqrt(k) * SQRT_2_OVER_PI)
    out["F3_4"] = path.z[oof][:, j_i]
    ti = f3.standard_normal((816, NJ))[oof]
    out["F3_5"] = np.tanh(0.6 * window_sum(ti, 5)[:, j_i] / math.sqrt(5))
    out["F3_6"] = np.tanh(0.6 * window_sum(ti, 15)[:, j_i] / math.sqrt(15))
    out["F3_7"] = np.tanh(0.8 * ar1(f3, (816, NJ), 0.6)[oof][:, j_i])
    out["F3_8"] = np.tanh(0.6 * ar1(f3, (816, NJ), 0.8)[oof][:, j_i])
    out["F3_9"] = np.tanh(0.5 * window_sum(f3.standard_normal((816, NJ))[oof], 5)[:, j_i] / math.sqrt(5))
    sb, ss = f3.poisson(0.3, (816, NJ))[oof], f3.poisson(0.3, (816, NJ))[oof]
    out["F3_10"] = (window_sum(sb, 5) - window_sum(ss, 5))[:, j_i] / 3.0
    rb, ra = f3.poisson(1.0, (816, NJ))[oof], f3.poisson(1.0, (816, NJ))[oof]
    out["F3_11"] = (window_sum(rb, 15) - window_sum(ra, 15))[:, j_i] / (math.sqrt(30.0) * SQRT_2_OVER_PI)
    out["F3_12"] = np.exp(0.3 * ar1(f3, (816, NJ), 0.98)[oof][:, j_i])

    feats = np.empty((nd - N_BURN, N_FEAT_MIN, len(FEATURE_COLUMNS)))
    for k, name in enumerate(FEATURE_COLUMNS):
        v = np.asarray(out[name], dtype=np.float64)
        feats[:, :, k] = _clip(v) if name in CLIPPED else v
    if not np.all(np.isfinite(feats)):
        raise AssertionError("non-finite synthetic feature")
    return feats


# ---------------------------------------------------------------- labels (INTERFACE 4.2)
def release_hit(t_ns: np.ndarray, end_ns: np.ndarray, releases) -> np.ndarray:
    """P3.6 rule 3: the closed span [t, end] meets the closed window [R - 2 min, R + 30 min]."""
    hit = np.zeros(t_ns.shape, dtype=bool)
    for r in releases:
        hit |= (t_ns <= r + RELEASE_POST_NS) & (end_ns >= r - RELEASE_PRE_NS)
    return hit


def interval_bounds(t_ns: np.ndarray, end_ns: np.ndarray, t0: int) -> tuple:
    """First and last one-minute interval (index from t0) that the span [t, end] meets by more than 1 s
    (P3.7). Spans start on minute marks here."""
    if np.any((t_ns - t0) % MIN_NS):
        raise ValueError("spans must start on minute marks")
    lo = (t_ns - t0) // MIN_NS
    full = (end_ns - t0) // MIN_NS
    rem = (end_ns - t0) - full * MIN_NS
    hi = np.where(rem > NS, full, full - 1)
    return lo, hi


def uniqueness(t_ns: np.ndarray, end_ns: np.ndarray, t0: int) -> np.ndarray:
    """P3.7 average uniqueness of one date's rows (raw, no renormalisation)."""
    lo, hi = interval_bounds(t_ns, end_ns, t0)
    if len(lo) == 0:
        return np.zeros(0)
    if np.any(hi < lo):
        raise ValueError("a span meets no interval by more than one second")
    size = int(hi.max()) + 2
    diff = np.zeros(size)
    np.add.at(diff, lo, 1.0)
    np.add.at(diff, hi + 1, -1.0)
    c = np.cumsum(diff)[:-1]
    inv = np.where(c > 0, 1.0 / np.where(c > 0, c, 1.0), 0.0)
    pref = np.concatenate([[0.0], np.cumsum(inv)])
    return (pref[hi + 1] - pref[lo]) / (hi - lo + 1)


def make_labels(label: str, cal: Calendar, path: Path_) -> dict:
    """Label tables of every OOF date: dict of arrays (dates, rows), per INTERFACE 4.2, plus the TB direction."""
    kind, h = LABELS[label]
    nd = len(cal.dates) - N_BURN
    n = LAST_MARK - h            # |G_h| = 278 - h rows, i = 0..277-h
    i = np.arange(n)
    oof = slice(N_BURN, len(cal.dates))
    bid, ask = path.bid[oof], path.ask[oof]
    jb = PRE + i
    t0 = cal.t0_ns[oof][:, None]
    t_ns = t0 + i[None, :] * MIN_NS
    entry_t = t_ns + L_NS
    ask_e, bid_e = ask[:, jb, 1], bid[:, jb, 1]
    if kind == "FH":
        jx = jb + h
        bid_x, ask_x = bid[:, jx, 1], ask[:, jx, 1]
        exit_t = t_ns + h * MIN_NS + L_NS
        n_long = (bid_x - ask_e).astype(np.float64) - FEE
        n_short = (bid_e - ask_x).astype(np.float64) - FEE
        y = np.where(n_long > 0, 1, np.where(n_short > 0, -1, 0)).astype(np.int8)
        if np.any((n_long > 0) & (n_short > 0)):
            raise AssertionError("N_long and N_short both positive (P3.3)")
    else:
        mid2_b = bid[:, :, 1] + ask[:, :, 1]
        two_b = 2.0 * path.sigma_zm[oof] * math.sqrt(h)                       # b = kappa sigma sqrt(h)
        if not np.all(two_b > 0):
            raise AssertionError("TB needs sigma_ZM(D) > 0")
        win = np.stack([mid2_b[:, jb + k] for k in range(1, h + 1)], axis=2)    # B_{i+k}, k = 1..h
        d = (win - mid2_b[:, jb][:, :, None]).astype(np.float64)
        up = d >= two_b[:, None, None]
        dn = d <= -two_b[:, None, None]
        if np.any(up & dn):
            raise AssertionError("one update reached both barriers (P3.4)")
        hit = up | dn
        any_hit = hit.any(axis=2)
        k_star = np.where(any_hit, np.argmax(hit, axis=2) + 1, h)
        up_at = np.take_along_axis(up, (k_star - 1)[:, :, None], axis=2)[:, :, 0]
        y = np.where(any_hit, np.where(up_at, 1, -1), 0).astype(np.int8)
        jx = jb[None, :] + k_star
        bid_x = np.take_along_axis(bid[:, :, 2], jx, axis=1)
        ask_x = np.take_along_axis(ask[:, :, 2], jx, axis=1)
        exit_t = t_ns + k_star * MIN_NS + 2 * L_NS                              # tau + L = C_j
        n_long = (bid_x - ask_e).astype(np.float64) - FEE
        n_short = (bid_e - ask_x).astype(np.float64) - FEE
    entry_ok = np.zeros((nd, n), dtype=bool)
    for d in range(nd):
        if cal.excluded[N_BURN + d]:
            continue
        entry_ok[d] = ~release_hit(t_ns[d], t_ns[d] + L_NS + h * MIN_NS, cal.releases[N_BURN + d])
    row_ok = entry_ok.copy()              # the synthetic book: M_ZM(t) always valid, rule 5 never fires
    w = np.full((nd, n), np.nan)
    for d in range(nd):
        r = row_ok[d]
        if r.any():
            w[d, r] = uniqueness(t_ns[d, r], exit_t[d, r], int(cal.t0_ns[N_BURN + d]))
    out = {"i": np.broadcast_to(i.astype(np.int16), (nd, n)), "t_ns": t_ns.astype(np.int64),
           "entry_ok": entry_ok, "row_ok": row_ok,
           "y": np.where(row_ok, y, 0).astype(np.int8),
           "n_long": np.where(row_ok, n_long, np.nan), "n_short": np.where(row_ok, n_short, np.nan),
           "w": w, "span_end_ns": np.where(row_ok, exit_t, -1).astype(np.int64)}
    mid2_e = bid[:, :, 1] + ask[:, :, 1]
    excl = cal.excluded[oof][:, None]
    # TB uses the vertical h; NaN on excluded dates (no book is built there in production)
    out["mid_move"] = np.where(excl, np.nan, (mid2_e[:, jb + h] - mid2_e[:, jb]) / 2.0)
    for side, net in (("long", n_long), ("short", n_short)):
        out[f"{side}_made"] = entry_ok.copy()
        out[f"{side}_net"] = np.where(entry_ok, net, np.nan)
        out[f"{side}_entry_ns"] = np.where(entry_ok, entry_t, -1).astype(np.int64)
        out[f"{side}_exit_ns"] = np.where(entry_ok, exit_t, -1).astype(np.int64)
        out[f"{side}_flags"] = np.zeros((nd, n), dtype=np.int16)
    return out


# ---------------------------------------------------------------- the oracle (P4.2 planted calibration)
def drift_moments(beta: float, h: int, phi: float = PLANT_PHI) -> tuple:
    """Window B_i -> B_{i+h}: E[drift] = beta z_i g and Var[drift | z_i] = beta^2 vz for the AR(1) plant.
    Drift over minute j is beta z_j; the window covers 59/60 of minute i, minutes i+1..i+h-1 and 1/60 of i+h."""
    c = np.ones(h + 1)
    c[0], c[h] = 59.0 / 60.0, 1.0 / 60.0
    g = float(sum(c[m] * phi ** m for m in range(h + 1)))
    a = [sum(c[m] * phi ** (m - k) for m in range(k, h + 1)) for k in range(1, h + 1)]
    vz = (1.0 - phi * phi) * float(sum(x * x for x in a))
    return beta * g, beta * beta * vz


def _gint(x: np.ndarray) -> np.ndarray:
    """Antiderivative of the standard normal CDF: G(x) = x Phi(x) + phi(x)."""
    from scipy.special import ndtr
    return x * ndtr(x) + np.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def _avg_cdf(k: float, m: np.ndarray, s: np.ndarray, u0: float, u1: float) -> np.ndarray:
    """(1/(u1-u0)) int_{u0}^{u1} Phi((k - u - m)/s) du, exactly (closed form)."""
    x0, x1 = (k - u0 - m) / s, (k - u1 - m) / s
    return s * (_gint(x0) - _gint(x1)) / (u1 - u0)


def fh_class_probs(m: np.ndarray, v: np.ndarray, q: float = SPREAD2_SHARE) -> tuple:
    """True P(y = +1) and P(y = -1) of the FH label given Delta = X(B_{i+h}) - X(B_i) ~ N(m, v), the
    fractional part u of X(B_i) uniform on [0, 1) and independent spreads (1 tick w.p. 1 - q, else 2) at
    entry and exit. With n = floor(X(B_i)): ask_e - n = 1, or 1 + [u >= 1/2] at a 2-tick entry; bid_e - n = 0,
    or [u >= 1/2] - 1. y = +1 iff Delta >= ask_e - n + 1 - u (1-tick exit) or + 1.5 - u (2-tick exit);
    y = -1 iff Delta < bid_e - n - 1 - u (1-tick exit) or - 1.5 - u (2-tick exit)."""
    m, s = np.asarray(m, dtype=np.float64), np.sqrt(np.asarray(v, dtype=np.float64))
    p_up, p_dn = np.zeros_like(m), np.zeros_like(m)
    for s_e, pe in ((1, 1 - q), (2, q)):
        for s_x, px in ((1, 1 - q), (2, q)):
            for u0, u1, upper in ((0.0, 0.5, False), (0.5, 1.0, True)):
                a_e = 1 + (1 if (s_e == 2 and upper) else 0)
                b_e = 0 if s_e == 1 else (0 if upper else -1)
                k_up = a_e + (1.0 if s_x == 1 else 1.5)
                k_dn = b_e - (1.0 if s_x == 1 else 1.5)
                wgt = pe * px * (u1 - u0)
                p_up += wgt * (1.0 - _avg_cdf(k_up, m, s, u0, u1))
                p_dn += wgt * _avg_cdf(k_dn, m, s, u0, u1)
    return p_up, p_dn


def class_means(y, w, n_long, n_short) -> tuple:
    """Weighted mu_long_k, mu_short_k (k = -1, 0, +1) over rows (P3.5, P3.7 weights)."""
    mu_l, mu_s = [], []
    for k in (-1, 0, 1):
        sel = y == k
        sw = float(np.sum(w[sel]))
        mu_l.append(float(np.sum(w[sel] * n_long[sel]) / sw))
        mu_s.append(float(np.sum(w[sel] * n_short[sel]) / sw))
    return mu_l, mu_s


def simulate_day(t_ns, entry_ok, ev_long, ev_short, net_long, net_short, exit_long, exit_short,
                 cap: int = 20) -> tuple:
    """P3.8 for one date (independent of search33; cross-checked in tests): returns (sum of nets, trades)."""
    total, trades, pos, n = 0.0, 0, 0, len(t_ns)
    while pos < n and trades < cap:
        if not entry_ok[pos]:
            pos += 1
            continue
        el, es = float(ev_long[pos]), float(ev_short[pos])
        side = 1 if el > max(es, 0.0) else (-1 if es > max(el, 0.0) else 0)
        if side == 0:
            pos += 1
            continue
        total += float(net_long[pos] if side == 1 else net_short[pos])
        trades += 1
        ext = int(exit_long[pos] if side == 1 else exit_short[pos])
        pos = int(np.searchsorted(t_ns, ext, side="left"))
    return total, trades


def oracle_fh(cal: Calendar, path: Path_, lab: dict, beta: float, h: int = 15) -> dict:
    """The P4.2 oracle at FH h: P3.5 with the true class probabilities and the class-conditional means
    (weighted over all rows of the series, P3.7), P3.8 with f and the dead zone. Returns the daily series."""
    from screening.stage_e_verdict import moments
    oof = slice(N_BURN, len(cal.dates))
    n = lab["t_ns"].shape[1]
    zi = path.z[oof][:, PRE:PRE + n]
    g, vz = drift_moments(beta, h)
    m = g * zi
    v = (path.sigma[oof] ** 2 * h)[:, None] + vz
    p_up, p_dn = fh_class_probs(m, v)
    p0 = 1.0 - p_up - p_dn
    ok = lab["row_ok"]
    mu_l, mu_s = class_means(lab["y"][ok], lab["w"][ok], lab["n_long"][ok], lab["n_short"][ok])
    ev_l = p_dn * mu_l[0] + p0 * mu_l[1] + p_up * mu_l[2]
    ev_s = p_dn * mu_s[0] + p0 * mu_s[1] + p_up * mu_s[2]
    x, nt = [], []
    for d in range(lab["t_ns"].shape[0]):
        tot, k = simulate_day(lab["t_ns"][d], lab["entry_ok"][d], ev_l[d], ev_s[d], lab["long_net"][d],
                              lab["short_net"][d], lab["long_exit_ns"][d], lab["short_exit_ns"][d])
        x.append(tot)
        nt.append(k)
    mom = moments(x)
    return {"sharpe": mom["sharpe"], "mean": mom["mean"], "sd": mom["sd"], "trades": int(sum(nt)),
            "trades_per_date": sum(nt) / len(x), "mean_net_per_trade": (sum(x) / sum(nt)) if sum(nt) else None,
            "share_dates_with_trade": sum(1 for k in nt if k) / len(x), "mu_long": mu_l, "mu_short": mu_s,
            "beta": beta, "h": h, "x": x, "n_trades": nt}


# ---------------------------------------------------------------- one seed in memory
@dataclass
class SeedData:
    seed: int
    kind: str
    beta: float
    cal: Calendar
    path: Path_
    feats: np.ndarray | None
    labels: dict


def generate(seed: int, kind: str | None = None, n_oof: int | None = None, *, with_features: bool = True,
             labels=tuple(LABELS), beta: float | None = None) -> SeedData:
    kind = kind or kind_of_seed(seed)
    beta = beta_of(kind) if beta is None else beta
    cal = load_calendar(n_oof)
    rng = streams(seed)
    path = make_path(seed, beta, len(cal.dates), rng)
    feats = make_features(seed, cal, path, rng) if with_features else None
    labs = {lb: make_labels(lb, cal, path) for lb in labels}
    return SeedData(seed, kind, beta, cal, path, feats, labs)


# ---------------------------------------------------------------- writing (INTERFACE 4.1 / 4.2 layout)
def generator_sha256() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def _sha12(tag: str, seed: int, kind: str) -> str:
    return hashlib.sha256(f"{generator_sha256()}:{seed}:{kind}:{tag}".encode()).hexdigest()[:12]


def _write_parquet(path: Path, cols: dict) -> None:
    import pyarrow as pa
    import pyarrow.parquet as pq
    tmp = path.with_name(f".{path.name}.tmp")
    pq.write_table(pa.table(cols), tmp)
    os.replace(tmp, path)


def _write_json(path: Path, obj) -> None:
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(json.dumps(obj, indent=1, sort_keys=True))
    os.replace(tmp, path)


def write_seed(seed: int, root, kind: str | None = None, n_oof: int | None = None) -> dict:
    """Write DERIVED-like tables for one seed under root (features/<sha12>/, labels/<sha12>/<LABEL>/) and
    synth/{oracle,manifest}.json; a DONE marker last. Resumable: a finished seed is skipped."""
    root = Path(root)
    done = root / "synth" / "DONE"
    if done.exists():
        return json.loads(done.read_text())
    t_start = time.perf_counter()
    data = generate(seed, kind, n_oof)
    cal, kind = data.cal, data.kind
    fdir = root / "features" / _sha12("features", seed, kind)
    ldir = root / "labels" / _sha12("labels", seed, kind)
    for p in (fdir / "_day", root / "synth"):
        p.mkdir(parents=True, exist_ok=True)
    import pyarrow as pa
    for d, day in enumerate(cal.dates):
        sz = data.path.sigma_zm[d]
        _write_json(fdir / "_day" / f"{day}.json",
                    {"date": day, "fronts": cal.fronts[d], "segment": None, "synthetic": True,
                     "sigma_zm": float(sz) if np.isfinite(sz) else None,
                     "sigma_zs": 4.0 if np.isfinite(sz) else None,      # unused by the search (synthetic)
                     "sigma_zl": 9.0 if np.isfinite(sz) else None, "n_history": min(d, N_BURN)})
    i = np.arange(N_FEAT_MIN, dtype=np.int16)
    for d, day in enumerate(cal.dates[N_BURN:]):
        cols = {"date": pa.array([day] * N_FEAT_MIN, pa.string()), "i": i,
                "t_ns": cal.t0_ns[N_BURN + d] + i.astype(np.int64) * MIN_NS}
        for k, name in enumerate(FEATURE_COLUMNS):
            cols[name] = data.feats[d, :, k]
        _write_parquet(fdir / f"{day}.parquet", cols)
    for lb, lab in data.labels.items():
        (ldir / lb / "_excl").mkdir(parents=True, exist_ok=True)
        _, h = LABELS[lb]
        for d, day in enumerate(cal.dates[N_BURN:]):
            _write_parquet(ldir / lb / f"{day}.parquet", {c: lab[c][d] for c in LABEL_COLUMNS})
            excl_date = bool(cal.excluded[N_BURN + d])
            n = lab["t_ns"].shape[1]
            _write_json(ldir / lb / "_excl" / f"{day}.json",
                        {"date": day, "label": lb, "grid_minutes": int(n), "synthetic": True,
                         "entry_ok_minutes": int(lab["entry_ok"][d].sum()),
                         "rows_kept": int(lab["row_ok"][d].sum()), "excluded_date": excl_date,
                         "rows_removed_first_rule": {"r4_roll_calendar": int(n) if excl_date else 0,
                                                     "r3_release": 0 if excl_date else
                                                     int(n - lab["entry_ok"][d].sum())}})
    oracle = oracle_fh(cal, data.path, data.labels["F15"], data.beta) if "F15" in data.labels else None
    if oracle is not None:
        _write_json(root / "synth" / "oracle.json", {k: v for k, v in oracle.items() if k not in ("x", "n_trades")}
                    | {"note": "P4.2 oracle at F15 on this seed's series (P3.5 with the true class "
                               "probabilities and the weighted class means; P3.8; f; dead zone)"})
    manifest = {"seed": seed, "kind": kind, "beta": data.beta, "plant_feature": PLANT_FEATURE,
                "plant_phi": PLANT_PHI, "n_oof": cal.n_oof, "labels": list(data.labels),
                "generator_sha256": generator_sha256(), "features_sha12": fdir.name, "labels_sha12": ldir.name,
                "constants": {"SIGMA_1M_TARGET": SIGMA_1M_TARGET, "SPREAD2_SHARE": SPREAD2_SHARE,
                              "LOGVOL_SD": LOGVOL_SD, "LOGVOL_PHI": LOGVOL_PHI, "FEE": FEE, "SEED_TAG": SEED_TAG},
                "mean_sigma_zm_oof": float(np.nanmean(data.path.sigma_zm[N_BURN:])),
                "seconds": round(time.perf_counter() - t_start, 2)}
    for p in (fdir, ldir):
        _write_json(p / "manifest.json", manifest)
    _write_json(root / "synth" / "manifest.json", manifest)
    _write_json(done, manifest)
    return manifest


# ---------------------------------------------------------------- calibration of PLANT_BETA
CALIB_SEEDS = tuple(range(70001, 70061))       # never proof seeds
CHECK_SEEDS = tuple(range(80001, 80061))


def oracle_sharpe(seed: int, beta: float, cache: dict | None = None) -> float:
    """Oracle daily Sharpe at F15 for one draw (common random numbers across beta: same seed, same noise)."""
    cal = load_calendar(None)
    rng = streams(seed)
    path = make_path(seed, beta, len(cal.dates), rng)
    lab = make_labels("F15", cal, path)
    return oracle_fh(cal, path, lab, beta)["sharpe"]


def mean_oracle(seeds, beta: float) -> tuple:
    vals = np.array([oracle_sharpe(s, beta) for s in seeds])
    return float(vals.mean()), float(vals.std(ddof=1) / math.sqrt(len(vals))), vals


def calibrate(seeds=CALIB_SEEDS, check=CHECK_SEEDS, target: float = TARGET_ORACLE_SR, lo: float = 0.1,
              hi: float = 1.0, tol: float = 5e-4, log=None) -> dict:
    """Bisection on beta for mean_seeds(oracle SR) = target, then an independent check on fresh draws."""
    log = log or (lambda msg: print(msg, flush=True))
    t0 = time.perf_counter()
    m_lo, _, _ = mean_oracle(seeds, lo)
    m_hi, _, _ = mean_oracle(seeds, hi)
    log(f"bracket beta {lo}: {m_lo:.4f}; beta {hi}: {m_hi:.4f}")
    if not m_lo < target < m_hi:
        raise RuntimeError("target not bracketed")
    steps = []
    while hi - lo > tol:
        mid = 0.5 * (lo + hi)
        m_mid, se, _ = mean_oracle(seeds, mid)
        steps.append((mid, m_mid, se))
        log(f"beta {mid:.5f}: mean oracle SR {m_mid:.4f} (se {se:.4f}) [{time.perf_counter() - t0:.0f} s]")
        lo, hi = (mid, hi) if m_mid < target else (lo, mid)
    beta = round(0.5 * (lo + hi), 4)
    m_cal, se_cal, v_cal = mean_oracle(seeds, beta)
    m_chk, se_chk, v_chk = mean_oracle(check, beta)
    slope = (steps[-1][1] - steps[0][1]) / (steps[-1][0] - steps[0][0]) if len(steps) > 1 else float("nan")
    return {"beta": beta, "target": target, "calib_seeds": [seeds[0], seeds[-1]], "check_seeds": [check[0], check[-1]],
            "calib_mean": m_cal, "calib_se": se_cal, "calib_sd": float(np.std(v_cal, ddof=1)),
            "check_mean": m_chk, "check_se": se_chk, "check_sd": float(np.std(v_chk, ddof=1)),
            "check_values": [float(x) for x in v_chk], "bisection": steps, "tol": tol,
            "d_sr_d_beta_approx": slope, "seconds": round(time.perf_counter() - t0, 1)}


# ---------------------------------------------------------------- CLI
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("write")
    w.add_argument("--seed", type=int, required=True)
    w.add_argument("--root", type=Path, required=True)
    w.add_argument("--kind", choices=("null", "planted"))
    w.add_argument("--n-oof", type=int)
    c = sub.add_parser("calibrate")
    c.add_argument("--out", type=Path, required=True)
    c.add_argument("--draws", type=int, default=len(CALIB_SEEDS))
    o = sub.add_parser("oracle")
    o.add_argument("--seed", type=int, required=True)
    o.add_argument("--kind", choices=("null", "planted"))
    args = ap.parse_args(argv)
    if os.nice(0) < 10:
        os.nice(10 - os.nice(0))
    if args.cmd == "write":
        print(json.dumps(write_seed(args.seed, args.root, args.kind, args.n_oof), indent=1))
    elif args.cmd == "calibrate":
        res = calibrate(CALIB_SEEDS[:args.draws], CHECK_SEEDS[:args.draws])
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(res, indent=1))
        print(json.dumps({k: v for k, v in res.items() if k not in ("check_values", "bisection")}, indent=1))
    else:
        data = generate(args.seed, args.kind, with_features=False, labels=("F15",))
        res = oracle_fh(data.cal, data.path, data.labels["F15"], data.beta)
        print(json.dumps({k: v for k, v in res.items() if k not in ("x", "n_trades")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
