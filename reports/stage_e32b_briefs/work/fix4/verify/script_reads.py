"""FixVerifier (F4) item 7: what each session-4 script reads. Lists the scripts modified or run in session 4 and greps
their file-opening expressions; flags anything under data/, parquet, dbn, bars, mbo, outcomes, ledger, holdout."""
import re
import subprocess
from pathlib import Path

B = Path(__file__).resolve().parents[3]
ROOT = B.parent.parent
cands = [
    "work/fix4/score/diff_score.py", "work/fix4/recs/scripts/build_draft_v3.py", "work/fix4/recs/scripts/assemble_s4.py",
    "work/R4/fix_lead_text_s4.py", "work/R2/patch_v31_q3_lead.py", "work/scope/build_scope.py", "work/score/score32b.py",
    "work/score/s32b_layer2.py", "work/score/r3_score.py", "work/rankmd/make_rankmd.py", "work/rankmd/extra_frags.py",
    "work/rankmd/assemble.py", "work/cost/make_cost.py", "work/score/make_fixture.py", "work/score/dry_run.py",
    "work/ret/quote_checks.py",
]
# add any .py under work/ modified since 08:40 PDT today
out = subprocess.run(["find", str(B / "work"), "-name", "*.py", "-newermt", "2026-10-29 08:40:00", "-not", "-path", "*/fix4/verify/*"],
                     capture_output=True, text=True).stdout.split()
for p in out:
    rel = str(Path(p).relative_to(B))
    if rel not in cands:
        cands.append(rel)
BAD = re.compile(r"data/|\.parquet|\.dbn|bars|mbo|outcome|holdout|ledger|trades\.|pnl|returns\.|\.zst|databento", re.I)
OPEN = re.compile(r"(open\(|read_text\(|read_bytes\(|json\.load|loads\(|Path\([^)]*\)|/ \"[^\"]+\"|glob\(|rglob\(|\"[^\"]+\.(json|md|jsonl|txt|csv|log)\")")
for rel in cands:
    p = B / rel
    if not p.exists():
        print(f"\n## {rel}: MISSING")
        continue
    mt = subprocess.run(["stat", "-c", "%y", str(p)], capture_output=True, text=True).stdout.strip()[:19]
    src = p.read_text()
    hits = sorted(set(m.group(0) for m in OPEN.finditer(src)))
    bad = sorted(set(l.strip()[:140] for l in src.splitlines() if BAD.search(l) and not l.strip().startswith("#")))
    print(f"\n## {rel} (mtime {mt}, {len(src.splitlines())} lines) open-like tokens {len(hits)}")
    paths = sorted(set(re.findall(r"\"([^\"]*\.(?:json|md|jsonl|txt|csv|log|py))\"", src)))
    print("  string paths:", paths[:40])
    if bad:
        print("  FLAGGED lines:", bad[:12])
