"""B3 diagnostic: Coder-A TB labels built with Coder-B's sigma_ZM(D) (implB/labels/_day/<D>.json), so the A-vs-B
TB comparison isolates the TB label logic from the sigma computation. Output under DERIVED/b3/tb_common_sigma/
<A code_sha12>/<LABEL>/<D>.parquet (never the production DERIVED/labels tree). Counts only on stdout.

Usage: uv run python reports/stage_e33_briefs/work/pipeline/tests_b3/tb_common_sigma.py [--procs 3]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
PIPE = HERE.parent
for p in (str(HERE), str(PIPE)):
    if p not in sys.path:
        sys.path.insert(0, p)

import build_labels33 as bl  # noqa: E402
import compare_b3 as cb  # noqa: E402
import guard33 as g  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--procs", type=int, default=3)
    args = ap.parse_args(argv)
    os.nice(10)
    if bl.available_mb() < bl.MIN_FREE_MB:
        raise SystemExit("available memory < 2 GB: not started")
    sha12, shas = bl.code_identity()
    out = g.DERIVED / "b3" / "tb_common_sigma" / sha12
    out.mkdir(parents=True, exist_ok=True)
    (out / "manifest.json").write_text(json.dumps(
        {"code_sha12": sha12, "code_files": shas, "sigma_source": "implB/labels/_day sigma_zm_ticks"}, indent=1))
    b_day = g.DERIVED / "implB" / "labels" / "_day"
    tasks = []
    for d in cb.b3_dates():
        sig = json.loads(g.check_path(b_day / f"{d}.json").read_text()).get("sigma_zm_ticks")
        tasks.append({"date": d, "labels": ["T15", "T30"], "out": str(out),
                      "sigma": None if sig is None else float(sig), "code_sha12": sha12,
                      "sigma_source": "implB/labels/_day"})
    with ProcessPoolExecutor(max_workers=max(1, min(args.procs, 3))) as pool:
        for res in pool.map(bl.build_date, tasks):
            per = " ".join(f"{k}:rows={v['rows']}" for k, v in res["labels"].items())
            print(f"{res['date']} excluded={res['excluded']} {per}", flush=True)
    print(f"out {out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
