"""Harness v8 (Stage E.12): data/config.py's acct-2 cap, key strip and E.12 block; docs/ACCESS.md.

- ACCOUNT_2_CAP_USD = 249.67: acct-2's ledger spend at 2026-10-03 07:52 PDT (the first 17,400
  lines of the append-only ledger, sha256-pinned) plus the user's $125.00 top-up (V19), rounded
  DOWN to the cent.
- E.11 review C-10(b): require_databento_key returns the stripped key; nothing prints it.
- The Stage E.12 block sits after the E.5 block, the active step 2 names point at it, and the
  earlier blocks stay as they were. E12_SESSION_CAP_USD is set by the lead from the fresh quote,
  so (ruling R-A2-2) no test pins its value.
- C-10(a): docs/ACCESS.md names DATABENTO_API_KEY1 and DATABENTO_API_KEY2.

Fake key values only; the real key variables are deleted from the environment first and the
repo's .env is never read. The ledger is read, never printed or written.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path

import pytest

from data import config
from data.config import ACCOUNT_1_ID, ACCOUNT_2_ID, require_databento_key
from data.spend_gate import account_committed_usd

KEY_VARS = ("DATABENTO_API_KEY1", "DATABENTO_API_KEY2", "DATABENTO_API_KEY")
FAKE = "fake-v8-key-not-real"
LEDGER_LINES_AT_RAISE = 17_400
LEDGER_SHA256_AT_RAISE = "0b5466c4366ca9eaba7e10525545631c83e97c1184a7e745d5ed8ad47a9fe957"
ACCT2_SPENT_AT_RAISE = 124.673761  # account_committed_usd over those lines, to 6 decimals
TOPUP_2026_10_02_USD = 125.00  # V19


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """No real key variable from the developer's shell reaches a test."""
    for name in KEY_VARS:
        monkeypatch.delenv(name, raising=False)


def _ledger_prefix(lines: int) -> bytes:
    """The ledger's first ``lines`` lines as bytes (the ledger is append-only)."""
    raw = config.LEDGER_PATH.read_bytes()
    cut = 0
    for _ in range(lines):
        cut = raw.index(b"\n", cut) + 1
    return raw[:cut]


# ------------------------------------------------------------- the acct-2 cap ----
def test_the_acct2_cap_is_the_ledger_spend_plus_the_topup_rounded_down_to_the_cent() -> None:
    # Arrange
    funds = ACCT2_SPENT_AT_RAISE + TOPUP_2026_10_02_USD

    # Act
    floored = math.floor(round(funds * 100, 6)) / 100

    # Assert: 124.673761 + 125.00 = 249.673761 -> 249.67, never above the funds
    assert funds == pytest.approx(249.673761, abs=1e-9)
    assert floored == 249.67 == config.ACCOUNT_2_CAP_USD
    assert funds >= config.ACCOUNT_2_CAP_USD
    assert config.ACCOUNTS[ACCOUNT_2_ID].cap_usd == config.ACCOUNT_2_CAP_USD
    assert config.ACCOUNTS[ACCOUNT_1_ID].cap_usd == config.SHARED_ACCOUNT_CAP_USD == 120.00


def test_the_acct2_spend_is_recomputed_from_the_pinned_ledger_prefix() -> None:
    # Arrange: the 17,400 lines the cap was computed from (later lines only append)
    prefix = _ledger_prefix(LEDGER_LINES_AT_RAISE)
    entries = [json.loads(line) for line in prefix.decode("utf-8").splitlines()
               if line.strip()]

    # Act
    spent = account_committed_usd(entries, ACCOUNT_2_ID)

    # Assert
    assert hashlib.sha256(prefix).hexdigest() == LEDGER_SHA256_AT_RAISE
    assert len(entries) == LEDGER_LINES_AT_RAISE
    assert round(spent, 6) == ACCT2_SPENT_AT_RAISE


# ----------------------------------------------------------------- key strip ----
@pytest.mark.parametrize("padded", [f"  {FAKE}  ", f"\t{FAKE}\n", f" {FAKE}"])
def test_a_whitespace_padded_key_comes_back_stripped_and_is_never_printed(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
        padded: str) -> None:
    # Arrange: the variable is set in the environment; the .env path does not exist
    monkeypatch.setenv("DATABENTO_API_KEY2", padded)

    # Act
    key = require_databento_key(env_file=tmp_path / ".env", account=ACCOUNT_2_ID)

    # Assert
    assert key == FAKE and key == key.strip()
    out = capsys.readouterr()
    assert FAKE not in out.out + out.err


def test_a_padded_key_in_the_env_file_comes_back_stripped(
        tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    # Arrange
    env = tmp_path / ".env"
    env.write_text(f"DATABENTO_API_KEY1 =   {FAKE}   \n", encoding="utf-8")

    # Act
    key = require_databento_key(env_file=env, account=ACCOUNT_1_ID)

    # Assert
    assert key == FAKE
    out = capsys.readouterr()
    assert FAKE not in out.out + out.err


# ------------------------------------------------------------ the E.12 block ----
def test_the_e12_block_and_the_repointed_step2_policy() -> None:
    # Assert: the block's fixed values (the session cap is the lead's, set from the quote)
    assert config.STAGE_E12_SESSION_ID == "stage-E.12-2026-10-03"
    assert config.E12_REQUEST_CAP_USD == 3.00 == config.E5_REQUEST_CAP_USD  # D13's per request
    assert config.STEP2_TRAINING_WINDOW_ONLY is True
    assert config.E12_SESSION_CAP_USD >= 0.0
    assert round(config.E12_SESSION_CAP_USD, 2) == config.E12_SESSION_CAP_USD  # whole cents
    assert config.E12_SESSION_CAP_USD <= config.SHARED_ACCOUNT_CAP_USD + config.ACCOUNT_2_CAP_USD
    # the three active names point at the E.12 block
    assert config.STEP2_PURCHASE_SESSION_ID is config.STAGE_E12_SESSION_ID
    assert config.STEP2_SESSION_CAP_USD == config.E12_SESSION_CAP_USD
    assert config.STEP2_REQUEST_CAP_USD == config.E12_REQUEST_CAP_USD


def test_the_earlier_blocks_stay_as_they_were() -> None:
    assert (config.STAGE_E5_SESSION_ID, config.E5_SESSION_CAP_USD, config.E5_REQUEST_CAP_USD) == (
        "stage-E.5-2026-09-27", 21.52, 3.00)
    assert (config.STAGE_E2B_SESSION_ID, config.E2B_SESSION_CAP_USD,
            config.E2B_REQUEST_CAP_USD) == ("stage-E.2b-2026-09-26", 0.00, 0.00)
    assert (config.STAGE_E1_SESSION_ID, config.E1_SESSION_CAP_USD,
            config.E1_REQUEST_CAP_USD) == ("stage-E.1-2026-09-24", 113.48, 3.00)
    assert (config.STAGE_E0_SESSION_ID, config.E0_SESSION_CAP_USD,
            config.E0_REQUEST_CAP_USD) == ("stage-E.0-2026-09-23", 0.00, 0.00)
    assert (config.STAGE_D1F_SESSION_ID, config.D1F_SESSION_CAP_USD,
            config.D1F_REQUEST_CAP_USD) == ("stage-D.1f-2026-09", 10.00, 10.00)
    assert config.ACTIVE_ACCOUNT == ACCOUNT_2_ID


def test_the_e12_block_sits_after_the_e5_block_and_before_the_active_names() -> None:
    # Arrange
    source = Path(config.__file__).read_text(encoding="utf-8")

    # Act
    e5 = source.index("\nE5_REQUEST_CAP_USD =")
    e12 = source.index("\nSTAGE_E12_SESSION_ID =")
    active = source.index("\nSTEP2_PURCHASE_SESSION_ID =")

    # Assert
    assert e5 < e12 < active
    assert "\nSTEP2_PURCHASE_SESSION_ID = STAGE_E12_SESSION_ID\n" in source


# ------------------------------------------------------------- docs/ACCESS.md ----
def test_access_doc_names_the_two_numbered_key_variables() -> None:
    # Arrange
    text = config.ACCESS_DOC_PATH.read_text(encoding="utf-8")
    credential = [line for line in text.splitlines() if line.startswith("- **Credential.**")]

    # Assert: C-10(a); the bare legacy name no longer appears (MLCE_... is MLCryptoEngine's)
    assert len(credential) == 1
    assert "`DATABENTO_API_KEY1` (acct-1)" in credential[0]
    assert "`DATABENTO_API_KEY2` (acct-2)" in credential[0]
    assert not re.search(r"(?<![A-Z_])DATABENTO_API_KEY(?![0-9A-Z_])", credential[0])
