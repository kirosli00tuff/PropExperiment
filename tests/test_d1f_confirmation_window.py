"""Stage D.1f Task 1: the confirmation window in the screening path.

reports/stage_d1f_confirmation_list.md 1.3, 1.4, 5.1, 5.2(iv) and 5.8. What these pin:

1. REFUSALS, both directions. The confirmation loader re-checks every row it returns and
   refuses holdout-1, holdout-2, embargo-2 and mined (research-slice, research-embargo)
   dates, and asserts max(trade_date) <= 2024-02-29 on its own. The research loader now
   also refuses holdout-2, embargo-2 and confirmation dates. A train ScreeningWindow refuses
   confirmation dates; a ConfirmationWindow refuses train-union, mined and sealed dates; the
   null generator refuses a frame that mixes research and confirmation dates (R-3).
2. END TO END on a synthetic confirmation parquet (tmp_path only; 20 trade dates in March
   2021 with a roll on 2021-03-11, written the way data/build_mes_bars.py writes the
   research parquet): the splice dates come from that parquet's metadata, the roll
   blackout, the drift path and the session benchmark are recomputed on its bars, and the
   research slice is never read.
3. CONTINUITY: an existing Stage D.1d trial screened on the train union reproduces
   reports/stage_d1d_accounting.json to the cent (the ScreeningWindow path is unchanged).

No real confirmation parquet exists and none is created outside tmp_path. The only real
bars read are the research slice's, for the continuity trial and the train-window refusal.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

import data.research_bars as rb
import screening.runner as runner
from data.adapter import RollBoundary
from data.research_bars import (
    CONFIRMATION_EARLIEST_TRADE_DATE,
    CONFIRMATION_LAST_TRADE_DATE,
    DATE_CLASSES,
    RESEARCH_SERIES_PATH,
    HoldoutLeakError,
    assert_confirmation_rows,
    assert_research_slice_rows,
    load_confirmation_bars,
    load_research_bars,
    trade_date_class,
)
from data.session import trade_date as session_trade_date
from funnel.null_generator import build_segment_table
from screening.runner import (
    ConfirmationWindow,
    ScreeningWindow,
    confirmation_window,
    fold_train_window,
    screen_candidate,
    train_union_window,
)
from sim.costs import load_slippage_table
from sim.engine import BAR_COLUMNS
from sim.fill_model import side_cost_at_ct_minute
from strategy.interface import AccountView, Bar, market_intent
from tests.test_null_generator import make_day

CT = ZoneInfo("America/Chicago")
HAS_RESEARCH = RESEARCH_SERIES_PATH.is_file()
needs_research = pytest.mark.skipif(not HAS_RESEARCH, reason="research parquet not present")

# ------------------------------------------------------------ synthetic confirmation data ----
SYN_DAYS = tuple(d for d in (date(2021, 3, 1) + timedelta(days=i) for i in range(26))
                 if d.weekday() < 5)  # 2021-03-01 .. 2021-03-26: 20 trade dates, no holiday
SPLICE_UTC = datetime(2021, 3, 11, tzinfo=UTC)  # midnight UTC = 18:00 CT inside trade date 03-11
SPLICE_DAY = date(2021, 3, 11)
BLACKOUT = frozenset({date(2021, 3, 9), date(2021, 3, 10), SPLICE_DAY})  # splice + 2 before
OLD_ID, NEW_ID = 42_001, 42_002
# RTH move per trade date, in ticks: the whole move happens inside the 09:00 CT bar. The three
# blackout dates carry huge moves, so any leak of them into the benchmark or the path shows.
SYN_MOVES = (40, -12, 24, 8, -30, 16, 200, -160, 300, -20,
             36, 4, -8, 28, 12, -44, 52, 20, -16, 32)
BASE_TICKS = 15_600  # 3900.00
SESSION_MINUTES = 23 * 60  # 17:00 CT reopen .. 15:59 CT, the 16:00-17:00 halt excluded


def _synthetic_bars() -> pd.DataFrame:
    """Full ETH + RTH sessions with every BAR_COLUMNS flag, instrument change at the splice."""
    rows = []
    for i, (day, move) in enumerate(zip(SYN_DAYS, SYN_MOVES, strict=True)):
        base = BASE_TICKS + 4 * i
        start = datetime.combine(day - timedelta(days=1), time(17, 0), tzinfo=CT).astimezone(UTC)
        for k in range(SESSION_MINUTES):
            ts = start + timedelta(minutes=k)
            local = ts.astimezone(CT)
            hm = local.hour * 60 + local.minute
            old = day < SPLICE_DAY or (day == SPLICE_DAY and ts < SPLICE_UTC)
            level = base + (80 if day == SPLICE_DAY and old else 0)
            if hm >= 17 * 60 or hm < 9 * 60:
                o = c = level
            elif hm == 9 * 60:
                o, c = level, level + move
            else:
                o = c = level + move
            ts_ns = int(ts.timestamp()) * 10**9
            rows.append({
                "ts_event": ts_ns, "open": o * 0.25, "high": max(o, c) * 0.25,
                "low": min(o, c) * 0.25, "close": c * 0.25, "volume": 100,
                "instrument_id": OLD_ID if old else NEW_ID,
                "raw_symbol": "MESH1" if old else "MESM1",
                "trade_date": session_trade_date(ts_ns),
                "in_flatten_window": 15 * 60 + 10 <= hm < 17 * 60,
                "in_no_new_positions_window": 15 * 60 + 8 <= hm < 17 * 60,
                "early_halt_ct": "", "in_scheduled_closure": False,
                "is_roll_session": day == SPLICE_DAY, "gap_before_minutes": 0,
                "vendor_degraded_day": False,
            })
            assert rows[-1]["trade_date"] == day  # the builder's own trade-date rule agrees
    return pd.DataFrame(rows)[list(BAR_COLUMNS)]


def _write_like_the_builder(frame: pd.DataFrame, path: Path, rolls: list[RollBoundary]) -> Path:
    """data/build_mes_bars.py's write: ISO-string trade_date, rolls in the schema metadata."""
    table = pa.Table.from_pandas(frame.assign(trade_date=frame["trade_date"].astype(str)),
                                 preserve_index=False)
    meta = {"source": "synthetic, tests/test_d1f_confirmation_window.py",
            "rolls": [asdict(r) for r in rolls], "degraded_vendor_days": []}
    blob = json.dumps(meta, default=str).encode()
    schema_meta = {**(table.schema.metadata or {}), b"propexperiment": blob}
    table = table.replace_schema_metadata(schema_meta)
    pq.write_table(table, path)
    return path


SYN_ROLL = RollBoundary(symbol="MES.v.0", date="2021-03-11",
                        ts_ns=int(SPLICE_UTC.timestamp()) * 10**9, from_instrument=str(OLD_ID),
                        to_instrument=str(NEW_ID), from_raw_symbol="MESH1",
                        to_raw_symbol="MESM1")


@pytest.fixture(scope="module")
def confirmation_parquet(tmp_path_factory: pytest.TempPathFactory) -> Path:
    path = tmp_path_factory.mktemp("confirmation") / "synthetic_confirmation.parquet"
    return _write_like_the_builder(_synthetic_bars(), path, [SYN_ROLL])


@dataclass(frozen=True)
class RthLong:
    """Trivial and unconditional: long 1 micro at the 08:30 CT decision, out at 15:00 CT."""

    name: str = "synthetic_rth_long"

    def on_bar(self, bar: Bar, account: AccountView) -> tuple:
        local = bar.open_ts_utc.astimezone(CT)
        hm = (local.hour, local.minute)
        if hm == (8, 30) and account.position_micros == 0:
            return (market_intent(bar, "buy", 1),)
        if hm == (15, 0) and account.position_micros:
            return (market_intent(bar, "sell", account.position_micros),)
        return ()


def _no_research(*_args, **_kwargs):
    raise AssertionError("the confirmation path touched the research slice")


@pytest.fixture(scope="module")
def confirmation_run(confirmation_parquet: Path) -> tuple:
    """One screen through screen_candidate with every research entry point booby-trapped and
    the splice reader spied on."""
    calls: list[Path] = []
    real_splices = runner.splice_trade_dates_from_parquet

    def spy(path: Path) -> tuple[date, ...]:
        calls.append(Path(path))
        return real_splices(path)

    with pytest.MonkeyPatch.context() as mp:
        for name in ("_research_frame", "_folds", "train_union_window", "load_research_bars"):
            mp.setattr(runner, name, _no_research)
        mp.setattr(rb, "load_research_bars", _no_research)
        mp.setattr(runner, "splice_trade_dates_from_parquet", spy)
        window = confirmation_window(SYN_DAYS[0], path=confirmation_parquet)
        report = screen_candidate("synthetic rth long", RthLong, window)
    return window, report, tuple(calls)


# ======================================================================= date classes ====
def test_date_classes_partition_every_date_from_mes_first_month_on() -> None:
    assert DATE_CLASSES[0][1] == CONFIRMATION_EARLIEST_TRADE_DATE
    assert DATE_CLASSES[-1][2] == date.max
    for (_, _, last), (_, first, _) in zip(DATE_CLASSES, DATE_CLASSES[1:], strict=False):
        assert first == last + timedelta(days=1)  # no gap, no overlap


@pytest.mark.parametrize(("day", "expected"), [
    (date(2019, 4, 30), rb.BEFORE_MES), (date(2019, 5, 1), rb.CONFIRMATION),
    (date(2024, 2, 29), rb.CONFIRMATION), (date(2024, 3, 1), rb.EMBARGO2),
    (date(2024, 3, 29), rb.EMBARGO2), (date(2024, 4, 1), rb.HOLDOUT2),
    (date(2025, 3, 31), rb.HOLDOUT2), (date(2025, 4, 1), rb.RESEARCH),
    (date(2026, 5, 13), rb.RESEARCH), (date(2026, 6, 12), rb.RESEARCH),
    (date(2026, 6, 15), rb.RESEARCH_EMBARGO), (date(2026, 6, 19), rb.RESEARCH_EMBARGO),
    (date(2026, 6, 22), rb.HOLDOUT1), (date(2026, 9, 16), rb.HOLDOUT1),
])
def test_boundary_dates_fall_in_the_declared_class(day: date, expected: str) -> None:
    assert trade_date_class(day) == expected


# ================================================================ confirmation loader ====
BAD_FOR_CONFIRMATION = [  # (date, words the refusal must name): list 1.2, 1.4 and 5.2(iv)
    (date(2024, 3, 1), "embargo-2"), (date(2024, 3, 29), "embargo-2"),
    (date(2024, 4, 1), "holdout-2"), (date(2024, 12, 31), "holdout-2"),
    (date(2025, 3, 31), "holdout-2"), (date(2025, 4, 1), "mined"),
    (date(2026, 5, 13), "mined"), (date(2026, 6, 12), "mined"),
    (date(2026, 6, 16), "research-embargo"), (date(2026, 6, 22), "holdout-1"),
    (date(2026, 9, 16), "holdout-1"),
]
GOOD_CONFIRMATION = [date(2019, 5, 1), date(2021, 3, 2), date(2024, 2, 29)]


def _date_rows_parquet(path: Path, days: list[date]) -> Path:
    """One row per date, in time order: just enough for the loaders' filter and re-check."""
    days = sorted(days)
    frame = pd.DataFrame({"ts_event": [int(datetime.combine(d, time(14), tzinfo=UTC)
                                           .timestamp()) * 10**9 for d in days],
                          "trade_date": [d.isoformat() for d in days]})
    pq.write_table(pa.Table.from_pandas(frame, preserve_index=False), path)
    return path


def _read_everything(path: Path, columns, first: date, last: date) -> pd.DataFrame:  # noqa: ANN001
    """A broken pushdown filter: returns every row, so only the re-check stands in the way."""
    return pq.read_table(path).to_pandas()


def test_confirmation_loader_returns_only_confirmation_dates(tmp_path: Path) -> None:
    path = _date_rows_parquet(tmp_path / "all.parquet",
                              GOOD_CONFIRMATION + [d for d, _ in BAD_FOR_CONFIRMATION])
    frame = load_confirmation_bars(["ts_event"], path=path)
    got = sorted(date.fromisoformat(d) for d in frame["trade_date"])
    assert got == GOOD_CONFIRMATION
    assert max(got) <= CONFIRMATION_LAST_TRADE_DATE == date(2024, 2, 29)


@pytest.mark.parametrize(("bad", "words"), BAD_FOR_CONFIRMATION)
def test_confirmation_loader_rechecks_rows_the_filter_let_through(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch, bad: date, words: str) -> None:
    monkeypatch.setattr(rb, "_read_trade_date_range", _read_everything)
    path = _date_rows_parquet(tmp_path / "leaky.parquet", [*GOOD_CONFIRMATION, bad])
    with pytest.raises(HoldoutLeakError, match=words):
        load_confirmation_bars(["ts_event"], path=path)


def test_max_trade_date_assertion_stands_on_its_own(monkeypatch: pytest.MonkeyPatch) -> None:
    # Even with a mis-declared class table that calls March 2024 "confirmation", the explicit
    # max(trade_date) <= 2024-02-29 assertion of list 5.2(iv) still refuses it.
    widened = ((rb.CONFIRMATION, CONFIRMATION_EARLIEST_TRADE_DATE, date(2024, 3, 31)),
               *DATE_CLASSES[1:])
    monkeypatch.setattr(rb, "DATE_CLASSES", widened)
    frame = pd.DataFrame({"trade_date": ["2024-02-29", "2024-03-01"]})
    with pytest.raises(HoldoutLeakError, match=r"max trade date 2024-03-01 > 2024-02-29"):
        assert_confirmation_rows(frame)


def test_confirmation_recheck_needs_a_trade_date_column() -> None:
    with pytest.raises(HoldoutLeakError, match="trade_date column"):
        assert_confirmation_rows(pd.DataFrame({"ts_event": [1]}))


# =================================================================== research loader ====
@pytest.mark.parametrize(("bad", "words"), [
    (date(2021, 3, 2), "confirmation-window"), (date(2019, 5, 1), "confirmation-window"),
    (date(2024, 3, 1), "embargo-2"), (date(2024, 6, 3), "holdout-2"),
    (date(2025, 3, 31), "holdout-2"), (date(2026, 6, 22), "holdout trade date"),
])
def test_research_recheck_refuses_confirmation_and_sealed_dates(bad: date, words: str) -> None:
    frame = pd.DataFrame({"trade_date": ["2026-01-06", bad.isoformat()]})
    with pytest.raises(HoldoutLeakError, match=words):
        assert_research_slice_rows(frame)


def test_research_recheck_allows_the_embargo_only_when_asked() -> None:
    frame = pd.DataFrame({"trade_date": ["2026-06-12", "2026-06-16"]})
    with pytest.raises(HoldoutLeakError, match="research-embargo"):
        assert_research_slice_rows(frame)
    assert_research_slice_rows(frame, include_embargo=True)


@pytest.mark.parametrize("bad", [date(2021, 3, 2), date(2024, 3, 1), date(2024, 6, 3)])
def test_research_loader_rechecks_rows_the_filter_let_through(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch, bad: date) -> None:
    path = _date_rows_parquet(tmp_path / "research.parquet", [bad, date(2026, 1, 6)])
    monkeypatch.setattr(rb, "RESEARCH_SERIES_PATH", path)
    assert load_research_bars(["ts_event"])["trade_date"].tolist() == ["2026-01-06"]  # filter
    monkeypatch.setattr(rb, "_read_trade_date_range", _read_everything)
    with pytest.raises(HoldoutLeakError):
        load_research_bars(["ts_event"])  # the re-check, with the filter broken


# ====================================================================== the windows ====
@needs_research
@pytest.mark.parametrize("bad", [date(2021, 3, 2), date(2024, 2, 29), date(2024, 6, 3)])
def test_train_window_refuses_confirmation_and_holdout2_dates(bad: date) -> None:
    leaky = ScreeningWindow("leaky", (*fold_train_window(0).trade_dates, bad))
    with pytest.raises(ValueError, match="train dates only"):
        screen_candidate("x", RthLong, leaky)


@pytest.mark.parametrize(("bad", "words"), [
    (date(2025, 4, 1), "mined"),  # first train-union date
    (date(2026, 5, 13), "mined"),  # last train-union date
    (date(2026, 6, 12), "mined"),  # a test-fold date
    (date(2026, 6, 16), "research-embargo"), (date(2026, 6, 22), "holdout-1"),
    (date(2024, 6, 3), "holdout-2"), (date(2024, 3, 4), "embargo-2"),
])
def test_confirmation_window_refuses_mined_and_sealed_dates(bad: date, words: str) -> None:
    with pytest.raises(HoldoutLeakError, match=words):
        ConfirmationWindow("leaky", (date(2021, 3, 2), bad))


def test_screen_candidate_rechecks_a_forced_confirmation_window(
        confirmation_parquet: Path) -> None:
    window = ConfirmationWindow("forced", (SYN_DAYS[0],), confirmation_parquet)
    object.__setattr__(window, "trade_dates", (SYN_DAYS[0], date(2025, 4, 1)))
    with pytest.raises(HoldoutLeakError, match="mined"):
        screen_candidate("x", RthLong, window)
    object.__setattr__(window, "trade_dates", ())
    with pytest.raises(ValueError, match="empty"):
        screen_candidate("x", RthLong, window)


def test_confirmation_window_dates_must_have_bars(confirmation_parquet: Path) -> None:
    window = ConfirmationWindow("gap", (date(2021, 4, 1),), confirmation_parquet)
    with pytest.raises(ValueError, match="no bars"):
        screen_candidate("x", RthLong, window)


def test_confirmation_window_runs_from_s_through_2024_02_29(confirmation_parquet: Path) -> None:
    window = confirmation_window(date(2021, 3, 3), path=confirmation_parquet)
    assert window.trade_dates == SYN_DAYS[2:]
    assert window.name == "confirmation_2021-03-03_2024-02-29"
    assert window.path == confirmation_parquet
    for start in (date(2019, 4, 30), date(2024, 3, 1), date(2025, 4, 1)):
        with pytest.raises(ValueError, match="outside the confirmation window"):
            confirmation_window(start, path=confirmation_parquet)


# ===================================================================== null generator ====
def test_null_generator_accepts_an_all_confirmation_frame() -> None:
    frame = pd.concat([make_day("2021-03-02", n_rth=8), make_day("2021-03-03", n_rth=8)])
    assert build_segment_table(frame, 2).trade_dates == ("2021-03-02", "2021-03-03")


def test_null_generator_refuses_a_mixed_frame() -> None:
    frame = pd.concat([make_day("2021-03-02", n_rth=8), make_day("2026-01-06", n_rth=8)])
    with pytest.raises(ValueError, match="mixed research and confirmation"):
        build_segment_table(frame, 1)


@pytest.mark.parametrize(("day", "words"), [
    ("2024-03-04", "embargo-2"), ("2024-06-03", "holdout-2"), ("2026-06-22", "holdout"),
    ("2026-06-16", "embargo"), ("2019-04-30", "out-of-range"),
])
def test_null_generator_refuses_sealed_embargo_and_pre_mes_dates(day: str, words: str) -> None:
    with pytest.raises(ValueError, match=words):
        build_segment_table(make_day(day, n_rth=1), 1)


# ========================================================== end to end, synthetic bars ====
def test_splices_come_from_the_confirmation_parquet(confirmation_run: tuple,
                                                    confirmation_parquet: Path) -> None:
    window, report, calls = confirmation_run
    assert calls == (confirmation_parquet,)
    assert (report.n_dates, report.first_date, report.last_date) == (20, SYN_DAYS[0],
                                                                    SYN_DAYS[-1])
    assert report.window == window.name
    assert report.blackout_dates_in_window == len(BLACKOUT) == 3


def test_roll_blackout_is_recomputed_on_the_confirmation_roll(confirmation_run: tuple) -> None:
    _, report, _ = confirmation_run
    traded = {d for d, n in zip(SYN_DAYS, report.daily_n_trips, strict=True) if n}
    assert traded == set(SYN_DAYS) - BLACKOUT  # no exposure on the splice or the 2 before
    assert report.n_trips == 17


def _tradable_moves() -> np.ndarray:
    return np.array([m for d, m in zip(SYN_DAYS, SYN_MOVES, strict=True) if d not in BLACKOUT])


def test_session_benchmark_is_the_hand_computation_on_the_synthetic_bars(
        confirmation_run: tuple) -> None:
    _, report, _ = confirmation_run
    moves = _tradable_moves()
    table = load_slippage_table()
    # One RTH session per tradable day: in at the 08:30 CT open, out at the 15:09 close
    # (exit minute 15:10), the whole day's move in between; one market side at each end.
    side_costs = (side_cost_at_ct_minute(table, 8 * 60 + 30, 1).total_cents
                  + side_cost_at_ct_minute(table, 15 * 60 + 10, 1).total_cents)
    bench = report.session_benchmark
    assert bench.n_sessions == 17
    assert bench.drift_ticks_per_session == pytest.approx(moves.mean(), abs=1e-12)
    assert bench.long_net_usd == pytest.approx((125 * moves.sum() - 17 * side_costs) / 100,
                                               abs=1e-9)
    assert bench.short_net_usd == pytest.approx((-125 * moves.sum() - 17 * side_costs) / 100,
                                                abs=1e-9)


def test_drift_path_is_recomputed_on_the_synthetic_bars(confirmation_run: tuple) -> None:
    # The unconditional long IS its own counterpart: in at the 08:31 open, out at the 15:01
    # open, so each trip earns its day's move and the path charges the tradable days' mean
    # move. Both totals equal 1.25 x the sum of the 17 tradable moves; a path that averaged
    # in a blackout day (moves 200, -160, 300) or the research slice would not.
    _, report, _ = confirmation_run
    gross = 1.25 * _tradable_moves().sum()
    assert report.drift.candidate_gross_usd == pytest.approx(gross, abs=1e-9)
    assert report.drift.drift_gross_usd == pytest.approx(gross, abs=1e-9)
    assert report.drift.drift_share_of_gross == pytest.approx(1.0, abs=1e-12)
    assert report.drift.excess_gross_usd == pytest.approx(0.0, abs=1e-9)
    assert report.drift_verdict == "fail"  # drift is not edge, on this window as on any
    assert len(report.trip_pnls_usd) == len(report.trip_micros) == 17
    assert round(sum(report.trip_pnls_usd), 2) == report.net_pnl_usd
    assert round(sum(report.daily_net_usd), 2) == report.net_pnl_usd


def test_confirmation_frame_cache_holds_only_confirmation_bars(
        confirmation_parquet: Path) -> None:
    frame, days = runner._confirmation_frame(confirmation_parquet)
    assert {trade_date_class(d) for d in days} == {rb.CONFIRMATION}
    assert list(frame.columns) == list(BAR_COLUMNS)
    assert runner._confirmation_frame(confirmation_parquet)[0] is frame  # loaded once


# ======================================================== continuity on the train union ====
CONTINUITY_LABEL = "E-H3 quarterly witching short"  # 4 trips; about 8 s on the train union


@pytest.fixture(scope="module")
def continuity_report():
    from strategy.research._d1d_accounting import ALL_TRIALS

    factory = dict(ALL_TRIALS)[CONTINUITY_LABEL]
    return screen_candidate(CONTINUITY_LABEL, factory, train_union_window())


@needs_research
def test_existing_trial_reproduces_stage_d1d_accounting_to_the_cent(continuity_report) -> None:
    from strategy.research._d1b_accounting import _moments

    logged = json.loads(Path("reports/stage_d1d_accounting.json").read_text())
    row = next(r for r in logged["runs"] if r["label"] == CONTINUITY_LABEL)
    report = continuity_report
    assert report.window == "train_union" and report.n_dates == 289
    assert round(report.net_pnl_usd, 2) == round(row["net_pnl_usd"], 2) == -25.60
    assert report.n_trips == row["n_trips"] == 4
    assert report.trades_per_day == pytest.approx(row["trades_per_day"], abs=1e-12)
    assert report.zero_edge.win_probability == row["win_probability"]
    assert report.zero_edge.win_loss_ratio == row["win_loss_ratio"]
    assert (report.zero_edge.robust, report.drift_verdict, report.verdict) == (
        row["robust"], row["drift_verdict"], row["verdict"])
    sharpe = _moments(list(report.daily_net_usd))["sharpe"]
    assert abs(sharpe - logged["per_trial"][CONTINUITY_LABEL]["sharpe"]) <= 1e-6


@needs_research
def test_confirmation_benchmark_differs_from_the_research_slice_one(
        continuity_report, confirmation_run: tuple) -> None:
    _, report, _ = confirmation_run
    research = continuity_report.session_benchmark
    assert report.session_benchmark != research
    assert (report.session_benchmark.n_sessions, research.n_sessions) == (17, 276)
    assert report.session_benchmark.drift_ticks_per_session != pytest.approx(
        research.drift_ticks_per_session, abs=1e-6)
