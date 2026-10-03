"""Stage E.11 fix (lead ruling 2026-10-03): the V2.2 roll-blackout rule,
docs/STAGE_E_ML_V2_DESIGN.md V2.2 "Excluded dates" (ml_route_v2/signals/_core.py
apply_leg_blackout, signals.compute_signals, pipeline.own_blackout and build_world_panel).

- A planted roll date on a lead root (CL, K4's lead, no traded product's own root here) keeps
  every product's rows and makes g17_cl not applicable on that date for every product (value 0,
  avail = t); no other signal and no other date moves.
- A product's own roll date (GC for MGC) still drops that product's rows; the other product keeps
  its rows and loses only the features that read GC there (g17_gc).
- The pipeline's panel carries the rule: the rows are kept, z_g17_cl and app_g17_cl are 0.
Synthetic data only.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Mapping
from datetime import date
from types import MappingProxyType

import pandas as pd

from ml_route_v2.pipeline import build_world_panel
from ml_route_v2.signals import compute_signals
from ml_route_v2.synthetic import SyntheticWorld
from tests.ml_v2_fixtures import context, world, world_rows

VEHICLES = ("MNQ", "MGC")
FIRST, LAST = date(2021, 3, 1), date(2021, 5, 28)
SEED = 20261004
NAMES = ("g17_cl", "g17_gc", "g17_nq", "g17_mes", "g01_ret30", "cp1_ret", "k8_flight_ret")


def _world() -> SyntheticWorld:
    return world(VEHICLES, FIRST, LAST, seed=SEED)


def _with_blackout(w: SyntheticWorld, plant: Mapping[str, date]) -> SyntheticWorld:
    out = dict(w.blackout)
    for root, day in plant.items():
        out[root] = frozenset(out.get(root, frozenset()) | {day})
    return dataclasses.replace(w, blackout=MappingProxyType(out))


def _signals(w: SyntheticWorld) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = world_rows(w)
    return rows, compute_signals(context(rows, w.bars, w.releases, w.blackout), NAMES)


def _clean_date(w: SyntheticWorld, rows: pd.DataFrame, k: int) -> date:
    """The k-th training date on which every vehicle has rows and no root has a roll blackout."""
    taken = set().union(*w.blackout.values())
    days = pd.to_datetime(rows["trade_date"]).dt.date
    full = rows.groupby(days)["root"].nunique()
    ok = [d for d in sorted(full.index[full == len(VEHICLES)])
          if d not in taken and d in set(w.calendar)]
    return ok[k]


def _on(rows: pd.DataFrame, day: date) -> pd.Series:
    return pd.to_datetime(rows["trade_date"]).dt.date == day


def test_lead_roll_date_makes_the_lead_not_applicable_for_every_product_and_keeps_rows() -> None:
    base = _world()
    rows0, sig0 = _signals(base)
    day = _clean_date(base, rows0, 30)
    rows1, sig1 = _signals(_with_blackout(base, {"CL": day}))

    pd.testing.assert_frame_equal(rows0, rows1)  # a leg's roll date drops no row
    on = _on(rows1, day)
    assert set(rows1.loc[on, "root"]) == set(VEHICLES)
    for v in VEHICLES:  # not vacuous: the lead is applicable there without the plant
        assert sig0.loc[on & (rows0["root"] == v), "app_g17_cl"].eq(1).any(), v
    assert sig1.loc[on, "app_g17_cl"].eq(0).all()
    assert sig1.loc[on, "raw_g17_cl"].eq(0).all()
    assert (sig1.loc[on, "avail_g17_cl"] == rows1.loc[on, "decision_ts_ns"]).all()
    pd.testing.assert_frame_equal(sig0.loc[~on], sig1.loc[~on])
    others = [c for c in sig1.columns if not c.endswith("_g17_cl")]
    pd.testing.assert_frame_equal(sig0.loc[on, others], sig1.loc[on, others])


def test_own_roll_date_still_drops_the_product_rows() -> None:
    base = _world()
    rows0, sig0 = _signals(base)
    day = _clean_date(base, rows0, 40)
    rows1, sig1 = _signals(_with_blackout(base, {"GC": day}))  # GC: MGC's price path

    on0, on1 = _on(rows0, day), _on(rows1, day)
    assert set(rows0.loc[on0, "root"]) == {"MNQ", "MGC"}
    assert set(rows1.loc[on1, "root"]) == {"MNQ"}
    assert len(rows1) == len(rows0) - int((on0 & (rows0["root"] == "MGC")).sum())
    mnq0 = on0 & (rows0["root"] == "MNQ")
    assert sig0.loc[mnq0, "app_g17_gc"].eq(1).any()  # not vacuous
    assert sig1.loc[on1, "app_g17_gc"].eq(0).all()  # MNQ reads GC as a lead: not applicable
    keep = ~(on0 & (rows0["root"] == "MGC")).to_numpy()
    rest = [c for c in sig1.columns if not c.endswith("_g17_gc")]
    pd.testing.assert_frame_equal(sig0.loc[keep, rest].reset_index(drop=True),
                                  sig1[rest].reset_index(drop=True))


def test_pipeline_panel_keeps_the_rows_and_zeroes_the_lead_feature() -> None:
    base = _world()
    day = _clean_date(base, world_rows(base), 30)
    f0 = build_world_panel(base).frame
    f1 = build_world_panel(_with_blackout(base, {"CL": day})).frame

    key = ["root", "decision_ts_ns"]
    k0 = set(map(tuple, f0[key].to_numpy().tolist()))
    k1 = set(map(tuple, f1[key].to_numpy().tolist()))
    assert k0 <= k1  # no row dropped; a row whose g17_cl was missing may now be kept
    new = [tuple(x) in k1 - k0 for x in f1[key].to_numpy().tolist()]
    assert _on(f1, day)[new].all()
    on0, on1 = _on(f0, day), _on(f1, day)
    assert set(f1.loc[on1, "root"]) == set(VEHICLES)
    assert f0.loc[on0, "app_g17_cl"].eq(1).any()  # not vacuous
    assert f1.loc[on1, "app_g17_cl"].eq(0).all()
    assert f1.loc[on1, "z_g17_cl"].eq(0).all()
