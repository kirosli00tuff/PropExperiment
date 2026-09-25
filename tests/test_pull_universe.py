"""Stage E.1: data/pull_universe.py, the Stage E step 1 purchase path.

Fake clients only: no network, no DATABENTO_API_KEY. Every ledger, ACCESS doc, vendor root and
summary lives under tmp_path; the real ledger/databento_spend.jsonl and docs/ACCESS.md are
checked untouched. Downloaded files are synthetic DBN files written by the fake.
"""

from __future__ import annotations

import dataclasses
import datetime as dt
import hashlib
import json
import threading
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import databento_dbn as dbn
import pytest
import zstandard

from data import adapter, config
from data import pull_universe as pu
from data import quote_universe as qu
from data.spend_gate import BudgetRefusedError, RequestParams, read_entries

INSTRUMENT_ID = 4242
RECORD_SIZE = {"ohlcv-1m": 56, "mbp-1": 80}
MNQ_MBP1_DAY_USD = {"2026-02-11": 4.14, "2025-11-12": 3.41}  # E.0's two quotes over $3.00


# ------------------------------------------------------------- helpers ----
def _hours(kwargs: dict[str, Any]) -> float:
    span = qu.parse_utc(kwargs["end"]) - qu.parse_utc(kwargs["start"])
    return span.total_seconds() / 3600


def e0_like_price(kwargs: dict[str, Any]) -> float:
    """Pro rata in time. MNQ mbp-1 costs E.0's quote on its two expensive dates."""
    if kwargs["schema"] == "ohlcv-1m":
        return 0.10 * _hours(kwargs) / 720
    day_usd = 0.50
    if kwargs["symbols"] == ["MNQ.v.0"]:
        day_usd = MNQ_MBP1_DAY_USD.get(kwargs["end"][:10], 2.90)
    return day_usd * _hours(kwargs) / 23


def records_for(kwargs: dict[str, Any]) -> int:
    return max(1, int(_hours(kwargs)))  # one synthetic record per hour


def billable_for(kwargs: dict[str, Any]) -> int:
    return records_for(kwargs) * RECORD_SIZE[kwargs["schema"]]


def write_dbn(path: Path, schema: str, symbol: str, start: str, end: str, n_records: int) -> None:
    """A zstd DBN file with metadata, a symbol mapping and ``n_records`` records."""
    t0 = int(qu.parse_utc(start).timestamp()) * 10**9
    t1 = int(qu.parse_utc(end).timestamp()) * 10**9
    day0, day1 = qu.parse_utc(start).date(), qu.parse_utc(end).date() + dt.timedelta(days=1)
    mapping = SimpleNamespace(raw_symbol=symbol, intervals=[
        SimpleNamespace(start_date=day0, end_date=day1, symbol=str(INSTRUMENT_ID))])
    kind = dbn.Schema.OHLCV_1M if schema == "ohlcv-1m" else dbn.Schema.MBP_1
    meta = dbn.Metadata("GLBX.MDP3", t0, dbn.SType.CONTINUOUS, dbn.SType.INSTRUMENT_ID, kind,
                        symbols=[symbol], partial=[], not_found=[], mappings=[mapping], end=t1)
    raw = bytes(meta.encode())
    for i in range(n_records):
        ts = t0 + i * 60 * 10**9
        if schema == "ohlcv-1m":
            record = dbn.OHLCVMsg(0x21, 1, INSTRUMENT_ID, ts, 1, 2, 3, 4, 5)
        else:
            record = dbn.MBP1Msg(1, INSTRUMENT_ID, ts, 1, 1, dbn.Action.ADD, dbn.Side.BID, 0, ts)
        raw += bytes(record)
    Path(path).write_bytes(zstandard.ZstdCompressor().compress(raw))


class FakeMetadata:
    def __init__(self, price=e0_like_price, size=billable_for) -> None:  # noqa: ANN001
        self.price, self.size = price, size
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self._lock = threading.Lock()

    def get_cost(self, **kwargs: Any) -> float:
        with self._lock:
            self.calls.append(("get_cost", kwargs))
        return self.price(kwargs)

    def get_billable_size(self, **kwargs: Any) -> int:
        with self._lock:
            self.calls.append(("get_billable_size", kwargs))
        return self.size(kwargs)


class FakeTimeseries:
    def __init__(self, calls: list[dict[str, Any]], extra_records: int = 0,
                 fail: Exception | None = None, on_call=None) -> None:  # noqa: ANN001
        self.calls, self.extra, self.fail, self.on_call = calls, extra_records, fail, on_call

    def get_range(self, *, path: Path, **kwargs: Any) -> None:
        self.calls.append(kwargs)
        if self.on_call is not None:
            self.on_call(kwargs)
        if self.fail is not None:
            Path(path).write_bytes(b"half a file")
            raise self.fail
        write_dbn(Path(path), kwargs["schema"], kwargs["symbols"][0], kwargs["start"],
                  kwargs["end"], records_for(kwargs) + self.extra)


class RecordingNamespace:
    def __init__(self, hits: list[str]) -> None:
        self._hits = hits

    def __getattr__(self, name: str) -> Any:
        self._hits.append(name)
        return lambda *a, **k: "BILLABLE"


def fake_client(**timeseries: Any) -> SimpleNamespace:
    downloads: list[dict[str, Any]] = []
    hits: list[str] = []
    return SimpleNamespace(metadata=FakeMetadata(),
                           timeseries=FakeTimeseries(downloads, **timeseries),
                           batch=RecordingNamespace(hits), downloads=downloads, batch_hits=hits)


def quote_only_client() -> SimpleNamespace:
    hits: list[str] = []
    return SimpleNamespace(metadata=FakeMetadata(), timeseries=RecordingNamespace(hits),
                           batch=RecordingNamespace(hits), billable_hits=hits)


def gate(tmp_path: Path, session_cap_usd: float = 50.0) -> qu.LockedQuoteGate:
    return pu.e1_gate(ledger_path=tmp_path / "ledger.jsonl",
                      access_doc_path=tmp_path / "ACCESS.md", session_cap_usd=session_cap_usd)


def request(root: str, schema: str, start: str, end: str) -> pu.PlannedRequest:
    return pu.PlannedRequest(root, RequestParams("GLBX.MDP3", (f"{root}.v.0",), schema,
                                                 "continuous", start, end))


def mnq_requests() -> list[pu.PlannedRequest]:
    """Two MNQ ohlcv-1m chunks and MNQ's $4.14 mbp-1 day (split in two when bought)."""
    plan = pu.plan_requests(["MNQ"])
    return [plan[0], plan[1], next(r for r in plan if r.params.end.startswith("2026-02-11"))]


def no_sleep(_: float) -> None:
    return None


def _lines(path: Path) -> int:
    return len(path.read_text().splitlines()) if path.is_file() else 0


# ----------------------------------------------------------------- plan ----
def test_the_step1_plan_is_45_roots_times_15_chunks_plus_5_mbp1_days() -> None:
    # Arrange
    months = [f"{y}-{m:02d}-01" for y, m in
              [(2025, m) for m in range(4, 13)] + [(2026, m) for m in range(1, 7)]]

    # Act
    plan = pu.plan_requests()
    chunks = pu.ohlcv_chunks()

    # Assert
    assert len(months) == 15 and [s for s, _ in chunks] == months
    assert chunks[-1] == ("2026-06-01", "2026-06-21") and chunks[0] == ("2025-04-01", "2025-05-01")
    assert all(e == chunks[i + 1][0] for i, (_, e) in enumerate(chunks[:-1]))  # contiguous
    assert len(plan) == 45 * (15 + 5) == 900
    assert {r.root for r in plan} == set(pu.STEP1_ROOTS) and len(pu.STEP1_ROOTS) == 45
    for root in pu.STEP1_ROOTS:
        mine = [r for r in plan if r.root == root]
        assert [r.params.schema for r in mine] == ["ohlcv-1m"] * 15 + ["mbp-1"] * 5
        assert [(r.params.start, r.params.end) for r in mine[15:]] == pu.mbp1_windows()
    assert pu.mbp1_windows() == [qu.full_trade_date_window_utc(d) for d in qu.SAMPLE_DATES]
    assert pu.mbp1_windows()[0] == ("2025-05-13T22:00:00Z", "2025-05-14T21:00:00Z")
    assert plan[0].params.as_kwargs() == {
        "dataset": "GLBX.MDP3", "symbols": ["MNQ.v.0"], "schema": "ohlcv-1m",
        "stype_in": "continuous", "start": "2025-04-01", "end": "2025-05-01"}
    assert all(r.params.schema == "ohlcv-1m" for r in plan[:675])  # bars phase first
    assert all(r.depth == 0 for r in plan)


def test_the_step1_set_is_e0s_universe_minus_the_refused_roots() -> None:
    assert set(pu.STEP1_ROOTS) == set(qu.PRODUCTS_BY_ROOT) - {"PL", "MET", "NKD", "6M", "ES"}
    assert {qu.PRODUCTS_BY_ROOT[r].cluster for r in pu.STEP1_ROOTS} == {
        "K1", "K2", "K3", "K4", "K5", "K6", "K7"}


@pytest.mark.parametrize("root", ["PL", "MET", "NKD", "6M", "ES", "MES", "ZZ", "mnq"])
def test_refused_roots_raise_before_any_vendor_call(tmp_path: Path, root: str) -> None:
    # Arrange
    client = fake_client()
    bad = pu.PlannedRequest(root, RequestParams("GLBX.MDP3", (f"{root}.v.0",), "ohlcv-1m",
                                                "continuous", "2025-04-01", "2025-05-01"))
    good = pu.plan_requests(["MNQ"])[:1]

    # Act / Assert: the six named refusals say so; any other root is outside the set.
    named = "is refused for step 1" if root in pu.REFUSED_ROOTS else "not in the 45-contract"
    with pytest.raises(pu.RefusedRootError, match=named):
        pu.symbol_for(root)
    with pytest.raises(pu.RefusedRootError):
        pu.plan_requests(["MNQ", root])
    with pytest.raises(pu.RefusedRootError):
        pu.run_buy(client, gate(tmp_path), [*good, bad], root=tmp_path / "v", log=print)
    with pytest.raises(pu.RefusedRootError):
        pu.run_quote_only(client, gate(tmp_path), [*good, bad], log=print)
    assert client.metadata.calls == [] and client.downloads == []
    assert read_entries(tmp_path / "ledger.jsonl") == []


def test_a_request_whose_symbol_does_not_match_its_root_is_refused() -> None:
    mismatched = pu.PlannedRequest("MNQ", RequestParams("GLBX.MDP3", ("ES.v.0",), "ohlcv-1m",
                                                        "continuous", "2025-04-01", "2025-05-01"))
    with pytest.raises(pu.RefusedRootError):
        pu.check_request(mismatched)


# ----------------------------------------------------------- date guard ----
BAD_WINDOWS = [
    ("2025-03-31T22:00:00Z", "2025-04-01T21:00:00Z"),  # touches trade date 2025-03-31
    ("2025-03-01", "2025-04-01"),  # holdout 2's last chunk
    ("2024-02-01", "2024-03-02"),  # touches 2024-03-01
    ("2024-06-01", "2024-07-01"),  # inside holdout 2
    ("2024-02-29T23:00:00Z", "2024-03-01T00:01:00Z"),
    ("2023-01-01", "2023-02-01"),  # before the research window
    ("2026-06-01", "2026-06-22"),  # ends after 2026-06-21T00:00Z
    ("2026-06-20T22:00:00Z", "2026-06-21T00:01:00Z"),
    ("2026-06-21", "2026-06-22"),  # starts at the cutoff
    ("2026-06-21T00:00:00Z", "2026-06-21T22:00:00Z"),
    ("2026-07-01", "2026-08-01"),  # holdout 1
    ("2025-05-01", "2025-05-01"),  # empty
    ("2025-06-01", "2025-05-01"),  # inverted
    ("2025-05-13T22:00Z", "2025-05-14T21:00:00Z"),  # not canonical
]


@pytest.mark.parametrize("start,end", BAD_WINDOWS)
def test_the_date_guard_refuses_before_any_vendor_call(tmp_path: Path, start: str,
                                                       end: str) -> None:
    # Arrange: a valid request first, the bad one last; the plan is checked as a whole.
    client = fake_client()
    requests = [pu.plan_requests(["MNQ"])[0], request("MNQ", "mbp-1", start, end)]

    # Act / Assert
    with pytest.raises(pu.DateGuardError):
        pu.check_window(start, end)
    with pytest.raises(pu.DateGuardError):
        pu.run_buy(client, gate(tmp_path), requests, root=tmp_path / "v", log=print)
    with pytest.raises(pu.DateGuardError):
        pu.run_quote_only(client, gate(tmp_path), requests, log=print)
    assert client.metadata.calls == [] and client.downloads == []
    assert read_entries(tmp_path / "ledger.jsonl") == []


@pytest.mark.parametrize("start,end", BAD_WINDOWS[:5])
def test_windows_touching_the_embargo_and_holdout_2_name_it(start: str, end: str) -> None:
    with pytest.raises(pu.DateGuardError, match="overlaps the embargo and holdout 2"):
        pu.check_window(start, end)


@pytest.mark.parametrize("start,end", BAD_WINDOWS[6:11])
def test_windows_at_or_after_the_cutoff_name_it(start: str, end: str) -> None:
    with pytest.raises(pu.DateGuardError, match="at or after 2026-06-21T00:00:00Z"):
        pu.check_window(start, end)


@pytest.mark.parametrize("start,end", [
    ("2025-04-01", "2025-05-01"), ("2026-06-01", "2026-06-21"),
    ("2025-05-13T22:00:00Z", "2025-05-14T21:00:00Z"),
    ("2025-04-01T00:00:00Z", "2026-06-21T00:00:00Z"),
])
def test_the_date_guard_admits_the_research_window_edges(start: str, end: str) -> None:
    pu.check_window(start, end)  # no raise


# ---------------------------------------------------------------- split ----
def _assert_tiles(pieces: list[pu.PlannedRequest], start: str, end: str) -> None:
    assert pieces[0].params.start == start and pieces[-1].params.end == end
    for left, right in zip(pieces, pieces[1:], strict=False):
        assert left.params.end == right.params.start  # contiguous, no gap, no overlap
    for piece in pieces:
        for bound in (piece.params.start, piece.params.end):
            assert qu.parse_utc(bound).second == 0  # whole minutes
        assert qu.parse_utc(piece.params.start) < qu.parse_utc(piece.params.end)


def test_split_pieces_are_contiguous_cover_the_window_and_fit_the_cap(tmp_path: Path) -> None:
    # Arrange: MNQ mbp-1 on 2026-02-11 at $4.14 (E.0), and an $11.00 day that needs quarters.
    parent = request("MNQ", "mbp-1", "2026-02-10T23:00:00Z", "2026-02-11T22:00:00Z")
    view = SimpleNamespace(metadata=FakeMetadata())
    dear = SimpleNamespace(metadata=FakeMetadata(price=lambda kw: 11.0 * _hours(kw) / 23))

    # Act
    halves = pu.quote_tree(parent, view, gate(tmp_path))
    quarters = pu.quote_tree(parent, dear, gate(tmp_path))

    # Assert
    assert [p.request.params.end for p in halves] == ["2026-02-11T10:30:00Z",
                                                       "2026-02-11T22:00:00Z"]
    for tree, depth in ((halves, 1), (quarters, 2)):
        assert all(p.status == "ok" and p.usd <= config.E1_REQUEST_CAP_USD for p in tree)
        assert all(p.request.depth == depth for p in tree)
        assert {p.parent_key for p in tree} == {parent.key}
        _assert_tiles([p.request for p in tree], parent.params.start, parent.params.end)
    assert len(quarters) == 4
    assert sum(p.usd for p in halves) == pytest.approx(4.14)


def test_the_split_midpoint_rounds_down_to_the_whole_minute() -> None:
    assert pu.split_window("2025-05-01T00:00:00Z", "2025-05-01T00:03:00Z") == (
        ("2025-05-01T00:00:00Z", "2025-05-01T00:01:00Z"),
        ("2025-05-01T00:01:00Z", "2025-05-01T00:03:00Z"))
    assert pu.split_window("2025-04-01", "2025-05-01") == (
        ("2025-04-01", "2025-04-16T00:00:00Z"), ("2025-04-16T00:00:00Z", "2025-05-01"))
    with pytest.raises(pu.SplitRefusedError):
        pu.split_window("2025-05-01T00:00:00Z", "2025-05-01T00:01:00Z")


def test_the_split_depth_limit_refuses(tmp_path: Path) -> None:
    # Arrange: $10.00 whatever the window, so no piece ever fits under $3.00.
    parent = request("MNQ", "mbp-1", "2026-02-10T23:00:00Z", "2026-02-11T22:00:00Z")
    client = fake_client()
    client.metadata = FakeMetadata(price=lambda kw: 10.0)
    g = gate(tmp_path)

    # Act
    tree = pu.quote_tree(parent, SimpleNamespace(metadata=client.metadata), g)

    # Assert: 16 pieces at depth 4, every one refused; the buy path raises at the first.
    assert len(tree) == 2 ** pu.MAX_SPLIT_DEPTH
    assert all(p.status == "split_refused" and p.request.depth == 4 for p in tree)
    _assert_tiles([p.request for p in tree], parent.params.start, parent.params.end)
    with pytest.raises(pu.SplitRefusedError):
        pu.split_request(tree[0].request)
    with pytest.raises(pu.SplitRefusedError):
        pu.run_buy(client, g, [parent], root=tmp_path / "v", log=print, sleep=no_sleep)
    assert client.downloads == []
    assert {e["event"] for e in read_entries(g.ledger_path)} == {"quote"}


# ------------------------------------------------------------ quote-only ----
def test_quote_only_makes_no_billable_call_and_writes_the_summary(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # Arrange
    real = (_lines(config.LEDGER_PATH), config.ACCESS_DOC_PATH.stat().st_size
            if config.ACCESS_DOC_PATH.exists() else 0)
    client = quote_only_client()
    logged: list[str] = []
    summary_path = tmp_path / "reports" / "stage_e1_quote_summary.json"

    # Act
    rc = pu.main(["--quote-only"], key_loader=lambda: "SECRET-KEY-DO-NOT-PRINT",
                 gate_factory=lambda: gate(tmp_path, session_cap_usd=0.0),
                 client_factory=lambda key: client, summary_path=summary_path,
                 log=logged.append)

    # Assert: nothing billable was touched, and a download attempt now raises.
    assert rc == 0
    assert client.billable_hits == []
    assert isinstance(client.timeseries, qu.ForbiddenNamespace)
    with pytest.raises(RuntimeError, match="forbidden"):
        client.timeseries.get_range(dataset="GLBX.MDP3")
    with pytest.raises(RuntimeError, match="forbidden"):
        client.batch.submit_job()
    entries = read_entries(tmp_path / "ledger.jsonl")
    assert len(entries) == 900 + 4  # two expensive MNQ days quoted whole, then as halves
    assert {(e["event"], e["usd"], e["account"], e["session_id"]) for e in entries} == {
        ("quote", 0.0, "acct-2", "stage-E.1-2026-09-24")}
    summary = json.loads(summary_path.read_text())
    counts = summary["counts"]
    assert (counts["planned_requests"], counts["pieces"], counts["requests_split"],
            counts["split_pieces"], counts["max_depth"]) == (900, 902, 2, 4, 1)
    assert summary["complete"] and counts["quote_failed"] == counts["split_refused"] == 0
    assert summary["largest_piece"]["usd"] <= 3.00
    assert summary["largest_piece"]["root"] == "MNQ" and summary["account"] == "acct-2"
    assert len(summary["per_root"]) == 45 and set(summary["per_schema"]) == {"ohlcv-1m", "mbp-1"}
    assert set(summary["per_cluster"]) == {"K1", "K2", "K3", "K4", "K5", "K6", "K7"}
    mnq = summary["per_root"]["MNQ"]
    assert (mnq["requests"], mnq["pieces"], mnq["cluster"]) == (20, 22, "K1")
    assert sum(b["requests"] for b in summary["per_cluster"].values()) == 900
    total = sum(b["usd"] for b in summary["per_root"].values())
    assert summary["total_usd"] == pytest.approx(total)
    assert summary["total_usd"] == pytest.approx(
        sum(b["usd"] for b in summary["per_schema"].values()))
    out = capsys.readouterr()
    everything = "\n".join(logged) + out.out + out.err + summary_path.read_text()
    assert "SECRET-KEY-DO-NOT-PRINT" not in everything
    assert "account acct-2 (cap $125.00" in logged[0] and "request cap $3.00" in logged[0]
    assert (_lines(config.LEDGER_PATH), config.ACCESS_DOC_PATH.stat().st_size
            if config.ACCESS_DOC_PATH.exists() else 0) == real


def test_quote_only_lists_failed_and_refused_pieces_and_marks_it_incomplete(tmp_path: Path) -> None:
    # Arrange: one request's pricing fails, another never fits under the cap.
    def price(kw: dict[str, Any]) -> float:
        if kw["symbols"] == ["ZN.v.0"]:
            raise RuntimeError("metadata down")
        return 10.0 if kw["symbols"] == ["GC.v.0"] else 0.01

    client = quote_only_client()
    client.metadata = FakeMetadata(price=price)
    requests = [request("ZN", "ohlcv-1m", "2025-04-01", "2025-05-01"),
                request("GC", "ohlcv-1m", "2025-04-01", "2025-05-01"),
                request("CL", "ohlcv-1m", "2025-04-01", "2025-05-01")]

    # Act
    g = gate(tmp_path)
    summary = pu.build_summary(pu.run_quote_only(client, g, requests, log=print, sleep=no_sleep), g)

    # Assert
    assert not summary["complete"]
    assert summary["counts"]["quote_failed"] == 1 and summary["counts"]["split_refused"] == 16
    assert summary["total_usd"] == pytest.approx(0.01)
    assert summary["per_root"]["GC"]["requests"] == 1 and summary["per_root"]["GC"]["usd"] == 0.0


def test_buy_refuses_while_the_session_cap_is_zero(tmp_path: Path) -> None:
    called: list[str] = []
    rc = pu.main(["--buy"], key_loader=lambda: called.append("key") or "k",
                 gate_factory=lambda: pu.e1_gate(ledger_path=tmp_path / "l.jsonl",
                                                 access_doc_path=tmp_path / "A.md",
                                                 session_cap_usd=0.0),  # E.1 Task 6 set the real cap
                 client_factory=lambda key: called.append("client"), log=print)
    assert rc == pu.RC_REFUSED and called == []
    with pytest.raises(BudgetRefusedError):
        pu.run_buy(fake_client(), gate(tmp_path, 0.0), [], root=tmp_path / "v", log=print)
    with pytest.raises(BudgetRefusedError):
        pu.run_buy(fake_client(), pu.e1_gate(ledger_path=tmp_path / "l.jsonl",
                                             session_cap_usd=120.01), [], log=print)


def test_the_e1_gate_is_acct_2_with_the_e1_caps(tmp_path: Path) -> None:
    g = pu.e1_gate(ledger_path=tmp_path / "l.jsonl", access_doc_path=tmp_path / "A.md")
    assert (g.session_id, g.account_id, g.account_cap_usd) == (
        "stage-E.1-2026-09-24", "acct-2", 125.00)
    assert (g.request_cap_usd, g.session_cap_usd, g.external_ledger_paths) == (3.00, 113.48, ())  # session cap set in E.1 Task 6


# ------------------------------------------------------------------ buy ----
def test_buy_quotes_gates_commits_downloads_checks_and_settles_each_piece(tmp_path: Path) -> None:
    # Arrange: record the ledger length at the moment each download starts.
    g = gate(tmp_path)
    at_download: list[int] = []
    client = fake_client(on_call=lambda kw: at_download.append(_lines(g.ledger_path)))
    root = tmp_path / "vendor"

    # Act
    done = pu.run_buy(client, g, mnq_requests(), root=root, log=print, sleep=no_sleep)

    # Assert
    assert [d["action"] for d in done] == ["bought"] * 4  # 2 chunks + the day as 2 halves
    events = [e["event"] for e in read_entries(g.ledger_path)]
    assert events == (["quote", "commit", "settle"] * 2 + ["quote"]
                      + ["quote", "commit", "settle"] * 2)
    assert at_download == [2, 5, 9, 12]  # quote + commit already on disk each time
    assert {e["account"] for e in read_entries(g.ledger_path)} == {"acct-2"}
    names = sorted(Path(d["path"]).name for d in done if "mbp-1" in d["path"])
    assert names == ["range=2026-02-10T230000Z_2026-02-11T103000Z.dbn.zst",
                     "range=2026-02-11T103000Z_2026-02-11T220000Z.dbn.zst"]
    first = Path(done[0]["path"])
    assert first == adapter.raw_path("MNQ.v.0", "ohlcv-1m", "2025-04-01", "2025-05-01", root)
    for d in done:
        assert not Path(d["path"]).stat().st_mode & 0o222, "raw file must be read-only"
    assert not list(root.rglob("*.partial"))
    settles = [e for e in read_entries(g.ledger_path) if e["event"] == "settle"]
    assert all(e["actual_usd"] == e["quoted_usd"] for e in settles)
    assert all("EXCEEDS" not in e["note"] for e in settles)
    assert g.session_spent_usd() == pytest.approx(sum(e["quoted_usd"] for e in settles))
    assert client.batch_hits == [] and isinstance(client.batch, qu.ForbiddenNamespace)


def test_new_ledger_lines_carry_account_acct_2(tmp_path: Path) -> None:
    g = gate(tmp_path)
    pu.run_buy(fake_client(), g, mnq_requests()[:1], root=tmp_path / "v", log=print,
               sleep=no_sleep)
    pu.run_quote_only(quote_only_client(), g, mnq_requests()[1:2], log=print, sleep=no_sleep)
    entries = read_entries(g.ledger_path)
    assert len(entries) == 4 and all(e["account"] == "acct-2" for e in entries)


def test_resume_skips_settled_requests_without_quoting_them(tmp_path: Path) -> None:
    # Arrange: a first run buys everything, including the two halves of the split day.
    g, root = gate(tmp_path), tmp_path / "vendor"
    pu.run_buy(fake_client(), g, mnq_requests(), root=root, log=print, sleep=no_sleep)
    before = _lines(g.ledger_path)
    again = fake_client()

    # Act
    done = pu.run_buy(again, g, mnq_requests(), root=root, log=print, sleep=no_sleep)

    # Assert
    assert [d["action"] for d in done] == ["skipped"] * 4
    assert again.metadata.calls == [] and again.downloads == []
    assert _lines(g.ledger_path) == before


def test_resume_buys_only_the_missing_half_of_a_split_window(tmp_path: Path) -> None:
    # Arrange: the first run stops at the second half of the split day (download fails).
    g, root = gate(tmp_path), tmp_path / "vendor"
    day = mnq_requests()[2]
    calls = {"n": 0}

    def fail_second(kw: dict[str, Any]) -> None:
        calls["n"] += 1
        if calls["n"] == 2:
            raise ConnectionError("dropped")

    with pytest.raises(pu.DownloadError):
        pu.run_buy(fake_client(on_call=fail_second), g, [day], root=root, log=print,
                   sleep=no_sleep)
    again = fake_client()

    # Act
    done = pu.run_buy(again, g, [day], root=root, log=print, sleep=no_sleep)

    # Assert: the parent is not re-quoted; only the second half is quoted and bought.
    assert [d["action"] for d in done] == ["skipped", "bought"]
    assert [kw["start"] for _, kw in again.metadata.calls] == ["2026-02-11T10:30:00Z"] * 2
    assert [kw["start"] for kw in again.downloads] == ["2026-02-11T10:30:00Z"]


def test_resume_names_a_file_without_a_settled_line(tmp_path: Path) -> None:
    # Arrange
    g, root = gate(tmp_path), tmp_path / "vendor"
    stray = pu.target_path(mnq_requests()[0].params, root)
    stray.parent.mkdir(parents=True)
    stray.write_bytes(b"not settled")
    client = fake_client()

    # Act / Assert
    with pytest.raises(pu.ResumeStateError, match="without a settled line"):
        pu.run_buy(client, g, mnq_requests(), root=root, log=print)
    with pytest.raises(pu.ResumeStateError, match="no settled ledger line"):
        pu.is_done(mnq_requests()[0], stray, set())
    assert stray.read_bytes() == b"not settled"  # never deleted
    assert client.metadata.calls == [] and client.downloads == []


def test_resume_names_a_settled_line_without_a_file(tmp_path: Path) -> None:
    # Arrange
    g, root = gate(tmp_path), tmp_path / "vendor"
    done = pu.run_buy(fake_client(), g, mnq_requests()[:1], root=root, log=print, sleep=no_sleep)
    gone = Path(done[0]["path"])
    gone.chmod(0o644)
    gone.unlink()
    client = fake_client()

    # Act / Assert
    with pytest.raises(pu.ResumeStateError, match="settled line"):
        pu.run_buy(client, g, mnq_requests()[:1], root=root, log=print)
    assert client.metadata.calls == [] and client.downloads == []


def test_a_gate_refusal_stops_the_run_at_that_request(tmp_path: Path) -> None:
    # Arrange: each chunk costs about $0.10; the session cap admits one.
    g, client = gate(tmp_path, session_cap_usd=0.15), fake_client()

    # Act / Assert
    with pytest.raises(BudgetRefusedError, match="session cap"):
        pu.run_buy(client, g, mnq_requests(), root=tmp_path / "v", log=print, sleep=no_sleep)
    assert len(client.downloads) == 1
    assert [e["event"] for e in read_entries(g.ledger_path)] == [
        "quote", "commit", "settle", "quote", "refused"]
    assert "acct-2" in g.access_doc_path.read_text()


def test_a_failed_download_stops_the_run_with_a_named_error(tmp_path: Path) -> None:
    g, root = gate(tmp_path), tmp_path / "vendor"
    client = fake_client(fail=ConnectionError("dropped"))
    with pytest.raises(pu.DownloadError, match="commit stays"):
        pu.run_buy(client, g, mnq_requests(), root=root, log=print, sleep=no_sleep)
    assert len(client.downloads) == 1
    assert [e["event"] for e in read_entries(g.ledger_path)] == ["quote", "commit"]
    assert not list(root.rglob("*.dbn.zst*"))  # the partial file is gone too


def test_a_delivery_larger_than_the_quote_settles_pro_rata_and_stops(tmp_path: Path) -> None:
    # Arrange: the fake delivers one record more than it quoted.
    g, client = gate(tmp_path), fake_client(extra_records=1)

    # Act / Assert
    with pytest.raises(pu.DeliveryCheckError, match="Run stopped"):
        pu.run_buy(client, g, mnq_requests(), root=tmp_path / "v", log=print, sleep=no_sleep)
    settle = read_entries(g.ledger_path)[-1]
    assert settle["event"] == "settle" and "DELIVERED EXCEEDS QUOTE" in settle["note"]
    n = records_for(mnq_requests()[0].params.as_kwargs())
    assert settle["actual_usd"] == pytest.approx(settle["quoted_usd"] * (n + 1) / n)
    assert len(client.downloads) == 1


# ---------------------------------------------------------------- files ----
def test_target_paths_follow_the_mes_layout_and_are_colon_free(tmp_path: Path) -> None:
    monthly = RequestParams("GLBX.MDP3", ("MNQ.v.0",), "ohlcv-1m", "continuous",
                            "2025-04-01", "2025-05-01")
    day = RequestParams("GLBX.MDP3", ("6E.v.0",), "mbp-1", "continuous",
                        "2025-05-13T22:00:00Z", "2025-05-14T21:00:00Z")
    assert pu.target_path(monthly, tmp_path) == adapter.raw_path(
        "MNQ.v.0", "ohlcv-1m", "2025-04-01", "2025-05-01", tmp_path)
    path = pu.target_path(day, tmp_path)
    assert path == tmp_path / "GLBX.MDP3" / "mbp-1" / "6E_v_0" / (
        "range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst")
    assert ":" not in path.name
    assert pu.parse_target_name(path.name) == ("2025-05-13T22:00:00Z", "2025-05-14T21:00:00Z")
    assert pu.parse_target_name("range=2025-04-01_2025-05-01.dbn.zst") == (
        "2025-04-01", "2025-05-01")
    assert pu.parse_target_name("range=2025-04-01_2025-05-01.dbn.zst.partial") is None


def test_inventory_reports_counts_times_ids_schema_and_sha_and_nothing_else(
    tmp_path: Path
) -> None:
    # Arrange
    bars, book = tmp_path / "bars.dbn.zst", tmp_path / "book.dbn.zst"
    write_dbn(bars, "ohlcv-1m", "MNQ.v.0", "2025-04-01", "2025-05-01", 3)
    write_dbn(book, "mbp-1", "MNQ.v.0", "2025-05-13T22:00:00Z", "2025-05-14T21:00:00Z", 2)

    # Act
    inv, inv_book = pu.inventory(bars), pu.inventory(book)

    # Assert
    assert [f.name for f in dataclasses.fields(pu.FileInventory)] == [
        "record_count", "first_ts_event_utc", "last_ts_event_utc", "symbols",
        "instrument_ids", "schema", "sha256"]
    assert dataclasses.asdict(inv) == {
        "record_count": 3, "first_ts_event_utc": "2025-04-01T00:00:00.000000000Z",
        "last_ts_event_utc": "2025-04-01T00:02:00.000000000Z", "symbols": ("MNQ.v.0",),
        "instrument_ids": (str(INSTRUMENT_ID),), "schema": "ohlcv-1m",
        "sha256": hashlib.sha256(bars.read_bytes()).hexdigest()}
    assert (inv_book.record_count, inv_book.schema) == (2, "mbp-1")
    assert inv_book.first_ts_event_utc == "2025-05-13T22:00:00.000000000Z"
    assert adapter.delivered_record_bytes(bars) == 3 * 56  # the record-byte check's decode
