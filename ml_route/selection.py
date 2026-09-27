"""M5.1's selection metric exactly as ruled (Stage E.2a ruling on audit ML-A01), and the P&L
helpers M5.3 reuses.

At each row, with the prediction y_hat and the row's D8 round-turn cost c at 1.0 x (both in
sigma_X,d units): long if y_hat > 0, short if y_hat < -2c, flat otherwise. M4's one-open-position
rule applies in time order per product: a decision time is skipped while a position from an
earlier decision time of the same product is open (a position is open from its decision time t
until its exit fill time; a decision at or after the exit is free). A trade's realized net P&L in
sigma units at cost multiple m is y - (m - 1) c for a long and -y - (m + 1) c for a short (at
m = 1: y and -y - 2c). A product's daily P&L is the sum of its trades' P&L on that date, and zero
on a date with rows and no trade; the portfolio's daily P&L is the mean over the products with
rows on that date. A split's score is the mean of the portfolio's daily P&L over the split's
validation dates that have rows; a configuration's score is the mean of its 10 split scores.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


def positions_from_predictions(y_hat: np.ndarray, cost: np.ndarray) -> np.ndarray:
    """+1 long, -1 short, 0 flat (ML-A01)."""
    y_hat = np.asarray(y_hat, dtype=np.float64)
    cost = np.asarray(cost, dtype=np.float64)
    return np.where(y_hat > 0, 1, np.where(y_hat < -2.0 * cost, -1, 0)).astype(np.int8)


def one_open_position(product: np.ndarray, t_ns: np.ndarray, exit_ns: np.ndarray,
                      pos: np.ndarray) -> np.ndarray:
    """Positions after M4's rule: a signal while the product's earlier position is open is
    skipped (set to 0). Rows may come in any order; the rule runs in time order per product."""
    out = np.zeros(len(pos), dtype=np.int8)
    order = np.lexsort((t_ns, np.asarray(product).astype(str)))
    busy_until: dict[str, int] = {}
    for r in order.tolist():
        if pos[r] == 0:
            continue
        p = str(product[r])
        if t_ns[r] < busy_until.get(p, -1):
            continue
        out[r] = pos[r]
        busy_until[p] = int(exit_ns[r])
    return out


def trade_pnl(y: np.ndarray, cost: np.ndarray, pos: np.ndarray, m: float) -> np.ndarray:
    """Realized net P&L per row in sigma units at cost multiple m (0 where flat)."""
    y = np.asarray(y, dtype=np.float64)
    cost = np.asarray(cost, dtype=np.float64)
    long_pnl = y - (m - 1.0) * cost
    short_pnl = -y - (m + 1.0) * cost
    return np.where(pos > 0, long_pnl, np.where(pos < 0, short_pnl, 0.0))


def portfolio_daily(product: np.ndarray, day: np.ndarray, pnl: np.ndarray) -> pd.Series:
    """Equal-risk portfolio daily P&L: per product the day's sum (0 with rows and no trade), then
    the mean over the products with rows that day. Indexed by day, ascending."""
    frame = pd.DataFrame({"p": np.asarray(product).astype(str), "d": day, "x": pnl})
    per_product = frame.groupby(["d", "p"], sort=True)["x"].sum()
    return per_product.groupby(level="d").mean()


@dataclass(frozen=True)
class SplitScore:
    score: float
    n_dates: int
    n_trades: int


def split_score(product: np.ndarray, day: np.ndarray, t_ns: np.ndarray, exit_ns: np.ndarray,
                y: np.ndarray, cost: np.ndarray, y_hat: np.ndarray) -> SplitScore:
    """ML-A01's score of one split's validation rows at 1.0 x cost."""
    pos = one_open_position(product, t_ns, exit_ns, positions_from_predictions(y_hat, cost))
    pnl = trade_pnl(y, cost, pos, 1.0)
    daily = portfolio_daily(product, day, pnl)
    if daily.empty:
        raise ValueError("a split with no validation rows has no score")
    return SplitScore(float(daily.mean()), int(len(daily)), int(np.count_nonzero(pos)))


def configuration_score(split_scores: list[float]) -> float:
    if len(split_scores) != 10:
        raise ValueError(f"a configuration's score needs its 10 split scores, got "
                         f"{len(split_scores)}")
    return float(np.mean(split_scores))


def smaller_first_key(challenger: str, config: dict) -> tuple:
    """ML-A10's tie order: the smaller model first."""
    if challenger == "lgbm":
        return (config["num_leaves"], -config["min_data_in_leaf"], -config["lambda_l2"])
    if challenger == "lstm":
        return (config["hidden"], config["lookback"])
    raise ValueError(f"unknown challenger {challenger!r}")


def select(challenger: str, scored: list[tuple[dict, float]]) -> dict:
    """The highest configuration score; ties to the smaller model (ML-A10)."""
    if not scored:
        raise ValueError("nothing to select from")
    best = max(s for _, s in scored)
    tied = [c for c, s in scored if s == best]
    return min(tied, key=lambda c: smaller_first_key(challenger, c))
