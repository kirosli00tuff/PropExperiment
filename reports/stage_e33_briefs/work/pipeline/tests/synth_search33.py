"""Synthetic feature and label tables in the INTERFACE.md 4.1 / 4.2 schemas, for search33's tests and
timing only (not the P4.2 proof generator, which belongs to another worker). Everything is synthetic."""
from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

CT = ZoneInfo("America/Chicago")
FEE = 0.528
FEAT_SHA = "aaaaaaaaaaaa"
LABEL_SHA = "bbbbbbbbbbbb"
N_MIN = 273
L_NS = 1_000_000_000
MIN_NS = 60 * L_NS


def synth_dates(n: int, start: str = "2020-12-30") -> list[str]:
    out, d = [], date.fromisoformat(start)
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d.isoformat())
        d += timedelta(days=1)
    return out


def grid_t_ns(d: str) -> np.ndarray:
    t0 = datetime.fromisoformat(d).replace(hour=8, minute=35, tzinfo=CT)
    base = int(t0.timestamp()) * 1_000_000_000
    return base + np.arange(N_MIN, dtype=np.int64) * MIN_NS


def uniqueness(ok: np.ndarray, h: int) -> np.ndarray:
    """P3.7 average uniqueness for FH spans of h one-minute intervals (rows only)."""
    n = len(ok)
    c = np.zeros(n + h)
    for i in np.flatnonzero(ok):
        c[i:i + h] += 1
    w = np.full(n, np.nan)
    for i in np.flatnonzero(ok):
        w[i] = np.mean(1.0 / c[i:i + h])
    return w


def write_tables(root, dates, labels=("F15",), *, seed=0, beta=0.0, move_sd=None, row_ok_share=0.9,
                 not_made_share=0.01, excluded_every=0, no_class=None, columns_const=("C_14",),
                 feat_sha=FEAT_SHA, label_sha=LABEL_SHA, with_mid_move=False, factor_corr=0.0):
    """Write features/<feat_sha>/ and labels/<label_sha>/<LABEL>/ for `dates` under root.
    beta: ticks of mid move per unit of F3_1 (the planted signal); no_class: a class never produced;
    factor_corr: share of variance from one common factor per family (ill-conditioned designs)."""
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import search33 as s
    root = Path(root)
    fdir = root / "features" / feat_sha
    (fdir / "_day").mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    for di, d in enumerate(dates):
        t_ns = grid_t_ns(d)
        x = rng.standard_normal((N_MIN, len(s.FEATURE_COLUMNS)))
        if factor_corr:
            fam = np.array([c.split("_")[0] for c in s.FEATURE_COLUMNS])
            for f in np.unique(fam):
                x[:, fam == f] = np.sqrt(1 - factor_corr) * x[:, fam == f] + \
                    np.sqrt(factor_corr) * rng.standard_normal((N_MIN, 1))
        x = np.clip(x, -5, 5)
        for j, c in enumerate(s.FEATURE_COLUMNS):
            if c in ("C_11", "C_12", "C_13"):
                x[:, j] = (rng.random(N_MIN) > 0.05).astype(float)
            if c in columns_const:
                x[:, j] = 1.0
        frame = pd.DataFrame(x, columns=list(s.FEATURE_COLUMNS))
        frame.insert(0, "t_ns", t_ns)
        frame.insert(0, "i", np.arange(N_MIN, dtype=np.int16))
        frame.insert(0, "date", d)
        frame.to_parquet(fdir / f"{d}.parquet", index=False)
        sig = float(2.0 + 2.0 * rng.random())
        (fdir / "_day" / f"{d}.json").write_text(json.dumps({"sigma_zm": sig, "sigma_zs": 1.0, "sigma_zl": 1.0}))
        excluded = bool(excluded_every) and di % excluded_every == excluded_every - 1
        z = x[:, s.FEATURE_COLUMNS.index("F3_1")]
        for label in labels:
            _write_label(root / "labels" / label_sha / label, d, label, s.LABEL_H[label], t_ns, z, sig, rng,
                         beta, move_sd, row_ok_share, not_made_share, excluded, no_class, with_mid_move)
    return root


def _write_label(ldir, d, label, h, t_full, z_full, sig, rng, beta, move_sd, row_ok_share, not_made_share,
                 excluded, no_class, with_mid_move):
    ldir.mkdir(parents=True, exist_ok=True)
    gs = 278 - h
    t_ns, z = t_full[:gs], z_full[:gs]
    sd = move_sd if move_sd is not None else 3.15 * np.sqrt(h)
    move = beta * z + sd * rng.standard_normal(gs)
    spread = np.where(rng.random(gs) < 0.8, 1.0, 2.0)
    n_long, n_short = move - spread - FEE, -move - spread - FEE
    if no_class == 1:
        n_long = -np.abs(n_long) - 0.1
    if no_class == -1:
        n_short = -np.abs(n_short) - 0.1
    if label.startswith("F"):
        y = np.where(n_long > 0, 1, np.where(n_short > 0, -1, 0))
        frac = np.ones(gs)
    else:
        b = sig * np.sqrt(h)
        y = np.where(move >= b, 1, np.where(move <= -b, -1, 0))
        if no_class is not None:
            y = np.where(y == no_class, 0, y)
        frac = np.where(y != 0, rng.uniform(0.2, 1.0, gs), 1.0)
    ok = (rng.random(gs) < row_ok_share) & (not excluded)
    entry_ok = (ok | (rng.random(gs) < 0.05)) & (not excluded)
    w = uniqueness(ok, h)
    exit_ns = t_ns + (frac * h * MIN_NS).astype(np.int64) + L_NS + rng.integers(0, 10**8, gs)
    cols = {"i": np.arange(gs, dtype=np.int16), "t_ns": t_ns, "entry_ok": entry_ok, "row_ok": ok,
            "y": np.where(ok, y, 0).astype(np.int8), "n_long": np.where(ok, n_long, np.nan),
            "n_short": np.where(ok, n_short, np.nan), "w": w,
            "span_end_ns": np.where(ok, t_ns + h * MIN_NS + L_NS, -1).astype(np.int64)}
    for side, net in (("long", n_long), ("short", n_short)):
        made = entry_ok & (rng.random(gs) >= not_made_share)
        fb = made & (rng.random(gs) < 0.01)
        cols[f"{side}_made"] = made
        cols[f"{side}_net"] = np.where(made, np.where(fb, net - 1.0, net), np.nan)
        cols[f"{side}_entry_ns"] = np.where(made, t_ns + L_NS + np.where(fb, 5 * 10**8, 0), -1).astype(np.int64)
        cols[f"{side}_exit_ns"] = np.where(made, exit_ns, -1).astype(np.int64)
        cols[f"{side}_flags"] = np.where(made, np.where(fb, 1, 0), np.where(entry_ok, 16, 0)).astype(np.int16)
    if with_mid_move:  # M_ZM(t+L+h) - M_ZM(t+L): defined on entry minutes, some exact zeros and NaNs
        u = rng.random(gs)
        cols["mid_move"] = np.where(entry_ok & (u >= 0.04), np.where(u < 0.10, 0.0, move), np.nan)
    pd.DataFrame(cols).to_parquet(ldir / f"{d}.parquet", index=False)
