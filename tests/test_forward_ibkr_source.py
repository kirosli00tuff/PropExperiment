"""IBKRSettlementSource with the mock gateway: rolls, missing days, partial history, time zones,
reconnects (Stage E.24; synthetic prices, no network)."""

from __future__ import annotations

import json
from datetime import UTC, date, datetime

import pytest

from forward.ibkr_gateway import (
    ConnectionParams,
    ConventionError,
    DayNotReady,
    GatewaySession,
    Pacer,
    RetryPolicy,
    SourceUnavailable,
)
from forward.runner import PaperRunner, RunnerConfig, load_tables
from forward.sources import Missing
from forward.sources_ibkr import (
    ContractResolver,
    IBKRSettlementSource,
    chicago_date,
    latest_ready_trade_date,
)
from tests._forward_ibkr_mock import (
    ENV,
    FAKE_VENDOR,
    ROLLS,
    FakeBar,
    FakeRequestError,
    MockGateway,
    build_bars,
    build_listings,
    ct,
    ib_price,
)

FIRST, LAST = date(2026, 10, 1), date(2027, 1, 29)


def make(now, *, holes=frozenset(), last=LAST, policy=None, provenance=None, clock=False):
    listings = build_listings(FIRST, LAST)
    gw = MockGateway(listings, build_bars(listings, FIRST, last, holes=holes), now=now)
    slept: list[float] = []
    extra = {"clock": gw.monotonic} if clock else {}  # the mock clock (stall fault mode)
    session = GatewaySession(
        gw,
        ConnectionParams.from_env(ENV),
        policy=policy or RetryPolicy(max_attempts=3),
        sleep=slept.append,
        **extra,
    )
    multipliers, _ = load_tables("forward/tables_f1.json")
    resolver = ContractResolver(session, FAKE_VENDOR, ROLLS, config_multipliers=multipliers)
    src = IBKRSettlementSource(
        session, resolver, ROLLS, now=lambda: gw.now, provenance_path=provenance
    )
    return gw, src, slept


def runner_config() -> RunnerConfig:
    multipliers, costs = load_tables("forward/tables_f1.json")
    return RunnerConfig(multipliers, costs, ROLLS, {})


def test_a_normal_day_delivers_every_reference_contract_in_runner_units():
    gw, src, _ = make(ct(2026, 11, 2, 19))
    day = date(2026, 11, 2)
    ans = src.settlements(day)
    assert set(ans) == set(ROLLS)
    assert ans["MNQ"] == {"MNQZ26": ib_price("MNQ", "MNQZ26", day)}
    assert ans["MZC"] == {"MZCZ26": ib_price("MZC", "MZCZ26", day) / 100}
    calls = gw.count("reqHistoricalData")
    assert src.settlements(day) == ans and gw.count("reqHistoricalData") == calls  # memo


def test_both_contracts_are_delivered_from_the_roll_date_through_the_anchor():
    gw, src, _ = make(ct(2026, 12, 21, 19))
    assert set(src.settlements(date(2026, 12, 9))["MNQ"]) == {"MNQZ26"}
    assert set(src.settlements(date(2026, 12, 10))["MNQ"]) == {"MNQZ26", "MNQH27"}
    assert set(src.settlements(date(2026, 12, 18))["MNQ"]) == {"MNQZ26", "MNQH27"}
    assert set(src.settlements(date(2026, 12, 21))["MNQ"]) == {"MNQH27"}


def test_runner_rolls_across_the_anchor_on_the_declared_roll_date(tmp_path):
    gw, src, _ = make(ct(2026, 12, 21, 19))
    plan = {"MNQ": 2}

    def target(history, prev, config):
        return {i: plan.get(i, 0) for i in prev if history[-1].price(i) is not None}

    runner = PaperRunner(tmp_path / "l.jsonl", src, runner_config(), target_fn=target)
    days = [date(2026, 12, d) for d in (7, 8, 9, 10, 11)]
    recs = runner.run_dates(days)
    roll = next(r for r in recs[3]["rolls"] if r["instrument"] == "MNQ")
    assert roll["from_contract"] == "MNQZ26"
    assert roll["to_contract"] == "MNQH27" and roll["qty"] == 2
    assert not any(r["instrument"] == "MNQ" for rec in recs[:3] for r in rec["rolls"])
    assert recs[2]["positions"]["MNQ"]["contract"] == "MNQZ26"
    assert recs[3]["positions"]["MNQ"]["contract"] == "MNQH27"


def test_an_instrument_without_a_bar_while_later_bars_exist_is_left_out():
    day = date(2026, 11, 4)
    gw, src, _ = make(ct(2026, 11, 5, 19), holes={("MGCZ26", day)})
    ans = src.settlements(day)
    assert "MGC" not in ans and "MNQ" in ans


def test_a_whole_day_without_bars_is_missing_only_when_later_bars_confirm_it():
    day = date(2026, 11, 26)  # synthetic: no contract has a bar this day
    listings = build_listings(FIRST, LAST)
    holes = {(cid, day) for (_, cid) in listings}
    gw, src, _ = make(ct(2026, 11, 27, 19), holes=holes)
    assert isinstance(src.settlements(day), Missing)


@pytest.mark.parametrize("inst,cid", [("MGC", "MGCZ26"), ("MZC", "MZCZ26")])
def test_no_bar_and_only_the_open_sessions_partial_bar_is_not_ready(tmp_path, inst, cid):
    # S2 (wave 3): the production state at 19:00 CT on t. The t+1 session opened at 17:00 CT,
    # so every list ends with its partial bar dated t+1 (the mock serves it, as IB does: I6).
    # That bar is not final, so it confirms nothing: the absence stays open (no record).
    day = date(2026, 11, 4)
    gw, src, _ = make(ct(2026, 11, 4, 19), holes={(cid, day)})
    src.session.ensure_connected()
    served = gw.reqHistoricalData(
        gw.listings[(inst, cid)].contract, "", "5 D", "1 day", "TRADES", False
    )
    assert max(b.date for b in served) == date(2026, 11, 5)  # the partial bar is present
    with pytest.raises(DayNotReady, match=f"{inst}:{cid}"):
        src.settlements(day)
    runner = PaperRunner(tmp_path / "l.jsonl", src, runner_config(), target_fn=lambda h, p, c: {})
    with pytest.raises(DayNotReady):
        runner.run_date(day)
    assert not (tmp_path / "l.jsonl").exists()
    # one evening later the t+1 bar is final: the absence is affirmed, the rest is priced
    gw2, src2, _ = make(ct(2026, 11, 5, 18), holes={(cid, day)})
    ans = src2.settlements(day)
    assert inst not in ans and len(ans) == 11


def test_a_friday_absence_waits_for_mondays_final_bar():
    day = date(2026, 11, 6)  # Friday
    gw, src, _ = make(ct(2026, 11, 8, 19), holes={("MGCZ26", day)})  # Sunday: Monday's bar open
    with pytest.raises(DayNotReady, match="MGC:MGCZ26"):
        src.settlements(day)
    gw2, src2, _ = make(ct(2026, 11, 9, 18, 1), holes={("MGCZ26", day)})
    assert "MGC" not in src2.settlements(day)


@pytest.mark.parametrize("kept", [0, 1, None])
def test_a_stalled_request_never_yields_a_partial_list_and_writes_no_record(tmp_path, kept):
    # B1 (wave 3): ib_async's wait_for fires mid-stream; the call returns after the timeout with
    # the bars received so far (kept=None: all bars before the day; 0: ib_async 2.1.0's cleared
    # list) and no error. That is never a complete answer: SourceUnavailable, no record.
    # MCL shares NYMEX with MNG, whose final t+1 bar would let rule (c) affirm MCL missing
    day = date(2026, 11, 4)
    gw, src, slept = make(ct(2026, 11, 5, 19), clock=True)
    con = gw.listings[("MCL", "MCLZ26")].contract.conId
    gw.stall[con] = [day if kept is None else kept] * 3
    runner = PaperRunner(tmp_path / "l.jsonl", src, runner_config(), target_fn=lambda h, p, c: {})
    with pytest.raises(SourceUnavailable, match="timed out"):
        runner.run_date(day)
    assert not (tmp_path / "l.jsonl").exists()
    assert slept == [15.0, 30.0]


def test_one_stalled_request_is_retried_and_the_full_answer_used():
    day = date(2026, 11, 4)
    gw, src, slept = make(ct(2026, 11, 5, 19), clock=True)
    con = gw.listings[("MGC", "MGCZ26")].contract.conId
    gw.stall[con] = [day]  # the day's bar (and the later ones) cut off, once
    ans = src.settlements(day)
    assert ans["MGC"] == {"MGCZ26": ib_price("MGC", "MGCZ26", day)} and slept == [15.0]


def test_error_321_stops_the_request_at_once():
    # N1 (wave 3): ib_async 2.1.0 logs 321 as a warning and lets the request time out; the
    # session sees it through errorEvent and stops without the four retries.
    gw, src, slept = make(ct(2026, 11, 2, 19), clock=True)
    con = gw.listings[("MNQ", "MNQZ26")].contract.conId
    gw.warn_321.add(con)
    with pytest.raises(SourceUnavailable, match="321") as info:
        src.settlements(date(2026, 11, 2))
    assert "gave up" not in str(info.value) and slept == []


def test_refuses_a_gateway_that_swallows_request_errors():
    from forward.ibkr_gateway import IBKRConfigError

    gw = MockGateway(build_listings(FIRST, LAST), {}, now=ct(2026, 11, 2, 19))
    gw.RaiseRequestErrors = False  # an error-ended request would come back as a partial list
    with pytest.raises(IBKRConfigError, match="RaiseRequestErrors"):
        GatewaySession(gw, ConnectionParams.from_env(ENV))


@pytest.mark.parametrize("inst,cid,close", [("MZC", "MZCZ26", 4.25), ("MZL", "MZLZ26", 0.45)])
def test_a_grain_close_in_dollars_breaks_the_cents_convention(inst, cid, close):
    # N7 (wave 3): IB quotes the micro grains in cents (I7 [unverified]); a dollar-level close
    # would be divided by 100 again. A level floor stops the run instead.
    gw, src, _ = make(ct(2026, 11, 2, 19))
    con = gw.listings[(inst, cid)].contract.conId
    orig = gw.reqHistoricalData

    def patched(contract, *a, **k):
        bars = orig(contract, *a, **k)
        return [FakeBar(b.date, close) for b in bars] if contract.conId == con else bars

    gw.reqHistoricalData = patched
    with pytest.raises(ConventionError, match="cents"):
        src.settlements(date(2026, 11, 2))


def test_partial_history_empty_answers_raise_unavailable_never_missing(tmp_path):
    gw, src, slept = make(ct(2026, 11, 2, 19))
    con = gw.listings[("MCL", "MCLZ26")].contract.conId
    gw.bars[con] = {}
    runner = PaperRunner(tmp_path / "l.jsonl", src, runner_config(), target_fn=lambda h, p, c: {})
    with pytest.raises(SourceUnavailable, match="gave up after 3 attempts"):
        runner.run_date(date(2026, 11, 2))
    assert not (tmp_path / "l.jsonl").exists()
    assert slept == [15.0, 30.0]


def test_a_drop_mid_request_reconnects_and_recovers():
    gw, src, slept = make(ct(2026, 11, 2, 19))
    gw.fail["reqHistoricalData"] = [ConnectionError("Socket disconnect")]
    ans = src.settlements(date(2026, 11, 2))
    assert len(ans) == 12
    assert gw.count("connect") == 2 and slept == [15.0]
    assert src.session.disconnects_seen == 1


def test_reconnect_exhaustion_raises_unavailable_and_no_record(tmp_path):
    gw, src, slept = make(ct(2026, 11, 2, 19))
    gw.fail["reqHistoricalData"] = [ConnectionError("Socket disconnect")]
    gw.fail["connect"] = [ConnectionError("refused")] * 5
    runner = PaperRunner(tmp_path / "l.jsonl", src, runner_config(), target_fn=lambda h, p, c: {})
    with pytest.raises(SourceUnavailable):
        runner.run_date(date(2026, 11, 2))
    assert not (tmp_path / "l.jsonl").exists()


@pytest.mark.parametrize(
    "code,text,retried",
    [
        (162, "Historical data request pacing violation", True),
        (354, "Not subscribed to requested market data.", False),
        (10187, "Failed to request historical ticks:No market data permissions", False),
    ],
)
def test_error_codes_retry_or_stop_but_never_yield_a_price(code, text, retried):
    gw, src, slept = make(ct(2026, 11, 2, 19))
    gw.fail["reqHistoricalData"] = [FakeRequestError(1, code, text)]
    if retried:
        assert len(src.settlements(date(2026, 11, 2))) == 12 and slept == [15.0]
    else:
        with pytest.raises(SourceUnavailable, match=str(code)):
            src.settlements(date(2026, 11, 2))


def test_hmds_no_data_is_not_a_price_and_not_missing_without_confirmation():
    day = date(2026, 11, 4)
    gw, src, _ = make(ct(2026, 11, 4, 19), last=day)
    gw.no_data.add(gw.listings[("MZL", "MZLZ26")].contract.conId)
    with pytest.raises(DayNotReady, match="MZL"):
        src.settlements(day)


def test_before_the_cutoff_the_day_is_not_ready():
    day = date(2026, 11, 2)
    gw, src, _ = make(ct(2026, 11, 2, 17, 59))
    with pytest.raises(DayNotReady, match="cutoff"):
        src.settlements(day)
    gw.now = ct(2026, 11, 2, 18, 0)
    assert len(src.settlements(day)) == 12


def test_trade_dates_follow_chicago_not_the_local_calendar():
    # 2026-11-03 06:30 UTC = Nov 2 22:30 in Vancouver = Nov 3 00:30 in Chicago
    now = datetime(2026, 11, 3, 6, 30, tzinfo=UTC)
    assert chicago_date(now) == date(2026, 11, 3)
    assert latest_ready_trade_date(now) == date(2026, 11, 2)
    gw, src, _ = make(now)
    # the open session's partial bar is dated Nov 3; Nov 2's bar is used for Nov 2
    assert src.settlements(date(2026, 11, 2))["MNQ"] == {
        "MNQZ26": ib_price("MNQ", "MNQZ26", date(2026, 11, 2))
    }
    with pytest.raises(DayNotReady):
        src.settlements(date(2026, 11, 3))
    # 15:30 PST on Nov 2 = 17:30 CST: Nov 2 not final yet, latest ready is Friday Oct 30
    assert latest_ready_trade_date(datetime(2026, 11, 2, 23, 30, tzinfo=UTC)) == date(2026, 10, 30)
    with pytest.raises(ConventionError, match="naive"):
        latest_ready_trade_date(datetime(2026, 11, 3, 6, 30))


@pytest.mark.parametrize("bad", [date(2026, 10, 31), datetime(2026, 11, 2, 16, 0, tzinfo=UTC)])
def test_weekend_or_datetime_bar_dates_break_the_convention(bad):
    gw, src, _ = make(ct(2026, 11, 2, 19))
    con = gw.listings[("MNQ", "MNQZ26")].contract.conId
    orig = gw.reqHistoricalData

    def patched(contract, *a, **k):
        bars = orig(contract, *a, **k)
        return bars + [FakeBar(bad, 1.0)] if contract.conId == con else bars

    gw.reqHistoricalData = patched
    with pytest.raises(ConventionError):
        src.settlements(date(2026, 11, 2))


def test_provenance_labels_the_field_and_the_bar_date(tmp_path):
    prov = tmp_path / "prov.jsonl"
    gw, src, _ = make(ct(2026, 11, 2, 19), provenance=prov)
    src.settlements(date(2026, 11, 2))
    lines = [json.loads(x) for x in prov.read_text().splitlines()]
    assert len(lines) == 12
    one = next(x for x in lines if x["instrument"] == "MNG")
    assert one["field"] == "close_last_trade" and one["what_to_show"] == "TRADES"
    assert one["bar_date"] == "2026-11-02" and one["status"] == "price"
    assert "DU" not in prov.read_text() and "4002" not in prov.read_text()


def test_pacer_spaces_historical_requests():
    t = [0.0]
    waits: list[float] = []

    def sleep(s):
        waits.append(s)
        t[0] += s

    pacer = Pacer(1.0, clock=lambda: t[0], sleep=sleep)
    for _ in range(3):
        pacer.wait()
    assert waits == [1.0, 1.0]


@pytest.mark.parametrize(
    "code,text",
    [
        (
            166,
            "HMDS Expired Contract Violation. Historical data is not available for the specified "
            "expired contract.",
        ),
        (162, "Historical Market Data Service error message:HMDS query returned no data: x"),
    ],
)
def test_affirmative_no_data_answers_are_not_retried_and_not_prices(code, text):
    day = date(2026, 11, 4)
    gw, src, slept = make(ct(2026, 11, 4, 19), last=day)
    con = gw.listings[("MZL", "MZLZ26")].contract.conId
    orig = gw.reqHistoricalData

    def patched(contract, *a, **k):
        if contract.conId == con:
            raise FakeRequestError(3, code, text)
        return orig(contract, *a, **k)

    gw.reqHistoricalData = patched
    with pytest.raises(DayNotReady, match="MZL:MZLZ26"):
        src.settlements(day)
    assert slept == []


def test_subscription_errors_stop_at_once():  # facts I4: 10089 "API data requires subscription"
    gw, src, slept = make(ct(2026, 11, 2, 19))
    gw.fail["reqHistoricalData"] = [FakeRequestError(1, 10089, "API data requires subscription")]
    with pytest.raises(SourceUnavailable, match="10089"):
        src.settlements(date(2026, 11, 2))
    assert slept == [] and gw.count("reqHistoricalData") == 1


def test_end_times_use_the_api_utc_format_across_daylight_saving():
    from forward.sources_ibkr import ib_end_of_day

    assert ib_end_of_day(date(2026, 12, 10)) == "20261211-05:59:59"  # CST, UTC-6
    assert ib_end_of_day(date(2026, 7, 10)) == "20260711-04:59:59"  # CDT, UTC-5


def test_client_id_zero_and_bad_ports_are_refused_without_values():
    from forward.ibkr_gateway import IBKRConfigError

    with pytest.raises(IBKRConfigError, match="IBKR_CLIENT_ID") as info:
        ConnectionParams.from_env({**ENV, "IBKR_CLIENT_ID": "0"})
    assert "0" not in str(info.value).replace("IBKR", "")
    with pytest.raises(IBKRConfigError, match="IBKR_GATEWAY_PORT"):
        ConnectionParams.from_env({**ENV, "IBKR_GATEWAY_PORT": "70000"})
    with pytest.raises(IBKRConfigError, match="IBKR_GATEWAY_HOST"):
        ConnectionParams.from_env({k: v for k, v in ENV.items() if k != "IBKR_GATEWAY_HOST"})


def test_socket_errors_never_leak_host_port_or_account():
    gw, src, _ = make(ct(2026, 11, 2, 19))
    msg = "[Errno 111] Connect call failed ('127.0.0.1', 4002)"
    gw.fail["connect"] = [ConnectionRefusedError(msg)] * 3
    with pytest.raises(SourceUnavailable) as info:
        src.settlements(date(2026, 11, 2))
    text = str(info.value)
    assert "127.0.0.1" not in text and "4002" not in text and "<host>" in text


@pytest.mark.parametrize(
    "code,text",
    [
        (354, "Requested market data is not subscribed."),
        (10089, "API data requires subscription"),
        (
            162,
            "Historical Market Data Service error message:No market data permissions for CME FUT",
        ),
    ],
)
def test_without_a_subscription_delayed_data_is_asked_first_then_refusal_is_unavailable(
    tmp_path, code, text
):  # factcheck C1: never assume failure, never Missing, a clear message, no record
    from forward.ibkr_gateway import SubscriptionNeeded

    gw, src, slept = make(ct(2026, 11, 2, 19))
    gw.fail["reqHistoricalData"] = [FakeRequestError(5, code, text)]
    runner = PaperRunner(tmp_path / "l.jsonl", src, runner_config(), target_fn=lambda h, p, c: {})
    with pytest.raises(SubscriptionNeeded, match="market data subscription needed") as info:
        runner.run_date(date(2026, 11, 2))
    assert str(code) in str(info.value)
    names = [n for n, _ in gw.calls]
    assert names.index("reqMarketDataType") < names.index("reqHistoricalData")
    assert ("reqMarketDataType", {"type": 3}) in gw.calls
    assert slept == [] and gw.count("reqHistoricalData") == 1  # not retried
    assert not (tmp_path / "l.jsonl").exists()


def test_with_delayed_data_served_the_day_is_delivered_normally():
    gw, src, _ = make(ct(2026, 11, 2, 19))
    assert len(src.settlements(date(2026, 11, 2))) == 12
    assert gw.calls[1] == ("reqMarketDataType", {"type": 3})
