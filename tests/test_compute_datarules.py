"""The compute backend's data rules (Stage E.2b Task 5, V10-4/5): what may leave the ThinkPad.

Synthetic parquets only; the forbidden locations (sealed store, ledger, .env) are tmp stand-ins
passed through DataRules, and the key is a fake one. The pins at the end tie the backend's
constants to the modules that own them (sealing magic, store names, store windows).
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from compute.datarules import (
    BACKTEST,
    SEALED_MAGIC,
    STORES,
    TRAINING,
    DataRuleRefused,
    DataRules,
    check_bar_file,
    check_data_root,
    default_rules,
    dest_relpath,
    file_contains,
    store_of,
)
from tests._compute_fixtures import (
    FAKE_KEY,
    RESEARCH,
    STEP2,
    bar_file,
    ct_ns,
    default_days,
    sealed_blob,
    store_name,
    trading_days,
    write_bars,
)

KEY = FAKE_KEY.encode()


@pytest.fixture()
def rules(tmp_path: Path) -> DataRules:
    return DataRules(sealed_roots=(tmp_path / "repo" / "data" / "sealed",),
                     ledger_paths=(tmp_path / "repo" / "ledger", tmp_path / "ext" / "ledger.jsonl"),
                     env_files=(tmp_path / "repo" / ".env",))


def send(path: Path, rules: DataRules, stores: tuple[str, ...] = (STEP2, RESEARCH)):
    return check_bar_file(path, allowed_stores=stores, rules=rules, key=KEY)


def test_clean_step2_and_research_files_pass(tmp_path: Path, rules: DataRules) -> None:
    step2 = send(bar_file(tmp_path / "s2", STEP2, "ES"), rules)
    research = send(bar_file(tmp_path / "rs", RESEARCH, "NQ"), rules)
    assert (step2.store, step2.product, step2.trade_dates) == (STEP2, "ES", 5)
    assert (research.store, research.product) == (RESEARCH, "NQ")
    assert step2.dest(TRAINING) == f"data/training/ES/{store_name(STEP2, 'ES')}"
    assert research.dest(BACKTEST) == f"data/backtest/research/NQ/{store_name(RESEARCH, 'NQ')}"


# One planted forbidden file of each kind: (builder, expected kind). Every one is refused.
def _sealed_store(tmp: Path) -> Path:
    return bar_file(tmp / "repo" / "data" / "sealed" / "ZZ_holdout_v2", STEP2)


def _sealed_elsewhere(tmp: Path) -> Path:
    return bar_file(tmp / "elsewhere" / "sealed", STEP2)


def _sealed_suffix(tmp: Path) -> Path:
    return sealed_blob(tmp / "x" / "range=2024-04-01_2024-05-01.dbn.zst.sealed")


def _sealed_content(tmp: Path) -> Path:
    return sealed_blob(tmp / "x" / "ES" / store_name(STEP2, "ES"))


def _holdout1(tmp: Path) -> Path:
    return bar_file(tmp / "x", RESEARCH, days=[date(2026, 6, 18), date(2026, 6, 22)])


def _holdout2(tmp: Path) -> Path:
    return bar_file(tmp / "x", STEP2, days=[date(2024, 2, 28), date(2024, 6, 3)])


def _embargo(tmp: Path) -> Path:
    return bar_file(tmp / "x", STEP2, days=[date(2024, 2, 29), date(2024, 3, 15)])


def _clean_name_and_metadata_dirty_rows(tmp: Path) -> Path:
    return bar_file(tmp / "x", RESEARCH, days=[date(2026, 6, 19), date(2026, 6, 23)],
                    meta_range=["2026-06-19", "2026-06-19"])


def _env_file(tmp: Path) -> Path:
    path = tmp / "repo" / ".env"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"DATABENTO_API_KEY={FAKE_KEY}\n", encoding="utf-8")
    return path


def _env_variant(tmp: Path) -> Path:
    path = tmp / "copy" / ".env.backup"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("x=1\n", encoding="utf-8")
    return path


def _key_inside(tmp: Path) -> Path:
    return bar_file(tmp / "x", STEP2, extra_meta={"note": FAKE_KEY})


def _ledger(tmp: Path) -> Path:
    path = tmp / "repo" / "ledger" / "databento_spend.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('{"usd": 1.0}\n', encoding="utf-8")
    return path


def _ledger_copy(tmp: Path) -> Path:
    path = tmp / "copies" / "old_spend_ledger.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{}\n", encoding="utf-8")
    return path


def _external_ledger(tmp: Path) -> Path:
    path = tmp / "ext" / "ledger.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{}\n", encoding="utf-8")
    return path


FORBIDDEN = {
    "sealed store": (_sealed_store, "sealed-store"),
    "any 'sealed' directory": (_sealed_elsewhere, "sealed-store"),
    "sealed suffix": (_sealed_suffix, "sealed-suffix"),
    "sealed bytes under a clean name": (_sealed_content, "sealed-content"),
    "holdout-1 bar": (_holdout1, "holdout-date"),
    "holdout-2 bar": (_holdout2, "holdout-date"),
    "March 2024 embargo bar": (_embargo, "holdout-date"),
    "clean name and metadata, holdout rows": (_clean_name_and_metadata_dirty_rows, "holdout-date"),
    ".env": (_env_file, "secret-env"),
    ".env variant": (_env_variant, "secret-env"),
    "key bytes inside a store file": (_key_inside, "secret-key"),
    "the ledger": (_ledger, "ledger"),
    "a spend ledger copy": (_ledger_copy, "ledger"),
    "an external ledger": (_external_ledger, "ledger"),
}


@pytest.mark.parametrize("case", sorted(FORBIDDEN))
def test_each_forbidden_kind_is_refused_on_the_send_side(case: str, tmp_path: Path,
                                                         rules: DataRules) -> None:
    build, kind = FORBIDDEN[case]
    with pytest.raises(DataRuleRefused) as refused:
        send(build(tmp_path), rules)
    assert refused.value.kind == kind


def test_holdout_refusal_names_the_class(tmp_path: Path, rules: DataRules) -> None:
    for build, word in ((_holdout1, "holdout-1"), (_holdout2, "holdout-2"),
                        (_embargo, "embargo-2")):
        with pytest.raises(DataRuleRefused, match=word):
            send(build(tmp_path / word), rules)


@pytest.mark.parametrize(("store", "days", "kind"), [
    (STEP2, [date(2025, 5, 1)], "outside-window"),  # M7.4's planted research-window bar
    (STEP2, [date(2019, 5, 3)], "outside-window"),  # before D4's earliest S_X
    (RESEARCH, [date(2024, 1, 5)], "outside-window"),
])
def test_bars_outside_their_stores_window_are_refused(store: str, days: list[date], kind: str,
                                                      tmp_path: Path, rules: DataRules) -> None:
    with pytest.raises(DataRuleRefused) as refused:
        send(bar_file(tmp_path, store, days=days), rules)
    assert refused.value.kind == kind


def test_metadata_must_match_the_rows_and_step2_must_say_so(tmp_path: Path,
                                                           rules: DataRules) -> None:
    days = default_days(STEP2)
    cases = {
        "range": bar_file(tmp_path / "a", STEP2, meta_range=["2019-05-06", "2019-05-07"]),
        "store": bar_file(tmp_path / "b", STEP2, meta_store="research"),
        "none": write_bars(tmp_path / "c" / "ES" / store_name(STEP2, "ES"), days,
                           meta_store=None),
    }
    for path in cases.values():
        with pytest.raises(DataRuleRefused) as refused:
            send(path, rules)
        assert refused.value.kind == "metadata"


def test_unreadable_or_undated_files_are_refused(tmp_path: Path, rules: DataRules) -> None:
    undated = bar_file(tmp_path / "u", STEP2, with_trade_date=False)
    garbage = tmp_path / "g" / "ZZ" / store_name(STEP2, "ZZ")
    garbage.parent.mkdir(parents=True)
    garbage.write_bytes(b"not a parquet")
    other = bar_file(tmp_path / "o", STEP2)
    renamed = other.with_name("ohlcv-1m_ZZ_v_0_2025-04-01_2026-06-19_confirmation.parquet")
    other.rename(renamed)
    for path, kind in ((undated, "no-trade-date"), (garbage, "not-parquet"),
                       (renamed, "not-allowlisted"), (tmp_path / "missing.parquet",
                                                      "not-a-regular-file")):
        with pytest.raises(DataRuleRefused) as refused:
            send(path, rules)
        assert refused.value.kind == kind


def test_rows_are_booked_by_the_cme_calendar_not_by_their_labels(tmp_path: Path,
                                                                  rules: DataRules) -> None:
    """Ruling L-9's case: MBT's bar of 2026-06-19 12:00 CT, which CME books to trade date
    2026-06-22 (holdout-1), labelled 2026-06-19 in the file. Labels and metadata look clean; the
    group-calendar booking refuses it. A bar past the calendar's coverage is refused too."""
    rows = [(ct_ns(date(2026, 6, 18), 8, 30), "2026-06-18"),
            (ct_ns(date(2026, 6, 19), 12, 0), "2026-06-19")]
    relabelled = write_bars(tmp_path / "a" / "MBT" / store_name(RESEARCH, "MBT"), [],
                            store=RESEARCH, rows=rows)
    with pytest.raises(DataRuleRefused, match="holdout-1") as refused:
        send(relabelled, rules)
    assert refused.value.kind == "holdout-date"
    sunday = write_bars(tmp_path / "b" / "ES" / store_name(RESEARCH, "ES"), [], store=RESEARCH,
                        rows=[(ct_ns(date(2026, 6, 21), 18, 0), "2026-06-19")])
    with pytest.raises(DataRuleRefused, match="holdout-1") as refused:
        send(sunday, rules)
    assert refused.value.kind == "unbookable"
    mislabelled = write_bars(tmp_path / "c" / "ES" / store_name(RESEARCH, "ES"), [],
                             store=RESEARCH,
                             rows=[(ct_ns(date(2025, 4, 7), 8, 30), "2025-04-08")])
    with pytest.raises(DataRuleRefused) as refused:
        send(mislabelled, rules)
    assert refused.value.kind == "label-mismatch"
    unknown = bar_file(tmp_path / "d", STEP2, "ZZ")
    with pytest.raises(DataRuleRefused) as refused:
        send(unknown, rules)
    assert refused.value.kind == "unknown-product"


def test_a_training_root_takes_step2_files_only(tmp_path: Path, rules: DataRules) -> None:
    research = bar_file(tmp_path, RESEARCH)
    with pytest.raises(DataRuleRefused) as refused:
        check_bar_file(research, allowed_stores=(STEP2,), rules=rules, key=KEY)
    assert refused.value.kind == "not-allowlisted"
    with pytest.raises(DataRuleRefused):
        dest_relpath(TRAINING, RESEARCH, "ZZ", store_name(RESEARCH, "ZZ"))


# ------------------------------------------------------ far side: whole roots ----
def _training_root(tmp: Path) -> Path:
    root = tmp / "agent" / "data" / "training"
    bar_file(root, STEP2, "ES")
    return root


def test_a_clean_training_root_passes(tmp_path: Path) -> None:
    files = check_data_root(_training_root(tmp_path), TRAINING)
    assert [f.product for f in files] == ["ES"]


@pytest.mark.parametrize(("plant", "kind"), [
    ("research file", "training-root"),
    ("step2 name, research rows", "outside-window"),
    ("partial upload", "training-root"),
    ("file at the root", "training-root"),
    ("nested directory", "training-root"),
    ("wrong product folder", "training-root"),
    ("sealed blob", "sealed-content"),
])
def test_a_training_root_holding_anything_else_is_refused(plant: str, kind: str,
                                                          tmp_path: Path) -> None:
    root = _training_root(tmp_path)
    if plant == "research file":
        bar_file(root, RESEARCH, "NQ")
    elif plant == "step2 name, research rows":
        bar_file(root, STEP2, "NQ", days=trading_days(date(2025, 4, 1), 3))
    elif plant == "partial upload":
        (root / "ES" / (store_name(STEP2, "ES") + ".partial")).write_bytes(b"x")
    elif plant == "file at the root":
        (root / "notes.txt").write_text("x", encoding="utf-8")
    elif plant == "nested directory":
        (root / "ES" / "old").mkdir()
    elif plant == "wrong product folder":
        bar_file(root / "XX", STEP2, "NQ")
    else:
        sealed_blob(root / "CL" / store_name(STEP2, "CL"))
    with pytest.raises(DataRuleRefused) as refused:
        check_data_root(root, TRAINING)
    assert refused.value.kind == kind


def test_a_backtest_root_holds_both_stores_at_their_layout_paths(tmp_path: Path) -> None:
    root = tmp_path / "agent" / "data" / "backtest"
    bar_file(root / "research", RESEARCH, "ES")
    bar_file(root / "step2", STEP2, "ES")
    assert sorted(f.store for f in check_data_root(root, BACKTEST)) == [RESEARCH, STEP2]
    bar_file(root / "research", STEP2, "NQ")  # a step 2 file in the research sub-root
    with pytest.raises(DataRuleRefused) as refused:
        check_data_root(root, BACKTEST)
    assert refused.value.kind == "backtest-root"


def test_missing_root_is_refused(tmp_path: Path) -> None:
    with pytest.raises(DataRuleRefused):
        check_data_root(tmp_path / "nope", TRAINING)


def test_key_scan_finds_the_key_across_a_chunk_boundary(tmp_path: Path) -> None:
    from compute.files import CHUNK_BYTES

    path = tmp_path / "blob"
    path.write_bytes(b"a" * (CHUNK_BYTES - 5) + KEY + b"b" * 10)
    assert file_contains(path, KEY)
    assert not file_contains(path, b"db-another-key-entirely")
    with pytest.raises(ValueError):
        file_contains(path, b"")


# --------------------------------------------------------------------- pins ----
def test_default_rules_name_the_real_forbidden_places() -> None:
    from data.config import DATA_ROOT, ENV_FILE, LEDGER_PATH

    rules = default_rules()
    assert DATA_ROOT / "sealed" in rules.sealed_roots
    assert LEDGER_PATH in rules.ledger_paths and LEDGER_PATH.parent in rules.ledger_paths
    assert ENV_FILE in rules.env_files


def test_constants_match_the_modules_that_own_them() -> None:
    from data.build_bars import (
        RESEARCH_FIRST_TRADE_DATE,
        RESEARCH_LAST_TRADE_DATE,
        research_parquet_path,
    )
    from data.holdout import MAGIC
    from data.step2_store import FIRST_TRADE_DATE, LAST_TRADE_DATE, step2_parquet_path
    from ml_route.store import step2_file_name

    assert SEALED_MAGIC == MAGIC
    for product in ("ES", "MBT", "6E", "ZN"):
        assert store_of(step2_parquet_path(product, Path("x")).name) == (STEP2, product)
        assert store_of(research_parquet_path(product, Path("x")).name) == (RESEARCH, product)
        assert step2_file_name(product) == store_name(STEP2, product)
    assert STORES[STEP2][1:] == (FIRST_TRADE_DATE, LAST_TRADE_DATE)
    assert STORES[RESEARCH][1:] == (RESEARCH_FIRST_TRADE_DATE, RESEARCH_LAST_TRADE_DATE)
