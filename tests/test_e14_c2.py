"""Harness v10 (Stage E.14): screening.stage_e14_c2, test C2's frozen rule and its run-once guard.

Synthetic bars (a LegFrame built in memory), a synthetic GEX CSV and the synthetic fixture
calendar. Run-once tests use a marker, output, registry, freeze, store and CSV under tmp_path;
the real reports/stage_e14_c2_RUN_ONCE.json is never written.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Iterator
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pytest

from data import hist_bars
from data.hist_calendar import HistGroupCalendar, load_hist_group_calendar
from data.hist_store import hist_parquet_path
from data.stage_e_bars import BAR_COLUMNS, LegFrame, StageEBarRefusal
from screening import stage_e14_c2 as c2
from screening import trial_registry as tr
from tests._e14_fixtures import FIXTURE_DIR, ct, next_weekday

HARNESS = "aa" * 32


@pytest.fixture(autouse=True, scope="module")
def real_marker_untouched() -> Iterator[None]:
    assert not c2.MARKER_PATH.exists()
    yield
    assert not c2.MARKER_PATH.exists()


@pytest.fixture(scope="module")
def cal() -> HistGroupCalendar:
    return load_hist_group_calendar("equity", base=FIXTURE_DIR)


# ------------------------------------------------------------------ builders ----
def _row(day: date, hhmm: str, open_px: float, close_px: float, closure: bool = False
         ) -> dict[str, Any]:
    return {"ts_event": ct(day, hhmm), "open": open_px, "high": max(open_px, close_px),
            "low": min(open_px, close_px), "close": close_px, "volume": 5,
            "instrument_id": 1, "raw_symbol": "ESM1", "trade_date": day.isoformat(),
            "in_flatten_window": False, "in_no_new_positions_window": False,
            "early_halt_ct": "", "in_scheduled_closure": closure, "is_roll_session": False,
            "gap_before_minutes": 0, "vendor_degraded_day": False}


def day_rows(day: date, prior: date, prior_close: float, close_1429: float, open_1430: float,
             open_1500: float, *, skip: str = "", closure: str = "") -> list[dict[str, Any]]:
    bars = {"b_14:59_prior": (prior, "14:59", prior_close, prior_close),
            "b_14:29": (day, "14:29", close_1429, close_1429),
            "b_14:30": (day, "14:30", open_1430, open_1430),
            "b_15:00": (day, "15:00", open_1500, open_1500)}
    return [_row(d, t, o, c, closure == name) for name, (d, t, o, c) in bars.items()
            if name != skip]


def leg_of(rows: list[dict[str, Any]], blackout: frozenset[date] = frozenset()) -> LegFrame:
    frame = pd.DataFrame(rows, columns=list(BAR_COLUMNS)).drop_duplicates("ts_event")
    frame = frame.sort_values("ts_event").reset_index(drop=True)
    days = tuple(sorted({date.fromisoformat(d) for d in frame["trade_date"]}))
    return LegFrame("ES", "hist:es2011", "synthetic", "0" * 64, frame, days, (), blackout)


def gex_csv(values: dict[date, float]) -> bytes:
    lines = ["date,price,dix,gex"] + [f"{d.isoformat()},1300.0,0.4,{v}"
                                      for d, v in sorted(values.items())]
    return ("\n".join(lines) + "\n").encode()


def gex_of(values: dict[date, float]) -> c2.GexSeries:
    return c2.parse_gex(gex_csv(values), Path("gex.csv"))


def weekdays(first: date, last: date) -> list[date]:
    return [first + timedelta(days=n) for n in range((last - first).days + 1)
            if (first + timedelta(days=n)).weekday() < 5]


# ------------------------------------------------------------------ constants ----
def test_the_cost_and_pass_bar_are_the_frozen_numbers() -> None:
    assert c2.COST_TICKS == 2.0379 and c2.PASS_BAR_TICKS == 3.05685
    assert math.isclose(c2.COMMISSION_TICKS, 1.22 / 1.25)
    assert (c2.SPREAD_1430_TICKS, c2.SPREAD_1500_TICKS) == (0.5191, 0.5428)
    assert c2.ALPHA == 0.025 and c2.MIN_TRADES == 30
    assert (date(2011, 5, 3), date(2019, 4, 30)) == c2.WINDOW


# ------------------------------------------------------------------ GEX timing ----
def test_gex_lag_1_uses_the_latest_row_strictly_before_d_and_lag_2_the_row_before() -> None:
    gex = gex_of({date(2011, 5, 2): -1.0, date(2011, 5, 3): 1.0, date(2011, 5, 4): -5.0})
    d = date(2011, 5, 4)
    assert gex.dates[c2.gex_index(gex, d, 1)] == date(2011, 5, 3)
    assert gex.dates[c2.gex_index(gex, d, 2)] == date(2011, 5, 2)
    assert c2.gex_index(gex, date(2011, 5, 2), 1) is None
    assert c2.gex_index(gex, date(2011, 5, 3), 2) is None
    with pytest.raises(ValueError):
        c2.gex_index(gex, d, 3)


def test_the_gex_row_decides_t1_membership_under_each_lag(cal: HistGroupCalendar) -> None:
    # Arrange: one eligible date, 2011-05-04
    d, prior = date(2011, 5, 4), date(2011, 5, 3)
    leg = leg_of(day_rows(d, prior, 1300.0, 1301.0, 1301.25, 1302.75))
    gex = gex_of({date(2011, 5, 2): -1.0, prior: 1.0, d: -5.0})

    # Act
    lag1, _ = c2.evaluate(leg, cal, gex, 1)
    lag2, _ = c2.evaluate(leg, cal, gex, 2)

    # Assert: the row dated d itself is never used
    assert [t.gex_negative for t in lag1] == [False] and [t.gex_negative for t in lag2] == [True]


@pytest.mark.parametrize("text,match", [
    ("date,price,dix\n2011-05-02,1,2\n", "lacks"),
    ("date,price,dix,gex\n2011-05-02,1,2,3\n2011-05-02,1,2,4\n", "repeats"),
    ("date,price,dix,gex\n2011-05-02,1,2,nan\n", "finite"),
    ("date,price,dix,gex\n05/02/2011,1,2,3\n", "unreadable"),
    ("date,price,dix,gex\n", "no rows"),
])
def test_a_malformed_gex_csv_is_refused(text: str, match: str) -> None:
    with pytest.raises(ValueError, match=match):
        c2.parse_gex(text.encode(), Path("g.csv"))


def test_load_gex_refuses_a_file_whose_sha_differs(tmp_path: Path) -> None:
    path = tmp_path / "g.csv"
    path.write_bytes(gex_csv({date(2011, 5, 2): 1.0}))
    with pytest.raises(ValueError, match="expected"):
        c2.load_gex(path, "0" * 64)
    assert c2.load_gex(path, hashlib.sha256(path.read_bytes()).hexdigest()).record()["rows"] == 1


# ------------------------------------------------------------------ the rule ----
def test_side_follows_the_rest_of_day_return_and_g_is_in_mes_ticks(
        cal: HistGroupCalendar) -> None:
    # Arrange: a long day and a short day
    up, down = date(2011, 5, 4), date(2011, 5, 5)
    rows = (day_rows(up, date(2011, 5, 3), 1300.0, 1301.0, 1301.25, 1302.75)
            + day_rows(down, up, 1310.0, 1305.0, 1305.0, 1304.0))
    gex = gex_of({date(2011, 5, 2): -1.0, date(2011, 5, 3): -1.0, up: 2.0})

    # Act
    trades, counts = c2.evaluate(leg_of(rows), cal, gex, 1)

    # Assert
    assert [(t.day, t.side, t.g, t.gex_negative) for t in trades] == [
        (up, 1, 6.0, True), (down, -1, 4.0, False)]
    assert counts["eligible_dates"] == 2 and counts["ties_no_trade"] == 0


def test_a_tie_is_no_trade_and_is_counted(cal: HistGroupCalendar) -> None:
    d = date(2011, 5, 4)
    trades, counts = c2.evaluate(leg_of(day_rows(d, date(2011, 5, 3), 1300.0, 1300.0, 1300.0,
                                                 1301.0)), cal,
                                 gex_of({date(2011, 5, 3): -1.0}), 1)
    assert trades == [] and counts["ties_no_trade"] == 1 and counts["eligible_dates"] == 1


@pytest.mark.parametrize("skip", ["b_14:29", "b_14:30", "b_15:00", "b_14:59_prior"])
def test_a_missing_bar_excludes_the_date_by_reason(cal: HistGroupCalendar, skip: str) -> None:
    d = date(2011, 5, 4)
    leg = leg_of(day_rows(d, date(2011, 5, 3), 1300.0, 1301.0, 1301.0, 1302.0, skip=skip))
    trades, counts = c2.evaluate(leg, cal, gex_of({date(2011, 5, 3): -1.0}), 1)
    by_name = counts["excluded_bars_by_name"]
    assert trades == [] and counts["eligible_dates"] == 0
    # every other window date has no bar at all, so it misses b_14:29 first
    others = counts["excluded_by_reason"]["missing_bar"] - 1
    assert by_name.get(f"missing_bar:{skip}", 0) == (1 if skip != "b_14:29" else 1 + others)


def test_a_bar_inside_a_scheduled_closure_counts_as_absent(cal: HistGroupCalendar) -> None:
    d = date(2011, 5, 4)
    leg = leg_of(day_rows(d, date(2011, 5, 3), 1300.0, 1301.0, 1301.0, 1302.0,
                          closure="b_15:00"))
    trades, counts = c2.evaluate(leg, cal, gex_of({date(2011, 5, 3): -1.0}), 1)
    assert trades == [] and counts["excluded_by_reason"]["bar_in_scheduled_closure"] == 1


@pytest.mark.parametrize("day,reason", [
    (date(2011, 5, 30), "early_halt"),  # fixture early halt (Memorial Day)
    (date(2011, 11, 25), "early_halt"),
    (date(2018, 12, 5), "late_open"),
    (date(2012, 10, 29), "not_a_trade_date"),  # full closure
    (date(2015, 6, 15), "unsourced"),  # listed unsourced
    (date(2016, 3, 25), "unsourced"),  # unverified entry
    (date(2015, 6, 16), "prior_trade_date_unsourced"),  # its prior trade date is unsourced
    (date(2016, 3, 28), "prior_trade_date_unsourced"),  # an unsourced weekday lies between
])
def test_calendar_exclusions_apply_before_any_bar_is_read(cal: HistGroupCalendar, day: date,
                                                          reason: str) -> None:
    assert c2.calendar_reason(day, cal, frozenset())[0] == reason


def test_a_roll_blackout_date_is_excluded(cal: HistGroupCalendar) -> None:
    d = date(2011, 5, 4)
    leg = leg_of(day_rows(d, date(2011, 5, 3), 1300.0, 1301.0, 1301.0, 1302.0),
                 blackout=frozenset({d}))
    trades, counts = c2.evaluate(leg, cal, gex_of({date(2011, 5, 3): -1.0}), 1)
    assert trades == [] and counts["excluded_by_reason"]["roll_blackout"] == 1


def test_the_first_window_date_reads_the_stores_first_trade_date_as_prior(
        cal: HistGroupCalendar) -> None:
    assert c2.calendar_reason(date(2011, 5, 3), cal, frozenset()) == (None, date(2011, 5, 2))


def test_every_window_weekday_is_counted_exactly_once(cal: HistGroupCalendar) -> None:
    trades, counts = c2.evaluate(leg_of([]), cal, gex_of({date(2011, 5, 2): 1.0}), 1)
    total = counts["eligible_dates"] + sum(counts["excluded_by_reason"].values())
    expected = int(np.busday_count("2011-05-03", "2019-05-01"))
    assert total == counts["weekdays_considered"] == len(c2.window_weekdays()) == expected


# ------------------------------------------------------------------ statistics ----
def test_the_statistics_match_a_hand_computation() -> None:
    from scipy.stats import t as student_t

    g = [5.0, 3.0, 4.0, 6.0, -2.0, 7.0]
    out = c2.stats_of(g)
    mean, sd = np.mean(g), np.std(g, ddof=1)
    t = mean / (sd / math.sqrt(len(g)))
    assert out["n"] == 6 and math.isclose(out["mean"], mean) and math.isclose(out["sd"], sd)
    assert math.isclose(out["t"], t) and math.isclose(out["p"], student_t.sf(t, 5))
    assert out["criteria"]["n_at_least_30"] is False and out["passes"] is False


def test_the_pass_bar_boundary_is_inclusive_on_mean_and_p() -> None:
    bar = c2.PASS_BAR_TICKS
    assert c2.passes(bar, 0.025, 30)
    assert not c2.passes(float(np.nextafter(bar, 0.0)), 0.025, 30)
    assert not c2.passes(bar, float(np.nextafter(0.025, 1.0)), 30)
    assert not c2.passes(bar, 0.025, 29)


def test_constant_or_tiny_samples_never_pass_by_accident() -> None:
    assert c2.stats_of([])["passes"] is False and c2.stats_of([9.0])["passes"] is False
    flat = c2.stats_of([4.0] * 40)
    assert flat["t"] is None and flat["t_text"] == "inf" and flat["passes"] is True
    assert c2.stats_of([-4.0] * 40)["passes"] is False


@pytest.mark.parametrize("t1,t2,verdict,alone", [
    ({"passes": True, "mean": 5.0}, {"passes": True, "mean": 4.0}, "PASS", False),
    ({"passes": True, "mean": 4.0}, {"passes": True, "mean": 4.0}, "FAIL", False),
    ({"passes": False, "mean": 9.0}, {"passes": True, "mean": 4.0}, "FAIL", True),
    ({"passes": False, "mean": 1.0}, {"passes": False, "mean": 0.5}, "FAIL", False),
])
def test_the_hypothesis_verdict_needs_t1_to_pass_and_beat_t2(t1: dict, t2: dict, verdict: str,
                                                             alone: bool) -> None:
    out = c2.verdict_of(t1, t2)
    assert out["verdict"] == verdict and out["t2_passes_alone"] is alone


def _many_days(cal: HistGroupCalendar) -> tuple[LegFrame, c2.GexSeries]:
    """40 eligible days in mid-2011: GEX < 0 on every other day; long +8 ticks on GEX < 0
    days, otherwise a short that loses 2 ticks."""
    rows: list[dict[str, Any]] = []
    values: dict[date, float] = {}
    days = weekdays(date(2011, 6, 1), date(2011, 7, 29))[:40]
    for i, d in enumerate(days):
        prior = date(2011, 5, 31) if i == 0 else days[i - 1]
        values[prior] = -1.0 if i % 2 == 0 else 1.0
        if i % 2 == 0:
            rows += day_rows(d, prior, 1300.0, 1301.0, 1300.0, 1302.0 + 0.25 * (i % 3))
        else:
            rows += day_rows(d, prior, 1301.0, 1300.0, 1300.0, 1300.5)
    rows += [_row(date(2011, 5, 31), "14:59", 1300.0, 1300.0)]
    return leg_of(rows), gex_of(values)


def test_t1_and_t2_on_a_synthetic_panel(cal: HistGroupCalendar) -> None:
    # Act
    leg, gex = _many_days(cal)
    trades, counts = c2.evaluate(leg, cal, gex, 1)
    result = c2.result_of(trades, counts)

    # Assert
    t1, t2 = result["tests"]["C2-T1"], result["tests"]["C2-T2"]
    assert (t1["n"], t1["long"], t1["short"]) == (20, 20, 0)
    assert (t2["n"], t2["long"], t2["short"]) == (40, 20, 20)
    assert t1["mean"] > c2.PASS_BAR_TICKS and t1["criteria"]["n_at_least_30"] is False
    assert result["verdict"] == "FAIL" and counts["eligible_dates_gex_negative"] == 20
    assert len(result["trades_sha256"]) == 64


def test_count_gex_negative_reads_calendar_and_gex_only(cal: HistGroupCalendar) -> None:
    values = {d: (-1.0 if d.day % 2 else 1.0) for d in weekdays(date(2011, 5, 2),
                                                                 date(2019, 4, 29))}
    out = c2.count_gex_negative(cal, gex_of(values), 1)
    assert out["weekdays"] == 2086 and out["gex_negative"] > 0
    assert out["calendar_and_gex_eligible"] + sum(out["excluded_by_reason"].values()) == 2086
    assert "roll_blackout" in out["not_applied"]


# ------------------------------------------------------------------ run once ----
@pytest.fixture
def run_env(tmp_path: Path, cal: HistGroupCalendar) -> dict[str, Any]:
    freeze = tmp_path / "stage_e14_prereg_C2.md"
    freeze.write_text("# C2 frozen\n", encoding="utf-8")
    freeze_sha = hashlib.sha256(freeze.read_bytes()).hexdigest()
    registry = tmp_path / "registry.jsonl"
    tr.init_registry(registry)
    tr.register("C2", ["C2-T1", "C2-T2"], freeze, freeze_sha, HARNESS, path=registry)
    store = hist_parquet_path("ES", "es2011", tmp_path / "hist")
    store.parent.mkdir(parents=True)
    store.write_bytes(b"synthetic store stand-in")
    leg, gex = _many_days(cal)
    gex_path = tmp_path / "gex.csv"
    gex_path.write_bytes(gex_csv(dict(zip(gex.dates, gex.gex, strict=True))))
    inp = c2.RunInputs(
        store_sha256=hashlib.sha256(store.read_bytes()).hexdigest(), gex_path=gex_path,
        gex_sha256=hashlib.sha256(gex_path.read_bytes()).hexdigest(), gex_lag=1,
        harness_sha256=HARNESS, freeze_sha256=freeze_sha, out=tmp_path / "out" / "c2.json",
        freeze_path=freeze, marker_path=tmp_path / "RUN_ONCE.json", registry_path=registry,
        hist_root=tmp_path / "hist", calendar_base=FIXTURE_DIR)
    return {"inp": inp, "leg": leg, "registry": registry}


def _patch_leg(monkeypatch: pytest.MonkeyPatch, inp: c2.RunInputs, leg: LegFrame,
               seen: list[bool]) -> None:
    def fake(root: str, plan: str, **kwargs: Any) -> LegFrame:
        seen.append(inp.marker_path.exists())  # the marker exists before any bar is read
        assert (root, plan, kwargs["expected_sha256"]) == ("ES", "es2011", inp.store_sha256)
        return leg

    monkeypatch.setattr(hist_bars, "load_hist_leg", fake)


def test_the_run_writes_the_marker_before_reading_bars_then_the_result_and_runs_once(
        run_env: dict[str, Any], monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    inp, seen = run_env["inp"], []
    _patch_leg(monkeypatch, inp, run_env["leg"], seen)

    # Act
    payload = c2.run(inp, preflight=lambda sha: sha, log=lambda m: None)

    # Assert
    assert seen == [True] and payload["verdict"] == "FAIL"
    written = json.loads(inp.out.read_text(encoding="utf-8"))
    assert written["tests"]["C2-T2"]["n"] == 40 and written["stop_reason"] is None
    assert written["inputs"]["registry"]["n_after"] == 473
    assert written["inputs"]["gex"]["sha256"] == inp.gex_sha256
    assert written["inputs"]["calendar"]["sha256"] == load_hist_group_calendar(
        "equity", base=FIXTURE_DIR).file_sha256
    assert written["rule"]["pass_bar_ticks"] == 3.05685 and written["rule"]["gex_lag"] == 1
    assert "1300" not in inp.out.read_text(encoding="utf-8")  # no price is written
    marker = json.loads(inp.marker_path.read_text(encoding="utf-8"))
    assert marker["test"] == "C2" and marker["gex_lag"] == 1
    with pytest.raises(c2.C2Refused, match="runs once"):
        c2.run(inp, preflight=lambda sha: sha, log=lambda m: None)


def test_a_store_refusal_after_the_marker_is_a_stopped_verdict(
        run_env: dict[str, Any], monkeypatch: pytest.MonkeyPatch) -> None:
    inp = run_env["inp"]

    def refuse(*args: Any, **kwargs: Any) -> LegFrame:
        raise StageEBarRefusal("rows outside the store")

    monkeypatch.setattr(hist_bars, "load_hist_leg", refuse)
    payload = c2.run(inp, preflight=lambda sha: sha, log=lambda m: None)
    assert payload["verdict"] == "STOPPED" and "rows outside the store" in payload["stop_reason"]
    assert inp.marker_path.exists() and inp.out.exists()


def _refused(inp: c2.RunInputs, match: str) -> None:
    with pytest.raises(c2.C2Refused, match=match):
        c2.run(inp, preflight=lambda sha: sha, log=lambda m: None)
    assert not inp.marker_path.exists() and not inp.out.exists()


@pytest.mark.parametrize("change,match", [
    ({"freeze_sha256": "1" * 64}, "freeze"),
    ({"store_sha256": "2" * 64}, "store"),
    ({"gex_sha256": "3" * 64}, "GEX CSV"),
    ({"gex_lag": 3}, "GEX_LAG"),
])
def test_a_precondition_failure_writes_nothing(run_env: dict[str, Any], change: dict[str, Any],
                                               match: str, monkeypatch: pytest.MonkeyPatch
                                               ) -> None:
    monkeypatch.setattr(hist_bars, "load_hist_leg", lambda *a, **k: pytest.fail("bars read"))
    inp = run_env["inp"]
    fields = {k: getattr(inp, k) for k in inp.__dataclass_fields__}
    _refused(c2.RunInputs(**{**fields, **change}), match)


def test_the_run_refuses_without_the_registration_or_with_a_marker_or_output(
        run_env: dict[str, Any], tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(hist_bars, "load_hist_leg", lambda *a, **k: pytest.fail("bars read"))
    inp = run_env["inp"]
    fields = {k: getattr(inp, k) for k in inp.__dataclass_fields__}
    empty = tmp_path / "empty.jsonl"
    tr.init_registry(empty)
    _refused(c2.RunInputs(**{**fields, "registry_path": empty}), "not registered")
    inp.out.parent.mkdir(parents=True, exist_ok=True)
    inp.out.write_text("{}", encoding="utf-8")
    with pytest.raises(c2.C2Refused, match="runs once"):
        c2.run(inp, preflight=lambda sha: sha, log=lambda m: None)
    inp.out.unlink()
    inp.marker_path.write_text("{}", encoding="utf-8")
    with pytest.raises(c2.C2Refused, match="runs once"):
        c2.run(inp, preflight=lambda sha: sha, log=lambda m: None)


def test_a_missing_or_malformed_calendar_is_refused_before_the_marker(
        run_env: dict[str, Any], tmp_path: Path) -> None:
    inp = run_env["inp"]
    fields = {k: getattr(inp, k) for k in inp.__dataclass_fields__}
    _refused(c2.RunInputs(**{**fields, "calendar_base": tmp_path / "nowhere"}), "does not exist")
    bad = tmp_path / "badcal"
    bad.mkdir()
    (bad / "equity.json").write_text('{"schema": "e14_hist_calendar/0"}', encoding="utf-8")
    _refused(c2.RunInputs(**{**fields, "calendar_base": bad}), "calendar refused")


def test_the_preflight_runs_first(run_env: dict[str, Any]) -> None:
    def refuse(sha: str) -> str:
        raise c2.harness_freeze.HarnessFreezeError("tree differs")

    with pytest.raises(c2.harness_freeze.HarnessFreezeError):
        c2.run(run_env["inp"], preflight=refuse, log=lambda m: None)
    assert not run_env["inp"].marker_path.exists()


def test_the_cli_count_prints_counts_only(tmp_path: Path, capsys: pytest.CaptureFixture[str]
                                          ) -> None:
    path = tmp_path / "g.csv"
    path.write_bytes(gex_csv({date(2011, 5, 2): -1.0, date(2011, 5, 3): 2.5}))
    rc = c2.main(["count", "--gex", str(path), "--gex-sha256",
                  hashlib.sha256(path.read_bytes()).hexdigest(), "--gex-lag", "1"],
                 calendar_base=FIXTURE_DIR)
    out = json.loads(capsys.readouterr().out)
    assert rc == 0 and out["gex_negative"] == 1 and "2.5" not in json.dumps(out)


def test_the_cli_run_refuses_without_writing_when_a_precondition_fails(
        tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rc = c2.main(["--store-sha256", "0" * 64, "--gex", str(tmp_path / "none.csv"),
                  "--gex-sha256", "0" * 64, "--gex-lag", "1", "--harness-sha256", HARNESS,
                  "--freeze-sha256", "0" * 64, "--freeze", str(tmp_path / "none.md"),
                  "--out", str(tmp_path / "o.json")],
                 preflight=lambda sha: sha, calendar_base=FIXTURE_DIR)
    assert rc == c2.RC_REFUSED and "nothing written" in capsys.readouterr().err
    assert not (tmp_path / "o.json").exists()


def test_next_weekday_helper_skips_weekends() -> None:
    assert next_weekday(date(2011, 5, 6)) == date(2011, 5, 9)


# ------------------------------------------------------------------ end to end ----
def test_end_to_end_on_a_built_es2011_store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                                            run_env: dict[str, Any]) -> None:
    """Synthetic chunks -> data.hist_store -> data.hist_bars.load_hist_leg -> the rule."""
    from data import hist_store as hs
    from data import pull_hist as ph
    from screening import harness_freeze
    from tests._e14_fixtures import PX, TICK_ES, bar, make_store_inputs

    # Arrange: two eligible dates, a long on 05-03 (GEX < 0 the day before) and a short on 05-04
    monkeypatch.setattr(harness_freeze, "preflight", lambda expected, root=None: expected)
    q = TICK_ES
    bars = [bar(ct("2011-05-02", "14:59"), PX, PX),
            bar(ct("2011-05-03", "14:29"), PX + 4 * q, PX + 4 * q),
            bar(ct("2011-05-03", "14:30"), PX + 4 * q, PX + 4 * q),
            bar(ct("2011-05-03", "14:59"), PX + 9 * q, PX + 9 * q),
            bar(ct("2011-05-03", "15:00"), PX + 10 * q, PX + 10 * q),
            bar(ct("2011-05-04", "14:29"), PX + 2 * q, PX + 2 * q),
            bar(ct("2011-05-04", "14:30"), PX + 2 * q, PX + 2 * q),
            bar(ct("2011-05-04", "15:00"), PX + 5 * q, PX + 5 * q)]
    paths = make_store_inputs(tmp_path / "s", ph.ES2011, "ES", bars, splice="2013-06-13",
                              iids=(1001, 1002), raws=("ESM1", "ESU1"))
    summary = hs.run_product("ES", "es2011", expected_harness_sha256=HARNESS,
                             out_base=tmp_path / "store", reports_base=paths["reports"],
                             rolls_dir=paths["rolls"], condition_dir=paths["condition_dir"],
                             calendar_base=FIXTURE_DIR, log=lambda m: None)
    assert summary["status"] == "built", summary["refusal_causes"]
    gex_path = tmp_path / "gex2.csv"
    gex_path.write_bytes(gex_csv({date(2011, 5, 2): -3.0, date(2011, 5, 3): 4.0}))
    inp = run_env["inp"]
    fields = {k: getattr(inp, k) for k in inp.__dataclass_fields__}
    inp = c2.RunInputs(**{**fields, "hist_root": tmp_path / "store",
                          "store_sha256": summary["parquet"]["sha256"], "gex_path": gex_path,
                          "gex_sha256": hashlib.sha256(gex_path.read_bytes()).hexdigest()})

    # Act
    payload = c2.run(inp, preflight=lambda sha: sha, log=lambda m: None)

    # Assert: 05-03 long +6 ticks (T1 and T2); 05-04 short, -(5 - 2) = -3 ticks (T2 only)
    assert payload["verdict"] == "FAIL", payload.get("stop_reason")
    assert payload["eligibility"]["eligible_dates"] == 2
    t1, t2 = payload["tests"]["C2-T1"], payload["tests"]["C2-T2"]
    assert (t1["n"], t1["mean"], t1["long"]) == (1, 6.0, 1)
    assert (t2["n"], t2["mean"], t2["short"]) == (2, 1.5, 1)
