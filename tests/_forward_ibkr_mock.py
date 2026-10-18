"""Mock IB Gateway for the forward IBKR adapter tests (Stage E.24). No network, no ib_async.

The classes mirror the ib_async 2.1.0 names the adapters use (Contract/Future fields,
ContractDetails.contract/contractMonth/priceMagnifier, BarData.date/close, Trade, Fill,
Execution, CommissionReport, Position, RequestError.code/message). Prices are synthetic and
written by hand here; nothing is fetched.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import UTC, date, datetime, timedelta
from typing import Any

from forward import rolls as R
from forward.ibkr_gateway import Vendor
from forward.sources_ibkr import CME_TZ, IB_SPECS

UNIVERSE = ("MNQ", "M2K", "MGC", "MCL", "MNG", "M6E", "2YY", "10Y", "30Y", "MZC", "MZS", "MZL")
PAPER = "DU7654321"
ENV = {
    "IBKR_GATEWAY_HOST": "127.0.0.1",
    "IBKR_GATEWAY_PORT": "4002",
    "IBKR_CLIENT_ID": "17",
    "IBKR_ACCOUNT_ID": PAPER,
}
BASE = {
    "MNQ": 21000.0,
    "M2K": 2300.0,
    "M6E": 1.085,
    "MGC": 2650.0,
    "MCL": 71.5,
    "MNG": 3.25,
    "2YY": 3.9,
    "10Y": 4.2,
    "30Y": 4.5,
    "MZC": 425.25,
    "MZS": 1050.5,
    "MZL": 45.12,
}
STEP = {
    "MNQ": 2.25,
    "M2K": 0.4,
    "M6E": 0.0001,
    "MGC": 0.7,
    "MCL": 0.03,
    "MNG": 0.002,
    "2YY": 0.001,
    "10Y": 0.002,
    "30Y": 0.001,
    "MZC": 0.25,
    "MZS": 0.5,
    "MZL": 0.02,
}
EPOCH = date(2024, 1, 1)
ROLLS = R.load_rolls()


@dataclass
class FakeContract:
    secType: str = "FUT"
    conId: int = 0
    symbol: str = ""
    lastTradeDateOrContractMonth: str = ""
    multiplier: str = ""
    exchange: str = ""
    currency: str = ""
    localSymbol: str = ""
    tradingClass: str = ""
    includeExpired: bool = False


def fake_future(**kw: Any) -> FakeContract:
    return FakeContract(secType="FUT", **kw)


def fake_contract(**kw: Any) -> FakeContract:
    return FakeContract(secType="", **kw)


@dataclass
class FakeDetails:
    contract: FakeContract
    contractMonth: str
    priceMagnifier: int = 1
    minTick: float = 0.0
    timeZoneId: str = "US/Central"


@dataclass
class FakeBar:
    date: Any
    close: float
    open: float = 0.0
    high: float = 0.0
    low: float = 0.0
    volume: float = 1.0


class FakeEvent:
    def __init__(self) -> None:
        self.handlers: list[Any] = []

    def __iadd__(self, handler: Any) -> FakeEvent:
        self.handlers.append(handler)
        return self

    def __isub__(self, handler: Any) -> FakeEvent:
        self.handlers.remove(handler)
        return self

    def emit(self, *args: Any) -> None:
        for h in list(self.handlers):
            h(*args)


class FakeRequestError(Exception):
    def __init__(self, reqId: int, code: int, message: str):
        super().__init__(f"[reqId {reqId}] API error: {code}: {message}")
        self.reqId, self.code, self.message = reqId, code, message


@dataclass
class FakeOrder:
    action: str
    totalQuantity: float
    orderType: str = "MKT"
    lmtPrice: float | None = None
    tif: str = ""
    account: str = ""
    orderRef: str = ""
    orderId: int = 0
    permId: int = 0
    filledQuantity: float = 1.7976931348623157e308  # ib_async UNSET_DOUBLE until IB fills it


def fake_market_order(action: str, totalQuantity: float, **kw: Any) -> FakeOrder:
    return FakeOrder(action, totalQuantity, "MKT", **kw)


def fake_limit_order(action: str, totalQuantity: float, lmtPrice: float, **kw: Any) -> FakeOrder:
    return FakeOrder(action, totalQuantity, "LMT", lmtPrice, **kw)


FAKE_VENDOR = Vendor(fake_future, fake_contract, fake_market_order, fake_limit_order)


@dataclass
class FakeExecution:
    execId: str
    time: datetime
    acctNumber: str
    side: str
    shares: float
    price: float
    orderRef: str = ""


@dataclass
class FakeCommission:
    execId: str
    commission: float
    currency: str = "USD"


@dataclass
class FakeFill:
    contract: FakeContract
    execution: FakeExecution
    commissionReport: FakeCommission
    time: datetime


@dataclass
class FakeStatus:
    status: str
    filled: float
    remaining: float
    avgFillPrice: float = 0.0


@dataclass
class FakeTrade:
    contract: FakeContract
    order: FakeOrder
    orderStatus: FakeStatus
    fills: list[FakeFill] = field(default_factory=list)

    def isDone(self) -> bool:
        return self.orderStatus.status in ("Filled", "Cancelled", "Inactive")


@dataclass
class FakePosition:
    account: str
    contract: FakeContract
    position: float
    avgCost: float


def ib_price(inst: str, cid: str, day: date) -> float:
    """Synthetic IB-unit close: level + daily step + a contango offset per contract."""
    year, month = R.parse_contract(ROLLS[inst], cid)
    offset = ((year - 2024) * 12 + month) * STEP[inst] * 3
    return round(BASE[inst] + STEP[inst] * (day - EPOCH).days + offset, 6)


def weekdays(first: date, last: date) -> list[date]:
    out, d = [], first
    while d <= last:
        if d.weekday() < 5:
            out.append(d)
        d += timedelta(days=1)
    return out


def contracts_between(spec: R.InstrumentRoll, first: date, last: date) -> list[str]:
    from forward.sources_ibkr import next_contract, previous_contract

    cid = previous_contract(spec, R.active_contract(spec, first))
    final = next_contract(spec, R.active_contract(spec, last))
    out = [cid]
    while cid != final:
        cid = next_contract(spec, cid)
        out.append(cid)
    return out


def build_listings(
    first: date, last: date, *, instruments: tuple[str, ...] = UNIVERSE
) -> dict[tuple[str, str], FakeDetails]:
    """One listing per contract in range; last trade date = the declared anchor date."""
    rolls, out, con_id = ROLLS, {}, 1000
    for inst in instruments:
        spec, ib = rolls[inst], IB_SPECS[inst]
        for cid in contracts_between(spec, first, last):
            con_id += 1
            year, month = R.parse_contract(spec, cid)
            expiry = R.expiry_guard(spec, cid)
            contract = FakeContract(
                "FUT",
                con_id,
                ib.symbol,
                expiry.strftime("%Y%m%d"),
                f"{ib.ib_multiplier:g}",
                ib.exchange,
                ib.currency,
                f"{ib.symbol}{cid[-3:]}",
                ib.trading_class or ib.symbol,
            )
            out[(inst, cid)] = FakeDetails(contract, f"{year:04d}{month:02d}", ib.price_magnifier)
    return out


def build_bars(
    listings: dict[tuple[str, str], FakeDetails],
    first: date,
    last: date,
    *,
    holes: set[tuple[str, date]] = frozenset(),
    listed_from: dict[str, date] | None = None,
) -> dict[int, dict[date, float]]:
    """Bars on every weekday a contract trades in [first, last] (minus holes by contract id)."""
    bars: dict[int, dict[date, float]] = {}
    for (inst, cid), det in listings.items():
        expiry = datetime.strptime(det.contract.lastTradeDateOrContractMonth, "%Y%m%d").date()
        start = max(first, (listed_from or {}).get(inst, first))
        bars[det.contract.conId] = {
            d: ib_price(inst, cid, d)
            for d in weekdays(start, min(last, expiry))
            if (cid, d) not in holes
        }
    return bars


def ct(y: int, m: int, d: int, hh: int, mm: int = 0) -> datetime:
    """An aware UTC datetime for a Chicago wall-clock time."""
    return datetime(y, m, d, hh, mm, tzinfo=CME_TZ).astimezone(UTC)


class MockGateway:
    """Scripted gateway. ``fail[method]`` is a queue of exceptions raised on the next calls;
    a ConnectionError also drops the connection (as ib_async's 'Socket disconnect').

    Fault and retention models (wave 3):
    - ``stall[conId]``: a queue of cuts (an int N: the first N bars of the answer; a date: the
      bars dated before it). The next historical request for that contract "times out": the
      mock clock advances by the request's timeout and the cut list comes back with no error
      (N=0 is ib_async 2.1.0's own timeout result, ``bars.clear()``; anything else is the
      partial list the B1 review describes). ``monotonic`` is the mock clock; ``sleep``
      advances it.
    - ``warn_321``: contracts whose request draws error 321 as an errorEvent warning (ib_async
      2.1.0 lists 321 in warningCodes), after which the request times out with no bars.
    - ``reqExecutions`` returns only the executions of the mock's current Chicago date (IB
      returns the current day's executions; the exact boundary is [unverified]), while
      ``reqCompletedOrders`` returns every finished order unless ``completed_visible`` is False.
    """

    def __init__(
        self,
        listings: dict[tuple[str, str], FakeDetails],
        bars: dict[int, dict[date, float]],
        *,
        now: datetime,
        accounts: tuple[str, ...] = (PAPER,),
        fill_mode: str = "immediate",
    ):
        self.listings = dict(listings)
        self.bars = bars
        self.now = now
        self.accounts = accounts
        self.fill_mode = fill_mode
        self.connected = False
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self.fail: dict[str, list[BaseException]] = {}
        self.no_data: set[int] = set()
        self.errorEvent, self.disconnectedEvent = FakeEvent(), FakeEvent()
        self.positions_by_con: dict[int, float] = {}
        self.trades: list[FakeTrade] = []
        self.executions: list[FakeFill] = []
        self.slept: list[float] = []
        self._seq = 0
        self.clock_s = 0.0
        self.stall: dict[int, list[int | date]] = {}
        self.warn_321: set[int] = set()
        self.completed_visible = True

    def monotonic(self) -> float:
        return self.clock_s

    # connection ------------------------------------------------------------------------------
    def _maybe_fail(self, method: str) -> None:
        queue = self.fail.get(method)
        if queue:
            exc = queue.pop(0)
            if isinstance(exc, ConnectionError):
                self.connected = False
                self.disconnectedEvent.emit()
            raise exc

    def connect(self, host: str, port: int, clientId: int, timeout: float, readonly: bool) -> None:
        self.calls.append(("connect", {"readonly": readonly, "timeout": timeout}))
        self._maybe_fail("connect")
        self.connected = True

    def disconnect(self) -> None:
        self.connected = False

    def isConnected(self) -> bool:
        return self.connected

    def _need_connection(self) -> None:
        if not self.connected:
            raise ConnectionError("Not connected")

    # contracts -------------------------------------------------------------------------------
    def reqContractDetails(self, contract: FakeContract) -> list[FakeDetails]:
        self.calls.append(("reqContractDetails", {"contract": replace(contract)}))
        self._need_connection()
        self._maybe_fail("reqContractDetails")
        today = self.now.astimezone(CME_TZ).date()
        out = []
        for det in self.listings.values():
            c = det.contract
            if contract.conId:
                if c.conId == contract.conId:
                    out.append(det)
                continue
            if (c.symbol, c.exchange, c.currency) != (
                contract.symbol,
                contract.exchange,
                contract.currency,
            ) or det.contractMonth != contract.lastTradeDateOrContractMonth:
                continue
            if contract.tradingClass and contract.tradingClass != c.tradingClass:
                continue
            expired = datetime.strptime(c.lastTradeDateOrContractMonth, "%Y%m%d").date() < today
            if expired and not contract.includeExpired:
                continue
            out.append(det)
        return [replace(d, contract=replace(d.contract)) for d in out]

    # historical data -------------------------------------------------------------------------
    def _end_date(self, end: str) -> date:
        if end == "":
            now_ct = self.now.astimezone(CME_TZ)
            # after 17:00 CT the next trade date's session is open (its partial bar exists)
            return now_ct.date() + timedelta(days=1 if now_ct.hour >= 17 else 0)
        moment = datetime.strptime(end, "%Y%m%d-%H:%M:%S").replace(tzinfo=UTC)  # API UTC form
        return moment.astimezone(CME_TZ).date()

    def reqHistoricalData(
        self,
        contract: FakeContract,
        endDateTime: Any,
        durationStr: str,
        barSizeSetting: str,
        whatToShow: str,
        useRTH: bool,
        formatDate: int = 1,
        keepUpToDate: bool = False,
        chartOptions: Any = (),
        timeout: float = 60,
    ) -> list[FakeBar]:
        self.calls.append(
            (
                "reqHistoricalData",
                {
                    "conId": contract.conId,
                    "end": endDateTime,
                    "duration": durationStr,
                    "bar": barSizeSetting,
                    "what": whatToShow,
                    "rth": useRTH,
                },
            )
        )
        self._need_connection()
        self._maybe_fail("reqHistoricalData")
        assert barSizeSetting == "1 day" and formatDate == 1 and not keepUpToDate
        assert isinstance(endDateTime, str), "pass strings, never dates (local-tz trap)"
        if contract.conId in self.no_data:
            raise FakeRequestError(
                7,
                162,
                "Historical Market Data Service error message:HMDS query returned no data: test",
            )
        if contract.conId in self.warn_321:
            self.errorEvent.emit(7, 321, "Error validating request.-'bW' : cause - test", contract)
            self.clock_s += timeout
            return []
        n, unit = durationStr.split()
        span = int(n) * (365 if unit == "Y" else 1)
        end = self._end_date(endDateTime)
        series = self.bars.get(contract.conId, {})
        bars = [
            FakeBar(d, series[d]) for d in sorted(series) if end - timedelta(days=span) < d <= end
        ]
        queue = self.stall.get(contract.conId)
        if queue:
            self.clock_s += timeout  # asyncio.wait_for fired: the timeout elapsed
            cut = queue.pop(0)  # bars arrive oldest first: a stall cuts the tail off
            return bars[:cut] if isinstance(cut, int) else [b for b in bars if b.date < cut]
        return bars

    # orders ----------------------------------------------------------------------------------
    def _contract(self, con_id: int) -> FakeContract:
        return next(d.contract for d in self.listings.values() if d.contract.conId == con_id)

    def _last_close(self, con_id: int) -> float:
        series = self.bars.get(con_id) or {EPOCH: 1.0}
        return series[max(series)]

    def placeOrder(self, contract: FakeContract, order: FakeOrder) -> FakeTrade:
        self.calls.append(("placeOrder", {"conId": contract.conId, "order": replace(order)}))
        self._need_connection()
        self._seq += 1
        order.orderId = order.permId = self._seq
        qty = float(order.totalQuantity)
        trade = FakeTrade(contract, order, FakeStatus("Submitted", 0.0, qty))
        self.trades.append(trade)
        if self.fill_mode == "immediate":
            self._fill(trade)
        return trade

    def _fill(self, trade: FakeTrade) -> None:
        order, con_id = trade.order, trade.contract.conId
        price = order.lmtPrice if order.orderType == "LMT" else self._last_close(con_id)
        qty = float(order.totalQuantity)
        side = "BOT" if order.action == "BUY" else "SLD"
        ex = FakeExecution(
            f"E{self._seq:04d}.{len(self.executions)}",
            self.now,
            order.account,
            side,
            qty,
            price,
            order.orderRef,
        )
        fill = FakeFill(trade.contract, ex, FakeCommission(ex.execId, 0.62 * qty), self.now)
        trade.fills.append(fill)
        trade.orderStatus = FakeStatus("Filled", qty, 0.0, price)
        self.executions.append(fill)
        sign = 1 if order.action == "BUY" else -1
        self.positions_by_con[con_id] = self.positions_by_con.get(con_id, 0.0) + sign * qty

    def fill_open_orders(self) -> None:
        """Fill every open order now, outside the trade objects' wait (a 'late' fill)."""
        for trade in self.trades:
            if not trade.isDone():
                self._fill(trade)

    def positions(self, account: str = "") -> list[FakePosition]:
        self._need_connection()
        return [
            FakePosition(account, self._contract(c), q, 0.0)
            for c, q in sorted(self.positions_by_con.items())
            if q
        ]

    def openTrades(self) -> list[FakeTrade]:
        return [t for t in self.trades if not t.isDone()]

    def reqExecutions(self, execFilter: Any = None) -> list[FakeFill]:
        today = self.now.astimezone(CME_TZ).date()
        return [f for f in self.executions if f.time.astimezone(CME_TZ).date() == today]

    def reqCompletedOrders(self, apiOnly: bool) -> list[FakeTrade]:
        self.calls.append(("reqCompletedOrders", {"apiOnly": apiOnly}))
        self._need_connection()
        if not self.completed_visible:
            return []
        # as ib_async 2.1.0 wrapper.completedOrder builds them: OrderStatus carries only the
        # status, the filled quantity is order.filledQuantity, and there are no fills
        return [
            FakeTrade(
                replace(t.contract),
                replace(t.order, filledQuantity=t.orderStatus.filled),
                FakeStatus(t.orderStatus.status, 0.0, 0.0),
            )
            for t in self.trades
            if t.isDone()
        ]

    def managedAccounts(self) -> list[str]:
        return list(self.accounts)

    def reqMarketDataType(self, marketDataType: int) -> None:
        self.calls.append(("reqMarketDataType", {"type": marketDataType}))

    def sleep(self, secs: float) -> None:
        self.slept.append(secs)
        self.clock_s += secs

    def count(self, method: str) -> int:
        return sum(1 for name, _ in self.calls if name == method)
