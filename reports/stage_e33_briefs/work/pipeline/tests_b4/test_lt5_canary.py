"""B4 LT5 leak canary (protocol P4.1 LT5): a deliberately leaked feature, the label shifted by one step
(LEAK(t) = y(t - 1 min), whose span ends at t - 1 min + h + L > t), must be caught by LT1 (truncation) and LT2
(span) and must give an absurd CV score through search33; then it is removed (it exists only in pytest's tmp
folders and is never a production column). Synthetic data only.

Interpretation (stated): "shifted by one step" = one grid minute back in time, the subtle form (the previous minute's
label looks like past information but is not known at t). The CV part uses search33's own run_fold /
finalize_config on synthetic INTERFACE-schema tables whose FH15 labels come from one random-walk mid path per date,
so neighbouring labels overlap by 14 of 15 minutes as real ones do."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

HERE = Path(__file__).resolve().parent
PIPE = HERE.parent
for _p in (str(HERE), str(PIPE), str(PIPE / "tests"), str(PIPE / "tests_b3")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import synth_labels as sl  # noqa: E402
import synth_streams as ss  # noqa: E402
import lab33  # noqa: E402
import compare_b3 as cb  # noqa: E402

NS = ss.NS
MIN = 60 * NS
LEAK_SEED = 20261027


# ---------------------------------------------------------------- the canary and an honest control --
def leak_from_labels(cols: dict, n_feat_rows: int = 273) -> tuple[np.ndarray, np.ndarray]:
    """LEAK(i) = y(i - 1) where row i - 1 is a row, else 0 (G3); returns (values, source span end per i)."""
    y, ok, end = cols["y"], cols["row_ok"], cols["span_end_ns"]
    val = np.zeros(n_feat_rows)
    src_end = np.full(n_feat_rows, -1, dtype=np.int64)
    for i in range(1, n_feat_rows):
        j = i - 1
        if j < len(y) and ok[j]:
            val[i] = float(y[j])
            src_end[i] = int(end[j])
    return val, src_end


def honest_ret5(hist: lab33.BookHistory, t_ns: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Control: mid change over the 5 minutes ending at t, from the book as of t and as of t - 5 min (in ticks).
    Its inputs end at t (window end = t)."""
    def mid(u: np.ndarray) -> np.ndarray:
        k = np.searchsorted(hist.t, u, side="right") - 1
        ok = k >= 0
        m = np.zeros(len(u))
        kk = np.where(ok, k, 0)
        m[ok] = (hist.bid[kk][ok] + hist.ask[kk][ok]) / 2.0
        return m
    return mid(t_ns) - mid(t_ns - 5 * MIN), t_ns.copy()


def lt2_window_violations(t_ns: np.ndarray, input_end_ns: np.ndarray) -> int:
    """LT2 feature part: a feature's inputs must end at or before t (input_end -1 = no input)."""
    return int(np.sum(input_end_ns > t_ns))


# ---------------------------------------------------------------- LT1 and LT2 catch it --
@pytest.fixture(scope="module")
def synth_day():
    day = ss.synth_dates(30)[4]
    arr, _ = ss.make_zm_day(day, 77, ss.ZMParams(rate_day=4.0, rate_night=1.0))
    return day, arr[arr["ts_recv"] < ss.ct_ns(day, 13, 20)]


def _labels_and_hist(day, arr, cutoff: int | None):
    rec = arr if cutoff is None else arr[arr["ts_recv"] <= cutoff]
    hist = lab33.replay(rec, 900_001, ss.TICK_FP["ZM"])
    di = lab33.DayInputs(date=day.isoformat(), t0_ns=ss.ct_ns(day, 8, 35), close_ns=ss.ct_ns(day, 13, 13),
                         session_end_ns=ss.ct_ns(day, 13, 20), releases=(), limits=None,
                         tick=ss.TICK_FP["ZM"], excluded=False, sigma_zm=3.15)
    cols, _ = lab33.compute_label(hist, di, "F15")
    return cols, hist


def test_canary_caught_by_lt1_truncation(synth_day) -> None:
    day, arr = synth_day
    full_cols, full_hist = _labels_and_hist(day, arr, None)
    t_grid = ss.ct_ns(day, 8, 35) + np.arange(273, dtype=np.int64) * MIN
    prod_leak, _ = leak_from_labels(full_cols)
    prod_ret, _ = honest_ret5(full_hist, t_grid)
    rng = np.random.default_rng(LEAK_SEED)
    sample = np.sort(rng.choice(np.arange(1, 262), size=40, replace=False))
    leak_bad = ret_bad = 0
    for i in sample.tolist():
        t = int(t_grid[i])
        cols_t, hist_t = _labels_and_hist(day, arr, t)
        re_leak, _ = leak_from_labels(cols_t)
        re_ret, _ = honest_ret5(hist_t, t_grid)
        leak_bad += int(not cb.eq_feature(np.array([prod_leak[i]]), np.array([re_leak[i]]))[0])
        ret_bad += int(not cb.eq_feature(np.array([prod_ret[i]]), np.array([re_ret[i]]))[0])
    assert ret_bad == 0  # the honest feature survives truncation at t
    assert leak_bad > 0  # the canary does not: LT1 catches it
    print(f"LT5 LT1: {len(sample)} truncation times; canary mismatches {leak_bad}; honest-feature mismatches {ret_bad}")


def test_canary_caught_by_lt2_span(synth_day) -> None:
    day, arr = synth_day
    cols, hist = _labels_and_hist(day, arr, None)
    t_grid = ss.ct_ns(day, 8, 35) + np.arange(273, dtype=np.int64) * MIN
    _, leak_end = leak_from_labels(cols)
    _, ret_end = honest_ret5(hist, t_grid)
    assert lt2_window_violations(t_grid, ret_end) == 0
    n_leak = lt2_window_violations(t_grid, leak_end)
    assert n_leak == int(np.sum(leak_end >= 0)) and n_leak > 200  # every defined canary value reaches past t
    print(f"LT5 LT2: canary rows reaching past t {n_leak} of {int(np.sum(leak_end >= 0))} defined; honest 0")


# ---------------------------------------------------------------- absurd CV score through search33 --
N_DATES = 60
H = 15


def _write_path_tables(root: Path, seed: int, leak: bool) -> None:
    import synth_search33 as g
    import search33 as s

    g.write_tables(root, g.synth_dates(N_DATES), ("F15",), seed=seed, beta=0.0)
    fdir = root / "features" / g.FEAT_SHA
    ldir = root / "labels" / g.LABEL_SHA / "F15"
    rng = np.random.default_rng(seed + 1)
    gs = 278 - H
    for d in g.synth_dates(N_DATES):
        t_ns = g.grid_t_ns(d)[:gs]
        path = np.concatenate([[0.0], np.cumsum(rng.normal(0.0, 3.15, 277))])  # mid at 08:35 + j min, ticks
        move = path[H:H + gs] - path[:gs]
        spread = np.where(rng.random(gs) < 0.8, 1.0, 2.0)
        n_long, n_short = move - spread - g.FEE, -move - spread - g.FEE
        y = np.where(n_long > 0, 1, np.where(n_short > 0, -1, 0)).astype(np.int8)
        ok = np.ones(gs, bool)
        cols = {"i": np.arange(gs, dtype=np.int16), "t_ns": t_ns, "entry_ok": ok, "row_ok": ok, "y": y,
                "n_long": n_long, "n_short": n_short, "w": g.uniqueness(ok, H),
                "span_end_ns": (t_ns + H * MIN + NS).astype(np.int64)}
        for side, net in (("long", n_long), ("short", n_short)):
            cols[f"{side}_made"] = ok
            cols[f"{side}_net"] = net
            cols[f"{side}_entry_ns"] = (t_ns + NS).astype(np.int64)
            cols[f"{side}_exit_ns"] = (t_ns + H * MIN + NS).astype(np.int64)
            cols[f"{side}_flags"] = np.zeros(gs, np.int16)
        pd.DataFrame(cols).to_parquet(ldir / f"{d}.parquet", index=False)
        if leak:
            fr = pd.read_parquet(fdir / f"{d}.parquet")
            v, _ = leak_from_labels({"y": y, "row_ok": ok, "span_end_ns": cols["span_end_ns"]})
            fr["F3_1"] = v  # the canary replaces one S5 column; never a production column name of its own
            fr.to_parquet(fdir / f"{d}.parquet", index=False)
    assert "LEAK" not in s.FEATURE_COLUMNS


def _run(root: Path) -> dict:
    import search33 as s

    cid = "E33-S5F15L010A"
    for k in range(1, 7):
        res = s.run_fold(root, cid, k, threads=1, expected_n=None)
        assert res["status"] == "done", res
    return s.finalize_config(root, cid, expected_n=None)


def test_canary_absurd_cv_score(tmp_path: Path) -> None:
    clean, leaky = tmp_path / "clean", tmp_path / "leak"
    _write_path_tables(clean, 5, leak=False)
    _write_path_tables(leaky, 5, leak=True)
    s_clean, s_leak = _run(clean), _run(leaky)
    t_clean, t_leak = s_clean["t_stat"], s_leak["t_stat"]
    sr_clean = s_clean["moments"]["sharpe"] if isinstance(s_clean["moments"], dict) else None
    sr_leak = s_leak["moments"]["sharpe"] if isinstance(s_leak["moments"], dict) else None
    print(f"LT5 CV: clean t {t_clean} SR {sr_clean} trades {s_clean['trade_count']}; "
          f"leaked t {t_leak} SR {sr_leak} trades {s_leak['trade_count']}")
    assert abs(t_clean) < 4.0
    assert t_leak > 10.0  # absurd: far beyond any threshold of P7.2 on 60 dates
