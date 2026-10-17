"""Trigger extraction (trigger_hold.events*): synthetic bars through the adapter and the engine,
the release-table filters, the 2010-2019 month-end table, and the recorded W_cf comparisons.
No store is read here."""

from __future__ import annotations

import json
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import pytest

from data.stage_e_bars import BAR_COLUMNS, LegFrame
from screening.stage_e_rules import load_release_calendar
from trigger_hold import events as EV
from trigger_hold import events_members as EM
from trigger_hold import events_tables as ET
from trigger_hold.types import EVENT_KEYS, TriggerEvent, events_record

CT = ZoneInfo("America/Chicago")
REPO = Path(__file__).resolve().parents[1]
DAYS = (date(2023, 6, 27), date(2023, 6, 28), date(2023, 6, 29), date(2023, 6, 30))
N_MINUS_1, N = date(2023, 6, 29), date(2023, 6, 30)  # the frozen month-end table's June 2023


def ct_ns(day: date, at: time) -> int:
    return int(datetime.combine(day, at, tzinfo=CT).astimezone(UTC).timestamp()) * 10**9


def synth_leg(root: str = "ZN", days=DAYS, drop: tuple[tuple[date, time], ...] = (),
              halts: dict[date, str] | None = None, price: float = 110.0) -> LegFrame:
    """Flat minute bars 06:00-15:30 CT on each day (no price movement), one contract."""
    halts = halts or {}
    rows = []
    for d in days:
        t = datetime.combine(d, time(6, 0))
        while t.time() < time(15, 30):
            if (d, t.time()) not in drop:
                rows.append({"ts_event": ct_ns(d, t.time()), "open": price, "high": price,
                             "low": price, "close": price, "volume": 100, "instrument_id": 7,
                             "raw_symbol": f"{root}U3", "trade_date": d.isoformat(),
                             "in_flatten_window": False, "in_no_new_positions_window": False,
                             "early_halt_ct": halts.get(d, ""), "in_scheduled_closure": False,
                             "is_roll_session": False, "gap_before_minutes": 0,
                             "vendor_degraded_day": False})
            t += timedelta(minutes=1)
    frame = pd.DataFrame(rows, columns=list(BAR_COLUMNS))
    return LegFrame(root, "synthetic", "synthetic", "0" * 64, frame, tuple(days), (), frozenset())


def run_monthend(leg: LegFrame):
    spec = EM.spec_for("K2-monthend-01 ZN")
    built = EM.build_member(spec, None)
    capture, mw = EV.run_member(built.member, built.decl.legs, {"ZN": leg}, "synthetic",
                                load_release_calendar())
    sched = EV.schedule_counts(built.member, {"ZN": leg}, mw.dates, DAYS[0], DAYS[-1],
                               capture.events)
    return capture, sched


def test_entry_lands_on_the_decision_bar_close_of_each_table_date() -> None:
    capture, sched = run_monthend(synth_leg())
    tau = [ct_ns(d, time(7, 21)) for d in (N_MINUS_1, N)]  # the 07:20 bar's close
    assert capture.events == ((N_MINUS_1, tau[0], 1), (N, tau[1], 1))
    assert capture.counts["entries"] == 2
    assert sched["table_date:entered"] == 2
    assert sched["window_dates_not_table_dates"] == 2


def test_early_halt_day_is_not_entered() -> None:
    capture, sched = run_monthend(synth_leg(halts={N: "12:00"}))
    assert [e[0] for e in capture.events] == [N_MINUS_1]
    assert sched["table_date:early_halt"] == 1


def test_missing_decision_bar_gives_no_entry_and_no_later_one() -> None:
    capture, sched = run_monthend(synth_leg(drop=((N_MINUS_1, time(7, 20)),)))
    assert [e[0] for e in capture.events] == [N]
    assert sched["table_date:decision_bar_missing"] == 1


def test_roll_blackout_date_is_refused_by_the_engine() -> None:
    leg = synth_leg()
    leg = LegFrame(leg.root, leg.store, leg.path, leg.sha256, leg.frame, leg.trade_dates, (N,),
                   frozenset({N}))
    capture, sched = run_monthend(leg)
    assert [e[0] for e in capture.events] == [N_MINUS_1]
    assert sched["table_date:outside_member_window (roll blackout)"] == 1
    assert capture.counts["entry_intent_refused:engine_not_a_window_date"] == 1


def test_events_record_holds_only_dates_instants_and_sides() -> None:
    capture, _ = run_monthend(synth_leg())
    rec = events_record("K2-monthend-01 ZN", "ZN", "W_cf",
                        [TriggerEvent(d, t, s, "K2-monthend-01 ZN") for d, t, s in capture.events],
                        capture.counts, {})
    assert all(set(r) == EVENT_KEYS for r in rec["events"])
    assert all(isinstance(v, int) for v in rec["counts"].values())


EXIT_SIDE = ("engine_counter", "mll", "forced_flatten", "liquidation", "order_cancelled:",
             "pnl", "exit")


def test_no_exit_side_fact_is_counted() -> None:
    capture, _ = run_monthend(synth_leg())
    assert not [k for k in capture.counts if any(w in k.lower() for w in EXIT_SIDE)]


@pytest.mark.parametrize("path", sorted((REPO / "reports" / "stage_e23_events").glob("*.json")))
def test_written_events_files_carry_no_exit_side_count(path: Path) -> None:
    body = json.loads(path.read_text(encoding="utf-8"))
    keys = list(body.get("counts", {}))
    assert not [k for k in keys if any(w in k.lower() for w in EXIT_SIDE)]


# ------------------------------------------------------------------ tables ----
def _row(release: str, day: str, instant: str, rid: str | None = None) -> dict:
    return {"id": rid or f"{release}-{day}", "release": release, "date": day,
            "instant_utc": instant}


def test_fomc_filter_keeps_only_13_00_ct_statements() -> None:
    rows = [_row("FOMC", "2012-01-25", "2012-01-25T17:30:00Z"),  # 12:30 ET
            _row("FOMC", "2012-03-13", "2012-03-13T18:15:00Z"),  # 14:15 ET
            _row("FOMC", "2014-03-19", "2014-03-19T18:00:00Z"),  # 14:00 ET = 13:00 CT
            _row("NGS", "2014-03-20", "2014-03-20T14:30:00Z")]
    dates, counts = ET.fomc_statement_dates(rows)
    assert dates == ("2014-03-19",)
    assert counts["fomc_rows"] == 3 and counts["kept"] == 1
    assert counts["excluded:statement_not_at_13:00_CT (11:30 CT)"] == 1
    assert counts["excluded:statement_not_at_13:00_CT (13:15 CT)"] == 1


def test_auction_filter_keeps_the_four_tenors_with_ct_times() -> None:
    rows = [_row("TREASURY_AUCTION", "2015-02-10", "2015-02-10T18:00:00Z",
                 "TREASURY_AUCTION-2015-02-10-3Y"),
            _row("TREASURY_AUCTION", "2015-02-11", "2015-02-11T18:00:00Z",
                 "TREASURY_AUCTION-2015-02-11-10Y")]
    got, counts = ET.treasury_auctions(rows)
    assert got == (("2015-02-11", "10Y", "12:00"),)
    assert counts["excluded:tenor_3Y"] == 1


def test_filters_reproduce_the_frozen_member_tables() -> None:
    from strategy.members.k2 import _releases as K2R
    from strategy.members.k5 import _releases as K5R

    frozen = ET.read_rows(ET.FROZEN_CALENDAR_PATH)
    assert ET.fomc_statement_dates(frozen.rows)[0] == K2R.FOMC_STATEMENT_DATES
    assert ET.fomc_statement_dates(frozen.rows)[0] == K5R.FOMC_STATEMENT_DATES
    assert ET.treasury_auctions(frozen.rows)[0] == tuple(sorted(K2R.TREASURY_AUCTIONS))


def test_month_end_rule_reproduces_the_frozen_table() -> None:
    from data.group_session import load_group_calendar
    from strategy.members.k2._month_end import MONTH_END

    cal = load_group_calendar("rates")
    first, last = cal.coverage
    assert ET.month_end_rows(cal, first, last) == MONTH_END


def test_hist_month_end_table_equals_the_backward_swap_s6() -> None:
    from strategy.members.k2 import monthend
    from trigger_hold.events_context import hist_context

    first, last = date(2011, 6, 1), date(2019, 4, 30)
    table = ET.hist_month_end_table(first, last)
    mine = {date.fromisoformat(d) for d in table.rows}
    frozen = monthend.EVENT_DATES
    with hist_context():
        s6 = {d for d in monthend.EVENT_DATES if first <= d <= last}
    assert monthend.EVENT_DATES is frozen  # restored
    assert s6 == mine and len(mine) == 190


def test_sourced_rows_agree_with_the_frozen_calendar_on_the_overlap() -> None:
    check = ET.overlap_check()
    assert all(v["equal"] for v in check.values())


def test_hist_fomc_table_starts_on_2013_03_20() -> None:
    table = ET.hist_fomc_table(date(2011, 6, 1), date(2019, 4, 30))
    assert table.rows[0] == "2013-03-20"
    assert sum(v for k, v in table.counts.items() if k.startswith("excluded")) > 0


def test_a_table_member_is_refused_on_w_ext_without_a_declared_table() -> None:
    spec = EM.TriggerSpec("K2-predrift-01 ZN", "K2", "K2-predrift-01 ZN", None)
    with pytest.raises(EM.MemberRefused):
        EM.check_table_need(spec)


def test_trigger_ids_resolve_with_space_or_underscore() -> None:
    assert EM.spec_for("K2-monthend-01_ZB").label == "K2-monthend-01 ZB"
    with pytest.raises(EM.MemberRefused):
        EM.spec_for("E20H6-T1 NQ")


# ------------------------------------------------------------------ recorded W_cf check ----
VALIDATION = REPO / "reports" / "stage_e23_events" / "validation"
TRIGGERS = ("K2-monthend-01_ZF", "K2-monthend-01_ZN", "K2-monthend-01_ZB", "E20H6-T1_NQ")


@pytest.mark.parametrize("trigger", TRIGGERS)
def test_recorded_w_cf_comparison(trigger: str) -> None:
    path = VALIDATION / f"{trigger}__cf.json"
    if not path.is_file():
        pytest.skip(f"{path.name} not written yet")
    body = json.loads(path.read_text(encoding="utf-8"))
    assert body["same_d0_and_side"] is True, body["differences"][:5]
    assert body["adapter"]["n"] == body["harness"]["n"]
