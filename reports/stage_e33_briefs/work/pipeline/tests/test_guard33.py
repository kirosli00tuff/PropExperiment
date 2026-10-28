"""LT6 (P4.1): the E.33 data guard refuses every path and date class of P1.2's Refused list."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

PIPELINE = Path(__file__).resolve().parents[1]
if str(PIPELINE) not in sys.path:
    sys.path.insert(0, str(PIPELINE))

import guard33 as g  # noqa: E402

Refused = g.GuardRefused


# ------------------------------------------------------------------ refused classes ----
def test_refuses_sealed_soy_test_folder() -> None:
    with pytest.raises(Refused, match="sealed soy test data"):
        g.check_path(g.SEALED / "anything.dbn.zst.sealed")
    with pytest.raises(Refused, match="sealed soy test data"):
        g.check_path(g.SEALED)


def test_refuses_sealed_folder_through_a_symlink(tmp_path: Path) -> None:
    link = tmp_path / "innocent"
    link.symlink_to(g.SEALED.resolve())
    with pytest.raises(Refused, match="sealed soy test data"):
        g.check_path(link / "file.dbn.zst")


def test_refuses_original_location_of_a_sealed_file() -> None:
    data = json.loads(g.SEAL_MANIFEST.read_text(encoding="utf-8"))
    original = data["raw_files"][0]["original_path"]
    with pytest.raises(Refused, match="P1.2"):
        g.check_path(original)


@pytest.mark.parametrize("day", ["2017-05-01", "2019-03-05", "2020-11-30"])
def test_refuses_test_window_dates(day: str) -> None:
    with pytest.raises(Refused, match="soy test window"):
        g.check_date(day)


@pytest.mark.parametrize("day", ["2024-03-01", "2024-03-04", "2025-01-02"])
def test_refuses_dates_on_or_after_2024_03_01(day: str) -> None:
    with pytest.raises(Refused, match="on or after 2024-03-01"):
        g.check_date(day)


def test_refuses_dates_before_the_discovery_span_outside_the_window() -> None:
    with pytest.raises(Refused, match="outside the discovery span"):
        g.check_date("2016-06-01")


@pytest.mark.parametrize("name", [
    "2019-03-05.parquet",
    "range=2020-10-31T210000Z_2020-11-30T220000Z.dbn.zst",
    "range=2017-03-31T210000Z_2017-04-30T210001Z.dbn.zst",
    "glbx-mdp3-2020-11-01_2020-12-31.dbn.zst",
    "ZM_2020-11-15_2020-12-15_abc123.parquet",
    "2020-11.split.json",
])
def test_refuses_test_window_spans_read_from_file_names(name: str) -> None:
    with pytest.raises(Refused, match="soy test window"):
        g.check_path(g.DERIVED / "features" / "abc" / name)


def test_refuses_test_window_date_in_a_folder_name() -> None:
    with pytest.raises(Refused, match="soy test window"):
        g.check_path(g.DERIVED / "probes" / "2019-03-05" / "x.npy")


@pytest.mark.parametrize("name", [
    "2024-03-01.npy",
    "range=2024-02-29T220000Z_2024-03-31T210000Z.dbn.zst",
    "2024-03.split.json",
])
def test_refuses_post_cutoff_spans_read_from_file_names(name: str) -> None:
    with pytest.raises(Refused, match="on or after 2024-03-01"):
        g.check_path(g.E31_Z1 / name)


def test_refuses_files_listed_in_derived_unsealed_tsv() -> None:
    lines = g.UNSEALED_TSV.read_text(encoding="utf-8").splitlines()[1:]
    listed = [ln.split("\t")[0] for ln in lines if ln.strip()]
    relative = next(p for p in listed if not p.startswith("/"))
    absolute = next(p for p in listed if p.startswith("/"))
    for p in (g.REPO / relative, absolute):
        with pytest.raises(Refused, match="derived_unsealed_files.tsv"):
            g.check_path(p)
    with pytest.raises(Refused, match="derived_unsealed_files.tsv"):
        g.check_path(Path(absolute).parent)  # a folder that holds a listed file


@pytest.mark.parametrize("rel", ["measure31", "measure31/2021-03-04/day.parquet", "stats31.json"])
def test_refuses_e31_runs(rel: str) -> None:
    with pytest.raises(Refused, match="E.31 measured outputs"):
        g.check_path(g.E31_RUNS / rel)


@pytest.mark.parametrize("path", [
    g.VENDOR / "mbp-1" / "ZM_v_0" / "range=2021-01-31T220000Z_2021-02-28T220000Z.dbn.zst",
    g.VENDOR / "mbp-1" / "ZC_v_0" / "range=2021-01-31T220000Z_2021-02-28T220000Z.dbn.zst",
    g.LARGE / "derived" / "e31" / "Z2" / "2021-03-04.npy",
    g.LARGE / "derived" / "e31" / "Z3" / "2021-03-04.npy",
    g.REPO / "data" / "processed" / "x.parquet",
    g.REPO / "README.md",
])
def test_refuses_other_market_data_and_unlisted_files(path: Path) -> None:
    with pytest.raises(Refused, match="not on the E.33 allowlist"):
        g.check_path(path)


def test_check_request_refuses_a_span_that_meets_the_window() -> None:
    with pytest.raises(Refused, match="soy test window"):
        g.check_request(g.DERIVED / "split" / "ZS", "2017-01-03", "2021-01-04")
    with pytest.raises(Refused, match="P1.2"):
        g.check_request(g.DERIVED / "split" / "ZS", "2020-11-02", "2020-12-04")
    with pytest.raises(Refused, match="on or after 2024-03-01"):
        g.check_request(g.DERIVED / "split" / "ZS", "2024-02-01", "2024-03-04")
    with pytest.raises(Refused, match="bad request"):
        g.check_request(g.DERIVED / "split" / "ZS", "2021-02-01", "2021-01-04")


def test_check_records_refuses_records_outside_the_owned_window() -> None:
    ok = np.array([g.SEAL_END_NS, g.CUTOFF_NS - 1], dtype=np.int64)
    with pytest.raises(Refused, match="soy test window"):
        g.check_records(ok - 1, ok, "early")
    with pytest.raises(Refused, match="on or after 2024-03-01"):
        g.check_records(ok + 1, ok, "late recv")
    with pytest.raises(Refused, match="on or after 2024-03-01"):
        g.check_records(ok, ok + 1, "late event")


# ------------------------------------------------------------------ allowed ----
def test_allows_all_156_discovery_files_and_their_manifests() -> None:
    files = g.discovery_manifest()["files"]
    assert len(files) == 156
    for f in files:
        assert g.check_path(f["path"]) == Path(f["path"]).resolve()
    for folder in g.DISCOVERY_DIRS.values():
        g.check_path(folder / "manifest.json")
        g.check_path(folder)


@pytest.mark.parametrize("path", [
    g.E31_Z1 / "2020-12-01.npy",
    g.E31_Z1 / "2024-02-29.npy",
    g.E31_Z1 / "2020-12.split.json",
    g.DERIVED / "split" / "ZS" / "2021-03-04.npy",
    g.DERIVED / "features" / "0123456789ab" / "_day" / "2022-06-30.json",
])
def test_allows_e31_zm_store_and_the_e33_derived_tree(path: Path) -> None:
    g.check_path(path)


@pytest.mark.parametrize("day", ["2020-12-01", "2022-06-30", "2024-02-29"])
def test_allows_discovery_dates(day: str) -> None:
    assert g.check_date(day).isoformat() == day


def test_allows_a_discovery_request() -> None:
    g.check_request(g.E31_Z1 / "2021-03-04.npy", "2020-12-01", "2024-02-29")


def test_reference_calendars_are_allowed_and_sha_pinned() -> None:
    for ref in g.REFERENCE_FILES:
        g.check_reference(ref)


def test_dry_check_refuses_all_four(capsys: pytest.CaptureFixture[str]) -> None:
    assert g.main(["dry-check"]) == 0
    out = capsys.readouterr().out
    assert out.count("REFUSED (P1.2") == 4
    assert "NOT REFUSED" not in out
