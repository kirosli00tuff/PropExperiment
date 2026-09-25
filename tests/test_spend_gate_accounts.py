"""Stage E.1: per-account spend in data/spend_gate.py (registry in data/config.py).

Temporary ledgers only; no network. Legacy ledger lines (no "account" field) are acct-1.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from data import config
from data import spend_gate as sg
from data.pull_mes import RequestCappedGate
from data.spend_gate import (
    BudgetRefusedError,
    ExternalLedgerUnavailableError,
    Quote,
    RequestParams,
    SpendGate,
    UnknownAccountError,
    read_entries,
)

PARAMS = RequestParams("GLBX.MDP3", ("MNQ.v.0",), "ohlcv-1m", "continuous",
                       "2026-01-01", "2026-02-01")


class FakeMetadata:
    def __init__(self, usd: float) -> None:
        self.usd = usd

    def get_cost(self, **_: object) -> float:
        return self.usd

    def get_billable_size(self, **_: object) -> int:
        return 56_000


class FakeClient:
    def __init__(self, usd: float) -> None:
        self.metadata = FakeMetadata(usd)


def _write_ledger(path: Path, lines: list[dict[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(line) + "\n" for line in lines))
    return path


def _line(usd: float, session: str = "old-session", account: str | None = None
          ) -> dict[str, Any]:
    line: dict[str, Any] = {"event": "commit", "session_id": session, "usd": usd}
    if account is not None:
        line["account"] = account
    return line


@pytest.fixture
def external(tmp_path: Path) -> Path:
    return _write_ledger(tmp_path / "mlce_ledger.jsonl", [{"usd": 82.12}])


def _acct2(tmp_path: Path, **kwargs: Any) -> SpendGate:
    return SpendGate("e1-test", ledger_path=tmp_path / "ledger.jsonl",
                     access_doc_path=tmp_path / "ACCESS.md", account="acct-2", **kwargs)


# --------------------------------------------------------------- registry ----
def test_registry_holds_both_accounts_with_their_caps_and_ledgers() -> None:
    # Arrange / Act
    acct1, acct2 = config.ACCOUNTS["acct-1"], config.ACCOUNTS["acct-2"]

    # Assert
    assert (acct1.cap_usd, acct1.external_ledger_paths) == (120.00, config.EXTERNAL_LEDGER_PATHS)
    assert (acct2.cap_usd, acct2.external_ledger_paths) == (125.00, ())
    assert config.ACTIVE_ACCOUNT == "acct-2" and config.LEGACY_ACCOUNT_ID == "acct-1"
    assert config.SHARED_ACCOUNT_CAP_USD == 120.00 and config.SESSION_CAP_USD == 15.00
    assert (config.STAGE_E1_SESSION_ID, config.E1_REQUEST_CAP_USD) == ("stage-E.1-2026-09-24", 3.00)
    assert config.E1_SESSION_CAP_USD == 113.48 and config.E1_SESSION_CAP_MAX_USD == 120.00  # set in E.1 Task 6
    with pytest.raises(TypeError):
        config.ACCOUNTS["acct-3"] = acct2  # type: ignore[index]


def test_the_default_account_is_legacy_acct_1(tmp_path: Path, external: Path) -> None:
    gate = SpendGate("s", ledger_path=tmp_path / "l.jsonl", external_ledger_paths=(external,),
                     access_doc_path=tmp_path / "A.md")
    assert gate.account_id == "acct-1" and gate.shared_cap_usd == 120.00


# ----------------------------------------------------------------- totals ----
def test_per_account_totals_are_right_with_legacy_lines_present(
    tmp_path: Path, external: Path
) -> None:
    # Arrange: legacy 1.00 + explicit acct-1 2.00 (acct-1 = 3.00 local); acct-2 4.00 + 0.50.
    ledger = _write_ledger(tmp_path / "ledger.jsonl", [
        _line(1.00), _line(2.00, account="acct-1"), _line(4.00, "e1-test", "acct-2"),
        _line(0.50, "e1-test", "acct-2"), _line(0.0, "e1-test"),
    ])
    gate1 = SpendGate("s", ledger_path=ledger, external_ledger_paths=(external,),
                      access_doc_path=tmp_path / "A.md")
    gate2 = _acct2(tmp_path)

    # Act / Assert
    assert gate1.account_spent_usd() == pytest.approx(82.12 + 3.00)
    assert gate1.shared_spent_usd() == pytest.approx(82.12 + 3.00)
    assert gate2.account_spent_usd() == pytest.approx(4.50)
    assert gate2.shared_spent_usd() == pytest.approx(4.50)
    assert gate2.session_spent_usd() == pytest.approx(4.50)  # the session, whatever the account
    assert sg.account_committed_usd(read_entries(ledger), "acct-1") == pytest.approx(3.00)


def test_new_ledger_lines_carry_the_gate_account(tmp_path: Path, external: Path) -> None:
    # Arrange
    gate2 = _acct2(tmp_path)
    gate1 = SpendGate("s1", ledger_path=gate2.ledger_path, external_ledger_paths=(external,),
                      access_doc_path=tmp_path / "A.md")

    # Act
    q2 = gate2.quote(FakeClient(0.40), PARAMS)
    assert q2 is not None
    gate2.commit(q2)
    gate1.quote(FakeClient(0.10), PARAMS)

    # Assert
    entries = read_entries(gate2.ledger_path)
    assert [e["account"] for e in entries] == ["acct-2", "acct-2", "acct-1"]
    assert entries[1]["shared_cumulative_usd"] == pytest.approx(0.40)  # acct-2's own total
    assert entries[2]["shared_cumulative_usd"] == pytest.approx(82.12)  # acct-1: external only


def test_account_lines_are_appended_never_rewritten(tmp_path: Path) -> None:
    ledger = _write_ledger(tmp_path / "ledger.jsonl", [_line(1.00), _line(2.0, account="acct-2")])
    before = ledger.read_text()
    gate = _acct2(tmp_path)
    gate.quote(FakeClient(0.2), PARAMS)
    assert ledger.read_text().startswith(before)
    assert len(ledger.read_text().splitlines()) == 3


# ------------------------------------------------------------------- caps ----
def test_the_acct_2_cap_refuses_past_125(tmp_path: Path) -> None:
    # Arrange: acct-2 has 124.00 committed; legacy acct-1 lines do not count against it.
    _write_ledger(tmp_path / "ledger.jsonl", [_line(124.00, account="acct-2"), _line(50.0)])
    gate = _acct2(tmp_path, session_cap_usd=1000.0)

    # Act / Assert: 124.00 + 1.00 = 125.00 is allowed; 124.00 + 1.01 is not.
    assert gate.authorize(PARAMS, Quote(PARAMS, 1.00, 56)).allowed
    with pytest.raises(BudgetRefusedError, match="account cap acct-2"):
        gate.authorize(PARAMS, Quote(PARAMS, 1.01, 56))
    refused = read_entries(gate.ledger_path)[-1]
    assert (refused["event"], refused["account"]) == ("refused", "acct-2")
    assert "acct-2" in gate.access_doc_path.read_text()


def test_the_session_cap_refuses_on_acct_2(tmp_path: Path) -> None:
    _write_ledger(tmp_path / "ledger.jsonl", [_line(2.50, "e1-test", "acct-2")])
    gate = _acct2(tmp_path, session_cap_usd=3.00)
    with pytest.raises(BudgetRefusedError, match="session cap"):
        gate.authorize(PARAMS, Quote(PARAMS, 0.51, 56))


def test_the_request_cap_refuses_on_acct_2(tmp_path: Path) -> None:
    gate = RequestCappedGate("e1-test", request_cap_usd=3.00, session_cap_usd=100.0,
                             ledger_path=tmp_path / "l.jsonl", access_doc_path=tmp_path / "A.md",
                             account="acct-2")
    assert gate.authorize(PARAMS, Quote(PARAMS, 3.00, 56)).allowed
    with pytest.raises(BudgetRefusedError, match="per-request cap"):
        gate.authorize(PARAMS, Quote(PARAMS, 3.01, 56))


def test_a_cap_may_be_tightened_but_never_raised(tmp_path: Path) -> None:
    assert _acct2(tmp_path, shared_cap_usd=10.0).account_cap_usd == 10.0
    with pytest.raises(ValueError, match="never raise"):
        _acct2(tmp_path, shared_cap_usd=125.01)


# ------------------------------------------------------ fail-closed rules ----
def test_an_unknown_account_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(UnknownAccountError):
        SpendGate("s", ledger_path=tmp_path / "l.jsonl", account="acct-9")
    with pytest.raises(UnknownAccountError):
        sg.resolve_account("")


def test_a_ledger_line_on_an_unknown_account_fails_closed(tmp_path: Path) -> None:
    _write_ledger(tmp_path / "ledger.jsonl", [_line(1.0, account="acct-7")])
    with pytest.raises(UnknownAccountError):
        _acct2(tmp_path).account_spent_usd()


def test_acct_2_reads_no_external_ledger(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange: record every ledger file the gate reads; the acct-1 external path is irrelevant.
    read: list[Path] = []
    real_read = sg.read_entries
    monkeypatch.setattr(sg, "read_entries", lambda p: read.append(Path(p)) or real_read(p))
    gate = _acct2(tmp_path)

    # Act
    total = gate.account_spent_usd()

    # Assert
    assert gate.external_ledger_paths == () and total == 0.0
    assert read == [gate.ledger_path]
    with pytest.raises(ValueError, match="no external ledger"):
        _acct2(tmp_path, external_ledger_paths=(tmp_path / "x.jsonl",))


def test_acct_1_still_requires_its_external_ledger(tmp_path: Path) -> None:
    missing = SpendGate("s", ledger_path=tmp_path / "l.jsonl",
                        external_ledger_paths=(tmp_path / "missing.jsonl",),
                        access_doc_path=tmp_path / "A.md", account="acct-1")
    with pytest.raises(ExternalLedgerUnavailableError):
        missing.account_spent_usd()
    with pytest.raises(ExternalLedgerUnavailableError):
        SpendGate("s", ledger_path=tmp_path / "l.jsonl", external_ledger_paths=(),
                  account="acct-1")
