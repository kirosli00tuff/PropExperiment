"""Harness v10 (Stage E.14): the E.14 config block and the harness-freeze listing.

The block is additive: every earlier block, ACCOUNT_2_CAP_USD (V26) and the step 2 active policy
stay as they were.
"""

from __future__ import annotations

from pathlib import Path

from data import config
from screening import harness_freeze as hf


def test_the_e14_block_holds_the_placeholders_and_d13s_request_cap() -> None:
    assert config.STAGE_E14_SESSION_ID == "stage-E.14-2026-10-05"
    assert config.E14_SESSION_CAP_USD == 0.00  # the lead sets it from the fresh quote x 1.03
    assert config.E14_REQUEST_CAP_USD == 3.00 == config.E12_REQUEST_CAP_USD
    assert config.STAGE_E14_EXT2010_SESSION_ID == "stage-E.14-ext2010"
    assert config.E14_EXT2010_SESSION_CAP_USD == 0.00  # C1's buy stays refused (V26)
    assert config.E14_BUY_ACCOUNT == config.ACCOUNT_2_ID
    assert config.HIST_ROOT == config.DATA_ROOT / "processed_hist"


def test_the_e14_session_cap_never_exceeds_acct2s_headroom_when_set() -> None:
    # $18.070270 of headroom (E.12_RETURN.md:572); the cap is whole cents, at most $18.07
    assert config.E14_SESSION_CAP_USD <= 18.07
    assert round(config.E14_SESSION_CAP_USD, 2) == config.E14_SESSION_CAP_USD


def test_acct2s_cap_and_the_step2_active_policy_are_unchanged() -> None:
    assert config.ACCOUNT_2_CAP_USD == 249.67
    assert config.ACCOUNTS[config.ACCOUNT_2_ID].cap_usd == 249.67
    assert config.STEP2_PURCHASE_SESSION_ID == config.STAGE_E12_SESSION_ID
    assert config.STEP2_SESSION_CAP_USD == config.E12_SESSION_CAP_USD == 137.73
    assert config.STEP2_REQUEST_CAP_USD == config.E12_REQUEST_CAP_USD
    assert config.STEP2_TRAINING_WINDOW_ONLY is True
    assert config.ACTIVE_ACCOUNT == config.ACCOUNT_2_ID


def test_the_e14_block_sits_after_the_step2_active_names() -> None:
    source = Path(config.__file__).read_text(encoding="utf-8")
    active = source.index("\nSTEP2_REQUEST_CAP_USD = E12_REQUEST_CAP_USD\n")
    e14 = source.index("\nSTAGE_E14_SESSION_ID =")
    assert active < e14 < source.index("\nDATABENTO_KEY_ENV_BY_ACCOUNT")


def test_the_harness_freeze_lists_the_v10_inputs_and_data_root() -> None:
    calendars = {f"data/calendars/hist2010/{g}.json" for g in (
        "equity", "rates", "fx", "energy", "metals", "grains")}
    assert calendars <= set(hf.FROZEN_INPUTS)
    assert "data/processed_hist" in hf.DATA_SUBDIRS
    assert {"data.pull_hist", "data.hist_calendar", "data.hist_store", "data.hist_bars",
            "screening.stage_e14_c2", "screening.trial_registry"} <= set(hf.ENTRY_MODULES)
    assert "test_e14_*.py" in hf.TEST_PATTERNS
    # the v9 entries are kept
    assert "reports/stage_e12_closure_rulings.json" in hf.FROZEN_INPUTS
    assert {"data/processed", "data/processed_step2", "data/vendor", "data/sealed"} <= set(
        hf.DATA_SUBDIRS)


def test_the_manifest_categories_include_the_new_modules_and_tests() -> None:
    cats = hf.manifest_categories(config.REPO_ROOT)
    for rel in ("data/pull_hist.py", "data/hist_calendar.py", "data/hist_store.py",
                "data/hist_bars.py", "screening/stage_e14_c2.py", "screening/trial_registry.py"):
        assert cats[rel] == "harness_code"
    assert cats["tests/test_e14_c2.py"] == "stage_e_test"
    assert "ledger/trial_registrations.jsonl" not in cats  # append-only: never frozen
    assert not any(hf._in_data_subdir(rel) for rel in cats)
