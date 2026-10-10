#!/usr/bin/env bash
# Stage E.17 start/post-purchase/end guardrail checks (E.16 script plus the E.16 freeze verification and the E.14
# C1 freeze verification). Prints the verbatim block quoted in the return. Usage: checks.sh <harness sha256>.
# pytest runs separately (pytest_*.out).
set -u
cd "$(dirname "$0")/../.."
H=${1:?harness sha256}
SCR=/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/0dcecb5d-5f79-4bc8-8a23-a1ca768d375b/scratchpad
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
P=$(mktemp -d "$SCR/e17pyc.XXXXXX")
echo "\$ PYTHONPYCACHEPREFIX=<fresh> uv run python -m screening.harness_freeze verify --expected $H"
PYTHONPYCACHEPREFIX=$P uv run python -m screening.harness_freeze verify --expected "$H"
echo "\$ cluster freezes (load_cluster_freeze + verify_cluster_code)"
P2=$(mktemp -d "$SCR/e17pyc.XXXXXX")
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
P3=$(mktemp -d "$SCR/e17pyc.XXXXXX")
PYTHONPYCACHEPREFIX=$P3 uv run python -c '
from data.config import ACCOUNTS
from data.spend_gate import SpendGate
for a in sorted(ACCOUNTS):
    g=SpendGate(session_id="e17-checks-readonly", account=a)
    s=g.account_spent_usd()
    print(f"{a}: spent {s:.6f} cap {g.account_cap_usd:.2f} headroom {g.account_cap_usd-s:.6f}")
'
echo "\$ v2 freeze manifest (ml_route_v2.phase1.freeze.verify_v2_freeze)"
P4=$(mktemp -d "$SCR/e17pyc.XXXXXX")
PYTHONPYCACHEPREFIX=$P4 uv run python -c '
from ml_route_v2.phase1.freeze import verify_v2_freeze
m=verify_v2_freeze("reports/stage_e12_ml_v2_freeze.json","a647cd06c8f71f9549c0afa1c740bc32bad05e8f83ed57c87642a1586a0cad5b")
print("v2 freeze OK:", len(m.get("files", [])), "files")
'
echo "\$ uv run python -m screening.trial_registry status"
P5=$(mktemp -d "$SCR/e17pyc.XXXXXX")
PYTHONPYCACHEPREFIX=$P5 uv run python -m screening.trial_registry status
echo "\$ wc -l ledger/trial_registrations.jsonl; sha256sum"; wc -l < ledger/trial_registrations.jsonl; sha256sum ledger/trial_registrations.jsonl | cut -d' ' -f1
echo "\$ E.14 C1 freeze (reports/stage_e14_prereg_C1.md; pinned afc5c10f628771afa3d1311192316ff3b4b681d7308d2b411fc655c15f821c0b): sha256, tracked, no diff vs HEAD, commits touching"
sha256sum reports/stage_e14_prereg_C1.md | cut -d' ' -f1
git ls-files --error-unmatch reports/stage_e14_prereg_C1.md >/dev/null && echo tracked
git diff --quiet HEAD -- reports/stage_e14_prereg_C1.md && echo "no diff vs HEAD"
git log --format=%h -- reports/stage_e14_prereg_C1.md | tr '\n' ' '; echo
echo "\$ E.14 C1 freeze inputs list (reports/stage_e14_c1_freeze_inputs.json; pinned 3356d676...)"
P6=$(mktemp -d "$SCR/e17pyc.XXXXXX")
PYTHONPYCACHEPREFIX=$P6 uv run python -c '
import hashlib,json,pathlib
p=pathlib.Path("reports/stage_e14_c1_freeze_inputs.json"); d=json.loads(p.read_bytes())
bad=[f["path"] for f in d["files"] if not pathlib.Path(f["path"]).is_file() or hashlib.sha256(pathlib.Path(f["path"]).read_bytes()).hexdigest()!=f["sha256"]]
print("list sha256", hashlib.sha256(p.read_bytes()).hexdigest(), "entries", len(d["files"]), "mismatches", bad)
'
echo "\$ E.16 freeze: uv run python reports/stage_e16_briefs/freeze_manifest.py verify --expected 5274aa97f3359d7dcfaae15cb0590b6147d1624e6056ea396df08c6215209ad4"
P7=$(mktemp -d "$SCR/e17pyc.XXXXXX")
PYTHONPYCACHEPREFIX=$P7 uv run python reports/stage_e16_briefs/freeze_manifest.py verify --expected 5274aa97f3359d7dcfaae15cb0590b6147d1624e6056ea396df08c6215209ad4; echo "exit $?"
echo "\$ git diff --quiet 8f388c8 -- base_rules tests/test_base_rules_*.py reports/stage_e16_prereg_*.md"
git diff --quiet 8f388c8 -- base_rules tests/test_base_rules_*.py reports/stage_e16_prereg_*.md; echo "exit $?"
