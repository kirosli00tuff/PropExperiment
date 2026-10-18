"""IB Gateway plumbing for E22-F1's IBKR adapters (Stage E.24, IBKRCoder).

Nothing here connects at import time, holds a credential or reads .env. The vendor library
(ib_async 2.1.0, pinned in forward/requirements_broker.txt, never in pyproject.toml/uv.lock) is
imported lazily in :func:`connect_live` and :func:`live_vendor` only, so every module and every
test runs without it.

Pieces:
- :class:`Gateway`: the Protocol the adapters call. It mirrors the subset of ``ib_async.IB`` they
  use (connect/disconnect/isConnected, reqContractDetails, reqHistoricalData, placeOrder,
  positions, openTrades, reqExecutions, managedAccounts, sleep, errorEvent, disconnectedEvent);
  an ``ib_async.IB`` instance satisfies it, and so does the test suite's mock gateway.
- :class:`Vendor`: constructors for contracts and orders (``ib_async.Future``, ``MarketOrder``,
  ``LimitOrder`` live; plain dataclasses in tests).
- :class:`GatewaySession`: connect, reconnect with bounded retries and exponential backoff,
  pacing between historical requests, and error classification. Anything it cannot finish raises
  :class:`SourceUnavailable`, so the caller writes no ledger record.
- Connection parameters come from environment variables whose NAMES are listed in
  :data:`ENV_NAMES`; their values are never printed, logged or stored.
"""

from __future__ import annotations

import time as _time
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

# Environment variable NAMES (values are never printed or logged; see env_status).
ENV_HOST = "IBKR_GATEWAY_HOST"
ENV_PORT = "IBKR_GATEWAY_PORT"
ENV_CLIENT_ID = "IBKR_CLIENT_ID"
ENV_ACCOUNT = "IBKR_ACCOUNT_ID"
ENV_NAMES = (ENV_HOST, ENV_PORT, ENV_CLIENT_ID, ENV_ACCOUNT)

# A historical request whose answer took the whole request timeout (less this slack) is a
# timeout, whatever came back (B1, wave 3): ib_async ends a request with asyncio.wait_for, and
# whatever bars it holds then never count as a complete answer. Slower answers are retried.
TIMEOUT_SLACK_S = 0.5

# Error codes of the TWS API. ibkr_facts.md I4 / "What this means" 6: handle 162, 166, 200 and
# 354 as data-unavailable errors, not crashes; 10186/10187 are the current no-permission codes.
CONNECTIVITY_CODES = frozenset({502, 504, 1100, 1300, 2110})
NOT_FOUND_CODES = frozenset({200})
# I4: 354 "Requested market data is not subscribed", 10089 "API data requires subscription",
# 10186 "... Delayed market data is not enabled", 10187 "... No market data permissions".
SUBSCRIPTION_CODES = frozenset({354, 10089, 10090, 10186, 10187})  # no subscription -> stop
VALIDATION_CODES = frozenset({321})
HMDS_CODE = 162  # "Historical Market Data Service error message": pacing, no data, other
# I4: "166 HMDS Expired Contract Violation. Historical data is not available for the specified
# expired contract." An affirmative no-data answer: never a price, never a Missing on its own.
HMDS_QUERY_CODE = 166
PACING_TEXT = "pacing violation"
NO_DATA_TEXT = "returned no data"

TRANSIENT, NO_DATA, NOT_FOUND, FATAL = "transient", "no_data", "not_found", "fatal"
SUBSCRIPTION = "subscription"
# a 162 (or any code) whose text says permissions/subscription is a refusal, not a gap (C1)
SUBSCRIPTION_TEXTS = ("market data permission", "not subscribed", "requires subscription")
DEFAULT_MARKET_DATA_TYPE = 3  # factcheck C1: request delayed data before historical requests
MARKET_DATA_TYPES = (None, 1, 2, 3, 4)  # ib_async reqMarketDataType: live, frozen, delayed, d-f


class IBKRError(Exception):
    """Base class of the IBKR adapters' errors. Any of them means: no ledger record."""


class IBKRConfigError(IBKRError):
    """Missing or malformed connection settings (the message names variables, never values)."""


class SourceUnavailable(IBKRError):
    """The gateway could not answer (connection, timeout, pacing, partial or empty response).

    Transient by nature: the day is retried later. It is never turned into Missing.
    """


class SubscriptionNeeded(SourceUnavailable):
    """IBKR refused market data for lack of a subscription/permission (162, 354, 10089, ...).

    Never retried and never a Missing: no ledger record is written until data access exists.
    """


class DayNotReady(SourceUnavailable):
    """The trade date's bar is not yet final (before the cutoff, or no confirming later bar)."""


class ContractResolutionError(IBKRError):
    """A contract did not resolve to exactly one IB contract, or its fields do not match."""


class ConventionError(IBKRError):
    """The gateway's data broke a declared convention (bar date type, weekend date, units)."""


class NoHistoricalData(IBKRError):
    """The server said affirmatively that the query has no data (HMDS 'returned no data')."""


class EmptyResponse(Exception):
    """reqHistoricalData returned no bars without an error (ib_async does this on a timeout)."""


class RequestTimedOut(TimeoutError):
    """A historical request took the whole request timeout; its bars, if any, are discarded."""


class RequestRejected(Exception):
    """The gateway rejected a request with a validation code that ib_async logs as a warning
    (321), so the request itself would only time out. Classified FATAL: never retried."""

    def __init__(self, code: int, message: str):
        super().__init__(f"{code}: {message}")
        self.code, self.message = code, message


@runtime_checkable
class Gateway(Protocol):
    """The subset of ``ib_async.IB`` the adapters use (keyword names as in ib_async 2.1.0)."""

    errorEvent: Any
    disconnectedEvent: Any

    def connect(
        self, host: str, port: int, clientId: int, timeout: float, readonly: bool
    ) -> Any: ...

    def disconnect(self) -> Any: ...

    def isConnected(self) -> bool: ...

    def reqContractDetails(self, contract: Any) -> list[Any]: ...

    def reqHistoricalData(
        self,
        contract: Any,
        endDateTime: Any,
        durationStr: str,
        barSizeSetting: str,
        whatToShow: str,
        useRTH: bool,
        formatDate: int = 1,
        keepUpToDate: bool = False,
        chartOptions: Any = (),
        timeout: float = 60,
    ) -> list[Any]: ...

    def placeOrder(self, contract: Any, order: Any) -> Any: ...

    def positions(self, account: str = "") -> list[Any]: ...

    def openTrades(self) -> list[Any]: ...

    def reqExecutions(self, execFilter: Any = None) -> list[Any]: ...

    def reqCompletedOrders(self, apiOnly: bool) -> list[Any]: ...

    def managedAccounts(self) -> list[str]: ...

    def reqMarketDataType(self, marketDataType: int) -> Any: ...

    def sleep(self, secs: float) -> Any: ...


@dataclass(frozen=True)
class Vendor:
    """Constructors the adapters need from the vendor library."""

    future: Callable[..., Any]
    contract: Callable[..., Any]
    market_order: Callable[..., Any]
    limit_order: Callable[..., Any]


def live_vendor() -> Vendor:
    """ib_async's constructors (lazy import; raises IBKRConfigError when it is not installed)."""
    ib_async = _import_ib_async()
    return Vendor(ib_async.Future, ib_async.Contract, ib_async.MarketOrder, ib_async.LimitOrder)


def _import_ib_async() -> Any:
    try:
        import ib_async  # noqa: PLC0415  (lazy by design: the suite never needs it)
    except ImportError as exc:
        raise IBKRConfigError(
            "ib_async is not installed; run through the overlay: uv run --with-requirements "
            "forward/requirements_broker.txt python -m forward.daily_f1 ..."
        ) from exc
    return ib_async


def connect_live() -> Gateway:
    """A fresh, unconnected ``ib_async.IB`` with request errors raised, not swallowed.

    ib_async's default (RaiseRequestErrors False) ends a failed request silently with whatever
    bars had arrived, which would look like a partial history; True raises RequestError instead.
    """
    ib_async = _import_ib_async()
    ib = ib_async.IB()
    ib.RaiseRequestErrors = True
    return ib


@dataclass(frozen=True)
class ConnectionParams:
    """Host, port and client id of the local IB Gateway, and the paper account id (optional)."""

    host: str
    port: int
    client_id: int
    account: str | None = field(default=None)

    def __repr__(self) -> str:  # never show values
        return "ConnectionParams(<values withheld>)"

    __str__ = __repr__

    @classmethod
    def from_env(
        cls, environ: Mapping[str, str], *, need_account: bool = False
    ) -> ConnectionParams:
        missing = [n for n in (ENV_HOST, ENV_PORT, ENV_CLIENT_ID) if not environ.get(n)]
        if need_account and not environ.get(ENV_ACCOUNT):
            missing.append(ENV_ACCOUNT)
        if missing:
            raise IBKRConfigError(f"environment variable(s) not set: {', '.join(missing)}")
        port = _int_env(environ, ENV_PORT)
        client_id = _int_env(environ, ENV_CLIENT_ID)
        if not 0 < port < 65536:
            raise IBKRConfigError(f"{ENV_PORT} is not a TCP port (value withheld)")
        if client_id <= 0:  # I9: clientId 0 merges manual TWS trading into the API client
            raise IBKRConfigError(f"{ENV_CLIENT_ID} must be a positive integer (value withheld)")
        account = environ.get(ENV_ACCOUNT) or None
        return cls(environ[ENV_HOST], port, client_id, account)


def _int_env(environ: Mapping[str, str], name: str) -> int:
    try:
        return int(environ[name])
    except ValueError:
        raise IBKRConfigError(f"{name} is not an integer (value withheld)") from None


def env_status(environ: Mapping[str, str]) -> dict[str, str]:
    """Each variable NAME with 'set' or 'unset'; values are never returned."""
    return {name: ("set" if environ.get(name) else "unset") for name in ENV_NAMES}


@dataclass(frozen=True)
class RetryPolicy:
    """Bounded retries with exponential backoff (seconds)."""

    max_attempts: int = 4
    backoff_base_s: float = 15.0  # I5: no identical historical request within 15 s
    backoff_cap_s: float = 120.0
    request_timeout_s: float = 60.0
    connect_timeout_s: float = 10.0

    def __post_init__(self) -> None:
        if self.max_attempts < 1 or self.backoff_base_s < 0 or self.backoff_cap_s < 0:
            raise IBKRConfigError("retry policy needs max_attempts >= 1 and non-negative waits")
        if self.request_timeout_s <= TIMEOUT_SLACK_S:  # 0 would make ib_async wait forever
            raise IBKRConfigError(f"request_timeout_s must exceed {TIMEOUT_SLACK_S} s")

    def backoff(self, attempt: int) -> float:
        return min(self.backoff_cap_s, self.backoff_base_s * 2 ** (attempt - 1))


class Pacer:
    """At least ``min_interval_s`` between consecutive historical-data requests."""

    def __init__(
        self,
        min_interval_s: float,
        *,
        clock: Callable[[], float] = _time.monotonic,
        sleep: Callable[[float], Any] = _time.sleep,
    ):
        self.min_interval_s = float(min_interval_s)
        self._clock, self._sleep = clock, sleep
        self._last: float | None = None

    def wait(self) -> None:
        now = self._clock()
        if self._last is not None:
            gap = self._last + self.min_interval_s - now
            if gap > 0:
                self._sleep(gap)
                now = self._clock()
        self._last = now


def classify(exc: BaseException) -> str:
    """TRANSIENT (retry), NO_DATA, NOT_FOUND (affirmative answers), SUBSCRIPTION or FATAL."""
    if isinstance(exc, (EmptyResponse, ConnectionError, TimeoutError, OSError)):
        return TRANSIENT
    code = getattr(exc, "code", None)
    if not isinstance(code, int):
        return FATAL
    text = str(getattr(exc, "message", "")).lower()
    if code in SUBSCRIPTION_CODES or any(m in text for m in SUBSCRIPTION_TEXTS):
        return SUBSCRIPTION
    if code == HMDS_CODE:
        if PACING_TEXT in text:
            return TRANSIENT
        return NO_DATA if NO_DATA_TEXT in text else TRANSIENT
    if code == HMDS_QUERY_CODE:
        return NO_DATA
    if code in NOT_FOUND_CODES:
        return NOT_FOUND
    if code in VALIDATION_CODES:
        return FATAL
    return TRANSIENT


def describe(exc: BaseException | None) -> str:
    if exc is None:
        return "no error recorded"
    code = getattr(exc, "code", None)
    return f"{type(exc).__name__}" + (f" {code}" if code is not None else "") + f": {exc}"


class GatewaySession:
    """One gateway connection with reconnects, retries and pacing.

    ``call`` runs one request function against the gateway. Transient failures (a dropped
    socket, a timed-out or empty historical answer, a pacing violation, connectivity codes) are
    retried
    up to ``policy.max_attempts`` times with backoff, reconnecting first when the socket is down;
    after that, or on a fatal error, it raises SourceUnavailable. NO_DATA and NOT_FOUND answers
    are raised as NoHistoricalData / returned as an empty list, never retried into a guess.
    """

    def __init__(
        self,
        gateway: Gateway,
        params: ConnectionParams,
        *,
        readonly: bool = True,
        market_data_type: int | None = DEFAULT_MARKET_DATA_TYPE,
        policy: RetryPolicy | None = None,
        pacer: Pacer | None = None,
        sleep: Callable[[float], Any] = _time.sleep,
        clock: Callable[[], float] = _time.monotonic,
    ):
        if getattr(gateway, "RaiseRequestErrors", True) is not True:
            # with it False, ib_async ends an error-ended request with the bars received so far
            raise IBKRConfigError("gateway.RaiseRequestErrors must be True (see connect_live)")
        self.gateway = gateway
        self.params = params
        self.readonly = readonly
        if market_data_type not in MARKET_DATA_TYPES:
            raise IBKRConfigError(f"market data type must be one of {MARKET_DATA_TYPES}")
        self.market_data_type = market_data_type
        self.policy = policy or RetryPolicy()
        self.pacer = pacer or Pacer(0.0, sleep=sleep)
        self._sleep = sleep
        self._clock = clock
        self.connects = 0
        self.disconnects_seen = 0
        self._rejections: list[tuple[int, str]] = []
        gateway.disconnectedEvent += self._on_disconnect
        gateway.errorEvent += self._on_error

    def _on_disconnect(self, *_: Any) -> None:
        self.disconnects_seen += 1

    def _on_error(self, req_id: Any, code: Any, message: Any = "", *_: Any) -> None:
        """Keep validation warnings (321) seen while a request runs (N1, wave 3): ib_async 2.1.0
        lists 321 in warningCodes, so the request is not ended and would only time out."""
        if code in VALIDATION_CODES:
            self._rejections.append((int(code), str(message)))

    def redact(self, text: str) -> str:
        """Remove connection values from an error text (socket errors quote host and port)."""
        p = self.params
        for value, label in (
            (p.account, "<account>"),
            (p.host, "<host>"),
            (str(p.port), "<port>"),
            (f"clientId {p.client_id}", "clientId <id>"),
        ):
            if value:
                text = text.replace(value, label)
        return text

    def ensure_connected(self) -> None:
        if self.gateway.isConnected():
            return
        self.gateway.connect(
            host=self.params.host,
            port=self.params.port,
            clientId=self.params.client_id,
            timeout=self.policy.connect_timeout_s,
            readonly=self.readonly,
        )
        self.connects += 1
        if not self.gateway.isConnected():
            raise ConnectionError("gateway did not report a connection after connect()")
        if self.market_data_type is not None:
            # factcheck C1: do not assume historical bars fail without a subscription; ask for
            # delayed data (type 3) on every connect, before any historical request.
            self.gateway.reqMarketDataType(self.market_data_type)

    def close(self) -> None:
        if self.gateway.isConnected():
            self.gateway.disconnect()

    def call(
        self,
        what: str,
        fn: Callable[[Gateway], Any],
        *,
        paced: bool = False,
        not_found_empty: bool = False,
    ) -> Any:
        last: BaseException | None = None
        for attempt in range(1, self.policy.max_attempts + 1):
            try:
                self.ensure_connected()
                if paced:
                    self.pacer.wait()
                return fn(self.gateway)
            except Exception as exc:  # classified below; nothing is swallowed
                kind = classify(exc)
                if kind == NO_DATA:
                    raise NoHistoricalData(f"{what}: {self.redact(describe(exc))}") from exc
                if kind == NOT_FOUND and not_found_empty:
                    return []
                if kind == SUBSCRIPTION:
                    raise SubscriptionNeeded(
                        f"{what}: market data subscription needed (delayed type "
                        f"{self.market_data_type} was requested first); "
                        f"{self.redact(describe(exc))}"
                    ) from exc
                if kind in (FATAL, NOT_FOUND):
                    raise SourceUnavailable(f"{what}: {self.redact(describe(exc))}") from exc
                last = exc
                if attempt < self.policy.max_attempts:
                    self._sleep(self.policy.backoff(attempt))
        raise SourceUnavailable(
            f"{what}: gave up after {self.policy.max_attempts} attempts; "
            f"last {self.redact(describe(last))}"
        ) from last

    def contract_details(self, what: str, query: Any) -> list[Any]:
        return list(self.call(what, lambda gw: gw.reqContractDetails(query), not_found_empty=True))

    def daily_bars(
        self,
        what: str,
        contract: Any,
        *,
        end: str,
        duration: str,
        what_to_show: str,
        use_rth: bool,
    ) -> list[Any]:
        """Daily bars, complete or not at all.

        An answer that took the whole request timeout raises RequestTimedOut, whatever bars came
        with it (B1, wave 3: bars arrive oldest first, so a stall cuts off the newest ones); an
        empty answer without an error raises EmptyResponse. Both are retried and end in
        SourceUnavailable. A 321 seen through errorEvent during the request stops at once.
        """
        timeout = self.policy.request_timeout_s

        def fn(gw: Gateway) -> list[Any]:
            self._rejections.clear()
            started = self._clock()
            bars = gw.reqHistoricalData(
                contract,
                endDateTime=end,
                durationStr=duration,
                barSizeSetting="1 day",
                whatToShow=what_to_show,
                useRTH=use_rth,
                formatDate=1,
                keepUpToDate=False,
                timeout=timeout,
            )
            bars = list(bars)  # a snapshot: nothing appended later can count
            elapsed = self._clock() - started
            if self._rejections:
                raise RequestRejected(*self._rejections[-1])
            if elapsed + TIMEOUT_SLACK_S >= timeout:
                raise RequestTimedOut(
                    f"{what}: timed out after {elapsed:.1f} s (limit {timeout:g} s); "
                    f"{len(bars)} bar(s) received and discarded"
                )
            if not bars:
                raise EmptyResponse(f"{what}: no bars and no error (ib_async timeout result)")
            return bars

        return self.call(what, fn, paced=True)
