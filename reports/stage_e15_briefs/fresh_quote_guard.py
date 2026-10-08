"""Stage E.15 attempt 2, Step 3 guard: the fresh ext2010 total from THIS run's own ledger lines, never the tool's JSON.

data.pull_hist.quotes_from_ledger falls back to earlier sessions' successful lines under the shared session id
(attempt 1: 642 of 642 calls failed, the JSON still reported E.14's $57.742330 as complete). This guard:
1. takes the ledger lines appended after --before-lines; every one must be a quote event of session
   stage-E.14-2026-10-05 on acct-2 with ts >= --run-start-utc and usd 0.0;
2. requires exactly one successful quote (quoted_usd not null) for each of the plan's 642 chunk keys, and no
   other line;
3. requires the run log to say "quoted 642 of 642 chunks; 0 failed";
4. sums quoted_usd (the fresh total), per root and overall, and compares the tool JSON's total (information
   only; a mismatch fails the guard);
5. computes x 1.03, acct-2's headroom under V27's cap 291.08 (spent from SpendGate, read-only), and the session
   cap = x 1.03 rounded DOWN to the cent; ok iff x 1.03 <= headroom and the cap <= 60.00.
Writes reports/stage_e15_fresh_quote.json; prints the summary. Exit 0 iff ok.

Usage (repo root): PYTHONPATH=. uv run python reports/stage_e15_briefs/fresh_quote_guard.py \
    --before-lines <n> --run-start-utc <iso> --log <run log> --tool-json <tool quotes json>
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from datetime import datetime
from decimal import ROUND_FLOOR, Decimal
from pathlib import Path

LEDGER = Path("ledger/databento_spend.jsonl")
SESSION = "stage-E.14-2026-10-05"
ACCOUNT = "acct-2"
V27_CAP = Decimal("291.08")
HARD_CAP = Decimal("60.00")
OUT = Path("reports/stage_e15_fresh_quote.json")
N_CHUNKS = 642


def main() -> int:
    from data.pull_hist import get_plan, plan_chunks, request_key
    from data.spend_gate import SpendGate

    ap = argparse.ArgumentParser()
    ap.add_argument("--before-lines", type=int, required=True)
    ap.add_argument("--run-start-utc", required=True)
    ap.add_argument("--log", required=True)
    ap.add_argument("--tool-json", required=True)
    a = ap.parse_args()
    start = datetime.fromisoformat(a.run_start_utc)
    lines = LEDGER.read_text(encoding="utf-8").splitlines()
    new = [json.loads(x) for x in lines[a.before_lines:]]
    keys = {c.key: c.root for c in plan_chunks(get_plan("ext2010"))}
    problems, seen, per_root = [], defaultdict(int), defaultdict(float)
    total = 0.0
    for e in new:
        if e.get("event") != "quote" or e.get("session_id") != SESSION or e.get("account") != ACCOUNT:
            problems.append(f"foreign line: {e.get('event')} {e.get('session_id')} {e.get('account')}")
            continue
        if datetime.fromisoformat(e["ts"]) < start or float(e.get("usd", 1)) != 0.0:
            problems.append(f"line before the run or not $0.00: {e['ts']}")
        k = request_key(e["request"])
        if k not in keys:
            problems.append(f"line outside the plan: {e.get('symbol')} {e.get('date')}")
            continue
        if e.get("quoted_usd") is None:
            problems.append(f"failed quote {e.get('symbol')} {e.get('date')}: {str(e.get('note'))[:80]}")
            continue
        seen[k] += 1
        per_root[keys[k]] += float(e["quoted_usd"])
        total += float(e["quoted_usd"])
    missing = [k for k in keys if seen.get(k, 0) == 0]
    dup = [k for k, n in seen.items() if n > 1]
    log_ok = f"quoted {N_CHUNKS} of {N_CHUNKS} chunks; 0 failed" in Path(a.log).read_text(encoding="utf-8")
    tool = json.loads(Path(a.tool_json).read_bytes())["sets"]
    tool = tool[0] if isinstance(tool, list) else next(iter(tool.values()))
    tool_total = float(tool["total_usd"])
    spent = SpendGate(session_id="e15-guard-readonly", account=ACCOUNT).account_spent_usd()
    x103 = total * 1.03
    headroom = V27_CAP - Decimal(repr(spent))
    cap = (Decimal(repr(x103)) * 100).to_integral_value(rounding=ROUND_FLOOR) / 100
    checks = {"lines_new": len(new), "lines_expected": N_CHUNKS, "problems": problems[:10],
              "n_problems": len(problems), "missing_chunks": len(missing), "duplicate_chunks": len(dup),
              "log_says_0_failed": log_ok, "tool_json_total_usd": tool_total,
              "tool_json_equals_ledger_sum": math.isclose(tool_total, total, rel_tol=0, abs_tol=1e-9),
              "x1_03_le_headroom": Decimal(repr(x103)) <= headroom, "cap_le_60": cap <= HARD_CAP}
    ok = (len(new) == N_CHUNKS and not problems and not missing and not dup and log_ok
          and checks["tool_json_equals_ledger_sum"] and checks["x1_03_le_headroom"] and checks["cap_le_60"])
    doc = {"schema": "stage_e15_fresh_quote/1", "run_start_utc": a.run_start_utc,
           "ledger_lines_before": a.before_lines, "ledger_lines_after": len(lines), "n_lines": len(new),
           "per_root": {r: {"usd": per_root[r], "chunks": sum(1 for k, v in keys.items() if v == r and seen.get(k))}
                        for r in ("NG", "NQ", "ZN", "6E", "GC", "ZC")},
           "total_usd": total, "x1_03": x103, "acct2_spent_usd": spent, "v27_cap_usd": str(V27_CAP),
           "headroom_usd": str(headroom), "session_cap_usd": str(cap), "checks": checks, "ok": ok}
    OUT.write_text(json.dumps(doc, indent=1) + "\n")
    print(json.dumps({k: doc[k] for k in ("n_lines", "total_usd", "x1_03", "acct2_spent_usd", "headroom_usd",
                                          "session_cap_usd", "ok")}))
    print({r: round(v["usd"], 6) for r, v in doc["per_root"].items()})
    print({k: v for k, v in checks.items() if k != "problems"}, checks["problems"][:3])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
