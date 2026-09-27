"""The timed probes' helpers (the probes themselves ran once; figures in
reports/stage_e2b_ml_probes.json)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from ml_route import probes


def test_probe_split_is_cpcv_split_12_with_its_embargo() -> None:
    day = np.arange(probes.N_DATES)
    train, val = probes.one_split(day)
    size = probes.N_DATES // 6
    assert val.sum() == 2 * size and not (train & val).any()
    assert not train[2 * size] and train[2 * size + 1]  # the embargo date after block 2
    assert not train[5 * size:].any()  # block 6 never trains in CPCV


def test_synthetic_table_has_the_real_shapes() -> None:
    tab = probes.synthetic_table()
    assert tab["X"].shape == (450_000, 17) and tab["product"].max() == 30
    assert np.all(np.diff(tab["day"]) >= 0)


def test_merge_keeps_other_probes(tmp_path: Path) -> None:
    out = tmp_path / "p.json"
    probes.merge(out, "a", {"x": 1})
    probes.merge(out, "b", {"y": 2})
    data = json.loads(out.read_text(encoding="utf-8"))["probes"]
    assert data["a"]["x"] == 1 and data["b"]["y"] == 2 and "recorded_pdt" in data["a"]


def test_recorded_probe_file_has_the_a1_batch_and_projections() -> None:
    data = json.loads(Path("reports/stage_e2b_ml_probes.json").read_text(encoding="utf-8"))
    p = data["probes"]
    assert p["lstm"]["batch_probe"]["batch_size"] in (512, 256, 128, 64)
    assert "hours_estimate" in p["lgbm"]["projection"] and "hours_estimate" in p["lstm"][
        "projection"]
    assert p["versions"]["lightgbm"] == "4.7.0" and p["versions"]["torch"].startswith("2.14.0")
