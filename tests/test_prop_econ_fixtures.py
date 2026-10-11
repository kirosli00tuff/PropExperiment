"""Hand fixtures for the Stage E.19 funnel tests (no store reads), plus checks of the fixtures.

``hand_doc`` is a complete rules document in the e19-rules-1 structure with simple hand numbers (not
Topstep's): every leaf gets an INFERRED RULE. ``UNIT`` is a product whose sigma is 2**20 with no
micro and no cost, so with f x D < 2**20 the bot trades exactly one contract and a day's P&L equals
z x 2**20 exactly: a hand path in dollars is ``unit_shocks([...])``.
"""

from __future__ import annotations

import copy
from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np

from prop_econ.rules import RuleBook, SizeRules, rules_from_dict, size_rules
from prop_econ.types import ProductSpec, ShockSet

SCALE = 2.0**20
UNIT = ProductSpec("U", SCALE, 0.0, None, None, None)
# micro-capable product for sizing tests: full sigma 1000 / RT 4, micro sigma 100 / RT 1
NQ = ProductSpec("NQ", 1000.0, 4.0, "MNQ", 100.0, 1.0)
ZN = ProductSpec("ZN", 500.0, 2.0, None, None, None)


def _size_block() -> dict[str, Any]:
    return {
        "combine": {
            "monthly_price_usd": {"standard": 50.0, "no_activation_fee": 100.0},
            "reset_price_usd": {"standard": 40.0, "no_activation_fee": 90.0},
            "dll_discount_monthly_usd": {"standard": None, "no_activation_fee": 10.0},
            "profit_target_usd": 3000.0,
            "mll_usd": 2000.0,
            "mll_trail": "eod",
            "mll_floor_max_rel_usd": 0.0,
            "dll_usd": None,
            "dll_option_usd": 1000.0,  # added field (FINAL file), the DLL chosen at checkout
            "consistency": {"type": "best_day_max_frac_of_profit", "frac": 0.5},
            "min_trading_days": 2,
            "max_minis": 5,
        },
        "activation_fee_usd": {"standard": 150.0, "no_activation_fee": 0.0},
        "xfa": {
            "start_balance_usd": 0.0,
            "mll_usd": 2000.0,
            "mll_trail": "eod",
            "mll_floor_lock_usd": 0.0,
            "mll_after_first_payout_usd": 0.0,
            "dll_option_usd": 1000.0,
            "scaling": [{"below_usd": 1500.0, "max_minis": 2},
                        {"below_usd": 2000.0, "max_minis": 3},
                        {"below_usd": None, "max_minis": 5}],
            "scaling_boundary": "lower",
            "payout": {
                "standard": {"winning_day_usd": 150.0, "winning_days": 5, "frac_of_balance": 0.5,
                             "cap_usd": 2000.0, "cap_usd_dll": 4000.0,
                             "net_positive_since_last": True},
                "consistency": {"traded_days": 3, "best_day_max_frac": 0.4, "frac_of_balance": 0.5,
                                "cap_usd": 3000.0, "cap_usd_dll": 6000.0,
                                "net_positive_since_last": True},
            },
            "payout_count_limit": None,
            "back2funded": {"price_usd": 600.0, "dll_discount_usd": 50.0, "max_per_xfa": 2,
                            "before_first_payout_only": True, "window_calendar_days": 30},
        },
    }


def _leaf_paths(value: Any, path: str) -> list[tuple[str, Any]]:
    if isinstance(value, Mapping):
        return [p for k, v in value.items() for p in _leaf_paths(v, f"{path}.{k}")]
    if isinstance(value, list):
        return [p for i, v in enumerate(value) for p in _leaf_paths(v, f"{path}.{i}")]
    return [(path, value)]


def with_rules(doc: dict[str, Any], readings: Mapping[str, Sequence[Any]] | None = None
               ) -> dict[str, Any]:
    """A copy of ``doc`` whose ``rules`` list has one RULE per leaf (extra readings by path)."""
    out = copy.deepcopy(doc)
    readings = dict(readings or {})
    leaves = _leaf_paths(out["global"], "global") + _leaf_paths(out["sizes"], "sizes")
    out["rules"] = [
        {"id": f"R{i:03d}", "path": path, "value": value,
         "status": "UNSOURCED" if path in readings else "INFERRED",
         "readings": [value, *readings.get(path, ())], "source": None, "quote": None,
         "note": "test fixture"}
        for i, (path, value) in enumerate(leaves, start=1)
    ]
    return out


def hand_doc(**global_changes: Any) -> dict[str, Any]:
    """The hand rules document (all three sizes identical), with RULEs."""
    glob = {
        "max_active_xfas": 5,
        "profit_split_trader": 0.9,
        "billing_period_calendar_days": 30,
        "rebill_adds_reset_credit": True,
        "reset_pushes_rebill": True,
        "resets_per_day": 2,
        "combine_time_limit_days": None,
        "payout_min_request_usd": 125.0,
        "payout_day_counts_toward_next_window": False,
        "xfa_inactivity_close_days": None,
        "callup": {"type": "none", "n": None, "usd": None, "closes_all_xfas": None,
                   "xfa_balance_on_callup": "worth 0 (fixture)"},
        "dll_doubles_payout_caps": True,
    }
    glob.update(global_changes)
    doc = {
        "schema_version": "e19-rules-1",
        "generated_pdt": "2026-10-10T18:00:00-07:00",
        "status": "PROVISIONAL",
        "sources": {},
        "terms_check": {"robots_txt": "n/a", "automated_access_clause": "none found",
                        "source": None, "decision": "fixture"},
        "global": glob,
        "sizes": {size: _size_block() for size in ("50K", "100K", "150K")},
        "prohibited": [],
    }
    return with_rules(doc, {"sizes.50K.xfa.scaling_boundary": ["upper"],
                            "global.callup.type": ["after_n_payouts"]})


def hand_book(**global_changes: Any) -> RuleBook:
    return rules_from_dict(hand_doc(**global_changes))


def hand_rules(size: str = "50K", **global_changes: Any) -> SizeRules:
    return size_rules(hand_book(**global_changes), size)


def make_shocks(z: Sequence[Sequence[float]], w: Sequence[Sequence[float]],
                prod: Sequence[Sequence[int]] | None = None,
                products: tuple[ProductSpec, ...] = (NQ,)) -> ShockSet:
    z_arr = np.asarray(z, dtype=np.float64)
    w_arr = np.asarray(w, dtype=np.float64)
    p_arr = np.zeros(z_arr.shape, dtype=np.int16) if prod is None else np.asarray(prod, np.int16)
    return ShockSet(z=z_arr, w=w_arr, prod=p_arr, products=products)


def unit_shocks(pnl: Sequence[float], worst: Sequence[float] | None = None) -> ShockSet:
    """One path of exact dollar P&Ls on the UNIT product; worst defaults to min(0, pnl)."""
    pnl_arr = np.asarray(pnl, dtype=np.float64)
    worst_arr = np.minimum(0.0, pnl_arr) if worst is None else np.asarray(worst, dtype=np.float64)
    return make_shocks([pnl_arr / SCALE], [worst_arr / SCALE], products=(UNIT,))


def pad_shocks(shocks: ShockSet, days: int) -> ShockSet:
    """Extend every row with zero-P&L days (z = w = 0, product 0) up to ``days``."""
    extra = days - shocks.n_days
    if extra <= 0:
        return shocks
    width = ((0, 0), (0, extra))
    return ShockSet(z=np.pad(shocks.z, width), w=np.pad(shocks.w, width),
                    prod=np.pad(shocks.prod, width), products=shocks.products)


def random_shocks(n: int, days: int, seed: int,
                  products: tuple[ProductSpec, ...] = (NQ, ZN)) -> ShockSet:
    """Fat-tailed random shocks (t with 4 df) with w <= min(0, z), random products."""
    rng = np.random.default_rng(seed)
    z = rng.standard_t(4, size=(n, days)) / np.sqrt(2.0)
    w = np.minimum(0.0, z) - np.abs(rng.normal(0.0, 0.6, size=(n, days)))
    prod = rng.integers(0, len(products), size=(n, days))
    return make_shocks(z, w, prod, products)


# ------------------------------------------------------------------- fixture self-checks ----
def test_hand_doc_loads_with_one_rule_per_leaf():
    book = hand_book()
    assert book.status == "PROVISIONAL"
    assert book.extra_fields == ("sizes.50K.combine.dll_option_usd",
                                 "sizes.100K.combine.dll_option_usd",
                                 "sizes.150K.combine.dll_option_usd")
    assert set(book.alternative_readings()) == {"sizes.50K.xfa.scaling_boundary",
                                                "global.callup.type"}


def test_unit_shocks_give_exact_dollar_pnl():
    s = unit_shocks([300.0, -125.5])
    assert s.z[0, 0] * SCALE == 300.0
    assert s.w[0, 1] * SCALE == -125.5
