"""forward.daily_f1 with the mock gateway (Stage E.24): exit codes, CSV mirror equivalence with the
frozen runner CLI, env-var hygiene, lazy ib_async. No network."""

from __future__ import annotations

import subprocess
import sys
from datetime import date

import pytest

from forward import daily_f1 as D
from forward import runner as frozen_runner
from forward.ibkr_gateway import ConnectionParams, RetryPolicy
from tests._forward_ibkr_mock import (
    ENV,
    FAKE_VENDOR,
    PAPER,
    MockGateway,
    build_bars,
    build_listings,
    ct,
)

FIRST, LAST = date(2026, 10, 1), date(2026, 12, 31)


def deps(gw, out):
    return D.Deps(
        environ=dict(ENV),
        gateway_factory=lambda: gw,
        vendor_factory=lambda: FAKE_VENDOR,
        now=lambda: gw.now,
        sleep=lambda s: None,
        clock=lambda: 0.0,
        policy=RetryPolicy(backoff_base_s=0),
        pacing_s=0.0,
        out=out.append,
    )


def mock(now, holes=frozenset()):
    listings = build_listings(FIRST, LAST)
    return MockGateway(listings, build_bars(listings, FIRST, LAST, holes=holes), now=now)


def test_run_writes_records_and_the_csv_mirror_replays_byte_identically(tmp_path):
    gw, out = mock(ct(2026, 11, 6, 19)), []
    days = ["2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05", "2026-11-06"]
    for d in days:
        rc = D.main(
            [
                "run",
                "--no-warmup",
                "--ledger",
                str(tmp_path / "ibkr.jsonl"),
                "--date",
                d,
                "--csv-mirror",
                str(tmp_path / "s.csv"),
                "--provenance",
                str(tmp_path / "prov.jsonl"),
            ],
            deps(gw, out),
        )
        assert rc == 0, out
    for d in days:  # the frozen runner CLI, unchanged, on the IBKR-sourced CSV
        assert (
            frozen_runner._main(
                [
                    "--ledger",
                    str(tmp_path / "csv.jsonl"),
                    "--csv",
                    str(tmp_path / "s.csv"),
                    "--tables",
                    "forward/tables_f1.json",
                    "--config",
                    "forward/config_f1.json",
                    "--date",
                    d,
                ]
            )
            == 0
        )
    assert (tmp_path / "ibkr.jsonl").read_bytes() == (tmp_path / "csv.jsonl").read_bytes()
    assert not any(v in line for line in out for v in ENV.values())
    assert gw.calls[0] == ("connect", {"readonly": True, "timeout": 10.0})


def test_not_ready_and_unavailable_exit_2_without_a_record(tmp_path):
    gw, out = mock(ct(2026, 11, 2, 17, 0)), []
    assert (
        D.main(
            ["run", "--no-warmup", "--ledger", str(tmp_path / "l.jsonl"), "--date", "2026-11-02"],
            deps(gw, out),
        )
        == 2
    )
    assert "DayNotReady" in out[-1] and not (tmp_path / "l.jsonl").exists()


def test_a_whole_missing_day_needs_the_explicit_flag(tmp_path):
    day = date(2026, 11, 26)
    listings = build_listings(FIRST, LAST)
    gw, out = mock(ct(2026, 11, 27, 19), holes={(cid, day) for (_, cid) in listings}), []
    args = ["run", "--no-warmup", "--ledger", str(tmp_path / "l.jsonl"), "--date", "2026-11-26"]
    assert D.main(args, deps(gw, out)) == 3 and not (tmp_path / "l.jsonl").exists()
    assert D.main([*args, "--accept-missing-day"], deps(gw, out)) == 0
    assert '"missing_day":true' in (tmp_path / "l.jsonl").read_text()


def test_env_status_prints_names_never_values():
    out: list[str] = []
    env = dict(ENV)
    env.pop("IBKR_ACCOUNT_ID")
    d = D.Deps(environ=env, out=out.append)
    assert D.main(["env-status"], d) == 0
    assert out == [
        "IBKR_GATEWAY_HOST: set",
        "IBKR_GATEWAY_PORT: set",
        "IBKR_CLIENT_ID: set",
        "IBKR_ACCOUNT_ID: unset",
    ]
    p = ConnectionParams.from_env(ENV, need_account=True)
    assert PAPER not in repr(p) and "4002" not in str(p)


def test_ready_uses_chicago_trade_dates():
    out: list[str] = []
    assert D.main(["ready", "--now", "2026-11-03T06:30:00+00:00"], D.Deps(out=out.append)) == 0
    assert out == ["2026-11-02"]


def test_modules_import_and_run_without_ib_async():
    code = (
        "import sys; sys.modules['ib_async'] = None\n"
        "import forward.daily_f1, forward.orders_ibkr, forward.sources_ibkr\n"
        "from forward.ibkr_gateway import live_vendor, IBKRConfigError\n"
        "try:\n    live_vendor()\nexcept IBKRConfigError as e:\n    print('lazy-ok')\n"
    )
    res = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
    assert res.stdout.strip() == "lazy-ok"


def _warmup_and_mock(tmp_path):
    import json

    listings = build_listings(date(2024, 3, 1), LAST)
    gw = MockGateway(
        listings, build_bars(listings, date(2024, 3, 1), LAST), now=ct(2026, 11, 1, 12)
    )
    out: list[str] = []
    wu = tmp_path / "warmup.jsonl"
    assert (
        D.main(
            [
                "warmup",
                "--start",
                "2026-11-02",
                "--out",
                str(wu),
                "--csv",
                str(tmp_path / "warmup.csv"),
            ],
            deps(gw, out),
        )
        == 0
    ), out
    summary = json.loads((tmp_path / "warmup.jsonl.summary.json").read_text())
    assert summary["last"] == "2026-10-30" and summary["first"] == "2024-03-01"
    assert all(s["rows"] > 256 and s["live_at_start"] for s in summary["instruments"].values())
    assert len(summary["history_fingerprint"]) == 64
    assert any(line.startswith("  MNG: rows=") for line in out)
    return listings, wu


def _shadow_cfg(tmp_path, **kw):
    import json

    cfg = {
        "enabled": True,
        "order_type": "MKT",
        "fill_wait_s": 0,
        "poll_s": 1,
        "shadow_ledger": str(tmp_path / "shadow.jsonl"),
        **kw,
    }
    path = tmp_path / "shadow_on.json"
    path.write_text(json.dumps(cfg))
    return path


def test_warmup_then_the_frozen_strategy_with_the_shadow_route_on_and_off(tmp_path):
    listings, wu = _warmup_and_mock(tmp_path)
    days = ["2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05", "2026-11-06"]
    ledgers = {}
    for mode in ("off", "on"):
        gw = MockGateway(
            listings, build_bars(listings, date(2024, 3, 1), LAST), now=ct(2026, 11, 6, 19)
        )
        out: list[str] = []
        ledger = tmp_path / f"{mode}.jsonl"
        extra = ["--shadow-config", str(_shadow_cfg(tmp_path))] if mode == "on" else []
        for d in days:
            assert (
                D.main(
                    ["run", "--ledger", str(ledger), "--warmup", str(wu), "--date", d, *extra],
                    deps(gw, out),
                )
                == 0
            ), out
        ledgers[mode] = ledger.read_bytes()
        if mode == "on":
            shadow = (tmp_path / "shadow.jsonl").read_text().splitlines()
            assert len(shadow) == 5 and gw.count("placeOrder") > 0
            assert gw.calls[0][1]["readonly"] is False
    assert ledgers["on"] == ledgers["off"]
    first = __import__("json").loads(ledgers["on"].splitlines()[0])
    assert any(first["orders"].values())  # the frozen strategy trades off the IBKR warm-up


def test_a_failing_shadow_route_keeps_the_record_and_exits_4(tmp_path):
    listings = build_listings(FIRST, LAST)
    gw = MockGateway(
        listings,
        build_bars(listings, FIRST, LAST),
        now=ct(2026, 11, 6, 19),
        accounts=("DU0000001",),
    )
    out: list[str] = []
    ledger = tmp_path / "l.jsonl"
    rc = D.main(
        [
            "run",
            "--no-warmup",
            "--ledger",
            str(ledger),
            "--date",
            "2026-11-02",
            "--shadow-config",
            str(_shadow_cfg(tmp_path)),
        ],
        deps(gw, out),
    )
    assert rc == 4 and ledger.exists() and "managed accounts" in out[-1]
    assert PAPER not in "".join(out)


def test_export_csv_subcommand_replays_the_warmup(tmp_path):
    from forward.history import load_warmup
    from forward.sources import CsvSettlementSource

    _, wu = _warmup_and_mock(tmp_path)
    out: list[str] = []
    assert (
        D.main(
            ["export-csv", "--warmup", str(wu), "--out", str(tmp_path / "x.csv")],
            D.Deps(out=out.append),
        )
        == 0
    )
    rows = load_warmup(wu)
    src = CsvSettlementSource(tmp_path / "x.csv")
    for r in (rows[0], rows[len(rows) // 2], rows[-1]):
        assert src.settlements(r.date) == {i: dict(q) for i, q in r.prices.items()}
    assert (tmp_path / "x.csv").read_text() == (tmp_path / "warmup.csv").read_text()


def test_run_needs_an_explicit_warmup_choice(tmp_path):
    gw, out = mock(ct(2026, 11, 2, 19)), []
    rc = D.main(
        ["run", "--ledger", str(tmp_path / "l.jsonl"), "--date", "2026-11-02"], deps(gw, out)
    )
    assert rc == 2 and "--warmup" in out[-1] and not (tmp_path / "l.jsonl").exists()
    assert gw.calls == []  # refused before any connection


def test_warmup_refuses_an_existing_file_before_connecting(tmp_path):
    wu = tmp_path / "warmup.jsonl"
    wu.write_text("")
    gw, out = mock(ct(2026, 11, 1, 12)), []
    assert D.main(["warmup", "--start", "2026-11-02", "--out", str(wu)], deps(gw, out)) == 2
    assert "never overwritten" in out[-1] and gw.calls == []


def test_warmup_before_the_last_days_cutoff_is_refused(tmp_path):
    gw, out = mock(ct(2026, 10, 30, 17, 30)), []
    rc = D.main(
        ["warmup", "--start", "2026-11-02", "--out", str(tmp_path / "w.jsonl")], deps(gw, out)
    )
    assert rc == 2 and "not final" in out[-1] and not (tmp_path / "w.jsonl").exists()


def test_probe_reports_bars_or_the_error_code_and_writes_nothing(tmp_path):
    from tests._forward_ibkr_mock import FakeRequestError

    gw, out = mock(ct(2026, 11, 6, 19)), []
    assert D.main(["probe", "--market-data-type", "3"], deps(gw, out)) == 0
    assert out[-1].startswith("probe MNQ MNQZ26 market_data_type=3: bars=")
    names = [name for name, _ in gw.calls]
    assert names[:2] == ["connect", "reqMarketDataType"]  # factcheck C1: delayed type first
    assert gw.calls[1][1] == {"type": 3}
    gw2, out2 = mock(ct(2026, 11, 6, 19)), []
    gw2.fail["reqHistoricalData"] = [FakeRequestError(4, 10089, "API data requires subscription")]
    assert D.main(["probe"], deps(gw2, out2)) == 2
    assert "10089" in out2[-1] and "subscription needed" in out2[-1]
    assert gw2.calls[1] == ("reqMarketDataType", {"type": 3})  # the default (factcheck C1)
    assert list(tmp_path.iterdir()) == []


# --- wave 3 (IBKRFixer): S3 date and holiday guards, S1/B1 warm-up refusals, S4 probe log, N3 ---
def _run(tmp_path, gw, *extra, ledger="l.jsonl"):
    out: list[str] = []
    rc = D.main(["run", "--no-warmup", "--ledger", str(tmp_path / ledger), *extra], deps(gw, out))
    return rc, out


def _holidays(tmp_path, *lines):
    path = tmp_path / "cme_holidays.txt"
    path.write_text("# operator's copy of the published CME holiday calendar\n" + "\n".join(lines))
    return str(path)


def test_run_without_a_date_needs_a_holiday_file(tmp_path):
    gw = mock(ct(2026, 11, 4, 19))
    rc, out = _run(tmp_path, gw)
    assert rc == 2 and "--date" in out[-1] and "--holidays" in out[-1]
    assert gw.calls == [] and not (tmp_path / "l.jsonl").exists()


def test_a_listed_holiday_is_never_recorded_and_is_declared_closed_in_the_gap(tmp_path):
    hol = _holidays(tmp_path, "2026-11-26 Thanksgiving Day", "2026-12-25 Christmas Day")
    gw = mock(ct(2026, 11, 25, 19))
    assert _run(tmp_path, gw, "--holidays", hol)[0] == 0  # default date: 2026-11-25
    gw.now = ct(2026, 11, 26, 19)  # the holiday's own evening: IB may serve a bar dated 11-26
    rc, out = _run(tmp_path, gw, "--holidays", hol)
    assert rc == 2 and "2026-11-26" in out[-1] and "closed" in out[-1]
    rc, out = _run(tmp_path, gw, "--holidays", hol, "--date", "2026-11-26")
    assert rc == 2 and "closed" in out[-1]
    assert len((tmp_path / "l.jsonl").read_text().splitlines()) == 1
    gw.now = ct(2026, 11, 27, 19)
    rc, out = _run(tmp_path, gw, "--holidays", hol)
    assert rc == 0, out
    last = __import__("json").loads((tmp_path / "l.jsonl").read_text().splitlines()[-1])
    assert last["date"] == "2026-11-27" and last["declared_closed"] == ["2026-11-26"]


def test_a_malformed_holiday_file_is_refused(tmp_path):
    gw = mock(ct(2026, 11, 4, 19))
    rc, out = _run(tmp_path, gw, "--holidays", _holidays(tmp_path, "2026-11-28 a Saturday"))
    assert rc == 2 and "weekend" in out[-1] and gw.calls == []


@pytest.mark.parametrize("group", [("MGC",), ("MZC", "MZS", "MZL")], ids=["COMEX", "CBOT-grains"])
def test_a_whole_exchange_missing_while_others_are_priced_needs_the_flag(tmp_path, group):
    day = date(2026, 11, 4)
    listings = build_listings(FIRST, LAST)
    holes = {(cid, day) for (inst, cid) in listings if inst in group}
    gw = mock(ct(2026, 11, 5, 19), holes=holes)
    rc, out = _run(tmp_path, gw, "--date", "2026-11-04")
    assert rc == 5 and "--accept-exchange-gap" in out[-1]
    assert all(i in out[-1] for i in group) and not (tmp_path / "l.jsonl").exists()
    rc, out = _run(tmp_path, gw, "--date", "2026-11-04", "--accept-exchange-gap")
    assert rc == 0, out
    flags = __import__("json").loads((tmp_path / "l.jsonl").read_text())["flags"]
    assert all(f"missing:{i}" in flags for i in group)


def test_one_missing_contract_on_a_shared_exchange_is_not_an_exchange_gap(tmp_path):
    day = date(2026, 11, 4)
    gw = mock(ct(2026, 11, 5, 19), holes={("MCLZ26", day)})  # MNG still priced on NYMEX
    rc, out = _run(tmp_path, gw, "--date", "2026-11-04")
    assert rc == 0, out


def test_an_undeclared_gap_exits_2_without_a_traceback(tmp_path):
    gw = mock(ct(2026, 11, 6, 19))
    assert _run(tmp_path, gw, "--date", "2026-11-02")[0] == 0
    rc, out = _run(tmp_path, gw, "--date", "2026-11-04")
    assert rc == 2 and "RunnerError" in out[-1] and "no record written" in out[-1]
    assert len((tmp_path / "l.jsonl").read_text().splitlines()) == 1


def test_warmup_refuses_a_stalled_window_and_writes_nothing(tmp_path):
    listings = build_listings(date(2024, 3, 1), LAST)
    gw = MockGateway(
        listings, build_bars(listings, date(2024, 3, 1), LAST), now=ct(2026, 11, 1, 12)
    )
    gw.stall[gw.listings[("MNQ", "MNQZ25")].contract.conId] = [10] * 4
    out: list[str] = []
    d = deps(gw, out)
    d.clock = gw.monotonic
    wu = tmp_path / "warmup.jsonl"
    assert D.main(["warmup", "--start", "2026-11-02", "--out", str(wu)], d) == 2
    assert "timed out" in out[-1] and list(tmp_path.iterdir()) == []


def test_warmup_refuses_an_open_roll_with_a_stale_last_date(tmp_path):
    from tests._forward_ibkr_mock import weekdays

    listings = build_listings(date(2024, 3, 1), LAST)
    holes = {("MNQZ26", x) for x in weekdays(date(2026, 9, 10), date(2026, 9, 18))}
    gw = MockGateway(
        listings,
        build_bars(listings, date(2024, 3, 1), LAST, holes=holes),
        now=ct(2026, 11, 1, 12),
    )
    out: list[str] = []
    wu = tmp_path / "warmup.jsonl"
    assert D.main(["warmup", "--start", "2026-11-02", "--out", str(wu)], deps(gw, out)) == 2
    assert "MNQ" in out[-1] and "open roll" in out[-1] and list(tmp_path.iterdir()) == []


def test_probe_logs_the_same_bar_at_different_ages(tmp_path):
    import json

    from forward.sources_ibkr import ib_end_of_day

    gw, out = mock(ct(2026, 11, 6, 19)), []
    log = tmp_path / "probe.jsonl"
    assert D.main(["probe", "--log", str(log)], deps(gw, out)) == 0
    ends = [c[1]["end"] for c in gw.calls if c[0] == "reqHistoricalData"]
    assert ends == ["", ib_end_of_day(date(2026, 11, 6))]  # N2: the explicit end form too
    con = gw.listings[("MNQ", "MNQZ26")].contract.conId
    gw.bars[con][date(2026, 11, 6)] += 1.0  # e.g. the close replaced by the settlement later
    gw.now = ct(2026, 11, 9, 8)  # Monday 08:00 CT: 11-06 is still the latest ready date
    out2: list[str] = []
    assert D.main(["probe", "--log", str(log)], deps(gw, out2)) == 0
    lines = [json.loads(x) for x in log.read_text().splitlines()]
    same = [x for x in lines if x["bar_date"] == "2026-11-06" and x["request_end"] == ""]
    assert len(same) == 2 and same[1]["close_ib"] - same[0]["close_ib"] == 1.0
    assert same[0]["age_h"] == 1.0 and same[1]["age_h"] == 62.0
    assert all(x["field"] == "close_last_trade" and x["contract_id"] == "MNQZ26" for x in lines)
    assert any("2026-11-06" in line and "changed" in line for line in out2)
    assert not any(v in log.read_text() for v in ("127.0.0.1", "4002", PAPER))
