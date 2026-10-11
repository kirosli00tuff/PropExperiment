"""h6_rod.signal and h6_rod.gex on synthetic bars and rows only (prereg sections 2 and 3)."""

from __future__ import annotations

import hashlib
from datetime import date, time, timedelta

import pandas as pd
import pytest

from h6_rod import clock, signal
from h6_rod import constants as K
from h6_rod.gex import GexInputError, load_gex
from tests._h6_rod_synth import day_frame, ts_ns

MON, TUE = date(2022, 3, 14), date(2022, 3, 15)
THANKSGIVING, BLACK_FRIDAY = date(2022, 11, 24), date(2022, 11, 25)
CYBER_MONDAY = date(2022, 11, 28)


def _bars(*day_rows: list[dict]) -> pd.DataFrame:
    rows = [r for rows in day_rows for r in rows]
    return pd.DataFrame(rows).sort_values("ts_event", kind="stable").reset_index(drop=True)


def _facts(bars: pd.DataFrame, days: list[date]) -> dict:
    return signal.compute_facts(bars[["ts_event", "close", "instrument_id"]], days)


# ------------------------------------------------------------------ r_ROD and the clock ----
def test_r_rod_on_a_normal_day_matches_the_hand_computation() -> None:
    bars = _bars(day_frame(MON, close_ticks={(14, 59): 60_000}),
                 day_frame(TUE, base_ticks=60_000, close_ticks={(14, 29): 60_120}))
    f = _facts(bars, [TUE])[TUE]
    # P(prior C) = Monday's 14:59 close = 15000.00; P(C-30) = Tuesday's 14:29 close = 15030.00
    assert (f.prior_close, f.signal_close) == (15000.00, 15030.00)
    assert f.r_rod == pytest.approx(15030.00 / 15000.00 - 1) == pytest.approx(0.002)
    assert f.eligible and f.side == "buy" and f.close_ct == time(15, 0) and not f.shortened
    assert f.prior_day == MON


def test_the_bars_read_are_1429_and_the_prior_1459_and_nothing_later() -> None:
    later = {(14, 30): 70_000, (14, 59): 61_000}  # bars after the signal bar must not matter
    bars = _bars(day_frame(MON, close_ticks={(14, 58): 59_000, (14, 59): 60_000, (15, 0): 1}),
                 day_frame(TUE, base_ticks=60_000, close_ticks={(14, 29): 59_960, **later}))
    f = _facts(bars, [TUE])[TUE]
    assert f.r_rod == pytest.approx(59_960 / 60_000 - 1) and f.side == "sell"
    assert clock.signal_bar_ns(TUE) == ts_ns(TUE, 14, 29)
    assert clock.prior_bar_ns(MON) == ts_ns(MON, 14, 59)
    assert clock.exit_from_ns(TUE) == ts_ns(TUE, 14, 58)


def test_a_shortened_day_uses_the_early_close_for_c_and_for_the_next_days_prior_bar() -> None:
    # 2022-11-24 halts 12:00 CT, 2022-11-25 halts 12:15 CT (the frozen equity calendar)
    assert clock.close_ct(THANKSGIVING) == time(12, 0)
    assert clock.close_ct(BLACK_FRIDAY) == time(12, 15)
    bars = _bars(day_frame(THANKSGIVING, start=(11, 0), end=(12, 0),
                           close_ticks={(11, 59): 60_000}),
                 day_frame(BLACK_FRIDAY, start=(11, 0), end=(12, 15), base_ticks=60_000,
                           close_ticks={(11, 44): 60_040, (12, 14): 60_100}),
                 day_frame(CYBER_MONDAY, base_ticks=60_100, close_ticks={(14, 29): 60_000}))
    facts = _facts(bars, [BLACK_FRIDAY, CYBER_MONDAY])
    fri, mon = facts[BLACK_FRIDAY], facts[CYBER_MONDAY]
    assert fri.shortened and fri.prior_day == THANKSGIVING
    assert (fri.prior_close, fri.signal_close) == (15000.00, 15010.00)  # 11:59 Thu, 11:44 Fri
    assert clock.signal_bar_ns(BLACK_FRIDAY) == ts_ns(BLACK_FRIDAY, 11, 44)  # early close - 31
    assert mon.prior_day == BLACK_FRIDAY and mon.prior_close == 15025.00  # Fri 12:14 = close - 1
    assert mon.side == "sell"


# ------------------------------------------------------------------ eligibility reasons ----
@pytest.mark.parametrize(("mon_kw", "tue_kw", "reason"), [
    ({"skip": [(14, 59)]}, {"close_ticks": {(14, 29): 60_004}}, K.REASON_MISSING_PRIOR_BAR),
    ({}, {"skip": [(14, 29)], "close_ticks": {(14, 29): 60_004}}, K.REASON_MISSING_SIGNAL_BAR),
    ({"skip": [(14, 59)]}, {"skip": [(14, 29)]}, K.REASON_MISSING_SIGNAL_BAR),  # listed order
    ({}, {"iid_at": {(14, 29): 999}, "close_ticks": {(14, 29): 60_004}},
     K.REASON_INSTRUMENT_CHANGE),
    ({}, {"close_ticks": {(14, 29): 60_000}}, K.REASON_ZERO_SIGNAL),
])
def test_each_no_trade_reason(mon_kw: dict, tue_kw: dict, reason: str) -> None:
    bars = _bars(day_frame(MON, **mon_kw), day_frame(TUE, **tue_kw))
    f = _facts(bars, [TUE])[TUE]
    assert f.reason == reason and not f.eligible and f.side is None
    sched = signal.t1_schedule({TUE: f}, TUE, TUE)
    assert sched.entries == {} and sched.excluded == {TUE: reason}


def test_a_date_with_no_bars_at_all_is_missing_signal_bar_and_counted() -> None:
    bars = _bars(day_frame(MON))
    facts = _facts(bars, [MON, TUE])
    counts = signal.eligibility_counts(facts, MON, TUE)
    assert counts["trade_dates"] == 2 and counts[K.REASON_MISSING_SIGNAL_BAR] == 1
    assert counts[K.REASON_MISSING_PRIOR_BAR] == 1  # Monday's prior (Friday) has no bars


# ------------------------------------------------------------------ T2 ----
def _f(day: date, r: float | None, reason: str | None = None, prior: date | None = None
       ) -> signal.DateFacts:
    return signal.DateFacts(day, time(15, 0), False, prior or day - timedelta(days=1),
                            None, None, None, None, r, reason)


def _series(n: int, start: date = date(2020, 1, 2)) -> list[date]:
    return list(clock.trade_dates(start, start + timedelta(days=200)))[:n]


def test_t2_has_no_threshold_with_59_eligible_dates_and_one_with_60() -> None:
    days = _series(62)
    facts = {d: _f(d, (i + 1) / 1000) for i, d in enumerate(days)}
    med = signal.t2_thresholds(facts, days, days[0])
    assert med[days[59]] is None  # 59 eligible dates before it
    assert med[days[60]] == pytest.approx(0.0305)  # median of 0.001..0.060
    sched = signal.t2_schedule(facts, days[59], days[61], days[0])
    assert sched.excluded[days[59]] == K.REASON_T2_WARMUP
    assert days[60] in sched.entries and days[61] in sched.entries


def test_t2_is_strict_and_counts_only_eligible_dates_in_the_allowed_range() -> None:
    days = _series(70)
    facts = {d: _f(d, 0.01) for d in days}
    facts[days[5]] = _f(days[5], None, K.REASON_MISSING_PRIOR_BAR)  # not eligible: not counted
    facts[days[69]] = _f(days[69], -0.01)  # |r| equal to the median: not a T2 date
    med = signal.t2_thresholds(facts, [days[60], days[61], days[69]], days[0])
    assert med[days[60]] is None  # only 59 eligible dates before it (days[5] is not eligible)
    assert med[days[61]] == pytest.approx(0.01)
    sched = signal.t2_schedule(facts, days[61], days[69], days[0])
    assert sched.excluded[days[69]] == K.REASON_T2_NOT_ABOVE
    assert sched.excluded[days[61]] == K.REASON_T2_NOT_ABOVE  # 0.01 > 0.01 is false
    # a later lookback start leaves fewer than 60 dates: warm-up again
    assert signal.t2_thresholds(facts, [days[69]], days[15])[days[69]] is None


def test_t2_warmup_first_is_the_60th_equity_trade_date_before_june_2020() -> None:
    w0 = clock.t2_warmup_first()
    span = clock.trade_dates(w0, date(2020, 5, 29))
    assert len(span) == 60 and span[-1] == date(2020, 5, 29)
    assert date(2020, 5, 25) in span  # Memorial Day 2020 halts early: a trade date


# ------------------------------------------------------------------ T3 ----
def test_t3_mask_needs_a_strictly_negative_gex_on_the_previous_trade_date() -> None:
    d1, d2, d3, d4 = date(2022, 3, 15), date(2022, 3, 16), date(2022, 3, 17), date(2022, 3, 18)
    facts = {d1: _f(d1, 0.01, prior=date(2022, 3, 14)), d2: _f(d2, -0.02, prior=d1),
             d3: _f(d3, 0.01, prior=d2), d4: _f(d4, None, K.REASON_ZERO_SIGNAL, prior=d3)}
    gex = {date(2022, 3, 14): -1.5e9, d1: 0.0, d3: -2.0}  # no row for d2
    sched = signal.t3_schedule(facts, d1, d4, gex)
    assert list(sched.entries) == [d1] and sched.entries[d1].side == "buy"
    assert sched.excluded == {d2: K.REASON_GEX_NOT_NEGATIVE, d3: K.REASON_GEX_MISSING,
                              d4: K.REASON_ZERO_SIGNAL}


def _csv(tmp_path, body: str) -> tuple[object, str]:
    path = tmp_path / "gex.csv"
    path.write_text(body, encoding="utf-8")
    return path, hashlib.sha256(path.read_bytes()).hexdigest()


def test_gex_rows_on_or_after_march_2024_are_cut_before_any_field_is_parsed(tmp_path) -> None:
    body = ("date,price,dix,gex\n2024-02-28,5000,0.4,-1.0e9\n2024-02-29,5010,0.41,2.5e9\n"
            "2024-03-01,not,a,number\n2026-10-02,x,y,z,extra\n")
    path, sha = _csv(tmp_path, body)
    rows, rec = load_gex(path, expected_sha256=sha)
    assert rows == {date(2024, 2, 28): -1.0e9, date(2024, 2, 29): 2.5e9}
    assert rec["rows_cut_on_or_after_2024_03_01"] == 2 and rec["rows_kept"] == 2


@pytest.mark.parametrize("body", [
    "date,price,gex,dix\n2020-01-02,1,2,3\n",  # header
    "date,price,dix,gex\n2020-01-02,1,2,nan\n",  # non-finite
    "date,price,dix,gex\n2020-01-02,1,2,x\n",  # not a number
    "date,price,dix,gex\n2020-01-02,1,2,3\n2020-01-02,1,2,4\n",  # duplicate date
    "date,price,dix,gex\n01/02/2020,1,2,3\n",  # not ISO
])
def test_a_malformed_gex_csv_is_refused(tmp_path, body: str) -> None:
    path, sha = _csv(tmp_path, body)
    with pytest.raises(GexInputError):
        load_gex(path, expected_sha256=sha)


def test_a_gex_csv_with_another_sha256_or_no_pin_is_refused(tmp_path) -> None:
    path, _ = _csv(tmp_path, "date,price,dix,gex\n2020-01-02,1,2,3\n")
    with pytest.raises(GexInputError, match="sha256"):
        load_gex(path, expected_sha256="0" * 64)
    with pytest.raises(GexInputError, match="None"):
        load_gex(path, expected_sha256=None)
