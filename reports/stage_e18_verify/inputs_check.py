"""Check 4 (VerdictVerifier-FableXHigh, Stage E.18): the result's and the marker's input hashes
against the freeze manifest reports/stage_e18_freeze.json; every manifest file rehashed now; the
C1 freeze-inputs file and the files it lists rehashed now; the registry entry; marker.inputs equal
to result.inputs. Writes reports/stage_e18_verify/inputs_check.json; prints a summary only."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
MANIFEST = REPO / "reports" / "stage_e18_freeze.json"
RESULT = REPO / "reports" / "stage_e18_c1b_result.json"
MARKER = REPO / "reports" / "stage_e18_c1b_RUN_ONCE.json"
REGISTRY = REPO / "ledger" / "trial_registrations.jsonl"
OUT = REPO / "reports" / "stage_e18_verify" / "inputs_check.json"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def abs_path(p: str) -> Path:
    q = Path(p)
    return q if q.is_absolute() else REPO / q


def main() -> int:
    man = json.loads(MANIFEST.read_bytes())
    res = json.loads(RESULT.read_bytes())
    mark = json.loads(MARKER.read_bytes())
    inp = res["inputs"]
    rows = []

    def chk(item: str, want, got) -> None:  # noqa: ANN001
        rows.append({"item": item, "manifest_or_expected": want, "got": got, "equal": want == got})

    # 1. Every manifest-listed file hashes now to the manifest's value.
    listed = {}
    for group in ("files", "c1_inputs"):
        for rec in man[group]:
            p = abs_path(rec["path"])
            now = sha(p) if p.is_file() else None
            listed[rec["path"]] = rec["sha256"]
            chk(f"manifest.{group}: {rec['path']} (now)", rec["sha256"], now)
    for rec in man["external"]:
        if "path" in rec and "sha256" in rec:
            p = Path(rec["path"])
            chk(f"manifest.external: {rec['what']} (now)", rec["sha256"], sha(p) if p.is_file() else None)
    pins = man["pins"]
    for k, (p, s) in pins.items():
        chk(f"manifest.pins.{k}: {p} (now)", s, sha(abs_path(p)))
    # 2. The result's recorded inputs against the manifest.
    chk("result.inputs.freeze.sha256 vs manifest.files prereg", listed["reports/stage_e18_prereg_C1b.md"],
        inp["freeze"]["sha256"])
    chk("result.inputs.harness_sha256 vs pins.harness_v12", pins["harness_v12"][1], inp["harness_sha256"])
    chk("result.inputs.model.sha256 vs pins.model", pins["model"][1], inp["model"]["sha256"])
    ext = {r.get("what"): r for r in man["external"]}
    for h in ("h60", "hF"):
        chk(f"result.inputs.model.m1_payload_sha256.{h} vs external", ext[f"M1 {h} payload"]["sha256"],
            inp["model"]["m1_payload_sha256"][h])
        chk(f"result.inputs.model.q.{h} vs external q_repr", ext["q (model JSON q_repr)"]["q"][h],
            inp["model"]["q"][h])
    for r in ("NG", "NQ", "ZN", "6E", "GC", "ZC"):
        chk(f"result.inputs.stores.{r}.sha256 vs external", ext[f"ext2010 store {r}"]["sha256"],
            inp["stores"][r]["sha256"])
    chk("result.inputs.store_hashes_file.sha256 vs pins.store_hashes", pins["store_hashes"][1],
        inp["store_hashes_file"]["sha256"])
    chk("result.inputs.calendar_inputs.hashes_file.sha256 vs pins.calendar_hashes",
        pins["calendar_hashes"][1], inp["calendar_inputs"]["hashes_file"]["sha256"])
    cal_rec = inp["calendar_inputs"]["calendars"]
    for g in ("equity", "rates", "fx", "energy", "metals", "grains"):
        want = listed[f"data/calendars/hist2010/{g}.json"]
        got = cal_rec[g].get("sha256") if isinstance(cal_rec[g], dict) else None
        chk(f"result.inputs.calendar_inputs.calendars.{g}.sha256 vs manifest", want, got)
    rel = inp["calendar_inputs"]["releases"]
    chk("result.inputs.calendar_inputs.releases.sha256 vs manifest",
        listed["reports/stage_e14_cal_releases.json"], rel.get("sha256") if isinstance(rel, dict) else None)
    chk("result.inputs.calendar_inputs.energy_full_sessions.sha256 vs manifest",
        listed["reports/stage_e14_cal_energy_full_sessions.json"],
        inp["calendar_inputs"]["energy_full_sessions"].get("sha256"))
    chk("result.inputs.gate0_list.sha256 vs pins.gate0_list", pins["gate0_list"][1], inp["gate0_list"]["sha256"])
    v2 = inp["v2_freeze"]
    chk("result.inputs.v2_freeze manifest sha256 vs pins.v2_freeze", pins["v2_freeze"][1],
        v2.get("manifest_sha256") or v2.get("sha256") or (v2 if isinstance(v2, str) else None))
    code_want = {Path(p).name: s for p, s in listed.items() if p.startswith("c1_replication/")}
    chk("result.inputs.code_sha256 (c1_replication/*.py incl. c1b.py) vs manifest", code_want, inp["code_sha256"])
    chk("result.inputs.code_sha256 names", sorted(code_want), sorted(inp["code_sha256"]))
    chk("result.inputs.registry", {"entry_id": "r003-C1b", "n_before": 478, "n_after": 480},
        {k: inp["registry"].get(k) for k in ("entry_id", "n_before", "n_after")})
    chk("result.inputs.c1b record", {"test": "C1b", "test_ids": ["C1b-T1", "C1b-T2"],
                                     "exempt": ["g17_cl", "g17_mbt"]},
        {"test": inp["c1b"]["test"], "test_ids": inp["c1b"]["test_ids"],
         "exempt": sorted(inp["c1b"]["c10_exempt"])})
    chk("result.inputs.window", ["2010-06-07", "2019-04-30"], inp["window"])
    chk("marker.inputs == result.inputs", True, mark["inputs"] == inp)
    chk("marker.started_local == result.started_local", mark["started_local"], res["started_local"])
    chk("marker.out", "reports/stage_e18_c1b_result.json", mark["out"])
    # 3. The C1 freeze-inputs file and the files it lists.
    fi_path = abs_path(pins["c1_freeze_inputs"][0])
    fi = json.loads(fi_path.read_bytes())
    n_listed, n_ok, bad = 0, 0, []

    def walk(o, trail: str = "") -> None:  # noqa: ANN001
        nonlocal n_listed, n_ok
        if isinstance(o, dict):
            if "path" in o and "sha256" in o and isinstance(o["path"], str):
                p = abs_path(o["path"])
                if p.is_file():
                    n_listed += 1
                    if sha(p) == o["sha256"]:
                        n_ok += 1
                    else:
                        bad.append(o["path"])
            for k, v in o.items():
                walk(v, f"{trail}/{k}")
        elif isinstance(o, list):
            for v in o:
                walk(v, trail)

    walk(fi)
    chk("c1_freeze_inputs: listed files rehash now (n_ok == n_listed)", n_listed, n_ok)
    # 4. The registry entry.
    entries = [json.loads(line) for line in REGISTRY.read_text().splitlines() if line.strip()]
    c1b = [e for e in entries if e.get("test") == "C1b"]
    chk("registry: exactly one C1b entry", 1, len(c1b))
    e = c1b[0] if c1b else {}
    chk("registry.C1b.freeze_sha256 vs manifest prereg", listed["reports/stage_e18_prereg_C1b.md"],
        e.get("freeze_sha256"))
    chk("registry.C1b.harness_sha256 vs pins.harness_v12", pins["harness_v12"][1], e.get("harness_sha256"))
    chk("registry.C1b ids and N", {"test_ids": ["C1b-T1", "C1b-T2"], "n_before": 478, "n_after": 480},
        {k: e.get(k) for k in ("test_ids", "n_before", "n_after")})
    chk("registry: last entry n_after == 480", 480, entries[-1].get("n_after"))
    chk("registry: entry_id chain", "r003-C1b", entries[-1].get("entry_id"))
    unequal = [r for r in rows if not r["equal"]]
    OUT.write_text(json.dumps({"schema": "stage_e18_verify/inputs/1", "n_items": len(rows),
                               "n_unequal": len(unequal), "unequal": unequal, "rows": rows,
                               "c1_freeze_inputs_bad": bad}, indent=1) + "\n")
    print(f"items {len(rows)}, unequal {len(unequal)}; c1 freeze-inputs files listed {n_listed}, ok {n_ok}")
    for r in unequal:
        print(f"  UNEQUAL {r['item']}: want {str(r['manifest_or_expected'])[:80]!r} got {str(r['got'])[:80]!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
