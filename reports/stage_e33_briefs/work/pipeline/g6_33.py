"""G6 clock report (P4 G6; brief_DataCoder deliverable 5): per month, the median, p1 and p99 of
ts_recv - ts_event for ZM, ZS and ZL side by side; months whose medians differ by more than
100 ms are flagged. A data check: no outcome is involved.

Records: every record of the 816 trade dates' per-day stores (ZM: E.31's Z1 store, all ZM
instrument ids, plus a ZM front-only column; ZS/ZL: the E.33 split), grouped by the trade date's
month, except records flagged F_SNAPSHOT or F_BAD_TS_RECV (READING G6-1: their ts_recv is the
snapshot generation time, or inaccurate). Quantiles: numpy.percentile (linear) on int64 ns.

CLI: g6_33.py run ZM|ZS|ZL (resumable per month; partials under DERIVED/probes/g6/), then
g6_33.py report (writes reports/stage_e33_briefs/work/G6_clock_report.md). Refuses to start a new
month between 15:28 and 16:00 America/Vancouver (exit 3).
"""

# ruff: noqa: I001 - cal33/data33 set sys.path before the repo imports
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, time
from itertools import combinations
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import cal33 as c  # noqa: E402
import data33 as d33  # noqa: E402
import guard33 as g  # noqa: E402
import mbo_book31 as mb  # noqa: E402

OUT_DIR = g.DERIVED / "probes" / "g6"
REPORT = HERE.parent / "G6_clock_report.md"
DROP = mb.F_SNAPSHOT | mb.F_BAD_TS_RECV
FLAG_NS = 100_000_000  # 100 ms
PACIFIC = ZoneInfo("America/Vancouver")
FEEDS = ("ZM", "ZS", "ZL")
COLS = ("ZM", "ZM_front", "ZS", "ZL")


def _months() -> list[str]:
    return sorted({f"{d:%Y-%m}" for d in c.trade_dates()})


def _stats(diff: np.ndarray, n_dropped: int) -> dict:
    if len(diff) == 0:
        return {"n": 0, "dropped": n_dropped}
    p1, med, p99 = np.percentile(diff, [1, 50, 99])
    return {"n": int(len(diff)), "dropped": int(n_dropped), "median_ns": float(med),
            "p1_ns": float(p1), "p99_ns": float(p99),
            "negative": int(np.count_nonzero(diff < 0))}


def month_stats(feed: str, month: str) -> dict:
    days = [d for d in c.trade_dates() if f"{d:%Y-%m}" == month]
    parts, front_parts, dropped, front_dropped = [], [], 0, 0
    for day in days:
        arr = d33.load_zm(day) if feed == "ZM" else d33.load_mbp1(feed, day)
        keep = (arr["flags"] & DROP) == 0
        dropped += int(np.count_nonzero(~keep))
        diff = arr["ts_recv"].astype(np.int64) - arr["ts_event"].astype(np.int64)
        parts.append(diff[keep])
        if feed == "ZM":
            front = arr["instrument_id"] == c.fronts(day)["ZM"]
            front_dropped += int(np.count_nonzero(front & ~keep))
            front_parts.append(diff[front & keep])
    out = {"feed": feed, "month": month, "dates": len(days),
           feed: _stats(np.concatenate(parts), dropped)}
    if feed == "ZM":
        out["ZM_front"] = _stats(np.concatenate(front_parts), front_dropped)
    return out


def run(feed: str) -> int:
    os.nice(10)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    g.check_path(OUT_DIR)
    for month in _months():
        target = OUT_DIR / f"{feed}_{month}.json"
        if target.is_file():
            continue
        if time(15, 28) <= datetime.now(PACIFIC).time() < time(16, 0):
            print(f"quiet window: stopped before {feed} {month}; rerun after 16:00", flush=True)
            return 3
        res = month_stats(feed, month)
        tmp = target.with_name(f".{target.name}.tmp")
        tmp.write_text(json.dumps(res) + "\n", encoding="utf-8")
        tmp.replace(target)
        print(f"{datetime.now(PACIFIC):%H:%M:%S} {feed} {month}", flush=True)
    return 0


def _ms(x: float | None) -> str:
    return "n/a" if x is None else f"{x / 1e6:.3f}"


def report() -> int:
    rows, missing = [], []
    for month in _months():
        rec: dict[str, dict] = {}
        for feed in FEEDS:
            path = OUT_DIR / f"{feed}_{month}.json"
            if not path.is_file():
                missing.append(f"{feed} {month}")
                continue
            data = json.loads(path.read_text(encoding="utf-8"))
            rec.update({k: v for k, v in data.items() if k in COLS})
        rows.append((month, rec))
    if missing:
        print(f"missing partials: {missing}")
        return 1
    lines = [
        "# G6 clock report (Stage E.33, DataCoder)", "",
        f"Written {datetime.now(PACIFIC):%Y-%m-%d %H:%M %Z} by "
        "reports/stage_e33_briefs/work/pipeline/g6_33.py (P4 G6). A data check on ts_recv - "
        "ts_event; no outcome is involved, and no rule changes because of it (P4 G6).", "",
        "Records: every record of the 816 trade dates (ZM: E.31's Z1 per-day store, all ZM "
        "instrument ids, and the ZM.v.0 front only; ZS and ZL: the E.33 MBP-1 split), grouped by "
        "the trade date's month; records flagged F_SNAPSHOT or F_BAD_TS_RECV are left out "
        "(READING G6-1). Quantiles by numpy.percentile (linear). Values in milliseconds.", "",
        "Flag rule: a month is flagged when the largest difference between the medians of ZM, ZS "
        "and ZL exceeds 100 ms; the ZM front-only median is checked the same way (flag column "
        "'front').", "",
        "| Month | ZM median | ZM p1 | ZM p99 | ZM front median | ZS median | ZS p1 | ZS p99 | "
        "ZL median | ZL p1 | ZL p99 | max median diff (ms) | flag | front |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    flagged = []
    totals = {k: 0 for k in COLS}
    for month, rec in rows:
        med = {k: rec[k]["median_ns"] for k in COLS}
        for k in COLS:
            totals[k] += rec[k]["n"]
        main = max(abs(med[a] - med[b]) for a, b in combinations(("ZM", "ZS", "ZL"), 2))
        front = max(abs(med[a] - med[b]) for a, b in combinations(("ZM_front", "ZS", "ZL"), 2))
        flag = main > FLAG_NS
        flag_front = front > FLAG_NS
        if flag or flag_front:
            flagged.append(month)
        lines.append(
            f"| {month} | {_ms(med['ZM'])} | {_ms(rec['ZM']['p1_ns'])} | "
            f"{_ms(rec['ZM']['p99_ns'])} | {_ms(med['ZM_front'])} | {_ms(med['ZS'])} | "
            f"{_ms(rec['ZS']['p1_ns'])} | {_ms(rec['ZS']['p99_ns'])} | {_ms(med['ZL'])} | "
            f"{_ms(rec['ZL']['p1_ns'])} | {_ms(rec['ZL']['p99_ns'])} | {_ms(max(main, front))} | "
            f"{'FLAG' if flag else ''} | {'FLAG' if flag_front else ''} |")
    lines += ["", f"Months: {len(rows)}. Flagged months (median difference > 100 ms): "
              f"{len(flagged)}{' (' + ', '.join(flagged) + ')' if flagged else ''}.", "",
              "Records used: " + ", ".join(f"{k} {totals[k]:,}" for k in COLS) + "."]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {REPORT}; months {len(rows)}; flagged {len(flagged)} {flagged}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) == 2 and args[0] == "run" and args[1] in FEEDS:
        return run(args[1])
    if args == ["report"]:
        return report()
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
