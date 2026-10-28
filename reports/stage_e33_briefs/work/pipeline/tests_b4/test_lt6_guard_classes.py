"""B4 LT6 supplement: one assertion per refused class of protocol P1.2 (the Refused bullet), through guard33's
public checks. DataCoder's pipeline/tests/test_guard33.py (44 tests) covers every class; this file adds the two
spellings that suite does not name (a stats31.md file and the runs/ folder itself) and restates each class once so
the B4 report can cite one test per class."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

PIPE = Path(__file__).resolve().parents[1]
if str(PIPE) not in sys.path:
    sys.path.insert(0, str(PIPE))

import guard33 as g  # noqa: E402

Refused = g.GuardRefused


def test_class1_sealed_soy_test_folder() -> None:
    with pytest.raises(Refused, match="sealed soy test data"):
        g.check_path(g.SEALED / "anything.dbn.zst")


def test_class2_zm_zs_zl_dated_in_the_test_window() -> None:
    for d in ("2017-05-01", "2018-08-15", "2020-11-30"):
        with pytest.raises(Refused):
            g.check_date(d)
    with pytest.raises(Refused, match="soy test window"):
        g.check_path(g.DERIVED / "split" / "ZS" / "2020-11-30.npy")


def test_class3_on_or_after_2024_03_01() -> None:
    with pytest.raises(Refused):
        g.check_date("2024-03-01")
    with pytest.raises(Refused, match="on or after 2024-03-01"):
        g.check_path(g.DERIVED / "split" / "ZL" / "2024-03-01.npy")


def test_class4_derived_unsealed_files_tsv() -> None:
    lines = g.UNSEALED_TSV.read_text(encoding="utf-8").splitlines()[1:]
    listed = [ln.split("\t")[0] for ln in lines if ln.strip()]
    assert listed
    p = listed[0] if listed[0].startswith("/") else str(g.REPO / listed[0])
    with pytest.raises(Refused, match="derived_unsealed_files.tsv"):
        g.check_path(p)


def test_class5_other_roots_market_data() -> None:
    with pytest.raises(Refused, match="not on the E.33 allowlist"):
        g.check_path(g.VENDOR / "mbo" / "ZC_v_0" / "range=2021-01-31T220000Z_2021-02-28T220000Z.dbn.zst")


@pytest.mark.parametrize("rel", ["", "measure31", "stats31.md", "stats31.json", "x/stats31.md"])
def test_class6_e31_measured_outputs(rel: str) -> None:
    with pytest.raises(Refused, match="E.31 measured outputs"):
        g.check_path(g.E31_RUNS / rel if rel else g.E31_RUNS)
