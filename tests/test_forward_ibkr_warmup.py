"""Warm-up assembly and CSV export (Stage E.24; synthetic prices, mock gateway, no network)."""

from __future__ import annotations

import hashlib
from datetime import date

import pytest

from forward import rolls as R
from forward.history import back_adjusted_series, load_warmup
from forward.ibkr_gateway import (
    ConnectionParams,
    GatewaySession,
    NoHistoricalData,
    RetryPolicy,
    SourceUnavailable,
)
from forward.runner import PaperRunner, RunnerConfig, load_tables
from forward.sources import CsvSettlementSource
from forward.sources_ibkr import (
    ContractNotFound,
    ContractResolver,
    assemble_rows,
    export_csv,
    fetch_warmup_prices,
    rows_to_days,
    warmup_summary,
    write_warmup,
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
    ib_price,
)

FIRST, START = date(2024, 3, 1), date(2026, 11, 2)
LAST = date(2026, 10, 30)
NOW = ct(2026, 11, 1, 12)


def hand_rows():
    mnq = ROLLS["MNQ"]
    roll = R.roll_date(mnq, 2026, 12)  # 2026-12-10
    days = [date(2026, 12, d) for d in (8, 9, 10, 11, 14)]
    prices = {
        "MNQ": {
            "MNQZ26": {d: 100.0 + i for i, d in enumerate(days)},
            "MNQH27": {d: 110.0 + i for i, d in enumerate(days) if d >= roll},
        }
    }
    return days, prices


def test_switch_rows_carry_both_prices_and_back_adjustment_is_additive():
    days, prices = hand_rows()
    rows = assemble_rows(prices, ROLLS, days[0], days[-1])
    refs = [r.reference["MNQ"] for r in rows]
    assert refs == ["MNQZ26", "MNQZ26", "MNQH27", "MNQH27", "MNQH27"]
    assert dict(rows[2].prices["MNQ"]) == {"MNQZ26": 102.0, "MNQH27": 112.0}
    adjusted = [p for _, p in back_adjusted_series(rows, "MNQ")]
    assert adjusted == [110.0, 111.0, 112.0, 113.0, 114.0]  # shift 112 - 102 = 10


def test_a_switch_waits_for_a_day_where_both_contracts_have_a_price():
    days, prices = hand_rows()
    del prices["MNQ"]["MNQH27"][date(2026, 12, 10)]
    rows = assemble_rows(prices, ROLLS, days[0], days[-1])
    assert [r.reference["MNQ"] for r in rows][2:4] == ["MNQZ26", "MNQH27"]
    back_adjusted_series(rows, "MNQ")


def make(listed_from=None, clock=False):
    listings = build_listings(FIRST, START)
    bars = build_bars(listings, FIRST, LAST, listed_from=listed_from)
    gw = MockGateway(listings, bars, now=NOW)
    session = GatewaySession(
        gw,
        ConnectionParams.from_env(ENV),
        policy=RetryPolicy(backoff_base_s=0),
        sleep=lambda s: None,
        **({"clock": gw.monotonic} if clock else {}),  # the mock clock (stall fault mode)
    )
    multipliers, _ = load_tables("forward/tables_f1.json")
    return (
        gw,
        session,
        ContractResolver(session, FAKE_VENDOR, ROLLS, config_multipliers=multipliers),
    )


def test_full_warmup_round_trip_through_load_warmup_and_the_runner(tmp_path):
    gw, session, resolver = make(listed_from={"MZC": date(2025, 2, 24)})
    for k in [
        k for k in gw.listings if k[0] == "MZC" and R.parse_contract(ROLLS["MZC"], k[1]) < (2025, 3)
    ]:
        del gw.listings[k]  # the micro grains were listed later: IB knows no earlier contract
    old = [k for k in gw.listings if k[1] in ("MNQH24", "MNQM24")]
    for k in old:  # older than 2 years at the read: IB no longer knows them (facts I5)
        del gw.listings[k]
    prices, notes = fetch_warmup_prices(
        session, resolver, ROLLS, FIRST, LAST, today=date(2026, 11, 1)
    )
    assert {(n.instrument, n.contract_id) for n in notes} >= {("MNQ", "MNQH24"), ("MNQ", "MNQM24")}
    rows = assemble_rows(prices, ROLLS, FIRST, LAST)
    path = tmp_path / "warmup.jsonl"
    digest = write_warmup(rows, path)
    assert load_warmup(path) == rows
    assert digest == hashlib.sha256(path.read_bytes()).hexdigest()
    assert (tmp_path / "warmup.jsonl.sha256").read_text() == f"{digest}  warmup.jsonl\n"
    summary = warmup_summary(rows, ROLLS, UNIVERSE)
    assert summary["MZC"]["first_date"] == "2025-02-24"
    assert summary["MNQ"]["first_date"] > summary["MCL"]["first_date"] == "2024-03-01"
    assert not any(s["open_roll"] for s in summary.values())
    for inst in UNIVERSE:  # every switch row carries both legs
        assert len(back_adjusted_series(rows, inst)) == summary[inst]["rows"] > 300
    assert rows[-1].reference["MNQ"] == R.active_contract(ROLLS["MNQ"], LAST)
    with pytest.raises(FileExistsError):
        write_warmup(rows, path)
    multipliers, costs = load_tables("forward/tables_f1.json")
    runner = PaperRunner(
        tmp_path / "l.jsonl",
        _InMemory(rows[-1].date),
        RunnerConfig(multipliers, costs, ROLLS, {}),
        target_fn=lambda h, p, c: {i: 0 for i in p},
        warmup=load_warmup(path),
    )
    assert runner.warmup == rows


class _InMemory:
    def __init__(self, day):
        self.day = day

    def settlements(self, trade_date):
        return {}


def test_a_contract_inside_the_two_year_depth_must_resolve():
    gw, session, resolver = make()
    del gw.listings[("MGC", "MGCZ25")]
    with pytest.raises(ContractNotFound):
        fetch_warmup_prices(
            session, resolver, ROLLS, FIRST, LAST, today=date(2026, 11, 1), instruments=["MGC"]
        )


def test_csv_export_round_trips_through_the_frozen_csv_source(tmp_path):
    days, prices = hand_rows()
    rows = assemble_rows(prices, ROLLS, days[0], days[-1])
    path = tmp_path / "s.csv"
    assert export_csv(rows_to_days(rows), path) == 6
    src = CsvSettlementSource(path, ["MNQ"])
    for r in rows:
        assert src.settlements(r.date) == {i: dict(q) for i, q in r.prices.items()}
    assert export_csv(rows_to_days(rows), path) == 0  # idempotent
    changed = rows_to_days(rows)
    changed[days[0]]["MNQ"]["MNQZ26"] = 1.5
    with pytest.raises(Exception, match="different rows"):
        export_csv(changed, path)
    assert "close_last_trade" in path.read_text().splitlines()[0]
    assert ib_price("MZC", "MZCZ26", days[0]) > 100  # IB cents in the mock, runner dollars out


def test_a_stalled_window_request_raises_and_never_shortens_the_series():
    # B1 (wave 3): a stall that cuts the tail (and its roll date) off a window raises
    gw, session, resolver = make(clock=True)
    con = gw.listings[("MNQ", "MNQZ25")].contract.conId
    gw.stall[con] = [10] * 4
    with pytest.raises(SourceUnavailable, match="timed out"):
        fetch_warmup_prices(
            session, resolver, ROLLS, FIRST, LAST, today=date(2026, 11, 1), instruments=["MNQ"]
        )


def test_a_no_data_answer_inside_the_two_year_depth_raises():
    # S1 (wave 3): HMDS "returned no data" for MNQU25 (inside the depth) is not a skip
    gw, session, resolver = make()
    gw.no_data.add(gw.listings[("MNQ", "MNQU25")].contract.conId)
    with pytest.raises(NoHistoricalData, match="MNQU25"):
        fetch_warmup_prices(
            session, resolver, ROLLS, FIRST, LAST, today=date(2026, 11, 1), instruments=["MNQ"]
        )


def test_a_no_data_answer_beyond_the_depth_is_noted_and_skipped():
    gw, session, resolver = make()
    gw.no_data.add(gw.listings[("MNQ", "MNQH24")].contract.conId)  # anchor 2024-03: beyond
    prices, notes = fetch_warmup_prices(
        session, resolver, ROLLS, FIRST, LAST, today=date(2026, 11, 1), instruments=["MNQ"]
    )
    assert ("MNQ", "MNQH24", "server: no data for the window") in {
        (n.instrument, n.contract_id, n.note) for n in notes
    }
    assert "MNQH24" not in prices["MNQ"] and "MNQZ25" in prices["MNQ"]


def test_an_open_roll_with_a_stale_last_date_is_refused():
    # S1 (wave 3): the roll MNQU26 -> MNQZ26 can never happen (no day with both legs), so the
    # reference sticks on U26 and the series stops at its anchor
    from forward.sources_ibkr import stale_open_rolls

    listings = build_listings(FIRST, START)
    holes = {("MNQZ26", d) for d in _weekdays(date(2026, 9, 10), date(2026, 9, 18))}
    bars = build_bars(listings, FIRST, LAST, holes=holes)
    rows = assemble_rows(_prices(listings, bars, ["MNQ", "MCL"]), ROLLS, FIRST, LAST)
    summary = warmup_summary(rows, ROLLS, ["MNQ", "MCL"])
    assert summary["MNQ"]["open_roll"] and summary["MNQ"]["last_date"] == "2026-09-18"
    assert stale_open_rolls(summary, LAST) == ["MNQ"]
    fresh = {**summary["MNQ"], "last_date": "2026-10-27"}  # a roll deferred at the very end
    assert stale_open_rolls({"MNQ": fresh}, LAST) == []


def _weekdays(a, b):
    from tests._forward_ibkr_mock import weekdays

    return weekdays(a, b)


def _prices(listings, bars, instruments):
    out = {}
    for (inst, cid), det in listings.items():
        if inst in instruments and bars[det.contract.conId]:
            divisor = 100 if inst in ("MZC", "MZS", "MZL") else 1
            out.setdefault(inst, {})[cid] = {
                d: p / divisor for d, p in bars[det.contract.conId].items()
            }
    return out
