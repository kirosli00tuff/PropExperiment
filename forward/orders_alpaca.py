"""E22-F2's optional shadow order route on Alpaca paper (AlpacaCoder, Stage E.24 Part C).

E22-F2's registered verdict is its paper book (forward/runner_f2.py and its ledger). This route
only mirrors the book in an Alpaca PAPER account and keeps its own record: after the F2 runner
writes day t's record, it reads that record's "date", "targets" and "positions" (nothing else),
compares the targets with the shadow account's positions, places the changes as paper orders for
the next session, and appends orders and fills to a SEPARATE shadow ledger (forward.ledger.Ledger).
It never writes to, and refuses any path equal to, the E22-F2 ledger. Off by default
(forward/shadow_f2.json, "enabled": false).

Modes (facts: reports/stage_e24_briefs/facts/alpaca_facts.md, cited as A5, A8):

- "moc_whole" (default): market-on-close orders, time_in_force "cls". CLS orders take whole
  shares only and fractional orders take time_in_force "day" only (A5, A8), so every target is
  rounded to whole shares (half away from zero). CLS orders submitted between 15:50 and 19:00 ET
  are rejected; after 19:00 ET they queue for the next day's closing auction (A8). The route
  submits from 19:00 ET on t until 15:45 ET on the next session (a 5-minute margin).
- "fractional_day": fractional market orders for longs (up to 9 decimals, A5), whole shares for
  shorts (Alpaca: "We do not support short sales in fractional orders. All fractional sell orders
  are marked long.", fractional-trading page line 84, fact check correction 1), time_in_force
  "day". Submitted after t's close they queue for the next session, so they fill near its OPEN,
  not its close (alpaca-py 0.44.0 TimeInForce docstring). Allowed from 16:05 ET on t until
  09:25 ET on the next session.

A long-to-short change is split into a close-the-long order and a whole-share short order; a
short-to-long change into a cover and a buy. Opening shorts need a shortable, easy-to-borrow asset
and shorting enabled on the account (A6). Paper fills are simulated against the quote, probably
not the auction price (A8): the shadow ledger is a record of what Alpaca paper did, nothing more.

Client order ids are deterministic (``e22f2-YYYYMMDD-SYMBOL-n``), so a rerun after a crash finds
the orders it already placed instead of placing them twice. Each run lists the open orders and
the orders submitted in the last ORDERS_LOOKBACK_DAYS days (one page each), and looks up every
older pending order of the shadow ledger by its client order id, so the queries do not grow with
the ledger.
"""

from __future__ import annotations

import json
import math
import os
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from typing import Any, Protocol
from zoneinfo import ZoneInfo

from forward.ledger import Ledger, LedgerOrderError
from forward.sources_alpaca import _INSTALL_HINT, paper_credentials

NY = ZoneInfo("America/New_York")
PAPER_TRADING_URL = "https://paper-api.alpaca.markets"  # A1, A10 (BaseURL.TRADING_PAPER)
DEFAULT_CONFIG_PATH = Path(__file__).with_name("shadow_f2.json")

MODES = ("moc_whole", "fractional_day")
TIME_IN_FORCE = {"moc_whole": "cls", "fractional_day": "day"}
CLS_REJECT_FROM_NY = time(15, 50)  # A8: CLS submitted after 15:50 and before 19:00 ET rejected
CLS_QUEUE_FROM_NY = time(19, 0)  # A8: after 19:00 ET queued for the next day's closing auction
SESSION_OPEN_NY = time(9, 30)
SESSION_CLOSE_NY = time(16, 0)
SUBMIT_MARGIN = timedelta(minutes=5)
FRACTION_DECIMALS = 9  # A5: qty takes up to 9 decimal places
QTY_EPS = 1e-9
CLIENT_ID_PREFIX = "e22f2"
ORDERS_LIMIT = 500  # per get_orders call; a full page is treated as possibly truncated
# The `all` query covers orders submitted from (run date - ORDERS_LOOKBACK_DAYS) on: this date's
# own orders (a rerun after a crash) and recent ones. Pending orders older than that are looked
# up one by one by client order id, so the query never grows with the ledger (C4a S2).
ORDERS_LOOKBACK_DAYS = 3
NOT_FOUND_STATUS = 404
FINAL_STATUSES = frozenset({"filled", "canceled", "expired", "rejected", "replaced"})
NOT_OPEN_STATUSES = FINAL_STATUSES | {"done_for_day"}
PENDING_RESULTS = frozenset({"submitted", "existing", "error"})
F2_FIELDS = {"date": "date", "targets": "targets", "positions": "positions"}
CONFIG_KEYS = frozenset({"enabled", "ledger_path", "mode", "closed_dates", "comment"})


class ShadowError(RuntimeError):
    """A precondition failed; nothing was submitted and no shadow record was written."""


class LiveEndpointRefused(ShadowError):  # noqa: N818
    """The trading client is not, or cannot be shown to be, on the paper endpoint."""


class LedgerPathRefused(ShadowError):  # noqa: N818
    """The shadow ledger path is the E22-F2 ledger (or the same file under another name)."""


class ShadowWindowError(ShadowError):
    """Outside the submission window for the next session's orders."""


class TradingClientLike(Protocol):
    """The part of alpaca-py 0.44.0's TradingClient(paper=True) the route uses."""

    def get_account(self) -> Any: ...

    def get_all_positions(self) -> list[Any]: ...

    def get_asset(self, symbol_or_asset_id: str) -> Any: ...

    def get_orders(self, filter: Any = None) -> list[Any]: ...  # noqa: A002

    def get_order_by_client_id(self, client_id: str) -> Any: ...

    def submit_order(self, order_data: Any) -> Any: ...


# --- config --------------------------------------------------------------------------------


@dataclass(frozen=True)
class ShadowConfig:
    enabled: bool
    ledger_path: Path
    mode: str = "moc_whole"
    closed_dates: frozenset[date] = frozenset()

    def __post_init__(self) -> None:
        if not isinstance(self.enabled, bool):
            raise ValueError(f"enabled must be true or false, got {self.enabled!r}")
        if self.mode not in MODES:
            raise ValueError(f"mode must be one of {MODES}, got {self.mode!r}")
        object.__setattr__(self, "ledger_path", Path(self.ledger_path))
        object.__setattr__(self, "closed_dates", frozenset(self.closed_dates))


def load_shadow_config(path: Path | str = DEFAULT_CONFIG_PATH) -> ShadowConfig:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: expected a JSON object")
    unknown = set(raw) - CONFIG_KEYS
    if unknown:
        raise ValueError(f"{path}: unknown keys {sorted(unknown)}")
    if not raw.get("ledger_path"):
        raise ValueError(f"{path}: ledger_path is required")
    closed = frozenset(date.fromisoformat(d) for d in raw.get("closed_dates", []))
    return ShadowConfig(raw.get("enabled"), Path(raw["ledger_path"]), raw.get("mode"), closed)


# --- the F2 record -------------------------------------------------------------------------


@dataclass(frozen=True)
class F2Input:
    date: date
    targets: Mapping[str, float]
    positions: Mapping[str, float]


def _shares(raw: Any, what: str) -> dict[str, float]:
    if not isinstance(raw, Mapping):
        raise ValueError(f"F2 record: {what} must be a mapping of symbol -> shares")
    out = {}
    for symbol, qty in raw.items():
        if isinstance(qty, bool) or not isinstance(qty, int | float) or not math.isfinite(qty):
            raise ValueError(f"F2 record: {what}[{symbol!r}] must be a finite number")
        out[str(symbol)] = float(qty)
    return dict(sorted(out.items()))


def f2_fields(record: Mapping[str, Any]) -> F2Input:
    """The only place that knows the F2 runner's field names (F2_FIELDS)."""
    for key in F2_FIELDS.values():
        if key not in record:
            raise ValueError(f"F2 record has no {key!r} field")
    return F2Input(
        date.fromisoformat(record[F2_FIELDS["date"]]),
        _shares(record[F2_FIELDS["targets"]], "targets"),
        _shares(record[F2_FIELDS["positions"]], "positions"),
    )


# --- order construction --------------------------------------------------------------------


@dataclass(frozen=True)
class PlannedOrder:
    symbol: str
    side: str  # "buy" | "sell"
    qty: float
    intent: str  # buy_to_open | sell_to_close | sell_to_open | buy_to_close
    time_in_force: str
    client_order_id: str


def _whole(x: float) -> float:
    return math.copysign(math.floor(abs(x) + 0.5), x) + 0.0


def _borrowable(asset: Any) -> bool:
    """A6: shorts need a shortable asset; easy-to-borrow names carry no locate or borrow fee."""
    return bool(getattr(asset, "shortable", False) and getattr(asset, "easy_to_borrow", False))


def _is_whole(x: float) -> bool:
    return abs(x - round(x)) < QTY_EPS


def _desired(symbol: str, target: float, mode: str, asset: Any, notes: list[str]) -> float:
    if target < 0 or mode == "moc_whole":
        return _whole(target)
    if asset is not None and not getattr(asset, "fractionable", True):
        notes.append(f"{symbol}: not fractionable; long target {target} rounded to whole shares")
        return _whole(target)
    return round(target, FRACTION_DECIMALS) + 0.0


def _legs(c: float, d: float, mode: str) -> list[tuple[str, float, str]]:
    """(side, qty, intent) legs that move the position from c to d."""
    if abs(d - c) < QTY_EPS:
        return []
    whole = mode == "moc_whole"
    if c >= 0 and d >= 0:
        qty = abs(d - c)
        qty = _whole(qty) if whole else round(qty, FRACTION_DECIMALS)
        side = "buy" if d > c else "sell"
        return [(side, qty, "buy_to_open" if side == "buy" else "sell_to_close")] if qty else []
    if c <= 0 and d <= 0:
        qty = _whole(abs(d - c))
        side = "buy" if d > c else "sell"
        return [(side, qty, "buy_to_close" if side == "buy" else "sell_to_open")] if qty else []
    if c > 0:  # long -> short
        close = math.floor(c + QTY_EPS) if whole else round(c, FRACTION_DECIMALS)
        return [("sell", float(close), "sell_to_close"), ("sell", abs(d), "sell_to_open")]
    return [("buy", _whole(abs(c)), "buy_to_close"), ("buy", d, "buy_to_open")]  # short -> long


def plan_orders(
    trade_date: date,
    targets: Mapping[str, float],
    current: Mapping[str, float],
    *,
    mode: str,
    assets: Mapping[str, Any],
    shorting_enabled: bool = True,
) -> tuple[tuple[PlannedOrder, ...], tuple[str, ...]]:
    """Orders that move the shadow account from ``current`` to ``targets`` (shares)."""
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}")
    notes: list[str] = []
    orders: list[PlannedOrder] = []
    for symbol in sorted(set(current) - set(targets)):
        notes.append(f"{symbol}: held {current[symbol]} but not in the targets; unmanaged")
    for symbol, target in sorted(targets.items()):
        asset = assets.get(symbol)
        c = float(current.get(symbol, 0.0))
        d = _desired(symbol, target, mode, asset, notes)
        if mode == "moc_whole" and not _is_whole(c):
            notes.append(f"{symbol}: fractional position {c} in moc_whole mode; residual kept")
        n = 0
        for side, qty, intent in _legs(c, d, mode):
            if qty < QTY_EPS:
                continue
            if intent == "sell_to_open":
                ok = shorting_enabled and (asset is None or _borrowable(asset))
                if not ok:
                    notes.append(
                        f"{symbol}: opening short skipped (shorting_enabled={shorting_enabled}, "
                        f"shortable={getattr(asset, 'shortable', None)}, "
                        f"easy_to_borrow={getattr(asset, 'easy_to_borrow', None)})"
                    )
                    continue
            n += 1
            cid = f"{CLIENT_ID_PREFIX}-{trade_date:%Y%m%d}-{symbol}-{n}"
            orders.append(PlannedOrder(symbol, side, float(qty), intent, TIME_IN_FORCE[mode], cid))
    return tuple(orders), tuple(notes)


# --- windows, paths, endpoints -------------------------------------------------------------


def _next_session(day: date, closed: Iterable[date] = ()) -> date:
    closed = frozenset(closed)
    nxt = day + timedelta(days=1)
    while nxt.weekday() >= 5 or nxt in closed:
        nxt += timedelta(days=1)
    return nxt


def _at(day: date, at: time) -> datetime:
    return datetime.combine(day, at, NY)


def submission_allowed(
    now: datetime, trade_date: date, mode: str, closed: Iterable[date] = ()
) -> bool:
    """Whether orders for the session after ``trade_date`` may be submitted at ``now``."""
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("now must be a time zone aware datetime")
    nxt = _next_session(trade_date, closed)
    if mode == "moc_whole":
        lo, hi = _at(trade_date, CLS_QUEUE_FROM_NY), _at(nxt, CLS_REJECT_FROM_NY) - SUBMIT_MARGIN
        if not lo <= now < hi:
            return False
        # between 15:50 and 19:00 ET of any day CLS is rejected (A8); days in between t and the
        # next session (weekends, holidays) have no documented queue rule
        local = now.astimezone(NY)
        return local.date() in (trade_date, nxt)
    lo = _at(trade_date, SESSION_CLOSE_NY) + SUBMIT_MARGIN
    hi = _at(nxt, SESSION_OPEN_NY) - SUBMIT_MARGIN
    return lo <= now < hi and now.astimezone(NY).date() in (trade_date, nxt)


def check_ledger_paths(shadow_path: Path | str, f2_ledger_path: Path | str) -> None:
    """Refuse a shadow ledger that is the E22-F2 ledger under any name."""
    if not str(shadow_path).strip():
        raise LedgerPathRefused("the shadow ledger path is empty")
    a, b = Path(shadow_path), Path(f2_ledger_path)
    if a.resolve() == b.resolve() or os.path.abspath(a) == os.path.abspath(b):
        raise LedgerPathRefused(f"shadow ledger {a} is the E22-F2 ledger {b}")
    if a.exists() and b.exists() and os.path.samefile(a, b):
        raise LedgerPathRefused(f"shadow ledger {a} is the same file as the E22-F2 ledger {b}")


def _url(client: Any) -> str | None:
    url = getattr(client, "_base_url", None)
    url = getattr(url, "value", url)
    return url if isinstance(url, str) else None


def assert_paper(client: Any) -> None:
    url = _url(client)
    if url is None or url.rstrip("/") != PAPER_TRADING_URL:
        raise LiveEndpointRefused(f"trading client base URL {url!r} is not {PAPER_TRADING_URL}")


def make_trading_client(
    environ: Mapping[str, str] | None = None, *, paper: bool = True, url_override: str | None = None
) -> TradingClientLike:
    """alpaca-py's TradingClient on the PAPER endpoint only (lazy import; keys from env)."""
    if paper is not True:
        raise LiveEndpointRefused("the shadow route trades on Alpaca paper only")
    if url_override is not None and url_override.rstrip("/") != PAPER_TRADING_URL:
        raise LiveEndpointRefused(f"url_override {url_override!r} is not the paper endpoint")
    key_id, secret = paper_credentials(environ)
    try:
        from alpaca.trading.client import TradingClient
    except ImportError as exc:
        raise ImportError(_INSTALL_HINT) from exc
    client = TradingClient(api_key=key_id, secret_key=secret, paper=True)
    assert_paper(client)
    return client


def market_order_request(
    *, symbol: str, qty: float, side: str, time_in_force: str, client_order_id: str
) -> Any:
    """alpaca-py's MarketOrderRequest (lazy import)."""
    try:
        from alpaca.trading.enums import OrderSide, TimeInForce
        from alpaca.trading.requests import MarketOrderRequest
    except ImportError as exc:
        raise ImportError(_INSTALL_HINT) from exc
    return MarketOrderRequest(
        symbol=symbol,
        qty=qty,
        side=OrderSide(side),
        time_in_force=TimeInForce(time_in_force),
        client_order_id=client_order_id,
    )


def orders_query(*, status: str, after: datetime | None) -> Any:
    """alpaca-py's GetOrdersRequest (lazy import)."""
    try:
        from alpaca.trading.enums import QueryOrderStatus
        from alpaca.trading.requests import GetOrdersRequest
    except ImportError as exc:
        raise ImportError(_INSTALL_HINT) from exc
    return GetOrdersRequest(
        status=QueryOrderStatus(status), after=after, limit=ORDERS_LIMIT, nested=False
    )


# --- helpers for SDK objects ---------------------------------------------------------------


def _value(x: Any) -> Any:
    return getattr(x, "value", x)


def _num(x: Any) -> float | None:
    if x is None or x == "":
        return None
    out = float(x)
    return out if math.isfinite(out) else None


def _iso(x: Any) -> str | None:
    if isinstance(x, datetime):
        return x.astimezone(UTC).isoformat() if x.tzinfo else x.isoformat()
    return None if x is None else str(x)


def _describe(exc: BaseException) -> str:
    status = getattr(exc, "status_code", None)
    head = type(exc).__name__ + (f" HTTP {status}" if isinstance(status, int) else "")
    return f"{head}: {' '.join(str(exc).split())[:200]}"


def account_positions(client: TradingClientLike) -> dict[str, float]:
    out = {}
    for p in client.get_all_positions():
        qty = abs(float(p.qty))
        out[str(p.symbol)] = -qty if str(_value(p.side)).lower() == "short" else qty
    return dict(sorted(out.items()))


# --- the route -----------------------------------------------------------------------------


class ShadowRoute:
    def __init__(
        self,
        config: ShadowConfig,
        f2_ledger_path: Path | str,
        client: TradingClientLike | None = None,
        *,
        client_factory: Callable[[], TradingClientLike] = make_trading_client,
        order_factory: Callable[..., Any] = market_order_request,
        query_factory: Callable[..., Any] = orders_query,
        clock: Callable[[], datetime] | None = None,
    ):
        check_ledger_paths(config.ledger_path, f2_ledger_path)
        self.config = config
        self.f2_ledger_path = Path(f2_ledger_path)
        self._client = client
        self._client_factory = client_factory
        self._order_factory = order_factory
        self._query_factory = query_factory
        self._clock = clock or (lambda: datetime.now(UTC))

    def run(self, f2_record: Mapping[str, Any]) -> dict[str, Any] | None:
        """Mirror one F2 record; returns the stored shadow record, or None when disabled."""
        if not self.config.enabled:
            return None
        check_ledger_paths(self.config.ledger_path, self.f2_ledger_path)
        f2 = f2_fields(f2_record)
        ledger = Ledger(self.config.ledger_path)
        history = ledger.records()
        if history and f2.date <= date.fromisoformat(history[-1]["date"]):
            raise LedgerOrderError(
                f"{f2.date} is not after the last shadow record {history[-1]['date']}; "
                "nothing was submitted"
            )
        now = self._clock()
        if not submission_allowed(now, f2.date, self.config.mode, self.config.closed_dates):
            raise ShadowWindowError(
                f"{now.isoformat()} is outside the {self.config.mode} window after {f2.date}"
            )
        client = self._client if self._client is not None else self._client_factory()
        assert_paper(client)
        account = self._check_account(client)
        orders_seen = self._orders(client, history, f2.date)
        pending = _pending_ids(history)
        today_prefix = f"{CLIENT_ID_PREFIX}-{f2.date:%Y%m%d}-"
        self._refuse_open_orders(orders_seen, today_prefix)
        fills, still_pending = _fills(pending, orders_seen)
        current = account_positions(client)
        assets = {s: client.get_asset(s) for s in f2.targets}
        planned, notes = plan_orders(
            f2.date,
            f2.targets,
            current,
            mode=self.config.mode,
            assets=assets,
            shorting_enabled=bool(getattr(account, "shorting_enabled", False)),
        )
        results = [self._submit(client, o, orders_seen) for o in planned]
        record = {
            "date": f2.date.isoformat(),
            "route": "alpaca_paper_shadow_e22f2",
            "mode": self.config.mode,
            "f2_record_sha256": f2_record.get("record_sha256"),
            "run_at_utc": now.astimezone(UTC).isoformat(),
            "account": {
                k: _value(getattr(account, k, None))
                for k in (
                    "status", "equity", "buying_power", "multiplier", "shorting_enabled",
                    "pattern_day_trader", "daytrade_count",  # A7: PDT status not settled; logged
                )
            },
            "targets": dict(f2.targets),
            "book_positions": dict(f2.positions),
            "account_positions": current,
            "orders": results,
            "fills": fills,
            "pending": still_pending,
            "notes": list(notes),
        }
        return ledger.append(record)

    # -- internals -----------------------------------------------------------------------

    def _check_account(self, client: TradingClientLike) -> Any:
        account = client.get_account()
        status = str(_value(getattr(account, "status", ""))).upper()
        if getattr(account, "trading_blocked", False) or getattr(account, "account_blocked", False):
            raise ShadowError("the paper account is blocked (trading_blocked/account_blocked)")
        if status != "ACTIVE":
            raise ShadowError(f"the paper account status is {status!r}, not ACTIVE")
        return account

    def _orders(self, client: TradingClientLike, history: list[dict], day: date) -> dict:
        """Open orders, orders submitted since ``day - ORDERS_LOOKBACK_DAYS``, and each pending
        order of the history that those two queries did not return (by client order id)."""
        after = datetime.combine(day - timedelta(days=ORDERS_LOOKBACK_DAYS), time(0), NY)
        seen: dict[str, Any] = {}
        for status, since in (("open", None), ("all", after)):
            batch = client.get_orders(filter=self._query_factory(status=status, after=since))
            if len(batch) >= ORDERS_LIMIT:
                raise ShadowError(f"get_orders({status}) returned a full page; possibly truncated")
            for o in batch:
                seen[str(o.client_order_id)] = o
        for cid in _pending_ids(history):
            if cid not in seen:
                found = _order_by_client_id(client, cid)
                if found is not None:
                    seen[cid] = found
        return seen

    @staticmethod
    def _refuse_open_orders(orders_seen: Mapping[str, Any], today_prefix: str) -> None:
        for cid, o in orders_seen.items():
            if cid.startswith(today_prefix):
                continue  # this date's own orders (a rerun after a crash)
            if str(_value(o.status)).lower() not in NOT_OPEN_STATUSES:
                raise ShadowError(
                    f"open order {cid} ({_value(o.status)}) on {o.symbol}: positions do not "
                    "reflect it yet; resolve it before the shadow route runs"
                )

    def _submit(
        self, client: TradingClientLike, o: PlannedOrder, orders_seen: Mapping[str, Any]
    ) -> dict[str, Any]:
        entry: dict[str, Any] = {
            "client_order_id": o.client_order_id,
            "symbol": o.symbol,
            "side": o.side,
            "qty": o.qty,
            "intent": o.intent,
            "type": "market",
            "time_in_force": o.time_in_force,
            "result": None,
            "order_id": None,
            "status": None,
            "error": None,
        }
        existing = orders_seen.get(o.client_order_id)
        if existing is not None:
            entry.update(
                result="existing", order_id=str(existing.id), status=_value(existing.status)
            )
            return entry
        request = self._order_factory(
            symbol=o.symbol,
            qty=o.qty,
            side=o.side,
            time_in_force=o.time_in_force,
            client_order_id=o.client_order_id,
        )
        try:
            placed = client.submit_order(request)
        except Exception as exc:  # noqa: BLE001 (recorded, not raised: a shadow record)
            status = getattr(exc, "status_code", None)
            definite = isinstance(status, int) and 400 <= status < 500
            entry.update(result="rejected" if definite else "error", error=_describe(exc))
            return entry
        entry.update(result="submitted", order_id=str(placed.id), status=_value(placed.status))
        return entry


def _order_by_client_id(client: TradingClientLike, cid: str) -> Any | None:
    """The order with this client order id, or None when the account has none (HTTP 404: an
    order whose submission failed before it reached Alpaca stays pending, as before)."""
    try:
        return client.get_order_by_client_id(cid)
    except Exception as exc:  # noqa: BLE001 (the client boundary; classified here)
        if getattr(exc, "status_code", None) == NOT_FOUND_STATUS:
            return None
        raise ShadowError(f"get_order_by_client_id({cid}): {_describe(exc)}") from exc


def _pending_ids(history: list[dict]) -> list[str]:
    pending: dict[str, None] = {}
    for record in history:
        for f in record.get("fills", []):
            pending.pop(f["client_order_id"], None)
        for o in record.get("orders", []):
            if o.get("result") in PENDING_RESULTS:
                pending[o["client_order_id"]] = None
    return list(pending)


def _fills(pending: list[str], orders_seen: Mapping[str, Any]) -> tuple[list[dict], list[str]]:
    fills, still = [], []
    for cid in pending:
        o = orders_seen.get(cid)
        if o is None or str(_value(o.status)).lower() not in FINAL_STATUSES:
            still.append(cid)
            continue
        fills.append(
            {
                "client_order_id": cid,
                "status": str(_value(o.status)).lower(),
                "filled_qty": _num(getattr(o, "filled_qty", None)) or 0.0,
                "filled_avg_price": _num(getattr(o, "filled_avg_price", None)),
                "filled_at": _iso(getattr(o, "filled_at", None)),
            }
        )
    return fills, still
