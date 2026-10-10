"""Stage E.17 amendment A3 (V30, budget as amended to $124.00): the Part 2 purchase selection, fixed before any
quote, reading no market data.

Order: ZT, ZF, ZB; then the other roots of the 21 in E.12's frozen phase-1 ranking order
(reports/stage_e12_ranking.json, rank 1 first; each vehicle mapped to its price-path root; roots in C1's set,
roots already taken and roots outside the 21 skipped). Greedy: a root is taken iff its fresh quote x 1.03 fits the
budget left; the budget left starts at B = $124.00 minus everything acct-2 billed in this stage before Part 2
(acct-2's ledger spend now minus its spend at the stage start), and falls by each taken root's quote x 1.03.
Every root of the 21 not taken goes on the fallback list (A5: window 2019-05-06..2024-02-29, "not funded").

Inputs: the ext2010h fresh-quote guard JSON (fresh_quote_guard.py, ok must be true; per-root sums of the run's own
ledger lines). Writes --out (selection) and --fallback-out (the fallback list; its sha256 goes into STATE before
any Part 2 purchase). Prints the selection, the skips and the sha256s.

Usage (repo root): PYTHONPATH=. uv run python reports/stage_e17_briefs/a3_select.py --guard-json <json> \
    --spent-at-start 231.599730238302 --out <selection json> --fallback-out <fallback json>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from decimal import Decimal
from pathlib import Path

BUDGET = Decimal("124.00")
FIRST = ("ZT", "ZF", "ZB")
C1_ROOTS = ("NG", "NQ", "ZN", "6E", "GC", "ZC")
FALLBACK = ["2019-05-06", "2024-02-29"]
RANKING = Path("reports/stage_e12_ranking.json")
WINDOWS = Path("reports/stage_e16_windows.json")
RANKING_SHA = "43f80e90bc26ce5d4997e88e9aaa1fab32c5884bc7a9ea4b4b0fadd4d5422aaf"


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def priority(the_21: list[str]) -> list[str]:
    ranking = sorted(json.loads(RANKING.read_bytes())["ranking"], key=lambda r: r["rank"])
    order = list(FIRST)
    for r in ranking:
        root = r["path"]
        if root in C1_ROOTS or root in order or root not in the_21:
            continue
        order.append(root)
    missing = [r for r in the_21 if r not in order]
    if missing or len(order) != len(the_21):
        raise SystemExit(f"priority list does not cover the 21 roots exactly: missing {missing}")
    return order


def main() -> int:
    from data.spend_gate import SpendGate

    ap = argparse.ArgumentParser()
    ap.add_argument("--guard-json", required=True)
    ap.add_argument("--spent-at-start", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--fallback-out", required=True)
    a = ap.parse_args()
    if sha(RANKING) != RANKING_SHA:
        raise SystemExit(f"{RANKING} sha256 {sha(RANKING)} is not E.12's {RANKING_SHA}")
    guard = json.loads(Path(a.guard_json).read_bytes())
    if not guard.get("ok") or guard.get("plan") != "ext2010h":
        raise SystemExit("the ext2010h guard did not pass: no selection")
    the_21 = json.loads(WINDOWS.read_bytes())["purchase_21_roots"]["roots"]
    if sorted(guard["per_root"]) != sorted(the_21):
        raise SystemExit("the guard's roots are not the 21")
    spent_now = Decimal(repr(SpendGate(session_id="e17-a3-readonly", account="acct-2").account_spent_usd()))
    billed_part1 = spent_now - Decimal(a.spent_at_start)
    left = BUDGET - billed_part1
    b_start = left
    selected, skipped = [], []
    for rank, root in enumerate(priority(the_21), start=1):
        cost = Decimal(repr(guard["per_root"][root]["usd"])) * Decimal("1.03")
        row = {"priority": rank, "root": root, "fresh_quote_usd": guard["per_root"][root]["usd"],
               "x1_03": str(cost), "budget_left_before": str(left)}
        if cost <= left:
            left -= cost
            selected.append({**row, "budget_left_after": str(left)})
        else:
            skipped.append({**row, "reason": "quote x 1.03 exceeds the budget left"})
    fallback = {"schema": "stage_e17_fallback_list/1", "rule": "A5 (V30): every root of the 21 not in the A3 "
                "selection runs on the fallback window, reason 'not funded'; products whose purchase or store build "
                "then fails are added with their reason before any test bar is read",
                "window": FALLBACK,
                "roots": {s["root"]: "not funded" for s in skipped}}
    Path(a.fallback_out).write_text(json.dumps(fallback, indent=1, sort_keys=True) + "\n")
    doc = {"schema": "stage_e17_a3_selection/1", "budget_usd": str(BUDGET), "spent_at_start": a.spent_at_start,
           "spent_now": str(spent_now), "billed_part1": str(billed_part1), "b_start": str(b_start),
           "guard_json": {"path": a.guard_json, "sha256": sha(Path(a.guard_json))},
           "ranking": {"path": str(RANKING), "sha256": RANKING_SHA},
           "selected": selected, "skipped": skipped,
           "selected_roots": [s["root"] for s in selected],
           "selected_x1_03_total": str(sum((Decimal(s["x1_03"]) for s in selected), Decimal(0))),
           "selected_quote_total": sum(s["fresh_quote_usd"] for s in selected),
           "budget_left_after": str(left),
           "fallback": {"path": a.fallback_out, "sha256": sha(Path(a.fallback_out))}}
    Path(a.out).write_text(json.dumps(doc, indent=1) + "\n")
    print(f"B = {b_start} (billed in Part 1 {billed_part1}); selected {doc['selected_roots']} "
          f"x1.03 {doc['selected_x1_03_total']}; left {left}")
    print("skipped:", [(s["root"], s["x1_03"][:8], s["budget_left_before"][:8]) for s in skipped])
    print(f"selection {a.out} sha256 {sha(Path(a.out))}; fallback {a.fallback_out} sha256 {doc['fallback']['sha256']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
