"""M5 steps 2-5: surrogate trees, candidate leaves, the block-6 pre-test, ranking and the rule JSON
(rulings ML-A02, ML-A10, ML-A11, ML-A15, ML-A16, ML-A17). Code only; nothing is chosen by hand.

Step 2. One surrogate per (cluster, challenger, horizon): sklearn DecisionTreeRegressor(max_depth=2,
min_samples_leaf=0.02, criterion="squared_error", max_features=None, random_state=20260924) fitted
to the selected (refit) model's predictions on the cluster's rows of blocks 1-5, on F1-F17 only.
Cut points are sklearn's thresholds as written (float64, unrounded). A leaf's conditions are
"feature <= cut" on each left branch and "feature > cut" on each right branch of its path.
A leaf with mean prediction mu and mean 1.0 x cost c_bar (its blocks 1-5 rows) is a long
candidate if mu > (m - 1) c_bar = 0.5 c_bar, a short candidate if mu < -(m + 1) c_bar = -2.5 c_bar
(m = 1.5), otherwise not a candidate.
Step 3. A candidate survives the block-6 pre-test only if, on block 6 at 1.5 x cost, its net P&L
is positive, it makes at least 30 trades, it meets D9.3's floors (at most 20 entries per product
per trade date, every hold at least 2 minutes, mean hold at least 10 minutes), and its realized
net P&L on blocks 1-5 at 1.5 x cost is also positive. P&L as in ML-A01: one open position per
product in time order, sigma units, summed per product and date, over the cluster's exposures
with rows.
Step 4. At most 2 rules per cluster, ranked by block-6 net P&L per trade date (dates with the
cluster's rows in block 6) at 1.5 x cost; ties: fewer conditions, the longer horizon, LightGBM
before the LSTM, then the leaf's left-to-right order.
Step 5. Each surviving rule is machine-readable JSON (ML-A16), hashed; ``render_entry`` renders
it without changing, dropping or rounding a field.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

import numpy as np

from ml_route.constants import (
    COST_STRESS,
    FEATURES_DISTILLABLE,
    HORIZONS,
    MAX_RULES_PER_CLUSTER,
    PRETEST_MIN_TRADES,
    SEED,
    SURROGATE_MAX_DEPTH,
    SURROGATE_MIN_LEAF,
)
from ml_route.ledger import canonical, sha256_bytes
from ml_route.selection import one_open_position, trade_pnl

CHALLENGER_ORDER = ("lgbm", "lstm")
MAX_ENTRIES_PER_DAY = 20
MIN_HOLD_NS = 2 * 60_000_000_000
MIN_MEAN_HOLD_NS = 10 * 60_000_000_000


def fit_surrogate(X17: np.ndarray, predictions: np.ndarray):  # noqa: ANN201
    from sklearn.tree import DecisionTreeRegressor

    if X17.shape[1] != len(FEATURES_DISTILLABLE):
        raise ValueError("the surrogate reads F1-F17 only")
    tree = DecisionTreeRegressor(max_depth=SURROGATE_MAX_DEPTH, min_samples_leaf=SURROGATE_MIN_LEAF,
                                 criterion="squared_error", max_features=None, random_state=SEED)
    tree.fit(np.asarray(X17, dtype=np.float64), np.asarray(predictions, dtype=np.float64))
    return tree


@dataclass(frozen=True)
class Leaf:
    order: int  # left-to-right
    node: int
    conditions: tuple[tuple[str, str, float], ...]  # (feature, "<=" or ">", cut)
    mu: float


def leaves(tree) -> list[Leaf]:  # noqa: ANN001
    t = tree.tree_
    out: list[Leaf] = []

    def walk(node: int, conds: tuple) -> None:
        left, right = int(t.children_left[node]), int(t.children_right[node])
        if left == right:  # a leaf
            out.append(Leaf(len(out), node, conds, float(t.value[node].ravel()[0])))
            return
        name = FEATURES_DISTILLABLE[int(t.feature[node])]
        cut = float(t.threshold[node])
        walk(left, (*conds, (name, "<=", cut)))
        walk(right, (*conds, (name, ">", cut)))

    walk(0, ())
    return out


def condition_mask(X17: np.ndarray, conditions: Sequence[Sequence]) -> np.ndarray:
    mask = np.ones(len(X17), dtype=bool)
    for feature, op, cut in conditions:
        col = X17[:, FEATURES_DISTILLABLE.index(feature)]
        mask &= (col <= cut) if op == "<=" else (col > cut)
    return mask


def candidate_sign(mu: float, c_bar: float, m: float = COST_STRESS) -> int:
    if mu > (m - 1.0) * c_bar:
        return 1
    if mu < -(m + 1.0) * c_bar:
        return -1
    return 0


@dataclass(frozen=True)
class RuleRows:
    """One cluster's rows of one horizon, in the arrays the rule P&L needs."""

    product: np.ndarray
    day: np.ndarray
    t_ns: np.ndarray
    exit_ns: np.ndarray
    X17: np.ndarray
    y: np.ndarray
    cost: np.ndarray


@dataclass(frozen=True)
class RuleResult:
    net_pnl: float
    trades: int
    dates: int
    per_trade_date: float
    max_entries_per_product_day: int
    min_hold_ns: int
    mean_hold_ns: float


def rule_result(rows: RuleRows, conditions: Sequence[Sequence], sign: int,
                m: float = COST_STRESS) -> RuleResult:
    fire = condition_mask(rows.X17, conditions)
    pos = one_open_position(rows.product, rows.t_ns, rows.exit_ns,
                            np.where(fire, sign, 0).astype(np.int8))
    pnl = trade_pnl(rows.y, rows.cost, pos, m)
    traded = pos != 0
    n_dates = len(np.unique(rows.day)) if len(rows.day) else 0
    per_pd = 0
    if traded.any():
        keys = [f"{p}|{d}" for p, d in zip(rows.product[traded].astype(str),
                                             rows.day[traded].astype(str), strict=True)]
        _, cnt = np.unique(keys, return_counts=True)
        per_pd = int(cnt.max())
    hold = (rows.exit_ns - (rows.t_ns + 60_000_000_000))[traded]
    return RuleResult(float(pnl.sum()), int(traded.sum()), n_dates,
                      float(pnl.sum()) / n_dates if n_dates else float("nan"), per_pd,
                      int(hold.min()) if hold.size else 0,
                      float(hold.mean()) if hold.size else 0.0)


def pretest(block6: RuleResult, blocks15: RuleResult) -> tuple[bool, list[str]]:
    reasons = []
    if not block6.net_pnl > 0:
        reasons.append("block-6 net P&L at 1.5 x cost not positive")
    if block6.trades < PRETEST_MIN_TRADES:
        reasons.append(f"{block6.trades} block-6 trades < {PRETEST_MIN_TRADES}")
    if block6.max_entries_per_product_day > MAX_ENTRIES_PER_DAY:
        reasons.append("more than 20 entries per product per trade date")
    if block6.trades and block6.min_hold_ns < MIN_HOLD_NS:
        reasons.append("a hold under 2 minutes")
    if block6.trades and block6.mean_hold_ns < MIN_MEAN_HOLD_NS:
        reasons.append("mean hold under 10 minutes")
    if not blocks15.net_pnl > 0:
        reasons.append("blocks 1-5 net P&L at 1.5 x cost not positive (sign disagrees)")
    return not reasons, reasons


def rank_key(rule: Mapping) -> tuple:
    """Step 4's order: the best first."""
    return (-rule["pretest"]["block6_per_trade_date"], len(rule["conditions"]),
            -HORIZONS.index(rule["horizon"]), CHALLENGER_ORDER.index(rule["challenger"]),
            rule["leaf_order"])


def keep_per_cluster(survivors: Sequence[Mapping]) -> list[Mapping]:
    out: list[Mapping] = []
    for cluster in sorted({r["cluster"] for r in survivors}):
        mine = sorted((r for r in survivors if r["cluster"] == cluster), key=rank_key)
        out.extend(mine[:MAX_RULES_PER_CLUSTER])
    return out


def rule_json(cluster: str, challenger: str, horizon: str, leaf: Leaf, sign: int, c_bar: float,
              exposures: Sequence[str], primary_leg: str, provenance: Mapping,
              pretest_fields: Mapping) -> dict:
    body = {"cluster": cluster, "challenger": challenger, "horizon": horizon,
            "leaf_order": leaf.order, "leaf_node": leaf.node,
            "conditions": [{"feature": f, "op": op, "cut": cut} for f, op, cut in leaf.conditions],
            "sign": int(sign), "leaf_mean_prediction": leaf.mu, "leaf_mean_cost": c_bar,
            "entry": "market intent at the decision time t; fills at the open of the bar at "
                     "t + 1 minute",
            "exit": "the open of the bar at t + h, or the forced flatten at F_X",
            "exposures": list(exposures), "primary_leg": primary_leg,
            "provenance": dict(provenance), "pretest": dict(pretest_fields)}
    body["rule_sha256"] = sha256_bytes(canonical(body))
    return body


def render_entry(rule: Mapping) -> str:
    """The catalog-format entry: a rendering of the JSON, every field verbatim (repr floats)."""
    cond = " AND ".join(f"{c['feature']} {c['op']} {c['cut']!r}" for c in rule["conditions"])
    lines = [f"### Route rule {rule['rule_sha256'][:12]} ({rule['cluster']}, {rule['challenger']}, "
             f"{rule['horizon']})", "",
             f"- Rule: IF {cond or 'TRUE'} THEN {'long' if rule['sign'] > 0 else 'short'}",
             f"- Exposures: {', '.join(rule['exposures'])}; primary leg {rule['primary_leg']}"]
    lines += [f"- {k}: {json.dumps(rule[k], sort_keys=True, default=str)}"
              for k in sorted(rule) if k not in ("conditions", "exposures", "primary_leg")]
    return "\n".join(lines) + "\n"
