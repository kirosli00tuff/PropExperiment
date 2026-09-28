"""Stage E.5 Task A3: compare a research replay with the E.4 records, field by field, every file.

Usage: python3 reports/stage_e5_briefs/a3_compare.py CLUSTER OLD_DIR NEW_DIR OLD_SHA NEW_SHA OUT_MD [EXTRA_ALLOWED,...]
Every *.json of OLD_DIR must exist in NEW_DIR and vice versa. Only harness_sha256, created_utc (records,
cluster record) and record_sha256 (trip files, whose record bytes carry the harness sha256) may differ;
each trip file must carry the sha256 of its new record's bytes and its trips must sum to the record's
daily_net_usd. Exit 0 only when everything matches.
"""
from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

ALLOWED = {"harness_sha256", "created_utc", "record_sha256"}


def diff(a, b, path=""):
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


def trip_check(trips_path: Path) -> str:
    t = json.loads(trips_path.read_text())
    rec_path = trips_path.with_name(t["record_file"])
    rec = json.loads(rec_path.read_text())
    problems = []
    if t["record_sha256"] != hashlib.sha256(rec_path.read_bytes()).hexdigest():
        problems.append("record_sha256 is not the record's bytes")
    if rec.get("status") == "run":
        if len(t["trips"]) != rec["series"]["n_trips"]:
            problems.append(f"{len(t['trips'])} trips vs n_trips {rec['series']['n_trips']}")
        by_day: dict[str, Fraction] = {}
        for tr in t["trips"]:
            by_day[tr["trade_date"]] = by_day.get(tr["trade_date"], Fraction(0)) + Fraction(tr["net_cents"])
        for d, usd in zip(rec["series"]["dates"], rec["daily_net_usd"]):
            if float(by_day.pop(str(d), Fraction(0)) / 100) != usd:
                problems.append(f"{d}: trips sum != daily_net_usd {usd}")
                break
        if by_day:
            problems.append(f"trips outside the series: {sorted(by_day)[:3]}")
    return "; ".join(problems) or "ok"


def main() -> int:
    cluster, old_dir, new_dir, old_sha, new_sha, out = sys.argv[1:7]
    ALLOWED.update(a for a in sys.argv[7:8][0].split(",") if a) if len(sys.argv) > 7 else None  # C2: e.g. "power"
    old, new = Path(old_dir), Path(new_dir)
    names = sorted({p.name for p in old.glob("*.json")} | {p.name for p in new.glob("*.json")})
    rows, bad = [], 0
    for name in names:
        op, np_ = old / name, new / name
        if not op.is_file() or not np_.is_file():
            rows.append((name, f"MISSING in {'old' if not op.is_file() else 'new'}", "", "", "")); bad += 1
            continue
        a, b = json.loads(op.read_text()), json.loads(np_.read_text())
        d = diff(a, b)
        hs = ""
        if "harness_sha256" in a:
            ok_h = a["harness_sha256"] == old_sha and b["harness_sha256"] == new_sha
            hs = "ok" if ok_h else f"harness {a['harness_sha256'][:8]} -> {b['harness_sha256'][:8]}"
            d += [] if ok_h else ["harness"]
        tmsg = trip_check(np_) if name.endswith("_trips.json") else ""
        if tmsg not in ("", "ok"):
            d.append("trips: " + tmsg)
        s = b.get("screen") if isinstance(b.get("screen"), dict) else {}
        extra = f"n_trips {b['series']['n_trips']} mean {s.get('mean_ticks')} t {s.get('t_daily')}" \
            if isinstance(b.get("series"), dict) else ""
        rows.append((name, "MATCH" if not d else "DIFF: " + "; ".join(d[:4]), hs, tmsg, extra))
        bad += bool(d)
    lines = [f"# Stage E.5 Task A3: {cluster} research replay under the v5 working tree", "",
             f"Old records {old_dir} (harness {old_sha}); replay {new_dir} (harness {new_sha}).",
             f"Files compared: {len(names)}; matching field by field (only harness_sha256, created_utc and the trip "
             f"files' record_sha256 may differ): {len(names) - bad}/{len(names)}.", "",
             "| File | Result | Harness | Trip list | Replay figures |", "|---|---|---|---|---|"]
    lines += ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]
    Path(out).write_text("\n".join(lines) + "\n")
    print(f"{cluster}: {len(names) - bad}/{len(names)} files match")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
