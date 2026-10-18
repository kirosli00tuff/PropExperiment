"""E22-F2 late corporate actions (prereg sections 5 and 6): booked once, never twice, never when
already inside a recorded return; other types flagged."""

from datetime import date
from types import SimpleNamespace

import pytest

from forward.etf_bars import EtfBar, EtfDayRow, InMemoryEtfSource
from forward.runner_f2 import PaperBookF2, load_book_config

CFG = load_book_config()
ETFS = CFG.symbols
W = date(2026, 11, 4)
D1, D2, D3, D4, D5 = (
    date(2026, 11, 5),
    date(2026, 11, 6),
    date(2026, 11, 9),
    date(2026, 11, 10),
    date(2026, 11, 11),
)
WARMUP = (EtfDayRow(W, {"QQQ": EtfBar(500.0), "TLT": EtfBar(90.0), "BIL": EtfBar(91.5)}),)


def day(prev, qqq=(500.0, 0.0), tlt=(90.0, 0.0)):
    return {
        "QQQ": EtfBar(qqq[0], qqq[1], prev),
        "TLT": EtfBar(tlt[0], tlt[1], prev),
        "BIL": EtfBar(91.5, 0.0, prev),
    }


def data(over=None):
    out = {D1: day(W), D2: day(D1), D3: day(D2), D4: day(D3), D5: day(D4)}
    out.update(over or {})
    return out


def fixed(tg):
    def fn(history, held, config, *, decision_date):
        return {s: float(tg.get(s, 0.0)) for s in ETFS}

    return fn


def book(tmp_path, src, tg):
    return PaperBookF2(tmp_path / "f2.jsonl", src, CFG, warmup=WARMUP, target_fn=fixed(tg))


def act(symbol, kind, ex, v):
    return {"symbol": symbol, "type": kind, "ex_date": ex.isoformat(), "amount_or_ratio": v}


DIV = act("TLT", "cash_dividend", D3, 0.30)


def test_late_dividend_booked_as_cash_on_shares_held_into_ex_session(tmp_path):
    bk = book(tmp_path, InMemoryEtfSource(data()), {"TLT": 100.0})
    bk.run_dates([D1, D2, D3])
    rec = bk.run_date(D4, late_actions=[DIV])
    assert rec["pnl"]["late_ca"] == pytest.approx(30.0)
    assert rec["late_ca"][0]["pnl_usd"] == pytest.approx(30.0)
    assert "late_ca:TLT" in rec["flags"]
    (entry,) = rec["late_ca"]
    assert entry["session"] == "2026-11-09" and entry["shares_held_into"] == 100.0
    assert rec["net_pnl"] == pytest.approx(sum(rec["pnl"].values()))


def test_late_split_adds_shares_books_their_value_and_corrects_the_series(tmp_path):
    src = InMemoryEtfSource(
        data({D3: day(D2, qqq=(251.0, 251.0 / 500.0 - 1)), D4: day(D3, qqq=(251.0, 0.0))})
    )
    seen = {}

    def fn(history, held, config, *, decision_date):
        seen[decision_date] = {r.date: r.bars["QQQ"].ret for r in history if "QQQ" in r.bars}
        return {s: (10.0 if s == "QQQ" else 0.0) for s in ETFS}

    bk = PaperBookF2(tmp_path / "f2.jsonl", src, CFG, warmup=WARMUP, target_fn=fn)
    r1, r2, r3 = bk.run_dates([D1, D2, D3])
    assert r3["pnl"]["excess"] == pytest.approx(5000 * (251.0 / 500.0 - 1))  # the false ex-day loss
    rec = bk.run_date(D4, late_actions=[act("QQQ", "forward_split", D3, 2.0)])
    (entry,) = rec["late_ca"]
    assert entry["extra_shares"] == 10.0 and entry["booked"] and entry["value_price"] == 251.0
    assert entry["pnl_usd"] == pytest.approx(2510.0)
    assert rec["pnl"]["late_ca"] == pytest.approx(2510.0)  # the value of the added shares
    assert r3["pnl"]["excess"] + rec["pnl"]["late_ca"] == pytest.approx(5000 * 0.004)
    assert rec["positions_before_fills"]["QQQ"] == 20.0
    assert rec["pnl_by_symbol"]["QQQ"]["shares_held_into"] == 20.0
    assert rec["positions"]["QQQ"] == 20.0
    # the rule's series: the ex-session return corrected with k on D4, recorded day unchanged
    assert seen[D3][D3] == pytest.approx(251.0 / 500.0 - 1)
    assert seen[D4][D3] == pytest.approx(2 * 251.0 / 500.0 - 1)
    assert r3 == bk.ledger.records()[2]


def test_duplicate_not_booked_twice_and_rerun_reuses_stored_input(tmp_path):
    bk = book(tmp_path, InMemoryEtfSource(data()), {"TLT": 100.0})
    bk.run_dates([D1, D2, D3])
    r4 = bk.run_date(D4, late_actions=[DIV])
    r5 = bk.run_date(D5, late_actions=[DIV])
    assert r5["late_ca"] == [] and r5["pnl"]["late_ca"] == 0.0
    assert r5["late_ca_skipped"]["already_handled"] == 1
    assert not any(f.startswith("late_ca") for f in r5["flags"])
    assert bk.run_date(D4) == r4  # None: the stored input is reused


def test_unknown_type_of_held_etf_flagged_not_booked(tmp_path):
    bk = book(tmp_path, InMemoryEtfSource(data()), {"TLT": 100.0})
    bk.run_dates([D1, D2, D3])
    spin = act("TLT", "spin_off", D3, 0.0)
    r4 = bk.run_date(D4, late_actions=[spin, act("QQQ", "spin_off", D3, 0.0)])
    assert "late_ca_unbooked:TLT:spin_off" in r4["flags"]
    assert r4["pnl"]["late_ca"] == 0.0 and r4["late_ca"][0]["booked"] is False
    assert r4["late_ca_skipped"]["not_held"] == 1  # QQQ not held: no flag
    r5 = bk.run_date(D5, late_actions=[spin])
    assert (
        r5["late_ca_skipped"]["already_handled"] == 1
        and "late_ca_unbooked:TLT:spin_off" not in r5["flags"]
    )


def test_action_outside_recorded_sessions_is_skipped(tmp_path):
    bk = book(tmp_path, InMemoryEtfSource(data()), {"TLT": 100.0})
    bk.run_dates([D1, D2, D3])
    r4 = bk.run_date(
        D4, late_actions=[act("TLT", "cash_dividend", W, 0.3), act("TLT", "cash_dividend", D5, 0.3)]
    )
    assert r4["late_ca"] == [] and r4["late_ca_skipped"]["not_in_a_recorded_session"] == 2


def test_missing_day_defers_late_action(tmp_path):
    src = InMemoryEtfSource({k: v for k, v in data().items() if k != D4})
    bk = book(tmp_path, src, {"TLT": 100.0})
    bk.run_dates([D1, D2, D3])
    r4 = bk.run_date(D4, late_actions=[DIV])
    assert r4["missing_day"] and r4["net_pnl"] == 0.0 and "late_ca_deferred:TLT" in r4["flags"]
    r5 = bk.run_date(D5, late_actions=[DIV])
    assert r5["pnl"]["late_ca"] == pytest.approx(30.0)


def test_same_symbol_type_ex_date_with_different_amounts_are_two_actions(tmp_path):
    # wave 3, B2 (was: refused as conflicting): the key carries the amount
    bk = book(tmp_path, InMemoryEtfSource(data()), {"TLT": 100.0})
    bk.run_dates([D1, D2, D3])
    r4 = bk.run_date(D4, late_actions=[DIV, {**DIV, "amount_or_ratio": 0.31}, DIV])
    assert sorted(e["amount_or_ratio"] for e in r4["late_ca"]) == [0.30, 0.31]


class FetchSource:
    """A source with fetch_day (as forward.sources_alpaca): applied actions and other-type notes."""

    def __init__(self, days, applied=None, flags=None):
        self.inner = InMemoryEtfSource(days)
        self.applied, self.flags = applied or {}, flags or {}

    def bars(self, t):
        return self.inner.bars(t)

    def fetch_day(self, t):
        return SimpleNamespace(
            answer=lambda: self.inner.bars(t),
            applied=self.applied.get(t, {}),
            flags=self.flags.get(t, {}),
        )

    def corporate_actions(self, start, end, symbols=None):
        """The applied actions over any span (wave 3, B1: the runner filters by ex_date)."""
        acts = tuple(a for day in self.applied.values() for acts in day.values() for a in acts)
        return SimpleNamespace(booked=acts, other=())


def test_action_inside_a_recorded_return_is_not_booked_again(tmp_path):
    split = SimpleNamespace(symbol="QQQ", kind="forward_split", ex_date=D3, ratio=2.0, amount=None)
    src = FetchSource(
        data({D3: day(D2, qqq=(251.0, 0.004))}),
        applied={D3: {"QQQ": (split,)}},
        flags={D4: {"TLT": ("spin_off ex_date 2026-11-10",)}},
    )
    bk = book(tmp_path, src, {"QQQ": 10.0, "TLT": 100.0})
    r = bk.run_dates([D1, D2, D3])
    assert r[-1]["ca_applied"] == {"QQQ": [act("QQQ", "forward_split", D3, 2.0)]}  # Q23
    assert r[-1]["positions_before_fills"]["QQQ"] == pytest.approx(20.0)
    r4 = bk.run_date(D4, late_actions=[act("QQQ", "forward_split", D3, 2.0)])
    assert r4["late_ca"] == [] and r4["late_ca_skipped"]["inside_recorded_return"] == 1
    assert "ca_other:TLT" in r4["flags"] and r4["ca_other"] == {
        "TLT": ["spin_off ex_date 2026-11-10"]
    }
