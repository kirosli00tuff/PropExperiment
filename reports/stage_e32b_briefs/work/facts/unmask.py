"""Unmask the BlindScorer's ratings (Stage E.32b, FactTable output 6).

Reads briefs/F4_blind_ratings_masked.json (SCHEMA.md section 3 shape with masked labels: "codes" keyed by contract
label, "pairs" keyed "<firm label>|<contract label>", "firms" keyed by firm label; each rating
R = {"value", "unknown", "reason"} plus optional "unverified": true) and briefs/F4_mask_key.json, and writes
briefs/F4_blind_unmasked.json exactly as SCHEMA.md section 3 (codes by CODE, pairs by "firm|CODE", firms by firm).
Each rating dict is carried over unchanged (including "unverified").

Refuses (exit 2, "REFUSED: ...") on an unknown label, a missing rating, a rating that is not an object, or a value
outside its scale. Required: all 47 codes x 7 keys, all 5 firms x 4 keys, and R and A for every pair the masked firm
sheet lists on the modelled plan (unlisted pairs may be rated; they are unmasked and checked the same way).

Run: uv run python reports/stage_e32b_briefs/work/facts/unmask.py [--ratings P] [--key P] [--masked-firms P] [--out P]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

B = Path(__file__).resolve().parents[2]
SPEC_SHA256 = "09ebe6970fcf027009152fa81a414360a015d535b095138cdf65cf1a4eb58635"

SCALES = {
    "codes": {"D2a": (0, 1), "D2b": (0, 0.5, 1), "s1": (0, 1, 2), "s2": (0, 1, 2), "s3": (0, 1),
              "sat_iii": (0, 1), "D6": (0, 1, 2, 3, 4)},
    "pairs": {"R": (1, 2, 3, 4), "A": (0, 1, 2, 3, 4)},
    "firms": {"rel_age": (0, 1), "rel_payout": (0, 1), "rel_rules": (0, 1), "rel_regulatory": (0, 2)},
}


class Refused(ValueError):
    """A contract break: the ratings file cannot be unmasked."""


def _check_rating(where: str, r, scale: tuple) -> dict:
    if not isinstance(r, dict):
        raise Refused(f"{where}: rating must be an object {{value, unknown, reason}}, got {r!r}")
    v = r.get("value")
    if v is None:
        return r
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
        raise Refused(f"{where}: value {v!r} is not a number")
    if not any(abs(v - s) < 1e-12 for s in scale):
        raise Refused(f"{where}: value {v!r} outside the scale {list(scale)}")
    if "unverified" in r and not isinstance(r["unverified"], bool):
        raise Refused(f"{where}: 'unverified' must be true or false")
    return r


def _block(doc: dict, name: str) -> dict:
    b = doc.get(name)
    if not isinstance(b, dict):
        raise Refused(f"ratings: '{name}' object missing")
    return b


def unmask(ratings: dict, key: dict, listed_masked_pairs: set[str]) -> dict:
    """The unmasked document (SCHEMA.md section 3) from the masked ratings and the mask key."""
    ck, fk = key["contracts"], key["firms"]
    out = {"codes": {}, "pairs": {}, "firms": {}}
    codes, pairs, firms = (_block(ratings, n) for n in ("codes", "pairs", "firms"))
    for lab, rec in codes.items():
        if lab not in ck:
            raise Refused(f"codes: unknown contract label {lab!r}")
        if not isinstance(rec, dict):
            raise Refused(f"codes.{lab}: not an object")
        out["codes"][ck[lab]] = {k: _check_rating(f"codes.{lab}.{k}", rec.get(k), sc) if k in rec else None
                                 for k, sc in SCALES["codes"].items()}
        missing = [k for k in SCALES["codes"] if k not in rec]
        if missing:
            raise Refused(f"codes.{lab}: missing ratings {missing}")
        extra = sorted(set(rec) - set(SCALES["codes"]))
        if extra:
            raise Refused(f"codes.{lab}: unknown rating keys {extra}")
    lack = sorted(set(ck.values()) - set(out["codes"]))
    if lack:
        raise Refused(f"codes: {len(lack)} contracts not rated (labels {sorted(l for l, c in ck.items() if c in lack)})")
    for lab, rec in firms.items():
        if lab not in fk:
            raise Refused(f"firms: unknown firm label {lab!r}")
        missing = [k for k in SCALES["firms"] if k not in (rec or {})]
        if missing:
            raise Refused(f"firms.{lab}: missing ratings {missing}")
        extra = sorted(set(rec) - set(SCALES["firms"]))
        if extra:
            raise Refused(f"firms.{lab}: unknown rating keys {extra}")
        out["firms"][fk[lab]] = {k: _check_rating(f"firms.{lab}.{k}", rec[k], sc) for k, sc in SCALES["firms"].items()}
    lack = sorted(set(fk.values()) - set(out["firms"]))
    if lack:
        raise Refused(f"firms: not rated: {lack}")
    for lab, rec in pairs.items():
        parts = lab.split("|")
        if len(parts) != 2 or parts[0] not in fk or parts[1] not in ck:
            raise Refused(f"pairs: unknown pair label {lab!r}")
        missing = [k for k in SCALES["pairs"] if k not in (rec or {})]
        if missing:
            raise Refused(f"pairs.{lab}: missing ratings {missing}")
        extra = sorted(set(rec) - set(SCALES["pairs"]))
        if extra:
            raise Refused(f"pairs.{lab}: unknown rating keys {extra}")
        out["pairs"][f"{fk[parts[0]]}|{ck[parts[1]]}"] = {
            k: _check_rating(f"pairs.{lab}.{k}", rec[k], sc) for k, sc in SCALES["pairs"].items()}
    lack = sorted(listed_masked_pairs - set(pairs))
    if lack:
        raise Refused(f"pairs: {len(lack)} listed pairs not rated, e.g. {lack[:5]}")
    return out


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ratings", default=str(B / "F4_blind_ratings_masked.json"))
    ap.add_argument("--key", default=str(B / "F4_mask_key.json"))
    ap.add_argument("--masked-firms", default=str(B / "F4_masked_firms.json"))
    ap.add_argument("--out", default=str(B / "F4_blind_unmasked.json"))
    a = ap.parse_args(argv)
    try:
        ratings = json.loads(Path(a.ratings).read_text())
        key = json.loads(Path(a.key).read_text())
        mf = json.loads(Path(a.masked_firms).read_text())
        listed = {k for k, v in (mf.get("pairs") or {}).items() if v.get("listed_on_modelled_plan") is True}
        doc = unmask(ratings, key, listed)
    except (Refused, OSError, json.JSONDecodeError, KeyError) as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 2
    doc = {"spec_sha256": SPEC_SHA256,
           "generated_pdt": datetime.now(ZoneInfo("America/Vancouver")).strftime("%Y-%m-%d %H:%M %Z"),
           "generated_by": "reports/stage_e32b_briefs/work/facts/unmask.py",
           "inputs": {"ratings": {"path": a.ratings, "sha256": sha256(Path(a.ratings))},
                      "key": {"path": a.key, "sha256": sha256(Path(a.key))}},
           **doc}
    Path(a.out).write_text(json.dumps(doc, indent=1, ensure_ascii=False))
    print(f"wrote {a.out}: {len(doc['codes'])} codes, {len(doc['pairs'])} pairs, {len(doc['firms'])} firms")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
