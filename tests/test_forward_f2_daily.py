"""E22-F2 daily driver: the E22-F2 ledger is byte-identical with the shadow route on and off."""

import json
from datetime import date, datetime, time, timedelta
from types import SimpleNamespace
from zoneinfo import ZoneInfo

from forward import daily_f2, orders_alpaca
from forward.etf_bars import EtfBar, EtfDayRow, InMemoryEtfSource
from forward.runner_f2 import PaperBookF2, load_book_config

NY = ZoneInfo("America/New_York")
CFG = load_book_config()
W = date(2026, 11, 4)
DAYS = [date(2026, 11, 5), date(2026, 11, 6), date(2026, 11, 9), date(2026, 11, 10)]


class _NotFound(Exception):  # noqa: N818
    status_code = 404


class FakeTradingClient:
    _base_url = orders_alpaca.PAPER_TRADING_URL

    def __init__(self):
        self.submitted = []

    def get_account(self):
        return SimpleNamespace(
            status="ACTIVE",
            shorting_enabled=True,
            equity="25000",
            buying_power="50000",
            multiplier="2",
        )

    def get_all_positions(self):
        return []

    def get_asset(self, symbol):
        return SimpleNamespace(fractionable=True, shortable=True, easy_to_borrow=True)

    def get_orders(self, filter=None):  # noqa: A002
        return []

    def get_order_by_client_id(self, client_id):
        # orders_alpaca now looks each pending order up by client id (AlpacaFixer, wave 3); this
        # fake account lists no orders, so the lookup answers 404 like get_orders' empty list
        raise _NotFound(f"no order {client_id}")

    def submit_order(self, order_data):
        self.submitted.append(order_data)
        return SimpleNamespace(id=f"id{len(self.submitted)}", status="accepted")


def data():
    out, prev = {}, W
    for k, d in enumerate(DAYS):
        out[d] = {
            "QQQ": EtfBar(500.0 + k, 0.002, prev),
            "TLT": EtfBar(90.0, 0.0, prev),
            "BIL": EtfBar(91.5, 0.0001, prev),
        }
        prev = d
    return out


def targets(history, held, config, *, decision_date):
    k = DAYS.index(decision_date)
    return {s: (10.0 + k if s == "QQQ" else (-5.0 if s == "TLT" else 0.0)) for s in CFG.symbols}


def run(tmp_path, name, shadow_on):
    warm = (EtfDayRow(W, {"QQQ": EtfBar(500.0), "TLT": EtfBar(90.0), "BIL": EtfBar(91.5)}),)
    ledger = tmp_path / f"{name}.jsonl"
    bk = PaperBookF2(ledger, InMemoryEtfSource(data()), CFG, warmup=warm, target_fn=targets)
    now = {"t": None}
    shadow = None
    client = FakeTradingClient()
    if shadow_on:
        cfg = orders_alpaca.ShadowConfig(True, tmp_path / f"{name}_shadow.jsonl", "moc_whole")
        shadow = orders_alpaca.ShadowRoute(
            cfg,
            ledger,
            client,
            order_factory=lambda **kw: kw,
            query_factory=lambda **kw: kw,
            clock=lambda: now["t"],
        )
    for d in DAYS:
        now["t"] = datetime.combine(d, time(20, 0), NY)
        rec, srec = daily_f2.run_session(bk, d, shadow=shadow)
        assert (srec is not None) == shadow_on
    return ledger.read_bytes(), client


def test_ledger_byte_identical_with_shadow_on_and_off(tmp_path):
    off, _ = run(tmp_path, "off", False)
    on, client = run(tmp_path, "on", True)
    assert off == on
    assert client.submitted  # the shadow route did place paper orders
    shadow_lines = (tmp_path / "on_shadow.jsonl").read_text().splitlines()
    assert len(shadow_lines) == len(DAYS)
    assert json.loads(shadow_lines[0])["targets"]["QQQ"] == 10.0


def test_build_shadow_disabled_by_default(tmp_path):
    assert daily_f2.build_shadow(daily_f2.DEFAULT_SHADOW, tmp_path / "x.jsonl") is None
    assert daily_f2.build_shadow(tmp_path / "missing.json", tmp_path / "x.jsonl") is None


def test_source_choice_without_credentials(tmp_path):
    csv = tmp_path / "b.csv"
    csv.write_text("trade_date,symbol,close,ret,prev_date\n2026-11-05,QQQ,500,0.001,2026-11-04\n")
    src = daily_f2.make_source(CFG, csv_path=csv, environ={})
    assert type(src).__name__ == "CsvEtfSource"
    assert daily_f2.credentials_present({}) is False
    names = daily_f2.credential_names()
    assert daily_f2.credentials_present({names[0]: "x", names[1]: "y"}) is True
    assert DAYS[0] - timedelta(days=1) == W
