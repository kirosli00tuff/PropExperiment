"""merge_q.py: merge the CombinationScorer's Q1-Q3 ratings into the combinations file (Stage E.32b step 3b).

Reads briefs/R2_combinations_unrated.json (build_combos.py) and briefs/R2_Q_ratings.json
({"rater", "generated_pdt", "ratings": {"<id>": {"Q1": R, "Q2": R, "Q3": R}}}, R = {"value", "unknown", "reason"}
plus an optional boolean "unverified"), and writes briefs/R2_combinations.json (work/score/SCHEMA.md section 7, the
input of r3_score.py). Refuses (exit 2, nothing written) when the spec hash is not the frozen one, a combination id
has no rating, a rating names an unknown id, a Q1-Q3 entry is missing, unknown, null, not an integer in 0..4, lacks a
reason, or carries a non-boolean "unverified". Ratings are copied unchanged; r3_score.py applies the Q2 evidence cap.

Run: uv run python reports/stage_e32b_briefs/work/R2/merge_q.py [--unrated P] [--ratings P] [--out P]
"""
from __future__ import annotations

import argparse
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from r2_common import (  # noqa: E402
    COMBOS_RATED, COMBOS_UNRATED, Q_RATINGS, SPEC_SHA256, check_spec, load, now_pdt, sha256_file, write_json,
)

Q_KEYS = ("Q1", "Q2", "Q3")
SCALE = (0, 1, 2, 3, 4)


class Refused(Exception):
    pass


def check_rating(cid: str, key: str, rt) -> dict:
    if not isinstance(rt, dict):
        raise Refused(f"{cid} {key}: rating missing")
    if rt.get("unknown") is True:
        raise Refused(f"{cid} {key}: unknown = true (every combination needs a rating)")
    v = rt.get("value")
    if v is None:
        raise Refused(f"{cid} {key}: value missing or null")
    if isinstance(v, bool) or not isinstance(v, (int, float)) or float(v) != int(v) or int(v) not in SCALE:
        raise Refused(f"{cid} {key}: value {v!r} out of scale (integers 0-4)")
    reason = rt.get("reason")
    if not isinstance(reason, str) or not reason.strip():
        raise Refused(f"{cid} {key}: reason missing")
    if "unverified" in rt and not isinstance(rt["unverified"], bool):
        raise Refused(f"{cid} {key}: unverified must be true or false")
    out = {"value": int(v), "unknown": False, "reason": reason}
    if "unverified" in rt:
        out["unverified"] = rt["unverified"]
    return out


def merge(unrated: dict, ratings_doc: dict) -> dict:
    if unrated.get("spec_sha256") not in (None, SPEC_SHA256):
        raise Refused("combinations file: spec_sha256 is not the frozen hash")
    ratings = ratings_doc.get("ratings")
    if not isinstance(ratings, dict):
        raise Refused("ratings file: 'ratings' must be an object keyed by combination id")
    ids = [str(c["id"]) for c in unrated["combinations"]]
    if len(set(ids)) != len(ids):
        raise Refused("combinations file: duplicate ids")
    missing = [i for i in ids if i not in ratings]
    extra = sorted(set(ratings) - set(ids))
    if missing:
        raise Refused(f"no rating for {len(missing)} ids: {missing[:10]}")
    if extra:
        raise Refused(f"ratings for {len(extra)} unknown ids: {extra[:10]}")
    out = copy.deepcopy(unrated)
    for c in out["combinations"]:
        if any(k in c for k in Q_KEYS):
            raise Refused(f"{c['id']}: the unrated file already carries Q1-Q3")
        rt = ratings[str(c["id"])]
        if not isinstance(rt, dict):
            raise Refused(f"{c['id']}: rating entry is not an object")
        for k in Q_KEYS:
            c[k] = check_rating(str(c["id"]), k, rt.get(k))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--unrated", default=str(COMBOS_UNRATED))
    ap.add_argument("--ratings", default=str(Q_RATINGS))
    ap.add_argument("--out", default=str(COMBOS_RATED))
    args = ap.parse_args(argv)
    try:
        check_spec()
        unrated, ratings_doc = load(args.unrated), load(args.ratings)
        merged = merge(unrated, ratings_doc)
    except (Refused, SystemExit, OSError, ValueError, KeyError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    merged["q_ratings"] = {"path": args.ratings, "sha256": sha256_file(args.ratings),
                           "rater": ratings_doc.get("rater"), "generated_pdt": ratings_doc.get("generated_pdt")}
    merged["unrated_source"] = {"path": args.unrated, "sha256": sha256_file(args.unrated)}
    merged["merged_pdt"] = now_pdt()
    merged["merged_by"] = "reports/stage_e32b_briefs/work/R2/merge_q.py"
    write_json(args.out, merged)
    print(f"merged {len(merged['combinations'])} combinations -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
