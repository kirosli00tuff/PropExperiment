"""Stage E.17 (copied from E.15's write_hash_files.py, output names changed): write C1's two hash files (c1_replication/README.md step 3). Hashes only.

    uv run python reports/stage_e17_briefs/write_hash_files.py calendars
    uv run python reports/stage_e17_briefs/write_hash_files.py stores

calendars -> reports/stage_e17_c1_calendar_hashes.json (schema stage_e14_c1_calendar_hashes/1): the six hist
calendars, the release file and the energy full sessions, each with the sha256 C1's freeze names (its inputs
list reports/stage_e14_c1_freeze_inputs.json), checked against the file on disk.
stores -> reports/stage_e17_c1_store_hashes.json (schema stage_e14_c1_store_hashes/1, plan ext2010): the six
stores' parquet sha256 from reports/hist/bars_<ROOT>_ext2010.json, checked against the parquet on disk.
Each file is written once (refused if it exists). Prints the written file's sha256.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

INPUTS = Path("reports/stage_e14_c1_freeze_inputs.json")
INPUTS_SHA = "3356d67604245db99383215f1fb7f694d25a1beb71b0693a86faeb7243a5140e"
GROUPS = ("equity", "rates", "fx", "energy", "metals", "grains")
RELEASES = "reports/stage_e14_cal_releases.json"
FULL = "reports/stage_e14_cal_energy_full_sessions.json"
ROOTS = ("NG", "NQ", "ZN", "6E", "GC", "ZC")
CAL_OUT = Path("reports/stage_e17_c1_calendar_hashes.json")
STORE_OUT = Path("reports/stage_e17_c1_store_hashes.json")


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_once(path: Path, doc: dict) -> str:
    raw = (json.dumps(doc, indent=1) + "\n").encode()
    with path.open("xb") as fh:
        fh.write(raw)
    return hashlib.sha256(raw).hexdigest()


def frozen(path: str, pinned: dict[str, str]) -> dict[str, str]:
    if path not in pinned:
        raise SystemExit(f"{path} is not in C1's freeze inputs")
    if sha(Path(path)) != pinned[path]:
        raise SystemExit(f"{path}: sha256 on disk differs from the freeze's")
    return {"path": path, "sha256": pinned[path]}


def calendars() -> None:
    if sha(INPUTS) != INPUTS_SHA:
        raise SystemExit("the freeze inputs list is not the frozen one")
    pinned = {f["path"]: f["sha256"] for f in json.loads(INPUTS.read_bytes())["files"]}
    doc = {"schema": "stage_e14_c1_calendar_hashes/1",
           "calendars": {g: frozen(f"data/calendars/hist2010/{g}.json", pinned) for g in GROUPS},
           "releases": frozen(RELEASES, pinned), "energy_full_sessions": frozen(FULL, pinned)}
    print(CAL_OUT, write_once(CAL_OUT, doc))


def stores() -> None:
    out = {}
    for root in ROOTS:
        summary = json.loads(Path(f"reports/hist/bars_{root}_ext2010.json").read_bytes())
        parquet = summary["parquet"]
        if sha(Path(parquet["path"])) != parquet["sha256"]:
            raise SystemExit(f"{root}: the parquet on disk differs from its summary's sha256")
        out[root] = parquet["sha256"]
    doc = {"schema": "stage_e14_c1_store_hashes/1", "plan": "ext2010", "stores": out}
    print(STORE_OUT, write_once(STORE_OUT, doc))


if __name__ == "__main__":
    {"calendars": calendars, "stores": stores}[sys.argv[1]]()
