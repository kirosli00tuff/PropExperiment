"""Stage E.0: data/quote_universe.py must be unable to request data.

Fake clients only: no network, no DATABENTO_API_KEY, and every ledger and ACCESS
doc lives under tmp_path. The real ledger/databento_spend.jsonl and docs/ACCESS.md
are never written (checked explicitly in the refusal test).
"""

from __future__ import annotations

import ast
import json
import threading
import time
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from data import config
from data import quote_universe as qu
from data.spend_gate import BudgetRefusedError, Quote, RequestParams, read_entries

SOURCE = Path(qu.__file__).read_text()
MONEY_MOVING_CALLS = {"fetch_range", "authorize", "commit", "settle", "get_range",
                      "submit_job", "download"}
PARAMS = RequestParams("GLBX.MDP3", ("ES.v.0",), "ohlcv-1m", "continuous",
                       "2026-01-01", "2026-02-01")


# ------------------------------------------------------------- fakes ----
class FakeHttpError(Exception):
    def __init__(self, status: int) -> None:
        super().__init__(f"HTTP {status}")
        self.http_status = status


class FakeMetadata:
    """Thread-safe fake pricing. ``script`` maps a start string to exceptions raised first."""

    def __init__(self, usd: float = 0.25, nbytes: int = 56 * 1000,
                 script: dict[str, list[Exception]] | None = None, delay_s: float = 0.0) -> None:
        self.usd, self.nbytes, self.delay_s = usd, nbytes, delay_s
        self.script = {k: list(v) for k, v in (script or {}).items()}
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self._lock = threading.Lock()

    def _hit(self, name: str, kwargs: dict[str, Any]) -> None:
        with self._lock:
            self.calls.append((name, kwargs))
            pending = self.script.get(kwargs["start"])
            exc = pending.pop(0) if pending else None
        if self.delay_s:
            time.sleep(self.delay_s)
        if exc is not None:
            raise exc

    def get_cost(self, **kwargs: Any) -> float:
        self._hit("get_cost", kwargs)
        return self.usd

    def get_billable_size(self, **kwargs: Any) -> int:
        self._hit("get_billable_size", kwargs)
        return self.nbytes


class FakeSymbology:
    def __init__(self, first: dict[str, str | None]) -> None:
        self.first = first
        self.calls: list[dict[str, Any]] = []

    def resolve(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(kwargs)
        symbol = kwargs["symbols"][0]
        d0 = self.first.get(symbol.removesuffix(".v.0"))
        if d0 is None:
            return {"result": {}, "not_found": [symbol], "partial": []}
        return {"result": {symbol: [{"d0": d0, "d1": "2026-06-21", "s": "12345"}]},
                "not_found": [], "partial": []}


class RecordingNamespace:
    def __init__(self, hits: list[str]) -> None:
        self._hits = hits

    def __getattr__(self, name: str) -> Any:
        self._hits.append(name)
        return lambda *a, **k: "BILLABLE"


def fake_client(metadata: FakeMetadata | None = None,
                first: dict[str, str | None] | None = None) -> SimpleNamespace:
    hits: list[str] = []
    return SimpleNamespace(
        metadata=metadata or FakeMetadata(), symbology=FakeSymbology(first or {}),
        timeseries=RecordingNamespace(hits), batch=RecordingNamespace(hits), billable_hits=hits,
    )


@pytest.fixture
def tmp_gate(tmp_path: Path) -> qu.LockedQuoteGate:
    external = tmp_path / "external_ledger.jsonl"
    external.write_text(json.dumps({"usd": 82.12}) + "\n")
    return qu.e0_gate(ledger_path=tmp_path / "ledger.jsonl", external_ledger_paths=(external,),
                      access_doc_path=tmp_path / "ACCESS.md")


def no_sleep(_: float) -> None:
    return None


def _lines(path: Path) -> int:
    return len(path.read_text().splitlines()) if path.is_file() else 0


# ------------------------------------------------ 1. the gate refuses ----
class TestGateRefusesBillable:
    def test_a_one_cent_quote_is_refused_and_ledgered_to_the_tmp_ledger_only(
        self, tmp_gate: qu.LockedQuoteGate
    ) -> None:
        # Arrange
        real_ledger, real_access = config.LEDGER_PATH, config.ACCESS_DOC_PATH
        before = (_lines(real_ledger), real_access.stat().st_size if real_access.exists() else 0)
        quote = Quote(PARAMS, 0.01, 56)

        # Act
        with pytest.raises(BudgetRefusedError):
            tmp_gate.authorize(PARAMS, quote)

        # Assert
        entries = read_entries(tmp_gate.ledger_path)
        assert [e["event"] for e in entries] == ["refused"]
        assert entries[0]["session_id"] == "stage-E.0-2026-09-23"
        assert entries[0]["usd"] == 0.0
        assert tmp_gate.access_doc_path.read_text().count("refused by spend gate") == 1
        after = (_lines(real_ledger), real_access.stat().st_size if real_access.exists() else 0)
        assert after == before

    def test_the_session_cap_alone_also_refuses(self, tmp_path: Path) -> None:
        external = tmp_path / "ext.jsonl"
        external.write_text("")
        gate = qu.e0_gate(ledger_path=tmp_path / "l.jsonl", external_ledger_paths=(external,),
                          access_doc_path=tmp_path / "A.md", request_cap_usd=5.0)
        with pytest.raises(BudgetRefusedError, match="session cap"):
            gate.authorize(PARAMS, Quote(PARAMS, 0.01, 56))

    def test_the_default_gate_has_zero_caps_and_the_e0_session(self) -> None:
        gate = qu.e0_gate()
        assert (gate.session_id, gate.session_cap_usd, gate.request_cap_usd) == (
            "stage-E.0-2026-09-23", 0.0, 0.0)

    def test_run_quotes_refuses_a_gate_with_nonzero_caps(self, tmp_path: Path) -> None:
        external = tmp_path / "ext.jsonl"
        external.write_text("")
        gate = qu.e0_gate(ledger_path=tmp_path / "l.jsonl", external_ledger_paths=(external,),
                          access_doc_path=tmp_path / "A.md", session_cap_usd=1.0)
        with pytest.raises(RuntimeError, match=r"\$0.00"):
            qu.run_quotes(fake_client(), gate, [], log=lambda _: None)


# ------------------------------------------- 2. no billable call site ----
class TestSourceHasNoBillableCallSite:
    def test_no_attribute_access_on_a_billable_namespace(self) -> None:
        tree = ast.parse(SOURCE)
        offenders = sorted({n.attr for n in ast.walk(tree)
                            if isinstance(n, ast.Attribute) and n.attr in ("timeseries", "batch")})
        assert offenders == []

    def test_no_money_moving_or_download_call(self) -> None:
        # Arrange
        called: set[str] = set()
        for node in ast.walk(ast.parse(SOURCE)):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name):
                    called.add(func.id)
                elif isinstance(func, ast.Attribute):
                    called.add(func.attr)

        # Act
        offenders = sorted(called & MONEY_MOVING_CALLS)

        # Assert
        assert offenders == []

    def test_fetch_range_is_not_imported(self) -> None:
        imported: set[str] = set()
        for node in ast.walk(ast.parse(SOURCE)):
            if isinstance(node, ast.Import | ast.ImportFrom):
                imported |= {a.name for a in node.names}
        assert "fetch_range" not in imported
        assert not hasattr(qu, "fetch_range")

    def test_no_dotted_billable_namespace_in_the_text(self) -> None:
        assert ".timeseries" not in SOURCE
        assert ".batch" not in SOURCE

    def test_the_module_declares_a_zero_budget(self) -> None:
        assert "Budget for this stage is $0.00" in SOURCE


# ------------------------------------------------------- 3. the guard ----
class TestGuard:
    def test_every_guarded_namespace_raises_on_access_and_call(self) -> None:
        client = qu.install_forbidden_guards(fake_client())
        for name in ("timeseries", "batch"):
            namespace = getattr(client, name)
            with pytest.raises(RuntimeError, match="E.0: timeseries/batch forbidden"):
                namespace.get_range  # noqa: B018
            with pytest.raises(RuntimeError, match="forbidden"):
                namespace()
        assert client.billable_hits == []

    def test_the_free_namespaces_survive(self) -> None:
        client = qu.install_forbidden_guards(fake_client(first={"ES": "2019-05-01"}))
        assert client.metadata.get_cost(start="x") == 0.25
        assert "result" in client.symbology.resolve(symbols=["ES.v.0"])

    def test_the_gate_sees_only_metadata(self) -> None:
        view = qu.QuoteOnlyView(fake_client())
        assert not hasattr(view, "timeseries")
        assert not hasattr(view, "batch")
        assert not hasattr(view, "symbology")

    def test_build_client_installs_the_guards_without_a_network_call(self) -> None:
        client = qu.build_client("db-NOT-A-REAL-KEY-for-a-local-constructor-only")
        for name in qu.FORBIDDEN_NAMESPACES:
            assert isinstance(getattr(client, name), qu.ForbiddenNamespace)

    def test_a_full_run_never_touches_a_billable_namespace(
        self, tmp_gate: qu.LockedQuoteGate, tmp_path: Path
    ) -> None:
        client = fake_client(first={"MBT": "2021-03-29"})
        qu.run_all(client, tmp_gate, symbology_path=tmp_path / "sym.json", log=lambda _: None,
                   sleep=no_sleep, products=[qu.PRODUCTS_BY_ROOT["MBT"]])
        assert client.billable_hits == []
        events = {e["event"] for e in read_entries(tmp_gate.ledger_path)}
        assert events == {"quote"}


# ----------------------------------------------------- 4. chunking ----
class TestChunking:
    def test_an_early_listed_product_has_86_chunks_ending_at_june_21(self) -> None:
        chunks = qu.history_chunks(date(2010, 9, 1))
        assert len(chunks) == 86
        assert chunks[0] == ("2019-05-01", "2019-06-01")
        assert chunks[-1] == ("2026-06-01", "2026-06-21")

    def test_a_product_first_mapped_in_july_2021_starts_on_july_1(self) -> None:
        chunks = qu.history_chunks(date(2021, 7, 12))
        assert chunks[0] == ("2021-07-01", "2021-08-01")
        assert chunks[-1] == ("2026-06-01", "2026-06-21")

    def test_the_plan_uses_the_symbology_first_mapped_date(self) -> None:
        sym = {"MET": {"status": "resolved", "first_mapped": "2021-12-06"}}
        planned = qu.plan_quotes(sym, [qu.PRODUCTS_BY_ROOT["MET"]])
        set_a = [q for q in planned if q.set_name == "A"]
        assert set_a[0].params.start == "2021-12-01"
        assert {q.set_name for q in planned} == {"A", "B", "C"}
        assert sum(q.set_name == "B" for q in planned) == 10
        assert sum(q.set_name == "C" for q in planned) == 5

    def test_the_universe_is_50_products_without_mes(self) -> None:
        assert len(qu.PRODUCTS) == 50
        assert "MES" not in qu.PRODUCTS_BY_ROOT
        per = {c: sum(p.cluster == c for p in qu.PRODUCTS) for c in qu.CLUSTERS}
        assert per == {"K1": 8, "K2": 6, "K3": 12, "K4": 8, "K5": 7, "K6": 7, "K7": 2}


# ------------------------------------------------------- 5. windows ----
class TestWindows:
    def test_no_set_a_request_ends_after_the_history_end(self) -> None:
        sym = {p.root: {"status": "resolved", "first_mapped": "2019-05-01"} for p in qu.PRODUCTS}
        planned = qu.plan_quotes(sym)
        assert max(qu.parse_utc(q.params.end) for q in planned if q.set_name == "A") == \
            qu.parse_utc("2026-06-21T00:00:00Z")
        qu.check_windows(planned)  # does not raise

    def test_every_b_and_c_window_is_inside_the_sample_span_and_outside_holdout_2(self) -> None:
        sym = {p.root: {"status": "resolved", "first_mapped": "2019-05-01"} for p in qu.PRODUCTS}
        lo, hi = qu.parse_utc("2025-04-01"), qu.parse_utc("2026-06-21")
        h2_lo, h2_hi = qu.parse_utc("2024-03-01"), qu.parse_utc("2025-04-01")
        for q in qu.plan_quotes(sym):
            if q.set_name == "A":
                continue
            start, end = qu.parse_utc(q.params.start), qu.parse_utc(q.params.end)
            assert lo <= start < end <= hi
            assert start >= h2_hi or end <= h2_lo

    def test_check_windows_refuses_a_late_request(self) -> None:
        late = qu.PlannedQuote("A", "ES", RequestParams(
            "GLBX.MDP3", ("ES.v.0",), "ohlcv-1m", "continuous", "2026-06-01",
            "2026-06-21T22:00:00Z"))
        with pytest.raises(ValueError, match="end after"):
            qu.check_windows([late])

    def test_full_trade_date_cdt_starts_at_2200z(self) -> None:
        assert qu.full_trade_date_window_utc(date(2025, 5, 14)) == (
            "2025-05-13T22:00:00Z", "2025-05-14T21:00:00Z")

    def test_full_trade_date_cst_starts_at_2300z(self) -> None:
        assert qu.full_trade_date_window_utc(date(2025, 11, 12)) == (
            "2025-11-11T23:00:00Z", "2025-11-12T22:00:00Z")

    def test_day_session_windows_convert_with_dst(self) -> None:
        es, zn = qu.PRODUCTS_BY_ROOT["ES"], qu.PRODUCTS_BY_ROOT["ZN"]
        assert qu.day_session_window_utc(es, date(2025, 8, 13)) == (
            "2025-08-13T13:30:00Z", "2025-08-13T20:00:00Z")
        assert qu.day_session_window_utc(zn, date(2026, 2, 11)) == (
            "2026-02-11T13:20:00Z", "2026-02-11T20:00:00Z")
        assert (es.window_minutes, zn.window_minutes) == (390, 400)
        assert qu.PRODUCTS_BY_ROOT["HE"].window_minutes == 275


# -------------------------------------------------- 6. resumability ----
class TestResumability:
    def test_an_already_quoted_request_is_skipped(self, tmp_gate: qu.LockedQuoteGate) -> None:
        # Arrange
        es = qu.PRODUCTS_BY_ROOT["ES"]
        planned = qu.plan_set_a(es, date(2010, 1, 1))[:3]
        first = fake_client()
        tmp_gate.quote(qu.QuoteOnlyView(first), planned[0].params)
        client = fake_client()

        # Act
        outcomes = qu.run_quotes(client, tmp_gate, planned, log=lambda _: None, sleep=no_sleep)

        # Assert
        assert [o.planned.params.start for o in outcomes] == ["2019-06-01", "2019-07-01"]
        priced = {kw["start"] for _, kw in client.metadata.calls}
        assert priced == {"2019-06-01", "2019-07-01"}

    def test_a_failed_quote_is_retried_on_the_next_run(self, tmp_gate: qu.LockedQuoteGate) -> None:
        es = qu.PRODUCTS_BY_ROOT["ES"]
        planned = qu.plan_set_a(es, date(2010, 1, 1))[:1]
        bad = fake_client(FakeMetadata(script={"2019-05-01": [FakeHttpError(400)]}))
        assert qu.run_quotes(bad, tmp_gate, planned, log=lambda _: None)[0].usd is None
        again = qu.run_quotes(fake_client(), tmp_gate, planned, log=lambda _: None)
        assert again[0].usd == 0.25

    def test_symbology_skips_resolved_and_records_unresolved(self, tmp_path: Path) -> None:
        path = tmp_path / "sym.json"
        products = [qu.PRODUCTS_BY_ROOT["ES"], qu.PRODUCTS_BY_ROOT["NKD"]]
        client = fake_client(first={"ES": "2019-05-01", "NKD": None})
        out = qu.resolve_symbology(client, products, path, log=lambda _: None, sleep=no_sleep)
        assert out["ES"]["status"] == "resolved"
        assert out["NKD"]["status"] == "unresolved"
        assert "not_found" in out["NKD"]["error"]
        client2 = fake_client(first={"ES": "2019-05-01", "NKD": None})
        qu.resolve_symbology(client2, products, path, log=lambda _: None, sleep=no_sleep)
        assert [c["symbols"] for c in client2.symbology.calls] == [["NKD.v.0"]]


# ------------------------------------------------- retry and failures ----
class TestRetry:
    def test_429_and_5xx_are_retried_with_exponential_backoff(self) -> None:
        sleeps: list[float] = []
        errors = [FakeHttpError(429), FakeHttpError(503)]

        def flaky() -> str:
            if errors:
                raise errors.pop(0)
            return "ok"

        assert qu.call_with_retry(flaky, sleep=sleeps.append) == "ok"
        assert sleeps == [1.0, 2.0]

    def test_a_4xx_other_than_429_is_not_retried(self) -> None:
        calls: list[int] = []

        def bad() -> None:
            calls.append(1)
            raise FakeHttpError(400)

        with pytest.raises(FakeHttpError):
            qu.call_with_retry(bad, sleep=no_sleep)
        assert len(calls) == 1

    def test_five_failures_leave_a_failed_quote_in_the_ledger(
        self, tmp_gate: qu.LockedQuoteGate
    ) -> None:
        es = qu.PRODUCTS_BY_ROOT["ES"]
        planned = qu.plan_set_a(es, date(2010, 1, 1))[:1]
        meta = FakeMetadata(script={"2019-05-01": [FakeHttpError(500)] * 5})
        out = qu.run_quotes(fake_client(meta), tmp_gate, planned, log=lambda _: None,
                            sleep=no_sleep)
        assert out[0].usd is None
        assert len(meta.calls) == 5
        (entry,) = read_entries(tmp_gate.ledger_path)
        assert entry["quoted_usd"] is None and entry["note"].startswith("quote failed")


# ------------------------------------------ 7. report arithmetic ----
def _quote_line(root: str, schema: str, start: str, end: str, usd: float, nbytes: int,
                *, ok: bool = True, event: str = "quote") -> dict[str, Any]:
    request = RequestParams("GLBX.MDP3", (f"{root}.v.0",), schema, "continuous",
                            start, end).as_kwargs()
    return {"event": event, "session_id": qu.STAGE_E0_SESSION_ID, "usd": 0.0,
            "quoted_usd": usd if ok else None, "billable_bytes": nbytes if ok else 0,
            "request": request, "note": "" if ok else "quote failed: X"}


class TestReport:
    def _synthetic(self) -> tuple[list[tuple[int, dict[str, Any]]], dict[str, Any]]:
        es_b = qu.full_trade_date_window_utc(date(2025, 5, 14))
        es_c1 = qu.day_session_window_utc(qu.PRODUCTS_BY_ROOT["ES"], date(2025, 5, 14))
        es_c2 = qu.day_session_window_utc(qu.PRODUCTS_BY_ROOT["ES"], date(2025, 8, 13))
        lines = [
            _quote_line("ES", "ohlcv-1m", "2026-05-01", "2026-06-01", 1.0, 56 * 21_000),
            _quote_line("ES", "ohlcv-1m", "2026-06-01", "2026-06-21", 0.5, 56 * 14_000),
            _quote_line("ES", "mbp-1", *es_b, 2.0, 1_000),
            _quote_line("ES", "tbbo", *es_b, 0.3, 200),
            _quote_line("ES", "ohlcv-1m", *es_c1, 0.01, 56 * 390),
            _quote_line("ES", "ohlcv-1m", *es_c2, 0.01, 56 * 195),
            _quote_line("ZN", "ohlcv-1m", "2026-06-01", "2026-06-21", 0.25, 56 * 1_400),
            _quote_line("ZN", "tbbo", *es_b, 0.0, 0, ok=False),
        ]
        sym = {"ES": {"status": "resolved", "first_mapped": "2019-05-01"},
               "ZN": {"status": "resolved", "first_mapped": "2019-05-01"},
               "NKD": {"status": "unresolved", "error": "not found"}}
        return [(100 + i, e) for i, e in enumerate(lines)], sym

    def test_records_coverage_and_totals(self) -> None:
        # Arrange
        lined, sym = self._synthetic()

        # Act
        rep = qu.build_report(lined, sym)

        # Assert
        es = next(r for r in rep["products"] if r["root"] == "ES")
        assert es["months_quoted"] == 2 and es["months_planned"] == 86
        assert es["ohlcv_1m_usd"] == pytest.approx(1.5)
        assert es["ohlcv_1m_records"] == 35_000
        assert es["quoted_range"] == ["2026-05-01", "2026-06-21"]
        assert es["weekdays_in_range"] == 36  # May 2026: 21, June 1-20: 15
        assert es["records_per_weekday"] == pytest.approx(35_000 / 36)
        assert (es["mbp1_usd"], es["mbp1_bytes"], es["tbbo_usd"]) == (2.0, 1_000, 0.3)
        assert es["coverage"] == {"2025-05-14": 1.0, "2025-08-13": 0.5}
        assert es["coverage_mean"] == pytest.approx(0.75)
        k1, k2 = rep["clusters"]["K1"], rep["clusters"]["K2"]
        assert k1["ohlcv_1m_usd"] == pytest.approx(1.5)  # set C ohlcv is not history
        assert k1["mbp1_usd"] == 2.0 and k1["products"] == 8
        assert k2["ohlcv_1m_usd"] == pytest.approx(0.25)
        assert rep["universe"]["ohlcv_1m_bytes"] == 56 * 36_400

    def test_set_c_is_not_counted_as_history(self) -> None:
        lined, sym = self._synthetic()
        rep = qu.build_report(lined, sym)
        k1 = rep["clusters"]["K1"]
        assert k1["ohlcv_1m_bytes"] == 56 * 35_000

    def test_counts_failures_unresolved_and_ledger_checks(self) -> None:
        lined, sym = self._synthetic()
        rep = qu.build_report(lined, sym)
        assert rep["counts"]["quote_events"] == 8
        assert rep["counts"]["failed_quote_events"] == 1
        assert rep["counts"]["outstanding_failures"] == 1
        assert rep["counts"]["unresolved_symbols"] == 48  # NKD + 47 never resolved
        assert rep["ledger"] == {
            "first_line": 100, "last_line": 107, "session_events": 8,
            "non_quote_or_nonzero_lines": [], "all_events_are_zero_usd_quotes": True,
            "session_committed_usd": 0.0, "passed": True,
        }

    def test_a_non_quote_event_fails_the_ledger_check(self) -> None:
        lined, sym = self._synthetic()
        bad = _quote_line("ES", "ohlcv-1m", "2026-04-01", "2026-05-01", 1.0, 56, event="commit")
        bad["usd"] = 1.0
        rep = qu.build_report([*lined, (200, bad)], sym)
        assert rep["ledger"]["passed"] is False
        assert rep["ledger"]["non_quote_or_nonzero_lines"] == [200]
        assert rep["ledger"]["session_committed_usd"] == 1.0

    def test_write_report_uses_only_this_sessions_lines(self, tmp_path: Path) -> None:
        lined, sym = self._synthetic()
        ledger = tmp_path / "ledger.jsonl"
        other = {**lined[0][1], "session_id": "stage-D.1f-2026-09", "quoted_usd": 99.0}
        ledger.write_text("\n".join(json.dumps(e) for e in [other, *(e for _, e in lined)]) + "\n")
        sym_path = tmp_path / "sym.json"
        qu.save_symbology(sym_path, {k: {"root": k, **v} for k, v in sym.items()})
        rep = qu.write_report(ledger_path=ledger, symbology_path=sym_path,
                              json_path=tmp_path / "r.json", md_path=tmp_path / "r.md")
        assert rep["ledger"]["first_line"] == 2
        assert rep["universe"]["ohlcv_1m_usd"] == pytest.approx(1.75)
        assert "| ES | K1 |" in (tmp_path / "r.md").read_text()
        assert json.loads((tmp_path / "r.json").read_text())["counts"]["quote_events"] == 8

    def test_the_ohlcv_record_size_is_56_bytes_in_the_installed_dbn(self) -> None:
        import databento_dbn
        import numpy as np

        assert qu.ohlcv_record_bytes() == 56 == qu.OHLCV_RECORD_BYTES
        assert np.dtype(databento_dbn.OHLCVMsg._dtypes).itemsize == 56


# ----------------------------------------------------- 8. config ----
class TestConfig:
    def test_e0_constants(self) -> None:
        assert config.STAGE_E0_SESSION_ID == "stage-E.0-2026-09-23"
        assert config.E0_SESSION_CAP_USD == 0.0
        assert config.E0_REQUEST_CAP_USD == 0.0
        assert config.SHARED_ACCOUNT_CAP_USD == 120.00

    def test_earlier_constants_unchanged(self) -> None:
        assert (config.SESSION_CAP_USD, config.D1F_SESSION_CAP_USD,
                config.D1F_REQUEST_CAP_USD) == (15.00, 10.00, 10.00)


# ------------------------------------------------ 9. the ledger lock ----
class TestLedgerLock:
    def test_concurrent_quotes_write_well_formed_lines(self, tmp_gate: qu.LockedQuoteGate) -> None:
        # Arrange
        planned = [q for root in ("ES", "NQ", "ZN")
                   for q in qu.plan_set_a(qu.PRODUCTS_BY_ROOT[root], date(2010, 1, 1))[:12]]
        client = fake_client(FakeMetadata(delay_s=0.002))

        # Act
        outcomes = qu.run_quotes(client, tmp_gate, planned, log=lambda _: None, workers=4)

        # Assert
        raw = tmp_gate.ledger_path.read_text().splitlines()
        assert len(raw) == len(outcomes) == 36
        parsed = [json.loads(line) for line in raw]
        assert all(e["event"] == "quote" and e["usd"] == 0.0 for e in parsed)
        keys = {qu.request_key(e["request"]) for e in parsed}
        assert keys == {qu.request_key(q.params.as_kwargs()) for q in planned}

    def test_every_append_holds_the_lock(self, tmp_gate: qu.LockedQuoteGate,
                                         monkeypatch: pytest.MonkeyPatch) -> None:
        from data.spend_gate import SpendGate

        seen: list[bool] = []
        original = SpendGate._append

        def spy(self: SpendGate, *args: Any, **kwargs: Any) -> dict[str, Any]:
            seen.append(tmp_gate.ledger_lock.locked())
            return original(self, *args, **kwargs)

        monkeypatch.setattr(SpendGate, "_append", spy)
        planned = qu.plan_set_a(qu.PRODUCTS_BY_ROOT["ES"], date(2010, 1, 1))[:4]
        qu.run_quotes(fake_client(), tmp_gate, planned, log=lambda _: None)
        assert seen == [True] * 4

    def test_at_most_four_workers(self, tmp_gate: qu.LockedQuoteGate) -> None:
        active, peak = [0], [0]
        lock = threading.Lock()

        class Counting(FakeMetadata):
            def get_cost(self, **kwargs: Any) -> float:
                with lock:
                    active[0] += 1
                    peak[0] = max(peak[0], active[0])
                time.sleep(0.005)
                with lock:
                    active[0] -= 1
                return 0.1

        planned = qu.plan_set_a(qu.PRODUCTS_BY_ROOT["ES"], date(2010, 1, 1))[:20]
        qu.run_quotes(fake_client(Counting()), tmp_gate, planned, log=lambda _: None, workers=16)
        assert 1 <= peak[0] <= 4


# --------------------------------------------- clean CLI refusals ----
class TestCliRefusesCleanly:
    def _no_client(self, _: str) -> Any:
        raise AssertionError("a client was built despite the refusal")

    def test_missing_key_refuses_before_any_vendor_call(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        def no_key() -> str:
            raise config.MissingSecretError("DATABENTO_API_KEY is not set")

        rc = qu.main(["--run"], key_loader=no_key, client_factory=self._no_client)
        assert rc == qu.RC_REFUSED
        assert "REFUSED before any vendor call" in capsys.readouterr().err

    def test_missing_external_ledger_refuses_before_any_vendor_call(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        def gate() -> qu.LockedQuoteGate:
            return qu.e0_gate(ledger_path=tmp_path / "l.jsonl",
                              external_ledger_paths=(tmp_path / "missing.jsonl",),
                              access_doc_path=tmp_path / "A.md")

        rc = qu.main(["--probe", "ES", "--n", "2"], key_loader=lambda: "k",
                     gate_factory=gate, client_factory=self._no_client)
        assert rc == qu.RC_REFUSED
        assert "ExternalLedgerUnavailableError" in capsys.readouterr().err
        assert not (tmp_path / "l.jsonl").exists()

    def test_probe_quotes_n_chunks_through_main(self, tmp_path: Path,
                                                monkeypatch: pytest.MonkeyPatch) -> None:
        external = tmp_path / "ext.jsonl"
        external.write_text("")
        client = qu.install_forbidden_guards(fake_client(first={"ES": "2019-05-01"}))
        monkeypatch.setattr(qu, "SYMBOLOGY_PATH", tmp_path / "sym.json")
        rc = qu.main(["--probe", "ES", "--n", "3"], key_loader=lambda: "k",
                     gate_factory=lambda: qu.e0_gate(
                         ledger_path=tmp_path / "l.jsonl", external_ledger_paths=(external,),
                         access_doc_path=tmp_path / "A.md"),
                     client_factory=lambda _: client)
        assert rc == 0
        starts = [e["request"]["start"] for e in read_entries(tmp_path / "l.jsonl")]
        assert starts == ["2019-05-01", "2019-06-01", "2019-07-01"]
        assert client.billable_hits == []
