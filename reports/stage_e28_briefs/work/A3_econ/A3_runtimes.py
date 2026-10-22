"""A3 runtimes from the logs and records on disk (no estimates) -> A3_runtimes.json. Usage: python3 A3_runtimes.py"""

from __future__ import annotations

import json
import re
from pathlib import Path

WORK = Path(__file__).resolve().parent


def _span(log: Path) -> dict[str, object] | None:
    if not log.exists():
        return None
    stamps = re.findall(r"^(\d\d:\d\d:\d\d) ", log.read_text(), flags=re.M)
    rc = re.findall(r"^rc=(\d+) (\d\d:\d\d:\d\d)", log.read_text(), flags=re.M)
    return {"log": log.name, "first_line_pdt": stamps[0] if stamps else None,
            "last_line_pdt": rc[-1][1] if rc else (stamps[-1] if stamps else None),
            "exit_code": int(rc[-1][0]) if rc else None, "lines_with_time": len(stamps)}


def _probe() -> dict[str, object]:
    t = (WORK / "time_probe.txt").read_text()
    el = re.search(r"Elapsed \(wall clock\) time \(h:mm:ss or m:ss\): (\S+)", t)
    rss = re.search(r"Maximum resident set size \(kbytes\): (\d+)", t)
    return {"what": "4 pairs (topstep, bulenox x NQ, MNQ) on 2 workers", "elapsed": el.group(1) if el else None,
            "maxrss_mb": int(rss.group(1)) // 1024 if rss else None}


def main() -> int:
    pairs = [json.loads(p.read_text()) for p in sorted((WORK / "pairs").glob("*.json"))
             if not p.name.startswith("opt2__")]
    comp = [r for r in pairs if r.get("computed")]
    grid = [json.loads(p.read_text()) for p in sorted((WORK / "gridcheck").glob("*.json"))]
    reg = json.loads((WORK / "A3_regress_e19.json").read_text())
    tests = (WORK / "test_A3_econ.out").read_text()
    el = re.search(r"Elapsed \(wall clock\) time \(h:mm:ss or m:ss\): (\S+)", tests)
    rss = re.search(r"Maximum resident set size \(kbytes\): (\d+)", tests)
    out = {
        "note": "times PDT from the logs' own stamps; per-pair seconds from the records (4 workers running at once)",
        "time_probe": _probe(),
        "main_run": {**(_span(WORK / "run_main.log") or {}), "pairs": 128, "workers": 4},
        "pair_seconds": {"sum": round(sum(r["runtime_s"] for r in pairs), 1),
                         "max": max(r["runtime_s"] for r in comp),
                         "evaluations_total": sum(r.get("n_evaluations", 0) for r in comp),
                         "maxrss_mb_max": max(r.get("maxrss_mb", 0) for r in comp)},
        "regression_e19_seconds": {k: reg[k]["seconds"] for k in ("e19_rules", "e26_refreshed_rules")},
        "unit_tests": {"elapsed": el.group(1) if el else None, "maxrss_mb": int(rss.group(1)) // 1024 if rss else None},
        "grid_check": {**(_span(WORK / "gridcheck_main.log") or {}), "pairs_on_disk": len(grid), "workers": 4,
                       "seconds_sum": round(sum(g["runtime_s"] for g in grid), 1),
                       "new_evaluations": sum(g["n_new_evaluations"] for g in grid),
                       "maxrss_mb_max": max((g["maxrss_mb"] for g in grid), default=None)},
        "bulenox_option2": _span(WORK / "opt2_main.log"),
    }
    (WORK / "A3_runtimes.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out)[:600])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
