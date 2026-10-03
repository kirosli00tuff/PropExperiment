"""The V2.9 selection metric: the ScoreFn of the nested CPCV (docs/STAGE_E_ML_V2_DESIGN.md V2.9
"Selection metric"; reports/stage_e11_interfaces.md section 5).

On one validation set:
1. the decision layer (decide.candidates: V2.7's cost gate at the configuration's k and horizon)
   turns the predictions into candidate trades;
2. portfolio.accept_trades applies every V2.8 cap with D held at the account's MLL ($2,000 at
   50K), so the metric has no path dependence;
3. portfolio.fixed_d_daily_pnl gives the net dollars per trade date at 1.0 x D8 cost plus the
   beyond-q_c surcharge (design review D-08a); ``slippage_multiple`` (default 1.0, design review
   D-08b) scales the slippage part of that cost (cost minus commission / tick value) for the
   cost-sensitivity re-pricing of the nested OOS record;
4. the daily series runs over ALL trade dates of the validation rows, zero on no-trade dates;
5. the score is mean / sd (ddof 1), 0 when the sd is 0 or there are fewer than two dates.
A candidate whose pair has no usable sigma or loss in the table (NaN: fewer than two training
rows in the split; or sd 0) is not sized: portfolio.admit skips it as "risk_unknown", and the
count is SplitScore.n_risk_unknown, which cpcv writes into the unit record (code review C-02).

Eligibility (at least MIN_TRADES trades) and ties belong to the caller (cpcv.py). The risk table
(``risk``) is the caller's: inside the nested CPCV it is the split's own training-row table
(design review D-04, cpcv's ``risk_fn``), passed as the ``risk`` keyword.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np
import pandas as pd

from ml_route_v2.account import ACCOUNT_50K, AccountSpec
from ml_route_v2.portfolio import accept_trades, fixed_d_daily_pnl, join_risk, risk_unknown

CandidatesFn = Callable[[pd.DataFrame, np.ndarray, Any], pd.DataFrame]


def _default_candidates() -> CandidatesFn:
    from ml_route_v2.decide import candidates  # Task 3; imported lazily (built in parallel)

    return candidates


def _scorable(cands: pd.DataFrame, rows: pd.DataFrame) -> pd.DataFrame:
    """Drop candidates whose gross target is missing (a missing bar: the trade cannot be scored).
    Reported to the lead as a reading of the contract."""
    if cands.empty:
        return cands
    keep = np.ones(len(cands), dtype=bool)
    for h in sorted(set(cands["horizon"])):
        col = f"y_gross_{h}"
        if col not in rows.columns:
            raise ValueError(f"score_split_missing_target: {col}")
        y = rows.loc[:, ["root", "decision_ts_ns", col]]
        sel = (cands["horizon"] == h).to_numpy()
        m = cands.loc[sel, ["root", "decision_ts_ns"]].merge(
            y, on=["root", "decision_ts_ns"], how="left", validate="many_to_one")
        keep[sel] = np.isfinite(m[col].to_numpy(dtype=float))
    return cands.loc[keep].reset_index(drop=True)


def daily_sharpe(daily: pd.Series) -> float:
    """mean / sd with ddof 1; 0 when undefined."""
    values = daily.to_numpy(dtype=float)
    if len(values) < 2:
        return 0.0
    sd = float(np.std(values, ddof=1))
    if not np.isfinite(sd) or sd == 0.0:
        return 0.0
    return float(np.mean(values)) / sd


def score_split(test_rows: pd.DataFrame, r_hat_ticks: np.ndarray, config: Any, *,
                risk: pd.DataFrame, account: AccountSpec = ACCOUNT_50K,
                candidates_fn: CandidatesFn | None = None,
                slippage_multiple: float = 1.0) -> Any:
    """The selection metric on one validation set -> configs.SplitScore."""
    from ml_route_v2.configs import SplitScore

    if len(r_hat_ticks) != len(test_rows):
        raise ValueError(f"score_split_misaligned: {len(r_hat_ticks)} predictions for "
                         f"{len(test_rows)} rows")
    cand_fn = candidates_fn if candidates_fn is not None else _default_candidates()
    cands = _scorable(cand_fn(test_rows, np.asarray(r_hat_ticks, dtype=float), config),
                      test_rows)
    joined = join_risk(cands, risk)  # a pair absent from the table raises here
    n_unknown = int(risk_unknown(joined).sum())
    accepted = accept_trades(joined, risk, account, d_fixed=account.mll_usd)
    dates = pd.DatetimeIndex(pd.to_datetime(test_rows["trade_date"]).dt.normalize().unique())
    daily = fixed_d_daily_pnl(accepted, test_rows, slippage_multiple=slippage_multiple).reindex(
        dates.sort_values(), fill_value=0.0)
    daily = daily.astype("float64").rename("net_usd")
    daily.index.name = "trade_date"
    return SplitScore(daily_sharpe(daily), int(len(accepted)), daily, n_unknown)


__all__ = ["daily_sharpe", "score_split"]
