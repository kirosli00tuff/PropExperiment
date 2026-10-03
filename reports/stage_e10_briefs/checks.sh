#!/usr/bin/env bash
# Stage E.10 start/end guardrail checks (prints the verbatim block quoted in the return)
cd "$(dirname "$0")/../.."
echo "\$ date"; TZ=America/Vancouver date
echo "\$ git status --short"; git status --short
echo "\$ git log --oneline -3"; git log --oneline -3
echo "\$ uv run python -m data.holdout status (keys)"
uv run python -m data.holdout status 2>/dev/null | python3 -c '
import json,sys
d=json.load(sys.stdin)
def walk(o,p=""):
    if isinstance(o,dict):
        if "all_ok" in o and "unlocks_logged" in o:
            print(p or "top", "all_ok", o["all_ok"], "unlocks_logged", o["unlocks_logged"], "unlock_log_ok", o.get("unlock_log_ok"))
        for k,v in o.items(): walk(v,k)
walk(d)'
echo "\$ wc -c REGISTRATION.md"; wc -c REGISTRATION.md
echo "\$ ledger"; wc -l < ledger/databento_spend.jsonl | sed 's/$/ ledger\/databento_spend.jsonl/'; sha256sum ledger/databento_spend.jsonl | cut -d' ' -f1
