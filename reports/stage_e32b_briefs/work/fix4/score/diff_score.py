"""Stage E.32b wave F, F1 step 5 (ScoreFixer-OpusHigh, 2026-10-29): compare score run 2 (05:40:30 PDT, copied to
work/score/score32b_out_run2.json) with run 3 (B/score32b_out.json after the RV1 S1/S3 fix).

Two passes:
1. a full recursive diff of the two JSON documents; every differing path is classed as ALLOWED (cost fields,
   input_checks, input hashes, generated time) or UNEXPECTED;
2. explicit named checks: per primary pair S, S_rounded, L1, L2, E R A D Rel P, m_star, m10K, status, gate_reasons,
   rank; Layer 1 rows; ties (pairs, ranks, decided_by); top 5, top 15, MNQ ranks, survivors, n_ranked; per variant
   every field of its summary.
Prints counts only; exit code 1 if anything UNEXPECTED differs.

Usage: python diff_score.py RUN2.json RUN3.json [--out diff.json]
"""
from __future__ import annotations

import argparse
import json
import sys

ALLOWED_KEYS = {"cost_per_attempt", "cost_per_attempt_lim", "input_checks", "generated_pdt"}
ALLOWED_PREFIXES = (("inputs",),)          # input paths and sha256 (econ32b.json was rewritten at 07:27:59)
PAIR_FIELDS = ("S", "S_rounded", "L1", "L2", "E", "R", "A", "D", "Rel", "P", "m_star", "m10K", "status",
               "gate_reasons", "rank", "econ_block", "room_a", "room_b")


def walk(a, b, path, out):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b), key=str):
            if k not in a or k not in b:
                out.append((path + (k,), "only in " + ("run3" if k not in a else "run2")))
            else:
                walk(a[k], b[k], path + (k,), out)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append((path, f"list length {len(a)} != {len(b)}"))
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, path + (i,), out)
    elif a != b:
        out.append((path, "value"))


def allowed(path) -> bool:
    if any(isinstance(p, str) and p in ALLOWED_KEYS for p in path):
        return True
    return any(path[:len(pre)] == pre for pre in ALLOWED_PREFIXES)


def pairs_by_key(doc):
    return {p["key"]: p for p in doc["primary"]["pairs"]}


def named_checks(r2, r3) -> dict:
    res = {}
    p2, p3 = pairs_by_key(r2), pairs_by_key(r3)
    res["pair keys equal"] = sorted(p2) == sorted(p3)
    res["pairs compared"] = len(p2)
    res["pair order equal"] = [p["key"] for p in r2["primary"]["pairs"]] == [p["key"] for p in r3["primary"]["pairs"]]
    bad = {f: [k for k in p2 if p2[k].get(f) != p3.get(k, {}).get(f)] for f in PAIR_FIELDS}
    res["pair field mismatches"] = {f: v for f, v in bad.items() if v}
    l2, l3 = r2["primary"]["layer1"], r3["primary"]["layer1"]
    res["layer1 codes compared"] = len(l2)
    res["layer1 rows differing"] = sorted(c for c in l2 if l2[c] != l3.get(c))
    for k in ("ties", "top15", "MNQ_ranks", "layer1_survivors", "n_ranked", "L1_below_2", "f5_handoff"):
        res[f"primary.{k} equal"] = r2["primary"].get(k) == r3["primary"].get(k)
    res["top5 equal"] = r2["primary"]["top15"][:5] == r3["primary"]["top15"][:5]
    res["n ties"] = len(r2["primary"]["ties"])
    res["moves_vs_e28 equal"] = r2["moves_vs_e28"] == r3["moves_vs_e28"]
    res["for_lead equal"] = r2["for_lead"] == r3["for_lead"]
    v2, v3 = r2["variants"], r3["variants"]
    res["variant names equal"] = sorted(v2) == sorted(v3)
    res["variants compared"] = len(v2)
    res["variants differing"] = sorted(n for n in v2 if v2[n] != v3.get(n))
    # cost fields: what changed, and the limit-case values now carried beside the market case
    ranked = [p for p in r3["primary"]["pairs"] if p["status"] == "ranked"]
    res["ranked pairs"] = len(ranked)
    res["run2 cost == run3 cost_per_attempt_lim (ranked)"] = sum(
        p2[p["key"]]["cost_per_attempt"] == p["cost_per_attempt_lim"] for p in ranked)
    res["run2 cost != run3 market cost (ranked)"] = sum(
        p2[p["key"]]["cost_per_attempt"] != p["cost_per_attempt"] for p in ranked)
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("run2")
    ap.add_argument("run3")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    with open(a.run2, encoding="utf-8") as fh:
        r2 = json.load(fh)
    with open(a.run3, encoding="utf-8") as fh:
        r3 = json.load(fh)
    diffs = []
    walk(r2, r3, (), diffs)
    unexpected = [(p, why) for p, why in diffs if not allowed(p)]
    by_key = {}
    for p, _ in diffs:
        if allowed(p):
            k = next((x for x in p if isinstance(x, str) and x in ALLOWED_KEYS), "inputs" if p[:1] == ("inputs",)
                     else "?")
            by_key[k] = by_key.get(k, 0) + 1
    named = named_checks(r2, r3)
    ok_named = (not named["pair field mismatches"] and not named["layer1 rows differing"]
                and not named["variants differing"] and named["pair keys equal"] and named["pair order equal"]
                and all(v for k, v in named.items() if k.endswith(" equal")))
    report = {"diff paths total": len(diffs), "allowed by key": by_key,
              "unexpected": [["/".join(map(str, p)), why] for p, why in unexpected], "named": named,
              "verdict": "only allowed fields differ" if not unexpected and ok_named else "UNEXPECTED DIFFERENCES"}
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=1)
    print(f"diff paths {len(diffs)}; allowed by key {by_key}; unexpected {len(unexpected)}")
    for p, why in unexpected[:20]:
        print("  UNEXPECTED", "/".join(map(str, p)), why)
    print({k: v for k, v in named.items() if k not in ("pair field mismatches",)})
    print("pair field mismatches:", named["pair field mismatches"])
    print("verdict:", report["verdict"])
    return 0 if report["verdict"] == "only allowed fields differ" else 1


if __name__ == "__main__":
    sys.exit(main())
