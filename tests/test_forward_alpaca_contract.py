"""Contract tests against the real alpaca-py 0.44.0 request and model classes. No network.

Skipped unless alpaca-py is importable. Run them with the broker overlay:
``uv run --frozen --with-requirements forward/requirements_broker.txt pytest -q
tests/test_forward_alpaca_contract.py`` (add ``--offline`` when the wheel is in the uv cache).
"""

from __future__ import annotations

import itertools
from datetime import UTC, date, datetime, time
from zoneinfo import ZoneInfo

import pytest

alpaca = pytest.importorskip("alpaca")

from alpaca.data.models import BarSet  # noqa: E402

from forward import orders_alpaca as oa  # noqa: E402
from forward import sources_alpaca as sa  # noqa: E402
from forward.etf_bars import EtfBar  # noqa: E402

NY = ZoneInfo("America/New_York")
WED, TUE = date(2026, 11, 4), date(2026, 11, 3)
ENV = {sa.KEY_ID_ENV: "PKCONTRACTTEST", sa.SECRET_KEY_ENV: "contract-test-secret"}


def test_pinned_version():
    from importlib.metadata import version

    assert version("alpaca-py") == "0.44.0"


def test_bars_request_fields_match_the_sdk():
    start = datetime.combine(date(2026, 10, 14), time(0), NY)
    end = datetime.combine(WED, time(23, 59, 59), NY)
    req = sa.alpaca_bars_request(
        symbol_or_symbols=["BIL", "QQQ"], start=start, end=end, adjustment="all", feed="sip"
    )
    fields = req.to_request_fields()
    assert fields["adjustment"] == "all"
    assert fields["feed"] == "sip"
    assert req.timeframe.value == "1Day"
    assert "limit" not in fields
    assert req.start == start.astimezone(UTC).replace(tzinfo=None)  # the SDK sends naive UTC
    assert req.end == end.astimezone(UTC).replace(tzinfo=None)


def test_source_parses_a_real_barset_built_from_hand_written_json():
    def bar(stamp: str, close: float) -> dict:
        return {"t": stamp, "o": 1, "h": 1, "l": 1, "c": close, "v": 1, "n": 1, "vw": 1}

    raw = {"QQQ": [bar("2026-11-03T05:00:00Z", 502.0), bar("2026-11-04T05:00:00Z", 503.0)]}

    class Client:
        def get_stock_bars(self, request_params):
            return BarSet(raw)

    ticks = itertools.count(0.0, 10.0)
    class NoActions:
        def get_corporate_actions(self, request_params):
            return {}

    src = sa.AlpacaEtfSource(
        ["QQQ"],
        Client(),
        ca_client=NoActions(),
        ca_request_factory=sa.alpaca_corporate_actions_request,
        clock=lambda: datetime.combine(WED, time(21, 0), NY),
        sleep=lambda s: None,
        monotonic=lambda: next(ticks),
    )
    assert src.bars(WED) == {"QQQ": EtfBar(503.0, 503.0 / 502.0 - 1, TUE)}


def test_data_client_is_built_without_network():
    client = sa.make_data_client(ENV)
    assert type(client).__name__ == "StockHistoricalDataClient"


def test_trading_client_is_paper_and_a_live_client_is_refused():
    from alpaca.trading.client import TradingClient

    client = oa.make_trading_client(ENV)
    oa.assert_paper(client)
    live = TradingClient(api_key="PKX", secret_key="sx", paper=False)
    with pytest.raises(oa.LiveEndpointRefused):
        oa.assert_paper(live)


def test_order_requests_match_the_sdk():
    req = oa.market_order_request(
        symbol="QQQ", qty=4.0, side="buy", time_in_force="cls",
        client_order_id="e22f2-20261104-QQQ-1",
    )
    fields = req.to_request_fields()
    assert fields["type"] == "market"
    assert fields["time_in_force"] == "cls"
    assert fields["side"] == "buy"
    assert fields["qty"] == 4.0
    assert fields["client_order_id"] == "e22f2-20261104-QQQ-1"
    frac = oa.market_order_request(
        symbol="QQQ", qty=1.123456789, side="buy", time_in_force="day", client_order_id="x"
    )
    assert frac.to_request_fields()["qty"] == 1.123456789
    query = oa.orders_query(status="all", after=datetime(2026, 11, 1, tzinfo=NY))
    qf = query.to_request_fields()
    assert qf["status"] == "all" and qf["limit"] == oa.ORDERS_LIMIT


def test_corporate_actions_request_and_client_match_the_sdk():
    req = sa.alpaca_corporate_actions_request(
        symbols=["BIL", "QQQ"], start=date(2026, 10, 14), end=WED
    )
    assert req.limit is None  # the class default (1000) would silently cap the answer
    assert req.types is None  # all types: capital gains and the flagged types included
    fields = req.to_request_fields()
    assert "limit" not in fields
    client = sa.make_corporate_actions_client(ENV)
    assert type(client).__name__ == "CorporateActionsClient"
    assert client._use_raw_data is True


def test_the_typed_sdk_set_would_drop_capital_gains():
    """Why the client runs with raw_data=True: 0.44.0 has no capital gains model or enum."""
    from alpaca.data.enums import CorporateActionsType
    from alpaca.data.models.corporate_actions import CorporateActionsSet

    assert "capital_gains_distribution" not in {t.value for t in CorporateActionsType}
    raw = {
        "capital_gains_distributions": [
            {"symbol": "GLD", "cusip": "0", "long_term_rate": 2.0, "short_term_rate": 0.5,
             "ex_date": "2026-11-04", "process_date": "2026-11-04"}
        ]
    }
    assert CorporateActionsSet(raw).data == {}
    parsed = sa.parse_corporate_actions(raw, ["GLD"])
    assert [(a.kind, a.amount) for a in parsed.booked] == [("capital_gains_distribution", 2.5)]



# --- C4a fixes against the real SDK request path (HTTP faked at the session; no network) ------


def _response(status: int, body: dict) -> object:
    import json

    import requests

    out = requests.Response()
    out.status_code = status
    out._content = json.dumps(body).encode()
    out.url = "https://example.invalid/faked"
    return out


class FakeSession:
    """Stands in for the SDK client's requests.Session: one canned response per request."""

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def request(self, method, url, **opts):
        self.calls.append((method, url, dict(opts.get("params") or {})))
        return self.responses.pop(0)


def test_corporate_actions_follow_every_page_and_filter_the_ex_dates():
    """C4a S1: one request over the padded process_date range; alpaca-py follows
    next_page_token to the last page (limit=None); ex_dates outside the span are dropped."""
    client = sa.make_corporate_actions_client(ENV)
    page1 = {
        "corporate_actions": {
            "cash_dividends": [
                {"symbol": "TLT", "cusip": "0", "rate": 0.25, "special": False, "foreign": False,
                 "ex_date": "2025-11-03", "process_date": "2025-11-18"},
            ]
        },
        "next_page_token": "p2",
    }
    page2 = {
        "corporate_actions": {
            "cash_dividends": [
                {"symbol": "TLT", "cusip": "0", "rate": 0.30, "special": False, "foreign": False,
                 "ex_date": "2026-11-04", "process_date": "2026-11-19"},
                {"symbol": "TLT", "cusip": "0", "rate": 9.0, "special": False, "foreign": False,
                 "ex_date": "2025-10-01", "process_date": "2025-10-02"},
            ],
            "reverse_splits": [
                {"symbol": "UNG", "cusip": "0", "new_rate": 1, "old_rate": 4,
                 "ex_date": "2026-03-02", "process_date": "2026-03-02"},
            ],
        },
        "next_page_token": None,
    }
    client._session = FakeSession([_response(200, page1), _response(200, page2)])
    src = sa.AlpacaEtfSource(["TLT", "UNG"], object(), ca_client=client)
    got = src.corporate_actions(date(2025, 11, 3), WED)
    assert [(a.symbol, a.ex_date.isoformat()) for a in got.booked] == [
        ("TLT", "2025-11-03"), ("TLT", "2026-11-04"), ("UNG", "2026-03-02"),
    ]
    (m1, url1, p1), (_, _, p2) = client._session.calls
    assert m1 == "GET" and url1.endswith("/v1/corporate-actions")
    assert (p1["start"], p1["end"]) == ("2025-09-04", "2027-01-03")  # +- CA_MARGIN_DAYS
    assert p1["page_token"] is None and p2["page_token"] == "p2"


def test_order_lookup_by_client_id_404_is_none_and_other_errors_raise():
    """C4a S2: a pending order is looked up by client order id; HTTP 404 means none."""
    client = oa.make_trading_client(ENV)
    client._session = FakeSession(
        [
            _response(404, {"code": 40410000, "message": "order not found"}),
            _response(403, {"code": 40310000, "message": "forbidden"}),
        ]
    )
    assert oa._order_by_client_id(client, "e22f2-20261104-QQQ-1") is None
    with pytest.raises(oa.ShadowError, match="403"):
        oa._order_by_client_id(client, "e22f2-20261104-QQQ-1")
    method, url, params = client._session.calls[0]
    assert method == "GET" and url.endswith("/v2/orders:by_client_order_id")
    assert params == {"client_order_id": "e22f2-20261104-QQQ-1"}
