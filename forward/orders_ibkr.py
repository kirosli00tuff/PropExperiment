"""Optional shadow order route of E22-F1 on an IBKR paper account (Stage E.24, IBKRCoder).

E22-F1's registered verdict is the paper book of its freeze (fills at the next settlement, in
the E22-F1 ledger). This route only mirrors that book in an IBKR PAPER account and records what
the broker did, in a SEPARATE shadow ledger (forward.ledger.Ledger: append-only, sha256 chain).

Contract with the frozen runner:
- It runs after the runner has written trade date t's record. It READS the E22-F1 ledger (a
  verified parse of the file's text) and never writes it, never changes the runner's inputs.
- Its ledger path can never be the E22-F1 ledger (same resolved path, a symlink to it or a hard
  link to it is refused), and every shadow record carries its own schema, so an E22-F1 record
  in the shadow file is refused too.
- Off by default: forward/shadow_f1.json has "enabled": false.

One run for trade date t:
1. Refuse unless enabled, the account looks like a paper account (prefix DU, listed in the
   gateway's managed accounts) and the port is not a default live port; refuse while shadow
   orders of an earlier run are still open.
2. If the shadow ledger already has a record for t, return it (no orders: a re-run never
   duplicates orders).
3. Targets = the record's orders (the new target positions) or else its positions, each in the
   record's reference contract. Current = the paper account's positions, identified by conId.
4. Orders = target minus current per contract (closing legs first), as MKT (default) or LMT at
   the record's settlement +- limit_offset_ticks ticks (BUY above, SELL below), time in force
   from the config. Orders are placed once, never retried.
5. Wait up to fill_wait_s for fills, then append one record: targets, positions before, orders
   with their status, fills (price, time, commission, contract) and late fills of earlier
   shadow orders found through reqExecutions. The account id is never written or printed.
6. Late fills past the executions' retention (S5, wave 3). IB returns only the current day's
   executions [unverified boundary], so a fill that came after a record (the CBOT grains open
   at 19:00 CT, after an 18:00 CT run) can be gone by the next run. Every earlier shadow order
   that its record left short of its quantity is therefore reconciled once, against the
   executions and then reqCompletedOrders: shares still unaccounted for that the completed
   order shows filled go to late_fills_unretained (quantity only: ib_async's completed orders
   carry no price or commission), a completed order with nothing more filled goes to
   closed_orders, and an order with no trace at all goes to unresolved_orders. Nothing is
   dropped silently; positions_before always shows the account's actual holdings.
"""

from __future__ import annotations

import json
import math
import os
import time as _time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, fields
from datetime import date, datetime
from decimal import ROUND_HALF_EVEN, Decimal
from pathlib import Path
from typing import Any

from forward import rolls as R
from forward.ibkr_gateway import ENV_ACCOUNT, ConnectionParams, GatewaySession, IBKRError, Vendor
from forward.ledger import Ledger, parse_chain
from forward.sources_ibkr import IB_SPECS, ContractResolver, ResolvedContract

SHADOW_SCHEMA = "E22-F1-shadow/1"
E22_SCHEMA = "E22-F1-ledger/1"
DEFAULT_SHADOW_CONFIG = Path(__file__).with_name("shadow_f1.json")
ORDER_TYPES = ("MKT", "LMT")
TIME_IN_FORCE = ("DAY", "GTC")
PAPER_ACCOUNT_PREFIX = "DU"  # IBKR paper account ids [unverified: not in ibkr_facts.md]
LIVE_PORTS = frozenset({4001, 7496})  # I1: IB Gateway live 4001, TWS live 7496 (defaults)
META_KEYS = frozenset({"schema", "status", "written_by", "doc"})
UNSET_LIMIT = 1e300  # IB sends DBL_MAX (1.797e308) for "unset" doubles


class ShadowRouteError(IBKRError):
    """The shadow route refused to run or could not finish (the E22-F1 ledger is untouched)."""


@dataclass(frozen=True)
class ShadowConfig:
    enabled: bool = False
    order_type: str = "MKT"
    limit_offset_ticks: int = 0
    time_in_force: str = "DAY"
    fill_wait_s: float = 60.0
    poll_s: float = 1.0
    order_ref: str = "E22F1-shadow"
    shadow_ledger: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.enabled, bool):
            raise ShadowRouteError("shadow config: enabled must be true or false")
        if self.order_type not in ORDER_TYPES:
            raise ShadowRouteError(f"shadow config: order_type must be one of {ORDER_TYPES}")
        if self.time_in_force not in TIME_IN_FORCE:
            raise ShadowRouteError(f"shadow config: time_in_force must be one of {TIME_IN_FORCE}")
        if not isinstance(self.limit_offset_ticks, int) or self.limit_offset_ticks < 0:
            raise ShadowRouteError("shadow config: limit_offset_ticks must be an int >= 0")
        if not (self.fill_wait_s >= 0 and self.poll_s > 0):
            raise ShadowRouteError("shadow config: fill_wait_s >= 0 and poll_s > 0")
        if self.enabled and not self.shadow_ledger:
            raise ShadowRouteError("shadow config: shadow_ledger is required when enabled")


def load_shadow_config(path: Path | str = DEFAULT_SHADOW_CONFIG) -> ShadowConfig:
    with open(path, encoding="utf-8") as fh:
        raw = json.load(fh)
    known = {f.name for f in fields(ShadowConfig)}
    settings = {k: v for k, v in raw.items() if k in known}
    unknown = sorted(k for k in raw if k not in known | META_KEYS and not k.startswith("_"))
    if unknown:
        raise ShadowRouteError(f"shadow config: unknown keys {unknown}")
    return ShadowConfig(**settings)


def check_distinct_paths(shadow: Path | str, e22: Path | str) -> None:
    """Refuse a shadow ledger path that is, or links to, the E22-F1 ledger."""
    a, b = Path(shadow).resolve(), Path(e22).resolve()
    if a == b:
        raise ShadowRouteError("the shadow ledger path is the E22-F1 ledger path; refused")
    if a.exists() and b.exists() and os.path.samefile(a, b):
        raise ShadowRouteError("the shadow ledger is a hard link to the E22-F1 ledger; refused")


def read_e22_records(path: Path | str) -> list[dict[str, Any]]:
    """The E22-F1 ledger's records, read-only (chain verified)."""
    with open(path, encoding="ascii") as fh:
        return parse_chain(fh.read())


def target_book(record: Mapping[str, Any]) -> dict[str, tuple[str, int]]:
    """{instrument: (reference contract, target qty)} from one E22-F1 record."""
    out = {}
    for inst, pos in sorted(record["positions"].items()):
        qty = int(record["orders"].get(inst, pos["qty"]))
        if pos["contract"] is None:
            if qty:
                raise ShadowRouteError(f"{inst}: target {qty} without a reference contract")
            continue
        out[inst] = (pos["contract"], qty)
    return out


@dataclass(frozen=True)
class PlannedOrder:
    instrument: str
    contract_id: str
    delta: int


def plan_orders(
    targets: Mapping[str, tuple[str, int]], current: Mapping[str, Mapping[str, int]]
) -> list[PlannedOrder]:
    """Target minus current per contract; legs in contracts that are not the target go first."""
    plan = []
    for inst in sorted(set(targets) | set(current)):
        cid_t, qty_t = targets.get(inst, (None, 0))
        want = {cid_t: qty_t} if cid_t and qty_t else {}
        have = current.get(inst, {})
        for cid in sorted(set(want) | set(have), key=lambda c: (c in want, c)):
            delta = want.get(cid, 0) - have.get(cid, 0)
            if delta:
                plan.append(PlannedOrder(inst, cid, delta))
    return plan


def _num(x: Any) -> float | None:
    try:
        value = float(x)
    except (TypeError, ValueError):
        return None
    return value if math.isfinite(value) and abs(value) < UNSET_LIMIT else None


def _when(x: Any) -> str | None:
    return x.isoformat() if isinstance(x, (datetime, date)) else (str(x) if x else None)


class ShadowRoute:
    def __init__(
        self,
        config: ShadowConfig,
        session: GatewaySession,
        resolver: ContractResolver,
        vendor: Vendor,
        *,
        e22_ledger_path: Path | str,
        ticks: Mapping[str, float],
        clock: Callable[[], float] = _time.monotonic,
    ):
        if not config.enabled:
            raise ShadowRouteError("the shadow route is disabled (shadow_f1.json enabled: false)")
        check_distinct_paths(str(config.shadow_ledger), e22_ledger_path)
        self.config, self.session, self.resolver, self.vendor = config, session, resolver, vendor
        self.e22_path = Path(e22_ledger_path)
        self.shadow = Ledger(str(config.shadow_ledger))
        self.ticks = dict(ticks)
        self._clock = clock

    # -- guards --------------------------------------------------------------------------------
    @staticmethod
    def _check_params(params: ConnectionParams) -> str:
        """Account prefix and port, before any connection (N4, wave 3)."""
        account = params.account or ""
        if not account.startswith(PAPER_ACCOUNT_PREFIX):
            raise ShadowRouteError(f"{ENV_ACCOUNT} is not a paper account id (value withheld)")
        if params.port in LIVE_PORTS:
            raise ShadowRouteError("the gateway port is a default LIVE port; shadow route refused")
        return account

    def _check_managed(self, account: str) -> str:
        if account not in self.session.gateway.managedAccounts():
            raise ShadowRouteError(f"{ENV_ACCOUNT} is not among the gateway's managed accounts")
        return account

    def _shadow_records(self) -> list[dict[str, Any]]:
        check_distinct_paths(self.shadow.path, self.e22_path)
        records = self.shadow.records()
        foreign = [r.get("schema") for r in records if r.get("schema") != SHADOW_SCHEMA]
        if foreign:
            raise ShadowRouteError(f"shadow ledger holds non-shadow records {foreign[:2]}")
        return records

    def _open_shadow_orders(self) -> list[Any]:
        return [
            t
            for t in self.session.gateway.openTrades()
            if str(getattr(t.order, "orderRef", "")).startswith(self.config.order_ref)
        ]

    # -- one run -------------------------------------------------------------------------------
    def run(self, trade_date: date) -> dict[str, Any]:
        records = self._shadow_records()
        done = next((r for r in records if r["date"] == trade_date.isoformat()), None)
        if done is not None:
            return done
        if records and records[-1]["date"] > trade_date.isoformat():
            raise ShadowRouteError(f"shadow ledger already runs past {trade_date}")
        e22 = read_e22_records(self.e22_path)
        record = next((r for r in e22 if r["date"] == trade_date.isoformat()), None)
        if record is None:
            raise ShadowRouteError(f"no E22-F1 record for {trade_date}; run the runner first")
        account = self._check_params(self.session.params)
        self.session.ensure_connected()
        self._check_managed(account)
        if self._open_shadow_orders():
            raise ShadowRouteError("open shadow orders from an earlier run exist; resolve them")
        targets = target_book(record)
        current, foreign = self._current(account, targets)
        plan = plan_orders(targets, current)
        trades = [(p, self._place(p, record, account, trade_date)) for p in plan]
        self._wait(trades)
        payload = self._payload(trade_date, record, targets, current, foreign, trades, records)
        return self.shadow.append(payload)

    def _current(
        self, account: str, targets: Mapping[str, tuple[str, int]]
    ) -> tuple[dict[str, dict[str, int]], list[str]]:
        for inst, (cid, _) in targets.items():
            self.resolver.resolve(inst, cid)  # caches conId -> contract for identification
        symbols = {s.symbol for s in IB_SPECS.values()}
        current: dict[str, dict[str, int]] = {}
        foreign = []
        for pos in self.session.gateway.positions(account):
            qty = int(round(float(pos.position)))
            if qty == 0:
                continue
            rc = self.resolver.identify(pos.contract) or self._identify_held(pos.contract)
            if rc is None:
                if getattr(pos.contract, "symbol", None) in symbols:
                    raise ShadowRouteError(
                        f"a position in {getattr(pos.contract, 'localSymbol', '?')} could not be "
                        "mapped to a runner contract; resolve it by hand"
                    )
                foreign.append(str(getattr(pos.contract, "localSymbol", "?")))
                continue
            book = current.setdefault(rc.instrument, {})
            book[rc.contract_id] = book.get(rc.contract_id, 0) + qty
        return current, sorted(foreign)

    def _identify_held(self, contract: Any) -> ResolvedContract | None:
        """Map a held contract outside the cache through its details (contract month)."""
        con_id = int(getattr(contract, "conId", 0) or 0)
        if not con_id:
            return None
        details = self.session.contract_details(
            "reqContractDetails by conId", self.vendor.contract(conId=con_id)
        )
        if len(details) != 1:
            return None
        c, month = details[0].contract, str(getattr(details[0], "contractMonth", ""))
        for inst, spec in IB_SPECS.items():
            if inst not in self.resolver.rolls or c.symbol != spec.symbol or len(month) != 6:
                continue
            try:
                cid = R.contract_id(self.resolver.rolls[inst], int(month[:4]), int(month[4:]))
                rc = self.resolver.resolve(inst, cid)
            except (ValueError, IBKRError):
                return None
            return rc if rc.con_id == con_id else None
        return None

    def _limit_price(
        self, p: PlannedOrder, record: Mapping[str, Any], rc: ResolvedContract
    ) -> float:
        settle = record["prices"].get(p.instrument, {}).get(p.contract_id)
        if settle is None:
            mark = record["positions"].get(p.instrument, {})
            settle = mark.get("mark") if mark.get("contract") == p.contract_id else None
        if settle is None:
            raise ShadowRouteError(f"{p.instrument} {p.contract_id}: no settlement for a limit")
        tick = Decimal(repr(float(self.ticks[p.instrument]))) * rc.price_divisor
        base = Decimal(repr(float(settle))) * rc.price_divisor
        offset = tick * self.config.limit_offset_ticks * (1 if p.delta > 0 else -1)
        steps = ((base + offset) / tick).quantize(Decimal(1), rounding=ROUND_HALF_EVEN)
        return float(steps * tick)

    def _place(self, p: PlannedOrder, record: Mapping[str, Any], account: str, day: date) -> Any:
        rc = self.resolver.resolve(p.instrument, p.contract_id)
        action, qty = ("BUY" if p.delta > 0 else "SELL"), abs(p.delta)
        common = {
            "tif": self.config.time_in_force,
            "account": account,
            "orderRef": f"{self.config.order_ref}:{day.isoformat()}",
        }
        if self.config.order_type == "MKT":
            order = self.vendor.market_order(action, qty, **common)
        else:
            order = self.vendor.limit_order(action, qty, self._limit_price(p, record, rc), **common)
        return self.session.gateway.placeOrder(rc.contract, order)  # once; never retried

    def _wait(self, trades: Sequence[tuple[PlannedOrder, Any]]) -> None:
        deadline = self._clock() + self.config.fill_wait_s
        while any(not t.isDone() for _, t in trades) and self._clock() < deadline:
            self.session.gateway.sleep(self.config.poll_s)

    def _payload(
        self,
        day: date,
        record: Mapping[str, Any],
        targets: Mapping[str, tuple[str, int]],
        current: Mapping[str, Mapping[str, int]],
        foreign: list[str],
        trades: Sequence[tuple[PlannedOrder, Any]],
        records: Sequence[Mapping[str, Any]],
    ) -> dict[str, Any]:
        fills = [self._fill(p.instrument, p.contract_id, f) for p, t in trades for f in t.fills]
        seen = {f["exec_id"] for r in records for f in (*r["fills"], *r["late_fills"])}
        seen |= {f["exec_id"] for f in fills}
        late = self._late_fills(seen)
        unretained, closed, unresolved = self._reconcile(records, late)
        return {
            "schema": SHADOW_SCHEMA,
            "date": day.isoformat(),
            "e22_record_sha256": record["record_sha256"],
            "account_env": ENV_ACCOUNT,
            "order_type": self.config.order_type,
            "limit_offset_ticks": self.config.limit_offset_ticks,
            "time_in_force": self.config.time_in_force,
            "targets": {i: {"contract": c, "qty": q} for i, (c, q) in sorted(targets.items())},
            "positions_before": {i: dict(sorted(q.items())) for i, q in sorted(current.items())},
            "foreign_positions": foreign,
            "orders": [self._order(p, t) for p, t in trades],
            "fills": fills,
            "late_fills": late,
            "late_fills_unretained": unretained,
            "closed_orders": closed,
            "unresolved_orders": unresolved,
        }

    def _order(self, p: PlannedOrder, trade: Any) -> dict[str, Any]:
        st, od = trade.orderStatus, trade.order
        return {
            "instrument": p.instrument,
            "contract_id": p.contract_id,
            "con_id": self.resolver.resolve(p.instrument, p.contract_id).con_id,
            "order_ref": str(getattr(od, "orderRef", "")),
            "action": "BUY" if p.delta > 0 else "SELL",
            "qty": abs(p.delta),
            "order_type": str(getattr(od, "orderType", self.config.order_type)),
            "limit_price_ib": _num(getattr(od, "lmtPrice", None)),
            "order_id": int(getattr(od, "orderId", 0) or 0),
            "perm_id": int(getattr(od, "permId", 0) or 0),
            "status": str(getattr(st, "status", "")),
            "filled": _num(getattr(st, "filled", None)),
            "remaining": _num(getattr(st, "remaining", None)),
            "avg_fill_price_ib": _num(getattr(st, "avgFillPrice", None)),
        }

    def _fill(self, inst: str, cid: str, fill: Any) -> dict[str, Any]:
        ex, cr = fill.execution, fill.commissionReport
        rc = self.resolver.resolve(inst, cid)
        price_ib = _num(ex.price)
        return {
            "instrument": inst,
            "contract_id": cid,
            "con_id": rc.con_id,
            "exec_id": str(ex.execId),
            "order_ref": str(getattr(ex, "orderRef", "")),
            "time": _when(getattr(fill, "time", None) or getattr(ex, "time", None)),
            "side": str(ex.side),
            "shares": _num(ex.shares),
            "price_ib": price_ib,
            "price": None if price_ib is None else price_ib / rc.price_divisor,
            "commission": _num(getattr(cr, "commission", None)),
            "commission_currency": str(getattr(cr, "currency", "")),
        }

    def _late_fills(self, seen: set[str]) -> list[dict[str, Any]]:
        out = []
        for fill in self.session.gateway.reqExecutions():
            ex = fill.execution
            if not str(getattr(ex, "orderRef", "")).startswith(self.config.order_ref):
                continue
            if str(ex.execId) in seen:
                continue
            rc = self.resolver.identify(fill.contract) or self._identify_held(fill.contract)
            if rc is None:
                raise ShadowRouteError("a shadow execution could not be mapped to a contract")
            out.append(self._fill(rc.instrument, rc.contract_id, fill))
        return out

    # -- S5 (wave 3): earlier orders left short of their quantity ------------------------------
    def _reconcile(
        self, records: Sequence[Mapping[str, Any]], late: Sequence[Mapping[str, Any]]
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
        pending = pending_orders(records, late)
        if not pending:
            return [], [], []
        completed: dict[tuple[str, int], Any] = {}
        for trade in self.session.gateway.reqCompletedOrders(True):
            ref = str(getattr(trade.order, "orderRef", ""))
            if ref.startswith(self.config.order_ref):
                completed[(ref, int(getattr(trade.contract, "conId", 0) or 0))] = trade
        unretained, closed, unresolved = [], [], []
        for key, (order, accounted) in sorted(pending.items()):
            base = {
                "instrument": order["instrument"],
                "contract_id": order["contract_id"],
                "con_id": key[1],
                "order_ref": key[0],
                "perm_id": order.get("perm_id", 0),
            }
            trade = completed.get(key)
            if trade is None:
                unresolved.append(
                    {
                        **base,
                        "qty": order["qty"],
                        "accounted_shares": accounted,
                        "note": "not open, no execution and no completed order found; "
                        "positions_before shows the account's actual holdings",
                    }
                )
                continue
            filled = _num(getattr(trade.order, "filledQuantity", None))
            if filled is None:
                filled = _num(getattr(trade.orderStatus, "filled", None)) or 0.0
            status = str(getattr(trade.orderStatus, "status", ""))
            if filled > accounted:
                avg = _num(getattr(trade.orderStatus, "avgFillPrice", None))
                unretained.append(
                    {
                        **base,
                        "shares": filled - accounted,
                        "status": status,
                        "avg_fill_price_ib": avg if avg else None,
                        "source": "completed_order",
                        "note": "executions no longer returned by reqExecutions (current-day "
                        "retention); quantity from the completed order, no price or commission",
                    }
                )
            else:
                closed.append({**base, "status": status, "filled_total": filled})
        return unretained, closed, unresolved


def pending_orders(
    records: Sequence[Mapping[str, Any]], late: Sequence[Mapping[str, Any]]
) -> dict[tuple[str, int], tuple[Mapping[str, Any], float]]:
    """{(order_ref, con_id): (order, shares accounted for)} for every earlier shadow order whose
    filled quantity at its record, plus the late fills and unretained shares recorded since
    (and ``late``, this run's), is short of its quantity, unless an earlier record already
    reconciled it (late_fills_unretained, closed_orders or unresolved_orders)."""
    orders: dict[tuple[str, int], Mapping[str, Any]] = {}
    accounted: dict[tuple[str, int], float] = {}
    settled: set[tuple[str, int]] = set()

    def key(x: Mapping[str, Any]) -> tuple[str, int]:
        return str(x.get("order_ref", "")), int(x.get("con_id", 0) or 0)

    for r in records:
        for o in r["orders"]:
            orders[key(o)] = o
            accounted[key(o)] = accounted.get(key(o), 0.0) + float(o.get("filled") or 0.0)
        for f in (*r.get("late_fills", ()), *r.get("late_fills_unretained", ())):
            accounted[key(f)] = accounted.get(key(f), 0.0) + float(f.get("shares") or 0.0)
        for x in (*r.get("late_fills_unretained", ()), *r.get("closed_orders", ())):
            settled.add(key(x))
        settled |= {key(x) for x in r.get("unresolved_orders", ())}
    for f in late:
        accounted[key(f)] = accounted.get(key(f), 0.0) + float(f.get("shares") or 0.0)
    return {
        k: (o, accounted.get(k, 0.0))
        for k, o in orders.items()
        if k not in settled and accounted.get(k, 0.0) < float(o["qty"])
    }
