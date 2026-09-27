#!/usr/bin/env bash
# Stage E.4 start/end checks (same commands as E.3 section 2). Usage: start_checks.sh <harness sha256>
set -u
cd /home/kiros-li/Documents/GitHub/PropExperiment
H=${1:-cf939270f0a00be74aa29a43f0c7de964256411a9cdcebc36f22fd3bdc021a45}
echo "\$ date"; TZ=America/Vancouver date
echo "\$ git status --short"; git status --short
echo "\$ git log --oneline -3"; git log --oneline -3
echo "\$ wc -c REGISTRATION.md"; wc -c REGISTRATION.md
echo "\$ uv run python -m data.holdout status (keys)"
uv run python -m data.holdout status 2>/dev/null | python3 -c '
import json,sys
d=json.load(sys.stdin)
print("holdout_1 all_ok",d.get("all_ok"),"unlocks_logged",d.get("unlocks_logged"),"unlock_log_ok",d.get("unlock_log_ok"))
h=d.get("holdout_2",{}); print("holdout_2 all_ok",h.get("all_ok"),"unlocks_logged",h.get("unlocks_logged"),"unlock_log_ok",h.get("unlock_log_ok"))
'
echo "\$ python3 reports/stage_e2b_briefs/check_frozen.py"; python3 reports/stage_e2b_briefs/check_frozen.py
P=$(mktemp -d /tmp/claude-1000/e4pyc.XXXXXX)
echo "\$ PYTHONPYCACHEPREFIX=<fresh> uv run python -m screening.harness_freeze verify --expected $H"
PYTHONPYCACHEPREFIX=$P uv run python -m screening.harness_freeze verify --expected "$H"
echo "\$ cluster freezes (load_cluster_freeze + verify_cluster_code)"
P2=$(mktemp -d /tmp/claude-1000/e4pyc.XXXXXX)
PYTHONPYCACHEPREFIX=$P2 uv run python -c '
from screening.stage_e_freeze import load_cluster_freeze, verify_cluster_code
for c in ("K2","K4","K5","K3"):
    try:
        f=load_cluster_freeze(c)
    except Exception as e:
        print(c,"no freeze:",type(e).__name__); continue
    verify_cluster_code(f); print(c,"cluster freeze OK",f.sha256,len(f.members),"members")
'
echo "\$ ledger"; wc -l ledger/databento_spend.jsonl; sha256sum ledger/databento_spend.jsonl | cut -d" " -f1
