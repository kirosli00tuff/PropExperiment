"""The two r_ROD features (reports/stage_e20_plan.md section 5.2; F6 addition 2), computed from
frozen helpers and attached to the frozen Panel by dataclasses.replace (codemap_clock Q2, Q6).

rod_ret(t) = P(t) / P(prior C) - 1, per row:
- P(t): the close of the bar closing at t on the row's trade date (signals.generic._own "it",
  the G1-G4 convention);
- P(prior C): the close of the bar opening at C - 1 min on the previous trade date of the
  vehicle's group calendar (signals.generic._previous_trade_day), C from D6's frozen day session
  (signals._daily.daily_of(...).c1_close; the G5 pattern);
- not applicable (0, flag 0) when the previous trade date is an early-halt date of the group
  calendar (signals._daily.halt_flags; as G5); missing (the row is dropped) when P(t) or the prior
  C bar is absent, or there is no previous trade date;
- available at the later of the two bars' closes, which is t (asserted).
rod_absratio(t) = |rod_ret(t)| / median(|rod_ret|) over the 60 most recent earlier row dates of
the same vehicle and t_index on which rod_ret is applicable and present (rows strictly before
the row's trade date; the _base_ratio pattern, with 60 dates and only eligible rows in the
window). Fewer than 60 such dates: missing (warm-up). Not applicable when rod_ret is not
applicable, and when the median is 0. Available at t.

Each enters the panel as z_<name> (normalize.zscore_causal, 250 / 60 / clip 5, per vehicle over
all its rows, as build_panel normalizes) and app_<name>; ``attach_rod`` applies build_panel's
rules itself: a value not applicable is 0 with flag 0; a row whose applicable value is missing or
has no z statistic is dropped; avail_max <= decision_ts_ns is asserted; signals.assert_causal runs
on the rod frame.
"""

from __future__ import annotations

import dataclasses
from typing import Any

import numpy as np
import pandas as pd

from pattern_search import constants as K
from pattern_search import guard  # noqa: F401  (F3)

NS_MIN = 60_000_000_000


class FeatureError(RuntimeError):
    """A rod value breaks the plan's rule (late, non-finite on a kept row)."""


def _rod_ret(ctx: Any) -> pd.DataFrame:
    from ml_route_v2.signals._core import empty, result, rows_of
    from ml_route_v2.signals._daily import daily_of, halt_flags
    from ml_route_v2.signals.generic import _by_vehicle, _own, _previous_trade_day

    view, own = rows_of(ctx), _own(ctx)
    value, app, avail = empty(view)
    for v, rows, b in _by_vehicle(ctx):
        dl = daily_of(ctx, v)
        days = view.day[rows]
        prev = np.array([_previous_trade_day(v, int(d)) for d in days], dtype=np.int64)
        has_prev = prev >= 0
        ppos = np.where(has_prev, dl.pos(np.where(has_prev, prev, 0)), -1)
        c1 = np.where(ppos >= 0, dl.c1_idx[np.clip(ppos, 0, None)], -1)
        it = own["it"][rows]
        ok = (it >= 0) & (c1 >= 0)
        val = np.full(len(rows), np.nan)
        val[ok] = b.close[it[ok]] / b.close[c1[ok]] - 1.0
        value[rows] = val
        late = np.full(len(rows), -1, dtype=np.int64)
        late[ok] = np.maximum(b.ts[it[ok]], b.ts[c1[ok]]) + NS_MIN
        avail[rows] = late
        halt_prev = np.zeros(len(rows), dtype=bool)
        if has_prev.any():
            halt_prev[has_prev] = halt_flags(v, prev[has_prev])
        app[rows] = ~halt_prev
    return result(view, value, app, avail)


def _rod_absratio(ctx: Any, ret: pd.DataFrame) -> pd.DataFrame:
    from ml_route_v2.signals._core import empty, result, rows_of

    view = rows_of(ctx)
    r_app = ret["applicable"].to_numpy(np.float64) > 0
    r_val = ret["value"].to_numpy(np.float64)
    value, app, avail = empty(view)
    app[:] = r_app
    eligible = r_app & np.isfinite(r_val)
    for v in pd.unique(view.root):
        for k in np.unique(view.t_index[view.root == v]):
            sel = np.flatnonzero((view.root == v) & (view.t_index == k))
            order = sel[np.argsort(view.day[sel], kind="mergesort")]
            if len(np.unique(view.day[order])) != len(order):
                raise FeatureError(f"{v} t{k}: two rows on one trade date")
            elig = order[eligible[order]]
            med = (pd.Series(np.abs(r_val[elig])).rolling(K.ROD_MEDIAN_DATES,
                                                            min_periods=K.ROD_MEDIAN_DATES)
                   .median().shift(1).to_numpy())
            zero = np.isfinite(med) & (med == 0.0)
            with np.errstate(divide="ignore", invalid="ignore"):
                value[elig] = np.where(zero, np.nan, np.abs(r_val[elig]) / med)
            app[elig[zero]] = False
    avail[:] = np.where(np.isfinite(value), view.t, -1)
    return result(view, value, app, avail)


def rod_frame(ctx: Any) -> pd.DataFrame:
    """raw_/app_/avail_ of rod_ret and rod_absratio aligned to ctx.rows; assert_causal has run."""
    from ml_route_v2.signals import assert_causal

    ret = _rod_ret(ctx)
    ratio = _rod_absratio(ctx, ret)
    cols: dict[str, np.ndarray] = {}
    for name, frame in ((K.ROD_RET, ret), (K.ROD_ABSRATIO, ratio)):
        cols[f"raw_{name}"] = frame["value"].to_numpy(np.float64)
        cols[f"app_{name}"] = frame["applicable"].to_numpy(np.float64)
        cols[f"avail_{name}"] = frame["avail_ts_ns"].to_numpy(np.int64)
    out = pd.DataFrame(cols, index=ctx.rows.index)
    assert_causal(out, ctx.rows)
    return out


def rod_z(frame: pd.DataFrame, rows: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(raw, app, z) arrays (rows x 2) with the frozen normalization of applicable values."""
    from ml_route_v2.normalize import zscore_causal

    names = list(K.ROD_SIGNALS)
    raw = frame[[f"raw_{n}" for n in names]].to_numpy(np.float64)
    app = frame[[f"app_{n}" for n in names]].to_numpy(np.float64) > 0
    masked = pd.DataFrame(np.where(app, raw, np.nan), index=rows.index, columns=names)
    z = zscore_causal(masked, rows, names).to_numpy(np.float64)
    return raw, app, z


def rod_columns() -> tuple[str, ...]:
    """The four columns attach_rod adds to feature_cols, in order."""
    return (*(f"z_{n}" for n in K.ROD_SIGNALS), *(f"app_{n}" for n in K.ROD_SIGNALS))


def attach_rod(panel: Any, ctx: Any, frame: pd.DataFrame | None = None) -> Any:
    """The panel with z_ and app_ columns of both rod features, build_panel's three rules applied
    (module docstring), feature_cols and signal_names extended, counts recorded."""
    frame = rod_frame(ctx) if frame is None else frame
    if not frame.index.equals(ctx.rows.index):
        raise FeatureError("the rod frame is not aligned to the decision rows")
    raw, app, z = rod_z(frame, ctx.rows)
    missing = app & ~np.isfinite(raw)
    no_stat = app & np.isfinite(raw) & ~np.isfinite(z)
    pos = ctx.rows.index.get_indexer(panel.frame.index)
    if (pos < 0).any():
        raise FeatureError("panel rows are not decision rows of the context")
    keep = ~(missing | no_stat).any(axis=1)[pos]
    sub = pos[keep]
    names = list(K.ROD_SIGNALS)
    extra = pd.DataFrame(
        {**{f"z_{n}": np.where(app[sub, i], z[sub, i], 0.0) for i, n in enumerate(names)},
         **{f"app_{n}": app[sub, i].astype(np.float64) for i, n in enumerate(names)}},
        index=panel.frame.index[keep])
    avail = frame[[f"avail_{n}" for n in names]].to_numpy(np.int64)
    rod_avail = np.where(app, avail, 0).max(axis=1)[sub]
    avail_max = np.maximum(np.asarray(panel.avail_max_ts_ns)[keep], rod_avail)
    out_frame = pd.concat([panel.frame.loc[keep], extra], axis=1)
    if np.any(avail_max > out_frame["decision_ts_ns"].to_numpy(np.int64)):
        raise FeatureError("a kept feature is available after its decision time")
    counts = dict(panel.counts)
    for i, n in enumerate(names):
        counts[f"missing_{n}"] = int(missing[pos, i].sum())
        counts[f"no_statistic_{n}"] = int(no_stat[pos, i].sum())
    counts["rows_dropped_rod"] = int((~keep).sum())
    counts["rows_out"] = int(keep.sum())
    return dataclasses.replace(panel, frame=out_frame,
                               feature_cols=tuple(panel.feature_cols) + rod_columns(),
                               signal_names=tuple(panel.signal_names) + tuple(names),
                               avail_max_ts_ns=avail_max, counts=counts)


__all__ = ["FeatureError", "attach_rod", "rod_columns", "rod_frame", "rod_z"]
