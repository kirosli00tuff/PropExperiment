"""The adapters' Gateway Protocol against the real ib_async 2.1.0 classes (no network).

Skipped unless ib_async is installed; run through the overlay:
uv run --offline --frozen --with-requirements forward/requirements_broker.txt \
    pytest -q -p no:cacheprovider tests/test_forward_ibkr_vendor_contract.py
"""

from __future__ import annotations

import inspect

import pytest

ib_async = pytest.importorskip("ib_async")


def _params(fn) -> set[str]:
    return set(inspect.signature(fn).parameters)


def test_ib_has_every_method_and_keyword_the_adapters_call():
    ib = ib_async.IB
    for name in (
        "connect",
        "disconnect",
        "isConnected",
        "reqContractDetails",
        "reqHistoricalData",
        "placeOrder",
        "positions",
        "openTrades",
        "reqExecutions",
        "reqCompletedOrders",
        "managedAccounts",
        "reqMarketDataType",
        "sleep",
    ):
        assert callable(getattr(ib, name)), name
    assert {"host", "port", "clientId", "timeout", "readonly"} <= _params(ib.connect)
    assert {
        "endDateTime",
        "durationStr",
        "barSizeSetting",
        "whatToShow",
        "useRTH",
        "formatDate",
        "keepUpToDate",
        "timeout",
    } <= _params(ib.reqHistoricalData)
    assert hasattr(ib, "RaiseRequestErrors")
    assert {"apiOnly"} <= _params(ib.reqCompletedOrders)
    assert hasattr(ib_async.IB(), "errorEvent")


def test_vendor_facts_the_wave3_fixes_lean_on():
    """ib_async 2.1.0 facts (wave 3). The adapter does not rely on the first one: it treats any
    answer that took the whole request timeout as a timeout, whatever came back."""
    src = inspect.getsource(ib_async.IB.reqHistoricalDataAsync)
    assert "asyncio.wait_for(future, timeout)" in src and "bars.clear()" in src
    wrapper_src = inspect.getsource(ib_async.wrapper.Wrapper.error)
    assert "321" in wrapper_src and "errorEvent.emit(reqId, errorCode, errorString" in wrapper_src
    completed = inspect.getsource(ib_async.wrapper.Wrapper.completedOrder)
    assert "OrderStatus(orderId=order.orderId, status=orderState.status)" in completed
    assert hasattr(ib_async.Order(), "filledQuantity")


def test_vendor_objects_carry_the_fields_the_adapters_read():
    fut = ib_async.Future(
        symbol="MHNG",
        lastTradeDateOrContractMonth="202701",
        exchange="NYMEX",
        currency="USD",
        includeExpired=True,
        tradingClass="MNG",
    )
    assert fut.secType == "FUT" and fut.includeExpired and fut.tradingClass == "MNG"
    det = ib_async.ContractDetails()
    for name in ("contract", "contractMonth", "priceMagnifier"):
        assert hasattr(det, name)
    bar = ib_async.BarData()
    assert hasattr(bar, "date") and hasattr(bar, "close")
    assert set(ib_async.Fill._fields) == {"contract", "execution", "commissionReport", "time"}
    ex = ib_async.Execution()
    for name in ("execId", "side", "shares", "price", "time", "orderRef"):
        assert hasattr(ex, name)
    assert hasattr(ib_async.CommissionReport(), "commission")
    order = ib_async.MarketOrder("BUY", 1, tif="DAY", account="DU0", orderRef="x")
    assert (order.orderType, order.tif, order.orderRef) == ("MKT", "DAY", "x")
    assert ib_async.LimitOrder("SELL", 1, 1.25).lmtPrice == 1.25
    err = ib_async.RequestError(1, 162, "HMDS query returned no data")
    assert (err.code, err.message) == (162, "HMDS query returned no data")


def test_connect_live_builds_an_unconnected_client_that_raises_request_errors():
    from forward.ibkr_gateway import connect_live

    ib = connect_live()
    assert ib.RaiseRequestErrors is True and not ib.isConnected()
