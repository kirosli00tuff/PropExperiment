"""E22-F2 end to end on synthetic bars: the frozen rule inside the runner, warm-up to live, the
look on a runner-made ledger, and the daily driver's CLI."""

import json
from datetime import date, timedelta
from types import SimpleNamespace

import numpy as np
import pytest

from forward import daily_f2, strategy_f2
from forward.etf_bars import (
    EtfBar,
    EtfDayRow,
    InMemoryEtfSource,
    SourceUnavailable,
    dump_etf_warmup,
    etf_history_sha256,
)
from forward.evaluate_f2 import look
from forward.runner_f2 import PaperBookF2, load_book_config

CFG = load_book_config()
SYMS = list(CFG.universe)


def sessions(start, n):
    out, d = [], start
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d)
        d += timedelta(days=1)
    return out


def series(n_warm=255, n_live=4, seed=3):
    """Warm-up rows (n_warm closes per symbol) and n_live live days, synthetic random walks."""
    rng = np.random.RandomState(seed)
    days = sessions(date(2025, 11, 3), n_warm + n_live)
    price = {s: 30.0 + 7 * k for k, s in enumerate(SYMS)}
    rows, prev = [], None
    for d in days:
        bars = {}
        for j, s in enumerate(SYMS):
            if prev is None:
                bars[s] = EtfBar(price[s])
                continue
            r = 0.0008 * (j % 3 - 1) + 0.012 * rng.standard_normal()
            price[s] = round(price[s] * (1 + r), 2)
            bars[s] = EtfBar(price[s], r, prev)
        rows.append(EtfDayRow(d, bars))
        prev = d
    return tuple(rows[:n_warm]), rows[n_warm:]


def test_rule_in_runner_goes_live_after_256_differences_and_fills(tmp_path):
    warm, live = series()
    src = InMemoryEtfSource({r.date: dict(r.bars) for r in live})
    bk = PaperBookF2(tmp_path / "f2.jsonl", src, CFG, warmup=warm)
    r1, r2, r3, r4 = bk.run_dates([r.date for r in live])
    assert r1["exposure"]["n_live"] == 0 and all(v == 0.0 for v in r1["targets"].values())
    assert r2["exposure"]["n_live"] == 11
    assert r2["exposure"]["idm"] == pytest.approx(2.3293791420997985, rel=1e-15)
    direct = strategy_f2.decide(
        (*warm, *live[:2]), r2["positions"], CFG.config, decision_date=live[1].date
    )
    assert r2["targets"] == direct.targets
    assert r2["exposure"]["target_gross_usd"] <= 50000.0 + 11 * 0.0005 * 100
    for s, q in r2["orders"].items():
        assert q == r2["targets"][s]
        assert q == strategy_f2.granular(q, 1000)
        if q < 0:
            assert q == int(q)
    filled = {f["symbol"]: f["shares"] for f in r3["fills"]}
    assert filled == r2["orders"]
    for s in r2["orders"]:
        assert r3["positions"][s] == r2["targets"][s]
    assert r3["costs"]["total"] > 0 and r3["net_pnl"] == pytest.approx(sum(r3["pnl"].values()))
    out = look([r1, r2, r3, r4], 1)
    assert out["traded_notional_usd"] == pytest.approx(
        sum(f["notional_usd"] for r in (r3, r4) for f in r["fills"])
    )
    assert out["costs_usd"] == pytest.approx(r3["costs"]["total"] + r4["costs"]["total"])
    assert out["days_cap_bound"] == sum(1 for r in (r2, r3, r4) if r["exposure"]["cap_bound"])


def _write_inputs(tmp_path):
    warm = (EtfDayRow(date(2026, 11, 4), {s: EtfBar(50.0) for s in SYMS}),)
    wpath = tmp_path / "warm.jsonl"
    dump_etf_warmup(warm, wpath)
    csv = tmp_path / "bars.csv"
    lines = ["trade_date,symbol,close,ret,prev_date"]
    lines += [f"2026-11-05,{s},50.5,0.01,2026-11-04" for s in SYMS]
    csv.write_text("\n".join(lines) + "\n")
    return wpath, csv


def _no_credentials(monkeypatch):
    for name in daily_f2.credential_names():
        monkeypatch.delenv(name, raising=False)


def test_cli_run_with_csv_writes_one_record(tmp_path, monkeypatch, capsys):
    _no_credentials(monkeypatch)
    wpath, csv = _write_inputs(tmp_path)
    ledger = tmp_path / "f2.jsonl"
    rc = daily_f2.main(
        [
            "run",
            "--date",
            "2026-11-05",
            "--ledger",
            str(ledger),
            "--warmup",
            str(wpath),
            "--csv",
            str(csv),
        ]
    )
    assert rc == 0 and "2026-11-05 net_pnl=0.00" in capsys.readouterr().out
    rec = json.loads(ledger.read_text().splitlines()[0])
    assert rec["warmup_sha256"] == etf_history_sha256(
        (EtfDayRow(date(2026, 11, 4), {s: EtfBar(50.0) for s in SYMS}),)
    )
    assert rc == daily_f2.main(
        [
            "run",
            "--date",
            "2026-11-05",
            "--ledger",
            str(ledger),
            "--warmup",
            str(wpath),
            "--csv",
            str(csv),
        ]
    )  # a re-run returns the stored record
    assert len(ledger.read_text().splitlines()) == 1


def test_cli_source_unavailable_writes_nothing(tmp_path, monkeypatch):
    _no_credentials(monkeypatch)
    wpath, _ = _write_inputs(tmp_path)
    src = InMemoryEtfSource({date(2026, 11, 5): SourceUnavailable("HTTP 429")})
    monkeypatch.setattr(daily_f2, "make_source", lambda cfg, **kw: src)
    ledger = tmp_path / "f2.jsonl"
    rc = daily_f2.main(
        ["run", "--date", "2026-11-05", "--ledger", str(ledger), "--warmup", str(wpath)]
    )
    assert rc == daily_f2.EXIT_SOURCE_UNAVAILABLE and not ledger.exists()


def test_cli_warmup_writes_file_and_sha256(tmp_path, monkeypatch, capsys):
    from forward import sources_alpaca

    names = daily_f2.credential_names()
    monkeypatch.setenv(names[0], "fake-id")
    monkeypatch.setenv(names[1], "fake-secret")
    rows = (EtfDayRow(date(2026, 11, 4), {s: EtfBar(50.0) for s in SYMS}),)

    class FakeSource:
        def __init__(self, symbols, client, **kw):
            self.symbols = tuple(symbols)

        def fetch_warmup(self, start):
            return sources_alpaca.WarmupResult(
                rows,
                etf_history_sha256(rows),
                {s: date(2026, 11, 4) for s in SYMS},
                {s: 1 for s in SYMS},
                {},
            )

    monkeypatch.setattr(sources_alpaca, "make_data_client", lambda: object())
    monkeypatch.setattr(sources_alpaca, "AlpacaEtfSource", FakeSource)
    out = tmp_path / "warm.jsonl"
    assert daily_f2.main(["warmup", "--start", "2026-11-05", "--out", str(out)]) == 0
    sha = etf_history_sha256(rows)
    assert (tmp_path / "warm.jsonl.sha256").read_text() == f"{sha}  warm.jsonl\n"
    assert sha in capsys.readouterr().out
    with pytest.raises(FileExistsError):
        daily_f2.main(["warmup", "--start", "2026-11-05", "--out", str(out)])


def test_late_actions_from_the_source_endpoint(tmp_path):
    d1 = date(2026, 11, 5)
    warm = (EtfDayRow(date(2026, 11, 4), {s: EtfBar(50.0) for s in SYMS}),)

    class Src(InMemoryEtfSource):
        def corporate_actions(self, start, end):
            self.asked = (start, end)
            ca = SimpleNamespace(
                symbol="TLT", kind="cash_dividend", ex_date=d1, ratio=None, amount=0.2
            )
            sp = SimpleNamespace(
                symbol="QQQ", kind="forward_split", ex_date=d1, ratio=2.0, amount=None
            )
            other = SimpleNamespace(
                symbol="GLD", kind="spin_off", ex_date=None, ratio=None, amount=None
            )
            return SimpleNamespace(booked=(ca, sp), other=(other,))

    src = Src({d1: {s: EtfBar(50.0, 0.0, date(2026, 11, 4)) for s in SYMS}})
    bk = PaperBookF2(tmp_path / "f2.jsonl", src, CFG, warmup=warm)
    assert daily_f2.late_actions_for(bk, d1) == []  # no records yet
    bk.run_date(d1)
    assert daily_f2.late_actions_for(bk, d1) is None  # recorded: a re-run reuses the stored input
    got = daily_f2.late_actions_for(
        bk,
        date(2026, 11, 6),
        [
            {
                "symbol": "IEF",
                "type": "cash_dividend",
                "ex_date": "2026-11-05",
                "amount_or_ratio": 0.1,
            }
        ],
    )
    assert {(a["symbol"], a["type"], a["amount_or_ratio"]) for a in got} == {
        ("IEF", "cash_dividend", 0.1),
        ("TLT", "cash_dividend", 0.2),
        ("QQQ", "forward_split", 2.0),
    }
    assert src.asked == (d1 - timedelta(days=daily_f2.LATE_CA_LOOKBACK_DAYS), d1)
