#!/usr/bin/env bash
# Stage E.5 start/end checks (E.4's commands plus the acct-2 total and the four roots' step 2 status).
# Usage: start_checks.sh <harness sha256> [K4 freeze note]
set -u
cd /home/kiros-li/Documents/GitHub/PropExperiment
H=${1:?harness sha256}
SCR=/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/b56ee083-7d81-4a9a-b281-328c8ac9ffa4/scratchpad
mkdir -p "$SCR"
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
echo "\$ python3 reports/stage_e2b_briefs/check_frozen.py"; python3 reports/stage_e2b_briefs/check_frozen.py | grep -v '^OK  '
P=$(mktemp -d "$SCR/e5pyc.XXXXXX")
echo "\$ PYTHONPYCACHEPREFIX=<fresh> uv run python -m screening.harness_freeze verify --expected $H"
PYTHONPYCACHEPREFIX=$P uv run python -m screening.harness_freeze verify --expected "$H"
echo "\$ cluster freezes (load_cluster_freeze + verify_cluster_code)"
P2=$(mktemp -d "$SCR/e5pyc.XXXXXX")
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
echo "\$ acct-2 position (pull_step2.account_position on the step 2 gate; reads the ledger only)"
P3=$(mktemp -d "$SCR/e5pyc.XXXXXX")
PYTHONPYCACHEPREFIX=$P3 uv run python -c '
from data import pull_step2 as p
g=p.step2_gate(); print(g.session_id, p.account_position(g))
'
echo "\$ python -m data.pull_step2 --status (MCL NG MGC MHG)"
P4=$(mktemp -d "$SCR/e5pyc.XXXXXX")
PYTHONPYCACHEPREFIX=$P4 uv run python -m data.pull_step2 --status | python3 -c '
import json,sys
d=json.load(sys.stdin)
print("roots in status:",len(d),"; states:",sorted({v.get("state","?") for v in d.values()}))
for r in ("MCL","NG","MGC","MHG"):
    v=d.get(r); print(r, json.dumps(v)[:400])
'
echo "\$ ls reports/step2/ data/processed_step2/"; ls reports/step2/ 2>&1 | head; ls data/processed_step2/ 2>&1 | head
