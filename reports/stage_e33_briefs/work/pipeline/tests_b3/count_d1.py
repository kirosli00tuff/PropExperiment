"""B3 latent difference D1: how often the real ZM data can trigger it. Over the 816 trade dates (data33.load_zm through
guard33): records of the ZM front carrying F_MAYBE_BAD_BOOK, how many of them are R records (D1: A's book is good
after such an R, B's stays bad until the next R), and how many fall in 08:35-13:20 CT. Counts only (book records;
no outcome). Output JSON path as argv[1]."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import cal33  # noqa: E402
import data33  # noqa: E402

os.nice(10)
BAD, R = 1 << 2, ord("R")
out = {"dates": 0, "bad_records": 0, "bad_R_records": 0, "bad_in_day_window": 0, "dates_with_bad": [],
       "dates_with_bad_R": []}
for d in cal33.trade_dates():
    rec = data33.load_zm(d)
    fr = int(cal33.fronts(d)["ZM"])
    r = rec[rec["instrument_id"] == fr]
    bad = (r["flags"] & BAD) != 0
    out["dates"] += 1
    n = int(bad.sum())
    if n:
        lo, hi = cal33.ct_ns(d, "08:35:00"), cal33.ct_ns(d, "13:20:00")
        ts = r["ts_recv"][bad]
        nr = int(((r["action"] == R) & bad).sum())
        out["bad_records"] += n
        out["bad_R_records"] += nr
        out["bad_in_day_window"] += int(((ts >= lo) & (ts < hi)).sum())
        out["dates_with_bad"].append(d.isoformat())
        if nr:
            out["dates_with_bad_R"].append(d.isoformat())
Path(sys.argv[1]).write_text(json.dumps(out, indent=1))
print(json.dumps({k: (len(v) if isinstance(v, list) else v) for k, v in out.items()}))
