"""forward/orders_alpaca.py, the E22-F2 shadow route on Alpaca paper (Stage E.24 Part C).

Mocks only: no network, no keys. The shadow route never writes to the E22-F2 ledger.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from forward import orders_alpaca as oa
from forward.ledger import Ledger, LedgerOrderError

NY = ZoneInfo("America/New_York")
WED, THU, FRI = date(2026, 11, 4), date(2026, 11, 5), date(2026, 11, 6)
EVENING_WED = datetime.combine(WED, time(19, 30), NY)
REPO = Path(__file__).resolve().parents[1]


# --- fakes mirroring alpaca-py 0.44.0 shapes --------------------------------------------------


@dataclass
class FakeEnum:
    value: str


@dataclass
class FakePosition:
    symbol: str
    qty: str
    side: FakeEnum


def pos(symbol: str, signed: float) -> FakePosition:
    side = "short" if signed < 0 else "long"
    return FakePosition(symbol, str(signed), FakeEnum(side))


@dataclass
class FakeAsset:
    symbol: str
    shortable: bool = True
    easy_to_borrow: bool = True
    fractionable: bool = True
    tradable: bool = True


@dataclass
class FakeAccount:
    status: FakeEnum = field(default_factory=lambda: FakeEnum("ACTIVE"))
    trading_blocked: bool = False
    account_blocked: bool = False
    shorting_enabled: bool = True
    equity: str = "25000"
    buying_power: str = "50000"
    multiplier: str = "2"


@dataclass
class FakeOrder:
    id: str
    client_order_id: str
    symbol: str
    qty: str
    side: FakeEnum
    time_in_force: FakeEnum
    status: FakeEnum
    submitted_at: datetime
    filled_qty: str = "0"
    filled_avg_price: str | None = None
    filled_at: datetime | None = None


@dataclass(frozen=True)
class FakeOrderRequest:
    symbol: str
    qty: float
    side: str
    time_in_force: str
    client_order_id: str


@dataclass(frozen=True)
class FakeOrdersQuery:
    status: str
    after: datetime | None


class FakeAPIError(Exception):
    def __init__(self, status: int, text: str):
        super().__init__(text)
        self.status_code = status


class FakeTradingClient:
    _base_url = "https://paper-api.alpaca.markets"

    def __init__(self, positions=(), assets=None, account=None, now=EVENING_WED):
        self.positions = list(positions)
        self.assets = assets or {}
        self.account = account or FakeAccount()
        self.orders: list[FakeOrder] = []
        self.calls: list[str] = []
        self.reject: dict[str, FakeAPIError] = {}
        self.now = now

    def get_account(self):
        self.calls.append("get_account")
        return self.account

    def get_all_positions(self):
        self.calls.append("get_all_positions")
        return list(self.positions)

    def get_asset(self, symbol_or_asset_id):
        self.calls.append(f"get_asset:{symbol_or_asset_id}")
        return self.assets.get(symbol_or_asset_id, FakeAsset(symbol_or_asset_id))

    def get_orders(self, filter=None):  # noqa: A002 (alpaca-py's parameter name)
        self.calls.append("get_orders")
        return list(self.orders)

    def get_order_by_client_id(self, client_id):
        self.calls.append(f"get_order:{client_id}")
        for o in self.orders:
            if o.client_order_id == client_id:
                return o
        raise FakeAPIError(404, '{"code":40410000,"message":"order not found"}')

    def submit_order(self, order_data):
        self.calls.append(f"submit:{order_data.client_order_id}")
        if order_data.symbol in self.reject:
            raise self.reject[order_data.symbol]
        order = FakeOrder(
            id=f"id-{len(self.orders)}",
            client_order_id=order_data.client_order_id,
            symbol=order_data.symbol,
            qty=str(order_data.qty),
            side=FakeEnum(order_data.side),
            time_in_force=FakeEnum(order_data.time_in_force),
            status=FakeEnum("accepted"),
            submitted_at=self.now.astimezone(UTC),
        )
        self.orders.append(order)
        return order


class WindowedClient(FakeTradingClient):
    """get_orders as the endpoint answers it: orders submitted after ``after``, newest first,
    at most ORDERS_LIMIT (the alpaca-py GetOrdersRequest docstring: ``after`` filters on the
    submission time, ``direction`` defaults to desc, ``limit`` max 500)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queries: list[FakeOrdersQuery] = []

    def get_orders(self, filter=None):  # noqa: A002
        self.calls.append("get_orders")
        self.queries.append(filter)
        orders = list(self.orders)
        if filter is not None and filter.after is not None:
            orders = [o for o in orders if o.submitted_at > filter.after]
        if filter is not None and filter.status == "open":
            orders = [o for o in orders if str(o.status.value) not in oa.NOT_OPEN_STATUSES]
        orders.sort(key=lambda o: o.submitted_at, reverse=True)
        return orders[: oa.ORDERS_LIMIT]


def fill_all(client: FakeTradingClient, price: float = 100.0) -> None:
    for o in client.orders:
        o.status = FakeEnum("filled")
        o.filled_qty = o.qty
        o.filled_avg_price = str(price)
        o.filled_at = datetime.combine(THU, time(16, 0), NY).astimezone(UTC)


def f2_record(day: date, targets: dict, positions: dict | None = None) -> dict:
    return {
        "date": day.isoformat(),
        "targets": targets,
        "positions": positions or {},
        "record_sha256": "ab" * 32,
    }


def make_route(tmp_path, client, *, mode="moc_whole", now=EVENING_WED, enabled=True):
    cfg = oa.ShadowConfig(enabled=enabled, ledger_path=tmp_path / "shadow.jsonl", mode=mode)
    f2_path = tmp_path / "f2.jsonl"
    return oa.ShadowRoute(
        cfg,
        f2_path,
        client=client,
        order_factory=lambda **kw: FakeOrderRequest(**kw),
        query_factory=lambda **kw: FakeOrdersQuery(**kw),
        clock=lambda: now,
    )


# --- config --------------------------------------------------------------------------------


def test_shipped_config_is_off_by_default():
    cfg = oa.load_shadow_config(REPO / "forward" / "shadow_f2.json")
    assert cfg.enabled is False
    assert cfg.mode == "moc_whole"
    raw = json.loads((REPO / "forward" / "shadow_f2.json").read_text())
    assert raw["enabled"] is False


def test_config_rejects_unknown_modes_and_keys(tmp_path):
    path = tmp_path / "c.json"
    path.write_text(json.dumps({"enabled": True, "ledger_path": "x.jsonl", "mode": "gtc"}))
    with pytest.raises(ValueError, match="mode"):
        oa.load_shadow_config(path)
    path.write_text(json.dumps({"enabled": "yes", "ledger_path": "x.jsonl", "mode": "moc_whole"}))
    with pytest.raises(ValueError, match="enabled"):
        oa.load_shadow_config(path)
    path.write_text(
        json.dumps({"enabled": False, "ledger_path": "x.jsonl", "mode": "moc_whole", "live": 1})
    )
    with pytest.raises(ValueError, match="unknown"):
        oa.load_shadow_config(path)


def test_disabled_route_touches_nothing(tmp_path):
    client = FakeTradingClient()
    f2 = Ledger(tmp_path / "f2.jsonl")
    f2.append({"date": WED.isoformat(), "x": 1})
    before = (tmp_path / "f2.jsonl").read_bytes()
    route = make_route(tmp_path, client, enabled=False)
    assert route.run(f2_record(WED, {"QQQ": 3.0})) is None
    assert client.calls == []
    assert not (tmp_path / "shadow.jsonl").exists()
    assert (tmp_path / "f2.jsonl").read_bytes() == before


# --- order construction --------------------------------------------------------------------


def plan(targets, current, mode="moc_whole", assets=None):
    orders, notes = oa.plan_orders(WED, targets, current, mode=mode, assets=assets or {})
    return [(o.symbol, o.side, o.qty, o.intent, o.time_in_force) for o in orders], notes


def test_fractional_long_in_fractional_day_mode():
    orders, _ = plan({"QQQ": 3.25}, {}, mode="fractional_day")
    assert orders == [("QQQ", "buy", 3.25, "buy_to_open", "day")]


def test_fractional_quantities_keep_nine_decimals():
    orders, _ = plan({"QQQ": 1.1234567891234}, {}, mode="fractional_day")
    assert orders[0][2] == 1.123456789


def test_moc_mode_rounds_longs_to_whole_shares_at_the_close():
    assert plan({"QQQ": 3.6}, {})[0] == [("QQQ", "buy", 4.0, "buy_to_open", "cls")]
    assert plan({"QQQ": 3.4}, {})[0] == [("QQQ", "buy", 3.0, "buy_to_open", "cls")]
    assert plan({"QQQ": 1.0}, {"QQQ": 4.0})[0] == [("QQQ", "sell", 3.0, "sell_to_close", "cls")]


@pytest.mark.parametrize("mode", ["moc_whole", "fractional_day"])
def test_shorts_are_whole_shares(mode):
    tif = "cls" if mode == "moc_whole" else "day"
    assert plan({"TLT": -2.7}, {}, mode)[0] == [("TLT", "sell", 3.0, "sell_to_open", tif)]
    assert plan({"TLT": -1.2}, {"TLT": -3.0}, mode)[0] == [
        ("TLT", "buy", 2.0, "buy_to_close", tif)
    ]
    assert plan({"TLT": -4.4}, {"TLT": -3.0}, mode)[0] == [
        ("TLT", "sell", 1.0, "sell_to_open", tif)
    ]


def test_long_to_short_crossing_is_split_into_close_and_whole_short():
    orders, _ = plan({"GLD": -3.2}, {"GLD": 4.5}, mode="fractional_day")
    assert orders == [
        ("GLD", "sell", 4.5, "sell_to_close", "day"),
        ("GLD", "sell", 3.0, "sell_to_open", "day"),
    ]
    orders, _ = plan({"GLD": -3.2}, {"GLD": 4.0})
    assert orders == [
        ("GLD", "sell", 4.0, "sell_to_close", "cls"),
        ("GLD", "sell", 3.0, "sell_to_open", "cls"),
    ]


def test_short_to_long_crossing_is_split_into_cover_and_open():
    orders, _ = plan({"IEF": 2.5}, {"IEF": -3.0}, mode="fractional_day")
    assert orders == [
        ("IEF", "buy", 3.0, "buy_to_close", "day"),
        ("IEF", "buy", 2.5, "buy_to_open", "day"),
    ]


def test_crossing_to_a_short_that_rounds_to_zero_only_closes():
    orders, _ = plan({"GLD": -0.3}, {"GLD": 2.0})
    assert orders == [("GLD", "sell", 2.0, "sell_to_close", "cls")]


def test_no_change_day_places_no_orders():
    assert plan({"QQQ": 4.0, "TLT": -2.0}, {"QQQ": 4.0, "TLT": -2.0})[0] == []
    assert plan({"QQQ": 4.2}, {"QQQ": 4.0})[0] == []  # rounds to the held 4 shares
    assert plan({"QQQ": 4.0 + 1e-12}, {"QQQ": 4.0}, "fractional_day")[0] == []
    assert plan({"QQQ": 0.0}, {})[0] == []


def test_opening_short_needs_a_shortable_easy_to_borrow_asset():
    assets = {"UNG": FakeAsset("UNG", easy_to_borrow=False)}
    orders, notes = plan({"UNG": -5.0}, {}, assets=assets)
    assert orders == []
    assert any("UNG" in n and "borrow" in n for n in notes)
    orders, notes = plan({"UNG": -5.0}, {"UNG": 2.0}, assets=assets)
    assert orders == [("UNG", "sell", 2.0, "sell_to_close", "cls")]


def test_non_fractionable_asset_is_rounded_in_fractional_mode():
    assets = {"SOYB": FakeAsset("SOYB", fractionable=False)}
    orders, notes = plan({"SOYB": 7.6}, {}, mode="fractional_day", assets=assets)
    assert orders == [("SOYB", "buy", 8.0, "buy_to_open", "day")]
    assert any("SOYB" in n and "fractionable" in n for n in notes)


def test_held_symbols_outside_the_targets_are_left_alone():
    orders, notes = plan({"QQQ": 1.0}, {"QQQ": 1.0, "SPY": 5.0})
    assert orders == []
    assert any("SPY" in n and "unmanaged" in n for n in notes)


def test_client_order_ids_are_deterministic_and_short():
    orders, _ = oa.plan_orders(WED, {"GLD": -3.2}, {"GLD": 4.0}, mode="moc_whole", assets={})
    ids = [o.client_order_id for o in orders]
    assert ids == ["e22f2-20261104-GLD-1", "e22f2-20261104-GLD-2"]
    assert all(len(i) <= 48 for i in ids)


# --- the F2 record mapping -----------------------------------------------------------------


def test_f2_fields_reads_only_date_targets_positions():
    got = oa.f2_fields(f2_record(WED, {"QQQ": 3}, {"QQQ": 2.5}) | {"pnl": 12.0})
    assert got.date == WED
    assert got.targets == {"QQQ": 3.0} and got.positions == {"QQQ": 2.5}
    with pytest.raises(ValueError, match="targets"):
        oa.f2_fields({"date": WED.isoformat(), "positions": {}})
    with pytest.raises(ValueError, match="finite"):
        oa.f2_fields(f2_record(WED, {"QQQ": float("nan")}))


# --- refusals: ledger path, live endpoint, window, account ---------------------------------


def test_refuses_the_f2_ledger_path(tmp_path):
    f2 = tmp_path / "f2.jsonl"
    with pytest.raises(oa.LedgerPathRefused):
        oa.check_ledger_paths(f2, f2)
    with pytest.raises(oa.LedgerPathRefused):
        oa.check_ledger_paths(tmp_path / "sub" / ".." / "f2.jsonl", f2)
    f2.write_text("")
    link = tmp_path / "link.jsonl"
    os.symlink(f2, link)
    with pytest.raises(oa.LedgerPathRefused):
        oa.check_ledger_paths(link, f2)
    hard = tmp_path / "hard.jsonl"
    os.link(f2, hard)
    with pytest.raises(oa.LedgerPathRefused):
        oa.check_ledger_paths(hard, f2)
    oa.check_ledger_paths(tmp_path / "shadow.jsonl", f2)


def test_route_refuses_to_construct_with_the_f2_ledger_path(tmp_path):
    cfg = oa.ShadowConfig(enabled=True, ledger_path=tmp_path / "f2.jsonl", mode="moc_whole")
    with pytest.raises(oa.LedgerPathRefused):
        oa.ShadowRoute(cfg, tmp_path / "f2.jsonl", client=FakeTradingClient())


def test_refuses_a_live_endpoint(tmp_path):
    live = FakeTradingClient()
    live._base_url = "https://api.alpaca.markets"
    with pytest.raises(oa.LiveEndpointRefused):
        oa.assert_paper(live)
    route = make_route(tmp_path, live)
    with pytest.raises(oa.LiveEndpointRefused):
        route.run(f2_record(WED, {"QQQ": 1.0}))
    assert not any(c.startswith("submit") for c in live.calls)
    unknown = FakeTradingClient()
    unknown._base_url = None
    with pytest.raises(oa.LiveEndpointRefused):
        oa.assert_paper(unknown)
    env = {"ALPACA_PAPER_KEY_ID": "k", "ALPACA_PAPER_SECRET_KEY": "s"}
    with pytest.raises(oa.LiveEndpointRefused):
        oa.make_trading_client(env, paper=False)
    with pytest.raises(oa.LiveEndpointRefused):
        oa.make_trading_client(env, url_override="https://api.alpaca.markets")


@pytest.mark.parametrize(
    "now, ok",
    [
        (datetime.combine(WED, time(17, 0), NY), False),  # 15:50-19:00 ET: CLS is rejected
        (datetime.combine(WED, time(19, 30), NY), True),  # queued for THU's close
        (datetime.combine(THU, time(10, 0), NY), True),  # before THU's 15:50 cutoff
        (datetime.combine(THU, time(15, 47), NY), False),  # inside the safety margin
        (datetime.combine(FRI, time(10, 0), NY), False),  # THU's close has passed
        (datetime.combine(WED, time(15, 0), NY), False),  # WED's own session is not over
    ],
)
def test_moc_submission_window(now, ok):
    assert oa.submission_allowed(now, WED, "moc_whole") is ok


def test_window_refusal_writes_nothing(tmp_path):
    client = FakeTradingClient()
    route = make_route(tmp_path, client, now=datetime.combine(WED, time(17, 0), NY))
    with pytest.raises(oa.ShadowWindowError):
        route.run(f2_record(WED, {"QQQ": 1.0}))
    assert not (tmp_path / "shadow.jsonl").exists()
    assert not any(c.startswith("submit") for c in client.calls)


def test_blocked_account_is_refused(tmp_path):
    client = FakeTradingClient(account=FakeAccount(trading_blocked=True))
    with pytest.raises(oa.ShadowError, match="blocked"):
        make_route(tmp_path, client).run(f2_record(WED, {"QQQ": 1.0}))
    assert not (tmp_path / "shadow.jsonl").exists()


def test_foreign_open_orders_are_refused(tmp_path):
    client = FakeTradingClient()
    client.orders.append(
        FakeOrder(
            "x", "manual-1", "QQQ", "1", FakeEnum("buy"), FakeEnum("day"), FakeEnum("new"),
            EVENING_WED.astimezone(UTC),
        )
    )
    with pytest.raises(oa.ShadowError, match="open order"):
        make_route(tmp_path, client).run(f2_record(WED, {"QQQ": 1.0}))


# --- the full run --------------------------------------------------------------------------


def test_enabled_run_submits_orders_and_writes_only_the_shadow_ledger(tmp_path):
    f2 = Ledger(tmp_path / "f2.jsonl")
    payload = f2_record(WED, {"QQQ": 3.6, "TLT": -2.2}, {"QQQ": 0.0})
    del payload["record_sha256"]
    f2.append(payload)
    before = hashlib.sha256((tmp_path / "f2.jsonl").read_bytes()).hexdigest()
    client = FakeTradingClient(positions=[pos("TLT", -1.0)])
    stored = make_route(tmp_path, client).run(f2.records()[-1])
    assert hashlib.sha256((tmp_path / "f2.jsonl").read_bytes()).hexdigest() == before
    shadow = Ledger(tmp_path / "shadow.jsonl").records()
    assert len(shadow) == 1 and shadow[0]["record_sha256"] == stored["record_sha256"]
    rec = shadow[0]
    assert rec["date"] == WED.isoformat()
    assert rec["f2_record_sha256"] == f2.records()[-1]["record_sha256"]
    assert rec["mode"] == "moc_whole"
    assert [(o["symbol"], o["side"], o["qty"], o["result"]) for o in rec["orders"]] == [
        ("QQQ", "buy", 4.0, "submitted"),
        ("TLT", "sell", 1.0, "submitted"),
    ]
    assert rec["account_positions"] == {"TLT": -1.0}
    assert rec["book_positions"] == {"QQQ": 0.0}
    assert [c for c in client.calls if c.startswith("submit")] == [
        "submit:e22f2-20261104-QQQ-1",
        "submit:e22f2-20261104-TLT-1",
    ]


def test_rerun_after_a_crash_does_not_resubmit(tmp_path):
    client = FakeTradingClient()
    route = make_route(tmp_path, client)
    record = f2_record(WED, {"QQQ": 2.0, "GLD": 1.0})
    # first run submits, then "crashes" before its shadow record: drop the record file
    route.run(record)
    (tmp_path / "shadow.jsonl").unlink()
    client.calls.clear()
    rec = make_route(tmp_path, client).run(record)
    assert not any(c.startswith("submit") for c in client.calls)
    assert {o["result"] for o in rec["orders"]} == {"existing"}


def test_same_or_earlier_date_is_refused_before_any_order(tmp_path):
    client = FakeTradingClient()
    thu_evening = datetime.combine(THU, time(19, 30), NY)
    make_route(tmp_path, client, now=thu_evening).run(f2_record(THU, {"QQQ": 2.0}))
    client.calls.clear()
    for day in (THU, WED):
        with pytest.raises(LedgerOrderError):
            make_route(tmp_path, client, now=thu_evening).run(f2_record(day, {"QQQ": 3.0}))
    assert client.calls == []
    assert len(Ledger(tmp_path / "shadow.jsonl").records()) == 1


def test_fills_of_earlier_orders_are_recorded_the_next_day(tmp_path):
    client = FakeTradingClient()
    make_route(tmp_path, client).run(f2_record(WED, {"QQQ": 2.0}))
    fill_all(client, price=501.25)
    client.positions = [pos("QQQ", 2.0)]
    client.now = datetime.combine(THU, time(19, 30), NY)
    rec = make_route(tmp_path, client, now=client.now).run(f2_record(THU, {"QQQ": 2.0}))
    assert rec["orders"] == []
    assert rec["fills"] == [
        {
            "client_order_id": "e22f2-20261104-QQQ-1",
            "status": "filled",
            "filled_qty": 2.0,
            "filled_avg_price": 501.25,
            "filled_at": "2026-11-05T21:00:00+00:00",
        }
    ]
    assert rec["pending"] == []


def test_open_shadow_orders_from_an_earlier_date_are_refused(tmp_path):
    client = FakeTradingClient()
    make_route(tmp_path, client).run(f2_record(WED, {"QQQ": 2.0}))
    later = datetime.combine(THU, time(19, 30), NY)
    for o in client.orders:  # still working: the positions do not reflect it yet
        o.status = FakeEnum("new")
    with pytest.raises(oa.ShadowError, match="open order"):
        make_route(tmp_path, client, now=later).run(f2_record(THU, {"QQQ": 2.0}))


def test_orders_not_found_stay_pending(tmp_path):
    client = FakeTradingClient()
    make_route(tmp_path, client).run(f2_record(WED, {"QQQ": 2.0}))
    client.orders.clear()  # the account's order list no longer shows it
    client.positions = [pos("QQQ", 2.0)]
    later = datetime.combine(THU, time(19, 30), NY)
    rec = make_route(tmp_path, client, now=later).run(f2_record(THU, {"QQQ": 2.0}))
    assert rec["pending"] == ["e22f2-20261104-QQQ-1"]
    assert rec["fills"] == []
    assert "get_order:e22f2-20261104-QQQ-1" in client.calls  # looked up; 404 = not found


def test_submit_errors_are_recorded_not_raised(tmp_path):
    client = FakeTradingClient()
    client.reject["TLT"] = FakeAPIError(403, '{"code":40310000,"message":"not shortable"}')
    rec = make_route(tmp_path, client).run(f2_record(WED, {"QQQ": 1.0, "TLT": -2.0}))
    by_symbol = {o["symbol"]: o for o in rec["orders"]}
    assert by_symbol["QQQ"]["result"] == "submitted"
    assert by_symbol["TLT"]["result"] == "rejected"
    assert "403" in by_symbol["TLT"]["error"]


# --- C4a S2: the orders query stays bounded however long the shadow ledger is ----------------


def long_history(client: FakeTradingClient, path: Path, sessions: int, first: date) -> list[str]:
    """``sessions`` shadow records of 4 orders each; every order is filled on the account and
    recorded as a fill by the next record, except the last record's. Returns those ids."""
    ledger = Ledger(path)
    day, done, prev = first, 0, []
    while done < sessions:
        if day.weekday() < 5:
            stamp = datetime.combine(day, time(19, 30), NY).astimezone(UTC)
            ids = [f"e22f2-{day:%Y%m%d}-S{i}-1" for i in range(4)]
            for i, cid in enumerate(ids):
                client.orders.append(
                    FakeOrder(
                        id=f"id-{len(client.orders)}", client_order_id=cid, symbol=f"S{i}",
                        qty="1", side=FakeEnum("buy"), time_in_force=FakeEnum("cls"),
                        status=FakeEnum("filled"), submitted_at=stamp, filled_qty="1",
                        filled_avg_price="100", filled_at=stamp + timedelta(hours=20),
                    )
                )
            ledger.append(
                {
                    "date": day.isoformat(),
                    "orders": [{"client_order_id": c, "result": "submitted"} for c in ids],
                    "fills": [{"client_order_id": c} for c in prev],
                }
            )
            prev, done = ids, done + 1
        day += timedelta(days=1)
    return prev


def test_orders_query_stays_bounded_after_more_than_a_page_of_orders(tmp_path):
    client = WindowedClient()
    last_ids = long_history(client, tmp_path / "shadow.jsonl", 130, date(2026, 5, 4))
    assert len(client.orders) > oa.ORDERS_LIMIT
    rec = make_route(tmp_path, client).run(f2_record(WED, {"QQQ": 2.0}))
    (query,) = [q for q in client.queries if q.status == "all"]
    assert query.after == datetime.combine(date(2026, 11, 1), time(0), NY)  # WED - 3 days
    # the previous record (Fri 2026-10-30) is older than the window: looked up by id
    assert [c for c in client.calls if c.startswith("get_order:")] == [
        f"get_order:{c}" for c in last_ids
    ]
    assert [f["client_order_id"] for f in rec["fills"]] == last_ids
    assert rec["pending"] == []
    assert [o["result"] for o in rec["orders"]] == ["submitted"]


def test_failed_lookup_of_a_pending_order_raises_and_writes_nothing(tmp_path):
    client = FakeTradingClient()
    make_route(tmp_path, client).run(f2_record(WED, {"QQQ": 2.0}))
    client.orders.clear()

    def refused(client_id):
        raise FakeAPIError(403, '{"code":40310000,"message":"forbidden"}')

    client.get_order_by_client_id = refused
    later = datetime.combine(THU, time(19, 30), NY)
    with pytest.raises(oa.ShadowError, match="403"):
        make_route(tmp_path, client, now=later).run(f2_record(THU, {"QQQ": 2.0}))
    assert [r["date"] for r in Ledger(tmp_path / "shadow.jsonl").records()] == [WED.isoformat()]
