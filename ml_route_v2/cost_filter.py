"""V2.2 c/sigma filter and the per-(product, horizon) risk table, on training rows only.

docs/STAGE_E_ML_V2_DESIGN.md V2.2 "The c/sigma filter" and V2.8 (L(p,h)); contract
reports/stage_e11_interfaces.md section 4. One row per (root, horizon), over the rows whose
target is formed (ok_<h>):
- c_ticks: mean of max(cost_long, cost_short), the D8 round trip at size 1 in vehicle ticks;
- sigma_ticks: sd (ddof 1) of y_gross;
- ratio = c / sigma; admissible: ratio <= constants.C_SIGMA_TAU (0.167, V23 item 1: under the
  gross reading the loosest hurdle 1.5 c is 0.25 sigma; looked up at call time);
- loss_ticks: the LOSS_QUANTILE quantile of |y_gross|;
- n_rows.
The filter reads volatility and cost only, never a return's sign or mean. Both tables refuse a
frame holding any trade date on or after FORBIDDEN_FROM (panel.assert_window, train mode).
``risk_table(..., roots=...)`` also lists the given roots that have no row in the frame (n_rows 0,
NaN figures): a split's table then names every pair of the run, and a pair it cannot estimate is
NaN rather than absent (code review C-02; portfolio.join_risk skips NaN pairs as risk_unknown and
raises only for an absent pair).
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd

from ml_route_v2 import constants as v2c
from ml_route_v2.constants import HORIZONS, LOSS_QUANTILE
from ml_route_v2.panel import Panel, assert_window

COLUMNS = ("root", "horizon", "c_ticks", "sigma_ticks", "ratio", "admissible", "loss_ticks",
           "n_rows")


def _frame(panel: pd.DataFrame | Panel) -> pd.DataFrame:
    frame = panel.frame if isinstance(panel, Panel) else panel
    assert_window(frame, "train")
    return frame


def _table(frame: pd.DataFrame, extra_roots: Sequence[str] = ()) -> pd.DataFrame:
    recs = []
    tau = v2c.C_SIGMA_TAU  # V23 item 1 (call time)
    roots = frame["root"].to_numpy(object)
    for root in sorted(set(map(str, pd.unique(roots))) | set(map(str, extra_roots))):
        sel = roots == root
        for h in HORIZONS:
            ok = sel & frame[f"ok_{h}"].to_numpy(bool)
            y = frame[f"y_gross_{h}"].to_numpy(np.float64)[ok]
            c = np.maximum(frame[f"cost_long_{h}"].to_numpy(np.float64)[ok],
                           frame[f"cost_short_{h}"].to_numpy(np.float64)[ok])
            n = int(ok.sum())
            c_mean = float(c.mean()) if n else np.nan
            sd = float(np.std(y, ddof=1)) if n >= 2 else np.nan
            ratio = c_mean / sd if (n >= 2 and sd > 0) else np.nan
            loss = float(np.quantile(np.abs(y), LOSS_QUANTILE)) if n else np.nan
            recs.append((root, h, c_mean, sd, ratio, bool(np.isfinite(ratio)
                         and ratio <= tau), loss, n))
    return pd.DataFrame.from_records(recs, columns=list(COLUMNS))


def c_sigma_table(panel: pd.DataFrame | Panel) -> pd.DataFrame:
    """V2.2's filter table on the training rows (refuses later dates)."""
    return _table(_frame(panel))


def risk_table(panel: pd.DataFrame | Panel, *, roots: Sequence[str] = ()) -> pd.DataFrame:
    """sigma(p,h), L(p,h) and the mean cost per (root, horizon), training rows only; ``roots``
    absent from the rows get NaN rows (module docstring)."""
    return _table(_frame(panel), roots)


def admissible_roots(table: pd.DataFrame) -> tuple[str, ...]:
    """Products with at least one admissible horizon (the others are dropped, V2.2)."""
    return tuple(sorted(table.loc[table["admissible"], "root"].unique()))


__all__ = ["COLUMNS", "admissible_roots", "c_sigma_table", "risk_table"]
