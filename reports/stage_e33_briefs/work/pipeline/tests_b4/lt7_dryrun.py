"""LT7 mechanics dry run (not the LT7 test): fit two configurations (E33-S5F15L001A, E33-S5T30L001A) with search33 on
SYNTHETIC tables over the real 796 OOF dates (synth_search33.write_tables; no real outcome), then run lt7_causality
on the LT1 timing draws that have production features, LT1 rebuilds and production label tables. Checks the script
end to end before the seed-1 proof models exist. Output: reports/stage_e33_briefs/work/b4_runs/LT7_dryrun.json."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for p in (str(HERE), str(HERE.parent), str(HERE.parent / "tests")):
    sys.path.insert(0, p)
os.environ.setdefault("OMP_NUM_THREADS", "1")
import cal33  # noqa: E402
import guard33 as g  # noqa: E402
import search33 as s  # noqa: E402
import synth_search33 as gs  # noqa: E402

import lt7_causality as lt7  # noqa: E402

os.nice(10)
pdir = g.DERIVED / "b4" / "lt7_dry"
root = pdir / "seed1"
cfgs = ("E33-S5F15L001A", "E33-S5T30L001A")
if not (root / "labels").exists():
    gs.write_tables(root, [d.isoformat() for d in cal33.oof_dates()], ("F15", "T30"), seed=1, beta=0.0)
for cid in cfgs:
    for k in range(1, 7):
        if not lt7._model_path(pdir, 1, cid, k).exists():
            print(s.run_fold(root, cid, k, threads=1), flush=True)
work = HERE.parents[1]
timing = json.loads((work / "b4_runs" / "LT1_timing.json").read_text())
draw_all = json.loads((work / "LT1_draw.json").read_text())["times"]
picked = {(d, i) for d, i in timing["picked"]}
draw = {"times": [x for x in draw_all if (x["date"], x["i"]) in picked]}
dpath = pdir / "draw_dry.json"
dpath.write_text(json.dumps(draw))
feat = g.DERIVED / "features" / sys.argv[1]
lab = g.DERIVED / "labels" / sys.argv[2]
raise SystemExit(lt7.main(["--features", str(feat), "--labels", str(lab), "--proofs-dir", str(pdir), "--seed", "1",
                           "--draw", str(dpath), "--configs", ",".join(cfgs),
                           "--out", str(work / "b4_runs" / "LT7_dryrun.json")]))
