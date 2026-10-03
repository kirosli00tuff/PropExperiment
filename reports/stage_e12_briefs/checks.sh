#!/usr/bin/env bash
# Stage E.12 start/post-purchase/end guardrail checks (E.11 script plus per-account ledger totals). Prints the verbatim block quoted
# in the return. Usage: checks.sh <harness sha256>. pytest runs separately (pytest_*.out).
set -u
cd "$(dirname "$0")/../.."
H=${1:?harness sha256}
SCR=/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/8200a1ff-b6ff-45e5-adaa-37850b4a7889/scratchpad
mkdir -p "$SCR"
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
echo "\$ python3 reports/stage_e2b_briefs/check_frozen.py"; python3 reports/stage_e2b_briefs/check_frozen.py | grep -v '^OK  '
P=$(mktemp -d "$SCR/e12pyc.XXXXXX")
echo "\$ PYTHONPYCACHEPREFIX=<fresh> uv run python -m screening.harness_freeze verify --expected $H"
PYTHONPYCACHEPREFIX=$P uv run python -m screening.harness_freeze verify --expected "$H"
echo "\$ cluster freezes (load_cluster_freeze + verify_cluster_code)"
P2=$(mktemp -d "$SCR/e12pyc.XXXXXX")
PYTHONPYCACHEPREFIX=$P2 uv run python -c '
from screening.stage_e_freeze import load_cluster_freeze, verify_cluster_code
for c in ("K1","K2","K3","K4","K5","K6","K7","K8"):
    try:
        f=load_cluster_freeze(c)
    except Exception as e:
        print(c,"no freeze:",type(e).__name__); continue
    verify_cluster_code(f); print(c,"cluster freeze OK",f.sha256,len(f.members),"members")
'
echo "\$ ledger"; wc -l < ledger/databento_spend.jsonl | sed 's/$/ ledger\/databento_spend.jsonl/'; sha256sum ledger/databento_spend.jsonl | cut -d' ' -f1
echo "\$ ledger total per account (SpendGate.account_spent_usd: external ledgers plus this repo's lines)"
P3=$(mktemp -d "$SCR/e12pyc.XXXXXX")
PYTHONPYCACHEPREFIX=$P3 uv run python -c '
from data.config import ACCOUNTS
from data.spend_gate import SpendGate
for a in sorted(ACCOUNTS):
    g=SpendGate(session_id="e12-checks-readonly", account=a)
    s=g.account_spent_usd()
    print(f"{a}: spent {s:.6f} cap {g.account_cap_usd:.2f} headroom {g.account_cap_usd-s:.6f}")
'
