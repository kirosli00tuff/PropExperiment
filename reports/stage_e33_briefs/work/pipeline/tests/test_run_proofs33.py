"""Tests for run_proofs33's guards (no search is run here; the reduced end-to-end run is in the readings).

Run: uv run pytest -q reports/stage_e33_briefs/work/pipeline/tests/test_run_proofs33.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

HERE = Path(__file__).resolve().parent
PIPE = HERE.parent
if str(PIPE) not in sys.path:
    sys.path.insert(0, str(PIPE))

import run_proofs33 as rp  # noqa: E402


def test_seeds_and_ids():
    assert rp.parse_seeds("1-20,101-120") == list(range(1, 21)) + list(range(101, 121))
    assert rp.parse_seeds("9001") == [9001]
    assert len(rp.IDS) == 20 and rp.IDS[0] == "E33-S5F15L001A" and rp.IDS[10] == "E33-S5T30L001A"
    assert rp.N_PROOF == 838


@pytest.mark.parametrize("argv", [
    ["--seeds", "1,9001"],                                   # production and test seeds mixed
    ["--seeds", "1-5"],                                      # a subset of the 40 production seeds
    ["--seeds", "1-20,101-120", "--n-oof", "100"],           # production seeds at reduced size
    ["--seeds", "1-20,101-120", "--n", "900"],               # production seeds at another N
    ["--seeds", "9001", "--kind", "null"],                   # test seeds without their own summary
])
def test_refusals(argv):
    with pytest.raises(SystemExit):
        rp.main(argv + ["--summary-only"])


def test_manifest_pins_code(tmp_path):
    args = SimpleNamespace(n=838, n_oof=50)
    rp.check_manifest(tmp_path, [9001], args)
    rp.check_manifest(tmp_path, [9001], args)                # same code: resume allowed
    man = json.loads((tmp_path / "run_manifest.json").read_text())
    assert len(man["starts"]) == 2 and "synth33.py" in man["code_sha256"]
    assert man["versions"]["lightgbm"] and man["versions"]["uv_lock_sha256"] and man["engine_pipeline_sha"]
    assert set(rp.HASHED) <= set(man["code_sha256"]) and "p7_final.py" in man["code_sha256"]
    for key, val in (("code_sha256", "search33.py"), ("versions", "sklearn"), ("versions", "uv_lock_sha256")):
        bad = json.loads(json.dumps(man))
        bad[key][val] = "changed"
        (tmp_path / "run_manifest.json").write_text(json.dumps(bad))
        with pytest.raises(SystemExit):
            rp.check_manifest(tmp_path, [9001], args)


def test_code_hashes_cover_the_engine_files():
    import search33
    names = set(rp.code_hashes())
    assert {p.name for p in search33.pipeline_files()} <= names


def _fake_seed(pdir, seed, tier_a, failed_cfgs):
    root = pdir / f"seed{seed}"
    configs = []
    for cid in rp.IDS:
        f = cid in failed_cfgs
        configs.append({"config": cid, "failed": f, "defined": not f, "constant": False if not f else None,
                        "sharpe": None if f else 0.01})
        if f:
            b = root / "search" / cid
            b.mkdir(parents=True)
            (b / "stats.json").write_text(json.dumps({"failed": True, "errors": {"3": "x", "5": "y"}}))
    sel = {"configs": configs, "tier_a": tier_a, "best_config": rp.IDS[0], "best_sharpe": 0.01,
           "funnel": {"in_order": {"G1": 1, "G1..G2": 0, "G1..G3": 0, "G1..G4": 0, "G1..G5": 0},
                      "alone": {"G1": 1, "G2": 0, "G3": 0, "G4": 0, "G5": 0}, "failed_configs": len(failed_cfgs)}}
    root.mkdir(parents=True, exist_ok=True)
    (root / "selection.json").write_text(json.dumps(sel))
    (root / "selection.DONE").write_text("{}")


def test_summary_reports_failed_fits_and_counts_them(tmp_path):
    _fake_seed(tmp_path, 1, [], [])
    _fake_seed(tmp_path, 2, [], ["E33-S5F15G2050"])                 # empty Tier A but a failed configuration
    _fake_seed(tmp_path, 3, ["E33-S5F15L001A"], [])
    _fake_seed(tmp_path, 101, ["E33-S5F15L001A"], [])
    _fake_seed(tmp_path, 102, ["E33-S5F15L001A"], ["E33-S5T30G3200"])
    out = tmp_path / "s.md"
    rp.write_summary(tmp_path, out, [1, 2, 3], [101, 102])
    text = out.read_text()
    assert "| 2 | - | failed fits: 1 |" in text
    assert "Tier A non-empty: 1; seeds with any failed configuration: 1; counted against the null proof (either): 2" \
        in text
    assert "seed 2: S5F15G2050 folds [3, 5]" in text
    assert "pass count (Tier A non-empty and no failed configuration): 1" in text
    assert "Counting rule (ProofReview SF1)" in text and "run_proofs33.py that wrote this summary" in text


def test_null_sharpe_sd():
    loaded = {s: {"sel": {"configs": [
        {"config": "A", "defined": True, "sharpe": 0.01 * s, "constant": False},
        {"config": "B", "defined": True, "sharpe": 0.0, "constant": True},
        {"config": "C", "defined": False, "sharpe": None, "constant": None}]}} for s in (1, 2, 3)}
    out = rp.null_sharpe_sd(loaded)
    assert out["n_all"] == 6 and out["n_live"] == 3 and out["n_constant"] == 3
    assert out["sd_live"] == pytest.approx(0.01 * (2 / 3) ** 0.5)
    assert out["sd_live_df"] == pytest.approx(out["sd_live"] * (3 / 2) ** 0.5)
