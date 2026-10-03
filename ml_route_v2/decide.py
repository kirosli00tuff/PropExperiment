"""The decision layer: the cost gate and the candidate trades (V2.7, F7; interfaces section 6).

At decision time, for the selected configuration's horizon h and multiple k:
- r_hat_ticks = r_hat x sigma_X,d (the caller converts; cpcv.py does it before score_fn);
- c_long and c_short are the row's D8 round trips at size 1 for each side (cost_long_<h>,
  cost_short_<h>, vehicle ticks);
- the reading is constants.COST_GATE_READING (design review D-05; looked up at call time, never
  a literal here; ``reading=`` overrides it):
  - "gross" (the built default, decided by the user, V23 item 1): long iff r_hat_ticks > k x
    c_long; short iff -r_hat_ticks > k x c_short; the hurdles are 1.5 c, 2 c and 3 c;
  - "net" (the literal F7 wording, kept selectable): long iff r_hat_ticks - c_long > k x c_long;
    short iff -r_hat_ticks - c_short > k x c_short. The predicted net edge exceeds k round trips,
    so the predicted gross must exceed (1 + k) c;
  else no trade. With positive costs both sides cannot pass at once.
- edge_over_cost = the taken side's predicted net edge over its cost, (|r_hat| - c) / c, in both
  readings (V2.7's ranking quantity e / c); NaN where no trade.
- release_window (V23 item 11; E.12 lead rule P-5): the row's own flag from targets.py (its entry
  fill lies in [r - 5 min, r + 30 min) of a release r of the vehicle's list), carried unchanged so
  the portfolio layer can apply the release-window rule.

candidates() returns one row per traded decision row with the section 6 columns plus
release_window, sorted by decision_ts_ns, then edge_over_cost descending, then root (V2.7's
ranking at one clock time).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ml_route_v2 import constants as v2c
from ml_route_v2.configs import Config

COST_GATE_READINGS = ("net", "gross")

# interfaces section 6, plus release_window (V23 item 11, the portfolio's release-window rule)
CANDIDATE_COLUMNS = ("root", "cluster", "trade_date", "decision_ts_ns", "horizon", "exit_ts_ns",
                     "side", "r_hat_ticks", "cost_ticks", "edge_over_cost", "release_window")


class DecisionError(ValueError):
    """Unusable inputs to the cost gate."""


def _vector(values: np.ndarray, name: str, n: int | None = None) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    if arr.ndim != 1:
        raise DecisionError(f"{name} must be 1-D, got shape {arr.shape}")
    if n is not None and arr.shape[0] != n:
        raise DecisionError(f"{name} has {arr.shape[0]} values, expected {n}")
    if not np.isfinite(arr).all():
        raise DecisionError(f"{name} holds a non-finite value")
    return arr


def gate_reading(reading: str | None = None) -> str:
    """The cost gate's reading: ``reading`` or constants.COST_GATE_READING (looked up now)."""
    mode = v2c.COST_GATE_READING if reading is None else reading
    if mode not in COST_GATE_READINGS:
        raise DecisionError(f"cost gate reading {mode!r} not in {COST_GATE_READINGS}")
    return mode


def cost_gate(r_hat_ticks: np.ndarray, cost_long: np.ndarray, cost_short: np.ndarray,
              k: float, *, reading: str | None = None) -> tuple[np.ndarray, np.ndarray]:
    """(side int8 in {-1, 0, 1}, edge over cost of the taken side; NaN where side is 0)."""
    mode = gate_reading(reading)
    r = _vector(r_hat_ticks, "r_hat_ticks")
    cl = _vector(cost_long, "cost_long", r.shape[0])
    cs = _vector(cost_short, "cost_short", r.shape[0])
    if not (np.isfinite(k) and k >= 0):
        raise DecisionError(f"k {k!r} must be finite and >= 0")
    if (cl <= 0).any() or (cs <= 0).any():
        raise DecisionError("a round-trip cost is not positive")
    edge_long, edge_short = r - cl, -r - cs
    if mode == "net":
        is_long = edge_long > k * cl
        is_short = edge_short > k * cs
    else:
        is_long = r > k * cl
        is_short = -r > k * cs
    side = np.zeros(r.shape[0], dtype=np.int8)
    side[is_long] = 1
    side[is_short] = -1
    ratio = np.full(r.shape[0], np.nan, dtype=np.float64)
    ratio[is_long] = edge_long[is_long] / cl[is_long]
    ratio[is_short] = edge_short[is_short] / cs[is_short]
    return side, ratio


def _exit_ts(rows: pd.DataFrame, horizon: str) -> np.ndarray:
    """The horizon's exit, or the flatten where the exit is missing: NaN, or <= 0 (targets.py
    encodes a missing exit as -1; code review C-06)."""
    col = f"exit_ts_ns_{horizon}"
    if col not in rows.columns:
        if "flatten_ts_ns" not in rows.columns:
            raise DecisionError(f"rows lack {col} and flatten_ts_ns")
        return rows["flatten_ts_ns"].to_numpy(dtype=np.int64)
    exit_ = pd.to_numeric(rows[col], errors="raise")
    # -1 (targets' missing exit) and NaN alike; int64 stays int64 (no float rounding of ns)
    missing = exit_.isna().to_numpy() | (exit_.fillna(1).to_numpy() <= 0)
    if not missing.any():
        return exit_.to_numpy(dtype=np.int64)
    if "flatten_ts_ns" not in rows.columns:
        raise DecisionError(f"{col} is missing and rows lack flatten_ts_ns")
    flatten = rows["flatten_ts_ns"].to_numpy(dtype=np.int64)
    return np.where(missing, flatten, exit_.fillna(0).to_numpy(dtype=np.int64))


def candidates(rows: pd.DataFrame, r_hat_ticks: np.ndarray, config: Config, *,
               reading: str | None = None) -> pd.DataFrame:
    """The section 6 candidate trades of one configuration on rows (r_hat aligned to rows)."""
    h = config.horizon
    need = ["root", "cluster", "trade_date", "decision_ts_ns", f"cost_long_{h}",
            f"cost_short_{h}", "release_window"]
    missing = [c for c in need if c not in rows.columns]
    if missing:
        raise DecisionError(f"rows lack columns {missing}")
    if not pd.api.types.is_bool_dtype(rows["release_window"]):
        raise DecisionError(f"release_window is {rows['release_window'].dtype}, not bool")
    r = _vector(r_hat_ticks, "r_hat_ticks", len(rows))
    cl = rows[f"cost_long_{h}"].to_numpy(dtype=np.float64)
    cs = rows[f"cost_short_{h}"].to_numpy(dtype=np.float64)
    side, ratio = cost_gate(r, cl, cs, config.k, reading=reading)
    take = side != 0
    out = pd.DataFrame({
        "root": rows["root"].to_numpy()[take],
        "cluster": rows["cluster"].to_numpy()[take],
        "trade_date": rows["trade_date"].to_numpy()[take],
        "decision_ts_ns": rows["decision_ts_ns"].to_numpy(dtype=np.int64)[take],
        "horizon": h,
        "exit_ts_ns": _exit_ts(rows, h)[take],
        "side": side[take].astype(np.int8),
        "r_hat_ticks": r[take],
        "cost_ticks": np.where(side == 1, cl, cs)[take],
        "edge_over_cost": ratio[take],
        "release_window": rows["release_window"].to_numpy(dtype=bool)[take],
    }, columns=list(CANDIDATE_COLUMNS))
    out = out.sort_values(["decision_ts_ns", "edge_over_cost", "root"],
                          ascending=[True, False, True], kind="mergesort")
    return out.reset_index(drop=True)
