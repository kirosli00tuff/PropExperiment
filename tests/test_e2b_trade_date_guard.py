"""Stage E.2b Task 4: the CME trade-date purchase guard (ruling L-9), data/trade_date_guard.py.

Calendars only (data.calendars, data.cme_calendar): no network, no vendor file, no bar. The
pull_universe tests use a fake client and a tmp ledger; the real ledger is checked untouched.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from types import SimpleNamespace

import pytest

from data import config, pull_mes
from data import holdout as ho
from data import pull_universe as pu
from data import trade_date_guard as tdg
from data.research_bars import CONFIRMATION_RAW_CHUNKS, HOLDOUT2_RAW_CHUNKS
from data.spend_gate import RequestParams, read_entries


def _lines(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines()) if path.is_file() else 0


# ------------------------------------------------------------- MBT, L-9 ----
def test_mbt_request_ending_2026_06_21_is_booked_partly_to_holdout1_and_refused() -> None:
    # Arrange: MBT's step 1 last chunk, which ends at 2026-06-21 00:00 UTC (timestamp guard end).
    start, end = "2026-06-01", "2026-06-21"

    # Act
    booked = tdg.booking("MBT", start, end)

    # Assert: Juneteenth (Fri 06-19) and the weekend belong to trade date 2026-06-22 from
    # Thursday 2026-06-18 16:02 CT (21:02 UTC), E.2a's L-9 finding.
    assert booked.group == "crypto"
    assert booked.trade_dates[-1] == date(2026, 6, 22)
    first_22 = dict(zip(booked.trade_dates, booked.first_minute_ns, strict=True))[date(2026, 6, 22)]
    assert tdg._iso(first_22) == "2026-06-18T21:02:00Z"
    with pytest.raises(tdg.HoldoutTradeDateRefused,
                       match=r"2026-06-18T21:02:00Z .*trade date 2026-06-22, a holdout-1"):
        tdg.refuse_holdout_bookings("MBT", start, end)
    with pytest.raises(tdg.HoldoutTradeDateRefused):  # sealing never admits holdout-1
        tdg.refuse_holdout_bookings("MBT", start, end, sealing=True)


def test_mbt_before_the_juneteenth_booking_is_admitted() -> None:
    got = tdg.refuse_holdout_bookings("MBT", "2026-06-01", "2026-06-18T21:00:00Z")
    assert got.trade_dates[-1] == date(2026, 6, 18)


def test_the_step1_buy_refuses_mbts_last_chunk_before_any_vendor_call(tmp_path: Path) -> None:
    # Arrange: the E.1 plan still builds (history), but its MBT last chunk cannot be bought.
    real = _lines(config.LEDGER_PATH)
    plan = pu.plan_requests(["MBT"])
    last = next(r for r in plan if (r.params.start, r.params.end) == ("2026-06-01", "2026-06-21"))
    calls: list[str] = []
    client = SimpleNamespace(metadata=SimpleNamespace(get_cost=lambda **k: calls.append("q")),
                             timeseries=SimpleNamespace(get_range=lambda **k: calls.append("d")),
                             batch=None)
    gate = pu.e1_gate(ledger_path=tmp_path / "ledger.jsonl",
                      access_doc_path=tmp_path / "ACCESS.md")

    # Act / Assert
    with pytest.raises(pu.TradeDateGuardError, match="holdout-1"):
        pu.check_trade_dates(last)
    with pytest.raises(pu.DateGuardError, match="2026-06-22"):
        pu.run_buy(client, gate, [plan[0], last], root=tmp_path / "v", log=print)
    assert calls == [] and read_entries(tmp_path / "ledger.jsonl") == []
    assert _lines(config.LEDGER_PATH) == real


def test_other_step1_last_chunks_are_refused_because_the_calendars_end_2026_06_19() -> None:
    last = pu.PlannedRequest("MNQ", RequestParams("GLBX.MDP3", ("MNQ.v.0",), "ohlcv-1m",
                                                  "continuous", "2026-06-01", "2026-06-21"))
    with pytest.raises(pu.TradeDateGuardError, match="not every minute of it can be booked"):
        pu.check_trade_dates(last)
    pu.check_trade_dates(pu.plan_requests(["MNQ"])[0])  # 2025-04 chunk: admitted


# ------------------------------------------------------------ holdout 2 ----
def test_an_unsealed_request_booked_to_holdout2_is_refused_and_the_sealing_one_admitted() -> None:
    # March 2024 chunk: its last evening (Sunday 03-31 17:00 CT) is trade date 2024-04-01.
    with pytest.raises(tdg.HoldoutTradeDateRefused, match=r"2024-04-01, a holdout-2"):
        tdg.refuse_holdout_bookings("ZN", "2024-03-01", "2024-04-01")
    got = tdg.refuse_holdout_bookings("ZN", "2024-03-01", "2024-04-01", sealing=True)
    assert got.trade_dates[-1] == date(2024, 4, 1)


def test_the_close_minute_is_booked_to_the_session_it_closes() -> None:
    # 2025-03-31 (holdout-2's last date) closes 16:00 CT = 21:00 UTC; its close minute is L-3's.
    with pytest.raises(tdg.HoldoutTradeDateRefused, match="2025-03-31"):
        tdg.refuse_holdout_bookings("ZN", "2025-03-31T21:00:00Z", "2025-03-31T21:01:00Z")
    got = tdg.booking("ZN", "2025-03-31T21:01:00Z", "2025-03-31T22:01:00Z")
    assert got.trade_dates == (date(2025, 4, 1),)  # the closure minutes carry no booking


def test_feb_2024_chunk_books_to_the_embargo_which_is_not_a_purchase_refusal() -> None:
    got = tdg.refuse_holdout_bookings("CL", "2024-02-01", "2024-03-01")
    assert got.trade_dates[-1] == date(2024, 3, 1)  # dropped by the step 2 store, not here


@pytest.mark.parametrize("root", ["NQ", "ZN", "6E", "CL", "GC", "ZC", "HE", "LE", "MBT"])
def test_every_unsealed_step2_chunk_is_clean_and_every_sealed_one_needs_sealing(root: str) -> None:
    for start, end in CONFIRMATION_RAW_CHUNKS:
        tdg.refuse_holdout_bookings(root, start, end)  # no raise
    for start, end in HOLDOUT2_RAW_CHUNKS[1:]:
        with pytest.raises(tdg.HoldoutTradeDateRefused):
            tdg.refuse_holdout_bookings(root, start, end)
        tdg.refuse_holdout_bookings(root, start, end, sealing=True)


def test_a_day_only_calendars_first_minutes_before_its_first_session_are_admitted() -> None:
    # Livestock opens 08:30 CT: 2019-05-01 00:00..13:30 UTC precede the calendar's first session,
    # and nothing on or before that trade date is a holdout date.
    got = tdg.refuse_holdout_bookings("HE", "2019-05-01", "2019-06-01")
    assert got.trade_dates[0] == date(2019, 5, 1)


def test_unknown_minutes_before_a_holdout_session_are_refused(monkeypatch: pytest.MonkeyPatch
                                                              ) -> None:
    # A calendar whose first shown session is a holdout-2 date cannot clear earlier minutes.
    real = tdg._intervals

    def clipped(group: str, first: date, last: date):  # noqa: ANN202
        return real(group, max(first, date(2024, 4, 1)), last)

    monkeypatch.setattr(tdg, "_intervals", clipped)
    with pytest.raises(tdg.CalendarCoverageRefused):
        tdg.booking("ZN", "2024-03-20", "2024-04-10")


def test_an_empty_or_inverted_request_is_refused() -> None:
    with pytest.raises(tdg.TradeDateRefused, match="empty or inverted"):
        tdg.booking("ZN", "2024-05-01", "2024-05-01")


# -------------------------------------------------- MES paths (not edited) ----
def test_mes_purchase_paths_never_reach_a_holdout_booking_outside_their_seals() -> None:
    """data/pull_mes.py is unchanged: its A.1 chunks either touch the sealed holdout-1 window
    (skipped by the timestamp guard) or pass the trade-date guard; its D.1f unsealed chunks
    pass; its holdout-2 chunks book holdout-2 and are the ones it seals."""
    for start, end in pull_mes.monthly_chunks(pull_mes.WINDOW_START, pull_mes.WINDOW_END):
        if ho.request_touches_sealed_window(start, end):
            continue
        tdg.refuse_holdout_bookings("MES", start, end)
    assert pull_mes.d1f_chunks()[:58] == list(CONFIRMATION_RAW_CHUNKS)
    for start, end in CONFIRMATION_RAW_CHUNKS:
        tdg.refuse_holdout_bookings("MES", start, end)
    for start, end in HOLDOUT2_RAW_CHUNKS:
        booked = tdg.refuse_holdout_bookings("MES", start, end, sealing=True)
        assert any(tdg.is_holdout2(d) for d in booked.trade_dates)
