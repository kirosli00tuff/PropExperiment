#!/usr/bin/env bash
# Stage E.25 start/end guardrail checks (research-only stage: no pytest, no freeze verify; E.24 owns the suite).
# Prints the verbatim block quoted in the return. Usage: checks.sh > start_checks.txt
set -u
cd "$(dirname "$0")/../.."
SCR=/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/37fc9660-82d1-49fd-be83-50b822ab0a5b/scratchpad
mkdir -p "$SCR"
echo "\$ date"; TZ=America/Vancouver date
echo "\$ git status --short (tracked lines; untracked count)"; git status --short | grep -v '^??'; echo "untracked: $(git status --short | grep -c '^??')"
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
echo "\$ spend ledger: wc -l; sha256sum"; wc -l < ledger/databento_spend.jsonl | sed 's/$/ ledger\/databento_spend.jsonl/'; sha256sum ledger/databento_spend.jsonl | cut -d' ' -f1
echo "\$ uv run python -m screening.trial_registry status"
P=$(mktemp -d "$SCR/e25pyc.XXXXXX")
PYTHONPYCACHEPREFIX=$P uv run python -m screening.trial_registry status | sed -n '1p;$p'
echo "\$ trial ledger: wc -l ledger/trial_registrations.jsonl; sha256sum"; wc -l < ledger/trial_registrations.jsonl; sha256sum ledger/trial_registrations.jsonl | cut -d' ' -f1
