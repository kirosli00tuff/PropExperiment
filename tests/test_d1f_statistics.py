"""Stage D.1f Task 4: strategy/research/_d1f_statistics.py (list 5.4, 3.2(ii)).

Two groups:
- EDA reproduction (the Task 1c check): on the research bars' 139 EDA dates, the only real
  date set this test touches (sanctioned by the stage prompt), the wrapper reproduces every
  recorded estimate, n and implied edge of both facts files to 1e-9, the recorded G0, F3.1
  and Q80 figures, reports/stage_d1e_members_events.json, and every per-event value of the
  hashed strategy/research/_d1e_event_series.py.
- Synthetic bars (2030 dates, no real data): exclusions, and forward intervals checked
  independently against the bars' own prices and clocks, and the drift helper.
"""

from __future__ import annotations

import hashlib
import inspect
import json
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import pytest

import strategy.research._d1f_statistics as stats_mod
import strategy.research.f_data_native._stylized_facts as fsf
from data.research_bars import RESEARCH_SERIES_PATH
from screening.drift import build_drift_path
from strategy.research._d1f_statistics import (
    CLOSE,
    NS_PER_MINUTE,
    OPEN,
    StatisticEvents,
    compute_statistics,
    forward_mean_moves_ticks,
)

TOL = 1e-9
TICK = 0.25
CT = ZoneInfo("America/Chicago")
REPORTS = Path("reports")
HAS_RESEARCH = RESEARCH_SERIES_PATH.exists()
needs_research = pytest.mark.skipif(not HAS_RESEARCH, reason="research parquet not present")

# list section 0: these must be byte-identical (the wrapper never edits them)
HASHED = {
    "strategy/research/f_data_native/_stylized_facts.py":
        "a692c47f226638876cda94541c5669e821873ef10f401b1564a85365ebf1f056",
    "strategy/research/g_timeframe/_stylized_facts.py":
        "61ae1930f9b2aa466e178842f0b02d0486e22c084615ea491fdaccd54b39653d",
    "strategy/research/g_timeframe/resample.py":
        "a0851b43ef33818563805b04d4ee27d851914f2e42e8c7ba3255d04e2f40bdc2",
    "strategy/research/_d1e_event_series.py":
        "51ec1d881cfdd9385f421809c2cdcfa9f8233d18ac5dcddbd92e84c3f8e90645",
}


def _close(a: float | None, b: float | None) -> bool:
    if a is None or b is None:
        return a is None and b is None
    return abs(float(a) - float(b)) <= TOL


# --------------------------------------------------------------- interval clock checks ----
def _ct_minute(ns: np.ndarray) -> np.ndarray:
    local = pd.to_datetime(ns, utc=True).tz_convert(CT)
    return np.asarray(local.hour * 60 + local.minute)


def _check_clocks(ev: StatisticEvents) -> None:
    """The declared forward window, per statistic type, read off the interval clocks."""
    if not len(ev.values):
        return
    start, end = ev.start_clock_ns, ev.end_clock_ns
    minutes = (end - start) // NS_PER_MINUTE
    same_day = ~ev.crosses_trade_date
    assert np.all(end > start)
    sid = ev.stat_id
    if ev.family == "F4.4":
        assert set(ev.start_price) == {OPEN} and set(ev.end_price) == {CLOSE}
        assert np.all(minutes[same_day] == 16)  # open(i) -> close(i+15)
        return
    assert set(ev.start_price) == {CLOSE} and set(ev.end_price) == {CLOSE}
    assert not ev.crosses_trade_date.any()
    if sid.startswith("F1_1_h"):
        h = int(sid.split("_h")[1].split("_")[0])
        assert np.all(minutes == h)
        if sid.endswith("_RTH") and h > 1:
            assert np.all((_ct_minute(start) - 510) % h == 0)  # on the 08:30 CT grid
    elif sid.startswith(("F2_4", "F3_2", "F5_")):
        h = 15 if sid.startswith("F2_4") else 30
        assert np.all(minutes == h) and np.all((_ct_minute(start) - 510) % h == 0)
    if sid.startswith("F3_2_bucket07_bucket08"):
        assert set(_ct_minute(start)) == {12 * 60} and set(_ct_minute(end)) == {12 * 60 + 30}
    if sid.startswith("F3_3"):
        assert set(_ct_minute(start)) == {14 * 60 + 30} and set(_ct_minute(end)) == {15 * 60}
    if sid == "F6_1_overnight_range_position":
        assert set(_ct_minute(start)) == {8 * 60 + 30} and set(_ct_minute(end)) == {9 * 60 + 30}
    if sid.startswith(("F4_1", "F4_2")):
        assert np.all(minutes == 15)
    if sid.startswith("G"):
        tf = int(sid.split(".")[2])
        if sid.startswith("G3"):
            assert np.all(_ct_minute(end) <= 15 * 60)
        else:
            assert np.all((minutes > 0) & (minutes <= 2 * tf))


# ================================================================== EDA reproduction ====
@pytest.fixture(scope="module")
def eda_run():
    from data.research_bars import load_research_bars
    from sim.engine import BAR_COLUMNS, splice_trade_dates_from_parquet

    frame = load_research_bars(list(BAR_COLUMNS))
    days = sorted(set(pd.to_datetime(frame["trade_date"].astype(str)).dt.date))
    eda_raw = days[142:289]  # exactly resolve_eda_dates' candidate slice
    return compute_statistics(frame, eda_raw, splice_trade_dates_from_parquet(
        RESEARCH_SERIES_PATH))


@pytest.fixture(scope="module")
def hashed_eda():
    from strategy.research._d1e_event_series import collect_f_stats, collect_g_stats
    from strategy.research.f_data_native._stylized_facts import resolve_eda_dates

    eda_dates, excluded, bars = resolve_eda_dates()
    stats = collect_f_stats(bars, eda_dates) + collect_g_stats(bars, eda_dates)
    return eda_dates, excluded, stats


def test_hashed_modules_are_byte_identical() -> None:
    for path, sha in HASHED.items():
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == sha, path


def test_module_loads_no_bars_itself() -> None:
    src = inspect.getsource(stats_mod)
    for banned in ("read_parquet", "pyarrow", "pads.", "load_research_bars(",
                   "load_confirmation_bars(", "resolve_eda_dates()"):
        assert banned not in src, banned


@needs_research
def test_eda_dates_and_exclusions_match_resolve_eda_dates(eda_run, hashed_eda) -> None:
    eda_dates, excluded, _ = hashed_eda
    assert len(eda_run.dates) == 139
    assert eda_run.dates == tuple(eda_dates)
    assert [dict(e) for e in eda_run.excluded] == excluded
    assert any("vendor_degraded_day" in e["reason"] for e in excluded)


@needs_research
def test_every_family_f_record_reproduces(eda_run) -> None:
    facts = json.loads((REPORTS / "stage_d1b_family_f_facts.json").read_text())
    records = facts["tested_statistics"]
    assert len(records) == 57
    for r in records:
        if r["directional"]:
            ev = eda_run.directional[r["id"]]
            got = (ev.estimate, ev.n, ev.implied_edge_ticks)
            for k in ("control_mean_ticks", "n_control"):
                if k in r:
                    assert _close(ev.extra[k], r[k]), (r["id"], k)
        else:
            d = eda_run.descriptive[r["id"]]
            got = (d["estimate"], d["n"], None)
        assert _close(got[0], r["estimate"]), (r["id"], got[0], r["estimate"])
        assert got[1] == r["n"], r["id"]
        assert _close(got[2], r["implied_edge_ticks"]), r["id"]
    assert len(eda_run.descriptive) == 21


@needs_research
def test_every_family_g_record_and_q80_reproduces(eda_run) -> None:
    facts = json.loads((REPORTS / "stage_d1d_family_g_facts.json").read_text())
    records = facts["tested_statistics"]
    assert len(records) == 28
    for r in records:
        ev = eda_run.directional[r["id"]]
        assert _close(ev.estimate, r["estimate"]), r["id"]
        assert ev.n == r["n"] == r["n_events"] == len(ev.values), r["id"]
        assert _close(ev.implied_edge_ticks, r["implied_edge_ticks"]), r["id"]
        if r["q80"] is not None:
            assert _close(eda_run.thresholds[f"{r['id']}_q80"][0], r["q80"]), r["id"]
    for row in facts["g0_vs_family_f_f1_1"]:
        mine = next(g for g in eda_run.g0
                    if g["tf"] == row["tf"] and g["segment"] == row["segment"])
        assert mine["n_pairs"] == row["n_pairs"]
        assert _close(mine["lag1_autocorrelation"], row["lag1_autocorrelation"])


@needs_research
def test_f3_1_descriptive_table_reproduces(eda_run) -> None:
    recorded = json.loads((REPORTS / "stage_d1b_family_f_facts.json").read_text())[
        "f3_1_descriptive_table"]
    assert len(recorded) == len(eda_run.f3_1_table) == 13
    for mine, rec in zip(eda_run.f3_1_table, recorded, strict=True):
        for k, v in rec.items():
            assert _close(mine[k], v) if isinstance(v, float) else mine[k] == v, k


@needs_research
def test_members_events_file_reproduces(eda_run) -> None:
    rec = json.loads((REPORTS / "stage_d1e_members_events.json").read_text())
    assert [d.isoformat() for d in eda_run.dates] == rec["meta"]["eda_dates"]
    members, coverage = rec["statistics"], rec["coverage_statistics"]
    assert (len(members), len(coverage)) == (21, 43)
    assert set(eda_run.directional) == set(members) | set(coverage)
    for sid, r in members.items():
        ev = eda_run.directional[sid]
        assert np.allclose(ev.values, r["event_values_ticks"], rtol=0, atol=TOL), sid
        assert [d.isoformat() for d in ev.trade_dates] == r["event_dates"], sid
        assert _close(ev.implied_edge_ticks, r["recorded_implied_edge_ticks"]), sid
    for sid, r in {**members, **coverage}.items():
        ev = eda_run.directional[sid]
        assert len(ev.values) == r["n_events"], sid
        assert np.allclose(ev.daily_sums(eda_run.dates), r["daily_sum_ticks"], rtol=0,
                           atol=TOL), sid
        counts = pd.Series(ev.trade_dates, dtype=object).value_counts()
        assert [int(counts.get(d, 0)) for d in eda_run.dates] == r["daily_count"], sid


@needs_research
def test_every_per_event_value_of_the_hashed_event_series(eda_run, hashed_eda) -> None:
    from strategy.research._d1e_event_series import _event_values

    _, _, stats = hashed_eda
    directional = [s for s in stats if s.directional]
    assert len(directional) == 64
    for s in directional:
        values = np.concatenate([np.asarray(_event_values(d, s.keys), dtype=float)
                                 for d in s.days])
        dates = [d.obs_date for d in s.days for _ in _event_values(d, s.keys)]
        ev = eda_run.directional[s.id]
        assert np.array_equal(ev.values, values), s.id
        assert list(ev.trade_dates) == dates, s.id


@needs_research
def test_eda_intervals_follow_the_declared_windows(eda_run) -> None:
    for ev in eda_run.directional.values():
        assert len(ev.start_bar_ts_ns) == len(ev.end_bar_ts_ns) == len(ev.values)
        _check_clocks(ev)
    crossing = {sid: int(ev.crosses_trade_date.sum())
                for sid, ev in eda_run.directional.items() if ev.crosses_trade_date.any()}
    assert set(crossing) <= {"F4_4_round_number_multiples_of_50",
                             "F4_4_round_number_multiples_of_100"}


# ==================================================================== synthetic bars ====
SYN_DAYS = tuple(d for d in (date(2030, 1, 7) + timedelta(days=i) for i in range(40))
                 if d.weekday() < 5)[:26]
SYN_DEGRADED = date(2030, 1, 10)
SYN_SPLICE = date(2030, 1, 22)  # blackout: 2030-01-18, -21, -22


def _synthetic_bars(seed: int = 7) -> pd.DataFrame:
    """17:00 CT (prior day) .. 15:59 CT per trade date, a +-2-tick random walk around 5000,
    four missing minutes a day, the first bar of each day with gap_before_minutes = 0 (as in
    the real parquet), one vendor-degraded bar on SYN_DEGRADED."""
    rng = np.random.default_rng(seed)
    price, frames = 4990.0, []
    for d in SYN_DAYS:
        start = datetime.combine(d - timedelta(days=1), time(17, 0), tzinfo=CT)
        start_ns = int(start.astimezone(UTC).timestamp()) * 1_000_000_000
        keep = np.setdiff1d(np.arange(1380), rng.choice(np.arange(1, 1380), 4, replace=False))
        steps = rng.integers(-2, 3, size=len(keep)) * TICK
        close = price + np.cumsum(steps)
        open_ = close - steps
        price = float(close[-1])
        frames.append(pd.DataFrame({
            "ts_event": start_ns + keep.astype(np.int64) * NS_PER_MINUTE,
            "open": open_, "close": close,
            "high": np.maximum(open_, close) + rng.integers(0, 3, len(keep)) * TICK,
            "low": np.minimum(open_, close) - rng.integers(0, 3, len(keep)) * TICK,
            "volume": rng.integers(50, 500, len(keep)), "instrument_id": 1,
            "raw_symbol": "MESH0", "trade_date": d.isoformat(), "in_flatten_window": False,
            "in_no_new_positions_window": False, "early_halt_ct": "",
            "in_scheduled_closure": False, "is_roll_session": False,
            "gap_before_minutes": np.concatenate([[0], np.diff(keep) - 1]),
            "vendor_degraded_day": False}))
    bars = pd.concat(frames, ignore_index=True)
    first = bars.index[bars["trade_date"] == SYN_DEGRADED.isoformat()][100]
    bars.loc[first, "vendor_degraded_day"] = True
    return bars


@pytest.fixture(scope="module")
def synthetic():
    bars = _synthetic_bars()
    return bars, compute_statistics(bars, SYN_DAYS, (SYN_SPLICE,))


def test_synthetic_exclusions_follow_the_eda_rule(synthetic) -> None:
    _, run = synthetic
    assert [dict(e) for e in run.excluded] == [
        {"date": "2030-01-10", "reason": "vendor_degraded_day"},
        {"date": "2030-01-18", "reason": "roll_blackout"},
        {"date": "2030-01-21", "reason": "roll_blackout"},
        {"date": "2030-01-22", "reason": "roll_blackout"}]
    assert len(run.dates) == 22 and SYN_DEGRADED not in run.dates


def test_synthetic_intervals_reproduce_each_event_value(synthetic) -> None:
    """Independent of the module's own checks: each event's move between its two interval
    prices, read straight off the synthetic frame, is |e| (F4.4: e is measured from a level L
    on the 50-point grid that the start bar's range touches)."""
    bars, run = synthetic
    by_ts = bars.set_index("ts_event")
    with_events = 0
    for sid, ev in run.directional.items():
        _check_clocks(ev)
        if not len(ev.values):
            continue
        with_events += 1
        start = by_ts.loc[ev.start_bar_ts_ns]
        end = by_ts.loc[ev.end_bar_ts_ns]
        assert list(pd.to_datetime(start["trade_date"]).dt.date) == list(ev.trade_dates), sid
        p_end = end["close"].to_numpy()
        if ev.family == "F4.4":
            step = 100.0 if sid.endswith("_100") else 50.0
            ok = np.zeros(len(ev.values), dtype=bool)
            for sign in (1, -1):  # L = p_end -+ e ticks, for the crossing direction
                level = p_end - sign * ev.values * TICK
                ok |= ((level % step == 0) & (start["low"].to_numpy() <= level)
                       & (level <= start["high"].to_numpy()))
            assert ok.all(), sid
            continue
        p_start = np.where(np.array(ev.start_price) == OPEN, start["open"], start["close"])
        move = (p_end - p_start) / TICK
        assert np.all((np.abs(np.abs(ev.values) - np.abs(move)) <= TOL) | (ev.values == 0)), sid
    assert with_events >= 56, with_events


def test_synthetic_thresholds_are_recomputed_on_the_supplied_dates(synthetic) -> None:
    _, run = synthetic
    eda_edges = (0.0016834655360190133, 0.002683843096824878)  # the EDA F2.4 edges
    assert run.thresholds["F2_4_trailvol_tercile_edges"] != eda_edges
    assert all(np.all(np.isfinite(v)) for k, v in run.thresholds.items() if k.startswith("F"))


def test_drift_helper_is_the_window_mean_move_over_each_interval(synthetic) -> None:
    bars, run = synthetic
    days = pd.to_datetime(bars["trade_date"]).dt.date
    path_bars = bars[days.isin(run.dates)]
    path = build_drift_path(path_bars, frozenset())
    ev = run.directional["F3_2_bucket07_bucket08"]
    assert len(ev.values) > 10
    got = forward_mean_moves_ticks(ev, path)
    frame = path_bars.assign(minute=((_ct_minute(path_bars["ts_event"].to_numpy()) - 1020)
                                     % 1440), day=pd.to_datetime(path_bars["trade_date"]))
    close = frame.pivot(index="day", columns="minute", values="close")
    for i in range(len(ev.values)):
        a = int(_ct_minute(ev.start_bar_ts_ns[i:i + 1])[0] - 1020) % 1440
        b = int(_ct_minute(ev.end_bar_ts_ns[i:i + 1])[0] - 1020) % 1440
        both = close[[a, b]].dropna()
        assert abs(got[i] - float(((both[b] - both[a]) / TICK).mean())) <= TOL


def test_drift_helper_refuses_an_interval_across_trade_dates(synthetic) -> None:
    bars, run = synthetic
    path = build_drift_path(bars[pd.to_datetime(bars["trade_date"]).dt.date.isin(run.dates)],
                            frozenset())
    ev = run.directional["F3_2_bucket07_bucket08"]
    other_day = bars.loc[bars["trade_date"] == run.dates[0].isoformat(), "ts_event"].iloc[5]
    moved = StatisticEvents(**{**ev.__dict__, "end_bar_ts_ns": np.array(
        [*ev.end_bar_ts_ns[:-1], other_day], dtype=np.int64)})
    with pytest.raises(ValueError, match="crosses a trade date"):
        forward_mean_moves_ticks(moved, path)


def test_alignment_refuses_a_replica_that_disagrees_with_the_hashed_values() -> None:
    d = date(2030, 1, 7)
    stat = fsf.TestedStat(id="t", family="G", description="", directional=True, null=0.0,
                      days=[fsf.DayObs(d, {"x": np.array([1.0])})], keys=("x",),
                      estimate_fn=lambda p: 0.0, n_fn=lambda p: 1, edge_equals_estimate=True)
    ok = stats_mod._Event((1.0,), (1, CLOSE), (2, CLOSE))
    assert stats_mod._align(stat, {d: [ok]}) == [(d, ok)]
    with pytest.raises(AssertionError, match="disagrees"):
        stats_mod._align(stat, {d: [stats_mod._Event((2.0,), (1, CLOSE), (2, CLOSE))]})
    with pytest.raises(AssertionError, match="lacks"):
        stats_mod._align(stat, {d: [ok], date(2030, 1, 8): [ok]})


def test_candidate_dates_without_bars_are_refused() -> None:
    bars = _synthetic_bars()
    with pytest.raises(ValueError, match="no bars"):
        compute_statistics(bars, (*SYN_DAYS, date(2030, 3, 1)), ())
