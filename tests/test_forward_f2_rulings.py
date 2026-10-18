"""Lead rulings of 2026-10-18 on F2BookCoder's Q5, Q7, Q9, Q15, Q16/Q17 (see late_ca tests), Q18."""

from datetime import date

import pytest

from forward import strategy_f2
from forward.etf_bars import EtfBar, EtfDayRow, InMemoryEtfSource
from forward.runner_f2 import PaperBookF2, RunnerError, load_book_config

CFG = load_book_config()
ETFS = CFG.symbols
W = date(2026, 11, 4)
D1, D2, D3, D4 = date(2026, 11, 5), date(2026, 11, 6), date(2026, 11, 9), date(2026, 11, 10)
WARMUP = (EtfDayRow(W, {"QQQ": EtfBar(500.0), "TLT": EtfBar(90.0), "BIL": EtfBar(91.5)}),)


def day(prev, bil_ret=0.0, etfs=True):
    out = {"BIL": EtfBar(91.5, bil_ret, prev)}
    if etfs:
        out.update({"QQQ": EtfBar(500.0, 0.0, prev), "TLT": EtfBar(90.0, 0.0, prev)})
    return out


def fixed(tg):
    def fn(history, held, config, *, decision_date):
        return {s: float(tg.get(s, 0.0)) for s in ETFS}

    return fn


def book(tmp_path, data, tg, **kw):
    return PaperBookF2(
        tmp_path / "f2.jsonl",
        InMemoryEtfSource(data),
        CFG,
        warmup=WARMUP,
        target_fn=fixed(tg),
        **kw,
    )


def test_q15_late_bil_distribution_corrects_the_cash_terms(tmp_path):
    data = {D1: day(W), D2: day(D1), D3: day(D2), D4: day(D3)}
    bk = book(tmp_path, data, {"QQQ": 100.0})
    *_, r3 = bk.run_dates([D1, D2, D3])
    assert r3["exposure"]["long_notional_held_into_usd"] == 50000.0
    act = {
        "symbol": "BIL",
        "type": "cash_dividend",
        "ex_date": "2026-11-09",
        "amount_or_ratio": 0.30,
    }
    r4 = bk.run_date(D4, late_actions=[act])
    (entry,) = r4["late_ca"]
    assert entry["long_notional_ex_usd"] == 50000.0
    assert entry["dr_c"] == pytest.approx(0.30 / 91.5)
    assert r4["pnl"]["late_ca"] == pytest.approx(-50000.0 * 0.30 / 91.5)
    assert "late_ca:BIL" in r4["flags"]


def test_q5_accruals_after_a_missing_day_charged_in_the_next_record(tmp_path):
    data = {D1: day(W), D2: day(D1), D4: day(D2, bil_ret=0.0002)}  # D3 (Mon) missing
    bk = book(tmp_path, data, {"TLT": -50.0, "QQQ": 100.0})
    *_, r2, r3, r4 = bk.run_dates([D1, D2, D3, D4])
    assert r3["missing_day"] and r3["accrual_days"] == 0 and r3["accrual_base"] == "2026-11-06"
    assert r4["accrual_days"] == 4  # Fri D2 -> Tue D4: the missing Monday's accruals included
    assert r4["pnl"]["shorts"] == pytest.approx(-4500 * (0.0002 + 0.01 * 4 / 360))
    assert r4["pnl"]["leverage"] == pytest.approx(-25000 * 0.025 * 4 / 360)
    assert r4["accrual_base"] == "2026-11-10"


def test_q7_a_bil_only_day_is_a_missing_day(tmp_path):
    data = {D1: day(W), D2: day(D1, etfs=False), D3: day(D2)}
    bk = book(tmp_path, data, {"QQQ": 10.0})
    r1, r2, r3 = bk.run_dates([D1, D2, D3])
    assert r2["missing_day"] and r2["net_pnl"] == 0.0 and r2["missing_reason"].startswith("no bar")
    assert "missing_day" in r2["flags"] and "order_expired:QQQ" in r2["flags"]
    assert set(r2["bars"]) == {"BIL"} and r2["orders"] == {} and r2["positions"]["QQQ"] == 0.0
    assert "prev_date_mismatch:BIL" not in r3["flags"]
    assert r3["accrual_days"] == 4  # from D1, the last record that is not a missing day


def test_q9_step5_rounds_scaled_positions_toward_zero_and_gross_never_exceeds_cap():
    syms = ["A", "B", "C", "D"]
    close = {"A": 97.13, "B": 41.07, "C": 100.0, "D": 63.3}
    res = strategy_f2.position_steps(
        syms,
        {"A": 200.0, "B": 300.0, "C": -100.0},
        {"A": 40.0, "B": 60.0, "C": 20.0},
        {"A": 203.9, "B": 305.9, "C": -101.0, "D": 50.0},  # D: no close on t, carried
        close,
        set(),
        cap_usd=45000.0,  # G = 41,747 (no first cap); held in the band: gross 45,633.12 > B
        buffer_size=0.1,
        steps=1000,
    )
    sc = res.second_check
    assert not res.cap_bound  # C + G = 3,165 + 41,747 = 44,912 <= B (wave 3, S4)
    assert sc["applied"] and sc["gross_before_usd"] == pytest.approx(45633.12)
    # wave 3, S1: the short is scaled too (toward zero to whole shares); carried D untouched
    assert res.targets["C"] == -99.0 and res.targets["D"] == 50.0
    assert res.target_gross_usd <= 45000.0
    for s in ("A", "B"):
        scaled = {"A": 203.9, "B": 305.9}[s] * sc["factor"]
        assert res.targets[s] <= scaled and scaled - res.targets[s] < 0.001
        assert res.targets[s] == strategy_f2.floor_long(res.targets[s], 1000)


def test_q18_feed_recorded_and_fixed(tmp_path):
    data = {D1: day(W), D2: day(D1)}
    r1 = book(tmp_path, data, {}).run_date(D1)
    assert r1["feed"] == "sip"
    with pytest.raises(RunnerError, match="feed"):
        book(tmp_path, data, {}, feed="iex").run_date(D2)
    other = PaperBookF2(
        tmp_path / "g.jsonl", InMemoryEtfSource(data), CFG, warmup=WARMUP, feed="iex"
    ).run_date(D1)
    assert other["feed"] == "iex" and other["config_sha256"] == r1["config_sha256"]
    with pytest.raises(RunnerError, match="registered"):
        book(tmp_path, data, {}, feed="delayed_sip")
