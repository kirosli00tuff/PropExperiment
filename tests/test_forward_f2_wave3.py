"""Wave 3 (lead rulings on reg_review.md, prereg sections 4-6 and 8 as revised 11:50-11:55 PDT):
B1 r and the share update from the RECORDED previous close and the session's actions over the
whole span (prev, t], prev_close_mismatch at 1e-6 relative; B2 the late-action key carries the
amount; S1 step 5 scales longs and shorts; S2 a late distribution books q_ex x k x amount; S4 the
carried notional C is held fixed in step 2; S6 the suspect-split guard; S7 delisting after 10
sessions and SGOV replacing BIL; S8 the tests the review listed; N5 and N7."""

import inspect
import math
from datetime import date, timedelta
from types import SimpleNamespace

import pytest

from forward import evaluate_f2, strategy_f2
from forward.etf_bars import EtfBar, EtfDayRow, InMemoryEtfSource
from forward.runner_f2 import PaperBookF2, load_book_config
from forward.sources_alpaca import CorporateAction

CFG = load_book_config()
ETFS = CFG.symbols
W = date(2026, 11, 4)
BOOKED = {"cash_dividend", "capital_gains_distribution", "forward_split", "reverse_split"}


def sessions(n, first=date(2026, 11, 5)):
    out, d = [], first
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d)
        d += timedelta(days=1)
    return out


S = sessions(16)
WARMUP = (EtfDayRow(W, {"QQQ": EtfBar(500.0), "TLT": EtfBar(90.0), "BIL": EtfBar(91.5)}),)


def bars(prev, **closes):
    """Source bars with ret 0 and prev_date ``prev``; QQQ 500, TLT 90, BIL 91.5 unless given;
    a symbol given as None has no bar."""
    base = {"QQQ": 500.0, "TLT": 90.0, "BIL": 91.5, **closes}
    return {s: EtfBar(c, 0.0, prev) for s, c in base.items() if c is not None}


class SpanSource:
    """fetch_day (the source's bars and the actions inside the source's own r) plus
    corporate_actions(start, end, symbols) over any span (AlpacaFixer's contract): every action
    published by the session being read; the runner filters by ex_date."""

    def __init__(self, days, published=None, source_applied=None):
        self.inner = InMemoryEtfSource(days)
        self.published = published or {}
        self.source_applied = source_applied or {}
        self.today = None
        self.asked = []

    def bars(self, t):
        return self.inner.bars(t)

    def fetch_day(self, t):
        self.today = t
        return SimpleNamespace(
            answer=lambda: self.inner.bars(t), applied=self.source_applied.get(t, {}), flags={}
        )

    def corporate_actions(self, start, end, symbols=None):
        self.asked.append((start, end, None if symbols is None else tuple(symbols)))
        acts = [a for d, lst in self.published.items() if d <= self.today for a in lst]
        return SimpleNamespace(
            booked=tuple(a for a in acts if a.kind in BOOKED),
            other=tuple(a for a in acts if a.kind not in BOOKED),
        )


def recorder(tg, seen):
    def fn(history, held, config, *, decision_date):
        seen[decision_date] = {
            s: {row.date: row.bars[s].ret for row in history if s in row.bars}
            for s in ("QQQ", "TLT", "BIL")
        }
        return {s: float(tg.get(s, 0.0)) for s in ETFS}

    return fn


def book(tmp_path, src, tg, seen=None):
    fn = recorder(tg, {} if seen is None else seen)
    return PaperBookF2(tmp_path / "f2.jsonl", src, CFG, warmup=WARMUP, target_fn=fn)


def act(symbol, kind, ex, v):
    return {"symbol": symbol, "type": kind, "ex_date": ex.isoformat(), "amount_or_ratio": v}


def ca(symbol, kind, ex, ratio=None, amount=None):
    return CorporateAction(symbol, kind, ex, ratio, amount, {})


# ------------------------------------------------------------------ B1 ----
def test_b1_revised_previous_close_leaves_the_shares_and_flags_the_mismatch(tmp_path):
    d1, d2, d3 = S[:3]
    revised = {**bars(d2), "QQQ": EtfBar(505.0, 505.0 / 500.25 - 1.0, d2)}  # source: 500.25
    bk = book(tmp_path, SpanSource({d1: bars(W), d2: bars(d1), d3: revised}), {"QQQ": 100.0})
    *_, r3 = bk.run_dates([d1, d2, d3])
    assert r3["positions_before_fills"]["QQQ"] == 100.0  # no drift
    assert r3["share_update"]["QQQ"] == 1.0
    assert r3["pnl_by_symbol"]["QQQ"]["ret"] == pytest.approx(0.01, abs=1e-15)
    assert r3["pnl_by_symbol"]["QQQ"]["etf_pnl"] == pytest.approx(500.0)
    assert r3["bars"]["QQQ"]["ret"] == pytest.approx(0.01, abs=1e-15)
    assert r3["bars"]["QQQ"]["prev_date"] == d2.isoformat()
    assert r3["source_bars"]["QQQ"]["ret"] == 505.0 / 500.25 - 1.0
    assert "prev_close_mismatch:QQQ" in r3["flags"]
    chk = r3["prev_close_check"]["QQQ"]
    assert chk["recorded"] == 500.0 and chk["source"] == pytest.approx(500.25)


def test_b1_agreeing_closes_are_not_flagged(tmp_path):
    d1, d2, d3 = S[:3]
    same = {**bars(d2), "QQQ": EtfBar(505.0, 0.01, d2)}
    bk = book(tmp_path, SpanSource({d1: bars(W), d2: bars(d1), d3: same}), {"QQQ": 100.0})
    *_, r3 = bk.run_dates([d1, d2, d3])
    assert not any(f.startswith("prev_close_mismatch") for f in r3["flags"])
    assert r3["positions_before_fills"]["QQQ"] == 100.0


def test_b1_return_spans_the_recorded_gap_with_the_actions_of_the_whole_span(tmp_path):
    d1, d2, d3, d4 = S[:4]
    split = ca("QQQ", "forward_split", d3, ratio=2.0)  # ex_date inside QQQ's gap
    days = {
        d1: bars(W),
        d2: bars(d1),
        d3: bars(d2, QQQ=None),  # QQQ has no bar after the cutoff on d3
        # the source later holds a d3 bar (250): its own previous session is d3, not d2
        d4: {**bars(d3), "QQQ": EtfBar(251.0, 251.0 / 250.0 - 1.0, d3)},
    }
    src = SpanSource(days, published={d4: [split]})
    bk = book(tmp_path, src, {"QQQ": 100.0})
    *_, r3, r4 = bk.run_dates([d1, d2, d3, d4])
    assert "missing:QQQ" in r3["flags"]
    span = (d2 + timedelta(days=1), d4)  # (d2, d4] as dates
    assert any(a[:2] == span and "QQQ" in a[2] for a in src.asked)
    assert r4["ca_applied"]["QQQ"] == [act("QQQ", "forward_split", d3, 2.0)]
    assert r4["bars"]["QQQ"]["prev_date"] == d2.isoformat()
    assert r4["pnl_by_symbol"]["QQQ"]["ret"] == pytest.approx(2.0 * 251.0 / 500.0 - 1.0)
    assert r4["positions_before_fills"]["QQQ"] == pytest.approx(200.0)
    assert "prev_date_mismatch:QQQ" in r4["flags"]


# ------------------------------------------------------------------ B2 ----
def _tlt_book(tmp_path, published=None, tg=None):
    days = {d: bars(p) for d, p in zip(S[:5], [W, *S[:4]], strict=True)}
    return book(tmp_path, SpanSource(days, published=published), tg or {"TLT": 100.0})


def test_b2_two_late_distributions_on_one_ex_date_are_two_actions(tmp_path):
    d1, d2, d3, d4 = S[:4]
    bk = _tlt_book(tmp_path)
    bk.run_dates([d1, d2, d3])
    late = [act("TLT", "cash_dividend", d3, 0.25), act("TLT", "cash_dividend", d3, 0.10)]
    r4 = bk.run_date(d4, late_actions=late)
    assert sorted(e["amount_or_ratio"] for e in r4["late_ca"]) == [0.10, 0.25]
    assert all(e["booked"] for e in r4["late_ca"])
    assert r4["pnl"]["late_ca"] == pytest.approx(35.0)
    assert len({e["key"] for e in r4["late_ca"]}) == 2


def test_b2_late_distribution_sharing_symbol_type_ex_date_with_a_recorded_one(tmp_path):
    d1, d2, d3, d4 = S[:4]
    bk = _tlt_book(tmp_path, published={d3: [ca("TLT", "cash_dividend", d3, amount=0.25)]})
    *_, r3 = bk.run_dates([d1, d2, d3])
    assert r3["ca_applied"]["TLT"] == [act("TLT", "cash_dividend", d3, 0.25)]
    late = [act("TLT", "cash_dividend", d3, 0.25), act("TLT", "cash_dividend", d3, 0.10)]
    r4 = bk.run_date(d4, late_actions=late)
    (entry,) = r4["late_ca"]
    assert entry["amount_or_ratio"] == 0.10 and entry["pnl_usd"] == pytest.approx(10.0)
    assert r4["late_ca_skipped"]["inside_recorded_return"] == 1


def test_b2_late_distributions_on_different_days_are_each_booked_once(tmp_path):
    d1, d2, d3, d4, d5 = S[:5]
    bk = _tlt_book(tmp_path)
    bk.run_dates([d1, d2, d3])
    a, b = act("TLT", "cash_dividend", d3, 0.25), act("TLT", "cash_dividend", d3, 0.10)
    r4 = bk.run_date(d4, late_actions=[a])
    r5 = bk.run_date(d5, late_actions=[a, b])
    assert r4["pnl"]["late_ca"] == pytest.approx(25.0)
    (entry,) = r5["late_ca"]
    assert entry["amount_or_ratio"] == 0.10 and r5["late_ca_skipped"]["already_handled"] == 1


# ------------------------------------------------------------------ S2, S8 late rule ----
def test_s2_late_distribution_on_a_split_session_books_q_ex_times_k_times_amount(tmp_path):
    d1, d2, d3, d4 = S[:4]
    days = {
        d1: bars(W),
        d2: bars(d1),
        d3: {**bars(d2), "QQQ": EtfBar(251.0, 2 * 251.0 / 500.0 - 1, d2)},
        d4: {**bars(d3), "QQQ": EtfBar(251.0, 0.0, d3)},
    }
    split = ca("QQQ", "forward_split", d3, ratio=2.0)
    bk = book(tmp_path, SpanSource(days, published={d3: [split]}), {"QQQ": 10.0})
    bk.run_dates([d1, d2, d3])
    r4 = bk.run_date(d4, late_actions=[act("QQQ", "cash_dividend", d3, 1.0)])
    (entry,) = r4["late_ca"]
    assert entry["shares_held_into"] == 10.0
    assert entry["pnl_usd"] == pytest.approx(20.0)  # 10 x 2 x 1.00, the 20 shares' payment


def test_s8_late_distribution_on_a_short_is_charged(tmp_path):
    d1, d2, d3, d4 = S[:4]
    bk = _tlt_book(tmp_path, tg={"TLT": -50.0})
    *_, r3 = bk.run_dates([d1, d2, d3])
    assert r3["pnl_by_symbol"]["TLT"]["shares_held_into"] == -50.0
    r4 = bk.run_date(d4, late_actions=[act("TLT", "cash_dividend", d3, 0.30)])
    assert r4["pnl"]["late_ca"] == pytest.approx(-15.0)


def test_s8_reverse_split_through_the_share_update(tmp_path):
    d1, d2, d3 = S[:3]
    rs = ca("QQQ", "reverse_split", d3, ratio=0.25)
    days = {d1: bars(W), d2: bars(d1), d3: {**bars(d2), "QQQ": EtfBar(2000.0, 0.0, d2)}}
    bk = book(tmp_path, SpanSource(days, published={d3: [rs]}), {"QQQ": 100.0})
    *_, r3 = bk.run_dates([d1, d2, d3])
    assert r3["positions_before_fills"]["QQQ"] == pytest.approx(25.0)
    assert r3["pnl_by_symbol"]["QQQ"]["ret"] == pytest.approx(0.0, abs=1e-15)
    assert not any(f.startswith("suspect_split") for f in r3["flags"])


def test_s8_late_reverse_split_repairs_the_recorded_move(tmp_path):
    d1, d2, d3, d4 = S[:4]
    days = {  # a 5:4 reverse split (ratio 0.8): +25%, below the suspect-split threshold
        d1: bars(W),
        d2: bars(d1),
        d3: {**bars(d2), "QQQ": EtfBar(625.0, 0.25, d2)},
        d4: {**bars(d3), "QQQ": EtfBar(625.0, 0.0, d3)},
    }
    bk = book(tmp_path, SpanSource(days), {"QQQ": 100.0})
    *_, r3 = bk.run_dates([d1, d2, d3])
    assert r3["pnl"]["excess"] == pytest.approx(12500.0)
    r4 = bk.run_date(d4, late_actions=[act("QQQ", "reverse_split", d3, 0.8)])
    (entry,) = r4["late_ca"]
    assert entry["extra_shares"] == pytest.approx(-20.0)
    assert entry["pnl_usd"] == pytest.approx(-12500.0)
    assert r4["positions_before_fills"]["QQQ"] == pytest.approx(80.0)


# ------------------------------------------------------------------ S1, S4, N5 ----
def test_s1_shorts_above_the_cap_are_scaled_toward_zero():
    res = strategy_f2.position_steps(
        ["A"], {"A": -300.0}, {"A": 100.0}, {"A": -320.0}, {"A": 100.0}, set(),
        cap_usd=30000.0, buffer_size=0.1, steps=1000,
    )  # fmt: skip
    assert res.buffered["A"] == -310.0
    sc = res.second_check
    assert sc["applied"] and sc["gross_before_usd"] == 31000.0
    assert sc["scaled"] == ["A"] and sc["factor"] == pytest.approx(30000.0 / 31000.0)
    assert res.targets["A"] == -300.0 and res.target_gross_usd == 30000.0


def test_s1_step5_scales_longs_and_shorts_with_carried_fixed():
    syms = ["A", "B", "C", "D"]
    close = {"A": 97.13, "B": 41.07, "C": 100.0, "D": 63.3}
    res = strategy_f2.position_steps(
        syms,
        {"A": 200.0, "B": 300.0, "C": -100.0},
        {"A": 40.0, "B": 60.0, "C": 20.0},
        {"A": 203.9, "B": 305.9, "C": -101.0, "D": 50.0},  # D carried
        close,
        set(),
        cap_usd=45000.0,
        buffer_size=0.1,
        steps=1000,
    )
    sc = res.second_check
    carried = 50.0 * 63.3
    new_gross = 203.9 * 97.13 + 305.9 * 41.07 + 101.0 * 100.0
    assert sc["applied"] and sc["carried_gross_usd"] == pytest.approx(carried)
    assert sc["factor"] == pytest.approx((45000.0 - carried) / new_gross)
    assert sc["scaled"] == ["A", "B", "C"]
    assert res.targets["D"] == 50.0  # carried left as it is
    assert res.targets["C"] == float(math.trunc(-101.0 * sc["factor"]))  # toward zero, whole
    for s, q in (("A", 203.9), ("B", 305.9)):
        assert res.targets[s] == strategy_f2.floor_long(q * sc["factor"], 1000)
    assert res.target_gross_usd <= 45000.0


def test_s4_carried_notional_is_held_fixed_in_step_2():
    syms = ["A", "B", "C", "D"]
    one = {s: 1.0 for s in syms}
    res = strategy_f2.position_steps(
        syms,
        {"A": 12000.0, "B": 12000.0, "C": -6000.0},
        {"A": 0.0, "B": 0.0, "C": 0.0},
        {"A": 12000.0, "B": 12000.0, "C": -6000.0, "D": 25000.0},  # D: no close on t
        one,
        set(),
        cap_usd=50000.0,
        buffer_size=0.1,
        steps=1000,
    )
    assert res.cap_bound and res.carried_gross_usd == 25000.0
    assert res.cap_scale == pytest.approx(25000.0 / 30000.0)
    assert res.targets == {"A": 10000.0, "B": 10000.0, "C": -5000.0, "D": 25000.0}
    assert not res.second_check["applied"]


def test_s1_carried_alone_above_the_cap_zeroes_every_new_target():
    res = strategy_f2.position_steps(
        ["A", "D"], {"A": 100.0}, {"A": 10.0}, {"A": 100.0, "D": 600.0},
        {"A": 10.0, "D": 100.0}, set(), cap_usd=50000.0, buffer_size=0.1, steps=1000,
    )  # fmt: skip
    assert res.cap_scale == 0.0 and res.targets == {"A": 0.0, "D": 600.0}


def test_n5_second_check_not_applied_when_nothing_gets_a_new_target():
    res = strategy_f2.position_steps(
        ["A", "D"], {}, {}, {"A": 0.0, "D": 600.0}, {"D": 100.0}, set(),
        cap_usd=50000.0, buffer_size=0.1, steps=1000,
    )  # fmt: skip
    sc = res.second_check
    assert sc["gross_before_usd"] == 60000.0
    assert sc["applied"] is False and sc["nothing_to_scale"] is True


# ------------------------------------------------------------------ S6 ----
def test_s6_suspect_move_is_no_bar_until_the_split_is_published(tmp_path):
    d1, d2, d3, d4 = S[:4]
    split = ca("QQQ", "forward_split", d3, ratio=4.0)
    days = {
        d1: bars(W),
        d2: bars(d1),
        d3: {**bars(d2), "QQQ": EtfBar(125.0, -0.75, d2)},  # 4:1, unpublished on d3
        d4: {**bars(d3), "QQQ": EtfBar(126.0, 0.008, d3)},
    }
    bk = book(tmp_path, SpanSource(days, published={d4: [split]}), {"QQQ": 100.0})
    *_, r3, r4 = bk.run_dates([d1, d2, d3, d4])
    assert "suspect_split:QQQ" in r3["flags"] and "missing:QQQ" not in r3["flags"]
    assert "QQQ" not in r3["bars"] and r3["source_bars"]["QQQ"]["close"] == 125.0
    assert r3["suspect_split"] == {"QQQ": 1}
    assert r3["positions"]["QQQ"] == 100.0 and r3["pnl_by_symbol"]["QQQ"]["etf_pnl"] == 0.0
    assert r3["fills"] == [] and "QQQ" not in r3["orders"]
    assert not any(f.startswith("suspect_split") for f in r4["flags"])
    assert r4["bars"]["QQQ"]["prev_date"] == d2.isoformat()
    assert r4["pnl_by_symbol"]["QQQ"]["ret"] == pytest.approx(4.0 * 126.0 / 500.0 - 1.0)
    assert r4["positions_before_fills"]["QQQ"] == pytest.approx(400.0)


def test_s6_after_10_suspect_sessions_the_move_is_accepted(tmp_path):
    days = {S[0]: bars(W), S[1]: bars(S[0])}
    for k in range(2, 13):
        days[S[k]] = {**bars(S[k - 1]), "QQQ": EtfBar(125.0, 0.0, S[k - 1])}
    bk = book(tmp_path, SpanSource(days), {"QQQ": 100.0})
    recs = bk.run_dates(S[:13])
    for k in range(2, 12):
        assert recs[k]["suspect_split"] == {"QQQ": k - 1}, k
        assert "QQQ" not in recs[k]["bars"]
    last = recs[12]
    assert "suspect_split_accepted:QQQ" in last["flags"] and not last.get("suspect_split")
    assert last["pnl_by_symbol"]["QQQ"]["ret"] == pytest.approx(-0.75)
    assert last["pnl_by_symbol"]["QQQ"]["etf_pnl"] == pytest.approx(-37500.0)
    assert last["positions_before_fills"]["QQQ"] == 100.0
    assert "QQQ" not in last["dropped"]  # suspect sessions are not missing bars


def test_s6_guard_does_not_apply_to_the_cash_benchmark(tmp_path):
    d1, d2, d3 = S[:3]
    days = {d1: bars(W), d2: bars(d1), d3: bars(d2, BIL=45.75)}
    *_, r3 = book(tmp_path, SpanSource(days), {"QQQ": 10.0}).run_dates([d1, d2, d3])
    assert r3["cash"]["r_c"] == pytest.approx(-0.5) and not r3.get("suspect_split")


# ------------------------------------------------------------------ S7 ----
def test_s7_delisting_after_10_sessions_without_a_bar_missing_days_skipped(tmp_path):
    seen = {}
    days = {S[0]: bars(W), S[1]: bars(S[0]), S[2]: bars(S[1])}
    for k in range(3, 14):
        days[S[k]] = bars(S[k - 1], TLT=None)
    days[S[7]] = {"BIL": EtfBar(91.5, 0.0, S[6])}  # a missing day: no ETF bar
    days[S[14]] = bars(S[13])  # TLT's bar is back
    bk = book(tmp_path, SpanSource(days), {"TLT": 100.0}, seen)
    recs = bk.run_dates(S[:15])
    assert recs[7]["missing_day"]
    assert recs[12]["positions"]["TLT"] == 100.0 and "delisted:TLT" not in recs[12]["flags"]
    r = recs[13]  # TLT's 10th session without a bar that is not a missing day
    assert "delisted:TLT" in r["flags"] and "TLT" in r["dropped"]
    (leg,) = [f for f in r["fills"] if f["symbol"] == "TLT"]
    assert leg["leg"] == "delist" and leg["shares"] == -100.0 and leg["price"] == 90.0
    assert r["costs"]["sec_fee"] == pytest.approx(0.19)  # 0.0000206 x 9,000 rounded up
    assert r["positions"]["TLT"] == 0.0
    back = recs[14]
    assert "TLT" in back["dropped"] and "TLT" not in back["bars"]
    assert back["targets"]["TLT"] == 0.0 and "TLT" not in back["orders"]
    assert S[14] not in seen[S[14]]["TLT"]  # the rule never sees the dropped ETF again


def test_s7_bil_replaced_by_sgov_after_10_sessions(tmp_path):
    days = {S[0]: {**bars(W), "SGOV": EtfBar(100.0, 0.0, W)}}
    for k in range(1, 13):
        sg = 100.0 + 0.01 * k
        days[S[k]] = {**bars(S[k - 1], BIL=None), "SGOV": EtfBar(sg, 0.0, S[k - 1])}
    days[S[12]]["BIL"] = EtfBar(91.6, 0.0, S[0])  # BIL back after the switch
    bk = book(tmp_path, SpanSource(days), {"QQQ": 10.0})
    recs = bk.run_dates(S[:12])
    sgov_div = act("SGOV", "cash_dividend", S[11], 0.1)  # late: the cash branch now holds SGOV
    recs.append(bk.run_date(S[12], late_actions=[sgov_div]))
    (entry,) = recs[12]["late_ca"]
    assert entry["long_notional_ex_usd"] == 5000.0
    assert entry["dr_c"] == pytest.approx(0.1 / 100.10)
    assert entry["pnl_usd"] == pytest.approx(-5000.0 * 0.1 / 100.10)
    assert recs[9]["cash"] == {"symbol": "BIL", "r_c": None}
    assert "SGOV" in recs[9]["bars"]
    r = recs[10]  # BIL's 10th session without a bar
    assert "cash_benchmark:SGOV" in r["flags"] and r["cash"]["symbol"] == "SGOV"
    assert r["cash"]["r_c"] == pytest.approx(100.10 / 100.09 - 1.0)
    assert recs[12]["cash"]["symbol"] == "SGOV"
    assert recs[12]["cash"]["r_c"] == pytest.approx(100.12 / 100.11 - 1.0)


def test_s7_read_universe_includes_the_replacement_benchmark():
    assert CFG.read_universe == (*CFG.universe, "SGOV")
    assert "SGOV" not in CFG.universe


# ------------------------------------------------------------------ N7 ----
def test_n7_horizon_is_imported_from_forward_evaluate():
    src = inspect.getsource(evaluate_f2)
    assert "HORIZON_MONTHS = 36" not in src and "HORIZON_MONTHS," in src


def test_s7_daily_source_reads_the_replacement_benchmark_every_session():
    from forward import daily_f2

    names = daily_f2.credential_names()
    env = {names[0]: "fake-id", names[1]: "fake-secret"}
    src = daily_f2.make_source(CFG, csv_path=None, environ=env, data_client_factory=object)
    assert set(src.symbols) == set(CFG.read_universe)
