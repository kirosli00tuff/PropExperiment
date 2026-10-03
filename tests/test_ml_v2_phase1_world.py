"""Stage E.12 Task 1b: the phase-1 world on fixture stores (ml_route_v2/phase1/world.py; lead rules
P-1 and P-3; design V2.2, V2.9). Synthetic stores only (tests/test_ml_v2_phase1_support.py).

Covers: the P-1 coverage rule; the P-3 start rule per root (S_X cut, empty window dropped by name,
MES's fixed date from D.1f's record); the window guard (a 2024-03-01 bar or row is refused); the
real group calendars' early-halt exclusion in ml_route_v2/clock.py; vendor-degraded dates reported
and kept; the store, summary and research sha256 pins.
"""

from __future__ import annotations

from datetime import date, time
from pathlib import Path
from types import MappingProxyType

import numpy as np
import pandas as pd
import pytest

from data.group_session import group_of, load_group_calendar
from data.stage_e_bars import ParquetHashMismatch, StageEBarRefusal
from ml_route_v2.clock import decision_rows, trade_dates_of
from ml_route_v2.constants import FORBIDDEN_FROM, TRAIN_LAST, UNIVERSE
from ml_route_v2.panel import WindowError, assert_window
from ml_route_v2.phase1.world import (
    COMPACT_COLUMNS,
    FORBIDDEN_FROM_NS,
    MES,
    Phase1Error,
    Phase1WindowError,
    available_roots,
    check_vehicles,
    compact_bars,
    mes_root_start,
    phase1_world,
    refuse_late,
    signal_coverage,
)
from ml_route_v2.pipeline import own_blackout
from ml_route_v2.signals import REGISTRY
from ml_route_v2.signals._core import SignalSpec
from tests.test_ml_v2_phase1_support import (
    EMPTY_ROOT,
    FIRST,
    HE_DEGRADED,
    LAST,
    LE_FIRST,
    OUTSIDE_DEGRADED,
    REQUESTED,
    VEHICLES,
    build_stores,
    day_session_bars,
)


@pytest.fixture(scope="module")
def stores(tmp_path_factory):
    return build_stores(tmp_path_factory.mktemp("p1_world_stores"), plant=None)


@pytest.fixture(scope="module")
def world(stores):
    return phase1_world(REQUESTED, **stores.world_kw())


# ------------------------------------------------------------------ P-1 coverage ----
def _spec(name: str, roots: tuple[str, ...], own: bool = False) -> SignalSpec:
    return SignalSpec(name, name, None, "generic", "test", roots, True, lambda ctx: None, own)


def test_coverage_rule_own_path_always_covered_and_missing_roots_named() -> None:
    reg = {"own": _spec("own", ("NQ", "CL", "HE"), own=True), "none": _spec("none", ()),
           "mes": _spec("mes", ("MES",)), "he": _spec("he", ("HE",)),
           "cross": _spec("cross", ("HE", "NQ", "CL"))}
    cov = signal_coverage(("HE",), reg)
    assert cov.available == ("HE", "MES")
    assert cov.covered == ("own", "none", "mes", "he")
    assert dict(cov.uncovered) == {"cross": ("NQ", "CL")}


def test_coverage_on_the_registry_uses_price_paths_plus_mes() -> None:
    cov = signal_coverage(("MNQ", "NG"))
    assert cov.available == ("MES", "NG", "NQ")
    assert set(cov.covered) | set(cov.uncovered) == set(REGISTRY)
    assert cov.covered == tuple(n for n in REGISTRY if n in cov.covered)  # REGISTRY order
    assert "g17_nq" in cov.covered and "g17_mes" in cov.covered
    assert cov.uncovered["g17_cl"] == ("CL",)
    for name in cov.covered:
        spec = REGISTRY[name]
        assert spec.own_path_only or set(spec.roots_read) <= set(cov.available)
    # the owned micro stores are not price paths: MCL's path is CL, never "MCL"
    assert available_roots(("MCL", "MGC")) == ("CL", "GC", "MES")


def test_check_vehicles_refuses_unknown_duplicate_and_empty() -> None:
    with pytest.raises(Phase1Error, match="UNIVERSE"):
        check_vehicles(("MES",))
    with pytest.raises(Phase1Error, match="twice"):
        check_vehicles(("HE", "HE"))
    with pytest.raises(Phase1Error, match="no vehicles"):
        check_vehicles(())


# ------------------------------------------------------------------ the world ----
def test_world_drops_the_empty_window_root_by_name(world) -> None:
    assert world.requested == REQUESTED
    assert world.vehicles == VEHICLES
    assert set(world.dropped) == {EMPTY_ROOT}
    assert "empty start window" in world.dropped[EMPTY_ROOT]
    assert world.starts[EMPTY_ROOT].s_x is None
    assert EMPTY_ROOT not in world.bars
    assert world.coverage.uncovered["g17_zc"] == (EMPTY_ROOT,)


def test_world_cuts_each_root_at_its_s_x_and_spans_the_training_calendar(world) -> None:
    assert world.starts["HE"].s_x == FIRST
    assert world.starts["LE"].s_x == LE_FIRST  # June 2022 volume below 0.25 V_ref
    assert world.starts[MES].s_x == FIRST
    for root in ("HE", "LE", MES):
        days = trade_dates_of(world.bars[root])
        assert days[0] == world.starts[root].s_x and days[-1] == LAST
    assert world.first == FIRST and world.last == TRAIN_LAST
    cal = load_group_calendar(group_of("HE"))
    assert world.calendar[0] == FIRST and world.calendar[-1] == LAST
    assert all(cal.is_trade_date(d) for d in world.calendar)
    assert world.bars_first == FIRST
    rec = world.roots["LE"]
    assert rec["s_x"] == LE_FIRST.isoformat()
    assert rec["start_rule"]["m_star"]["0.25"] == "2022-07"


def test_world_bars_are_compact_and_the_fields_mirror_the_synthetic_world(world, stores) -> None:
    for frame in world.bars.values():
        assert tuple(frame.columns) == COMPACT_COLUMNS
        assert isinstance(frame["trade_date"].dtype, pd.CategoricalDtype)
        assert frame["volume"].dtype == np.uint32
    assert dict(world.frames) == {}
    assert set(world.costs) == set(VEHICLES)
    assert set(world.legs["HE"]) <= set(world.bars)
    assert world.roots["HE"]["store_sha256"] == world.starts["HE"].store_sha256
    assert world.roots[MES]["store_sha256"] == stores.mes_start.store_sha256


def test_world_roll_blackout_drops_only_the_products_own_rows(world) -> None:
    vs = world.vehicles
    rows = decision_rows(vs, {v: trade_dates_of(world.bars[UNIVERSE[v][1]]) for v in vs},
                         exclude=own_blackout(world.blackout, vs))
    he_days = set(rows.loc[rows["root"] == "HE", "trade_date"].dt.date)
    assert world.blackout["HE"] and not (he_days & world.blackout["HE"])
    assert world.roots["HE"]["roll_blackout_dates_in_window"] == sum(
        FIRST <= d <= LAST for d in world.blackout["HE"])


def test_vendor_degraded_dates_are_reported_and_kept(world) -> None:
    deg = world.roots["HE"]["degraded"]
    assert deg["in_window_trade_dates"] == list(HE_DEGRADED)
    assert deg["flagged_bar_trade_dates"] == list(HE_DEGRADED)
    assert OUTSIDE_DEGRADED in deg["vendor_degraded_utc_dates"]
    assert world.roots[MES]["degraded"]["in_window_trade_dates"] == ["2022-08-15"]
    he_days = {d.isoformat() for d in trade_dates_of(world.bars["HE"])}
    assert set(HE_DEGRADED) <= he_days  # kept (NULL_CRITERIA_E 4)


def test_compact_bars_keeps_the_eight_columns_and_widens_when_needed() -> None:
    frame = pd.DataFrame({"ts_event": np.array([1, 2], dtype=np.int64),
                          "open": [1.0, 2.0], "high": [1.5, 2.5], "low": [0.5, 1.5],
                          "close": [1.25, 2.25], "volume": np.array([3, 2**33], dtype=np.int64),
                          "instrument_id": np.array([7, 7], dtype=np.int64),
                          "raw_symbol": ["HEZ9", "HEZ9"], "trade_date": ["2023-01-03"] * 2})
    out = compact_bars(frame)
    assert tuple(out.columns) == COMPACT_COLUMNS
    assert out["volume"].dtype == np.int64 and out["instrument_id"].dtype == np.uint32
    assert out["close"].tolist() == [1.25, 2.25]


# ------------------------------------------------------------------ guards ----
def test_window_guard_refuses_a_2024_03_01_bar_or_row() -> None:
    ok = pd.DataFrame({"ts_event": np.array([FORBIDDEN_FROM_NS - 1], dtype=np.int64),
                       "trade_date": ["2024-02-29"]})
    refuse_late("HE", ok)
    late_day = pd.DataFrame({"ts_event": np.array([1], dtype=np.int64),
                             "trade_date": [FORBIDDEN_FROM.isoformat()]})
    with pytest.raises(Phase1WindowError, match="2024-03-01"):
        refuse_late("HE", late_day)
    late_ts = pd.DataFrame({"ts_event": np.array([FORBIDDEN_FROM_NS], dtype=np.int64),
                            "trade_date": ["2024-02-29"]})
    with pytest.raises(Phase1WindowError):
        refuse_late("HE", late_ts)
    with pytest.raises(WindowError):
        assert_window(pd.DataFrame({"trade_date": [pd.Timestamp("2024-03-01")]}), "train")


def test_a_store_with_a_2024_03_01_bar_is_refused(tmp_path, stores) -> None:
    late = day_session_bars("HE", [date(2024, 3, 1)], time(9, 0), 3, 50)
    bad = build_stores(tmp_path, plant=None, mes_path=stores.mes_path,
                       mes_sha256=stores.mes_start.store_sha256, extra_bars={"HE": late})
    with pytest.raises(StageEBarRefusal, match="2024-03-01"):
        phase1_world(REQUESTED, **bad.world_kw())


def test_store_pins_research_sha_and_mes_sha(stores) -> None:
    """A price path's pin stops the build; MES's makes MES unavailable (P-1a)."""
    kw = stores.world_kw()
    with pytest.raises(ParquetHashMismatch):
        phase1_world(VEHICLES, **{**kw, "research_sha256": MappingProxyType(
            {**stores.research_sha256, "HE": "0" * 64})})
    wrong_mes = type(stores.mes_start)(**{**stores.mes_start.__dict__, "store_sha256": "1" * 64})
    w = phase1_world(VEHICLES, **{**kw, "mes_start": wrong_mes})
    assert w.mes_status == "refused" and MES not in w.bars
    assert w.mes_refusal.startswith("MES store refused: ParquetHashMismatch: ")


# ------------------------------------------------------------------ F-3 vehicles ----
def test_vehicles_derive_from_the_ranking_subset_with_a_store(stores, tmp_path) -> None:
    import hashlib

    from ml_route_v2.phase1.world import NO_STORE, phase1_subset
    from tests.test_ml_v2_phase1_support import NO_STORE_VEHICLE, RANKED, write_ranking

    path = write_ranking(tmp_path, RANKED)
    got = phase1_subset(path, step2_root=stores.step2_root, summaries_root=stores.summaries_root)
    assert got.vehicles == REQUESTED  # ranking order; ZC has a store (its window is P-3's)
    assert got.subset == RANKED
    assert dict(got.dropped) == {NO_STORE_VEHICLE: NO_STORE}
    assert got.ranking_sha256 == hashlib.sha256(path.read_bytes()).hexdigest()


def test_a_subset_vehicle_without_its_summary_is_dropped_by_name(stores, tmp_path) -> None:
    import shutil

    from ml_route_v2.phase1.world import NO_STORE, phase1_subset
    from tests.test_ml_v2_phase1_support import write_ranking

    summaries = tmp_path / "summaries"
    shutil.copytree(stores.summaries_root, summaries)
    (summaries / "bars_LE.json").unlink()
    got = phase1_subset(write_ranking(tmp_path, REQUESTED), step2_root=stores.step2_root,
                        summaries_root=summaries)
    assert got.vehicles == ("HE", EMPTY_ROOT) and dict(got.dropped) == {"LE": NO_STORE}


def test_an_absent_or_malformed_ranking_refuses(stores, tmp_path) -> None:
    import json

    from ml_route_v2.phase1.world import phase1_subset

    with pytest.raises(Phase1Error, match="does not exist"):
        phase1_subset(tmp_path / "stage_e12_ranking.json")
    for doc, msg in (({"subset": []}, "no \"subset\""),
                     ({"subset": [{"vehicle": "MCL", "path": "MCL"}]}, "not a vehicle"),
                     ({"subset": [{"vehicle": "HE"}]}, "malformed"),
                     ({"subset": [{"vehicle": "ZN", "path": "ZN"}]}, "no subset vehicle")):
        path = tmp_path / "r.json"
        path.write_text(json.dumps(doc), encoding="utf-8")
        with pytest.raises(Phase1Error, match=msg):
            phase1_subset(path, step2_root=stores.step2_root,
                          summaries_root=stores.summaries_root)


# ------------------------------------------------------------------ P-1a ----
def test_only_a_signal_only_root_can_be_unavailable() -> None:
    assert available_roots(("HE",), ("MES",)) == ("HE",)
    with pytest.raises(Phase1Error, match="P-1a"):
        available_roots(("HE",), ("HE",))


def test_mes_with_mislabelled_trade_dates_is_refused_and_the_build_completes(
        tmp_path, stores, capsys) -> None:
    import json

    from data.stage_e_bars import TradeDateMismatch
    from ml_route_v2.phase1 import cli
    from ml_route_v2.phase1.build import BARS_REPORT
    from screening import harness_freeze
    from tests.test_ml_v2_phase1_support import MES_NAME, write_freeze, write_mes, write_ranking

    mes_path = tmp_path / "MES" / MES_NAME
    sha = write_mes(mes_path, mislabel=("2023-05-17", "2023-05-18"))
    start = type(stores.mes_start)(**{**stores.mes_start.__dict__, "store_path": str(mes_path),
                                      "store_sha256": sha})
    with pytest.raises(TradeDateMismatch):  # the loader's own refusal, as P-1a names it
        from ml_route_v2.phase1.world import load_root_leg
        load_root_leg(start, step2_root=stores.step2_root)
    _path, freeze_sha = write_freeze(tmp_path / "frozen", {"x.py": b"X = 1\n"})
    write_ranking(tmp_path / "reports", REQUESTED)
    with pytest.MonkeyPatch.context() as mp:  # the CLI's canonical paths (review F-2)
        mp.setattr(cli, "FREEZE_ROOT", tmp_path / "frozen")
        mp.setattr(cli, "REPORTS_DIR", tmp_path / "reports")
        mp.setattr(cli, "STATE_DIR", tmp_path / "state")
        mp.setattr(cli, "WORLD_KW", {**stores.world_kw(), "mes_start": start})
        mp.setattr(harness_freeze, "preflight", lambda s: s)
        assert cli.main(["build", "--harness-sha256", "a" * 64,
                         "--freeze-sha256", freeze_sha]) == 0
    printed = [x for x in capsys.readouterr().out.splitlines() if x.startswith("MES store")]
    assert len(printed) == 1 and "refused" in printed[0] and "TradeDateMismatch" in printed[0]
    rep = json.loads((tmp_path / "reports" / BARS_REPORT).read_text(encoding="utf-8"))
    assert rep["mes_status"] == "refused" and MES not in rep["roots"]
    assert rep["mes_refusal"].startswith("MES store refused: TradeDateMismatch: ")
    reads_mes = [n for n, sp in REGISTRY.items() if not sp.own_path_only and MES in sp.roots_read]
    assert reads_mes and set(reads_mes) <= set(rep["signals"]["uncovered"])
    assert not set(reads_mes) & set(rep["signals"]["covered"])
    for name in reads_mes:
        assert rep["signals"]["uncovered_reasons"][name].startswith("MES store refused: "
                                                                     "TradeDateMismatch: ")
    assert rep["signals"]["uncovered_reasons"]["g17_nq"] == "reads roots outside phase 1: NQ"


def test_a_failing_d1f_record_check_makes_mes_unavailable(stores, monkeypatch) -> None:
    from screening import stage_e_start_dates as sd

    def refuse(_root):
        raise sd.StartDatesRefusal("MES: reports/stage_d1f_step5_start_rule.json sha256 differs")

    monkeypatch.setattr(sd, "mes_from_d1f", refuse)
    w = phase1_world(VEHICLES, **{**stores.world_kw(), "mes_start": None})
    assert w.mes_status == "refused" and MES not in w.bars and MES not in w.starts
    assert w.mes_refusal.startswith("MES store refused: StartDatesRefusal: ")
    assert "g17_mes" in w.coverage.uncovered and "g17_mes" not in w.coverage.covered


def test_mes_loaded_status_is_recorded(world) -> None:
    assert world.mes_status == "loaded" and world.mes_refusal is None
    assert not world.coverage.unavailable


def test_summary_of_another_store_is_refused(tmp_path, stores) -> None:
    import json
    import shutil

    summaries = tmp_path / "summaries"
    shutil.copytree(stores.summaries_root, summaries)
    path = summaries / "bars_HE.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["parquet"]["sha256"] = "2" * 64
    path.write_text(json.dumps(doc), encoding="utf-8")
    with pytest.raises(Phase1Error, match="bars_HE.json"):
        phase1_world(VEHICLES, **{**stores.world_kw(), "summaries_root": summaries})


def test_mes_start_is_d4_fixed_date_from_the_d1f_record() -> None:
    from data.config import REPO_ROOT

    start = mes_root_start(Path("unused.parquet"), record_root=REPO_ROOT)  # reads the JSON record
    assert start.s_x == date(2020, 2, 3)
    assert len(start.store_sha256) == 64 and start.research_sha256 is None


# ------------------------------------------------------------------ the clock ----
@pytest.mark.parametrize("vehicle", ["HE", "MNQ", "ZN"])
def test_clock_excludes_real_early_halt_dates(vehicle) -> None:
    """ml_route_v2/clock.py applies the REAL group calendar's early halts (no adapter needed)."""
    cal = load_group_calendar(group_of(vehicle))
    halts = sorted(d for d in cal.holidays if cal.early_halt_ct(d) is not None
                   and date(2019, 5, 6) <= d <= TRAIN_LAST and cal.is_trade_date(d))
    assert halts
    regular = date(2023, 5, 17)  # a Wednesday with no holiday in any group
    rows = decision_rows((vehicle,), {vehicle: [*halts, regular]})
    assert set(rows["trade_date"].dt.date) == {regular}
    assert len(rows) == 3
