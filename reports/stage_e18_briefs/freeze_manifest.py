"""Stage E.18 Step 4: C1b's freeze manifest, reports/stage_e18_freeze.json.

    uv run python reports/stage_e18_briefs/freeze_manifest.py write
    uv run python reports/stage_e18_briefs/freeze_manifest.py verify --expected <manifest sha256>

"files": C1b's own frozen files (text, code, test, diff, generator, dry check and its outputs, listing evidence).
"c1_inputs": every C1 input C1b uses unchanged, re-hashed from disk and checked against the pins: C1's freeze and
its freeze-inputs list, every C1 code and test file (c1_replication/*.py except c1b.py, tests/test_c1_*.py,
tests/_c1_*.py), the E.12 state manifest, the model JSON, the v2 freeze, the Gate 0 list, the calendar-hashes and
store-hashes files of Stage E.17 and every file they name in the repo.
"external": files outside the repository, hashed from disk and checked: both M1 payloads (against the model JSON),
the six ext2010 stores (against the store-hashes file; file bytes are hashed, no bar is parsed), the E.12 state copy
(c1_replication.guards.verify_state against its manifest). q is cited from the model JSON (q_repr).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
MANIFEST = REPO / "reports" / "stage_e18_freeze.json"
SCHEMA = "stage_e18_freeze/1"
PINS = {
    "c1_freeze": ["reports/stage_e14_prereg_C1.md",
                  "afc5c10f628771afa3d1311192316ff3b4b681d7308d2b411fc655c15f821c0b"],
    "c1_freeze_inputs": ["reports/stage_e14_c1_freeze_inputs.json",
                         "3356d67604245db99383215f1fb7f694d25a1beb71b0693a86faeb7243a5140e"],
    "e12_state_manifest": ["reports/stage_e14_c1_e12_state_manifest.json",
                           "8a38eeb150ba7c063e1f7b4292b00efb0bd10549c61e8202fcb926bc8dab1ad9"],
    "model": ["reports/stage_e14_c1_model.json",
              "c6075306ddfd70cb22a2b32f8017ae41ba6050778e6cb66568d00b94585421e6"],
    "v2_freeze": ["reports/stage_e12_ml_v2_freeze.json",
                  "a647cd06c8f71f9549c0afa1c740bc32bad05e8f83ed57c87642a1586a0cad5b"],
    "gate0_list": ["reports/stage_e12_gate0_list.json",
                   "53e7ef576feba9959360b52a633b793175bce98d62a839fefa0f41baf19fa8ea"],
    "calendar_hashes": ["reports/stage_e17_c1_calendar_hashes.json",
                        "d5e48579d2bd70b2e73d7583010e7c7ef61f94cc58fe68b07e7734a12911f6f8"],
    "store_hashes": ["reports/stage_e17_c1_store_hashes.json",
                     "b77bfc183943a07561c6a79020820b43fb8c757e3023ef2e042093c48d3d2a08"],
    "harness_v12": ["reports/stage_e2b_harness_freeze.json",
                    "ece91ae8e6993ad3c64412d30cc0b6ff6a4af07a15a6956ce9f2927f7ea70d32"],
}
C1B_FILES = (
    "reports/stage_e18_prereg_C1b.md", "c1_replication/c1b.py", "tests/test_c1b.py",
    "reports/stage_e18_c1b_diff.md", "reports/stage_e18_briefs/make_c1b_text.py",
    "reports/stage_e18_briefs/make_diff_doc.py",
    "reports/stage_e18_briefs/dry_check.py", "reports/stage_e18_dry_check.json", "reports/stage_e18_dry_check.md",
    "reports/stage_e18_briefs/pages/LOG.md", "reports/stage_e18_briefs/pages/mbt_launch_20210503.html",
    "reports/stage_e18_briefs/pages/btc_selfcert_20171201.html", "reports/stage_e18_briefs/freeze_manifest.py",
)
STATE_COPY = Path.home() / ".cache" / "propexp_e14_c1" / "e12_state_copy"
M1_DIR = Path.home() / ".cache" / "propexp_e14_c1" / "m1"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def rec(path: Path) -> dict:
    return {"path": path.relative_to(REPO).as_posix(), "sha256": sha256(path), "bytes": path.stat().st_size}


def c1_input_paths() -> list[Path]:
    paths = [REPO / p for p, _ in PINS.values()]
    paths += sorted(p for p in (REPO / "c1_replication").glob("*.py") if p.name != "c1b.py")
    paths += sorted((REPO / "tests").glob("test_c1_*.py")) + sorted((REPO / "tests").glob("_c1_*.py"))
    cal = json.loads((REPO / PINS["calendar_hashes"][0]).read_text())
    named = [c["path"] for c in cal["calendars"].values()]
    named += [cal["releases"]["path"], cal["energy_full_sessions"]["path"]]
    paths += [REPO / p for p in named]
    return paths


def check_c1_inputs() -> list[str]:
    errors = [f"pin mismatch: {p}" for p, want in PINS.values() if sha256(REPO / p) != want]
    cal = json.loads((REPO / PINS["calendar_hashes"][0]).read_text())
    entries = [*cal["calendars"].values(), cal["releases"], cal["energy_full_sessions"]]
    errors += [f"calendar file differs from the hashes file: {e['path']}" for e in entries
               if sha256(REPO / e["path"]) != e["sha256"]]
    return errors


def external() -> tuple[list[dict], list[str]]:
    from c1_replication.guards import verify_state
    from c1_replication.q_m1 import payload_name
    from data.config import HIST_ROOT
    from data.hist_store import hist_parquet_path

    out, errors = [], []
    model = json.loads((REPO / PINS["model"][0]).read_text())
    for h, m in sorted(model["m1"].items()):
        p = M1_DIR / payload_name(h)
        got = sha256(p) if p.is_file() else None
        out.append({"what": f"M1 {h} payload", "path": str(p), "sha256": got})
        if got != m["payload_sha256"]:
            errors.append(f"M1 {h} payload differs from the model JSON")
    stores = json.loads((REPO / PINS["store_hashes"][0]).read_text())["stores"]
    for root, want in sorted(stores.items()):
        p = hist_parquet_path(root, "ext2010", HIST_ROOT)
        got = sha256(p) if p.is_file() else None
        out.append({"what": f"ext2010 store {root}", "path": str(p), "sha256": got})
        if got != want:
            errors.append(f"store {root} differs from the store-hashes file")
    try:
        st = verify_state(STATE_COPY, REPO / PINS["e12_state_manifest"][0], PINS["e12_state_manifest"][1])
        out.append({"what": "E.12 state copy", "path": str(STATE_COPY), "verify_state": st})
    except Exception as exc:  # noqa: BLE001
        errors.append(f"E.12 state copy: {exc}")
    out.append({"what": "q (model JSON q_repr)", "q": {h: model["q"][h]["q_repr"] for h in sorted(model["q"])}})
    return out, errors


def write() -> int:
    errors = check_c1_inputs()
    ext, ext_errors = external()
    errors += ext_errors
    if errors:
        print("REFUSED:\n" + "\n".join(errors))
        return 1
    body = {"schema": SCHEMA,
            "created_pdt": datetime.now(ZoneInfo("America/Vancouver")).strftime("%Y-%m-%d %H:%M:%S"),
            "pins": PINS, "files": [rec(REPO / p) for p in C1B_FILES],
            "c1_inputs": [rec(p) for p in c1_input_paths()], "external": ext}
    MANIFEST.write_text(json.dumps(body, indent=1) + "\n")
    print(f"wrote {MANIFEST.relative_to(REPO)}: {len(body['files'])} C1b files, {len(body['c1_inputs'])} C1 inputs, "
          f"{len(ext)} external; manifest sha256 {sha256(MANIFEST)}")
    return 0


def verify(expected: str) -> int:
    errors = []
    got = sha256(MANIFEST)
    if got != expected:
        errors.append(f"manifest sha256 {got} != expected {expected}")
    body = json.loads(MANIFEST.read_text())
    if body.get("schema") != SCHEMA or body.get("pins") != PINS:
        errors.append("schema or pins differ from this script's")
    for e in body["files"] + body["c1_inputs"]:
        p = REPO / e["path"]
        if not p.is_file():
            errors.append(f"missing: {e['path']}")
        elif sha256(p) != e["sha256"] or p.stat().st_size != e["bytes"]:
            errors.append(f"changed: {e['path']}")
    errors += check_c1_inputs()
    ext, ext_errors = external()
    errors += ext_errors
    if [x.get("sha256") for x in ext if "sha256" in x] != [x.get("sha256") for x in body["external"] if "sha256" in x]:
        errors.append("external hashes differ from the manifest's")
    n = len(body["files"]) + len(body["c1_inputs"])
    print("\n".join(errors) if errors else f"E.18 C1b freeze OK: {n} files, {len(ext)} external; manifest sha256 {got}")
    return 1 if errors else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("write", "verify"))
    ap.add_argument("--expected")
    a = ap.parse_args()
    if a.mode == "write":
        return write()
    if not a.expected:
        ap.error("verify needs --expected")
    return verify(a.expected)


if __name__ == "__main__":
    sys.exit(main())
