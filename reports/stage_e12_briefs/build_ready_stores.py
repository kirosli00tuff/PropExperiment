"""Stage E.12 Task 6: build the step 2 store of every phase-1 root whose training-window purchase is
complete and whose store is not built yet (lead-run; the frozen builder data.step2_store, harness v8).

    uv run python reports/stage_e12_briefs/build_ready_stores.py

Complete = the purchase manifest lists the expected number of kept chunks (58; MBT 35, from its
first priced month 2021-04) and no chunk at or after range=2024-03-01. Appends to store_builds.log.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V8 = "452c4a51ebfae33f6f18822c9b754634f1ce3ab879b88abe416633c75965a426"
BOUGHT = ["NQ", "GC", "6E", "ZL", "MBT", "LE", "HE", "UB", "CL", "ZS", "TN", "ZF", "ZB", "ZN", "ZT",
          "ZC", "YM", "RTY", "HG", "6S", "6J", "6A", "6B", "6N", "ZM", "ZW", "6C"]
EXPECTED = {"MBT": 35}
LOG = ROOT / "reports/stage_e12_briefs/store_builds.log"


def ready(root: str) -> bool:
    p = ROOT / f"reports/step2/purchase_{root}.json"
    if not p.exists():
        return False
    names = [f["name"] for f in json.loads(p.read_text())["files"]]
    late = [n for n in names if n >= "range=2024-03-01"]
    if late:
        raise SystemExit(f"{root}: chunk at or after 2024-03 in the purchase manifest: {late}")
    return len(names) == EXPECTED.get(root, 58)


def built(root: str) -> bool:
    p = ROOT / f"reports/step2/bars_{root}.json"
    return p.exists() and json.loads(p.read_text()).get("status") == "built"


def held(root: str) -> bool:
    p = ROOT / f"reports/step2/bars_{root}.json"
    return p.exists() and json.loads(p.read_text()).get("status") == "held_for_lead"


todo = [r for r in BOUGHT if ready(r) and not built(r) and not held(r)]
print("to build:", todo)
for r in todo:
    with LOG.open("a") as fh:
        rc = subprocess.run(["nice", "-n", "10", "uv", "run", "python", "-m", "data.step2_store",
                             "--products", r, "--harness-sha256", V8], cwd=ROOT, stdout=fh,
                            stderr=subprocess.STDOUT).returncode
    print(r, "rc", rc, "built" if built(r) else "NOT BUILT")  # a held root is reported, not fatal
print("built so far:", [r for r in BOUGHT if built(r)])
print("held for the lead:", [r for r in BOUGHT if held(r)])
