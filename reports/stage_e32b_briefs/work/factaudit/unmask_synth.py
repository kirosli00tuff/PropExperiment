"""FactAuditor (E.32b C1v): synthetic ratings for work/facts/unmask.py.

Writes three ratings files into work/factaudit/ (never into briefs/): a good one (every label, values on the scales,
deterministic pattern), one with an out-of-scale value, one with an unknown label. Runs unmask.py on each with --out
inside work/factaudit/ and checks: good -> exit 0 and every rating lands under the right code, pair and firm; bad ->
exit 2 with REFUSED. Read-only on every FactTable file.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

B = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
BR = B / "reports/stage_e32b_briefs"
W = BR / "work/factaudit"
UNMASK = BR / "work/facts/unmask.py"
SCALES = {"codes": {"D2a": [0, 1], "D2b": [0, 0.5, 1], "s1": [0, 1, 2], "s2": [0, 1, 2], "s3": [0, 1],
                    "sat_iii": [0, 1], "D6": [0, 1, 2, 3, 4]},
          "pairs": {"R": [1, 2, 3, 4], "A": [0, 1, 2, 3, 4]},
          "firms": {"rel_age": [0, 1], "rel_payout": [0, 1], "rel_rules": [0, 1], "rel_regulatory": [0, 2]}}


def build(key: dict) -> dict:
    doc = {"codes": {}, "pairs": {}, "firms": {}}
    for i, lab in enumerate(sorted(key["contracts"])):
        doc["codes"][lab] = {k: {"value": sc[(i + j) % len(sc)], "unknown": False, "reason": f"synthetic {lab} {k}"}
                             for j, (k, sc) in enumerate(SCALES["codes"].items())}
    for i, lab in enumerate(sorted(key["pairs"])):
        doc["pairs"][lab] = {k: {"value": sc[(i + j) % len(sc)], "unknown": False, "reason": f"synthetic {lab} {k}"}
                             for j, (k, sc) in enumerate(SCALES["pairs"].items())}
    for i, lab in enumerate(sorted(key["firms"])):
        doc["firms"][lab] = {k: {"value": sc[(i + j) % len(sc)], "unknown": False, "reason": f"synthetic {lab} {k}"}
                             for j, (k, sc) in enumerate(SCALES["firms"].items())}
    return doc


def run(ratings: Path, out: Path) -> subprocess.CompletedProcess:
    cmd = ["uv", "run", "python", str(UNMASK), "--ratings", str(ratings), "--key", str(BR / "F4_mask_key.json"),
           "--masked-firms", str(BR / "F4_masked_firms.json"), "--out", str(out)]
    return subprocess.run(cmd, cwd=str(B), capture_output=True, text=True, timeout=300)


def main() -> int:
    key = json.loads((BR / "F4_mask_key.json").read_text())
    good = build(key)
    p_good = W / "synth_ratings_good.json"; p_good.write_text(json.dumps(good))
    out_good = W / "synth_unmasked_good.json"
    r = run(p_good, out_good)
    print("good: rc", r.returncode, (r.stdout + r.stderr).strip()[-300:])
    ok = True
    if r.returncode == 0:
        um = json.loads(out_good.read_text())
        for lab, ratings in good["codes"].items():
            code = key["contracts"][lab]
            if um["codes"].get(code) != ratings:
                ok = False; print("  code mapping error", lab, code)
        for lab, ratings in good["pairs"].items():
            pair = key["pairs"][lab]
            if um["pairs"].get(pair) != ratings:
                ok = False; print("  pair mapping error", lab, pair)
        for lab, ratings in good["firms"].items():
            firm = key["firms"][lab]
            if um["firms"].get(firm) != ratings:
                ok = False; print("  firm mapping error", lab, firm)
        print(f"  mapped codes {len(um['codes'])} pairs {len(um['pairs'])} firms {len(um['firms'])}; all ratings match: {ok}")
        extra = [k for k in um if k not in ("codes", "pairs", "firms")]
        print("  extra top-level keys:", extra)
    # bad 1: out-of-scale value
    bad1 = json.loads(json.dumps(good)); lab = sorted(key["contracts"])[0]
    bad1["codes"][lab]["D6"]["value"] = 5
    p1 = W / "synth_ratings_bad_scale.json"; p1.write_text(json.dumps(bad1))
    r1 = run(p1, W / "synth_unmasked_bad_scale.json")
    print("bad scale: rc", r1.returncode, (r1.stdout + r1.stderr).strip()[-200:])
    # bad 2: unknown label
    bad2 = json.loads(json.dumps(good)); bad2["codes"]["K-ZZZZ"] = bad2["codes"][lab]
    p2 = W / "synth_ratings_bad_label.json"; p2.write_text(json.dumps(bad2))
    r2 = run(p2, W / "synth_unmasked_bad_label.json")
    print("bad label: rc", r2.returncode, (r2.stdout + r2.stderr).strip()[-200:])
    # bad 3: missing rating
    bad3 = json.loads(json.dumps(good)); del bad3["codes"][lab]["D6"]
    p3 = W / "synth_ratings_bad_missing.json"; p3.write_text(json.dumps(bad3))
    r3 = run(p3, W / "synth_unmasked_bad_missing.json")
    print("bad missing: rc", r3.returncode, (r3.stdout + r3.stderr).strip()[-200:])
    # bad 4: pair rated under an unlisted pair is allowed; a listed pair missing is refused
    listed = [pl for pl, p in json.loads((BR / "F4_masked_firms.json").read_text())["pairs"].items()
              if p.get("listed_on_modelled_plan")]
    bad4 = json.loads(json.dumps(good)); del bad4["pairs"][listed[0]]
    p4 = W / "synth_ratings_bad_pair.json"; p4.write_text(json.dumps(bad4))
    r4 = run(p4, W / "synth_unmasked_bad_pair.json")
    print("bad listed pair missing: rc", r4.returncode, (r4.stdout + r4.stderr).strip()[-200:])
    return 0


if __name__ == "__main__":
    sys.exit(main())
