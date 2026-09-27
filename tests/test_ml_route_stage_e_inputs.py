"""Stage E.2b G4 (MLTestCoder): the shared S_X and release-calendar wiring of ml_route.inputs
(lead ruling OC-K / OC-J) and lead ruling OC-M on exit fills inside the D9.5a guard, with known
answers. Synthetic data only."""

from __future__ import annotations

import json
import sys
import types
from datetime import UTC, date, datetime, timedelta

import numpy as np
import pandas as pd
import pytest

import screening
from ml_route import inputs as inputs_mod
from ml_route.dataset import build_from_bars
from ml_route.features import Bars
from ml_route.inputs import (
    EventCalendar,
    ReleaseListMismatch,
    RouteInputMissing,
    day_times,
    event_calendar_from_release,
    load_products,
)
from ml_route.rows import deferred_exit
from ml_route.synthetic import bars_from_frame, synthetic_bars, synthetic_inputs
from screening.stage_e_rules import (
    ReleaseCalendarMissing,
    release_calendar_from_dict,
)
from screening.stage_e_runner import StartRuleMissing

NS_MIN = 60_000_000_000
TRADED = ("NQ", "RTY", "YM", "ZT", "ZF", "ZN", "TN", "ZB", "UB", "6E", "6A", "6B", "6C", "6J",
          "6S", "6N", "CL", "NG", "GC", "HG", "ZC", "ZW", "ZS", "ZM", "ZL", "HE", "LE", "MBT")


# ------------------------------------------------------------------ S_X wiring ----
ML_FILE = "reports/stage_e_start_rule_ML.json"


def _fake_start_module(values: dict[str, date], missing: frozenset[str] = frozenset(),
                       files: tuple[str, ...] = (ML_FILE,), sha: str = "a" * 64):
    """The shared loader's API (screening.stage_e_start_dates.start_dates_for)."""
    mod = types.ModuleType("screening.stage_e_start_dates")

    def start_dates_for(root_symbols, root=None, *, allow_empty=False):  # noqa: ANN001, ANN202
        wanted = list(root_symbols)
        absent = [r for r in wanted if r in missing or r not in values]
        if absent:
            raise StartRuleMissing(f"no frozen S_X for {absent}")
        prov = {r: {"s_x": str(values[r]), "step2_sha256": sha,
                    "files": [{"path": f, "sha256": "f" * 64} for f in files]} for r in wanted}
        mod.seen_root = root
        return {r: values[r] for r in wanted}, prov

    mod.start_dates_for = start_dates_for
    return mod


def _install(monkeypatch: pytest.MonkeyPatch, mod) -> None:  # noqa: ANN001
    monkeypatch.setitem(sys.modules, "screening.stage_e_start_dates", mod)
    monkeypatch.setattr(screening, "stage_e_start_dates", mod, raising=False)


class TestStartDates:
    def test_every_traded_price_path_contract_reads_the_shared_loader(self, monkeypatch) -> None:
        values = {r: date(2019, 5, 6) + timedelta(days=i) for i, r in enumerate(TRADED)}
        _install(monkeypatch, _fake_start_module(values | {"MES": date(2020, 1, 2)}))
        got = inputs_mod.load_start_dates()
        assert got == values  # the 28 with a vehicle; RB, HO and SI have none and are not read
        assert set(TRADED) == {p for p, s in load_products().items() if s.vehicle is not None}

    def test_a_missing_root_is_refused_by_name(self, monkeypatch) -> None:
        values = {r: date(2019, 5, 6) for r in TRADED}
        _install(monkeypatch, _fake_start_module(values, frozenset({"ZL"})))
        with pytest.raises(RouteInputMissing, match=r"no frozen S_X.*'ZL'"):
            inputs_mod.load_start_dates()

    def test_a_value_that_is_not_a_date_is_refused(self, monkeypatch) -> None:
        mod = _fake_start_module({"ZN": "2019-05-06"})
        _install(monkeypatch, mod)
        with pytest.raises(RouteInputMissing, match="not a date"):
            inputs_mod.load_start_dates(["ZN"])

    def test_the_store_sha256_comes_with_s_x_from_set_ml(self, monkeypatch) -> None:
        _install(monkeypatch, _fake_start_module({"ZN": date(2019, 5, 6)}, sha="b" * 64))
        assert inputs_mod.load_start_rule(["ZN"]) == ({"ZN": date(2019, 5, 6)}, {"ZN": "b" * 64})
        _install(monkeypatch, _fake_start_module({"ZN": date(2019, 5, 6)},
                                                 files=("reports/stage_e_start_rule_K2.json",)))
        with pytest.raises(RouteInputMissing, match="not from set ML"):
            inputs_mod.load_start_rule(["ZN"])
        _install(monkeypatch, _fake_start_module({"ZN": date(2019, 5, 6)}, sha="not-a-sha"))
        with pytest.raises(RouteInputMissing, match="no step 2 sha256 for ZN"):
            inputs_mod.load_start_rule(["ZN"])

    def test_an_absent_shared_module_is_refused_by_name(self, monkeypatch) -> None:
        monkeypatch.setitem(sys.modules, "screening.stage_e_start_dates", None)
        monkeypatch.delattr(screening, "stage_e_start_dates", raising=False)
        with pytest.raises(RouteInputMissing, match="shared S_X loader"):
            inputs_mod.load_start_dates(["ZN"])


# ------------------------------------------------------- release calendar wiring ----
def _raw_calendar(first: str = "2019-05-01", last: str = "2026-06-21",
                  nq_own: list[str] | None = None, paths_listed: bool = True) -> dict:
    universe = {s.vehicle for s in load_products().values() if s.vehicle}
    universe |= set(TRADED) if paths_listed else set()
    nfp = ["NQ", "MNQ", "ZN"] if paths_listed else ["MNQ", "ZN"]
    releases = [
        {"id": "fomc-1", "instant_utc": "2019-06-19T18:00:00Z", "products": sorted(universe),
         "cpi": False, "source": "t"},
        {"id": "cpi-1", "instant_utc": "2019-06-12T12:30:00Z", "products": [], "cpi": True,
         "source": "t"},
        {"id": "nfp-1", "instant_utc": "2019-06-07T12:30:00Z", "products": nfp,
         "cpi": False, "source": "t"},
    ]
    if nq_own is not None:
        releases += [{"id": f"nq-{i}", "instant_utc": s, "products": ["NQ"], "cpi": False,
                      "source": "t"} for i, s in enumerate(nq_own)]
    return {"schema": "stage_e_release_calendar/1", "coverage": {"first": first, "last": last},
            "releases": releases}


def _ns(text: str) -> int:
    return int(pd.Timestamp(text).value)


class TestReleaseCalendar:
    def test_a_price_path_contract_reads_its_vehicles_list_and_cpi_in_ns(self) -> None:
        cal = release_calendar_from_dict(_raw_calendar(), "f" * 64, "reports/x.json")
        ev = event_calendar_from_release(cal, load_products())
        # NQ trades as MNQ: FOMC and MNQ's NFP; RTY trades as M2K: FOMC only
        assert ev.of("NQ").tolist() == [_ns("2019-06-07T12:30Z"), _ns("2019-06-19T18:00Z")]
        assert ev.of("RTY").tolist() == [_ns("2019-06-19T18:00Z")]
        assert ev.of("ZN").tolist() == [_ns("2019-06-07T12:30Z"), _ns("2019-06-19T18:00Z")]
        assert ev.cpi.tolist() == [_ns("2019-06-12T12:30Z")] and ev.cpi.dtype == np.int64
        assert ev.sha256 == "f" * 64 and ev.source == "reports/x.json"
        assert "RB" not in ev.releases and set(ev.releases) == set(TRADED)
        with pytest.raises(RouteInputMissing, match="no entry for RB"):
            ev.of("RB")

    def test_an_unlisted_price_path_contract_reads_its_vehicles_list(self) -> None:
        raw = _raw_calendar(paths_listed=False)
        ev = event_calendar_from_release(release_calendar_from_dict(raw, "f" * 64, "x"),
                                         load_products())
        assert ev.of("NQ").tolist() == [_ns("2019-06-07T12:30Z"), _ns("2019-06-19T18:00Z")]
        assert ev.of("CL").tolist() == [_ns("2019-06-19T18:00Z")]  # MCL's list

    def test_a_path_list_that_differs_from_its_vehicles_is_refused(self) -> None:
        raw = _raw_calendar(nq_own=["2019-07-19T18:00:00Z"])
        cal = release_calendar_from_dict(raw, "f" * 64, "x")
        with pytest.raises(ReleaseListMismatch, match="NQ .* and its vehicle MNQ"):
            event_calendar_from_release(cal, load_products())

    def test_an_identical_path_list_is_accepted(self) -> None:
        raw = _raw_calendar(nq_own=["2019-06-19T18:00:00Z", "2019-06-07T12:30:00Z"])
        cal = release_calendar_from_dict(raw, "f" * 64, "x")
        ev = event_calendar_from_release(cal, load_products())
        assert len(ev.of("NQ")) == 2  # duplicates of the same instants collapse

    def test_a_vehicle_the_calendar_does_not_list_is_refused(self) -> None:
        raw = _raw_calendar()
        raw["releases"][0]["products"] = [p for p in raw["releases"][0]["products"] if p != "MCL"]
        cal = release_calendar_from_dict(raw, "f" * 64, "x")
        with pytest.raises(RouteInputMissing, match="MCL, the vehicle of CL"):
            event_calendar_from_release(cal, load_products())

    def test_coverage_of_the_training_window_is_required(self) -> None:
        cal = release_calendar_from_dict(_raw_calendar(first="2019-06-01"), "f" * 64, "x")
        ev = event_calendar_from_release(cal, load_products())
        with pytest.raises(RouteInputMissing, match="does not cover the training window"):
            ev.require_coverage(date(2019, 5, 6), date(2024, 2, 29), "the training window")
        full = event_calendar_from_release(
            release_calendar_from_dict(_raw_calendar(), "f" * 64, "x"), load_products())
        full.require_coverage(date(2019, 5, 6), date(2024, 2, 29), "the training window")
        synthetic = EventCalendar({}, np.array([], dtype=np.int64), "synthetic", "0" * 64)
        with pytest.raises(RouteInputMissing, match="does not cover"):
            synthetic.require_coverage(date(2025, 4, 1), date(2026, 6, 19), "the research window")

    def test_the_runners_loader_is_used_and_its_refusal_is_named(self, monkeypatch) -> None:
        from screening import stage_e_rules

        def missing(root=None):  # noqa: ANN001, ANN202
            raise ReleaseCalendarMissing("reports/stage_e2b_release_calendar.json does not exist")

        monkeypatch.setattr(stage_e_rules, "load_release_calendar", missing)
        with pytest.raises(RouteInputMissing, match="release calendar is not available"):
            inputs_mod.load_event_calendar()
        cal = release_calendar_from_dict(_raw_calendar(), "a" * 64, "reports/y.json")
        monkeypatch.setattr(stage_e_rules, "load_release_calendar", lambda root=None: cal)
        assert inputs_mod.load_event_calendar().sha256 == "a" * 64

    def test_load_route_inputs_wires_both(self, monkeypatch) -> None:
        from screening import stage_e_rules

        cal = release_calendar_from_dict(_raw_calendar(), "a" * 64, "reports/y.json")
        monkeypatch.setattr(stage_e_rules, "load_release_calendar", lambda root=None: cal)
        _install(monkeypatch, _fake_start_module({r: date(2019, 5, 6) for r in TRADED}))
        got = inputs_mod.load_route_inputs()
        assert got.events.sha256 == "a" * 64 and len(got.s_x) == 28
        assert got.traded() == TRADED
        assert got.step2_sha256 == {r: "a" * 64 for r in TRADED}
        short = release_calendar_from_dict(_raw_calendar(last="2023-12-31"), "a" * 64, "y")
        monkeypatch.setattr(stage_e_rules, "load_release_calendar", lambda root=None: short)
        with pytest.raises(RouteInputMissing, match="training window"):
            inputs_mod.load_route_inputs()


# ----------------------------------------------------------- OC-M: the fill guard ----
def _mini_bars(minutes: list[int], base: int) -> Bars:
    ts = np.array([base + m * NS_MIN for m in minutes], dtype=np.int64)
    px = np.arange(len(ts), dtype=np.float64) + 100.0
    return Bars("NQ", ts, px, px, px, px, np.ones(len(ts)), np.ones(len(ts), dtype=np.int64),
                np.full(len(ts), np.datetime64("2019-06-03"), dtype="datetime64[D]"))


class TestDeferredExitKnownAnswers:
    BASE = 1_559_570_400 * 1_000_000_000  # 2019-06-03 14:00 UTC

    def test_not_in_a_guard_window(self) -> None:
        bars = _mini_bars(list(range(0, 60)), self.BASE)
        rel = np.array([self.BASE + 10 * NS_MIN], dtype=np.int64)
        assert deferred_exit(bars, rel, self.BASE + 12 * NS_MIN, self.BASE + 50 * NS_MIN) == (
            self.BASE + 12 * NS_MIN, 12, "none")

    def test_deferred_to_release_plus_two_minutes(self) -> None:
        bars = _mini_bars(list(range(0, 60)), self.BASE)
        rel = np.array([self.BASE + 10 * NS_MIN], dtype=np.int64)
        for x in (10, 11):  # [release, release + 2 min)
            assert deferred_exit(bars, rel, self.BASE + x * NS_MIN, self.BASE + 50 * NS_MIN) == (
                self.BASE + 12 * NS_MIN, 12, "deferred")

    def test_a_missing_bar_moves_the_fill_to_the_next_bar(self) -> None:
        bars = _mini_bars([m for m in range(0, 60) if m not in (12, 13)], self.BASE)
        rel = np.array([self.BASE + 10 * NS_MIN], dtype=np.int64)
        when, j, kind = deferred_exit(bars, rel, self.BASE + 10 * NS_MIN, self.BASE + 50 * NS_MIN)
        assert (when, kind) == (self.BASE + 14 * NS_MIN, "deferred") and bars.ts[j] == when

    def test_chained_releases_defer_again(self) -> None:
        bars = _mini_bars(list(range(0, 60)), self.BASE)
        rel = np.array([self.BASE + 10 * NS_MIN, self.BASE + 11 * NS_MIN], dtype=np.int64)
        # at 10: latest release 10 -> 12; 12 is inside [11, 13) -> 13
        assert deferred_exit(bars, rel, self.BASE + 10 * NS_MIN, self.BASE + 50 * NS_MIN)[0] == (
            self.BASE + 13 * NS_MIN)

    def test_a_deferral_reaching_f_is_the_forced_flatten_at_f(self) -> None:
        bars = _mini_bars(list(range(0, 60)), self.BASE)
        rel = np.array([self.BASE + 49 * NS_MIN], dtype=np.int64)
        f = self.BASE + 50 * NS_MIN
        assert deferred_exit(bars, rel, self.BASE + 49 * NS_MIN, f) == (f, 50, "flatten")
        assert deferred_exit(bars, rel, f, f) == (f, 50, "flatten")  # the to-F exit itself
        gap = _mini_bars([m for m in range(0, 60) if m != 50], self.BASE)
        assert deferred_exit(gap, rel, self.BASE + 49 * NS_MIN, f) == (f, -1, "flatten")


FIRST, LAST = date(2019, 5, 6), date(2019, 12, 31)


def _events(instants: list[int]) -> EventCalendar:
    arr = np.array(sorted(instants), dtype=np.int64)
    return EventCalendar({"NQ": arr}, np.array([], dtype=np.int64), "synthetic", "0" * 64)


@pytest.fixture(scope="module")
def nq() -> dict:
    frame = synthetic_bars("NQ", "equity", FIRST, LAST, 11, 0.25, 8000.0)
    bars = bars_from_frame("NQ", frame)
    base = build_from_bars({"NQ": bars}, synthetic_inputs({"NQ": FIRST}, _events([])))
    ok = np.flatnonzero(np.isfinite(base.y["h30"]) & np.isfinite(base.y["hF"]))
    r = int(ok[len(ok) // 2])
    return {"frame": frame, "bars": bars, "base": base, "t": int(base.t_ns[r]),
            "day": base.day[r]}


def _open(frame: pd.DataFrame, ts: int) -> float:
    return float(frame.loc[frame["ts_event"] == ts, "open"].iloc[0])


def _side(ts: int, side: str, event: bool) -> float:
    raw = json.loads(inputs_mod.COSTS_PATH.read_text(encoding="utf-8"))["products"]["MNQ"]
    local = pd.Timestamp(ts, tz="UTC").tz_convert("America/Chicago")
    m = local.hour * 60 + local.minute
    b = [b for b in raw["buckets"] if b["start_min"] <= m < b["end_min"]][0]
    half = max(x["half_spread_ticks"] for x in raw["buckets"]) if event else b["half_spread_ticks"]
    return half + b["depth_ticks"][side]


def _commission_ticks() -> float:
    raw = json.loads(inputs_mod.COSTS_PATH.read_text(encoding="utf-8"))["products"]["MNQ"]
    return raw["commission_rt_usd"] / raw["tick_value_usd"]


class TestOcmTargets:
    def test_an_exit_in_the_guard_is_deferred_and_charged_the_event_cost(self, nq) -> None:
        t, frame = nq["t"], nq["frame"]
        release = t + 29 * NS_MIN  # the h30 exit at t + 30 lies in [release, release + 2 min)
        tb = build_from_bars({"NQ": nq["bars"]}, synthetic_inputs({"NQ": FIRST},
                                                                  _events([release])))
        r = int(np.flatnonzero(tb.t_ns == t)[0])
        assert tb.exit_ns["h30"][r] == release + 2 * NS_MIN == t + 31 * NS_MIN
        cost = (_commission_ticks() + _side(t + NS_MIN, "buy", False)
                + _side(t + 31 * NS_MIN, "sell", True))
        move = (_open(frame, t + 31 * NS_MIN) - _open(frame, t + NS_MIN)) * 4
        assert tb.y["h30"][r] == pytest.approx((move - cost) / tb.sigma[r], rel=1e-12)
        assert tb.cost["h30"][r] == pytest.approx(cost / tb.sigma[r], rel=1e-12)
        assert tb.counts["target_h30_exit_deferred_event_guard"] == 1
        assert "target_h30_exit_in_event_guard" not in tb.counts
        # every other row's h30 target is unchanged, except the next decision's (its entry at
        # t + 31 lies in the release's 30-minute event window and pays the event cost)
        base = nq["base"]
        same = (tb.t_ns != t) & (tb.t_ns != t + 30 * NS_MIN)
        nxt = int(np.flatnonzero(tb.t_ns == t + 30 * NS_MIN)[0])
        assert tb.cost["h30"][nxt] > base.cost["h30"][nxt]
        assert np.array_equal(tb.y["h30"][same], base.y["h30"][same], equal_nan=True)

    def test_the_to_f_exit_in_a_guard_is_the_forced_flatten_at_f(self, nq) -> None:
        t, frame, day = nq["t"], nq["frame"], nq["day"]
        dt = day_times("NQ", "equity", day.astype(object))
        release = dt.flatten_ns - NS_MIN
        tb = build_from_bars({"NQ": nq["bars"]}, synthetic_inputs({"NQ": FIRST},
                                                                  _events([release])))
        on_day = np.flatnonzero((tb.day == day) & np.isfinite(tb.y["hF"]))
        assert len(on_day) == 12 and tb.counts["target_hF_exit_guard_forced_at_flatten"] == 12
        assert (tb.exit_ns["hF"][on_day] == dt.flatten_ns).all()
        r = int(np.flatnonzero(tb.t_ns == t)[0])
        cost = (_commission_ticks() + _side(t + NS_MIN, "buy", False)
                + _side(dt.flatten_ns, "sell", True))
        move = (_open(frame, dt.flatten_ns) - _open(frame, t + NS_MIN)) * 4
        assert tb.y["hF"][r] == pytest.approx((move - cost) / tb.sigma[r], rel=1e-12)

    def test_the_old_missing_target_rule_is_gone(self, nq) -> None:
        t = nq["t"]
        release = t + 29 * NS_MIN
        tb = build_from_bars({"NQ": nq["bars"]}, synthetic_inputs({"NQ": FIRST},
                                                                  _events([release])))
        assert np.isfinite(tb.y["h30"][tb.t_ns == t]).all()
        assert int(np.isfinite(tb.y["h30"]).sum()) == int(np.isfinite(nq["base"].y["h30"]).sum())


def test_cpi_instants_are_exact_nanoseconds() -> None:
    when = datetime(2026, 5, 12, 12, 30, tzinfo=UTC)
    assert inputs_mod._ns_of(when) == 1_778_589_000 * 1_000_000_000


def test_the_repo_root_reaches_both_shared_loaders(monkeypatch, tmp_path) -> None:
    from screening import stage_e_rules

    seen: dict = {}

    def calendar(root=None):  # noqa: ANN001, ANN202
        seen["calendar"] = root
        raise ReleaseCalendarMissing("absent under this root")

    monkeypatch.setattr(stage_e_rules, "load_release_calendar", calendar)
    with pytest.raises(RouteInputMissing, match="release calendar"):
        inputs_mod.load_route_inputs(repo_root=tmp_path)
    mod = _fake_start_module({"ZN": date(2019, 5, 6)})
    _install(monkeypatch, mod)
    assert inputs_mod.load_start_dates(["ZN"], repo_root=tmp_path) == {"ZN": date(2019, 5, 6)}
    assert seen == {"calendar": tmp_path} and mod.seen_root == tmp_path
