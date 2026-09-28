"""Render reports/stage_e6_briefs/audit_k7/mutants.json as the audit report's markdown table."""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> None:
    rows = json.loads((HERE / "mutants.json").read_text(encoding="utf-8"))
    order = {"cp1.py": 0, "_port_common.py": 1, "cp2.py": 2, "cp3.py": 3, "expiry.py": 4,
             "rev2h.py": 5, "montrend.py": 6, "_event_common.py": 7, "_calendar.py": 8}
    rows.sort(key=lambda r: (order.get(r["file"], 9), r["id"]))
    out = ["| # | Mutant | File | What it tests | Result | Killing tests (count; first two) |",
           "|---|---|---|---|---|---|"]
    counts = {"KILLED": 0, "SURVIVED": 0, "PATTERN-MISS": 0}
    for i, r in enumerate(rows, 1):
        counts[r["status"]] = counts.get(r["status"], 0) + 1
        killed = r.get("killed_by", [])
        names = [k.split("::")[-1] for k in killed[:2]]
        cell = f"{len(killed)}; " + ", ".join(names) if killed else (
            r.get("detail", "") if r["status"] == "PATTERN-MISS" else "none")
        out.append(f"| {i} | {r['id']} | {r['file']} | {r['what']} | {r['status']} | {cell} |")
    out.append("")
    out.append(f"Totals: {len(rows)} mutants; " + ", ".join(f"{k} {v}" for k, v in counts.items()))
    (HERE / "mutants.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out[-3:]))
    for r in rows:
        if r["status"] != "KILLED":
            print("NON-KILLED:", r["id"], r["status"], r.get("summary", r.get("detail", ""))[:120])


if __name__ == "__main__":
    main()
