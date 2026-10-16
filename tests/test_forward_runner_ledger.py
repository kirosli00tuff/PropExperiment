"""forward.ledger (E.22, ForwardRunnerCoder): chain, refusals, tamper detection."""

from __future__ import annotations

import json

import pytest

from forward.ledger import (
    GENESIS_SHA256,
    Ledger,
    LedgerError,
    LedgerIntegrityError,
    LedgerOrderError,
    canonical_json,
    record_sha256,
    verify,
)


def _payload(day: str, pnl: float = 1.5) -> dict:
    return {"date": day, "net_pnl": pnl, "prices": {"MNQ": {"MNQZ26": 100.25}}, "flags": []}


@pytest.fixture
def ledger(tmp_path):
    led = Ledger(tmp_path / "l.jsonl")
    for k, day in enumerate(("2026-11-02", "2026-11-03", "2026-11-04")):
        led.append(_payload(day, float(k)))
    return led


def test_chain_links_and_verifies(ledger):
    records = ledger.records()
    assert [r["date"] for r in records] == ["2026-11-02", "2026-11-03", "2026-11-04"]
    assert records[0]["prev_record_sha256"] == GENESIS_SHA256
    for prev, cur in zip(records, records[1:], strict=False):
        assert cur["prev_record_sha256"] == prev["record_sha256"]
    for r in records:
        assert r["record_sha256"] == record_sha256(r)
    report = verify(ledger.path)
    assert report.ok and report.n_records == 3 and report.last_date == "2026-11-04"


def test_lines_are_canonical_json(ledger):
    for line in ledger.path.read_text(encoding="ascii").splitlines():
        assert canonical_json(json.loads(line)) == line


def test_rewrite_and_backwards_dates_are_refused(ledger):
    before = ledger.path.read_bytes()
    with pytest.raises(LedgerOrderError, match="already"):
        ledger.append(_payload("2026-11-04"))
    with pytest.raises(LedgerOrderError, match="already"):
        ledger.append(_payload("2026-11-03"))
    with pytest.raises(LedgerOrderError):
        ledger.append(_payload("2026-10-30"))
    assert ledger.path.read_bytes() == before


def test_payload_with_hash_fields_or_nan_is_refused(ledger):
    with pytest.raises(LedgerError):
        ledger.append({**_payload("2026-11-05"), "record_sha256": "x"})
    with pytest.raises(ValueError):
        ledger.append(_payload("2026-11-05", float("nan")))
    assert verify(ledger.path).n_records == 3


def _rewrite_line(path, index, mutate):
    lines = path.read_text(encoding="ascii").splitlines()
    lines[index] = mutate(lines[index])
    path.write_text("\n".join(lines) + "\n", encoding="ascii")


def test_tampered_value_is_detected(ledger):
    _rewrite_line(ledger.path, 1, lambda s: s.replace("100.25", "100.5"))
    report = verify(ledger.path)
    assert not report.ok and report.line == 2 and "record_sha256" in report.error
    with pytest.raises(LedgerIntegrityError):
        ledger.records()
    with pytest.raises(LedgerIntegrityError):
        ledger.append(_payload("2026-11-05"))


def test_rehashed_tamper_breaks_the_next_link(ledger):
    def rehash(line):
        rec = json.loads(line)
        rec["net_pnl"] = 1000.0
        rec["record_sha256"] = record_sha256(rec)
        return canonical_json(rec)

    _rewrite_line(ledger.path, 0, rehash)
    report = verify(ledger.path)
    assert not report.ok and report.line == 2 and "prev_record_sha256" in report.error


def test_deleted_line_and_reordered_lines_are_detected(ledger, tmp_path):
    lines = ledger.path.read_text(encoding="ascii").splitlines()
    gap = tmp_path / "gap.jsonl"
    gap.write_text("\n".join([lines[0], lines[2]]) + "\n", encoding="ascii")
    assert not verify(gap).ok
    swapped = tmp_path / "swap.jsonl"
    swapped.write_text("\n".join([lines[1], lines[0], lines[2]]) + "\n", encoding="ascii")
    assert not verify(swapped).ok


def test_truncated_tail_and_blank_lines_are_detected(ledger, tmp_path):
    text = ledger.path.read_text(encoding="ascii")
    cut = tmp_path / "cut.jsonl"
    cut.write_text(text[:-10], encoding="ascii")
    assert "truncated" in verify(cut).error
    blank = tmp_path / "blank.jsonl"
    blank.write_text(text.replace("\n", "\n\n", 1), encoding="ascii")
    assert not verify(blank).ok


def test_empty_or_absent_ledger_verifies_empty(tmp_path):
    report = verify(tmp_path / "none.jsonl")
    assert report.ok and report.n_records == 0
    assert Ledger(tmp_path / "none.jsonl").records() == []
