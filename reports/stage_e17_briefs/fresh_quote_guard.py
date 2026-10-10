"""Stage E.17 fresh-quote guard: E.15's reports/stage_e15_briefs/fresh_quote_guard.py generalized to both plans
(ext2010 for C1, step 5; ext2010h for the base-rule batch, step 9) and to A1's stage budget ($124.00, V30 as
amended). The fresh total is the sum of THIS run's own new ledger lines, never the tool's JSON (V29):
1. every ledger line appended after --before-lines is a quote event of --session on acct-2 with ts >=
   --run-start-utc and usd 0.0;
2. exactly one successful quote (quoted_usd not null) for each chunk key of the plan, and no other line;
3. the run log says "quoted N of N chunks; 0 failed";
4. quoted_usd summed per root and overall; the tool JSON's total must equal the ledger sum (a mismatch fails);
5. x 1.03; the session cap = x 1.03 rounded DOWN to the cent; ACCOUNT_2_CAP_USD = acct-2's spend (SpendGate,
   read-only) + x 1.03, rounded UP to the cent. With --budget-usd: ok also needs x 1.03 <= the budget; with
   --hard-cap-usd: the session cap <= it (V27's $60.00 for C1). For ext2010h the budget is applied per root by
   the A3 selection, so the guard is run without --budget-usd there.
Writes --out (JSON); prints a short summary. Exit 0 iff ok.

Usage (repo root): PYTHONPATH=. uv run python reports/stage_e17_briefs/fresh_quote_guard.py --plan ext2010 \
    --session stage-E.14-2026-10-05 --before-lines <n> --run-start-utc <iso> --log <run log> \
    --tool-json <tool quotes json> --out <json> [--budget-usd 124.00] [--hard-cap-usd 60.00]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from datetime import datetime
from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal
from pathlib import Path

LEDGER = Path("ledger/databento_spend.jsonl")
ACCOUNT = "acct-2"


def cents(value: Decimal, rounding: str) -> Decimal:
    return (value * 100).to_integral_value(rounding=rounding) / 100


def main() -> int:
    from data.pull_hist import get_plan, plan_chunks, request_key
    from data.spend_gate import SpendGate

    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--session", required=True)
    ap.add_argument("--before-lines", type=int, required=True)
    ap.add_argument("--run-start-utc", required=True)
    ap.add_argument("--log", required=True)
    ap.add_argument("--tool-json", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--budget-usd")
    ap.add_argument("--hard-cap-usd")
    a = ap.parse_args()
    start = datetime.fromisoformat(a.run_start_utc)
    plan = get_plan(a.plan)
    keys = {c.key: c.root for c in plan_chunks(plan)}
    n_chunks = len(keys)
    lines = LEDGER.read_text(encoding="utf-8").splitlines()
    new = [json.loads(x) for x in lines[a.before_lines:]]
    problems, seen, per_root = [], defaultdict(int), defaultdict(float)
    total = 0.0
    for e in new:
        if e.get("event") != "quote" or e.get("session_id") != a.session or e.get("account") != ACCOUNT:
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
    log_ok = f"quoted {n_chunks} of {n_chunks} chunks; 0 failed" in Path(a.log).read_text(encoding="utf-8")
    tool = json.loads(Path(a.tool_json).read_bytes())["sets"]
    tool = tool[0] if isinstance(tool, list) else next(iter(tool.values()))
    tool_total = float(tool["total_usd"])
    spent = SpendGate(session_id="e17-guard-readonly", account=ACCOUNT).account_spent_usd()
    x103 = Decimal(repr(total * 1.03))
    session_cap = cents(x103, ROUND_FLOOR)
    account_cap = cents(Decimal(repr(spent)) + x103, ROUND_CEILING)
    checks = {"lines_new": len(new), "lines_expected": n_chunks, "problems": problems[:10],
              "n_problems": len(problems), "missing_chunks": len(missing), "duplicate_chunks": len(dup),
              "log_says_0_failed": log_ok, "tool_json_total_usd": tool_total,
              "tool_json_equals_ledger_sum": math.isclose(tool_total, total, rel_tol=0, abs_tol=1e-9)}
    ok = (len(new) == n_chunks and not problems and not missing and not dup and log_ok
          and checks["tool_json_equals_ledger_sum"])
    if a.budget_usd is not None:
        checks["x1_03_le_budget"] = x103 <= Decimal(a.budget_usd)
        ok = ok and checks["x1_03_le_budget"]
    if a.hard_cap_usd is not None:
        checks["session_cap_le_hard_cap"] = session_cap <= Decimal(a.hard_cap_usd)
        ok = ok and checks["session_cap_le_hard_cap"]
    roots = list(dict.fromkeys(keys.values()))
    doc = {"schema": "stage_e17_fresh_quote/1", "plan": plan.name, "session_id": a.session,
           "run_start_utc": a.run_start_utc, "ledger_lines_before": a.before_lines, "ledger_lines_after": len(lines),
           "n_lines": len(new), "n_chunks": n_chunks,
           "per_root": {r: {"usd": per_root[r], "x1_03": per_root[r] * 1.03,
                            "chunks_quoted": sum(1 for k, v in keys.items() if v == r and seen.get(k)),
                            "chunks": sum(1 for v in keys.values() if v == r)} for r in roots},
           "total_usd": total, "x1_03": str(x103), "acct2_spent_usd": spent,
           "budget_usd": a.budget_usd, "hard_cap_usd": a.hard_cap_usd,
           "session_cap_usd": str(session_cap), "account_cap_usd_spent_plus_x1_03_ceil": str(account_cap),
           "checks": checks, "ok": ok}
    Path(a.out).write_text(json.dumps(doc, indent=1) + "\n")
    print(json.dumps({k: doc[k] for k in ("plan", "n_lines", "total_usd", "x1_03", "acct2_spent_usd",
                                          "session_cap_usd", "account_cap_usd_spent_plus_x1_03_ceil", "ok")}))
    print({r: round(v["usd"], 6) for r, v in doc["per_root"].items()})
    print({k: v for k, v in checks.items() if k != "problems"}, checks["problems"][:3])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
