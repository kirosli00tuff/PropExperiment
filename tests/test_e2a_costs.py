"""Stage E.2a Task 8: the per-product D8 cost model (known answers on synthetic books)."""

from __future__ import annotations

import json
from datetime import UTC, date, datetime, time
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest

from data.calendars import Segment, SessionSpec
from data.group_session import GroupCalendar
from data.session import ct_ns
from sim import calibrate_costs as cc
from sim import cost_inputs, cost_report, cost_rule, product_costs
from sim.cost_inputs import SAMPLE_DATES, TickSpec

DAY = date(2025, 5, 14)  # CDT
TICK = 250_000_000  # 0.25 in 1e-9 units
NULL = cc.NULL_PRICE
S = 1_000_000_000


def _px(x: float) -> int:
    return int(round(x * 1e9))


def _cal(segments: tuple[tuple[time, time], ...] = ((time(8, 0), time(9, 0)),
                                                    (time(9, 30), time(10, 10)))
         ) -> GroupCalendar:
    spec = SessionSpec(valid_from=date(2025, 1, 1), valid_to=None,
                       segments=tuple(Segment(0, a, 0, b) for a, b in segments),
                       day_session_ct={"*": (time(8, 0), time(10, 10))}, source="test")
    return GroupCalendar(group="test", holidays={}, sessions=(spec,),
                         coverage=(date(2025, 1, 1), date(2026, 12, 31)),
                         assert_coverage=lambda days: None, module_paths=())


# (CT time, bid, ask, bid size, ask size); the hand calculation is in each test's comments.
RECORDS = [
    (time(7, 59), 100.00, 100.50, 5, 7),   # r0 closed; carried into 08:00:01 (2 ticks)
    (time(8, 10), 100.00, 100.25, 3, 4),   # r1 1 tick
    (time(8, 20), 100.50, 100.25, 1, 1),   # r2 crossed: dropped
    (time(8, 25), 100.00, 100.75, 10, 2),  # r3 3 ticks
    (time(8, 40), 100.25, 100.25, 1, 1),   # r4 locked: dropped
    (time(8, 50), 100.00, 100.25, 1, 1),   # r5 1 tick
    (time(9, 10), 100.00, 101.00, 9, 9),   # r6 in the closure; carried into 09:30:01 (4 ticks)
    (time(9, 45), 100.00, None, 3, 0),     # r7 empty ask: dropped
    (time(9, 50), 100.00, 100.50, 2, 6),   # r8 2 ticks, to the 10:10 close
]


def _chunk(rows: list[tuple], day: date = DAY, inst: int = 7, flags: int = 0) -> cc.Chunk:
    n = len(rows)
    return cc.Chunk(
        ts_recv=np.array([ct_ns(day, r[0]) for r in rows], dtype=np.int64),
        instrument_id=np.full(n, inst, dtype=np.int64), flags=np.full(n, flags, dtype=np.int64),
        bid_px=np.array([NULL if r[1] is None else _px(r[1]) for r in rows], dtype=np.int64),
        ask_px=np.array([NULL if r[2] is None else _px(r[2]) for r in rows], dtype=np.int64),
        bid_sz=np.array([r[3] for r in rows], dtype=np.int64),
        ask_sz=np.array([r[4] for r in rows], dtype=np.int64))


def _run_day(chunk_sizes: tuple[int, ...] = (len(RECORDS),), day: date = DAY) -> dict:
    acc = cc.DayAccumulator(cc.bucket_pieces(_cal(), day), TICK, ct_ns(day, time(10, 10)))
    start = 0
    for size in chunk_sizes:
        acc.feed(_chunk(RECORDS[start:start + size], day))
        start += size
    assert start == len(RECORDS)
    acc.finish()
    return acc.result()


# ------------------------------------------------------------------ buckets ----
def test_buckets_split_segments_at_ct_half_hours_with_reopen_grace() -> None:
    pieces = cc.bucket_pieces(_cal(), DAY)
    assert [(p.key, p.start_min, p.end_min) for p in pieces] == [
        ("08:00", 480, 510), ("08:30", 510, 540), ("09:30", 570, 600), ("10:00", 600, 610)]
    # the 1-second reopen grace starts each segment's first bucket; 10:00-10:10 is partial
    assert pieces[0].start_ns == ct_ns(DAY, time(8, 0)) + S
    assert pieces[2].start_ns == ct_ns(DAY, time(9, 30)) + S
    assert pieces[3].end_ns - pieces[3].start_ns == 600 * S


def test_evening_segment_buckets_cross_midnight_in_trade_date_order() -> None:
    cal = _cal(((time(17, 0), time(16, 0)),))
    spec = SessionSpec(valid_from=date(2025, 1, 1), valid_to=None,
                       segments=(Segment(-1, time(17, 0), 0, time(16, 0)),),
                       day_session_ct={"*": (time(8, 30), time(15, 0))}, source="test")
    cal = GroupCalendar(group="test", holidays={}, sessions=(spec,),
                        coverage=cal.coverage, assert_coverage=lambda d: None, module_paths=())
    pieces = cc.bucket_pieces(cal, DAY)
    assert len(pieces) == 46
    assert (pieces[0].key, pieces[0].start_ns) == ("17:00", ct_ns(date(2025, 5, 13),
                                                                  time(17, 0)) + S)
    assert [(p.key, p.end_min) for p in pieces if p.key in ("23:30", "15:30")] == [
        ("23:30", 1440), ("15:30", 960)]


# ------------------------------------------------------------------ time weighting ----
def test_time_weighted_spreads_known_answer_with_drops_and_closure() -> None:
    got = _run_day()["buckets"]
    b = got["08:00"]  # [08:00:01, 08:30): r0 599 s @2, r1 600 s @1, r2 300 s crossed, r3 300 s @3
    assert b["spread_ticks_ns"] == {"1": 600 * S, "2": 599 * S, "3": 300 * S}
    assert b["class_ns"] == {"valid": 1499 * S, "empty": 0, "locked": 0, "crossed": 300 * S}
    assert b["class_records"] == {"valid": 2, "empty": 0, "locked": 0, "crossed": 1}
    assert b["bid_size_ns"] == {"3": 600 * S, "5": 599 * S, "10": 300 * S}
    b = got["08:30"]  # r3 600 s @3, r4 600 s locked, r5 600 s @1 (to the 09:00 closure)
    assert b["spread_ticks_ns"] == {"1": 600 * S, "3": 600 * S}
    assert b["class_ns"]["locked"] == 600 * S
    b = got["09:30"]  # r6 (a closure record) carried from 09:30:01: 899 s @4; r7 300 s empty
    assert b["spread_ticks_ns"] == {"2": 600 * S, "4": 899 * S}
    assert b["class_ns"]["empty"] == 300 * S
    assert b["class_records"] == {"valid": 1, "empty": 1, "locked": 0, "crossed": 0}
    assert got["10:00"]["spread_ticks_ns"] == {"2": 600 * S}
    assert all(v["unknown_ns"] == 0 for v in got.values())
    # scale check: 6 valid states (r0 r1 r3 r5 r6 r8) x 2 prices; every bid is 100.00, on the
    # 10-tick grid (2.50); every ask (100.25, .50, .75, 101.00) is off it
    stats = _run_day()["stats"]
    assert stats["valid_prices_checked"] == 12
    assert stats["valid_prices_off_10x_grid"] == 6
    # the closure 09:00-09:30:01 counts nowhere; r0 and r6 are records in closed time
    assert _run_day()["stats"]["records_in_closed_time"] == 2


def test_chunking_does_not_change_the_result() -> None:
    whole = _run_day()
    for sizes in ((1,) * 9, (2, 3, 4), (4, 5), (8, 1)):
        assert _run_day(sizes)["buckets"] == whole["buckets"]


def test_state_before_the_first_record_is_unknown() -> None:
    acc = cc.DayAccumulator(cc.bucket_pieces(_cal(), DAY), TICK, ct_ns(DAY, time(10, 10)))
    acc.feed(_chunk(RECORDS[1:]))
    acc.finish()
    b = acc.result()["buckets"]["08:00"]  # nothing known from 08:00:01 to r1 at 08:10
    assert b["unknown_ns"] == 599 * S
    assert b["class_ns"]["valid"] == 900 * S


def test_regression_offgrid_and_unsnapshotted_switch_are_refused() -> None:
    def acc() -> cc.DayAccumulator:
        return cc.DayAccumulator(cc.bucket_pieces(_cal(), DAY), TICK, ct_ns(DAY, time(10, 10)))

    with pytest.raises(cc.CalibrationError, match="regresses"):
        acc().feed(_chunk([RECORDS[2], RECORDS[1]]))
    with pytest.raises(cc.CalibrationError, match="off the vendor tick grid"):
        acc().feed(_chunk([(time(8, 5), 100.00, 100.10, 1, 1), RECORDS[1]]))
    two = cc.Chunk.concat(_chunk([RECORDS[1]], inst=1), _chunk([RECORDS[3]], inst=2))
    with pytest.raises(cc.CalibrationError, match="snapshot"):
        acc().feed(two)


def test_instrument_switch_at_a_utc_midnight_snapshot_is_followed() -> None:
    cal = _cal(((time(17, 0), time(23, 0)),))  # 17:00-23:00 CDT holds 00:00 UTC
    midnight = int(datetime(2025, 5, 15, tzinfo=UTC).timestamp()) * S
    old = _chunk([(time(18, 0), 100.00, 100.25, 1, 1)], inst=1)
    new = _chunk([(time(18, 0), 100.00, 100.75, 1, 1)], inst=2, flags=cc.F_SNAPSHOT)
    new.ts_recv[:] = midnight
    acc = cc.DayAccumulator(cc.bucket_pieces(cal, DAY), TICK, ct_ns(DAY, time(23, 0)))
    acc.feed(cc.Chunk.concat(old, new))
    acc.finish()
    res = acc.result()
    assert res["instruments"] == [1, 2] and len(res["instrument_switches"]) == 1
    assert res["buckets"]["18:30"]["spread_ticks_ns"] == {"1": 1800 * S}  # old book to 19:00
    assert res["buckets"]["19:00"]["spread_ticks_ns"] == {"3": 1800 * S}  # the new book


def test_request_pieces_map_to_their_trade_date() -> None:
    assert cc.trade_date_of_request({"request_end": "2025-05-14T21:00:00Z"}) == DAY
    assert cc.trade_date_of_request({"request_end": "2025-11-12T10:30:00Z"}) == date(2025, 11, 12)
    assert cc.trade_date_of_request({"request_end": "2025-11-12T22:00:00Z"}) == date(2025, 11, 12)


# ------------------------------------------------------------------ the D8 rule ----
def _bucket(start_min: int, end_min: int, spread: dict[int, int], bid: dict[int, int],
            ask: dict[int, int]) -> dict:
    valid = sum(spread.values())
    return {"start_min": start_min, "end_min": end_min, "start_utc": "", "end_utc": "",
            "open_ns": valid, "unknown_ns": 0,
            "class_ns": {"valid": valid, "empty": 0, "locked": 0, "crossed": 0},
            "class_records": {"valid": 0, "empty": 0, "locked": 0, "crossed": 0},
            "spread_ticks_ns": {str(k): v for k, v in spread.items()},
            "bid_size_ns": {str(k): v for k, v in bid.items()},
            "ask_size_ns": {str(k): v for k, v in ask.items()}}


def _raw_dates(thin_dates: int = 2) -> dict[str, dict]:
    """A: 1-tick spread, bid median 1, ask 10; B: 2 ticks, sizes 10; C quoted on ``thin_dates``."""
    out = {}
    for i, day in enumerate(SAMPLE_DATES):
        buckets = {
            "08:00": _bucket(480, 510, {1: 1800 * S}, {1: 1800 * S}, {10: 1800 * S}),
            "08:30": _bucket(510, 540, {2: 1800 * S}, {10: 1800 * S}, {10: 1800 * S}),
        }
        c = {1: 1800 * S} if i < thin_dates else {}
        buckets["09:00"] = _bucket(540, 570, c, {5: 1800 * S} if c else {},
                                   {5: 1800 * S} if c else {})
        out[day.isoformat()] = {"buckets": buckets, "stats": {"records": 1},
                                "first_ts_recv_utc": "", "knowledge_end_utc": "",
                                "instruments": [1], "instrument_switches": [],
                                "min_spread_ticks": 1}
    return out


def test_pooled_half_spread_and_lower_median_on_the_known_book() -> None:
    day = _run_day()
    stats = cost_rule.aggregate({d.isoformat(): day for d in SAMPLE_DATES})
    by = {b.key: b for b in stats}
    # 08:00: (599x2 + 600x1 + 300x3) / 1499 s / 2 = 1349/1499 ticks
    assert by["08:00"].half_spread == Fraction(1349, 1499)
    assert by["08:30"].half_spread == 1  # (600x3 + 600x1) / 1200 / 2
    assert by["09:30"].half_spread == Fraction(2398, 1499)  # (899x4 + 600x2) / 1499 / 2
    assert by["08:00"].median_size == {"bid": 5, "ask": 4}  # bid 3:600 5:599 10:300 of 1499
    assert by["08:30"].median_size == {"bid": 1, "ask": 1}  # lower median of a 50/50 split
    assert by["09:30"].median_size == {"bid": 9, "ask": 9}
    assert all(b.dates_with_quotes == 5 for b in stats)
    assert cost_rule.weighted_lower_median({}) is None


def test_depth_term_below_at_and_above_q_c() -> None:
    assert cost_rule.depth_ticks(1, 4) == Fraction(3, 4)
    assert cost_rule.depth_ticks(3, 4) == Fraction(1, 4)
    assert cost_rule.depth_ticks(4, 4) == 0
    assert cost_rule.depth_ticks(10, 4) == 0
    assert cost_rule.depth_ticks(1, None) == 0  # pending
    with pytest.raises(ValueError):
        cost_rule.depth_ticks(1, 0)


def test_fallback_takes_the_largest_other_bucket_per_side_and_event_matches() -> None:
    stats = cost_rule.aggregate(_raw_dates(thin_dates=2))
    rule = cost_rule.ProductRule(Decimal("1.72"), Decimal("1.0"), q_c=4)
    costs, event = cost_rule.apply_rule(stats, rule)
    by = {c.stats.key: c for c in costs}
    # A: s_b 1/2; buy hits ask (10 >= 4): 0; sell hits bid (1 < 4): 3/4 -> 1/2, 5/4
    assert by["08:00"].side_ticks == {"buy": Fraction(1, 2), "sell": Fraction(5, 4)}
    # B: s_b 1; sizes 10 >= 4: no depth
    assert by["08:30"].side_ticks == {"buy": 1, "sell": 1}
    # C quoted on 2 of 5 dates: per side the largest of A and B (buy from B, sell from A)
    assert by["09:00"].fallback and by["09:00"].stats.dates_with_quotes == 2
    assert by["09:00"].side_ticks == {"buy": 1, "sell": Fraction(5, 4)}
    assert by["09:00"].depth == {"buy": None, "sell": None}
    assert event == {"buy": 1, "sell": Fraction(5, 4)}
    # round turn = 1.72 / 1.0 + buy + sell
    assert by["08:00"].round_turn_ticks == Fraction(172, 100) + Fraction(7, 4)


def test_three_dates_qualify_and_no_qualified_bucket_is_uncalibratable() -> None:
    stats = cost_rule.aggregate(_raw_dates(thin_dates=3))
    costs, _ = cost_rule.apply_rule(stats, cost_rule.ProductRule(Decimal("1"), Decimal("1"),
                                                                 None))
    assert not any(c.fallback for c in costs)
    thin = [cost_rule.BucketStats(**{**s.__dict__, "dates_with_quotes": 2}) for s in stats]
    with pytest.raises(cost_rule.UncalibratableError):
        cost_rule.apply_rule(thin, cost_rule.ProductRule(Decimal("1"), Decimal("1"), None))


def test_day_session_buckets_include_a_bucket_straddling_the_open() -> None:
    stats = cost_rule.aggregate(_raw_dates(3))
    costs, _ = cost_rule.apply_rule(stats, cost_rule.ProductRule(Decimal("1"), Decimal("1"),
                                                                 None))
    keys = [c.stats.key for c in cost_rule.day_session_buckets(costs, time(8, 20), time(9, 0))]
    assert keys == ["08:00", "08:30"]


# ------------------------------------------------------------------ inputs ----
def test_commissions_apply_the_2026_10_01_increase_to_mcl_and_mng_only() -> None:
    table = cost_inputs.load_commissions()
    assert table["MCL"] == Decimal("1.72") and table["MNG"] == Decimal("1.92")
    for root, usd in {"MNQ": "1.22", "ZN": "2.62", "6E": "4.22", "GC": "4.32", "ZC": "5.28",
                      "CL": "4.02", "NG": "4.22", "MES": "1.22"}.items():
        assert table[root] == Decimal(usd)
    admissible = set(cost_inputs.mbp1_files())
    assert len(admissible) == 45 and admissible <= set(table)


def test_ticks_and_vendor_units_of_cent_quoted_products() -> None:
    ticks = cost_inputs.load_ticks()
    assert set(cost_inputs.mbp1_files()) <= set(ticks)
    expect = {"ZC": "0.25", "ZW": "0.25", "ZS": "0.25", "ZL": "0.01", "HE": "0.025",
              "LE": "0.025", "ZM": "0.10", "ZN": "0.015625", "6J": "5E-7", "MBT": "5.00"}
    for root, vendor in expect.items():
        assert ticks[root].vendor_tick == Decimal(vendor), root
    assert ticks["MNQ"].tick_value_usd == Decimal("0.5")


# ------------------------------------------------------------------ table and loader ----
def _entry(q_c: int | None) -> dict:
    raw = {"product": "MCL", "group": "energy", "vendor_tick_fixed": 10_000_000,
           "dates": _raw_dates(2), "files": [], "calendar_sha256": {}, "code_sha256": {}}
    tick = TickSpec("MCL", Decimal("0.01"), Decimal("1.0"), 1, "0.01")
    return cost_report.product_entry(raw, tick, Decimal("1.72"), q_c, (time(8, 0), time(9, 0)))


def _write_table(tmp_path: Path, q_c: int | None) -> Path:
    path = tmp_path / "costs.json"
    path.write_text(json.dumps({"depth_term": "applied" if q_c else "pending",
                                "products": {"MCL": _entry(q_c)}}))
    return path


def test_loader_round_trip_and_event_override(tmp_path: Path) -> None:
    entry = _entry(4)
    model = product_costs.load_cost_table(_write_table(tmp_path, 4))["MCL"]
    assert model.commission_rt_usd == 1.72 and model.q_c == 4 and not model.provisional
    for b in entry["buckets"]:
        assert model.bucket_at(time(b["start_min"] // 60, b["start_min"] % 60)).side_ticks == \
            b["side_ticks"]
    at = datetime(2025, 5, 14, 13, 10, tzinfo=UTC)  # 08:10 CDT, bucket 08:00
    assert model.side_slippage_ticks(at, "buy") == 0.5
    assert model.side_slippage_ticks(at, "sell") == 1.25
    assert model.side_slippage_ticks(at, "buy", in_event_window=True) == 1.0
    assert model.side_slippage_ticks(at, "sell", in_event_window=True) == 1.25
    # a long entered at 08:10 and exited at 08:40 CT: 1.72 + buy@08:00 (0.5) + sell@08:30 (1)
    assert model.round_turn_ticks(time(8, 10), time(8, 40), +1) == pytest.approx(3.22)
    assert model.round_turn_usd(time(8, 10), time(8, 40), -1, qty=2) == pytest.approx(
        2 * (1.72 + 1.25 + 1.0))
    assert model.side_cost_usd(time(8, 10), "sell", 3) == pytest.approx(3 * (0.86 + 1.25))
    assert entry["event_window_side_ticks"] == {"buy": 1.0, "sell": 1.25}
    assert entry["headline_day_session"]["n_buckets"] == 2
    with pytest.raises(product_costs.CostLookupError):
        model.side_slippage_ticks(time(9, 45), "buy")  # no bucket there


def test_provisional_table_is_refused_unless_asked(tmp_path: Path) -> None:
    path = _write_table(tmp_path, None)
    with pytest.raises(product_costs.ProvisionalTableError):
        product_costs.load_cost_table(path)
    model = product_costs.load_cost_table(path, allow_provisional=True)["MCL"]
    assert model.provisional and model.bucket_at(time(8, 5)).side_ticks == {"buy": 0.5,
                                                                            "sell": 0.5}


def test_mes_check_reexpresses_fifteen_minute_halves(tmp_path: Path) -> None:
    d1 = {"bucket_minutes": 15, "buckets_ct": {
        "08:30": {"half_spread_ticks_mean": 0.54}, "08:45": {"half_spread_ticks_mean": 0.56}}}
    path = tmp_path / "d1.json"
    path.write_text(json.dumps(d1))
    got = cost_report.mes_check(None, path)
    row = got["rows"][0]
    assert row["key"] == "08:30" and row["mes_s_b_ticks"] == pytest.approx(0.55)
    assert row["mes_round_turn_ticks"] == pytest.approx(1.22 / 1.25 + 1.10)


# ------------------------------------------------------------------ the frozen table ----
REPORT = cost_report.OUT_JSON


@pytest.mark.skipif(not REPORT.exists(), reason="the cost table has not been built")
def test_frozen_table_is_internally_consistent() -> None:
    table = json.loads(REPORT.read_text())
    assert table["sample_dates"] == [d.isoformat() for d in SAMPLE_DATES]
    commissions = cost_inputs.load_commissions()
    for root, p in table["products"].items():
        assert p["commission_rt_usd"] == pytest.approx(float(commissions[root]))
        assert p["vendor_tick_check"]["passed"], root
        if not p["calibrated"]:
            continue
        qualified = [b for b in p["buckets"] if b["dates_with_quotes"] >= 3]
        for b in p["buckets"]:
            assert b["round_turn_ticks"] == pytest.approx(
                p["commission_rt_ticks"] + b["side_ticks"]["buy"] + b["side_ticks"]["sell"])
            if b["fallback"]:
                for side in ("buy", "sell"):
                    assert b["side_ticks"][side] == pytest.approx(
                        max(q["side_ticks"][side] for q in qualified))
        for side in ("buy", "sell"):
            assert p["event_window_side_ticks"][side] == pytest.approx(
                max(b["side_ticks"][side] for b in p["buckets"]))
