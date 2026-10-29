#!/usr/bin/env bash
# RV1 copy of work/F3/guard_checks.sh with this session's scratchpad for the pycache prefix. Usage: guard_checks_rv1.sh <label>
set -u
cd /home/kiros-li/Documents/GitHub/PropExperiment
SCR=/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/3860d0d1-cf19-46b3-a4da-6fda65b58c32/scratchpad
mkdir -p "$SCR"
echo "# E.32b RV1 guard checks: ${1:-?}"
echo "\$ date"; TZ=America/Vancouver date
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
echo "\$ uv run python reports/stage_e32_briefs/seal/soy_test_seal.py status (keys)"
uv run python reports/stage_e32_briefs/seal/soy_test_seal.py status 2>/dev/null | python3 -c 'import json,sys; d=json.load(sys.stdin); print("soy test", {k: d[k] for k in ("state","files_sealed","files_ok","plaintext_in_window_present","unlocks_logged","all_ok")})'
P=$(mktemp -d "$SCR/pyc.XXXXXX")
echo "\$ guard33.py dry-check"
(cd reports/stage_e33_briefs/work/pipeline && PYTHONPYCACHEPREFIX=$P uv run python guard33.py dry-check 2>&1 | tail -1; echo "rc=${PIPESTATUS[0]}")
