#!/usr/bin/env bash
# Stage E.28b start and end checks (lean subset of E.26 checks.sh). Usage: checks_b.sh <label>.
# DATABENTO_API_KEY3 is checked by NAME only (empty or non-empty); its value is never printed.
set -u
cd "$(dirname "$0")/../.."
H=2e908c81e01d0aad835b30ab7b95f628182666dd8d76301cdd4ea465bb41edd1
SCR=/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/c4961140-6cb5-4eeb-8deb-096950337c09/scratchpad
mkdir -p "$SCR"
echo "# E.28b checks: ${1:-?}"
echo "\$ date"; TZ=America/Vancouver date
echo "\$ git status --short | wc -l (tracked changes: git status --short -uno)"; git status --short | wc -l; git status --short -uno
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
    g=SpendGate(session_id="e28b-checks-readonly", account=a)
    s=g.account_spent_usd()
    print(f"{a}: spent {s:.6f} cap {g.account_cap_usd:.2f} headroom {g.account_cap_usd-s:.6f}")
'
echo "\$ uv run python -m screening.trial_registry status (N)"
PYTHONPYCACHEPREFIX=$P uv run python -m screening.trial_registry status 2>&1 | tail -4
echo "\$ DATABENTO_API_KEY3 by name (.env and environment)"
if grep -q '^DATABENTO_API_KEY3=..*' .env 2>/dev/null; then echo ".env DATABENTO_API_KEY3: non-empty"; elif grep -q '^DATABENTO_API_KEY3=' .env 2>/dev/null; then echo ".env DATABENTO_API_KEY3: empty"; else echo ".env DATABENTO_API_KEY3: absent"; fi
if [ -n "${DATABENTO_API_KEY3:-}" ]; then echo "env DATABENTO_API_KEY3: non-empty"; else echo "env DATABENTO_API_KEY3: empty or unset"; fi
rm -rf "$P"
