"""Lead patch B2 + SHOULD FIX (FactAuditor re-check, 2026-10-29): exact string replacements in the masked firm sheet.
Labels and item ids are not touched. Each replacement must occur the expected number of times, or nothing is written."""
import json
import sys
from pathlib import Path

B = Path(__file__).resolve().parents[2]
SHEET, KEY = B / "F4_masked_firms.json", B / "F4_mask_key.json"
REPL = [  # (old, new, expected count in the raw file text, reason)
    ("MyFunded Futures", "V-CXFO", 1, "B2 firm name (mffu)"),
    ("news_builder", "news_plan_P1", 1, "mffu plan P1 = Builder"),
    ("builder_50k", "plan_P1_50k", 1, "mffu plan P1 = Builder"),
    ("combine_consistency", "plan_P1_eval_consistency", 1, "topstep plan P1 evaluation stage = Combine"),
    ("combine_min_days", "plan_P1_eval_min_days", 1, "topstep plan P1 evaluation stage = Combine"),
    ("growth eval", "plan P1 eval", 1, "tradeify plan P1 = Growth"),
    ("master-trading-rules", "funded-stage trading rules page", 1, "bulenox plan P1 funded stage = Master"),
    ("master_inactivity", "plan_P1_funded_inactivity", 1, "bulenox plan P1 funded stage = Master"),
]
text = SHEET.read_text()
for old, new, n, why in REPL:
    got = text.count(old)
    if got != n:
        sys.exit(f"refused: {old!r} occurs {got} times, expected {n}")
    text = text.replace(old, new)
json.loads(text)  # still valid JSON
SHEET.write_text(text)
key = json.loads(KEY.read_text())
key.setdefault("patches", []).append({"by": "lead (session 3)", "pdt": "2026-10-29", "file": "F4_masked_firms.json",
                                      "replacements": [{"old": o, "new": w, "count": n, "reason": r} for o, w, n, r in REPL]})
KEY.write_text(json.dumps(key, indent=1, ensure_ascii=False))
print("patched", len(REPL), "replacements")
