"""Lead rulings Q21 and Q23 of 2026-10-18 (prereg section 6, late corporate-action bullet as
revised at 11:20 PDT): each record stores the actions counted in its r with type, ex_date and
amount or ratio; a session's corrected return applies k x (rawclose(t) + D) / rawclose(prev) - 1
to ALL its actions (recorded and late); a late BIL action of either kind books -L_ex x dr_c with
dr_c = corrected minus recorded BIL return of that session."""

from datetime import date
from types import SimpleNamespace

import pytest

from forward.etf_bars import EtfBar, EtfDayRow, InMemoryEtfSource
from forward.runner_f2 import PaperBookF2, RunnerError, load_book_config
from forward.sources_alpaca import CorporateAction

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


def day(prev, qqq=(500.0, 0.0), bil=(91.5, 0.0)):
    return {
        "QQQ": EtfBar(qqq[0], qqq[1], prev),
        "TLT": EtfBar(90.0, 0.0, prev),
        "BIL": EtfBar(bil[0], bil[1], prev),
    }


class FetchSource:
    """A source with fetch_day and corporate_actions, as forward.sources_alpaca: DayFetch.applied
    holds the CorporateAction objects counted inside each symbol's r."""

    def __init__(self, days, applied=None):
        self.inner = InMemoryEtfSource(days)
        self.applied = applied or {}

    def bars(self, t):
        return self.inner.bars(t)

    def fetch_day(self, t):
        return SimpleNamespace(
            answer=lambda: self.inner.bars(t), applied=self.applied.get(t, {}), flags={}
        )

    def corporate_actions(self, start, end, symbols=None):
        """Every action published at record time (wave 3, B1: the runner queries the span
        (prev, t] and filters by ex_date)."""
        acts = tuple(a for day in self.applied.values() for acts in day.values() for a in acts)
        return SimpleNamespace(booked=acts, other=())


def recorder(tg, seen):
    """Fixed targets; stores each decision's view of the returns {symbol: {session: r}}."""

    def fn(history, held, config, *, decision_date):
        seen[decision_date] = {
            s: {row.date: row.bars[s].ret for row in history if s in row.bars}
            for s in ("QQQ", "BIL")
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


SPLIT_QQQ = ca("QQQ", "forward_split", D3, ratio=2.0)
R_SPLIT = 2.0 * 251.0 / 500.0 - 1.0  # QQQ's D3 r with the split counted when recorded


# ------------------------------------------------------------------ Q23 ----
def test_q23_ca_applied_stores_each_action_with_type_ex_date_and_amount(tmp_path):
    src = FetchSource(
        {D1: day(W), D2: day(D1), D3: day(D2, qqq=(251.0, R_SPLIT))},
        applied={
            D3: {
                "QQQ": (SPLIT_QQQ,),
                # a regular and a special dividend on one ex_date: both counted, both stored
                "TLT": (
                    ca("TLT", "cash_dividend", D3, amount=0.25),
                    ca("TLT", "cash_dividend", D3, amount=0.10),
                ),
            }
        },
    )
    *_, r3 = book(tmp_path, src, {"QQQ": 10.0}).run_dates([D1, D2, D3])
    assert r3["ca_applied"] == {
        "QQQ": [act("QQQ", "forward_split", D3, 2.0)],
        "TLT": [act("TLT", "cash_dividend", D3, 0.10), act("TLT", "cash_dividend", D3, 0.25)],
    }


def test_q23_applied_action_without_its_number_is_refused(tmp_path):
    bad = ca("QQQ", "forward_split", D3)  # neither ratio nor amount
    src = FetchSource(
        {D1: day(W), D2: day(D1), D3: day(D2, qqq=(251.0, R_SPLIT))},
        applied={D3: {"QQQ": (bad,)}},
    )
    bk = book(tmp_path, src, {})
    bk.run_dates([D1, D2])
    with pytest.raises(RunnerError, match="amount_or_ratio"):
        bk.run_date(D3)
    assert len(bk.ledger.records()) == 2  # nothing written for D3


def test_q23_late_distribution_on_a_session_whose_recorded_r_contained_a_split(tmp_path):
    seen = {}
    src = FetchSource(
        {D1: day(W), D2: day(D1), D3: day(D2, qqq=(251.0, R_SPLIT)), D4: day(D3, qqq=(251.0, 0.0))},
        applied={D3: {"QQQ": (SPLIT_QQQ,)}},
    )
    bk = book(tmp_path, src, {"QQQ": 10.0}, seen)
    *_, r3 = bk.run_dates([D1, D2, D3])
    r4 = bk.run_date(D4, late_actions=[act("QQQ", "cash_dividend", D3, 1.0)])
    (entry,) = r4["late_ca"]
    assert entry["booked"] and entry["session"] == "2026-11-09"
    # section 6 on ALL the session's actions: k = 2 (recorded), D = 1.00 (late, per new share)
    assert seen[D4]["QQQ"][D3] == pytest.approx(2.0 * (251.0 + 1.0) / 500.0 - 1.0, abs=1e-15)
    assert seen[D3]["QQQ"][D3] == pytest.approx(R_SPLIT, abs=1e-15)  # as recorded
    assert r3 == bk.ledger.records()[2]  # the recorded day is unchanged


# ------------------------------------------------------------------ Q21 ----
BIL_SPLIT_DAYS = {
    D1: day(W),
    D2: day(D1),
    D3: day(D2, bil=(45.75, -0.5)),  # BIL split 2:1 on D3, not yet published: r_c = -50%
    D4: day(D3, bil=(45.75, 0.0)),
    D5: day(D4, bil=(45.75, 0.0)),
}


def test_q21_late_bil_split_books_minus_l_ex_times_dr_c(tmp_path):
    seen = {}
    bk = book(tmp_path, FetchSource(BIL_SPLIT_DAYS), {"QQQ": 100.0}, seen)
    *_, r3 = bk.run_dates([D1, D2, D3])
    assert r3["exposure"]["long_notional_held_into_usd"] == 50000.0
    assert r3["pnl"]["excess"] == pytest.approx(25000.0)  # the false cash-term gain
    r4 = bk.run_date(D4, late_actions=[act("BIL", "forward_split", D3, 2.0)])
    (entry,) = r4["late_ca"]
    assert entry["booked"] and entry["session"] == "2026-11-09"
    assert entry["long_notional_ex_usd"] == 50000.0
    assert entry["dr_c"] == pytest.approx(0.5, abs=1e-15)  # 2 x 45.75 / 91.5 - 1 - (-0.5)
    assert entry["extra_shares"] == 0.0  # BIL is the cash proxy: no shares
    assert entry["pnl_usd"] == pytest.approx(-25000.0)
    assert r4["pnl"]["late_ca"] == pytest.approx(-25000.0)
    assert r3["pnl"]["excess"] + r4["pnl"]["late_ca"] == pytest.approx(0.0, abs=1e-9)
    assert "late_ca:BIL" in r4["flags"]
    assert seen[D4]["BIL"][D3] == pytest.approx(0.0, abs=1e-15)  # the rule sees the corrected r
    assert r3 == bk.ledger.records()[2]


@pytest.mark.parametrize("same_batch", [False, True])
def test_q21_each_late_bil_action_books_only_its_increment(tmp_path, same_batch):
    split = act("BIL", "forward_split", D3, 2.0)
    dist = act("BIL", "cash_dividend", D3, 0.10)  # per share after the split
    bk = book(tmp_path, FetchSource(BIL_SPLIT_DAYS), {"QQQ": 100.0})
    bk.run_dates([D1, D2, D3])
    if same_batch:
        r4 = bk.run_date(D4, late_actions=[split, dist])
        entries = r4["late_ca"]
    else:
        r4 = bk.run_date(D4, late_actions=[split])
        r5 = bk.run_date(D5, late_actions=[dist])
        entries = r4["late_ca"] + r5["late_ca"]
        (e5,) = r5["late_ca"]
        assert e5["dr_c"] == pytest.approx(2.0 * 0.10 / 91.5, abs=1e-15)  # increment only
    corrected = 2.0 * (45.75 + 0.10) / 91.5 - 1.0
    assert sum(e["dr_c"] for e in entries) == pytest.approx(corrected - (-0.5), abs=1e-15)
    assert sum(e["pnl_usd"] for e in entries) == pytest.approx(-50000.0 * (corrected + 0.5))


def test_q21_late_bil_distribution_with_a_recorded_bil_split_uses_k(tmp_path):
    bil_split = ca("BIL", "forward_split", D3, ratio=2.0)
    days = {**BIL_SPLIT_DAYS, D3: day(D2, bil=(45.75, 0.0))}  # the split counted in r_c
    bk = book(tmp_path, FetchSource(days, applied={D3: {"BIL": (bil_split,)}}), {"QQQ": 100.0})
    bk.run_dates([D1, D2, D3])
    r4 = bk.run_date(D4, late_actions=[act("BIL", "cash_dividend", D3, 0.10)])
    (entry,) = r4["late_ca"]
    assert entry["dr_c"] == pytest.approx(2.0 * (45.75 + 0.10) / 91.5 - 1.0, abs=1e-15)
    assert entry["pnl_usd"] == pytest.approx(-50000.0 * 2.0 * 0.10 / 91.5)
