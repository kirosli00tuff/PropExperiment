"""Trade-level reported items of the SCREEN (reports/stage_e20_plan.md section 9, "Reported, not
gating"), from refits of the nested CPCV's outer models (composition of frozen functions only).

Each outer split's model of a configuration is refit on that split's purged and embargoed
training rows exactly as cpcv._fit_and_score and pipeline._nested_schedule fit it, and its
sha256 must equal the CPCV record (nested.selected_sha256, or outer_table's sha256 for the final
configuration); the validation set is then scored with the split's own risk table
(pipeline.split_risk_fn on the split's training rows), as cpcv scores it.

- ``SplitTrades``: the accepted trades of one (configuration, split): decide.candidates,
  selection_metric._scorable, portfolio.join_risk, portfolio.accept_trades at D = $2,000 (the
  steps of selection_metric.score_split), with t_index joined from the rows; its daily net $
  (portfolio.fixed_d_daily_pnl reindexed to the validation dates) must equal score_split's.
- Nested record (each split's selected configuration): per-product round trips per path (path j
  takes block b from split paths[j][b]) and over all five paths (each (split, block) once), with
  products below 30 flagged under three readings (stop item: the plan names no reading); the
  1.5 x slippage re-pricing (score_split with slippage_multiple 1.5 on each split's selected
  configuration, assembled with pipeline.assemble_record; the 1.0 x record must reproduce
  nested.path_daily within $1e-6, pipeline._nested_schedule's check).
- Final configuration: its CPCV OOS net P&L over the 15 outer splits (each block's trades of the
  5 splits testing it; config_daily is that sum divided by 5, checked); the t4 share (its accepted
  t4 trades' net P&L over the total) and the r_ROD share (1 - P&L with z_rod_ret and
  z_rod_absratio set to 0 at prediction, same models, no refit, over P&L as fitted; both P&L
  figures shown); its five path series' daily t.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from pattern_search import constants as K
from pattern_search import guard  # noqa: F401  (F3)

TOL_USD = 1e-6  # pipeline.COST_CHECK_TOL_USD
ROD_Z_COLUMNS = tuple(f"z_{n}" for n in K.ROD_SIGNALS)


class OOSCheckError(RuntimeError):
    """A refit or re-score does not reproduce the CPCV record."""


@dataclass(frozen=True)
class SplitFit:
    split: int
    model: Any
    rows: pd.DataFrame  # validation rows (horizon_data rows), panel order
    X: np.ndarray  # validation features
    sigma: np.ndarray
    risk: pd.DataFrame  # the split's own training-row risk table


class Refits:
    """Refits of outer models, cached per (model_id, horizon, split) (fits are shared by k)."""

    def __init__(self, panel: Any, nested: Any, admissible: Sequence[tuple[str, str]],
                 risk_fn: Callable[[pd.DataFrame], pd.DataFrame]) -> None:
        self.panel, self.nested = panel, nested
        self.adm = tuple(admissible) if admissible else None
        self.risk_fn = risk_fn
        self._data: dict[str, Any] = {}
        self._fits: dict[tuple[str, str, int], SplitFit] = {}
        sha = nested.outer_table[["config_id", "split", "sha256"]]
        self._sha = {(str(c), int(s)): v for c, s, v in sha.itertuples(index=False)}

    def data(self, horizon: str) -> Any:
        from ml_route_v2.cpcv import horizon_data

        if horizon not in self._data:
            self._data[horizon] = horizon_data(self.panel, horizon, self.adm)
        return self._data[horizon]

    def fit(self, config: Any, split_index: int) -> SplitFit | None:
        from ml_route_v2.cpcv import split_masks
        from ml_route_v2.models import fit_model

        key = (config.model.model_id, config.horizon, int(split_index))
        if key in self._fits:
            return self._fits[key]
        split = self.nested.splits[split_index]
        data = self.data(config.horizon)
        train, test = split_masks(split, data.days, data.t_ns, data.x_ns)
        if not train.any() or not test.any():
            return None
        model = fit_model(config.model, data.X[train], data.y[train])
        want = self._sha.get((config.config_id, int(split_index)))
        if model.sha256 != want:
            raise OOSCheckError(f"split {split_index} {config.config_id}: refit sha256 "
                                f"{model.sha256[:12]} differs from the CPCV record "
                                f"{str(want)[:12]}")
        idx = np.flatnonzero(test)
        fit = SplitFit(int(split_index), model, data.rows.iloc[idx], data.X[test],
                       data.sigma[test], self.risk_fn(data.rows.iloc[np.flatnonzero(train)]))
        self._fits[key] = fit
        return fit


def accepted_trades(fit: SplitFit, config: Any, X: np.ndarray | None = None) -> pd.DataFrame:
    """score_split's accepted trades of one validation set (module docstring), with t_index."""
    from ml_route_v2.account import ACCOUNT_50K
    from ml_route_v2.decide import candidates
    from ml_route_v2.models import predict
    from ml_route_v2.portfolio import accept_trades, join_risk
    from ml_route_v2.selection_metric import _scorable

    r_hat = predict(fit.model, fit.X if X is None else X) * fit.sigma
    cands = _scorable(candidates(fit.rows, r_hat, config), fit.rows)
    acc = accept_trades(join_risk(cands, fit.risk), fit.risk, ACCOUNT_50K,
                        d_fixed=ACCOUNT_50K.mll_usd)
    t_idx = fit.rows[["root", "decision_ts_ns", "t_index"]]
    return acc.merge(t_idx, on=["root", "decision_ts_ns"], how="left", validate="many_to_one")


def daily_net(trades: pd.DataFrame, fit: SplitFit, slippage_multiple: float = 1.0) -> pd.Series:
    """Net $ per validation date (zeros on no-trade dates), as score_split forms it."""
    from ml_route_v2.portfolio import fixed_d_daily_pnl

    dates = pd.DatetimeIndex(pd.to_datetime(fit.rows["trade_date"]).dt.normalize().unique())
    return fixed_d_daily_pnl(trades, fit.rows, slippage_multiple=slippage_multiple).reindex(
        dates.sort_values(), fill_value=0.0).astype("float64")


def _scored(fit: SplitFit, config: Any, multiple: float) -> pd.Series:
    from ml_route_v2.models import predict
    from ml_route_v2.selection_metric import score_split

    r_hat = predict(fit.model, fit.X) * fit.sigma
    return score_split(fit.rows, r_hat, config, risk=fit.risk, slippage_multiple=multiple).daily


def _check_same(a: pd.Series, b: pd.Series, what: str) -> float:
    diff = float(np.max(np.abs(a.to_numpy() - b.reindex(a.index, fill_value=0.0).to_numpy()),
                        initial=0.0))
    if not diff <= TOL_USD or len(a) != len(b):
        raise OOSCheckError(f"{what}: the replicated daily differs from score_split by ${diff:.6g}")
    return diff


def _days_in(trades: pd.DataFrame, block: Sequence[Any]) -> pd.DataFrame:
    days = pd.to_datetime(trades["trade_date"]).dt.date
    return trades.loc[days.isin(set(block)).to_numpy()]


# ------------------------------------------------------------------ the nested record ----
def nested_record(refits: Refits, configs_by_id: dict[str, Any]) -> dict[str, Any]:
    """Per-product round trips (per path and over all paths) and the 1.5 x re-pricing of the
    nested OOS record (module docstring)."""
    from ml_route_v2.pipeline import assemble_record, record_figures

    nested = refits.nested
    trades_by_split: dict[int, pd.DataFrame] = {}
    daily = {1.0: {}, K.SLIPPAGE_STRESS: {}}
    for split, cid in zip(nested.splits, nested.selected, strict=True):
        if cid is None:
            continue
        cfg = configs_by_id[cid]
        fit = refits.fit(cfg, split.index)
        if fit is None:
            continue
        trades = accepted_trades(fit, cfg)
        scored = _scored(fit, cfg, 1.0)
        _check_same(daily_net(trades, fit), scored, f"split {split.index} {cid}")
        trades_by_split[split.index] = trades
        daily[1.0][split.index] = scored
        daily[K.SLIPPAGE_STRESS][split.index] = _scored(fit, cfg, K.SLIPPAGE_STRESS)
    records = {m: assemble_record(nested, d) for m, d in daily.items()}
    diff = float(np.max(np.abs(records[1.0].to_numpy() - nested.path_daily.to_numpy()),
                        initial=0.0))
    if not diff <= TOL_USD:
        raise OOSCheckError(f"the 1.0 x re-score differs from nested.path_daily by ${diff:.6g}")
    per_path = _per_path_trips(nested, trades_by_split)
    return {"trips": round_trip_table(per_path),
            "trips_per_path": per_path,
            "cost_sensitivity": {str(m): record_figures(r) for m, r in records.items()},
            "path_daily_1_5x": records[K.SLIPPAGE_STRESS],
            "cost_check_max_abs_diff": diff,
            "trades_t4": int(sum(int((t["t_index"] == K.T4_INDEX).sum())
                                 for t in trades_by_split.values())),
            "trades_total": int(sum(len(t) for t in trades_by_split.values()))}


def _per_path_trips(nested: Any, trades_by_split: dict[int, pd.DataFrame]) -> pd.DataFrame:
    """Rows = products traded, columns = the 5 paths: accepted trades on each path's blocks."""
    counts: dict[int, pd.Series] = {}
    for j, path in enumerate(nested.paths):
        parts = [_days_in(trades_by_split[path[b]], block)
                 for b, block in enumerate(nested.blocks) if path[b] in trades_by_split]
        frame = pd.concat(parts) if parts else pd.DataFrame(columns=["root"])
        counts[j] = frame["root"].value_counts()
    table = pd.DataFrame(counts).fillna(0).astype(int)
    table.index.name = "root"
    return table.sort_index()


def round_trip_table(per_path: pd.DataFrame) -> pd.DataFrame:
    """Per product: trips on each path, over all paths, the path minimum and median, and the
    below-30 flag under each reading (the lead picks the reading; nothing gates on it)."""
    out = per_path.copy()
    out.columns = [f"path_{c}" for c in out.columns]
    paths = per_path.to_numpy(dtype=float) if len(per_path) else np.zeros((0, 1))
    out["all_paths_total"] = per_path.sum(axis=1) if len(per_path) else []
    out["path_min"] = paths.min(axis=1) if len(per_path) else []
    out["path_median"] = np.median(paths, axis=1) if len(per_path) else []
    for col in ("all_paths_total", "path_min", "path_median"):
        out[f"below_30_{col}"] = out[col] < K.MIN_ROUND_TRIPS_PER_PRODUCT
    return out


# ------------------------------------------------------------------ the final configuration ----
def final_record(refits: Refits, final_config: Any | None) -> dict[str, Any]:
    """The final configuration's CPCV OOS net P&L, t4 share and r_ROD share (module docstring)."""
    from ml_route_v2.pipeline import assemble_record, record_figures

    if final_config is None:
        return {"status": "no final configuration: the t4 and r_ROD shares are not computed"}
    nested, cid = refits.nested, final_config.config_id
    cols = list(refits.panel.feature_cols)
    zero_at = [cols.index(c) for c in ROD_Z_COLUMNS]
    total = t4 = zeroed = 0.0
    trips: dict[str, int] = {}
    daily_by_split: dict[int, pd.Series] = {}
    for split in nested.splits:
        fit = refits.fit(final_config, split.index)
        if fit is None:
            continue
        trades = accepted_trades(fit, final_config)
        d = daily_net(trades, fit)
        _check_same(d, _scored(fit, final_config, 1.0), f"final {cid} split {split.index}")
        daily_by_split[split.index] = d
        total += float(d.sum())
        t4_trades = trades.loc[trades["t_index"] == K.T4_INDEX]
        t4 += float(daily_net(t4_trades, fit).sum()) if len(t4_trades) else 0.0
        X0 = fit.X.copy()
        X0[:, zero_at] = 0.0
        zeroed += float(daily_net(accepted_trades(fit, final_config, X0), fit).sum())
        for root, n in trades["root"].value_counts().items():
            trips[str(root)] = trips.get(str(root), 0) + int(n)
    want = 5.0 * float(nested.config_daily[cid].sum())  # each block is tested by 5 splits
    if abs(total - want) > TOL_USD * max(1, len(nested.config_daily)):
        raise OOSCheckError(f"final {cid}: refit P&L {total:.6f} is not 5 x config_daily "
                            f"{want:.6f}")
    paths = assemble_record(nested, daily_by_split)
    return {"config_id": cid, "registry_id": {v: k for k, v in K.config_ids().items()}.get(cid),
            "pnl_total_15_splits_usd": total, "pnl_t4_15_splits_usd": t4,
            "t4_share": t4 / total if total != 0 else None,
            "pnl_rod_zeroed_15_splits_usd": zeroed,
            "rod_share": 1.0 - zeroed / total if total != 0 else None,
            "trips_15_splits": dict(sorted(trips.items())),
            "path_figures": record_figures(paths),
            "note": "sums over the 15 outer splits count each block 5 times (config_daily x 5); "
                    "the shares are ratios, so the factor cancels"}


__all__ = ["OOSCheckError", "Refits", "SplitFit", "accepted_trades", "daily_net", "final_record",
           "nested_record", "round_trip_table"]
