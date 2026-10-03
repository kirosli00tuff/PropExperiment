"""Portfolio construction of ML route v2 (docs/STAGE_E_ML_V2_DESIGN.md V2.8 "Caps", V2.9
"Selection metric").

``admit`` is the one admission rule, shared by ``accept_trades`` (D held fixed, the selection
metric) and simulate.PortfolioMember (D from the engine's account):
- one open position per product: a candidate while the product's earlier position is open is
  skipped (a position is open on [decision_ts, exit_ts); a candidate at its exit time may enter);
- at most MAX_OPEN_POSITIONS open, at most MAX_OPEN_PER_CLUSTER per cluster;
- per product at most PER_PRODUCT_LOT_EQUIVALENTS lot-equivalent and D9.11's 50K caps
  (rules.products.member_cap_contracts);
- the portfolio at most the scaling tier at the prior session's closing balance minus
  PORTFOLIO_TIER_MARGIN_LOTS (with D fixed: the base tier);
- the size from sizing.contracts; 0 means skipped;
- the daily risk budget (design review D-03): the trade date starts with sigma_target^2 =
  (0.10 x D_open)^2 and each accepted trade consumes (n x sigma(p,h) x tick value)^2
  (sizing.daily_variance_budget / budget_use); n is also at most what fits the remaining budget,
  and a candidate the budget alone refuses is skipped with reason "risk_budget_spent".

Risk per candidate (code review C-02, C-04): ``join_risk`` gives each candidate sigma_ticks and
loss_ticks. Candidates that already carry both columns keep them (the row-level values: the
nested schedule attaches the table of each trade's own split, C-04) and the table is not merged;
otherwise the table's (root, horizon) row is merged and a pair absent from the table raises
(risk_missing_pairs). A pair present with a NaN sigma or loss (fewer than two training rows in
the split), or a sigma that is not positive (sd 0), cannot be sized: ``admit`` skips it with
reason "risk_unknown" and ``risk_unknown`` marks it; the selection metric counts these per
validation set (SplitScore.n_risk_unknown).

Candidates at one decision time are ranked by edge_over_cost (descending), then root. Vehicle
facts (tick value, lot-equivalent, product cap) come from rules.products, never literals; D2's q_c
and the D8 commission come from the frozen leg (screening.stage_e_frozen.leg_inputs).

The fixed-D P&L (``fixed_d_daily_pnl``) charges per contract the row's D8 cost plus the surcharge
for the contracts beyond q_c, 2 x (n - q_c)^+ / n ticks (design review D-08a,
sizing.excess_cost_ticks). ``slippage_multiple`` (design review D-08b) scales the slippage part of
that cost, everything but the commission: cost = commission + m x (D8 cost + surcharge -
commission), in ticks; at m = 1.0 the cost is the unscaled one exactly.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from functools import cache

import numpy as np
import pandas as pd

from ml_route_v2.account import AccountSpec, tier_max_tenths
from ml_route_v2.constants import (
    MAX_OPEN_PER_CLUSTER,
    MAX_OPEN_POSITIONS,
    PER_PRODUCT_LOT_EQUIVALENTS,
    PORTFOLIO_TIER_MARGIN_LOTS,
)
from ml_route_v2.sizing import (
    budget_use,
    contracts,
    daily_variance_budget,
    excess_cost_ticks,
)
from rules.products import TENTHS_PER_LOT, member_cap_contracts, product

CANDIDATE_COLUMNS = ("root", "cluster", "trade_date", "decision_ts_ns", "horizon", "exit_ts_ns",
                     "side", "r_hat_ticks", "cost_ticks", "edge_over_cost")
RISK_COLUMNS = ("root", "horizon", "sigma_ticks", "loss_ticks")
RISK_VALUE_COLUMNS = ("sigma_ticks", "loss_ticks")  # row-level values a candidate may carry
MARGIN_TENTHS = round(PORTFOLIO_TIER_MARGIN_LOTS * TENTHS_PER_LOT)


class PortfolioInputError(ValueError):
    """A candidate or risk frame breaks the interfaces contract (section 6, section 4)."""


@dataclass(frozen=True)
class VehicleFacts:
    root: str
    tick_value_usd: float
    lot_tenths: int  # lot-equivalent in tenths (mini 10, micro 1, SIL 2, MBT 10)
    product_cap: int  # min(1 lot-equivalent, D9.11 50K cap) in contracts
    q_c: int | None = None  # D2's size (reports/stage_e2a_vehicles.json via stage_e_frozen)
    commission_rt_ticks: float = 0.0  # D8 round-trip commission / tick value (as targets.py)

    @property
    def lot_equiv(self) -> float:
        return self.lot_tenths / TENTHS_PER_LOT


@cache
def vehicle_facts(root: str) -> VehicleFacts:
    from screening.stage_e_frozen import leg_inputs

    p = product(root)
    per_product = int(PER_PRODUCT_LOT_EQUIVALENTS * TENTHS_PER_LOT) // p.lot_weight_tenths
    leg = leg_inputs(root, traded=True)  # the frozen D2 vehicle and D8 costs
    assert leg.vehicle is not None and leg.costs is not None
    return VehicleFacts(root, float(p.tick_value_usd), p.lot_weight_tenths,
                        min(member_cap_contracts(root), per_product), int(leg.vehicle.q_c),
                        float(leg.costs.commission_rt_cents) / float(leg.tick_value_cents))


@dataclass(frozen=True)
class OpenPosition:
    root: str
    cluster: str
    contracts: int
    exit_ts_ns: int

    @property
    def tenths(self) -> int:
        return self.contracts * vehicle_facts(self.root).lot_tenths


@dataclass(frozen=True)
class Admission:
    contracts: int
    reason: str  # "" when admitted


def admit(*, root: str, cluster: str, sigma_ticks: float, loss_ticks: float, cost_ticks: float,
          d_open: float, d_now: float, book: Sequence[OpenPosition], tier_tenths: int,
          multiplier: float = 1.0, extra_cap: int | None = None,
          budget_var: float | None = None) -> Admission:
    """The portfolio caps and the V2.8 size for one candidate against the open ``book``;
    ``budget_var`` is the trade date's remaining variance budget (D-03). A candidate whose sigma
    or loss is unknown (NaN, or sigma <= 0) is skipped with reason "risk_unknown" (C-02)."""
    if not _risk_known(sigma_ticks, loss_ticks):
        return Admission(0, "risk_unknown")
    if any(p.root == root for p in book):
        return Admission(0, "product_open")
    if len(book) >= MAX_OPEN_POSITIONS:
        return Admission(0, "max_open_positions")
    if sum(p.cluster == cluster for p in book) >= MAX_OPEN_PER_CLUSTER:
        return Admission(0, "cluster_open")
    facts = vehicle_facts(root)
    room = tier_tenths - MARGIN_TENTHS - sum(p.tenths for p in book)
    capacity = max(room, 0) // facts.lot_tenths
    cap = facts.product_cap if extra_cap is None else min(facts.product_cap, extra_cap)
    kw = dict(d_open=d_open, d_now=d_now, sigma_ticks=sigma_ticks, loss_ticks=loss_ticks,
              cost_ticks=cost_ticks, tick_value_usd=facts.tick_value_usd, product_cap=cap,
              capacity_contracts=capacity, multiplier=multiplier)
    n = contracts(**kw, budget_var=budget_var)
    if n >= 1:
        return Admission(n, "")
    spent = budget_var is not None and contracts(**kw) >= 1
    return Admission(0, "risk_budget_spent" if spent else "size_zero")


def base_tier_tenths(account: AccountSpec) -> int:
    """The scaling plan's base tier in tenths (used with D fixed: V2.8 "with d_fixed use the base
    tier")."""
    return round(account.base_lots * TENTHS_PER_LOT)


def live_tier_tenths(account: AccountSpec, prior_close_balance_usd: float) -> int:
    """The tier at the prior session's closing balance (V2.8), in tenths."""
    return tier_max_tenths(account, prior_close_balance_usd)


def _require(frame: pd.DataFrame, cols: Sequence[str], what: str) -> None:
    missing = [c for c in cols if c not in frame.columns]
    if missing:
        raise PortfolioInputError(f"{what}_missing_columns: {missing}")


def _risk_known(sigma_ticks: float, loss_ticks: float) -> bool:
    return bool(np.isfinite(sigma_ticks) and sigma_ticks > 0 and np.isfinite(loss_ticks))


def risk_unknown(frame: pd.DataFrame) -> np.ndarray:
    """True where a joined candidate cannot be sized: sigma or loss NaN, or sigma <= 0 (C-02)."""
    sigma = frame["sigma_ticks"].to_numpy(dtype=float)
    loss = frame["loss_ticks"].to_numpy(dtype=float)
    with np.errstate(invalid="ignore"):
        return ~(np.isfinite(sigma) & (sigma > 0) & np.isfinite(loss))


def join_risk(cands: pd.DataFrame, risk: pd.DataFrame) -> pd.DataFrame:
    """Candidates with sigma_ticks and loss_ticks: their own when they carry both columns (the
    row-level values, C-04), else their (root, horizon) row of ``risk``; a pair absent from the
    table raises, a pair with NaN figures is kept (skipped later as risk_unknown, C-02)."""
    _require(cands, CANDIDATE_COLUMNS, "candidates")
    _require(risk, RISK_COLUMNS, "risk")
    bad_side = ~cands["side"].isin((-1, 1))
    if bad_side.any():
        raise PortfolioInputError(f"candidate_bad_side: {sorted(set(cands.loc[bad_side, 'side']))}")
    r = risk.loc[:, list(RISK_COLUMNS)]
    if r.duplicated(["root", "horizon"]).any():
        raise PortfolioInputError("risk_duplicate_pairs: one row per (root, horizon) expected")
    own = [c for c in RISK_VALUE_COLUMNS if c in cands.columns]
    if len(own) == len(RISK_VALUE_COLUMNS):
        return cands.copy()
    if own:
        raise PortfolioInputError(f"candidate_partial_risk_columns: {own} without the other")
    out = cands.merge(r, on=["root", "horizon"], how="left", validate="many_to_one",
                      indicator="_pair")
    absent = (out["_pair"] == "left_only").to_numpy()
    if absent.any():
        pairs = sorted(set(zip(out.loc[absent, "root"], out.loc[absent, "horizon"],
                               strict=True)))
        raise PortfolioInputError(f"risk_missing_pairs: {pairs[:5]}")
    return out.drop(columns="_pair")


def rank_candidates(frame: pd.DataFrame) -> pd.DataFrame:
    """Time order; at one decision time edge_over_cost descending, then root (stable)."""
    keyed = frame.assign(_neg_edge=-frame["edge_over_cost"].astype("float64"))
    keyed = keyed.sort_values(["decision_ts_ns", "_neg_edge", "root"], kind="mergesort")
    return keyed.drop(columns="_neg_edge").reset_index(drop=True)


def accept_trades(cands: pd.DataFrame, risk: pd.DataFrame, account: AccountSpec, *,
                  d_fixed: float | None) -> pd.DataFrame:
    """The accepted candidates in time order, with contracts, sigma_ticks, loss_ticks,
    tick_value_usd and lot_equiv added. D is held at ``d_fixed`` (the selection metric, V2.9);
    the tier is then the base tier. Each trade date starts with the variance budget
    (0.10 x d_fixed)^2 (D-03)."""
    if d_fixed is None:
        raise PortfolioInputError("accept_trades_needs_d_fixed: a path-dependent D needs the "
                                  "account path; use simulate.run_portfolio")
    if not (np.isfinite(d_fixed) and d_fixed > 0):
        raise PortfolioInputError(f"accept_trades_bad_d: {d_fixed!r}")
    ranked = rank_candidates(join_risk(cands, risk))
    tier = base_tier_tenths(account)
    book: tuple[OpenPosition, ...] = ()
    kept: list[int] = []
    sizes: list[int] = []
    budget: dict[pd.Timestamp, float] = {}  # trade date -> remaining variance budget (D-03)
    for i, row in enumerate(ranked.itertuples(index=False)):
        t = int(row.decision_ts_ns)
        if int(row.exit_ts_ns) <= t:
            raise PortfolioInputError(f"candidate_exit_not_after_decision: {row.root} at {t}")
        book = tuple(p for p in book if p.exit_ts_ns > t)
        day = pd.Timestamp(row.trade_date)
        remaining = budget.get(day, daily_variance_budget(d_fixed))
        adm = admit(root=row.root, cluster=row.cluster, sigma_ticks=float(row.sigma_ticks),
                    loss_ticks=float(row.loss_ticks), cost_ticks=float(row.cost_ticks),
                    d_open=d_fixed, d_now=d_fixed, book=book, tier_tenths=tier,
                    budget_var=remaining)
        if adm.contracts < 1:
            continue
        budget[day] = remaining - budget_use(adm.contracts, float(row.sigma_ticks),
                                             vehicle_facts(row.root).tick_value_usd)
        book = (*book, OpenPosition(row.root, row.cluster, adm.contracts, int(row.exit_ts_ns)))
        kept.append(i)
        sizes.append(adm.contracts)
    out = ranked.iloc[kept].reset_index(drop=True)
    facts = [vehicle_facts(r) for r in out["root"]]
    return out.assign(contracts=np.asarray(sizes, dtype=np.int64),
                      tick_value_usd=np.asarray([f.tick_value_usd for f in facts], dtype=float),
                      lot_equiv=np.asarray([f.lot_equiv for f in facts], dtype=float))


def _trade_cost_ticks(base: np.ndarray, n: np.ndarray, roots: Sequence[str],
                      slippage_multiple: float) -> np.ndarray:
    """Per-contract cost in ticks: the D8 cost plus the beyond-q_c surcharge (D-08a), its
    slippage part scaled by ``slippage_multiple`` (D-08b; exact at 1.0)."""
    facts = [vehicle_facts(r) for r in roots]
    extra = np.asarray([excess_cost_ticks(int(k), f.q_c) for k, f in zip(n, facts, strict=True)],
                       dtype=float)
    cost = base + extra
    if slippage_multiple == 1.0:
        return cost
    comm = np.asarray([f.commission_rt_ticks for f in facts], dtype=float)
    return comm + slippage_multiple * (cost - comm)


def fixed_d_daily_pnl(accepted: pd.DataFrame, targets: pd.DataFrame, *,
                      slippage_multiple: float = 1.0) -> pd.Series:
    """Net $ per trade date: contracts x (side x y_gross_<h> - cost) x tick value, summed by
    trade_date, with cost = cost_<side>_<h> + the beyond-q_c surcharge, its slippage part x
    ``slippage_multiple`` (module docstring). ``targets`` is aligned to decision rows (root,
    decision_ts_ns)."""
    if not (np.isfinite(slippage_multiple) and slippage_multiple >= 0):
        raise PortfolioInputError(f"bad_slippage_multiple: {slippage_multiple!r}")
    _require(accepted, ("root", "decision_ts_ns", "trade_date", "horizon", "side", "contracts"),
             "accepted")
    _require(targets, ("root", "decision_ts_ns"), "targets")
    if accepted.empty:
        return pd.Series(dtype="float64", name="net_usd")
    horizons = sorted(set(accepted["horizon"]))
    cols = [f"{k}_{h}" for h in horizons for k in ("y_gross", "cost_long", "cost_short")]
    _require(targets, cols, "targets")
    t = targets.loc[:, ["root", "decision_ts_ns", *cols]]
    if t.duplicated(["root", "decision_ts_ns"]).any():
        raise PortfolioInputError("targets_duplicate_rows: one row per (root, decision_ts_ns)")
    m = accepted.merge(t, on=["root", "decision_ts_ns"], how="left", validate="many_to_one")
    y = np.full(len(m), np.nan)
    cost = np.full(len(m), np.nan)
    side = m["side"].to_numpy(dtype=np.int64)
    for h in horizons:
        sel = (m["horizon"] == h).to_numpy()
        y[sel] = m.loc[sel, f"y_gross_{h}"].to_numpy(dtype=float)
        cl = m.loc[sel, f"cost_long_{h}"].to_numpy(dtype=float)
        cs = m.loc[sel, f"cost_short_{h}"].to_numpy(dtype=float)
        cost[sel] = np.where(side[sel] > 0, cl, cs)
    if not (np.isfinite(y).all() and np.isfinite(cost).all()):
        raise PortfolioInputError("target_missing_for_accepted_trade")
    tv = (m["tick_value_usd"].to_numpy(dtype=float) if "tick_value_usd" in m.columns
          else np.asarray([vehicle_facts(r).tick_value_usd for r in m["root"]]))
    n = m["contracts"].to_numpy(dtype=np.int64)
    cost = _trade_cost_ticks(cost, n, list(m["root"]), float(slippage_multiple))
    net = n.astype(float) * (side * y - cost) * tv
    days = pd.to_datetime(m["trade_date"]).dt.normalize()
    return pd.Series(net, index=days).groupby(level=0).sum().rename("net_usd")


__all__ = [
    "CANDIDATE_COLUMNS", "MARGIN_TENTHS", "RISK_COLUMNS", "Admission", "OpenPosition",
    "PortfolioInputError", "VehicleFacts", "accept_trades", "admit", "base_tier_tenths",
    "fixed_d_daily_pnl", "join_risk", "live_tier_tenths", "rank_candidates", "risk_unknown",
    "vehicle_facts",
]
