"""Tests for sr80.py: the independent re-implementation against p7_final's printed values, and SR80.json."""
from __future__ import annotations

import json
import math
import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sr80  # noqa: E402

PRINTED = {"SR0_disc": 0.1137, "G3": 0.1724, "t_bar_test": 0.1017, "DSR_test": 0.1649, "b_test": 0.1649,
           "G4": 0.2007, "G3_G4_binding": 0.2007}   # reports/stage_e32_briefs/protocol/p7_final_budget300.md


def test_independent_thresholds_match_p7_printed_values_at_4dp():
    th = sr80.thresholds_b()
    for key, printed in PRINTED.items():
        assert round(th[key], 4) == printed, key


def test_independent_sr80_test_matches_p7_printed_s80():
    th = sr80.thresholds_b()
    assert round(sr80.sr80_set(th, sr80.se_b)["closed"]["test"], 4) == 0.1936


def test_exact_root_has_power_080_and_lies_just_above_closed_form():
    th = sr80.thresholds_b()
    s = sr80.sr80_set(th, sr80.se_b)
    for key, (bar, t) in {"disc_G3": (th["G3"], 796), "test": (th["b_test"], 870)}.items():
        exact = s["exact"][key]
        assert sr80.Z.cdf((exact - bar) / sr80.se_b(exact, t)) == pytest.approx(0.80, abs=1e-9)
        assert 0 < exact - s["closed"][key] < 1e-3


def test_g4_lower_bound_reaches_b_test():
    th = sr80.thresholds_b()
    assert th["G4"] - sr80.se_b(th["G4"], 796) == pytest.approx(th["b_test"], abs=1e-12)
    assert th["G3_G4_binding"] == max(th["G3"], th["G4"])


def test_dsr_required_is_the_095_boundary():
    s = sr80.dsr_required_b(838, 796)
    sr0 = sr80.expected_max_b(838, 1 / 795)
    z = (s - sr0) * math.sqrt(795) / math.sqrt(1 + 0.5 * s * s)
    assert sr80.Z.cdf(z) == pytest.approx(0.95, abs=1e-9)


def test_spec_hash_refusal(tmp_path):
    bad = tmp_path / "spec.md"
    shutil.copy(sr80.SPEC, bad)
    bad.write_bytes(bad.read_bytes()[:-1])
    with pytest.raises(sr80.SpecHashError):
        sr80.require_frozen_spec(bad)
    assert sr80.require_frozen_spec() == sr80.FROZEN_SPEC_SHA256


def test_sr80_json_on_disk_is_consistent():
    doc = json.loads(sr80.DEFAULT_OUT.read_text())
    assert doc["spec_sha256"] == sr80.FROZEN_SPEC_SHA256
    assert doc["cross_check"]["pass"] is True and all(doc["cross_check"]["checks"].values())
    s = sr80.sr80_set(sr80.thresholds_b(), sr80.se_b)["closed"]
    for key in ("disc_G3", "disc_G3G4", "test"):
        assert doc["SR80"][key] == pytest.approx(s[key], abs=1e-7)
    assert doc["inputs"]["N"] == 838 and doc["inputs"]["T_disc"] == 796 and doc["inputs"]["T_test"] == 870


def test_build_cross_checks_p7_final_and_reproduces_the_file_on_disk():
    doc = sr80.build()
    assert doc["cross_check"]["pass"] is True
    assert doc["cross_check"]["max_abs_diff_A_vs_B"] < sr80.CROSS_CHECK_TOL
    on_disk = json.loads(sr80.DEFAULT_OUT.read_text())
    assert doc["SR80"] == on_disk["SR80"] and doc["thresholds"] == on_disk["thresholds"]
    assert all(v > 0.799 for v in doc["power_at_SR80_by_p7_power"].values())


def test_printed_value_parser_reads_the_frozen_output():
    printed = sr80.parse_printed(sr80.P7_FROZEN_MD.read_text())
    assert printed["SR80_test"] == 0.1936 and printed["G4"] == 0.2007 and None not in printed.values()
