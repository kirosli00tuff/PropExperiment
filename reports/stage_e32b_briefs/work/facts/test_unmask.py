"""Tests for unmask.py on a synthetic key and synthetic ratings (no real labels or ratings)."""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import unmask as U  # noqa: E402

KEY = {"contracts": {"K-AAAA": "MNQ", "K-BBBB": "NQ"}, "firms": {"V-AAAA": "topstep", "V-BBBB": "lucid"}}
LISTED = {"V-AAAA|K-AAAA", "V-BBBB|K-AAAA"}


def r(v, **kw):
    return {"value": v, "unknown": v is None, "reason": "synthetic", **kw}


def ratings():
    code = {"D2a": r(1), "D2b": r(0.5), "s1": r(2), "s2": r(1), "s3": r(0), "sat_iii": r(0), "D6": r(3)}
    firm = {"rel_age": r(0), "rel_payout": r(1), "rel_rules": r(0), "rel_regulatory": r(2)}
    return {"codes": {"K-AAAA": copy.deepcopy(code), "K-BBBB": {**copy.deepcopy(code), "D6": r(2, unverified=True)}},
            "pairs": {"V-AAAA|K-AAAA": {"R": r(4), "A": r(3)}, "V-BBBB|K-AAAA": {"R": r(None), "A": r(1)}},
            "firms": {"V-AAAA": copy.deepcopy(firm), "V-BBBB": copy.deepcopy(firm)}}


def test_unmasks_to_schema_keys_and_carries_ratings_unchanged():
    out = U.unmask(ratings(), KEY, LISTED)
    assert set(out["codes"]) == {"MNQ", "NQ"}
    assert set(out["pairs"]) == {"topstep|MNQ", "lucid|MNQ"}
    assert set(out["firms"]) == {"topstep", "lucid"}
    assert out["codes"]["NQ"]["D6"] == {"value": 2, "unknown": False, "reason": "synthetic", "unverified": True}
    assert out["pairs"]["lucid|MNQ"]["R"]["value"] is None


@pytest.mark.parametrize("mutate,msg", [
    (lambda d: d["codes"].__setitem__("K-ZZZZ", d["codes"]["K-AAAA"]), "unknown contract label"),
    (lambda d: d["firms"].__setitem__("V-ZZZZ", d["firms"]["V-AAAA"]), "unknown firm label"),
    (lambda d: d["pairs"].__setitem__("V-AAAA|K-ZZZZ", {"R": r(1), "A": r(1)}), "unknown pair label"),
    (lambda d: d["codes"]["K-AAAA"].pop("D6"), "missing ratings"),
    (lambda d: d["codes"].pop("K-BBBB"), "not rated"),
    (lambda d: d["firms"].pop("V-BBBB"), "not rated"),
    (lambda d: d["pairs"].pop("V-BBBB|K-AAAA"), "listed pairs not rated"),
    (lambda d: d["pairs"]["V-AAAA|K-AAAA"].pop("A"), "missing ratings"),
    (lambda d: d["codes"]["K-AAAA"].__setitem__("D2b", r(0.7)), "outside the scale"),
    (lambda d: d["codes"]["K-AAAA"].__setitem__("s3", r(2)), "outside the scale"),
    (lambda d: d["codes"]["K-AAAA"].__setitem__("D6", r(5)), "outside the scale"),
    (lambda d: d["pairs"]["V-AAAA|K-AAAA"].__setitem__("R", r(0)), "outside the scale"),
    (lambda d: d["firms"]["V-AAAA"].__setitem__("rel_regulatory", r(1)), "outside the scale"),
    (lambda d: d["codes"]["K-AAAA"].__setitem__("D2a", r(True)), "not a number"),
    (lambda d: d["codes"]["K-AAAA"].__setitem__("D2a", 1), "must be an object"),
    (lambda d: d["codes"]["K-AAAA"].__setitem__("D7", r(1)), "unknown rating keys"),
])
def test_refuses_contract_breaks(mutate, msg):
    d = ratings()
    mutate(d)
    with pytest.raises(U.Refused, match=msg):
        U.unmask(d, KEY, LISTED)


def test_unlisted_pair_may_be_rated():
    d = ratings()
    d["pairs"]["V-BBBB|K-BBBB"] = {"R": r(2), "A": r(0)}
    assert U.unmask(d, KEY, LISTED)["pairs"]["lucid|NQ"]["A"]["value"] == 0


def test_cli_writes_file_and_refuses_with_exit_2(tmp_path):
    rp, kp, mp, op = (tmp_path / n for n in ("r.json", "k.json", "m.json", "o.json"))
    kp.write_text(json.dumps(KEY))
    mp.write_text(json.dumps({"pairs": {p: {"listed_on_modelled_plan": True} for p in LISTED}}))
    rp.write_text(json.dumps(ratings()))
    args = ["--ratings", str(rp), "--key", str(kp), "--masked-firms", str(mp), "--out", str(op)]
    assert U.main(args) == 0
    doc = json.loads(op.read_text())
    assert doc["spec_sha256"] == U.SPEC_SHA256 and set(doc["codes"]) == {"MNQ", "NQ"}
    bad = ratings()
    bad["codes"]["K-AAAA"]["D6"] = r(9)
    rp.write_text(json.dumps(bad))
    assert U.main(args) == 2
