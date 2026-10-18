"""Daily ETF bars from Alpaca's market data API for E22-F2 (AlpacaCoder, Stage E.24 Part C).

An ``EtfBarSource`` (forward/etf_bars.py) over alpaca-py 0.44.0's StockHistoricalDataClient. The
library is imported lazily inside the client factory and the default request factory, so this
module and its tests work without it (install it as an overlay:
``uv run --frozen --with-requirements forward/requirements_broker.txt ...``).

For a session date ``t`` (America/New_York) and the caller's symbol list:

- one daily-bar request over ``[t - DAILY_WINDOW_DAYS, t]`` with adjustment "raw" (Alpaca's "all"
  adjustment is never requested: its method is undocumented and errors are reported, facts A3,
  E22-F2 registration section 6) and one corporate-actions request (GET /v1/corporate-actions on
  data.alpaca.markets, alpaca-py's CorporateActionsClient with raw_data=True, all types);
- ``close`` = rawclose(t); ``prev`` = the symbol's previous bar in the same response or, when
  the window holds none, in one single-symbol request reaching back to GAP_FIRST_DATE (so r
  spans a gap of any length; with no earlier bar at all the bar is the first row of the
  symbol's history: close only, ``ret`` and ``prev_date`` None);
  ``ret = k x (rawclose(t) + D) / rawclose(prev) - 1`` with ``k`` the product of the split ratios
  (forward_split, reverse_split; new shares per old = new_rate / old_rate) with ex_date in
  (prev, t] and ``D`` the sum of the per-share amounts (per share after that day's split) of
  cash_dividend (``rate``; special included) and capital_gains_distribution (``long_term_rate`` +
  ``short_term_rate``) with ex_date in (prev, t]; ``prev_date`` = prev. Only actions published
  when the day is fetched count; the endpoint's examples show actions processed up to ~15 days
  after their ex_date, so a distribution can arrive after its session (booked late by the runner);
- any other corporate action type naming a symbol is exposed as a flag (``DayFetch.flags``), never
  booked; ``AlpacaEtfSource.corporate_actions(start, end, symbols)`` returns every published
  action with ex_date in [start, end], however long the span (process_date padded by
  CA_MARGIN_DAYS on both sides, every page), so the runner can take the actions over any
  (prev, t] and book late actions (an ex_date in an already-recorded session);
- a bar's session date is its timestamp converted to America/New_York (Alpaca stamps a daily bar
  at 00:00 New York time of its session), never the machine's local date and never the UTC date;
- ``t`` is answered only after ``bar_cutoff(t)``; before it the source raises ``NotReady``.

Missing vs unavailable:

- a symbol is Missing only when the response lacks ``t``'s bar after the cutoff AND a dedicated
  single-symbol request confirms it (so a truncated multi-symbol response is never read as a
  halt); if the single-symbol request has the bar, the multi-symbol response was partial and the
  source raises ``SourceUnavailable``;
- the whole day is Missing only when no symbol has ``t``'s bar (each confirmed) and ``t`` is a
  weekday not declared closed (weekends and declared closed dates raise ``NotASession``); a
  response with no bar for any symbol on any date of the window raises ``SourceUnavailable``
  (it affirms nothing about ``t``);
- transport errors, HTTP 429/5xx, timeouts, empty bodies, malformed or partial responses raise
  ``SourceUnavailable`` after bounded retries with backoff (HTTP 429 and 5xx, connection errors and
  timeouts are retried; other client errors are not). The caller writes no ledger record.

Credentials: only the environment variable NAMES below are known here. Their values are read
inside the client factory, passed to the client and never printed, logged or stored.
"""

from __future__ import annotations

import math
import os
import time as _time
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from typing import Any, Protocol
from zoneinfo import ZoneInfo

from forward.etf_bars import (
    SYMBOL_RE,
    EtfBar,
    EtfBarError,
    EtfDay,
    EtfDayRow,
    Missing,
    NotReady,
    SourceUnavailable,
    dump_etf_warmup,
    etf_history_sha256,
)

NY = ZoneInfo("America/New_York")

# --- credentials (names only) ---------------------------------------------------------------
KEY_ID_ENV = "ALPACA_PAPER_KEY_ID"
SECRET_KEY_ENV = "ALPACA_PAPER_SECRET_KEY"

# --- data constants (PHASE 2: aligned with reports/stage_e24_briefs/facts/alpaca_facts.md) ---
# Feed: always passed explicitly and recorded (facts "What this means" 2). E22-F2 registration
# section 6 names "sip" (the SIP close is in practice the closing-auction print, A4) with one
# conditional rule: if the first connection session finds SIP daily bars refused for the account
# (A2: vendor pages conflict), the feed is "iex", fixed before any ledger record and logged in
# docs/DECISIONS.md. A refusal surfaces here as SourceUnavailable (HTTP 403, not retried); the
# caller (daily_f2.py, config_f2.json "data_feed") owns the switch. The free plan serves SIP
# history only when `end` is >= 15 minutes old (A2, FAQ).
DATA_FEED = "sip"
ALLOWED_FEEDS = frozenset({"iex", "sip", "delayed_sip"})
SESSION_CLOSE_NY = time(16, 0)  # regular session close, New York time
# Cutoff: close + 2 h. The bar's date is the New York day and its close is set by the closing
# trade (A4); extended-hours trades do not move it (A4); SIP needs end >= 15 min old (A2); when
# a corrected close (condition 9, A4) can arrive is not documented, hence the wide margin. Nothing
# is time-critical before 19:00 ET, when CLS orders start to queue (A8).
BAR_CUTOFF_DELAY = timedelta(hours=2)
QUERY_END_LAG = timedelta(minutes=16)  # A2: end >= 15 minutes old for SIP on the free plan
DAILY_WINDOW_DAYS = 21  # calendar days before t in the daily request (>= 10 sessions)
WARMUP_FIRST_DATE = date(2024, 3, 1)  # E.24 brief C3a item 4
# A symbol whose window holds t's bar and no earlier one is re-requested alone from this date
# (the first date of E22-F2's history), so r spans a gap of any length (C4a S1).
GAP_FIRST_DATE = WARMUP_FIRST_DATE

# --- retries and pacing ---------------------------------------------------------------------
MAX_ATTEMPTS = 5  # per request, including the first
BACKOFF_BASE_SECONDS = 2.0  # 2, 4, 8, 16 s
MAX_BACKOFF_SECONDS = 60.0
RATE_LIMIT_PER_MINUTE = 200  # A9: Basic plan historical calls per minute; 429 when exceeded
MIN_REQUEST_INTERVAL_S = 60.0 / RATE_LIMIT_PER_MINUTE
RETRY_STATUS = frozenset({429, 500, 502, 503, 504})
MESSAGE_CHARS = 200


class NotASession(ValueError):  # noqa: N818
    """The date is a weekend or a declared exchange-closed day; no bars are expected."""


class CredentialsMissing(RuntimeError):  # noqa: N818
    """A required environment variable is unset (its NAME is in the message, never a value)."""


class BarLike(Protocol):
    timestamp: datetime
    close: float


class BarSetLike(Protocol):
    data: Mapping[str, Sequence[BarLike]]


class StockBarsClient(Protocol):
    """The part of alpaca-py's StockHistoricalDataClient this source uses."""

    def get_stock_bars(self, request_params: Any) -> BarSetLike: ...


class CorporateActionsClientLike(Protocol):
    """alpaca-py's CorporateActionsClient constructed with raw_data=True (a mapping response)."""

    def get_corporate_actions(self, request_params: Any) -> Mapping[str, Any]: ...


RequestFactory = Callable[..., Any]

# --- corporate actions (E22-F2 registration section 6) -------------------------------------
SPLIT_KINDS = frozenset({"forward_split", "reverse_split"})
DISTRIBUTION_KINDS = frozenset(
    {"cash_dividend", "capital_gains_distribution", "capital_gain_distribution"}
)
BOOKED_KINDS = SPLIT_KINDS | DISTRIBUTION_KINDS
CAPITAL_GAINS_LEGS = ("long_term_rate", "short_term_rate")
# The endpoint's start/end is an interval of `process_date` ("The corporate actions are sorted by
# their `process_date`", /v1/corporate-actions reference, pages/alpaca/ref_us_corporateactions-1.md;
# process_date = "The date when the corporate action is processed by Alpaca"). Its examples show
# process_date up to ~15 days AFTER ex_date (cash dividend FCF: ex 2023-05-04, processed
# 2023-05-19; capital gains GCAD: ex 2025-12-26, processed 2026-01-08). Requests therefore span a
# wide process_date range around the bars and filter on ex_date locally:
# ``AlpacaEtfSource.corporate_actions(start, end)`` asks for process dates
# [start - CA_MARGIN_DAYS, end + CA_MARGIN_DAYS] and keeps ex_date in [start, end].
CA_MARGIN_DAYS = 60


# --- time ----------------------------------------------------------------------------------


def _aware(value: datetime, what: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{what} must be a time zone aware datetime, got {value!r}")
    return value


def session_date(timestamp: datetime) -> date:
    """The America/New_York date of a bar timestamp (never the local or the UTC date)."""
    return _aware(timestamp, "bar timestamp").astimezone(NY).date()


def bar_cutoff(trade_date: date) -> datetime:
    """When ``trade_date``'s daily bar is accepted: the New York close plus BAR_CUTOFF_DELAY."""
    return datetime.combine(trade_date, SESSION_CLOSE_NY, NY) + BAR_CUTOFF_DELAY


def _is_session(day: date, closed: Iterable[date] = ()) -> bool:
    return day.weekday() < 5 and day not in set(closed)


def latest_ready_session(now: datetime, closed: Iterable[date] = ()) -> date:
    """The latest weekday session (not declared closed) whose cutoff has passed at ``now``."""
    closed = frozenset(closed)
    day = _aware(now, "now").astimezone(NY).date()
    if _is_session(day, closed) and now >= bar_cutoff(day):
        return day
    day -= timedelta(days=1)
    while not _is_session(day, closed):
        day -= timedelta(days=1)
    return day


def _ny_midnight(day: date) -> datetime:
    return datetime.combine(day, time(0), NY)


def _ny_end_of_day(day: date) -> datetime:
    return datetime.combine(day, time(23, 59, 59), NY)


# --- credentials and lazy clients ----------------------------------------------------------

_INSTALL_HINT = (
    "alpaca-py is not installed in this environment; run with "
    "`uv run --frozen --with-requirements forward/requirements_broker.txt ...` "
    "(alpaca-py 0.44.0 is pinned there, never in pyproject.toml or uv.lock)"
)


def paper_credentials(environ: Mapping[str, str] | None = None) -> tuple[str, str]:
    """(key id, secret) from ALPACA_PAPER_KEY_ID and ALPACA_PAPER_SECRET_KEY. Never logged."""
    env = os.environ if environ is None else environ
    values = []
    for name in (KEY_ID_ENV, SECRET_KEY_ENV):
        value = env.get(name, "")
        if not value or not value.strip():
            raise CredentialsMissing(f"environment variable {name} is not set")
        values.append(value.strip())
    return values[0], values[1]


def make_data_client(environ: Mapping[str, str] | None = None) -> StockBarsClient:
    """alpaca-py's StockHistoricalDataClient with the paper account's keys (lazy import)."""
    key_id, secret = paper_credentials(environ)
    try:
        from alpaca.data.historical import StockHistoricalDataClient
    except ImportError as exc:
        raise ImportError(_INSTALL_HINT) from exc
    return StockHistoricalDataClient(api_key=key_id, secret_key=secret)


def make_corporate_actions_client(
    environ: Mapping[str, str] | None = None,
) -> CorporateActionsClientLike:
    """alpaca-py's CorporateActionsClient, raw_data=True (lazy import). Raw mode matters: the
    0.44.0 typed CorporateActionsSet has no capital_gains_distribution model and its type enum
    has no such member, so typed parsing would not carry those actions."""
    key_id, secret = paper_credentials(environ)
    try:
        from alpaca.data.historical.corporate_actions import CorporateActionsClient
    except ImportError as exc:
        raise ImportError(_INSTALL_HINT) from exc
    return CorporateActionsClient(api_key=key_id, secret_key=secret, raw_data=True)


def alpaca_corporate_actions_request(*, symbols: list[str], start: date, end: date) -> Any:
    """alpaca-py's CorporateActionsRequest for all types (lazy import). ``limit=None``: the
    request class defaults to 1000, which would silently cap the result."""
    try:
        from alpaca.data.requests import CorporateActionsRequest
    except ImportError as exc:
        raise ImportError(_INSTALL_HINT) from exc
    return CorporateActionsRequest(symbols=list(symbols), start=start, end=end, limit=None)


def alpaca_bars_request(
    *, symbol_or_symbols: list[str], start: datetime, end: datetime, adjustment: str, feed: str
) -> Any:
    """alpaca-py's StockBarsRequest for daily bars (lazy import). No ``limit``: the SDK then
    follows ``next_page_token`` until the response is complete."""
    try:
        from alpaca.data.enums import Adjustment, DataFeed
        from alpaca.data.requests import StockBarsRequest
        from alpaca.data.timeframe import TimeFrame
    except ImportError as exc:
        raise ImportError(_INSTALL_HINT) from exc
    return StockBarsRequest(
        symbol_or_symbols=list(symbol_or_symbols),
        timeframe=TimeFrame.Day,
        start=start,
        end=end,
        adjustment=Adjustment(adjustment),
        feed=DataFeed(feed),
    )


# --- errors --------------------------------------------------------------------------------


def _status(exc: BaseException) -> int | None:
    status = getattr(exc, "status_code", None)
    if status is None:
        status = getattr(getattr(exc, "response", None), "status_code", None)
    return status if isinstance(status, int) else None


def _is_transient(exc: BaseException) -> bool:
    status = _status(exc)
    if status is not None:
        return status in RETRY_STATUS
    return isinstance(exc, OSError)  # ConnectionError, TimeoutError, requests' errors


def _describe(exc: BaseException) -> str:
    status = _status(exc)
    head = type(exc).__name__ + (f" HTTP {status}" if status is not None else "")
    text = " ".join(str(exc).split())[:MESSAGE_CHARS]
    return f"{head}: {text}" if text else head


def _reset_wait(exc: BaseException, now: datetime) -> float | None:
    headers = getattr(getattr(exc, "response", None), "headers", None)
    if not isinstance(headers, Mapping):
        return None
    lowered = {str(k).lower(): v for k, v in headers.items()}
    try:
        if "retry-after" in lowered:
            return float(lowered["retry-after"])
        if "x-ratelimit-reset" in lowered:
            return float(lowered["x-ratelimit-reset"]) - now.timestamp()  # A9 headers
    except (TypeError, ValueError):
        return None
    return None


# --- results -------------------------------------------------------------------------------


@dataclass(frozen=True)
class CorporateAction:
    symbol: str
    kind: str  # Alpaca's type name, singular (e.g. cash_dividend, forward_split, spin_off)
    ex_date: date | None
    ratio: float | None  # splits: new shares per old share (new_rate / old_rate)
    amount: float | None  # distributions: USD per share (after that day's split)
    fields: Mapping[str, Any]  # the raw record as published


@dataclass(frozen=True)
class CorporateActions:
    """What the endpoint published for a symbol list and date range."""

    booked: tuple[CorporateAction, ...]  # splits and distributions (BOOKED_KINDS)
    other: tuple[CorporateAction, ...]  # any other type naming a requested symbol (flags only)

    def between(self, symbol: str, after: date, through: date) -> tuple[CorporateAction, ...]:
        """Booked actions of ``symbol`` with ex_date in (after, through]."""
        return tuple(
            a for a in self.booked
            if a.symbol == symbol and a.ex_date is not None and after < a.ex_date <= through
        )

    def flags(self, symbol: str, after: date, through: date) -> tuple[str, ...]:
        return tuple(
            f"{a.kind} ex_date {a.ex_date}"
            for a in self.other
            if a.symbol == symbol and (a.ex_date is None or after < a.ex_date <= through)
        )

    def within(self, first: date, last: date) -> CorporateActions:
        """The actions with ex_date in [first, last]; undated other actions are kept (flags)."""
        return CorporateActions(
            tuple(a for a in self.booked if a.ex_date is not None and first <= a.ex_date <= last),
            tuple(a for a in self.other if a.ex_date is None or first <= a.ex_date <= last),
        )


def total_return(
    raw_t: float, raw_prev: float, actions: Iterable[CorporateAction]
) -> float:
    """k x (rawclose(t) + D) / rawclose(prev) - 1 (E22-F2 registration section 6)."""
    k, dist = 1.0, 0.0
    for a in actions:
        if a.kind in SPLIT_KINDS:
            k *= a.ratio  # type: ignore[operator]
        elif a.kind in DISTRIBUTION_KINDS:
            dist += a.amount  # type: ignore[operator]
    return k * (raw_t + dist) / raw_prev - 1


@dataclass(frozen=True)
class DayFetch:
    """One day's answer with per-symbol Missing reasons (``bars()`` returns ``answer()``)."""

    trade_date: date
    bars: Mapping[str, EtfBar]
    missing: Mapping[str, Missing]
    have_session: bool  # at least one symbol had a bar for trade_date
    applied: Mapping[str, tuple[CorporateAction, ...]] = field(default_factory=dict)
    flags: Mapping[str, tuple[str, ...]] = field(default_factory=dict)

    def answer(self) -> EtfDay | Missing:
        if not self.have_session:
            return Missing(
                f"no bar for any of {len(self.missing)} symbols on {self.trade_date.isoformat()} "
                "after the cutoff (a weekday not declared closed; each symbol confirmed)"
            )
        if not self.bars:
            return Missing(f"no usable bar on {self.trade_date.isoformat()}: {self.missing}")
        return dict(sorted(self.bars.items()))


@dataclass(frozen=True)
class WarmupResult:
    rows: tuple[EtfDayRow, ...]
    sha256: str
    first_date: Mapping[str, date]
    row_count: Mapping[str, int]
    gaps: Mapping[str, tuple[date, ...]]  # sessions other symbols have and this one lacks
    corporate_actions: CorporateActions | None = None


def write_warmup(result: WarmupResult, path: Path | str) -> str:
    """Write the warm-up JSONL (refuses to overwrite); returns and checks its sha256."""
    digest = dump_etf_warmup(result.rows, path)
    if digest != result.sha256:
        raise EtfBarError("warm-up sha256 changed between fetch and write")
    return digest


Series = dict[str, dict[date, float]]


# --- the source ----------------------------------------------------------------------------


class AlpacaEtfSource:
    """EtfBarSource over Alpaca daily bars. Symbols come from the caller (E22-F2's ETFs + BIL)."""

    def __init__(
        self,
        symbols: Iterable[str],
        client: StockBarsClient,
        *,
        feed: str = DATA_FEED,
        request_factory: RequestFactory = alpaca_bars_request,
        ca_client: CorporateActionsClientLike | None = None,
        ca_request_factory: RequestFactory = alpaca_corporate_actions_request,
        ca_client_factory: Callable[[], CorporateActionsClientLike] = (
            make_corporate_actions_client
        ),
        clock: Callable[[], datetime] | None = None,
        sleep: Callable[[float], None] = _time.sleep,
        monotonic: Callable[[], float] = _time.monotonic,
        closed_dates: Iterable[date] = (),
        window_days: int = DAILY_WINDOW_DAYS,
        max_attempts: int = MAX_ATTEMPTS,
    ):
        symbols = list(symbols)
        if not symbols:
            raise ValueError("symbol list is empty")
        if len(set(symbols)) != len(symbols):
            raise ValueError(f"duplicate symbols in {symbols}")
        for s in symbols:
            if not isinstance(s, str) or not SYMBOL_RE.match(s):
                raise ValueError(f"bad symbol {s!r}")
        if feed not in ALLOWED_FEEDS:
            raise ValueError(f"feed must be one of {sorted(ALLOWED_FEEDS)}, got {feed!r}")
        if window_days < 7 or max_attempts < 1:
            raise ValueError("window_days must be >= 7 and max_attempts >= 1")
        self.symbols = tuple(sorted(symbols))
        self.feed = feed
        self._client = client
        self._request_factory = request_factory
        self._ca_client = ca_client
        self._ca_client_factory = ca_client_factory
        self._ca_request_factory = ca_request_factory
        self._clock = clock or (lambda: datetime.now(UTC))
        self._sleep = sleep
        self._monotonic = monotonic
        self.closed_dates = frozenset(closed_dates)
        self.window_days = window_days
        self.max_attempts = max_attempts
        self._last_request: float | None = None

    # -- public --------------------------------------------------------------------------

    def bars(self, trade_date: date) -> EtfDay | Missing:
        return self.fetch_day(trade_date).answer()

    def fetch_day(self, trade_date: date) -> DayFetch:
        self._check_session(trade_date)
        now = self._now()
        if now < bar_cutoff(trade_date):
            raise NotReady(
                f"{trade_date.isoformat()} is not ready before {bar_cutoff(trade_date).isoformat()}"
            )
        first = trade_date - timedelta(days=self.window_days)
        start = _ny_midnight(first)
        end = min(_ny_end_of_day(trade_date), now - QUERY_END_LAG)
        raw = self._fetch(self.symbols, start, end, "raw")
        if not any(raw.get(s) for s in self.symbols):  # C4a S3
            raise SourceUnavailable(
                f"empty window: no bar for any of {len(self.symbols)} symbols on any date from "
                f"{first.isoformat()} to {trade_date.isoformat()} (affirms nothing about "
                f"{trade_date.isoformat()})"
            )
        ca = self.corporate_actions(first, trade_date)
        bars: dict[str, EtfBar] = {}
        missing: dict[str, Missing] = {}
        applied: dict[str, tuple[CorporateAction, ...]] = {}
        flags: dict[str, tuple[str, ...]] = {}
        unconfirmed: list[str] = []
        have_session = False
        for s in self.symbols:
            r = {d: c for d, c in raw.get(s, {}).items() if d <= trade_date}
            if trade_date not in r:
                unconfirmed.append(s)
                continue
            have_session = True
            bars[s], used, notes = self._symbol_bar(s, trade_date, r, ca, end)
            if used:
                applied[s] = used
            if notes:
                flags[s] = notes
        for s in unconfirmed:
            single = self._fetch((s,), start, end, "raw").get(s, {})
            if trade_date in single:
                raise SourceUnavailable(
                    f"{s}: the multi-symbol response lacked {trade_date.isoformat()} but a "
                    "single-symbol request has it (partial response)"
                )
            missing[s] = Missing(
                f"{s}: no bar for {trade_date.isoformat()} after the cutoff "
                "(confirmed by a single-symbol request)"
            )
        return DayFetch(trade_date, bars, missing, have_session, applied, flags)

    def fetch_warmup(self, start_date: date, first_date: date = WARMUP_FIRST_DATE) -> WarmupResult:
        """Every session from ``first_date`` to the day before ``start_date``: one raw-bar fetch
        and one corporate-actions fetch for all symbols, the same return formula as the daily
        fetch; a symbol whose sessions differ from the others' is re-requested alone, and a
        difference between the two answers raises SourceUnavailable."""
        last = start_date - timedelta(days=1)
        if last < first_date:
            raise ValueError(f"start date {start_date} leaves no warm-up after {first_date}")
        now = self._now()
        if now < bar_cutoff(last):
            raise NotReady(f"warm-up through {last.isoformat()} is not ready before its cutoff")
        start = _ny_midnight(first_date)
        end = min(_ny_end_of_day(last), now - QUERY_END_LAG)
        raw = _clip(self._fetch(self.symbols, start, end, "raw"), first_date, last)
        ca = self.corporate_actions(first_date, last)
        for s in self.symbols:
            if not raw.get(s):
                raise SourceUnavailable(f"{s}: no bars between {first_date} and {last}")
        union = sorted(set().union(*(raw[s].keys() for s in self.symbols)))
        gaps: dict[str, tuple[date, ...]] = {}
        for s in self.symbols:
            lacking = tuple(d for d in union if d not in raw[s])
            if not lacking:
                continue
            single = _clip(self._fetch((s,), start, end, "raw"), first_date, last).get(s, {})
            if set(single) != set(raw[s]):
                raise SourceUnavailable(
                    f"{s}: the multi-symbol warm-up response differs from a single-symbol "
                    "request (partial response)"
                )
            gaps[s] = lacking
        rows = _warmup_rows(self.symbols, union, raw, ca)
        return WarmupResult(
            rows=rows,
            sha256=etf_history_sha256(rows),
            first_date={s: min(raw[s]) for s in self.symbols},
            row_count={s: len(raw[s]) for s in self.symbols},
            gaps=gaps,
            corporate_actions=ca,
        )

    def corporate_actions(
        self, start: date, end: date, symbols: Iterable[str] | None = None
    ) -> CorporateActions:
        """Every corporate action the endpoint publishes for ``symbols`` (default: the
        source's) with EX_DATE in [start, end], both ends included, however long the span
        (C4a S1). The endpoint's start/end is a process_date interval, so one request asks for
        process dates [start - CA_MARGIN_DAYS, end + CA_MARGIN_DAYS] and the ex_dates are
        filtered here; alpaca-py follows next_page_token to the last page (limit=None). Other
        action types without an ex_date are kept as published (flags only). For a return over
        (prev, t] call ``corporate_actions(prev, t)`` and use ``.between(symbol, prev, t)``, which
        leaves out ex_date == prev. An action processed more than CA_MARGIN_DAYS after its
        ex_date is not found by a span that ends at that ex_date (booked late, section 6)."""
        if self._ca_client is None:  # built on first use, with the same paper keys (env)
            self._ca_client = self._ca_client_factory()
        wanted = tuple(sorted(symbols)) if symbols is not None else self.symbols
        margin = timedelta(days=CA_MARGIN_DAYS)
        request = self._ca_request_factory(
            symbols=list(wanted), start=start - margin, end=end + margin
        )
        what = f"corporate actions {','.join(wanted)} ex {start}..{end}"
        response = self._call(lambda: self._ca_client.get_corporate_actions(request), what)
        return parse_corporate_actions(response, wanted, what).within(start, end)

    # -- internals -----------------------------------------------------------------------

    def _symbol_bar(
        self,
        s: str,
        trade_date: date,
        r: Mapping[date, float],
        ca: CorporateActions,
        end: datetime,
    ) -> tuple[EtfBar, tuple[CorporateAction, ...], tuple[str, ...]]:
        """t's bar for ``s`` (``r`` holds t), the actions applied and the flags. The return runs
        from the symbol's previous bar; when the window holds none it is looked for beyond the
        window, with the corporate actions over that whole span (C4a S1)."""
        close = r[trade_date]
        prev = max((d for d in r if d < trade_date), default=None)
        if prev is None:
            found = self._earlier_bar(s, trade_date, close, end)
            if found is None:  # the first bar of the symbol's history: close only
                return _bar(s, close, None, None), (), ()
            prev, raw_prev = found
            ca = self.corporate_actions(prev, trade_date, (s,))
        else:
            raw_prev = r[prev]
        used = ca.between(s, prev, trade_date)
        bar = _bar(s, close, total_return(close, raw_prev, used), prev)
        return bar, used, ca.flags(s, prev, trade_date)

    def _earlier_bar(
        self, s: str, trade_date: date, close: float, end: datetime
    ) -> tuple[date, float] | None:
        """(date, raw close) of the latest bar of ``s`` before ``trade_date``, from one
        single-symbol request reaching back to GAP_FIRST_DATE; None when there is none. The
        wider answer must agree with the window: the same close on ``trade_date`` and no earlier
        bar inside the window (else the multi-symbol response was partial)."""
        window_first = trade_date - timedelta(days=self.window_days)
        first = min(GAP_FIRST_DATE, window_first)
        wide = self._fetch((s,), _ny_midnight(first), end, "raw").get(s, {})
        t = trade_date.isoformat()
        if wide.get(trade_date) != close:
            raise SourceUnavailable(
                f"{s}: a single-symbol request from {first} gives {wide.get(trade_date)!r} for "
                f"{t}, the multi-symbol response {close!r}"
            )
        if any(window_first <= d < trade_date for d in wide):
            raise SourceUnavailable(
                f"{s}: the multi-symbol response had no bar before {t} in the window but a "
                "single-symbol request has one (partial response)"
            )
        prev = max((d for d in wide if d < trade_date), default=None)
        return None if prev is None else (prev, wide[prev])

    def _now(self) -> datetime:
        return _aware(self._clock(), "clock()")

    def _check_session(self, trade_date: date) -> None:
        if isinstance(trade_date, datetime) or not isinstance(trade_date, date):
            raise TypeError(f"trade_date must be a date, got {trade_date!r}")
        if not _is_session(trade_date, self.closed_dates):
            raise NotASession(f"{trade_date.isoformat()} is a weekend or declared closed")

    def _pace(self) -> None:
        now = self._monotonic()
        if self._last_request is not None:
            wait = MIN_REQUEST_INTERVAL_S - (now - self._last_request)
            if wait > 0:
                self._sleep(wait)
                now += wait
        self._last_request = now

    def _call(self, fn: Callable[[], Any], what: str) -> Any:
        for attempt in range(self.max_attempts):
            self._pace()
            try:
                return fn()
            except Exception as exc:  # noqa: BLE001 (the client boundary; classified below)
                if not _is_transient(exc):
                    raise SourceUnavailable(f"{what}: {_describe(exc)} (not retried)") from exc
                if attempt == self.max_attempts - 1:
                    raise SourceUnavailable(
                        f"{what}: {_describe(exc)} after {self.max_attempts} attempts"
                    ) from exc
                backoff = BACKOFF_BASE_SECONDS * 2**attempt
                reset = _reset_wait(exc, self._now())
                self._sleep(min(MAX_BACKOFF_SECONDS, max(backoff, reset or 0.0)))
        raise AssertionError("unreachable")

    def _fetch(
        self, symbols: Sequence[str], start: datetime, end: datetime, adjustment: str
    ) -> Series:
        request = self._request_factory(
            symbol_or_symbols=list(symbols),
            start=start,
            end=end,
            adjustment=adjustment,
            feed=self.feed,
        )
        what = f"bars {adjustment} {','.join(symbols)} {start.date()}..{end.date()}"
        response = self._call(lambda: self._client.get_stock_bars(request), what)
        return _parse(response, symbols, what)


def _bar(symbol: str, close: float, ret: float | None, prev: date | None) -> EtfBar:
    try:
        return EtfBar(close, ret, prev)
    except EtfBarError as exc:
        raise SourceUnavailable(f"{symbol}: {exc}") from exc


def _clip(series: Series, first: date, last: date) -> Series:
    return {s: {d: c for d, c in v.items() if first <= d <= last} for s, v in series.items()}


def _parse(response: Any, symbols: Sequence[str], what: str) -> Series:
    data = getattr(response, "data", None)
    if not isinstance(data, Mapping):
        raise SourceUnavailable(f"{what}: malformed response (no data mapping)")
    out: Series = {}
    for s in symbols:
        bars = data.get(s) or []
        series: dict[date, float] = {}
        for bar in bars:
            try:
                day = session_date(bar.timestamp)
            except (AttributeError, ValueError) as exc:
                raise SourceUnavailable(f"{what}: {s}: bad bar timestamp ({exc})") from exc
            close = getattr(bar, "close", None)
            if (
                isinstance(close, bool)
                or not isinstance(close, int | float)
                or not math.isfinite(close)
                or close <= 0
            ):
                raise SourceUnavailable(f"{what}: {s}: bad close {close!r} on {day}")
            if day in series:
                raise SourceUnavailable(f"{what}: {s}: duplicate session {day}")
            series[day] = float(close)
        if series:
            out[s] = dict(sorted(series.items()))
    return out


def _warmup_rows(
    symbols: Sequence[str], union: Sequence[date], raw: Series, ca: CorporateActions
) -> tuple[EtfDayRow, ...]:
    prev: dict[str, date] = {}
    rows = []
    for day in union:
        bars: dict[str, EtfBar] = {}
        for s in symbols:
            if day not in raw[s]:
                continue
            p = prev.get(s)
            if p is None:
                bars[s] = _bar(s, raw[s][day], None, None)
            else:
                ret = total_return(raw[s][day], raw[s][p], ca.between(s, p, day))
                bars[s] = _bar(s, raw[s][day], ret, p)
            prev[s] = day
        rows.append(EtfDayRow(day, bars))
    return tuple(rows)


def _positive(item: Mapping[str, Any], key: str, what: str) -> float:
    value = item.get(key)
    if isinstance(value, bool) or not isinstance(value, int | float | str):
        raise SourceUnavailable(f"{what}: {key}={value!r} is not a number")
    try:
        out = float(value)
    except ValueError as exc:
        raise SourceUnavailable(f"{what}: {key}={value!r} is not a number") from exc
    if not math.isfinite(out) or out < 0:
        raise SourceUnavailable(f"{what}: {key}={value!r} is not a finite non-negative number")
    return out


def _usd(item: Mapping[str, Any], what: str) -> None:
    currency = item.get("currency")
    if currency not in (None, "USD"):
        raise SourceUnavailable(f"{what}: amount in {currency!r}, not USD")


def _distribution_amount(kind: str, item: Mapping[str, Any], what: str) -> float:
    """cash_dividend: ``rate``. capital_gains_distribution: ``long_term_rate`` +
    ``short_term_rate`` ("At least one of the two rates is always present"; it has no ``rate``
    field), both per share."""
    if kind == "cash_dividend":
        return _positive(item, "rate", what)
    legs = [k for k in CAPITAL_GAINS_LEGS if item.get(k) is not None]
    if not legs:
        raise SourceUnavailable(f"{what}: neither long_term_rate nor short_term_rate is present")
    return sum(_positive(item, k, what) for k in legs)


def _ex_date(item: Mapping[str, Any], what: str, required: bool) -> date | None:
    raw = item.get("ex_date") or item.get("effective_date")
    if raw is None:
        if required:
            raise SourceUnavailable(f"{what}: no ex_date")
        return None
    try:
        return raw if isinstance(raw, date) else date.fromisoformat(str(raw))
    except ValueError as exc:
        raise SourceUnavailable(f"{what}: bad ex_date {raw!r}") from exc


def parse_corporate_actions(
    response: Any, symbols: Sequence[str], what: str = "corporate actions"
) -> CorporateActions:
    """Raw /v1/corporate-actions data ({type_plural: [record, ...]}) -> CorporateActions."""
    data = response.get("corporate_actions", response) if isinstance(response, Mapping) else None
    if not isinstance(data, Mapping):
        raise SourceUnavailable(f"{what}: malformed response (expected the raw mapping)")
    wanted = set(symbols)
    booked: list[CorporateAction] = []
    other: list[CorporateAction] = []
    for key, items in sorted(data.items()):
        kind = key[:-1] if key.endswith("s") else key
        if not isinstance(items, list):
            raise SourceUnavailable(f"{what}: {key} is not a list")
        for item in items:
            where = f"{what}: {kind} {item.get('symbol')}"
            if kind in BOOKED_KINDS:
                if item.get("symbol") not in wanted:
                    continue
                ex = _ex_date(item, where, required=True)
                if kind in SPLIT_KINDS:
                    old = _positive(item, "old_rate", where)
                    if old == 0:
                        raise SourceUnavailable(f"{where}: old_rate is 0")
                    ratio = _positive(item, "new_rate", where) / old
                    if ratio <= 0:
                        raise SourceUnavailable(f"{where}: split ratio {ratio} is not positive")
                    booked.append(CorporateAction(item["symbol"], kind, ex, ratio, None, item))
                else:
                    _usd(item, where)
                    amount = _distribution_amount(kind, item, where)
                    booked.append(CorporateAction(item["symbol"], kind, ex, None, amount, item))
                continue
            named = {
                v for k, v in item.items() if k.endswith("symbol") and isinstance(v, str)
            } & wanted
            ex = _ex_date(item, where, False) if named else None
            for sym in sorted(named):
                other.append(CorporateAction(sym, kind, ex, None, None, item))
    order = lambda a: (a.symbol, a.ex_date or date.min, a.kind)  # noqa: E731
    return CorporateActions(tuple(sorted(booked, key=order)), tuple(sorted(other, key=order)))
