"""The modelling panel: decision rows, normalized V2.3 features, flags, identifiers and targets.

docs/STAGE_E_ML_V2_DESIGN.md V2.3 (missing values, G18/G19), V2.4, V2.5; contract
reports/stage_e11_interfaces.md section 4.
- Features: compute_signals (assert_causal has run), then per signal: a value that is not
  applicable is masked before normalization, z_<name> = zscore_causal of the applicable values
  (normalize=True) or the raw value (flags, normalize=False), and 0 where not applicable;
  app_<name> = the applicability flag.
- G18/G19: id_root_<vehicle> and id_cluster_<K> one-hots (constants.UNIVERSE, CLUSTERS).
- Rows dropped (V2.3, no imputation): any applicable feature with no value, for data reasons
  (raw NaN) or because its z-score has no statistic yet (warm-up, V2.4). Counts by cause and by
  signal are in Panel.counts (addition to the contract). Panel.counts also holds, per (root,
  horizon), the kept rows whose target lost its cost (``cost_missing_<root>_<h>``: no calibrated
  cost bucket at a fill minute, so ok_<h> is False; targets.cost_missing_counts, code review C-05).
- feature_cols: the z_ columns, the app_ columns of the signals whose applicability can vary
  (the app_ column of an always-applicable signal, signals.ALWAYS_APPLICABLE: the pooled ports
  and the always-on generic features, is constant 1 and is left out; reading PN-1), then
  id_root_ and id_cluster_.
- assert_window: in "train" mode no trade date on or after constants.FORBIDDEN_FROM.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from ml_route_v2.clock import ROW_COLUMNS
from ml_route_v2.constants import CLUSTERS, FORBIDDEN_FROM, HORIZONS, UNIVERSE
from ml_route_v2.normalize import zscore_causal
from ml_route_v2.signals import ALWAYS_APPLICABLE, REGISTRY, SignalContext, compute_signals
from ml_route_v2.targets import cost_missing_counts

MODES = ("train", "eval")


class WindowError(RuntimeError):
    """A training-mode frame holds a trade date on or after FORBIDDEN_FROM."""


@dataclass(frozen=True)
class Panel:
    frame: pd.DataFrame
    feature_cols: tuple[str, ...]
    signal_names: tuple[str, ...]
    horizons: tuple[str, ...]
    avail_max_ts_ns: np.ndarray
    counts: Mapping[str, int] = field(default_factory=dict)


def assert_window(panel_or_rows: pd.DataFrame | Panel, mode: str = "train") -> None:
    """Raise WindowError in train mode if any trade_date >= FORBIDDEN_FROM."""
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}, not {mode!r}")
    frame = panel_or_rows.frame if isinstance(panel_or_rows, Panel) else panel_or_rows
    if mode != "train" or len(frame) == 0:
        return
    days = pd.to_datetime(frame["trade_date"]).dt.date
    late = days >= FORBIDDEN_FROM
    if bool(late.any()):
        raise WindowError(f"train mode: {int(late.sum())} rows on or after {FORBIDDEN_FROM} "
                          f"(first {days[late].min()})")


def _features(ctx: SignalContext, names: tuple[str, ...]
              ) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray, dict]:
    sig = compute_signals(ctx, names)
    raw = sig[[f"raw_{n}" for n in names]].to_numpy(np.float64)
    app = sig[[f"app_{n}" for n in names]].to_numpy(np.float64) > 0
    masked = pd.DataFrame(np.where(app, raw, np.nan), index=ctx.rows.index, columns=list(names))
    norm = [n for n in names if REGISTRY[n].normalize]
    z = masked.copy()
    if norm:
        z[norm] = zscore_causal(masked, ctx.rows, norm)
    zv = z.to_numpy(np.float64)
    missing_raw = app & ~np.isfinite(raw)
    no_stat = app & np.isfinite(raw) & ~np.isfinite(zv)
    counts = {"rows_in": int(len(ctx.rows))}
    for i, n in enumerate(names):
        if missing_raw[:, i].any():
            counts[f"missing_{n}"] = int(missing_raw[:, i].sum())
        if no_stat[:, i].any():
            counts[f"no_statistic_{n}"] = int(no_stat[:, i].sum())
    drop = (missing_raw | no_stat).any(axis=1)
    counts["rows_dropped_missing_data"] = int(missing_raw.any(axis=1).sum())
    counts["rows_dropped_no_statistic_only"] = int((no_stat.any(axis=1)
                                                    & ~missing_raw.any(axis=1)).sum())
    zf = pd.DataFrame(np.where(app, zv, 0.0), index=ctx.rows.index,
                      columns=[f"z_{n}" for n in names])
    af = pd.DataFrame(app.astype(np.float64), index=ctx.rows.index,
                      columns=[f"app_{n}" for n in names])
    avail = sig[[f"avail_{n}" for n in names]].to_numpy(np.int64)
    avail_max = np.where(app, avail, 0).max(axis=1) if len(names) else np.zeros(len(sig))
    return zf, af, np.asarray(drop), {"counts": counts, "avail_max": avail_max}


def _identifiers(rows: pd.DataFrame) -> pd.DataFrame:
    root = rows["root"].to_numpy(object)
    cluster = rows["cluster"].to_numpy(object)
    cols = {f"id_root_{v}": (root == v).astype(np.float64) for v in UNIVERSE}
    cols |= {f"id_cluster_{k}": (cluster == k).astype(np.float64) for k in CLUSTERS}
    return pd.DataFrame(cols, index=rows.index)


def build_panel(ctx: SignalContext, targets: pd.DataFrame, *, mode: str = "train",
                signals: Sequence[str] | None = None) -> Panel:
    """The panel of ``signals`` (REGISTRY order and all of it when None; Stage E.12 lead rule
    P-1: phase 1 passes only the signals its roots cover, the others enter as no feature)."""
    assert_window(ctx.rows, mode)
    if not targets.index.equals(ctx.rows.index):
        raise ValueError("targets are not aligned to the decision rows")
    names = tuple(REGISTRY) if signals is None else tuple(signals)
    if len(set(names)) != len(names):
        raise ValueError("duplicate signal names")
    zf, af, drop, extra = _features(ctx, names)
    ids = _identifiers(ctx.rows)
    frame = pd.concat([ctx.rows[list(ROW_COLUMNS)], zf, af, ids, targets], axis=1)
    keep = ~drop
    counts = dict(extra["counts"])
    counts["rows_out"] = int(keep.sum())
    frame = frame.loc[keep]
    counts.update(cost_missing_counts(frame))  # C-05
    avail_max = extra["avail_max"][keep]
    if np.any(avail_max > frame["decision_ts_ns"].to_numpy(np.int64)):
        raise RuntimeError("a kept feature is available after its decision time")
    feature_cols = (tuple(f"z_{n}" for n in names)
                    + tuple(f"app_{n}" for n in names if n not in ALWAYS_APPLICABLE)
                    + tuple(ids.columns))
    assert_window(frame, mode)
    return Panel(frame, feature_cols, names, HORIZONS, avail_max, counts)


__all__ = ["MODES", "Panel", "WindowError", "assert_window", "build_panel"]
