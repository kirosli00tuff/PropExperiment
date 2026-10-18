"""forward/sources_alpaca.py on mocks and hand-written fixtures (Stage E.24 Part C). No network."""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import pytest

from forward import sources_alpaca as sa
from forward.etf_bars import (
    EtfBar,
    EtfBarSource,
    Missing,
    NotReady,
    SourceUnavailable,
    etf_history_sha256,
    load_etf_warmup,
)

NY = ZoneInfo("America/New_York")
VAN = ZoneInfo("America/Vancouver")

# A week of sessions (no holidays): Wed 2026-11-04 is the trade date in most tests.
MON, TUE, WED = date(2026, 11, 2), date(2026, 11, 3), date(2026, 11, 4)
FRI_PREV = date(2026, 10, 30)
AFTER_WED = datetime.combine(WED, time(21, 0), NY)  # well after any cutoff on WED


# --- fakes mirroring alpaca-py 0.44.0 shapes --------------------------------------------------


@dataclass(frozen=True)
class FakeBar:
    timestamp: datetime
    close: float


@dataclass(frozen=True)
class FakeBarSet:
    data: dict


@dataclass(frozen=True)
class FakeRequest:
    symbol_or_symbols: object
    start: datetime
    end: datetime
    adjustment: str
    feed: str


def fake_factory(**kwargs):
    return FakeRequest(**kwargs)


@dataclass(frozen=True)
class FakeCARequest:
    symbols: list
    start: date
    end: date


def fake_ca_factory(**kwargs):
    return FakeCARequest(**kwargs)


def _named(item: dict) -> set:
    return {v for k, v in item.items() if k.endswith("symbol")}


@dataclass
class FakeCAClient:
    """Mirrors CorporateActionsClient(raw_data=True): {type_plural: [raw record, ...]}."""

    data: dict = field(default_factory=dict)
    fail: list = field(default_factory=list)
    requests: list = field(default_factory=list)

    def get_corporate_actions(self, request_params):
        self.requests.append(request_params)
        if self.fail:
            raise self.fail.pop(0)
        out = {}
        for key, items in self.data.items():
            keep = [
                i for i in items
                if _named(i) & set(request_params.symbols)
                and request_params.start
                <= date.fromisoformat(i.get("ex_date") or i["effective_date"])
                <= request_params.end
            ]
            if keep:
                out[key] = keep
        return out


class ProcessDateCAClient(FakeCAClient):
    """Filters on process_date, as the endpoint does (its start/end is a process_date
    interval, pages/alpaca/ref_us_corporateactions-1.md)."""

    def get_corporate_actions(self, request_params):
        self.requests.append(request_params)
        if self.fail:
            raise self.fail.pop(0)
        out = {}
        for key, items in self.data.items():
            keep = [
                i for i in items
                if _named(i) & set(request_params.symbols)
                and request_params.start
                <= date.fromisoformat(i["process_date"])
                <= request_params.end
            ]
            if keep:
                out[key] = keep
        return out


def processed(item: dict, day: date) -> dict:
    return item | {"process_date": day.isoformat()}


def div(symbol: str, ex: date, rate: float, special: bool = False) -> dict:
    return {
        "symbol": symbol, "cusip": "000000000", "rate": rate, "special": special,
        "foreign": False, "process_date": ex.isoformat(), "ex_date": ex.isoformat(),
        "record_date": ex.isoformat(), "payable_date": ex.isoformat(),
    }


def split(symbol: str, ex: date, new: float, old: float) -> dict:
    return {
        "symbol": symbol, "cusip": "000000000", "new_rate": new, "old_rate": old,
        "process_date": ex.isoformat(), "ex_date": ex.isoformat(),
    }


class FakeHTTPError(Exception):
    def __init__(self, status: int, headers: dict | None = None):
        super().__init__(f"HTTP {status}")
        self.status_code = status
        self.response = type("R", (), {"headers": headers or {}, "status_code": status})()


def ny_midnight_utc(day: date) -> datetime:
    """Alpaca stamps a daily bar at 00:00 America/New_York of its session, sent as UTC."""
    return datetime.combine(day, time(0), NY).astimezone(UTC)


def table_responder(tables: dict, drop: dict | None = None):
    """tables: {adjustment: {symbol: {date: close}}}; drop: {(adjustment, symbol): {dates}} that
    a multi-symbol response leaves out (to fake truncation)."""
    drop = drop or {}

    def respond(req: FakeRequest):
        symbols = (
            [req.symbol_or_symbols]
            if isinstance(req.symbol_or_symbols, str)
            else list(req.symbol_or_symbols)
        )
        lo, hi = req.start.astimezone(NY).date(), req.end.astimezone(NY).date()
        out = {}
        for sym in symbols:
            series = tables[req.adjustment].get(sym, {})
            dropped = drop.get((req.adjustment, sym), set()) if len(symbols) > 1 else set()
            bars = [
                FakeBar(ny_midnight_utc(d), c)
                for d, c in sorted(series.items())
                if lo <= d <= hi and d not in dropped
            ]
            if bars:
                out[sym] = bars
        return FakeBarSet(out)

    return respond


@dataclass
class FakeDataClient:
    respond: object
    requests: list = field(default_factory=list)

    def get_stock_bars(self, request_params):
        self.requests.append(request_params)
        return self.respond(request_params)


class Clock:
    def __init__(self, now: datetime):
        self.now = now

    def __call__(self) -> datetime:
        return self.now


def make_source(client, symbols=("QQQ", "TLT", "BIL"), now=AFTER_WED, ca=None, **kw):
    """A source whose monotonic clock moves 10 s per reading, so pacing never sleeps and every
    recorded sleep is a retry backoff."""
    sleeps: list[float] = []
    ticks = itertools.count(0.0, 10.0)
    src = sa.AlpacaEtfSource(
        symbols,
        client,
        request_factory=fake_factory,
        ca_client=ca if ca is not None else FakeCAClient(),
        ca_request_factory=fake_ca_factory,
        clock=Clock(now),
        sleep=sleeps.append,
        monotonic=lambda: next(ticks),
        **kw,
    )
    return src, sleeps


def flat_tables(symbols=("QQQ", "TLT", "BIL"), days=(FRI_PREV, MON, TUE, WED)):
    base = {"QQQ": 500.0, "TLT": 90.0, "BIL": 91.5}
    raw = {s: {d: base[s] + i for i, d in enumerate(days)} for s in symbols}
    return {"raw": raw, "all": {s: dict(v) for s, v in raw.items()}}


# --- time zone and cutoff ------------------------------------------------------------------


def test_session_date_uses_new_york_not_local_or_utc():
    ts = datetime(2026, 11, 4, 5, 0, tzinfo=UTC)  # 00:00 EST on Nov 4
    assert ts.astimezone(VAN).date() == TUE  # the ThinkPad's local date is the day before
    assert sa.session_date(ts) == WED
    summer = datetime(2026, 7, 1, 4, 0, tzinfo=UTC)  # 00:00 EDT on Jul 1
    assert sa.session_date(summer) == date(2026, 7, 1)
    with pytest.raises(ValueError, match="time zone"):
        sa.session_date(datetime(2026, 11, 4, 5, 0))


def test_cutoff_is_new_york_close_plus_delay():
    cut = sa.bar_cutoff(WED)
    assert cut.tzinfo is not None
    assert cut.astimezone(NY).date() == WED
    assert cut.astimezone(NY).time() >= time(16, 0)
    assert cut == datetime.combine(WED, sa.SESSION_CLOSE_NY, NY) + sa.BAR_CUTOFF_DELAY


def test_request_before_the_close_is_not_ready_and_calls_nothing():
    client = FakeDataClient(table_responder(flat_tables()))
    before = datetime.combine(WED, time(15, 59), NY)
    src, _ = make_source(client, now=before)
    with pytest.raises(NotReady):
        src.bars(WED)
    assert client.requests == []
    just_before = sa.bar_cutoff(WED) - timedelta(seconds=1)
    src, _ = make_source(client, now=just_before)
    with pytest.raises(NotReady):
        src.bars(WED)
    assert client.requests == []


def test_local_evening_is_already_the_next_new_york_date():
    # 22:30 PT on Wed is 01:30 ET on Thu: Wed's session is over; Thu's has not started.
    late = datetime.combine(WED, time(22, 30), VAN)
    client = FakeDataClient(table_responder(flat_tables()))
    src, _ = make_source(client, now=late)
    assert sa.latest_ready_session(late) == WED
    day = src.bars(WED)
    assert set(day) == {"QQQ", "TLT", "BIL"}
    with pytest.raises(NotReady):
        src.bars(date(2026, 11, 5))


def test_latest_ready_session_skips_weekends_and_declared_closed_days():
    sat_noon = datetime(2026, 11, 7, 12, 0, tzinfo=NY)
    assert sa.latest_ready_session(sat_noon) == date(2026, 11, 6)
    mon_morning = datetime(2026, 11, 9, 10, 0, tzinfo=NY)
    assert sa.latest_ready_session(mon_morning) == date(2026, 11, 6)
    thanks_eve = datetime(2026, 11, 27, 10, 0, tzinfo=NY)
    assert sa.latest_ready_session(thanks_eve, closed={date(2026, 11, 26)}) == date(2026, 11, 25)


def test_naive_clock_is_refused():
    client = FakeDataClient(table_responder(flat_tables()))
    src, _ = make_source(client, now=datetime(2026, 11, 4, 21, 0))
    with pytest.raises(ValueError, match="time zone"):
        src.bars(WED)


def test_weekend_or_declared_closed_date_is_not_a_session():
    client = FakeDataClient(table_responder(flat_tables()))
    src, _ = make_source(client, closed_dates={TUE})
    with pytest.raises(sa.NotASession):
        src.bars(date(2026, 11, 7))
    with pytest.raises(sa.NotASession):
        src.bars(TUE)
    assert client.requests == []


# --- the daily fetch -----------------------------------------------------------------------


def test_daily_fetch_requests_raw_bars_and_corporate_actions_never_all():
    client = FakeDataClient(table_responder(flat_tables()))
    ca = FakeCAClient()
    src, _ = make_source(client, ca=ca)
    assert isinstance(src, EtfBarSource)
    day = src.bars(WED)
    assert day["QQQ"] == EtfBar(503.0, 503.0 / 502.0 - 1, TUE)
    assert [r.adjustment for r in client.requests] == ["raw"]
    assert {r.feed for r in client.requests} == {sa.DATA_FEED}
    for r in client.requests:
        assert r.symbol_or_symbols == ["BIL", "QQQ", "TLT"]
        assert r.start.tzinfo is not None and r.end.tzinfo is not None
        assert r.end.astimezone(NY).date() == WED
        assert r.start.astimezone(NY).date() == WED - timedelta(days=sa.DAILY_WINDOW_DAYS)
        assert not hasattr(r, "limit")
    assert len(ca.requests) == 1
    assert ca.requests[0].symbols == ["BIL", "QQQ", "TLT"]
    # the endpoint's interval is process_date: a wide range, ex_date filtered locally
    assert ca.requests[0].end == WED + timedelta(days=sa.CA_MARGIN_DAYS)
    assert ca.requests[0].start == WED - timedelta(
        days=sa.DAILY_WINDOW_DAYS + sa.CA_MARGIN_DAYS
    )


def test_split_day_return_uses_the_split_ratio():
    # UNG-style 1-for-4 reverse split ex WED: raw jumps 5.00 -> 20.40; k = new/old = 1/4.
    tables = {"raw": {"UNG": {MON: 5.10, TUE: 5.00, WED: 20.40}}}
    ca = FakeCAClient({"reverse_splits": [split("UNG", WED, 1.0, 4.0)]})
    src, _ = make_source(FakeDataClient(table_responder(tables)), symbols=["UNG"], ca=ca)
    fetch = src.fetch_day(WED)
    bar = fetch.bars["UNG"]
    assert bar.close == 20.40  # raw, unadjusted close of the session
    assert bar.ret == pytest.approx(0.25 * 20.40 / 5.00 - 1)  # +2%, not +308%
    assert bar.prev_date == TUE
    assert [a.kind for a in fetch.applied["UNG"]] == ["reverse_split"]


def test_distribution_ex_date_return_includes_the_distribution():
    tables = {"raw": {"TLT": {MON: 90.10, TUE: 90.00, WED: 89.80}}}
    ca = FakeCAClient({"cash_dividends": [div("TLT", WED, 0.30)]})
    src, _ = make_source(FakeDataClient(table_responder(tables)), symbols=["TLT"], ca=ca)
    bar = src.bars(WED)["TLT"]
    assert bar.close == 89.80
    assert bar.ret == pytest.approx((89.80 + 0.30) / 90.00 - 1)
    assert bar.ret > 0 > 89.80 / 90.00 - 1  # the raw return would have been negative


def test_split_and_dividend_on_the_same_day():
    # 2-for-1 forward split and a 0.10 dividend per post-split share, both ex WED.
    tables = {"raw": {"QQQ": {MON: 99.0, TUE: 100.0, WED: 50.5}}}
    ca = FakeCAClient(
        {"forward_splits": [split("QQQ", WED, 2.0, 1.0)], "cash_dividends": [div("QQQ", WED, 0.10)]}
    )
    src, _ = make_source(FakeDataClient(table_responder(tables)), symbols=["QQQ"], ca=ca)
    assert src.bars(WED)["QQQ"].ret == pytest.approx(2.0 * (50.5 + 0.10) / 100.0 - 1)


def test_special_dividend_and_capital_gains_distribution_are_added():
    tables = {"raw": {"GLD": {MON: 200.0, TUE: 200.0, WED: 196.0}}}
    ca = FakeCAClient(
        {
            "cash_dividends": [div("GLD", WED, 1.00, special=True)],
            "capital_gains_distributions": [
                {"symbol": "GLD", "cusip": "0", "long_term_rate": 2.0, "short_term_rate": 0.5,
                 "currency": "USD", "ex_date": WED.isoformat(), "process_date": WED.isoformat()}
            ],
        }
    )
    src, _ = make_source(FakeDataClient(table_responder(tables)), symbols=["GLD"], ca=ca)
    fetch = src.fetch_day(WED)
    assert fetch.bars["GLD"].ret == pytest.approx((196.0 + 1.00 + 2.5) / 200.0 - 1)
    kinds = sorted(a.kind for a in fetch.applied["GLD"])
    assert kinds == ["capital_gains_distribution", "cash_dividend"]


def capgain(symbol: str, ex: date, **legs) -> dict:
    return {"symbol": symbol, "cusip": "0", "ex_date": ex.isoformat(),
            "process_date": ex.isoformat(), **legs}


def test_capital_gains_with_one_leg_and_bad_records():
    tables = {"raw": {"GLD": {MON: 200.0, TUE: 200.0, WED: 199.0}}}
    ok = FakeCAClient({"capital_gains_distributions": [capgain("GLD", WED, short_term_rate=0.4)]})
    src, _ = make_source(FakeDataClient(table_responder(tables)), symbols=["GLD"], ca=ok)
    assert src.bars(WED)["GLD"].ret == pytest.approx((199.0 + 0.4) / 200.0 - 1)
    legless = FakeCAClient({"capital_gains_distributions": [capgain("GLD", WED, rate=0.4)]})
    src, _ = make_source(FakeDataClient(table_responder(tables)), symbols=["GLD"], ca=legless)
    with pytest.raises(SourceUnavailable, match="long_term_rate"):
        src.bars(WED)
    cad = div("GLD", WED, 0.4) | {"currency": "CAD"}
    src, _ = make_source(
        FakeDataClient(table_responder(tables)), ["GLD"], ca=FakeCAClient({"cash_dividends": [cad]})
    )
    with pytest.raises(SourceUnavailable, match="USD"):
        src.bars(WED)


def test_action_processed_after_its_ex_date_is_found_by_the_wide_window():
    # FCF-style: ex WED, processed (and so listed by process_date) two weeks later.
    tables = {"raw": {"TLT": {MON: 90.10, TUE: 90.00, WED: 89.80}}}
    late = processed(div("TLT", WED, 0.30), WED + timedelta(days=15))
    ca = ProcessDateCAClient({"cash_dividends": [late]})
    src, _ = make_source(FakeDataClient(table_responder(tables)), symbols=["TLT"], ca=ca)
    assert src.bars(WED)["TLT"].ret == pytest.approx((89.80 + 0.30) / 90.00 - 1)


def test_bil_monthly_dividend_counts_only_on_its_ex_date():
    days = (FRI_PREV, MON, TUE, WED)
    tables = {"raw": {"BIL": dict(zip(days, [91.50, 91.25, 91.26, 91.27], strict=True))}}
    ca = FakeCAClient({"cash_dividends": [div("BIL", MON, 0.30)]})
    mon_evening = datetime.combine(MON, time(21, 0), NY)
    src, _ = make_source(FakeDataClient(table_responder(tables)), ["BIL"], mon_evening, ca)
    assert src.bars(MON)["BIL"].ret == pytest.approx((91.25 + 0.30) / 91.50 - 1)
    src, _ = make_source(FakeDataClient(table_responder(tables)), ["BIL"], AFTER_WED, ca)
    assert src.bars(WED)["BIL"].ret == pytest.approx(91.27 / 91.26 - 1)


def test_ex_date_inside_a_gap_is_applied_to_the_return_spanning_the_gap():
    tables = {"raw": {"TLT": {FRI_PREV: 90.0, WED: 89.9}}}  # no bars MON, TUE
    ca = FakeCAClient({"cash_dividends": [div("TLT", MON, 0.25)]})
    src, _ = make_source(FakeDataClient(table_responder(tables)), symbols=["TLT"], ca=ca)
    bar = src.bars(WED)["TLT"]
    assert bar.prev_date == FRI_PREV
    assert bar.ret == pytest.approx((89.9 + 0.25) / 90.0 - 1)


def test_empty_corporate_actions_response_gives_raw_returns():
    src, _ = make_source(FakeDataClient(table_responder(flat_tables())), ca=FakeCAClient({}))
    fetch = src.fetch_day(WED)
    assert fetch.bars["TLT"].ret == pytest.approx(93.0 / 92.0 - 1)
    assert fetch.applied == {} and fetch.flags == {}


def test_other_corporate_action_types_are_flags_not_returns():
    spin = {
        "source_symbol": "QQQ", "source_cusip": "0", "source_rate": 1.0, "new_symbol": "NEWQ",
        "new_cusip": "1", "new_rate": 0.1, "process_date": WED.isoformat(),
        "ex_date": WED.isoformat(),
    }
    ca = FakeCAClient({"spin_offs": [spin]})
    src, _ = make_source(FakeDataClient(table_responder(flat_tables())), ca=ca)
    fetch = src.fetch_day(WED)
    assert fetch.flags == {"QQQ": ("spin_off ex_date 2026-11-04",)}
    assert fetch.bars["QQQ"].ret == pytest.approx(503.0 / 502.0 - 1)


def test_malformed_corporate_action_raises_unavailable():
    bad = split("QQQ", WED, 2.0, 0.0)
    src, _ = make_source(
        FakeDataClient(table_responder(flat_tables())), ca=FakeCAClient({"forward_splits": [bad]})
    )
    with pytest.raises(SourceUnavailable, match="old_rate"):
        src.bars(WED)


def test_corporate_actions_api_returns_published_actions_for_a_range():
    ca = FakeCAClient(
        {
            "cash_dividends": [div("TLT", MON, 0.25), div("XYZ", MON, 9.0)],
            "reverse_splits": [split("UNG", TUE, 1.0, 4.0)],
        }
    )
    src, _ = make_source(FakeDataClient(table_responder(flat_tables())), ca=ca)
    got = src.corporate_actions(FRI_PREV, WED, symbols=["TLT", "UNG"])
    assert [(a.symbol, a.kind, a.ex_date) for a in got.booked] == [
        ("TLT", "cash_dividend", MON),
        ("UNG", "reverse_split", TUE),
    ]
    assert got.booked[1].ratio == 0.25 and got.booked[0].amount == 0.25
    assert ca.requests[-1].symbols == ["TLT", "UNG"]


def test_corporate_actions_cover_every_ex_date_in_a_long_span_whatever_the_process_date():
    """C4a S1: the runner asks for the actions over (prev, t] however long; the endpoint
    filters on process_date, so the source pads it and filters ex_date locally."""
    start, end = date(2025, 9, 1), WED  # more than a year
    lag = timedelta(days=15)
    first = processed(div("TLT", start, 0.20), start + lag)  # ex == start: inclusive
    last = processed(div("TLT", end, 0.30), end + lag)  # processed after `end`
    early = processed(split("UNG", date(2026, 3, 2), 1.0, 4.0), date(2026, 2, 25))
    before = processed(div("TLT", start - timedelta(days=1), 9.0), start + timedelta(days=3))
    after = processed(div("TLT", end + timedelta(days=1), 9.0), end)
    ca = ProcessDateCAClient(
        {"cash_dividends": [first, last, before, after], "reverse_splits": [early]}
    )
    src, _ = make_source(FakeDataClient(table_responder(flat_tables())), ca=ca)
    got = src.corporate_actions(start, end, symbols=["TLT", "UNG"])
    assert [(a.symbol, a.kind, a.ex_date) for a in got.booked] == [
        ("TLT", "cash_dividend", start),
        ("TLT", "cash_dividend", end),
        ("UNG", "reverse_split", date(2026, 3, 2)),
    ]
    assert [(a.ex_date, a.amount) for a in got.between("TLT", start, end)] == [(end, 0.30)]
    margin = timedelta(days=sa.CA_MARGIN_DAYS)
    assert (ca.requests[-1].start, ca.requests[-1].end) == (start - margin, end + margin)


def test_previous_bar_may_be_several_sessions_back():
    tables = flat_tables()
    for adj in ("raw", "all"):
        del tables[adj]["TLT"][TUE]
        del tables[adj]["TLT"][MON]
    src, _ = make_source(FakeDataClient(table_responder(tables)))
    assert src.bars(WED)["TLT"].prev_date == FRI_PREV


def test_missing_symbol_is_confirmed_by_a_single_symbol_request():
    tables = flat_tables()
    for adj in ("raw", "all"):
        del tables[adj]["TLT"][WED]  # a halted ETF: earlier bars, none on WED
    client = FakeDataClient(table_responder(tables))
    src, _ = make_source(client)
    fetch = src.fetch_day(WED)
    assert set(fetch.bars) == {"QQQ", "BIL"}
    assert isinstance(fetch.missing["TLT"], Missing)
    assert "TLT" in fetch.missing["TLT"].reason
    day = src.bars(WED)
    assert set(day) == {"QQQ", "BIL"}
    confirm = [r for r in client.requests if r.symbol_or_symbols == ["TLT"]]
    assert confirm and confirm[0].adjustment == "raw"


def test_truncated_multi_symbol_response_raises_unavailable():
    tables = flat_tables()
    drop = {("raw", "TLT"): {WED}, ("all", "TLT"): {WED}}  # cut off in the multi response only
    src, _ = make_source(FakeDataClient(table_responder(tables, drop)))
    with pytest.raises(SourceUnavailable, match="TLT"):
        src.bars(WED)


def test_missing_day_when_no_symbol_has_the_session_after_the_cutoff():
    tables = flat_tables(days=(FRI_PREV, MON, TUE))
    client = FakeDataClient(table_responder(tables))
    src, _ = make_source(client)
    answer = src.bars(WED)
    assert isinstance(answer, Missing)
    assert WED.isoformat() in answer.reason


def test_all_empty_window_raises_unavailable_not_a_missing_day():
    """C4a S3: no bar for any symbol on any date of the window affirms nothing about t."""
    client = FakeDataClient(table_responder({"raw": {}}))
    ca = FakeCAClient()
    src, _ = make_source(client, ca=ca)
    with pytest.raises(SourceUnavailable, match="empty"):
        src.bars(WED)
    assert len(client.requests) == 1 and ca.requests == []


def test_return_spans_a_gap_longer_than_the_request_window():
    """C4a S1: TLT's previous bar is 30 days back (outside the 21-day window), with a
    dividend inside the gap but before the daily span: one wider single-symbol request finds
    prev, a corporate-actions request over (prev, t] finds the dividend."""
    gap_from = date(2026, 10, 5)  # Mon; TLT has no bar after it until WED
    ex = date(2026, 10, 7)  # inside the gap, before WED - DAILY_WINDOW_DAYS
    assert gap_from < WED - timedelta(days=sa.DAILY_WINDOW_DAYS)
    tables = flat_tables()
    tables["raw"]["TLT"] = {date(2026, 10, 2): 89.0, gap_from: 90.0, WED: 88.0}
    dividend = processed(div("TLT", ex, 0.40), ex + timedelta(days=15))
    ca = ProcessDateCAClient({"cash_dividends": [dividend]})
    client = FakeDataClient(table_responder(tables))
    src, _ = make_source(client, ca=ca)
    fetch = src.fetch_day(WED)
    assert fetch.bars["TLT"] == EtfBar(88.0, (88.0 + 0.40) / 90.0 - 1, gap_from)
    assert [(a.kind, a.ex_date) for a in fetch.applied["TLT"]] == [("cash_dividend", ex)]
    assert "TLT" not in fetch.missing
    wide = [r for r in client.requests if r.symbol_or_symbols == ["TLT"]]
    assert len(wide) == 1 and wide[0].adjustment == "raw"
    assert wide[0].start.astimezone(NY).date() == sa.WARMUP_FIRST_DATE
    assert wide[0].end == client.requests[0].end
    margin = timedelta(days=sa.CA_MARGIN_DAYS)
    assert ca.requests[-1].symbols == ["TLT"]
    assert (ca.requests[-1].start, ca.requests[-1].end) == (gap_from - margin, WED + margin)
    assert fetch.bars["QQQ"].ret == pytest.approx(503.0 / 502.0 - 1)


def test_symbol_with_no_earlier_bar_since_the_first_date_gets_its_close_without_a_return():
    """C4a S1: t's raw close is delivered whatever the window; with no earlier bar at all the
    bar is the first row of the symbol's history (ret and prev_date None)."""
    tables = flat_tables()
    tables["raw"]["TLT"] = {WED: 90.0}
    client = FakeDataClient(table_responder(tables))
    src, _ = make_source(client)
    fetch = src.fetch_day(WED)
    assert fetch.bars["TLT"] == EtfBar(90.0) and "TLT" not in fetch.missing
    assert "TLT" not in fetch.applied
    wide = [r for r in client.requests if r.symbol_or_symbols == ["TLT"]]
    assert len(wide) == 1 and wide[0].start.astimezone(NY).date() == sa.WARMUP_FIRST_DATE


def test_wider_request_finding_bars_the_window_lacked_raises_unavailable():
    tables = flat_tables()
    drop = {("raw", "TLT"): {FRI_PREV, MON, TUE}}  # left out of the multi response only
    src, _ = make_source(FakeDataClient(table_responder(tables, drop)))
    with pytest.raises(SourceUnavailable, match="TLT"):
        src.bars(WED)


def test_wider_request_disagreeing_on_t_raises_unavailable():
    tables = flat_tables()
    tables["raw"]["TLT"] = {WED: 90.0}
    good = table_responder(tables)

    def respond(req):
        out = good(req)
        if req.symbol_or_symbols == ["TLT"]:
            out.data["TLT"] = [FakeBar(ny_midnight_utc(WED), 91.0)]
        return out

    src, _ = make_source(FakeDataClient(respond))
    with pytest.raises(SourceUnavailable, match="TLT"):
        src.bars(WED)


@pytest.mark.parametrize("bad", [0.0, -3.0, float("nan")])
def test_non_positive_or_nan_close_raises_unavailable(bad):
    tables = flat_tables()
    tables["raw"]["QQQ"][WED] = bad
    src, _ = make_source(FakeDataClient(table_responder(tables)))
    with pytest.raises(SourceUnavailable, match="QQQ"):
        src.bars(WED)


def test_duplicate_session_in_a_response_raises_unavailable():
    good = table_responder(flat_tables())

    def respond(req):
        out = good(req)
        out.data["QQQ"].append(out.data["QQQ"][-1])
        return out

    src, _ = make_source(FakeDataClient(respond))
    with pytest.raises(SourceUnavailable, match="duplicate"):
        src.bars(WED)


def test_symbols_come_from_the_caller_and_are_validated():
    client = FakeDataClient(table_responder(flat_tables()))
    with pytest.raises(ValueError):
        sa.AlpacaEtfSource([], client, request_factory=fake_factory)
    with pytest.raises(ValueError):
        sa.AlpacaEtfSource(["QQQ", "QQQ"], client, request_factory=fake_factory)
    with pytest.raises(ValueError):
        sa.AlpacaEtfSource(["qqq"], client, request_factory=fake_factory)


# --- retries, rate limits, transport errors ------------------------------------------------


def flaky(responder, failures):
    """Raise the given exceptions on the first calls, then answer normally."""
    queue = list(failures)

    def respond(req):
        if queue:
            raise queue.pop(0)
        return responder(req)

    return respond


def test_rate_limit_then_recovery():
    good = table_responder(flat_tables())
    client = FakeDataClient(flaky(good, [FakeHTTPError(429), FakeHTTPError(429)]))
    src, sleeps = make_source(client)
    day = src.bars(WED)
    assert set(day) == {"QQQ", "TLT", "BIL"}
    assert len(sleeps) == 2 and sleeps[0] > 0 and sleeps[1] > sleeps[0]


def test_rate_limit_reset_header_is_honoured_within_the_cap():
    good = table_responder(flat_tables())
    reset = int(AFTER_WED.timestamp()) + 7
    err = FakeHTTPError(429, {"X-RateLimit-Reset": str(reset)})
    src, sleeps = make_source(FakeDataClient(flaky(good, [err])))
    src.bars(WED)
    assert sleeps[0] == pytest.approx(7.0, abs=1.0)


def test_exhausted_retries_raise_unavailable():
    always = FakeDataClient(lambda req: (_ for _ in ()).throw(FakeHTTPError(503)))
    src, sleeps = make_source(always)
    with pytest.raises(SourceUnavailable, match="503"):
        src.bars(WED)
    assert len(always.requests) == sa.MAX_ATTEMPTS
    assert len(sleeps) == sa.MAX_ATTEMPTS - 1
    assert max(sleeps) <= sa.MAX_BACKOFF_SECONDS


@pytest.mark.parametrize("exc", [ConnectionError("reset"), TimeoutError("read timed out")])
def test_transport_errors_are_retried(exc):
    good = table_responder(flat_tables())
    src, sleeps = make_source(FakeDataClient(flaky(good, [exc])))
    assert set(src.bars(WED)) == {"QQQ", "TLT", "BIL"}
    assert len(sleeps) == 1


def test_client_errors_are_not_retried():
    client = FakeDataClient(lambda req: (_ for _ in ()).throw(FakeHTTPError(403)))
    src, sleeps = make_source(client)
    with pytest.raises(SourceUnavailable, match="403"):
        src.bars(WED)
    assert len(client.requests) == 1 and sleeps == []


def test_empty_body_from_the_sdk_is_unavailable_not_missing():
    # alpaca-py returns None for an empty body and then fails inside its pagination loop.
    def respond(req):
        raise AttributeError("'NoneType' object has no attribute 'get'")

    src, _ = make_source(FakeDataClient(respond))
    with pytest.raises(SourceUnavailable):
        src.bars(WED)


def test_requests_are_paced_to_the_rate_limit():
    ticks = iter([0.0, 0.01, 0.02, 0.03, 0.04, 0.05])
    sleeps: list[float] = []
    src = sa.AlpacaEtfSource(
        ["QQQ"],
        FakeDataClient(table_responder(flat_tables(symbols=("QQQ",)))),
        request_factory=fake_factory,
        ca_client=FakeCAClient(),
        ca_request_factory=fake_ca_factory,
        clock=Clock(AFTER_WED),
        sleep=sleeps.append,
        monotonic=lambda: next(ticks),
    )
    src.bars(WED)
    assert sleeps and all(s <= sa.MIN_REQUEST_INTERVAL_S for s in sleeps)


# --- pagination ----------------------------------------------------------------------------


class PagingClient:
    """Mimics alpaca-py's _get_marketdata: follow next_page_token, merge pages by symbol."""

    def __init__(self, tables, page_size=2, fail_on_page=None):
        self.respond = table_responder(tables)
        self.page_size = page_size
        self.fail_on_page = fail_on_page
        self.requests: list = []
        self.pages_served = 0

    def get_stock_bars(self, request_params):
        self.requests.append(request_params)
        full = self.respond(request_params).data
        flat = [(s, b) for s in sorted(full) for b in full[s]]
        pages = [flat[i : i + self.page_size] for i in range(0, len(flat), self.page_size)]
        merged: dict = {}
        token = 0
        while True:
            if self.fail_on_page is not None and token == self.fail_on_page:
                raise FakeHTTPError(500)
            self.pages_served += 1
            for s, b in pages[token] if pages else []:
                merged.setdefault(s, []).append(b)
            token += 1
            if token >= len(pages):
                break
        return FakeBarSet(merged)


def test_multi_page_response_is_assembled_completely():
    client = PagingClient(flat_tables(), page_size=3)
    src, _ = make_source(client)
    day = src.bars(WED)
    assert set(day) == {"QQQ", "TLT", "BIL"}
    assert client.pages_served >= 4


def test_failure_mid_pagination_raises_unavailable():
    client = PagingClient(flat_tables(), page_size=3, fail_on_page=2)
    src, _ = make_source(client)
    with pytest.raises(SourceUnavailable, match="500"):
        src.bars(WED)


# --- warm-up -------------------------------------------------------------------------------


def warm_tables():
    days = [date(2024, 3, 1), date(2024, 3, 4), date(2024, 3, 5), date(2024, 3, 6)]
    raw = {
        "QQQ": dict(zip(days, [440.0, 442.0, 438.0, 441.0], strict=True)),
        "BIL": dict(zip(days, [91.40, 91.41, 91.42, 91.43], strict=True)),
        "USO": {days[0]: 75.0, days[1]: 76.0, days[3]: 77.0},  # no bar on Mar 5 (halt)
    }
    adj = {s: {d: c * 0.98 for d, c in v.items()} for s, v in raw.items()}
    return {"raw": raw, "all": adj}, days


def test_warmup_builds_rows_one_fetch_per_adjustment(tmp_path):
    tables, days = warm_tables()
    client = FakeDataClient(table_responder(tables))
    start = date(2024, 3, 7)
    src, _ = make_source(client, symbols=["QQQ", "BIL", "USO"], now=AFTER_WED)
    result = src.fetch_warmup(start)
    multi = [r for r in client.requests if len(r.symbol_or_symbols) == 3]
    assert [r.adjustment for r in multi] == ["raw"]
    assert multi[0].start.astimezone(NY).date() == sa.WARMUP_FIRST_DATE
    assert multi[0].end.astimezone(NY).date() == start - timedelta(days=1)
    assert [r.date for r in result.rows] == days
    assert result.first_date == {"BIL": days[0], "QQQ": days[0], "USO": days[0]}
    assert result.row_count == {"BIL": 4, "QQQ": 4, "USO": 3}
    assert result.rows[0].bars["QQQ"] == EtfBar(440.0)
    assert result.rows[1].bars["QQQ"].ret == pytest.approx(442.0 / 440.0 - 1)
    assert "USO" not in result.rows[2].bars
    assert result.rows[3].bars["USO"].prev_date == days[1]
    assert result.sha256 == etf_history_sha256(result.rows)
    path = tmp_path / "warm_f2.jsonl"
    assert sa.write_warmup(result, path) == result.sha256
    assert load_etf_warmup(path) == result.rows


def test_warmup_uses_the_same_formula_with_corporate_actions():
    tables, days = warm_tables()
    ca = FakeCAClient(
        {
            "cash_dividends": [div("QQQ", days[1], 0.5)],
            "forward_splits": [split("BIL", days[2], 2.0, 1.0)],
        }
    )
    src, _ = make_source(
        FakeDataClient(table_responder(tables)), symbols=["QQQ", "BIL"], ca=ca
    )
    result = src.fetch_warmup(date(2024, 3, 7))
    margin = timedelta(days=sa.CA_MARGIN_DAYS)
    assert ca.requests[0].start == sa.WARMUP_FIRST_DATE - margin
    assert ca.requests[0].end == days[3] + margin
    assert result.rows[1].bars["QQQ"].ret == pytest.approx((442.0 + 0.5) / 440.0 - 1)
    assert result.rows[2].bars["QQQ"].ret == pytest.approx(438.0 / 442.0 - 1)
    assert result.rows[2].bars["BIL"].ret == pytest.approx(2.0 * 91.42 / 91.41 - 1)
    assert [a.kind for a in result.corporate_actions.booked] == ["forward_split", "cash_dividend"]


def test_warmup_refuses_a_symbol_with_no_bars():
    tables, _ = warm_tables()
    src, _ = make_source(FakeDataClient(table_responder(tables)), symbols=["QQQ", "XYZ"])
    with pytest.raises(SourceUnavailable, match="XYZ"):
        src.fetch_warmup(date(2024, 3, 7))


def test_warmup_refuses_a_truncated_multi_symbol_response():
    tables, days = warm_tables()
    drop = {("raw", "QQQ"): {days[3]}, ("all", "QQQ"): {days[3]}}
    src, _ = make_source(FakeDataClient(table_responder(tables, drop)), symbols=["QQQ", "BIL"])
    with pytest.raises(SourceUnavailable, match="QQQ"):
        src.fetch_warmup(date(2024, 3, 7))


def test_warmup_before_the_last_session_cutoff_is_not_ready():
    tables, _ = warm_tables()
    early = datetime.combine(date(2024, 3, 6), time(15, 0), NY)
    src, _ = make_source(FakeDataClient(table_responder(tables)), symbols=["QQQ"], now=early)
    with pytest.raises(NotReady):
        src.fetch_warmup(date(2024, 3, 7))


# --- credentials and the lazy client factory -----------------------------------------------


def test_credentials_are_read_by_name_and_never_echoed():
    env = {sa.KEY_ID_ENV: "PKTESTKEY", sa.SECRET_KEY_ENV: "s3cr3t-value"}
    assert sa.KEY_ID_ENV == "ALPACA_PAPER_KEY_ID"
    assert sa.SECRET_KEY_ENV == "ALPACA_PAPER_SECRET_KEY"
    assert sa.paper_credentials(env) == ("PKTESTKEY", "s3cr3t-value")
    with pytest.raises(sa.CredentialsMissing) as info:
        sa.paper_credentials({sa.KEY_ID_ENV: "PKTESTKEY"})
    assert "ALPACA_PAPER_SECRET_KEY" in str(info.value)
    assert "PKTESTKEY" not in str(info.value)


def test_modules_import_and_run_without_alpaca():
    import subprocess
    import sys

    code = (
        "import sys; sys.modules['alpaca'] = None\n"
        "import forward.etf_bars, forward.sources_alpaca as sa, forward.orders_alpaca\n"
        "env = {sa.KEY_ID_ENV: 'k', sa.SECRET_KEY_ENV: 's'}\n"
        "try:\n"
        "    sa.make_data_client(env)\n"
        "except ImportError as exc:\n"
        "    assert 'requirements_broker' in str(exc), exc\n"
        "    print('lazy-ok')\n"
    )
    out = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, timeout=60, check=False
    )
    assert out.returncode == 0, out.stderr[-2000:]
    assert out.stdout.strip() == "lazy-ok"
