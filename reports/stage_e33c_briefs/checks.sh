#!/usr/bin/env bash
# Stage E.33c start and end checks (copy of reports/stage_e33b_briefs/checks.sh, scratchpad path changed) (adapted from reports/stage_e32_briefs/checks.sh). Usage: checks.sh <label>.
# Keys are checked by NAME only: the value is never read into a variable, printed or logged.
set -u
cd "$(dirname "$0")/../.."
H=2e908c81e01d0aad835b30ab7b95f628182666dd8d76301cdd4ea465bb41edd1
SCR=/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/7c6136a3-16c6-44df-891a-efd174837057/scratchpad
mkdir -p "$SCR"
echo "# E.33c checks: ${1:-?}"
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
echo "\$ trial_registry.require_registered(300 E33 ids, test=E33); last entry"
PYTHONPYCACHEPREFIX=$P uv run python -c '
import json, sys
sys.path.insert(0, "reports/stage_e33_briefs/work/pipeline")
import search33 as s
from screening import trial_registry as tr
ids = s.all_config_ids(); tr.require_registered(ids, test="E33")
last = [json.loads(l) for l in open("ledger/trial_registrations.jsonl")][-1]
print("require_registered ok", len(ids), "| current_n", tr.current_n(), "| last", last["entry_id"], last["n_before"], "->", last["n_after"], last["time_local"])
'
echo "\$ guard33.py dry-check"
(cd reports/stage_e33_briefs/work/pipeline && PYTHONPYCACHEPREFIX=$P uv run python guard33.py dry-check 2>&1 | tail -1; echo "rc=${PIPESTATUS[0]}")
if [ -f ledger/trial_amendments.jsonl ]; then echo "\$ ledger/trial_amendments.jsonl"; wc -l < ledger/trial_amendments.jsonl; sha256sum ledger/trial_amendments.jsonl | cut -d' ' -f1; fi
for f in reports/stage_e32_discovery_protocol_v0.3.md; do [ -f "$f" ] && { echo "\$ sha256sum $f"; sha256sum "$f"; }; done
