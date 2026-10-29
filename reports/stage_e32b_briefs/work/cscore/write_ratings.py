"""Write briefs/R2_Q_ratings.json (dossier by dossier, resumable) and briefs/R2_Q_ratings.md.

Usage: python -I write_ratings.py   (run from anywhere; paths are absolute from this file's location)
Prints only counts.
"""
import json
import os
import sys
from collections import Counter
from datetime import datetime
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from data_eq import DOSSIERS_EQ  # noqa: E402
from data_zl_pools import DOSSIERS_POOLS, DOSSIERS_ZL  # noqa: E402
from flags import FLAGS, RULES  # noqa: E402

BRIEFS = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT_JSON = os.path.join(BRIEFS, "R2_Q_ratings.json")
OUT_MD = os.path.join(BRIEFS, "R2_Q_ratings.md")
RATER = "CombinationScorer-OpusXHigh"
ALL = DOSSIERS_EQ + DOSSIERS_ZL + DOSSIERS_POOLS


def now_pdt() -> str:
    return datetime.now(ZoneInfo("America/Vancouver")).strftime("%Y-%m-%d %H:%M:%S %Z")


def load() -> dict:
    if os.path.exists(OUT_JSON):
        with open(OUT_JSON) as fh:
            return json.load(fh)
    return {"rater": RATER, "generated_pdt": now_pdt(), "ratings": {}}


def save(doc: dict) -> None:
    tmp = OUT_JSON + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(doc, fh, indent=1)
    os.replace(tmp, OUT_JSON)


def entry(value: int, reason: str, q2: bool) -> dict:
    out = {"value": value, "unknown": False, "reason": reason}
    if q2:
        out["unverified"] = False
    return out


def rate_dossier(d: dict) -> dict:
    out = {}
    for cid, _band, _short in d["ids"]:
        rec = {}
        for q in ("Q1", "Q2", "Q3"):
            value, reason = d.get("override", {}).get(cid, {}).get(q, d[q])
            rec[q] = entry(value, reason, q == "Q2")
        out[cid] = rec
    return out


def write_json() -> dict:
    doc = load()
    for d in ALL:
        ids = [c for c, _, _ in d["ids"]]
        if all(c in doc["ratings"] for c in ids):
            continue  # resume: dossier already written
        doc["ratings"].update(rate_dossier(d))
        doc["generated_pdt"] = now_pdt()
        save(doc)
    return doc


def check(doc: dict) -> None:
    want = {f"C{n:03d}" for n in range(1, 186)}
    got = set(doc["ratings"])
    listed = [c for d in ALL for c, _, _ in d["ids"]]
    assert len(listed) == len(set(listed)) == 185, (len(listed), len(set(listed)))
    assert got == want, (sorted(want - got), sorted(got - want))


def write_md(doc: dict) -> Counter:
    r = doc["ratings"]
    counts = Counter()
    lines = [
        "# R2 Q1-Q3 ratings (Stage E.32b step 3b)",
        "",
        f"Rater: {RATER} (worker-xhigh, opus, fresh context). Generated {doc['generated_pdt']}. "
        "Inputs read: brief_wave_d.md section D2 and R2_dossiers_for_rating.md only (no combinations file, ranking, "
        "F5 or score). Q4-Q7 are the script's. JSON: R2_Q_ratings.json (185 ids). Helper code: work/cscore/.",
        "",
        "## Rules applied",
        "",
    ]
    lines += [f"- {x}" for x in RULES]
    lines += ["", "## Ratings by dossier", "",
              "Q values are integers 0-4; 'unv' is the Q2 evidence-rule flag (none set). Every id in a dossier shares "
              "the dossier's mechanism, evidence and closed-line overlap; the reasons are in the JSON and, per dossier, "
              "below each table.", ""]
    for d in ALL:
        lines += [f"### {d['dossier']}", "", "| id | band | shortest | Q1 | Q2 | Q3 | unv |", "|---|---|---|---|---|---|---|"]
        for cid, band, short in d["ids"]:
            q = r[cid]
            for k in ("Q1", "Q2", "Q3"):
                counts[(k, q[k]["value"])] += 1
            lines.append(f"| {cid} | {band} | {short} | {q['Q1']['value']} | {q['Q2']['value']} | "
                         f"{q['Q3']['value']} | {'yes' if q['Q2']['unverified'] else 'no'} |")
        first = d["ids"][0][0]
        lines += ["", f"- Q1: {r[first]['Q1']['reason']}", f"- Q2: {r[first]['Q2']['reason']}",
                  f"- Q3: {r[first]['Q3']['reason']}"]
        for cid, ov in d.get("override", {}).items():
            for k, (_v, reason) in ov.items():
                lines.append(f"- {k} ({cid}): {reason}")
        lines.append("")
    lines += ["## Counts", "", "| Q | 0 | 1 | 2 | 3 | 4 |", "|---|---|---|---|---|---|"]
    for k in ("Q1", "Q2", "Q3"):
        lines.append(f"| {k} | " + " | ".join(str(counts[(k, v)]) for v in range(5)) + " |")
    unv = sum(1 for q in r.values() if q["Q2"]["unverified"])
    lines += ["", f"Q2 unverified: {unv}. Q unknown: "
              f"{sum(1 for q in r.values() for k in ('Q1', 'Q2', 'Q3') if q[k]['unknown'])}.", ""]
    zero = [(c, r[c]["Q3"]["reason"]) for c in sorted(r) if r[c]["Q3"]["value"] == 0]
    lines += ["## Q3 = 0 (gate: excluded) with the closed line", "", "| id | closed line |", "|---|---|"]
    lines += [f"| {c} | {reason} |" for c, reason in zero]
    lines += ["", "## Flags for the lead", ""]
    lines += [f"{i}. {x}" for i, x in enumerate(FLAGS, 1)]
    lines.append("")
    with open(OUT_MD, "w") as fh:
        fh.write("\n".join(lines))
    return counts


def main() -> None:
    doc = write_json()
    check(doc)
    counts = write_md(doc)
    for k in ("Q1", "Q2", "Q3"):
        print(k, {v: counts[(k, v)] for v in range(5)})
    print("ids", len(doc["ratings"]), "unverified", sum(1 for q in doc["ratings"].values() if q["Q2"]["unverified"]))
    print("Q3=0", [c for c in sorted(doc["ratings"]) if doc["ratings"][c]["Q3"]["value"] == 0])


if __name__ == "__main__":
    main()
