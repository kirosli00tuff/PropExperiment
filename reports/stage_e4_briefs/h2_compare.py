"""Stage E.4 Task H2: compare the K2 regression replay with E.3's records, field by field.

Usage: python3 reports/stage_e4_briefs/h2_compare.py <new harness sha256>
Reads reports/stage_e3_k2_screen/*.json (E.3) and reports/stage_e4_k2_regression/*.json (the replay),
writes reports/stage_e4_k2_regression.md. Only harness_sha256 and created_utc may differ.
"""
from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT / "reports/stage_e3_k2_screen"
NEW = ROOT / "reports/stage_e4_k2_regression"
OUT = ROOT / "reports/stage_e4_k2_regression.md"
ALLOWED = {"harness_sha256", "created_utc"}
OLD_HARNESS = "cf939270f0a00be74aa29a43f0c7de964256411a9cdcebc36f22fd3bdc021a45"


def diff(a, b, path=""):
    """Every path where a and b differ, skipping ALLOWED keys at any depth."""
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b)):
            if k in ALLOWED:
                continue
            if k not in a or k not in b:
                out.append(f"{path}/{k} (only in {'new' if k in b else 'old'})")
            else:
                out.extend(diff(a[k], b[k], f"{path}/{k}"))
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [f"{path} (length {len(a)} vs {len(b)})"]
        out = []
        for i, (x, y) in enumerate(zip(a, b)):
            out.extend(diff(x, y, f"{path}[{i}]"))
        return out
    return [] if a == b and type(a) is type(b) else [f"{path}: {a!r} != {b!r}"]


def frac(v) -> Fraction:
    if isinstance(v, dict):  # {"exact": "p/q", "float": x} or similar
        v = v.get("exact", v.get("value"))
    return Fraction(v) if isinstance(v, str) else Fraction(v)


def trip_check(rec: dict, rec_path: Path) -> tuple[bool, str]:
    trips_path = rec_path.with_name(rec_path.stem + "_trips.json")
    if not trips_path.is_file():
        return False, "no trip file"
    t = json.loads(trips_path.read_text())
    problems = []
    rec_sha = hashlib.sha256(rec_path.read_bytes()).hexdigest()
    shas = [v for k, v in t.items() if "sha256" in k and isinstance(v, str)]
    if rec_sha not in shas:
        problems.append("record sha256 not in trip file")
    trips = t.get("trips", [])
    if rec.get("status") == "run":
        if len(trips) != rec["series"]["n_trips"]:
            problems.append(f"{len(trips)} trips vs n_trips {rec['series']['n_trips']}")
        by_day: dict[str, Fraction] = {}
        for tr in trips:
            d = str(tr["trade_date"])
            by_day[d] = by_day.get(d, Fraction(0)) + frac(tr["net_cents"])
        dates = rec["series"]["dates"]
        for d, usd in zip(dates, rec["daily_net_usd"]):
            if float(by_day.pop(str(d), Fraction(0)) / 100) != usd:
                problems.append(f"{d}: trips sum != daily_net_usd {usd}")
                break
        if by_day:
            problems.append(f"trips on dates outside the series: {sorted(by_day)[:3]}")
    return not problems, "; ".join(problems) or "ok"


def main() -> int:
    new_sha = sys.argv[1]
    olds = sorted(p for p in OLD.glob("K2_*_research.json") if not p.name.endswith("_cluster.json"))
    rows, n_match, n_trip_ok = [], 0, 0
    for op in olds:
        np_ = NEW / op.name
        if not np_.is_file():
            rows.append((op.name, "MISSING", "", "", "", "", "", "")); continue
        a, b = json.loads(op.read_text()), json.loads(np_.read_text())
        d = diff(a, b)
        harness_ok = a["harness_sha256"] == OLD_HARNESS and b["harness_sha256"] == new_sha
        ok = not d and harness_ok
        n_match += ok
        tok, tmsg = trip_check(b, np_)
        n_trip_ok += tok
        s = b.get("screen") or {}
        cov = ",".join(f"{r}:{c['ratio']:.4f}" for r, c in b["coverage"].items())
        rows.append((op.name.removeprefix("K2_").removesuffix("_research.json"),
                     "MATCH" if ok else "DIFF: " + "; ".join(d[:3]) + ("" if harness_ok else " harness"),
                     b["series"]["n_trips"] if b.get("series") else "-",
                     f"{s.get('mean_ticks', float('nan')):.6f}", f"{s.get('t_daily') if s.get('t_daily') is None else round(s['t_daily'], 6)}",
                     cov, ",".join(b.get("labels", [])) or "-", tmsg))
    oc = json.loads((OLD / "K2_research_cluster.json").read_text())
    nc = json.loads((NEW / "K2_research_cluster.json").read_text())
    cd = diff(oc, nc)
    tiers_new = {m["member_id"]: m.get("tier") for m in nc["tiers"]["members"]} if nc.get("tiers") else {}
    lines = ["# Stage E.4 Task H2: K2 regression replay under the fixed harness", "",
             f"Old harness {OLD_HARNESS}; replay harness {new_sha}.",
             f"Records compared: {len(olds)}; field-by-field match (only harness_sha256 and created_utc may differ): {n_match}/{len(olds)}.",
             f"Trip lists that sum to their record's daily series (and carry its sha256): {n_trip_ok}/{len(olds)}.",
             f"Cluster record (tiers, members, refusals): {'MATCH' if not cd else 'DIFF: ' + '; '.join(cd[:5])}.",
             f"Tiers in the replay: {sorted(set(tiers_new.values()))} over {len(tiers_new)} members.", "",
             "| Trial | Record vs E.3 | n_trips | mean ticks | daily t | coverage | labels | trip list |",
             "|---|---|---|---|---|---|---|---|"]
    lines += ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]
    OUT.write_text("\n".join(lines) + "\n")
    print(f"match {n_match}/{len(olds)} trips_ok {n_trip_ok}/{len(olds)} cluster {'MATCH' if not cd else 'DIFF'}")
    return 0 if n_match == len(olds) and n_trip_ok == len(olds) and not cd else 1


if __name__ == "__main__":
    sys.exit(main())
