"""Stage E.15 Step 1: verify C1's freeze by script before anything else (freeze section 11; model file step 1).

Checks, each recorded in reports/stage_e15_briefs/verify_freeze.json (hashes and counts only, no data value):
1. reports/stage_e14_c1_freeze_inputs.json hashes to its pinned sha256 and every one of its 43 entries matches
   (sha256 and bytes);
2. the freeze file hashes to its pinned sha256, is tracked, has no diff against HEAD, was added in 1680982 and
   no later commit touched it (its blob at 1680982 equals the working file);
3. the E.12 state copy matches reports/stage_e14_c1_e12_state_manifest.json (c1_replication.guards.verify_state:
   every file's size and sha256, nothing extra);
4. reports/stage_e14_c1_model.json and both M1 payload files hash to the values recorded in Stage E.14 (model
   file reports/stage_e14_c1_model.md, reports/stage_e14_STATE.md), and the JSON's own payload sha256s and q
   equal them;
5. the harness preflight at v10 (the manifest is also a freeze input).
Exit 0 iff every check passes. Usage (repo root): uv run python reports/stage_e15_briefs/verify_freeze.py
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

INPUTS = Path("reports/stage_e14_c1_freeze_inputs.json")
INPUTS_SHA = "3356d67604245db99383215f1fb7f694d25a1beb71b0693a86faeb7243a5140e"
FREEZE = Path("reports/stage_e14_prereg_C1.md")
FREEZE_SHA = "afc5c10f628771afa3d1311192316ff3b4b681d7308d2b411fc655c15f821c0b"
FREEZE_COMMIT = "1680982"
STATE_DIR = Path("~/.cache/propexp_e14_c1/e12_state_copy").expanduser()
STATE_MANIFEST = Path("reports/stage_e14_c1_e12_state_manifest.json")
STATE_MANIFEST_SHA = "8a38eeb150ba7c063e1f7b4292b00efb0bd10549c61e8202fcb926bc8dab1ad9"
MODEL = Path("reports/stage_e14_c1_model.json")
MODEL_SHA = "c6075306ddfd70cb22a2b32f8017ae41ba6050778e6cb66568d00b94585421e6"
MODEL_DIR = Path("~/.cache/propexp_e14_c1/m1").expanduser()
PAYLOADS = {"h60": ("c1_m1_h60.ridge", "9c2d9986ec788a0abcd08186cf249061f91ed0794d3519532ef779de4ccfb9d8"),
            "hF": ("c1_m1_hF.ridge", "153c2bdc25087e0b2f2f236d46fa186e78bb85fa2d50d8702d4c7e5ac4dfbe99")}
Q_REPR = {"h60": "0.033735277284776724", "hF": "0.0831931045522869"}
HARNESS_V10 = "fde3a49c8e15f08b36108e9a32d062f08f342fe2414607d33a7b8981ef00e34b"
OUT = Path("reports/stage_e15_briefs/verify_freeze.json")


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], capture_output=True, text=True)


def check_inputs() -> dict:
    got = sha(INPUTS)
    doc = json.loads(INPUTS.read_bytes())
    bad, roles = [], {}
    for f in doc["files"]:
        roles[f["role"]] = roles.get(f["role"], 0) + 1
        p = Path(f["path"])
        if not p.is_file():
            bad.append(f"{f['path']}: missing")
            continue
        raw = p.read_bytes()
        if len(raw) != f["bytes"] or hashlib.sha256(raw).hexdigest() != f["sha256"]:
            bad.append(f"{f['path']}: differs")
    return {"list_sha256": got, "list_sha256_ok": got == INPUTS_SHA, "n_entries": len(doc["files"]),
            "roles": roles, "harness_manifest_sha256_in_list": doc.get("harness_manifest_sha256"),
            "mismatches": bad, "ok": got == INPUTS_SHA and not bad and len(doc["files"]) == 43}


def check_freeze_git() -> dict:
    got = sha(FREEZE)
    tracked = git("ls-files", "--error-unmatch", str(FREEZE)).returncode == 0
    no_diff = git("diff", "--quiet", "HEAD", "--", str(FREEZE)).returncode == 0
    commits = git("log", "--format=%h", "--", str(FREEZE)).stdout.split()
    later = git("log", "--format=%h", f"{FREEZE_COMMIT}..HEAD", "--", str(FREEZE)).stdout.split()
    blob = subprocess.run(["git", "show", f"{FREEZE_COMMIT}:{FREEZE}"], capture_output=True).stdout
    blob_sha = hashlib.sha256(blob).hexdigest()
    ok = got == FREEZE_SHA and tracked and no_diff and commits == [FREEZE_COMMIT] and not later \
        and blob_sha == FREEZE_SHA
    return {"sha256": got, "sha256_ok": got == FREEZE_SHA, "tracked": tracked, "no_diff_vs_head": no_diff,
            "commits_touching": commits, "commits_after_freeze": later, "blob_at_freeze_commit_sha256": blob_sha,
            "ok": ok}


def check_state() -> dict:
    from c1_replication.guards import C1Refused, verify_state

    try:
        rec = verify_state(STATE_DIR, STATE_MANIFEST, STATE_MANIFEST_SHA)
        return {**rec, "ok": rec["n_files"] == 51}
    except C1Refused as exc:
        return {"ok": False, "refused": str(exc)}


def check_model() -> dict:
    got = sha(MODEL)
    doc = json.loads(MODEL.read_bytes())
    out = {"model_sha256": got, "model_sha256_ok": got == MODEL_SHA, "payloads": {}, "q": {}}
    ok = got == MODEL_SHA
    for h, (name, want) in PAYLOADS.items():
        p = MODEL_DIR / name
        file_sha = sha(p) if p.is_file() else None
        in_json = doc["m1"][h]["payload_sha256"]
        mode = oct(p.stat().st_mode & 0o777) if p.is_file() else None
        out["payloads"][h] = {"file_sha256": file_sha, "json_sha256": in_json, "expected": want, "mode": mode,
                              "ok": file_sha == want == in_json}
        q = doc["q"][h]
        out["q"][h] = {"q_repr": q["q_repr"], "expected": Q_REPR[h], "ok": q["q_repr"] == Q_REPR[h] == repr(q["q"])}
        ok = ok and out["payloads"][h]["ok"] and out["q"][h]["ok"]
    out["ok"] = ok
    return out


def check_harness() -> dict:
    from screening.harness_freeze import HarnessFreezeError, preflight

    try:
        return {"preflight": preflight(HARNESS_V10), "ok": True}
    except HarnessFreezeError as exc:
        return {"ok": False, "refused": str(exc)[:300]}


def main() -> int:
    started = datetime.now(ZoneInfo("America/Vancouver")).isoformat(timespec="seconds")
    res = {"schema": "stage_e15_verify_freeze/1", "started_local": started,
           "inputs": check_inputs(), "freeze": check_freeze_git(), "e12_state": check_state(),
           "model": check_model(), "harness_v10": check_harness()}
    res["all_ok"] = all(res[k]["ok"] for k in ("inputs", "freeze", "e12_state", "model", "harness_v10"))
    res["finished_local"] = datetime.now(ZoneInfo("America/Vancouver")).isoformat(timespec="seconds")
    OUT.write_text(json.dumps(res, indent=1) + "\n")
    for k in ("inputs", "freeze", "e12_state", "model", "harness_v10"):
        r = res[k]
        extra = {"inputs": lambda: f"{r['n_entries']} entries {r['roles']} mismatches {r['mismatches']}",
                 "freeze": lambda: f"tracked {r['tracked']} no_diff {r['no_diff_vs_head']} commits "
                                   f"{r['commits_touching']} later {r['commits_after_freeze']}",
                 "e12_state": lambda: f"{r.get('n_files')} files ({r.get('n_npy')} npy) {r.get('refused', '')}",
                 "model": lambda: " ".join(f"{h} payload {v['ok']} q {r['q'][h]['ok']} mode {v['mode']}"
                                           for h, v in r["payloads"].items()),
                 "harness_v10": lambda: r.get("preflight", r.get("refused"))}[k]()
        print(f"{k}: ok {r['ok']}; {extra}")
    print(f"ALL_OK {res['all_ok']}; {OUT} sha256 {sha(OUT)}")
    return 0 if res["all_ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
