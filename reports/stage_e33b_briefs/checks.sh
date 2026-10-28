#!/usr/bin/env bash
# Stage E.33b start and end checks (copy of reports/stage_e33_briefs/checks.sh, scratchpad path changed) (adapted from reports/stage_e32_briefs/checks.sh). Usage: checks.sh <label>.
# Keys are checked by NAME only: the value is never read into a variable, printed or logged.
set -u
cd "$(dirname "$0")/../.."
H=2e908c81e01d0aad835b30ab7b95f628182666dd8d76301cdd4ea465bb41edd1
SCR=/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/b8cfc9d8-3e96-415a-a441-462542346e80/scratchpad
mkdir -p "$SCR"
echo "# E.33b checks: ${1:-?}"
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
echo "\$ uv run python reports/stage_e32_briefs/seal/soy_test_seal.py status (keys)"
uv run python reports/stage_e32_briefs/seal/soy_test_seal.py status 2>/dev/null | python3 -c 'import json,sys; d=json.load(sys.stdin); print("soy test", {k: d[k] for k in ("state","files_sealed","files_ok","plaintext_in_window_present","unlocks_logged","all_ok")})'
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
    g=SpendGate(session_id="e33-checks-readonly", account=a)
    s=g.account_spent_usd()
    print(f"{a}: spent {s:.6f} cap {g.account_cap_usd:.2f} headroom {g.account_cap_usd-s:.6f}")
'
echo "\$ uv run python -m screening.trial_registry status (N)"
PYTHONPYCACHEPREFIX=$P uv run python -m screening.trial_registry status 2>&1 | tail -4
for K in DATABENTO_API_KEY DATABENTO_API_KEY2 DATABENTO_API_KEY3; do
  if grep -q "^${K}=..*" .env 2>/dev/null; then echo ".env ${K}: non-empty"; elif grep -q "^${K}=" .env 2>/dev/null; then echo ".env ${K}: empty"; else echo ".env ${K}: absent"; fi
done
echo "\$ sha256sum reports/stage_e32_discovery_protocol.md (expected c4ffb9d79af4bbbf10574ac138668aa49a80b22a8f5fba5879184d357d2c7e05)"
sha256sum reports/stage_e32_discovery_protocol.md
echo "\$ cat reports/stage_e32_discovery_protocol.sha256"; cat reports/stage_e32_discovery_protocol.sha256
if [ -f reports/stage_e33_pipeline_freeze.sha256 ]; then echo "\$ sha256sum reports/stage_e33_pipeline_freeze.sha256"; sha256sum reports/stage_e33_pipeline_freeze.sha256; fi
