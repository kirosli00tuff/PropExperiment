"""Check the P3.6 rule-3 parse rule of protocol v0.3 against the two release-calendar CSVs.

Prints hashes, headers, distinct (report, time_et) counts and per-month valid NOPA counts. No row text.
"""
from __future__ import annotations

import csv
import hashlib
import re
from collections import Counter
from pathlib import Path

ROOT = Path("/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e31_briefs/research")
FILES = ["usda_releases.csv", "usda_releases_ext.csv"]
KEEP = {"USDA WASDE", "NASS Crop Production", "NASS Crop Production Annual", "NASS Grain Stocks",
        "NASS Prospective Plantings", "NASS Acreage", "NOPA Monthly Crush (not USDA)"}
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


def main() -> None:
    months: Counter[str] = Counter()
    for name in FILES:
        p = ROOT / name
        raw = p.read_bytes()
        print(name, "sha256", hashlib.sha256(raw).hexdigest())
        lines = [ln for ln in raw.decode().splitlines() if not ln.startswith("#")]
        print("  comment lines skipped:", sum(1 for ln in raw.decode().splitlines() if ln.startswith("#")))
        rows = list(csv.DictReader(lines))
        print("  header:", list(rows[0].keys()) if rows else None, "rows:", len(rows))
        valid = [r for r in rows if DATE.fullmatch(r.get("date", "") or "")]
        print("  rows with invalid date:", len(rows) - len(valid))
        dates = sorted(r["date"] for r in valid)
        print("  date range of valid rows:", dates[0], dates[-1])
        combo = Counter((r["report"], r["time_et"]) for r in valid)
        for (rep, t), n in sorted(combo.items()):
            print(f"    {rep!r:42} time_et={t!r:8} n={n}  kept={rep in KEEP and t == '12:00'}")
        for r in valid:
            if r["report"] == "NOPA Monthly Crush (not USDA)" and r["time_et"] == "12:00":
                months[r["date"][:7]] += 1
    all_months = []
    y, m = 2020, 12
    while (y, m) <= (2024, 2):
        all_months.append(f"{y}-{m:02d}")
        m += 1
        if m == 13:
            y, m = y + 1, 1
    missing = [mo for mo in all_months if months.get(mo, 0) == 0]
    dup = [mo for mo in all_months if months.get(mo, 0) > 1]
    print("months 2020-12..2024-02:", len(all_months), "valid NOPA months:", sum(1 for mo in all_months if months.get(mo)),
          "months without a valid NOPA row:", missing, "months with >1:", dup)


if __name__ == "__main__":
    main()
