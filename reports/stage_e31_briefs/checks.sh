#!/usr/bin/env bash
# Stage E.31 start and end checks (adapted from reports/stage_e30_briefs/checks.sh). Usage: checks.sh <label>.
# Keys are checked by NAME only: the value is never read into a variable, printed or logged.
set -u
cd "$(dirname "$0")/../.."
H=2e908c81e01d0aad835b30ab7b95f628182666dd8d76301cdd4ea465bb41edd1
SCR=/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/f6ca509c-6908-4e0b-a24a-4a4214833a47/scratchpad
mkdir -p "$SCR"
echo "# E.31 checks: ${1:-?}"
echo "\$ date"; TZ=America/Vancouver date
echo "\$ git status --short"; git status --short
echo "\$ git status --short | wc -l"; git status --short | wc -l
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
P=$(mktemp -d "$SCR/pyc.XXXXXX")
echo "\$ uv run python -m screening.harness_freeze verify --expected $H"
PYTHONPYCACHEPREFIX=$P uv run python -m screening.harness_freeze verify --expected "$H" 2>&1 | tail -3
echo "\$ ledger"; wc -l < ledger/databento_spend.jsonl | sed 's/$/ ledger\/databento_spend.jsonl/'; sha256sum ledger/databento_spend.jsonl | cut -d' ' -f1
echo "\$ ledger total per account (SpendGate.account_spent_usd)"
PYTHONPYCACHEPREFIX=$P uv run python -c '
from data.config import ACCOUNTS
from data.spend_gate import SpendGate
for a in sorted(ACCOUNTS):
    g=SpendGate(session_id="e31-checks-readonly", account=a)
    s=g.account_spent_usd()
    print(f"{a}: spent {s:.6f} cap {g.account_cap_usd:.2f} headroom {g.account_cap_usd-s:.6f}")
'
echo "\$ uv run python -m screening.trial_registry status (N)"
PYTHONPYCACHEPREFIX=$P uv run python -m screening.trial_registry status 2>&1 | tail -4
for K in DATABENTO_API_KEY DATABENTO_API_KEY2 DATABENTO_API_KEY3; do
  if grep -q "^${K}=..*" .env 2>/dev/null; then echo ".env ${K}: non-empty"; elif grep -q "^${K}=" .env 2>/dev/null; then echo ".env ${K}: empty"; else echo ".env ${K}: absent"; fi
done
