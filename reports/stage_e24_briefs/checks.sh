#!/usr/bin/env bash
# Stage E.24 start/end guardrail checks (E.23 checks.sh with this session scratchpad; E.22 list and F1 freeze pinned).
# C1 freeze verification). Prints the verbatim block quoted in the return. Usage: checks.sh <harness sha256>.
# pytest runs separately (pytest_*.out).
set -u
cd "$(dirname "$0")/../.."
H=${1:?harness sha256}
SCR=/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/c2dca792-060d-4694-91ef-4a6f3f808f1d/scratchpad
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
P=$(mktemp -d "$SCR/e24pyc.XXXXXX")
echo "\$ PYTHONPYCACHEPREFIX=<fresh> uv run python -m screening.harness_freeze verify --expected $H"
PYTHONPYCACHEPREFIX=$P uv run python -m screening.harness_freeze verify --expected "$H"
echo "\$ cluster freezes (load_cluster_freeze + verify_cluster_code)"
P2=$(mktemp -d "$SCR/e24pyc.XXXXXX")
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
P3=$(mktemp -d "$SCR/e24pyc.XXXXXX")
PYTHONPYCACHEPREFIX=$P3 uv run python -c '
from data.config import ACCOUNTS
from data.spend_gate import SpendGate
for a in sorted(ACCOUNTS):
    g=SpendGate(session_id="e24-checks-readonly", account=a)
    s=g.account_spent_usd()
    print(f"{a}: spent {s:.6f} cap {g.account_cap_usd:.2f} headroom {g.account_cap_usd-s:.6f}")
'
echo "\$ v2 freeze manifest (ml_route_v2.phase1.freeze.verify_v2_freeze)"
P4=$(mktemp -d "$SCR/e24pyc.XXXXXX")
PYTHONPYCACHEPREFIX=$P4 uv run python -c '
from ml_route_v2.phase1.freeze import verify_v2_freeze
m=verify_v2_freeze("reports/stage_e12_ml_v2_freeze.json","a647cd06c8f71f9549c0afa1c740bc32bad05e8f83ed57c87642a1586a0cad5b")
print("v2 freeze OK:", len(m.get("files", [])), "files")
'
echo "\$ uv run python -m screening.trial_registry status"
P5=$(mktemp -d "$SCR/e24pyc.XXXXXX")
PYTHONPYCACHEPREFIX=$P5 uv run python -m screening.trial_registry status
echo "\$ wc -l ledger/trial_registrations.jsonl; sha256sum"; wc -l < ledger/trial_registrations.jsonl; sha256sum ledger/trial_registrations.jsonl | cut -d' ' -f1
echo "\$ E.14 C1 freeze (reports/stage_e14_prereg_C1.md; pinned afc5c10f628771afa3d1311192316ff3b4b681d7308d2b411fc655c15f821c0b): sha256, tracked, no diff vs HEAD, commits touching"
sha256sum reports/stage_e14_prereg_C1.md | cut -d' ' -f1
git ls-files --error-unmatch reports/stage_e14_prereg_C1.md >/dev/null && echo tracked
git diff --quiet HEAD -- reports/stage_e14_prereg_C1.md && echo "no diff vs HEAD"
git log --format=%h -- reports/stage_e14_prereg_C1.md | tr '\n' ' '; echo
echo "\$ E.14 C1 freeze inputs list (reports/stage_e14_c1_freeze_inputs.json; pinned 3356d676...)"
P6=$(mktemp -d "$SCR/e24pyc.XXXXXX")
PYTHONPYCACHEPREFIX=$P6 uv run python -c '
import hashlib,json,pathlib
p=pathlib.Path("reports/stage_e14_c1_freeze_inputs.json"); d=json.loads(p.read_bytes())
bad=[f["path"] for f in d["files"] if not pathlib.Path(f["path"]).is_file() or hashlib.sha256(pathlib.Path(f["path"]).read_bytes()).hexdigest()!=f["sha256"]]
print("list sha256", hashlib.sha256(p.read_bytes()).hexdigest(), "entries", len(d["files"]), "mismatches", bad)
'
echo "\$ E.16 freeze: uv run python reports/stage_e16_briefs/freeze_manifest.py verify --expected 5274aa97f3359d7dcfaae15cb0590b6147d1624e6056ea396df08c6215209ad4"
P7=$(mktemp -d "$SCR/e24pyc.XXXXXX")
PYTHONPYCACHEPREFIX=$P7 uv run python reports/stage_e16_briefs/freeze_manifest.py verify --expected 5274aa97f3359d7dcfaae15cb0590b6147d1624e6056ea396df08c6215209ad4; echo "exit $?"
echo "\$ git diff --quiet 8f388c8 -- base_rules tests/test_base_rules_*.py reports/stage_e16_prereg_*.md"
git diff --quiet 8f388c8 -- base_rules tests/test_base_rules_*.py reports/stage_e16_prereg_*.md; echo "exit $?"
echo "\$ E.18 C1b freeze: uv run python reports/stage_e18_briefs/freeze_manifest.py verify --expected 5ed208a21c2556e84830aca6fb7b2dba08a3012713f62de6e7bd1c57fb702d03"
P8=$(mktemp -d "$SCR/e24pyc.XXXXXX")
PYTHONPYCACHEPREFIX=$P8 uv run python reports/stage_e18_briefs/freeze_manifest.py verify --expected 5ed208a21c2556e84830aca6fb7b2dba08a3012713f62de6e7bd1c57fb702d03; echo "exit $?"
echo "\$ git diff --quiet b714751 -- c1_replication/c1b.py tests/test_c1b.py reports/stage_e18_prereg_C1b.md reports/stage_e18_freeze.json"
git diff --quiet b714751 -- c1_replication/c1b.py tests/test_c1b.py reports/stage_e18_prereg_C1b.md reports/stage_e18_freeze.json; echo "exit $?"
echo "\$ git diff --quiet HEAD -- ml_route_v2 rules sim screening data/holdout.py live ops"
git diff --quiet HEAD -- ml_route_v2 rules sim screening data/holdout.py live ops; echo "exit $?"
echo "\$ E.20 store sha256 (17 roots; step2 search stores and the ext2010/ext2010h backward stores, hashed as bytes, never decoded) vs reports/stage_e17_run_manifest.json"
python3 - <<'PY'
import hashlib, json, pathlib
ROOTS = ["NG","NQ","ZN","6E","GC","ZC","ZT","ZF","ZB","UB","TN","CL","ZL","ZS","RTY","HE","LE"]
m = json.loads(pathlib.Path("reports/stage_e17_run_manifest.json").read_bytes())["stores"]
def h(p):
    d = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): d.update(b)
    return d.hexdigest()
bad = []; n = 0
for r in ROOTS:
    for kind in ("step2", "ext2010"):
        e = m[r][kind]; n += 1
        if h(e["path"]) != e["sha256"]: bad.append((r, kind))
print("stores checked", n, "mismatches", bad)
PY
echo "\$ E.20 H6 freeze: PYTHONPATH=. uv run python reports/stage_e20_briefs/h6_freeze_manifest.py verify 22e606f0b74532e267a4155d93e295702ff86f6e8f4143236882f3c2f230e795"
if [ -f reports/stage_e20_h6_freeze.json ]; then P9=$(mktemp -d "$SCR/e24pyc.XXXXXX"); PYTHONPATH=. PYTHONPYCACHEPREFIX=$P9 uv run python reports/stage_e20_briefs/h6_freeze_manifest.py verify 22e606f0b74532e267a4155d93e295702ff86f6e8f4143236882f3c2f230e795; echo "exit $?"; else echo "not yet written"; fi
echo "\$ E.20 search freeze: uv run python -m pattern_search.freeze_manifest verify --sha256 94ee86b02d1cb644c9307be958b7791587d42c062996a6220dc901d4fe5a0f2f"
if [ -f reports/stage_e20_search_freeze.json ]; then P10=$(mktemp -d "$SCR/e24pyc.XXXXXX"); PYTHONPYCACHEPREFIX=$P10 uv run python -m pattern_search.freeze_manifest verify --sha256 94ee86b02d1cb644c9307be958b7791587d42c062996a6220dc901d4fe5a0f2f 2>&1 | tail -2; echo "exit ${PIPESTATUS[0]}"; else echo "not yet written"; fi
echo "\$ E.21 freeze: uv run python -m multiday.freeze_manifest verify --sha256 0bb899e56729d84075f43d72ae7e4207a026a955f1b39b39b490330a2e03bb1e"
P11=$(mktemp -d "$SCR/e24pyc.XXXXXX"); PYTHONPYCACHEPREFIX=$P11 uv run python -m multiday.freeze_manifest verify --sha256 0bb899e56729d84075f43d72ae7e4207a026a955f1b39b39b490330a2e03bb1e 2>&1 | tail -2; echo "exit ${PIPESTATUS[0]}"
echo "\$ E.22 confirmation list and E22-F1 registration (pinned 6f2fbf38... and 04ef33a6...)"
for f in reports/stage_e22_confirmation_list.md reports/stage_e22_prereg_F1.md; do sha256sum "$f"; git ls-files --error-unmatch "$f" >/dev/null 2>&1 && { git diff --quiet HEAD -- "$f" && echo "tracked, no diff vs HEAD"; } || echo "untracked"; done
echo "\$ E.23 freeze and registration (written during the stage)"
for f in reports/stage_e23_freeze.json reports/stage_e23_prereg.md; do if [ -f "$f" ]; then sha256sum "$f"; git ls-files --error-unmatch "$f" >/dev/null 2>&1 && { git diff --quiet HEAD -- "$f" && echo "tracked, no diff vs HEAD"; } || echo "untracked"; else echo "$f not yet written"; fi; done
echo "\$ E.23 freeze: uv run python -m trigger_hold.freeze_manifest verify --sha256 24dcf4dd671dbada927f548b3aff7a58a89c8fa92a6d43ae498aa69cbb3df5a5"
P12=$(mktemp -d "$SCR/e24pyc.XXXXXX"); PYTHONPYCACHEPREFIX=$P12 uv run python -m trigger_hold.freeze_manifest verify --sha256 24dcf4dd671dbada927f548b3aff7a58a89c8fa92a6d43ae498aa69cbb3df5a5 2>&1 | tail -2; echo "exit ${PIPESTATUS[0]}"
echo "\$ E22-F1 frozen file set: sha256sum -c reports/stage_e22_f1_files.sha256 (list pinned bb3bf3b3...)"
sha256sum reports/stage_e22_f1_files.sha256 | cut -d' ' -f1
sha256sum -c --quiet reports/stage_e22_f1_files.sha256 && echo "all $(wc -l < reports/stage_e22_f1_files.sha256) files OK"; echo "exit $?"
echo "\$ E.24 E22-F2 freeze and registration (written during the stage)"
for f in reports/stage_e24_prereg_F2.md reports/stage_e24_f2_files.sha256; do if [ -f "$f" ]; then sha256sum "$f"; git ls-files --error-unmatch "$f" >/dev/null 2>&1 && { git diff --quiet HEAD -- "$f" && echo "tracked, no diff vs HEAD"; } || echo "untracked"; else echo "$f not yet written"; fi; done
if [ -f reports/stage_e24_f2_files.sha256 ]; then sha256sum -c --quiet reports/stage_e24_f2_files.sha256 && echo "all $(wc -l < reports/stage_e24_f2_files.sha256) F2 files OK"; echo "exit $?"; fi
echo "\$ .env variable names (status only; values never read)"
if [ -f .env ]; then python3 - <<'PY'
import re
names = ("IBKR_", "IB_", "ALPACA_", "APCA_")
for line in open(".env", encoding="utf-8", errors="replace"):
    m = re.match(r"\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$", line)
    if m and m.group(1).startswith(names):
        print(m.group(1), "non-empty" if m.group(2).strip().strip("'\"") else "empty")
PY
else echo ".env absent"; fi
