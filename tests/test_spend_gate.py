"""Spend gate + immutable raw storage, exercised with fake clients (no network, no spend)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from data import adapter
from data.spend_gate import (
    BudgetRefusedError,
    ExternalLedgerUnavailableError,
    RequestParams,
    SpendGate,
    decide,
    read_entries,
)

PARAMS = RequestParams("GLBX.MDP3", ("MES.v.0",), "ohlcv-1m", "continuous",
                       "2026-01-01", "2026-02-01")


class FakeMetadata:
    def __init__(self, usd: float | Exception) -> None:
        self.usd = usd

    def get_cost(self, **_: object) -> float:
        if isinstance(self.usd, Exception):
            raise self.usd
        return self.usd

    def get_billable_size(self, **_: object) -> int:
        return 56_000


class FakeTimeseries:
    def __init__(self, calls: list[str]) -> None:
        self.calls = calls

    def get_range(self, *, path: Path, **_: object) -> None:
        self.calls.append("download")
        Path(path).write_bytes(b"dbn")


class FakeClient:
    def __init__(self, usd: float | Exception) -> None:
        self.calls: list[str] = []
        self.metadata = FakeMetadata(usd)
        self.timeseries = FakeTimeseries(self.calls)


@pytest.fixture
def gate(tmp_path: Path) -> SpendGate:
    external = tmp_path / "mlce_spend_ledger.jsonl"
    external.write_text(json.dumps({"usd": 82.12}) + "\n")
    return SpendGate(
        "test-session",
        ledger_path=tmp_path / "ledger" / "databento_spend.jsonl",
        external_ledger_paths=(external,),
        access_doc_path=tmp_path / "ACCESS.md",
    )


def test_decide_allows_exactly_reaching_a_cap_and_refuses_beyond() -> None:
    assert decide(5.0, 10.0, 50.0, session_cap_usd=15.0).allowed
    assert not decide(5.01, 10.0, 50.0, session_cap_usd=15.0).allowed
    assert decide(37.88, 0.0, 82.12, session_cap_usd=50.0, shared_cap_usd=120.0).allowed
    assert not decide(37.89, 0.0, 82.12, session_cap_usd=50.0, shared_cap_usd=120.0).allowed
    shared = decide(1.0, 0.0, 119.5, session_cap_usd=15.0, shared_cap_usd=120.0)
    assert not shared.allowed and shared.reason.startswith("shared account cap")


def test_session_cap_checked_before_shared_cap() -> None:
    both = decide(20.0, 0.0, 119.0, session_cap_usd=15.0, shared_cap_usd=120.0)
    assert both.reason.startswith("session cap")


def test_unpriced_request_is_refused() -> None:
    assert not decide(None, 0.0, 0.0).allowed


def test_quote_failure_refuses_and_documents(gate: SpendGate) -> None:
    client = FakeClient(RuntimeError("metadata down"))
    quote = gate.quote(client, PARAMS)
    with pytest.raises(BudgetRefusedError):
        gate.authorize(PARAMS, quote)
    events = [e["event"] for e in read_entries(gate.ledger_path)]
    assert events == ["quote", "refused"]
    assert "unpriceable" in gate.access_doc_path.read_text()


def test_shared_cap_counts_external_ledger(gate: SpendGate) -> None:
    # External ledger 110.00 + quoted 10.50 = 120.50 > 120, while session 10.50 <= 15.
    for path in gate.external_ledger_paths:
        path.write_text(json.dumps({"usd": 110.0}) + "\n")
    client = FakeClient(10.5)
    with pytest.raises(BudgetRefusedError, match="shared account cap"):
        gate.authorize(PARAMS, gate.quote(client, PARAMS))
    note = gate.access_doc_path.read_text()
    assert "10.5" in note and '"start": "2026-01-01"' in note


def test_missing_external_ledger_closes_the_gate(tmp_path: Path) -> None:
    closed = SpendGate("s", ledger_path=tmp_path / "l.jsonl",
                       external_ledger_paths=(tmp_path / "missing.jsonl",),
                       access_doc_path=tmp_path / "A.md")
    with pytest.raises(ExternalLedgerUnavailableError):
        closed.shared_spent_usd()


def test_fetch_commits_before_download_then_settles(
    gate: SpendGate, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(adapter, "delivered_record_bytes", lambda _p: 56_000)
    client = FakeClient(0.1)
    ledger_lines: list[int] = []
    original = client.timeseries.get_range

    def spy(**kwargs: object) -> None:
        ledger_lines.append(len(read_entries(gate.ledger_path)))
        original(**kwargs)  # type: ignore[arg-type]

    client.timeseries.get_range = spy  # type: ignore[method-assign]
    target = adapter.fetch_range(gate, client, PARAMS, root=tmp_path / "vendor")
    entries = read_entries(gate.ledger_path)
    assert [e["event"] for e in entries] == ["quote", "commit", "settle"]
    assert ledger_lines == [2]  # quote + commit already on disk when the download ran
    assert gate.session_spent_usd() == pytest.approx(0.1)
    assert entries[-1]["actual_usd"] == 0.1
    assert entries[-1]["session_cumulative_usd"] == pytest.approx(0.1)
    assert entries[-1]["shared_cumulative_usd"] == pytest.approx(82.22)
    assert entries[1]["request"]["start"] == "2026-01-01"
    assert not (target.stat().st_mode & 0o222), "raw file must be read-only"


def test_existing_raw_file_refused_before_any_quote(gate: SpendGate, tmp_path: Path) -> None:
    root = tmp_path / "vendor"
    target = adapter.raw_path("MES.v.0", "ohlcv-1m", "2026-01-01", "2026-02-01", root)
    target.parent.mkdir(parents=True)
    target.write_bytes(b"paid-for")
    client = FakeClient(0.1)
    with pytest.raises(adapter.RawFileExistsError, match="REFUSED"):
        adapter.fetch_range(gate, client, PARAMS, root=root)
    assert target.read_bytes() == b"paid-for"
    assert client.calls == []
    assert read_entries(gate.ledger_path) == []


def test_session_cap_stops_a_second_request(
    gate: SpendGate, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(adapter, "delivered_record_bytes", lambda _p: 0)
    adapter.fetch_range(gate, FakeClient(10.0), PARAMS, root=tmp_path / "v")
    second = RequestParams("GLBX.MDP3", ("MES.v.0",), "ohlcv-1m", "continuous",
                           "2026-02-01", "2026-03-01")
    client = FakeClient(5.01)
    with pytest.raises(BudgetRefusedError, match="session cap"):
        adapter.fetch_range(gate, client, second, root=tmp_path / "v")
    assert client.calls == []  # never downloaded


def test_ledger_is_append_only(gate: SpendGate) -> None:
    client = FakeClient(0.2)
    gate.quote(client, PARAMS)
    first = gate.ledger_path.read_text()
    gate.quote(client, PARAMS)
    assert gate.ledger_path.read_text().startswith(first)


def test_roll_cycle_and_id_reuse() -> None:
    intervals = [
        {"d0": "2026-03-01", "d1": "2026-03-18", "s": "42003800"},
        {"d0": "2026-03-18", "d1": "2026-06-17", "s": "42005163"},
    ]
    raw = {
        "42003800": [{"d0": "2025-01-01", "d1": "2025-06-01", "s": "OTHER"},
                     {"d0": "2025-09-01", "d1": "2026-03-21", "s": "MESH6"}],
        "42005163": [{"d0": "2025-12-01", "d1": "2026-06-20", "s": "MESM6"}],
    }
    (roll,) = adapter.boundaries_from_intervals("MES.v.0", intervals, raw)
    assert (roll.from_raw_symbol, roll.to_raw_symbol) == ("MESH6", "MESM6")
    assert adapter.roll_cycle_violations([roll]) == []
    bad = adapter.RollBoundary("MES.v.0", "2026-03-18", 0, "1", "2", "MESH6", "MESU6")
    assert adapter.roll_cycle_violations([bad])


def test_delivery_larger_than_quote_is_charged_pessimistically(
    gate: SpendGate, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Quote $0.10 for 56,000 billable bytes; 84,000 delivered -> ledger $0.15.
    monkeypatch.setattr(adapter, "delivered_record_bytes", lambda _p: 84_000)
    adapter.fetch_range(gate, FakeClient(0.1), PARAMS, root=tmp_path / "v")
    settle = read_entries(gate.ledger_path)[-1]
    assert settle["actual_usd"] == pytest.approx(0.15)
    assert "DELIVERED EXCEEDS QUOTE" in settle["note"]
    assert gate.session_spent_usd() == pytest.approx(0.15)
