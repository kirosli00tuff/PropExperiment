"""E22-F2 verdict (section 8) and looks (section 9) on synthetic ledgers."""

from datetime import date, timedelta

import numpy as np
import pytest

from forward.evaluate import EvaluationRefused
from forward.evaluate_f2 import ABANDONED, look, verdict, verdict_ledger
from forward.ledger import Ledger


def records(net, start=date(2026, 11, 2)):
    out, d = [], start
    for v in net:
        while d.weekday() >= 5:
            d += timedelta(days=1)
        out.append(
            {
                "schema": "E22-F2-ledger/1",
                "date": d.isoformat(),
                "net_pnl": float(v),
                "config_sha256": "c",
                "warmup_sha256": "w",
                "feed": "sip",
                "flags": [],
                "fills": [],
                "costs": {"total": 0.0},
                "exposure": {"cap_bound": True},
            }
        )
        d += timedelta(days=1)
    return out


def test_pass_and_fail_on_36_months():
    rng = np.random.RandomState(1)
    n = 800  # > 36 months of weekdays
    good = verdict(records(20 + 100 * rng.standard_normal(n)))
    assert good["status"] == "PASS" and good["p_one_sided"] <= 0.05
    bad = verdict(records(100 * rng.standard_normal(n) - 1))
    assert bad["status"] == "FAIL"
    assert good["horizon_end_exclusive"] == "2029-11-02"


def test_window_excludes_records_after_36_months_and_refuses_early():
    recs = records([1.0, -1.0] * 400)
    out = verdict(recs)
    assert out["n_days"] == sum(1 for r in recs if r["date"] < "2029-11-02")
    with pytest.raises(EvaluationRefused):
        verdict(recs[:500])


def test_missing_days_count_as_zero():
    recs = records([5.0, 0.0] * 400)
    for r in recs[1::2]:
        r["missing_day"] = True
    out = verdict(recs)
    assert out["n_missing_days"] > 0
    assert out["mean_daily_net_usd"] == pytest.approx(2.5, rel=0.01)


def test_abandoned_on_fingerprint_change_and_broken_chain(tmp_path):
    recs = records([1.0] * 800)
    recs[5]["config_sha256"] = "other"
    assert verdict(recs)["status"] == ABANDONED
    recs = records([1.0] * 800)
    recs[7]["feed"] = "iex"
    assert "feed" in verdict(recs)["reason"]
    path = tmp_path / "l.jsonl"
    led = Ledger(path)
    for r in records([1.0, 2.0, 3.0]):
        led.append(r)
    lines = path.read_text().splitlines()
    path.write_text("\n".join([lines[0], lines[2]]) + "\n")
    assert verdict_ledger(path)["status"] == ABANDONED


def test_look_is_descriptive_only():
    out = look(records([1.0, -0.5] * 200), 1)
    assert out["interim"] and "p_one_sided" not in out and "nw_t" not in out
    assert out["days_cap_bound"] == out["n_days"]
    assert out["window_end_exclusive"] == "2027-05-02"
