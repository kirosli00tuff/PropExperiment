"""M7.4 / ML-A23: the training job reads only the step 2 store and refuses anything else."""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from data.config import PROCESSED_ROOT, STEP2_ROOT
from ml_route.store import (
    StoreRefused,
    assert_store_root,
    assert_window,
    read_product_bars,
    step2_file_name,
)
from ml_route.synthetic import synthetic_bars, write_step2_store

FIRST, LAST = date(2019, 5, 6), date(2019, 6, 28)


@pytest.fixture(scope="module")
def frame() -> pd.DataFrame:
    return synthetic_bars("NQ", "equity", FIRST, LAST, seed=1)


@pytest.fixture()
def store(tmp_path: Path, frame: pd.DataFrame) -> Path:
    root = tmp_path / "step2"
    write_step2_store(root, {"NQ": frame}, {"NQ": [date(2019, 6, 14)]})
    return root


def test_file_name_matches_the_step2_builder() -> None:
    from data.step2_store import step2_parquet_path

    assert step2_file_name("ZN") == step2_parquet_path("ZN", Path("x")).name
    assert STEP2_ROOT != PROCESSED_ROOT and not STEP2_ROOT.is_relative_to(PROCESSED_ROOT)


def test_reads_the_store_and_cuts_at_s_x(store: Path, frame: pd.DataFrame) -> None:
    pb = read_product_bars(store, "NQ", date(2019, 5, 20), forbidden_root=store.parent / "p")
    assert pb.trade_date.min() >= np.datetime64("2019-05-20")
    assert pb.rows_cut_before_s_x == int((frame["trade_date"] < "2019-05-20").sum()) > 0
    assert pb.roll_blackout_dates == frozenset({date(2019, 6, 14)})
    assert len(pb) + pb.rows_cut_before_s_x == len(frame)


def test_research_store_root_is_refused_outright(tmp_path: Path) -> None:
    for bad in (PROCESSED_ROOT, PROCESSED_ROOT / "NQ", PROCESSED_ROOT.parent):
        with pytest.raises(StoreRefused, match="research"):
            assert_store_root(bad)


def test_planted_research_window_path_is_refused(store: Path, frame: pd.DataFrame) -> None:
    planted = store / "NQ" / "ohlcv-1m_NQ_v_0_2025-04-01_2026-06-19.parquet"
    frame.head(5).to_parquet(planted)
    with pytest.raises(StoreRefused, match="allowlist"):
        read_product_bars(store, "NQ", FIRST, forbidden_root=store.parent / "p")


def test_other_stray_files_are_refused(store: Path) -> None:
    (store / "notes.txt").write_text("x", encoding="utf-8")
    with pytest.raises(StoreRefused, match="allowlist"):
        assert_store_root(store, forbidden_root=store.parent / "p")


def test_mismatched_root_directory_is_refused(tmp_path: Path, frame: pd.DataFrame) -> None:
    root = tmp_path / "s"
    (root / "ZN").mkdir(parents=True)
    frame.head(5).to_parquet(root / "ZN" / step2_file_name("NQ"))
    with pytest.raises(StoreRefused, match="allowlist"):
        assert_store_root(root, forbidden_root=tmp_path / "p")


@pytest.mark.parametrize("planted_day", ["2025-05-01", "2024-03-01", "2024-04-02"])
def test_planted_out_of_window_bar_makes_the_job_refuse(tmp_path: Path, frame: pd.DataFrame,
                                                        planted_day: str) -> None:
    bad = frame.copy()
    bad.loc[bad.index[-1], "trade_date"] = planted_day  # a research-window / embargo / holdout bar
    write_step2_store(tmp_path / "s", {"NQ": bad})
    with pytest.raises(StoreRefused, match="on or after 2024-03-01"):
        read_product_bars(tmp_path / "s", "NQ", FIRST, forbidden_root=tmp_path / "p")


def test_wrong_store_metadata_is_refused(tmp_path: Path, frame: pd.DataFrame) -> None:
    import json

    import pyarrow as pa
    import pyarrow.parquet as pq

    path = tmp_path / "s" / "NQ" / step2_file_name("NQ")
    path.parent.mkdir(parents=True)
    table = pa.Table.from_pandas(frame.head(10), preserve_index=False)
    table = table.replace_schema_metadata({b"propexperiment": json.dumps({"store": "research"})
                                           .encode()})
    pq.write_table(table, path)
    with pytest.raises(StoreRefused, match="not step2"):
        read_product_bars(tmp_path / "s", "NQ", FIRST, forbidden_root=tmp_path / "p")


@pytest.mark.skipif(os.name == "nt", reason="symlinks need privileges on Windows")
def test_symlink_into_the_research_root_is_refused(tmp_path: Path, frame: pd.DataFrame) -> None:
    research = tmp_path / "processed" / "NQ"
    research.mkdir(parents=True)
    target = research / step2_file_name("NQ")
    frame.head(5).to_parquet(target)
    link_dir = tmp_path / "s" / "NQ"
    link_dir.mkdir(parents=True)
    (link_dir / step2_file_name("NQ")).symlink_to(target)
    with pytest.raises(StoreRefused, match="links to"):
        assert_store_root(tmp_path / "s", forbidden_root=tmp_path / "processed")


def test_s_x_outside_the_window_and_missing_product_refused(store: Path) -> None:
    with pytest.raises(StoreRefused, match="S_X"):
        read_product_bars(store, "NQ", date(2024, 3, 1), forbidden_root=store.parent / "p")
    with pytest.raises(StoreRefused, match="no step 2 file"):
        read_product_bars(store, "ZN", FIRST, forbidden_root=store.parent / "p")


def test_window_assertion_on_a_saved_row_index() -> None:
    ok = np.array(["2019-05-06", "2024-02-29"], dtype="datetime64[D]")
    assert_window("NQ", FIRST, ok, "t")
    with pytest.raises(StoreRefused):
        assert_window("NQ", FIRST, np.array(["2024-03-01"], dtype="datetime64[D]"), "t")
    with pytest.raises(StoreRefused):
        assert_window("NQ", date(2020, 1, 2), np.array(["2020-01-01"], dtype="datetime64[D]"), "t")
