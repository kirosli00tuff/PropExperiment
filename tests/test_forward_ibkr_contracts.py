"""forward.sources_ibkr contract resolution against the mock gateway (Stage E.24, no network)."""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import date
from pathlib import Path

import pytest

from forward import rolls as R
from forward.ibkr_gateway import ConnectionParams, GatewaySession, RetryPolicy
from forward.sources_ibkr import (
    IB_SPECS,
    ContractNotFound,
    ContractResolutionError,
    ContractResolver,
    check_specs,
    contracts_for_day,
    next_contract,
    previous_contract,
    to_runner_price,
)
from tests._forward_ibkr_mock import (
    ENV,
    FAKE_VENDOR,
    ROLLS,
    UNIVERSE,
    MockGateway,
    build_bars,
    build_listings,
    ct,
)

ROOT = Path(__file__).resolve().parents[1]
FIRST, LAST = date(2026, 9, 1), date(2027, 3, 31)


def config_multipliers() -> dict[str, float]:
    raw = json.loads((ROOT / "forward/config_f1.json").read_text(encoding="utf-8"))
    return {k: float(v["multiplier"]) for k, v in raw["instruments"].items()}


def make(listings=None, now=None, extra=None):
    listings = listings if listings is not None else build_listings(FIRST, LAST)
    bars = build_bars(listings, FIRST, LAST)
    gw = MockGateway({**listings, **(extra or {})}, bars, now=now or ct(2026, 11, 2, 19))
    session = GatewaySession(
        gw,
        ConnectionParams.from_env(ENV),
        policy=RetryPolicy(backoff_base_s=0),
        sleep=lambda s: None,
    )
    return gw, ContractResolver(
        session, FAKE_VENDOR, ROLLS, config_multipliers=config_multipliers()
    )


def test_specs_cover_the_universe_and_match_config_f1_multipliers():
    assert set(IB_SPECS) == set(UNIVERSE) == set(ROLLS)
    check_specs(IB_SPECS, config_multipliers())
    bad = dict(config_multipliers(), MZC=5.0)
    with pytest.raises(ContractResolutionError, match="MZC"):
        check_specs(IB_SPECS, bad)


def test_resolves_a_contract_id_to_one_ib_future_with_the_declared_fields():
    gw, resolver = make()
    rc = resolver.resolve("MNQ", "MNQZ26")
    query = gw.calls[-1][1]["contract"]
    assert (query.symbol, query.lastTradeDateOrContractMonth, query.exchange, query.currency) == (
        "MNQ",
        "202612",
        "CME",
        "USD",
    )
    assert query.tradingClass == "MNQ"
    assert query.includeExpired is True and query.secType == "FUT"
    assert rc.contract_id == "MNQZ26" and rc.con_id > 0
    assert rc.last_trade_date == R.expiry_guard(ROLLS["MNQ"], "MNQZ26")
    assert resolver.identify(rc.contract) == rc
    resolver.resolve("MNQ", "MNQZ26")
    assert gw.count("reqContractDetails") == 1  # cached


def test_micro_henry_hub_resolves_as_symbol_mhng_trading_class_mng():  # facts I7
    gw, resolver = make()
    rc = resolver.resolve("MNG", "MNGF27")
    query = gw.calls[-1][1]["contract"]
    assert (query.symbol, query.tradingClass, query.exchange) == ("MHNG", "MNG", "NYMEX")
    assert rc.contract_id == "MNGF27"


def test_an_expired_contract_resolves_only_through_include_expired():
    listings = build_listings(FIRST, LAST)
    gw, resolver = make(listings, now=ct(2027, 1, 15, 19))
    rc = resolver.resolve("MNQ", "MNQU26")  # expired 2026-09-18
    assert rc.last_trade_date < date(2027, 1, 15)
    plain = replace(resolver.query("MNQ", "MNQU26"), includeExpired=False)
    assert gw.reqContractDetails(plain) == []


def test_an_ambiguous_contract_is_an_error_never_a_guess():
    listings = build_listings(FIRST, LAST)
    twin = listings[("MGC", "MGCZ26")]
    extra = {("MGC", "twin"): replace(twin, contract=replace(twin.contract, conId=99999))}
    _, resolver = make(listings, extra=extra)
    with pytest.raises(ContractResolutionError, match="ambiguous, 2 matches"):
        resolver.resolve("MGC", "MGCZ26")


def test_an_unknown_contract_is_not_found():
    listings = {k: v for k, v in build_listings(FIRST, LAST).items() if k != ("MCL", "MCLF27")}
    _, resolver = make(listings)
    with pytest.raises(ContractNotFound):
        resolver.resolve("MCL", "MCLF27")


@pytest.mark.parametrize(
    "field,value,match",
    [
        ("multiplier", "50", "multiplier"),
        ("secType", "CONTFUT", "secType"),
        ("conId", 0, "conId"),
    ],
)
def test_a_contract_whose_fields_differ_from_the_spec_is_refused(field, value, match):
    listings = build_listings(FIRST, LAST)
    det = listings[("MZC", "MZCH27")]
    listings[("MZC", "MZCH27")] = replace(det, contract=replace(det.contract, **{field: value}))
    _, resolver = make(listings)
    with pytest.raises(ContractResolutionError, match=match):
        resolver.resolve("MZC", "MZCH27")


def test_contract_month_and_price_magnifier_are_checked():
    listings = build_listings(FIRST, LAST)
    det = listings[("MZS", "MZSF27")]
    listings[("MZS", "MZSF27")] = replace(det, priceMagnifier=1)
    _, resolver = make(listings)
    with pytest.raises(ContractResolutionError, match="priceMagnifier"):
        resolver.resolve("MZS", "MZSF27")


def test_foreign_roots_and_off_cycle_months_are_refused_before_any_request():
    gw, resolver = make()
    with pytest.raises(ValueError):
        resolver.resolve("MNQ", "NQZ26")
    with pytest.raises(ValueError):
        resolver.resolve("MNQ", "MNQF27")  # F is not in MNQ's HMUZ cycle
    with pytest.raises(ContractResolutionError):
        resolver.resolve("ES", "ESZ26")
    assert gw.count("reqContractDetails") == 0


def test_cents_quoted_grains_are_converted_exactly():
    assert to_runner_price(425.25, 100) == 4.2525 == float("4.2525")
    assert to_runner_price(45.12, 100) == 0.4512
    assert to_runner_price(21034.25, 1) == 21034.25
    with pytest.raises(Exception, match="not finite"):
        to_runner_price(float("nan"), 1)


def test_contract_neighbours_and_the_roll_overlap_window():
    mnq = ROLLS["MNQ"]
    assert previous_contract(mnq, "MNQH27") == "MNQZ26"
    assert next_contract(mnq, "MNQZ26") == "MNQH27"
    assert previous_contract(ROLLS["MZS"], "MZSF27") == "MZSX26"
    roll = R.roll_date(mnq, 2026, 12)  # 2026-12-10, 6 weekdays before the 3rd Friday (12-18)
    assert roll == date(2026, 12, 10)
    assert contracts_for_day(mnq, date(2026, 12, 9)) == ("MNQZ26",)
    assert contracts_for_day(mnq, roll) == ("MNQH27", "MNQZ26")
    assert contracts_for_day(mnq, date(2026, 12, 18)) == ("MNQH27", "MNQZ26")
    assert contracts_for_day(mnq, date(2026, 12, 21)) == ("MNQH27",)
