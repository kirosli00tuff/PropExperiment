"""E22-F2 paper book (prereg sections 5-6): fills, costs, P&L terms, missing data, ledger."""

from datetime import date

import pytest

from forward.etf_bars import EtfBar, EtfDayRow, InMemoryEtfSource, SourceUnavailable
from forward.ledger import verify
from forward.runner_f2 import (
    SCHEMA,
    LedgerConflictError,
    PaperBookF2,
    RunnerError,
    ceil_cent,
    load_book_config,
)

CFG = load_book_config()
ETFS = CFG.symbols
W = date(2026, 11, 4)  # Wed, warm-up
D1, D2, D3, D4 = date(2026, 11, 5), date(2026, 11, 6), date(2026, 11, 9), date(2026, 11, 10)


def B(c, r=None, p=None):
    return EtfBar(c, r, p)


def flat_day(prev, qqq=500.0, tlt=90.0, bil=91.5):
    return {"QQQ": B(qqq, 0.0, prev), "TLT": B(tlt, 0.0, prev), "BIL": B(bil, 0.0, prev)}


WARMUP = (EtfDayRow(W, {"QQQ": B(500.0), "TLT": B(90.0), "BIL": B(91.5)}),)


def fixed_targets(tg):
    def fn(history, held, config, *, decision_date):
        return {s: float(tg.get(s, 0.0)) for s in ETFS}

    return fn


def book(tmp_path, data, tg, name="f2.jsonl"):
    return PaperBookF2(
        tmp_path / name, InMemoryEtfSource(data), CFG, warmup=WARMUP, target_fn=fixed_targets(tg)
    )


BASE = {D1: flat_day(W), D2: flat_day(D1)}


def test_fills_costs_and_pnl_terms_with_weekend_accrual(tmp_path):
    data = {
        **BASE,
        D3: {"QQQ": B(505.0, 0.01, D2), "TLT": B(89.1, -0.01, D2), "BIL": B(91.5, 0.0003, D2)},
    }
    bk = book(tmp_path, data, {"QQQ": 100.0, "TLT": -50.0})
    r1, r2, r3 = bk.run_dates([D1, D2, D3])
    assert (
        r1["schema"] == SCHEMA
        and r1["net_pnl"] == 0.0
        and r1["orders"] == {"QQQ": 100.0, "TLT": -50.0}
    )
    assert [(f["symbol"], f["shares"], f["price"]) for f in r2["fills"]] == [
        ("QQQ", 100.0, 500.0),
        ("TLT", -50.0, 90.0),
    ]
    c = r2["costs"]
    assert c["half_spread"] == pytest.approx(1.5)
    assert c["sec_fee"] == 0.10  # 4500 x 0.0000206 = 0.0927 -> up to 0.10
    assert c["finra_taf"] == 0.0
    assert c["cat_fee"] == 0.01  # 150 x 0.000003 -> up to 0.01
    assert r2["net_pnl"] == pytest.approx(-1.61)
    assert r3["accrual_days"] == 3
    p = r3["pnl"]
    assert p["excess"] == pytest.approx(50000 * (0.01 - 0.0003) + (-4500) * (-0.01 - 0.0003))
    assert p["shorts"] == pytest.approx(-4500 * (0.0003 + 0.01 * 3 / 360))
    assert p["leverage"] == pytest.approx(-25000 * 0.025 * 3 / 360)
    assert p["costs"] == 0.0
    assert r3["net_pnl"] == pytest.approx(524.4166666666667)
    assert r3["positions"]["QQQ"] == 100.0 and r3["positions"]["TLT"] == -50.0
    assert verify(tmp_path / "f2.jsonl").ok


def test_distribution_day_reinvests_and_pnl_is_total_return(tmp_path):
    r = 89.3 / 90.0 - 1
    data = {**BASE, D3: {"QQQ": B(500.0, 0.0, D2), "TLT": B(89.0, r, D2), "BIL": B(91.5, 0.0, D2)}}
    rec = book(tmp_path, data, {"TLT": 100.0}).run_dates([D1, D2, D3])[-1]
    assert rec["positions_before_fills"]["TLT"] == pytest.approx(100 * 89.3 / 89.0)
    assert rec["pnl_by_symbol"]["TLT"]["etf_pnl"] == pytest.approx(-70.0)
    assert rec["pnl"]["excess"] == pytest.approx(-70.0)
    # the shares changed; the order from D2 (none) leaves them; value = N x (1 + r)
    assert rec["positions"]["TLT"] * 89.0 == pytest.approx(9000 * (1 + r))


def test_split_day_changes_shares_by_ratio(tmp_path):
    data = {
        **BASE,
        D3: {
            "QQQ": B(251.0, 251.0 * 2 / 500.0 - 1, D2),
            "TLT": B(90.0, 0.0, D2),
            "BIL": B(91.5, 0.0, D2),
        },
    }
    rec = book(tmp_path, data, {"QQQ": 10.0}).run_dates([D1, D2, D3])[-1]
    assert rec["positions_before_fills"]["QQQ"] == pytest.approx(20.0)
    assert rec["pnl"]["excess"] == pytest.approx(5000 * 0.004)


def test_sign_change_is_two_legs(tmp_path):
    tg = {"TLT": 100.0}
    data = {**BASE, D3: flat_day(D2), D4: flat_day(D3)}
    bk = book(tmp_path, data, tg)
    bk.run_dates([D1, D2])
    tg["TLT"] = -50.0
    bk.run_date(D3)
    rec = bk.run_date(D4)
    assert [(f["leg"], f["shares"]) for f in rec["fills"]] == [("close", -100.0), ("open", -50.0)]
    assert rec["costs"]["sec_fee"] == ceil_cent(150 * 90 * 0.0000206)
    assert rec["positions"]["TLT"] == -50.0


def test_missing_etf_expires_order_and_accrues_on_return(tmp_path):
    data = {D1: flat_day(W), D2: {"TLT": B(90.0, 0.0, D1), "BIL": B(91.5, 0.0, D1)}}
    bk = book(tmp_path, data, {"QQQ": 10.0})
    r1, r2 = bk.run_dates([D1, D2])
    assert "missing:QQQ" in r2["flags"] and "order_expired:QQQ" in r2["flags"]
    assert r2["expired_orders"] == {"QQQ": 10.0} and r2["fills"] == []
    assert r2["targets"]["QQQ"] == 0.0 and "QQQ" not in r2["orders"]
    # with a position: hold QQQ, then QQQ misses D3 and returns D4 with r spanning the gap
    data2 = {
        **BASE,
        D3: {"TLT": B(90.0, 0.0, D2), "BIL": B(91.5, 0.0001, D2)},
        D4: {"QQQ": B(510.0, 0.02, D2), "TLT": B(90.0, 0.0, D3), "BIL": B(91.5, 0.0001, D3)},
    }
    bk2 = book(tmp_path, data2, {"QQQ": 10.0}, name="g.jsonl")
    *_, r3, r4 = bk2.run_dates([D1, D2, D3, D4])
    assert "missing:QQQ" in r3["flags"]
    assert r3["pnl_by_symbol"]["QQQ"]["etf_pnl"] == 0.0
    assert r3["pnl"]["excess"] == pytest.approx(-5000 * 0.0001)  # cash part accrues
    assert r4["pnl_by_symbol"]["QQQ"]["etf_pnl"] == pytest.approx(5000 * 0.02)
    assert r4["pnl"]["excess"] == pytest.approx(5000 * (0.02 - 0.0001))


def test_missing_bil_defers_cash_terms(tmp_path):
    data = {**BASE, D3: {"QQQ": B(505.0, 0.01, D2), "TLT": B(90.0, 0.0, D2)}}
    rec = book(tmp_path, data, {"QQQ": 10.0}).run_dates([D1, D2, D3])[-1]
    assert "missing:BIL" in rec["flags"] and rec["cash"]["r_c"] is None
    assert rec["pnl"]["excess"] == pytest.approx(5000 * 0.01)


def test_missing_day_zero_pnl_flagged(tmp_path):
    data = {D1: flat_day(W), D3: flat_day(D1)}
    bk = book(tmp_path, data, {"QQQ": 10.0})
    r1 = bk.run_date(D1)
    r2 = bk.run_date(D2)  # absent from the source -> Missing -> a missing day
    assert r2["missing_day"] and r2["net_pnl"] == 0.0
    assert "missing_day" in r2["flags"] and "order_expired:QQQ" in r2["flags"]
    assert r2["orders"] == {} and r2["positions"]["QQQ"] == 0.0
    assert r1["orders"] == {"QQQ": 10.0}


def test_declared_closed_gap_and_undeclared_refused(tmp_path):
    data = {D1: flat_day(W), D3: flat_day(D1)}
    bk = book(tmp_path, data, {})
    bk.run_date(D1)
    with pytest.raises(RunnerError, match="no record"):
        bk.run_date(D3)
    with pytest.raises(RunnerError, match="strictly inside"):
        bk.run_date(D3, declared_closed=[date(2026, 11, 7)])
    rec = bk.run_date(D3, declared_closed=[D2])
    assert rec["declared_closed"] == ["2026-11-06"] and rec["accrual_days"] == 4


def test_source_unavailable_writes_nothing(tmp_path):
    data = {D1: flat_day(W), D2: SourceUnavailable("timeout")}
    bk = book(tmp_path, data, {})
    bk.run_date(D1)
    before = (tmp_path / "f2.jsonl").read_bytes()
    with pytest.raises(SourceUnavailable):
        bk.run_date(D2)
    assert (tmp_path / "f2.jsonl").read_bytes() == before


def test_rerun_returns_stored_and_conflict_raises(tmp_path):
    data = {**BASE}
    bk = book(tmp_path, data, {"QQQ": 10.0})
    r1, r2 = bk.run_dates([D1, D2])
    size = (tmp_path / "f2.jsonl").stat().st_size
    assert bk.run_date(D1) == r1 and bk.run_date(D2) == r2
    assert (tmp_path / "f2.jsonl").stat().st_size == size
    bk2 = book(tmp_path, {**BASE, D2: flat_day(D1, qqq=501.0)}, {"QQQ": 10.0})
    with pytest.raises(LedgerConflictError):
        bk2.run_date(D2)
    with pytest.raises(RunnerError):
        bk.run_date(date(2026, 11, 3))
    assert r2["prev_record_sha256"] == r1["record_sha256"]


def test_config_change_refused(tmp_path):
    bk = book(tmp_path, dict(BASE), {})
    bk.run_date(D1)
    cfg2 = load_book_config()
    cfg2.config["financing"]["borrow_fee_b"]["value"] = 0.02
    other = PaperBookF2(tmp_path / "f2.jsonl", InMemoryEtfSource(BASE), cfg2, warmup=WARMUP)
    with pytest.raises(RunnerError, match="another configuration"):
        other.run_date(D2)


def test_default_rule_runs_on_short_warmup(tmp_path):
    bk = PaperBookF2(tmp_path / "f2.jsonl", InMemoryEtfSource(dict(BASE)), CFG, warmup=WARMUP)
    r1 = bk.run_date(D1)
    assert r1["targets"]["QQQ"] == 0.0 and r1["exposure"]["n_live"] == 0


def test_bil_return_spans_its_gap_and_charges_notional_held_into_return_day(tmp_path):
    data = {
        **BASE,
        D3: {"QQQ": B(505.0, 0.01, D2), "TLT": B(90.0, 0.0, D2)},
        D4: {"QQQ": B(505.0, 0.0, D3), "TLT": B(90.0, 0.0, D3), "BIL": B(91.6, 0.0002, D2)},
    }
    *_, r3, r4 = book(tmp_path, data, {"QQQ": 10.0}).run_dates([D1, D2, D3, D4])
    assert r3["cash"]["r_c"] is None and r3["pnl"]["excess"] == pytest.approx(5000 * 0.01)
    assert "prev_date_mismatch:BIL" not in r4["flags"]  # BIL's prev is its last bar (D2)
    assert r4["cash"]["r_c"] == 0.0002
    assert r4["pnl"]["excess"] == pytest.approx(-5050 * 0.0002)
    assert r4["accrual_days"] == 1
