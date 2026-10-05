"""Test C1's default leg loader against harness v10's real loader (data.hist_bars.load_hist_leg)
on a SYNTHETIC ext2010 fixture store built by data.hist_store from synthetic DBN chunks (v10's own
test fixtures, tests/_e14_fixtures.py). It checks the wiring the evaluation uses: plan ext2010,
the pinned sha256, the pinned hist calendar object, and the refusals passing through.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from c1_replication.evaluate import check_stores, default_leg_loader
from c1_replication.guards import C1Refused
from data import hist_store as hs
from data import pull_hist as ph
from data.hist_calendar import load_hist_group_calendar
from data.stage_e_bars import StageEBarRefusal
from screening import harness_freeze
from tests._e14_fixtures import FIXTURE_DIR, bar, ct, make_store_inputs

HARNESS = "ef" * 32


@pytest.fixture
def ng_store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[dict, Path]:
    monkeypatch.setattr(harness_freeze, "preflight", lambda expected, root=None: expected)
    px = 4_000_000_000
    bars = [bar(ct("2010-06-06", "18:00"), px, px + 1_000_000),
            bar(ct("2010-06-07", "10:00"), px, px), bar(ct("2011-03-01", "10:00"), px, px),
            bar(ct("2019-04-30", "10:00"), px, px)]
    paths = make_store_inputs(tmp_path, ph.get_plan("ext2010"), "NG", bars, splice="2013-06-13",
                              iids=(1001, 1002), raws=("NGN0", "NGQ0"))
    summary = hs.run_product("NG", "ext2010", expected_harness_sha256=HARNESS,
                             out_base=tmp_path / "store", reports_base=paths["reports"],
                             rolls_dir=paths["rolls"], condition_dir=paths["condition_dir"],
                             calendar_base=FIXTURE_DIR, log=lambda m: None)
    assert summary["status"] == "built", summary.get("refusal_causes")
    return summary, tmp_path / "store"


def test_the_default_loader_reads_the_v10_store_pinned(ng_store):
    summary, store = ng_store
    sha = summary["parquet"]["sha256"]
    cal = load_hist_group_calendar("energy", base=FIXTURE_DIR)
    leg = default_leg_loader(store)("NG", expected_sha256=sha, calendar=cal)
    assert leg.root == "NG" and leg.sha256 == sha
    assert [d.isoformat() for d in leg.trade_dates][:2] == ["2010-06-07", "2011-03-01"]
    assert leg.trade_dates[-1].isoformat() == "2019-04-30"
    assert check_stores({"NG": sha}, store)["NG"]["sha256"] == sha
    with pytest.raises(StageEBarRefusal):
        default_leg_loader(store)("NG", expected_sha256="0" * 64, calendar=cal)
    with pytest.raises(C1Refused, match="sha256"):
        check_stores({"NG": "0" * 64}, store)
