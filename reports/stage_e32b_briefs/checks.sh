#!/usr/bin/env bash
# Stage E.32b start and end checks (adapted from reports/stage_e33c_briefs/checks.sh; registry printed concisely).
# Usage: checks.sh <label>. Keys are checked by NAME only: no value is read into a variable, printed or logged.
set -u
cd "$(dirname "$0")/../.."
H=2e908c81e01d0aad835b30ab7b95f628182666dd8d76301cdd4ea465bb41edd1
SCR=/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/3d79635b-4dfe-4992-b743-c48717efe7fc/scratchpad
mkdir -p "$SCR"
echo "# E.32b checks: ${1:-?}"
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
echo "\$ uv run python reports/stage_e32_briefs/seal/soy_test_seal.py status (keys)  [the E.32 test seal]"
uv run python reports/stage_e32_briefs/seal/soy_test_seal.py status 2>/dev/null | python3 -c 'import json,sys; d=json.load(sys.stdin); print("soy test", {k: d[k] for k in ("state","files_sealed","files_ok","plaintext_in_window_present","unlocks_logged","all_ok")})'
P=$(mktemp -d "$SCR/pyc.XXXXXX")
echo "\$ guard33.py dry-check  [E.33 test-seal read guard: must refuse every forbidden read]"
(cd reports/stage_e33_briefs/work/pipeline && PYTHONPYCACHEPREFIX=$P uv run python guard33.py dry-check 2>&1 | tail -1; echo "rc=${PIPESTATUS[0]}")
echo "\$ wc -c REGISTRATION.md"; wc -c REGISTRATION.md
echo "\$ uv run python -m screening.harness_freeze verify --expected $H"
PYTHONPYCACHEPREFIX=$P uv run python -m screening.harness_freeze verify --expected "$H" 2>&1 | tail -3
echo "\$ ledger"; wc -l < ledger/databento_spend.jsonl | sed 's/$/ ledger\/databento_spend.jsonl/'; sha256sum ledger/databento_spend.jsonl | cut -d' ' -f1
echo "\$ ledger total per account (SpendGate.account_spent_usd)"
PYTHONPYCACHEPREFIX=$P uv run python -c '
from data.config import ACCOUNTS
from data.spend_gate import SpendGate
for a in sorted(ACCOUNTS):
    g=SpendGate(session_id="e32b-checks-readonly", account=a)
    s=g.account_spent_usd()
    print(f"{a}: spent {s:.6f} cap {g.account_cap_usd:.2f} headroom {g.account_cap_usd-s:.6f}")
'
echo "\$ trial registry: current_n and last entry (N)"
PYTHONPYCACHEPREFIX=$P uv run python -c '
import json
from screening import trial_registry as tr
rows=[json.loads(l) for l in open("ledger/trial_registrations.jsonl")]
last=rows[-1]
print("current_n", tr.current_n(), "| registrations", len(rows), "| last", last["entry_id"], last["n_before"], "->", last["n_after"], last["time_local"])
'
echo "\$ sha256sum ledger/trial_registrations.jsonl"; sha256sum ledger/trial_registrations.jsonl | cut -d' ' -f1
for K in DATABENTO_API_KEY DATABENTO_API_KEY2 DATABENTO_API_KEY3; do
  if grep -q "^${K}=..*" .env 2>/dev/null; then echo ".env ${K}: non-empty"; elif grep -q "^${K}=" .env 2>/dev/null; then echo ".env ${K}: empty"; else echo ".env ${K}: absent"; fi
done
echo "\$ ls reports | grep -c stage_e32b"; ls reports | grep -c stage_e32b
