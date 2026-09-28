"""HarnessReviewer (E.5 A3): independent field-by-field comparison of the K4/K5 replays with E.4."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
IGNORE = {"harness_sha256", "created_utc"}


def strip(o, ignore):
    if isinstance(o, dict):
        return {k: strip(v, ignore) for k, v in o.items() if k not in ignore}
    if isinstance(o, list):
        return [strip(v, ignore) for v in o]
    return o


def diffpaths(a, b, path=""):
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append(f"{path}/{k} (missing on one side)")
            else:
                out += diffpaths(a[k], b[k], f"{path}/{k}")
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append(f"{path} (len {len(a)} vs {len(b)})")
        else:
            for i, (x, y) in enumerate(zip(a, b, strict=True)):
                out += diffpaths(x, y, f"{path}[{i}]")
    elif a != b:
        out.append(f"{path} ({a!r} vs {b!r})"[:160])
    return out


def walk_keys(o, key, found):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == key:
                found.add(v)
            walk_keys(v, key, found)
    elif isinstance(o, list):
        for v in o:
            walk_keys(v, key, found)


for old, new in (("reports/stage_e4_k4_screen", "reports/stage_e5_replay_k4"),
                 ("reports/stage_e4b_k5_screen", "reports/stage_e5_replay_k5")):
    oldp, newp = REPO / old, REPO / new
    of = sorted(p.name for p in oldp.glob("*.json"))
    nf = sorted(p.name for p in newp.glob("*.json"))
    print(f"{old}: {len(of)} json | {new}: {len(nf)} json | same names: {of == nf}")
    print("  only old:", sorted(set(of) - set(nf)), "| only new:", sorted(set(nf) - set(of)))
    print("  non-json old:", sorted(p.name for p in oldp.iterdir() if p.suffix != '.json')[:8],
          "| non-json new:", sorted(p.name for p in newp.iterdir() if p.suffix != '.json')[:8])
    n_match = 0
    h_old, h_new, rs_old, rs_new = set(), set(), set(), set()
    for name in sorted(set(of) & set(nf)):
        a = json.loads((oldp / name).read_text(encoding="utf-8"))
        b = json.loads((newp / name).read_text(encoding="utf-8"))
        walk_keys(a, "harness_sha256", h_old)
        walk_keys(b, "harness_sha256", h_new)
        ign = set(IGNORE)
        if name.endswith("_trips.json"):
            ign.add("record_sha256")
            walk_keys(a, "record_sha256", rs_old)
            walk_keys(b, "record_sha256", rs_new)
        d = diffpaths(strip(a, ign), strip(b, ign))
        if d:
            print("  DIFF", name, d[:6], "..." if len(d) > 6 else "")
        else:
            n_match += 1
    print(f"  matched: {n_match} of {len(set(of) & set(nf))}")
    print("  harness_sha256 old:", sorted(h_old), "| new:", sorted(h_new))
    print("  trip record_sha256 old==new:", rs_old == rs_new, "| n old", len(rs_old), "n new", len(rs_new))
