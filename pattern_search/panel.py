"""The search panel (reports/stage_e20_plan.md sections 4, 5 and 6): pipeline.build_world_panel's
steps recomposed with t4 rows, the 34 KEPT signals and the two r_ROD features, every frozen check
plan 6 names re-applied by name (review PR-4):

1. synthetic worlds only: pipeline.assert_bars_on_session_grid on the world's bars (V2.9's
   shifted-product guard). Real worlds (world.SearchWorld, source "real") skip it (lead ruling
   after the first check --world, V2.2b: "On real bars the session-grid check of the synthetic
   pipeline is replaced by the frozen loader's own L-3 booking check"; E.12's phase-1 world keeps
   and counts scheduled-closure bars, closure_counts, under harness v9's keep-and-flag ruling);
   their closure counts are recorded instead (run.closure_record). Then guard.check_frames (the
   guard's equivalent of phase1 world.refuse_late; the real world's loader has already run
   refuse_late, the degraded-day record, closure_counts and compact_bars);
2. rows: rows.search_rows (frozen t1-t3 plus t4);
3. SignalContext(rows, bars, releases, targets.sigma_d(rows, bars), blackout=world.blackout);
   targets.build_targets on every row (t4 included; build_targets marks h120 unavailable on t4
   rows by its own t + h <= F_X rule);
4. panel.build_panel(ctx, targets, mode="train", signals=the 34 KEPT names, exactly);
5. features.attach_rod (build_panel's three rules on the two rod columns; assert_causal);
6. the calendar cut (rows outside the training calendar dropped and counted) and the
   empty-panel refusal, as build_world_panel applies them; panel.assert_window(..., "train");
7. ``check_panel``: the feature names equal the plan's 36 exactly, feature_cols equal the frozen
   rule's columns plus the four rod columns, every feature is finite on every row (each kept row
   is an ok row of some horizon or carries no target), t4 rows have ok_h120 False, t_index is in
   1..4, avail_max <= decision_ts_ns.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Sequence
from typing import Any

import numpy as np
import pandas as pd

from pattern_search import constants as K
from pattern_search import guard
from pattern_search.features import attach_rod, rod_columns, rod_frame, rod_z
from pattern_search.rows import search_rows


class PanelCheckError(RuntimeError):
    """The composed panel breaks one of the plan's checks."""


def context(world: Any, rows: pd.DataFrame) -> Any:
    from ml_route_v2.signals import SignalContext
    from ml_route_v2.targets import sigma_d

    return SignalContext(rows, world.bars, world.releases, sigma_d(rows, world.bars),
                         blackout=world.blackout)


def is_real(world: Any) -> bool:
    """A real-data world (world.SearchWorld, source "real")."""
    return getattr(world, "source", None) == "real"


def build_search_panel(world: Any, *, check_grid: bool | None = None,
                       signals: Sequence[str] = K.KEPT_SIGNALS) -> Any:
    """The training panel of ``world`` (module docstring). ``check_grid`` None: the session-grid
    assertion on synthetic worlds only (never on real bars). ``signals`` stays the KEPT list in
    every search run; check_panel refuses any other list."""
    from ml_route_v2.panel import assert_window, build_panel
    from ml_route_v2.pipeline import PipelineError, assert_bars_on_session_grid
    from ml_route_v2.targets import build_targets

    grid = (not is_real(world)) if check_grid is None else check_grid
    if grid:
        assert_bars_on_session_grid(world.bars)
    guard.check_frames(world.bars)
    rows = search_rows(world)
    ctx = context(world, rows)
    targets = build_targets(rows, world.bars, releases=world.releases, costs=world.costs)
    panel = build_panel(ctx, targets, mode="train", signals=tuple(signals))
    panel = attach_rod(panel, ctx)
    keep = pd.to_datetime(panel.frame["trade_date"]).dt.date.isin(set(world.calendar))
    keep = keep.to_numpy()
    counts = dict(panel.counts)
    counts["rows_warmup_dropped"] = int((~keep).sum())
    counts["rows_training"] = int(keep.sum())
    out = dataclasses.replace(panel, frame=panel.frame.loc[keep],
                              avail_max_ts_ns=np.asarray(panel.avail_max_ts_ns)[keep],
                              counts=counts)
    assert_window(out, "train")
    if len(out.frame) == 0:
        raise PipelineError("the training panel is empty")
    check_panel(out)
    return out


def expected_feature_cols(signals: Sequence[str] = K.KEPT_SIGNALS) -> tuple[str, ...]:
    """build_panel's feature_cols for ``signals`` (its frozen rule) plus attach_rod's columns."""
    from ml_route_v2.constants import CLUSTERS, UNIVERSE
    from ml_route_v2.signals import ALWAYS_APPLICABLE

    return (tuple(f"z_{n}" for n in signals)
            + tuple(f"app_{n}" for n in signals if n not in ALWAYS_APPLICABLE)
            + tuple(f"id_root_{v}" for v in UNIVERSE) + tuple(f"id_cluster_{k}" for k in CLUSTERS)
            + rod_columns())


def check_panel(panel: Any) -> dict[str, Any]:
    """The plan's panel checks (module docstring, item 7); PanelCheckError on any failure."""
    from ml_route_v2.constants import HORIZONS

    if tuple(panel.signal_names) != K.FEATURE_NAMES:
        raise PanelCheckError(f"the feature list is not the plan's 36: {panel.signal_names}")
    if tuple(panel.feature_cols) != expected_feature_cols():
        raise PanelCheckError("feature_cols differ from the frozen rule plus the rod columns")
    frame = panel.frame
    t_index = frame["t_index"].to_numpy(np.int64)
    if not set(np.unique(t_index).tolist()) <= {1, 2, 3, K.T4_INDEX}:
        raise PanelCheckError(f"t_index outside 1..4: {sorted(set(t_index.tolist()))}")
    t4 = t_index == K.T4_INDEX
    if bool(frame["ok_h120"].to_numpy(bool)[t4].any()):
        raise PanelCheckError("a t4 row is ok for h120")
    X = frame[list(panel.feature_cols)].to_numpy(np.float64)
    bad = ~np.isfinite(X).all(axis=1)
    if bad.any():
        raise PanelCheckError(f"{int(bad.sum())} rows hold a non-finite feature")
    if np.any(np.asarray(panel.avail_max_ts_ns) > frame["decision_ts_ns"].to_numpy(np.int64)):
        raise PanelCheckError("a kept feature is available after its decision time")
    ok = {h: int(frame[f"ok_{h}"].to_numpy(bool).sum()) for h in HORIZONS}
    ok_t4 = {h: int(frame[f"ok_{h}"].to_numpy(bool)[t4].sum()) for h in HORIZONS}
    return {"rows": int(len(frame)), "rows_t4": int(t4.sum()), "ok_rows": ok, "ok_rows_t4": ok_t4,
            "rows_by_t_index": {int(k): int((t_index == k).sum()) for k in np.unique(t_index)},
            "n_features": len(K.FEATURE_NAMES), "n_feature_cols": len(panel.feature_cols)}


def feature_frame(ctx: Any, signals: Sequence[str] = K.KEPT_SIGNALS) -> pd.DataFrame:
    """Every model input before the row drop, aligned to ctx.rows: raw_ and app_ of the KEPT
    signals and both rod features, and their z columns (the perturbation tests' callable)."""
    from ml_route_v2.normalize import zscore_causal
    from ml_route_v2.signals import REGISTRY, compute_signals

    names = tuple(signals)
    sig = compute_signals(ctx, names)
    raw = sig[[f"raw_{n}" for n in names]].to_numpy(np.float64)
    app = sig[[f"app_{n}" for n in names]].to_numpy(np.float64) > 0
    masked = pd.DataFrame(np.where(app, raw, np.nan), index=ctx.rows.index, columns=list(names))
    norm = [n for n in names if REGISTRY[n].normalize]
    z = zscore_causal(masked, ctx.rows, norm) if norm else masked.iloc[:, :0]
    rod = rod_frame(ctx)
    r_raw, r_app, r_z = rod_z(rod, ctx.rows)
    cols = {**{c: sig[c].to_numpy(np.float64) for c in sig.columns if not c.startswith("avail_")},
            **{f"z_{n}": z[n].to_numpy(np.float64) for n in norm}}
    for i, n in enumerate(K.ROD_SIGNALS):
        cols[f"raw_{n}"] = r_raw[:, i]
        cols[f"app_{n}"] = r_app[:, i].astype(np.float64)
        cols[f"z_{n}"] = r_z[:, i]
    return pd.DataFrame(cols, index=ctx.rows.index)


__all__ = ["PanelCheckError", "build_search_panel", "check_panel", "context",
           "expected_feature_cols", "feature_frame", "is_real"]
