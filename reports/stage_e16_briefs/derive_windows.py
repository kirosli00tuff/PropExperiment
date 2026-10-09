"""Stage E.16: each product's test window start under user ruling U2 (2026-10-09), and the E.17 purchase list.

U2: a product's window starts at the first priced month after its last unpriced gap before 2019-05, in E.12's
2010-extension quote record (reports/stage_e12_quotes_ext2010.json), plus warm-up; the start is the first trade date
on or after the first day of that month. The 21 roots outside C1's set are bought in E.17 from that month through
2019-04; their cost here is the sum of E.12's successful quote lines (ledger/databento_spend.jsonl, session
stage-E.12-2026-10-03) over exactly those months. Reads JSON metadata only, never a bar.

    python3 reports/stage_e16_briefs/derive_windows.py    # writes reports/stage_e16_windows.json
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
QUOTES = REPO / "reports" / "stage_e12_quotes_ext2010.json"
LEDGER = REPO / "ledger" / "databento_spend.jsonl"
OUT = REPO / "reports" / "stage_e16_windows.json"
E12_SESSION = "stage-E.12-2026-10-03"
C1_ROOTS = ("NG", "NQ", "ZN", "6E", "GC", "ZC")  # data.pull_hist EXT2010.roots
LAST_MONTH = "2019-04"
FALLBACK = ["2019-05-06", "2024-02-29"]
WINDOW_END = "2024-02-29"


def months(first: str, last: str) -> list[str]:
    y, m = map(int, first.split("-"))
    out = []
    while f"{y:04d}-{m:02d}" <= last:
        out.append(f"{y:04d}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def start_month(failed: list[str]) -> str:
    """First priced month after the last unpriced month before 2019-05 (no failure: 2010-01)."""
    unpriced = sorted(f.split("..")[0][:7] for f in failed)
    if not unpriced:
        return "2010-01"
    return months(unpriced[-1], "2019-05")[1]


def e12_quotes() -> dict[str, dict[str, float]]:
    q: dict[str, dict[str, float]] = {}
    with LEDGER.open() as fh:
        for line in fh:
            if E12_SESSION not in line:
                continue
            d = json.loads(line)
            if d.get("event") != "quote" or d.get("session_id") != E12_SESSION or d.get("quoted_usd") is None:
                continue
            a, b = d["date"].split("..")
            if "2010-01-01" <= a and b <= "2019-05-01":
                q.setdefault(d["symbol"].split(".")[0], {})[a[:7]] = d["quoted_usd"]
    return q


def main() -> None:
    record = json.loads(QUOTES.read_text())["sets"]["ml-v2+extension-2010"]
    quotes = e12_quotes()
    products, total = {}, 0.0
    for root, row in sorted(record["per_contract"].items()):
        first = start_month(row["failed"])
        span = months(first, LAST_MONTH)
        missing = [m for m in span if m not in quotes.get(root, {})]
        if missing:
            raise SystemExit(f"{root}: months in its window without an E.12 quote: {missing}")
        usd = sum(quotes[root][m] for m in span)
        buy = root not in C1_ROOTS
        total += usd if buy else 0.0
        products[root] = {
            "start_month": first, "window_start_on_or_after": f"{first}-01", "window_end": WINDOW_END,
            "unpriced_months_in_e12_record": sorted(f.split("..")[0][:7] for f in row["failed"]),
            "chunks_2010_to_2019_04": len(span), "e12_quoted_usd": round(usd, 6),
            "source_of_2010_2019_bars": "E.17 purchase (21-root plan)" if buy else "C1's ext2010 plan (E.17)",
        }
    body = {
        "schema": "stage_e16_windows/1",
        "rule": "U2 (user, 2026-10-09): the first priced month after the last unpriced gap before 2019-05 in "
                "reports/stage_e12_quotes_ext2010.json; window = first trade date on or after its first day "
                "through 2024-02-29, plus the test's warm-up; fallback 2019-05-06..2024-02-29 per product, recorded "
                "at E.17's registration",
        "inputs": {p.relative_to(REPO).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in (QUOTES,)},
        "fallback_window": FALLBACK,
        "products": products,
        "purchase_21_roots": {"roots": sorted(r for r in products if r not in C1_ROOTS),
                              "chunks": sum(v["chunks_2010_to_2019_04"] for r, v in products.items()
                                            if r not in C1_ROOTS),
                              "e12_quoted_usd": round(total, 6), "x1_03": round(total * 1.03, 6)},
    }
    OUT.write_text(json.dumps(body, indent=1) + "\n")
    starts: dict[str, list[str]] = {}
    for r, v in products.items():
        starts.setdefault(v["start_month"], []).append(r)
    print({k: (len(v) if len(v) > 3 else v) for k, v in starts.items()}, body["purchase_21_roots"]["chunks"],
          body["purchase_21_roots"]["e12_quoted_usd"], body["purchase_21_roots"]["x1_03"])


if __name__ == "__main__":
    main()
