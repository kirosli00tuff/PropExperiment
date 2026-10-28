"""LT1 timing probe (brief: time 5 rebuilds first, then project): 5 draws of LT1_draw.json whose 21 history dates
have production pass-1 tables, one with prior=recompute (all 22 dates re-streamed) and four with prior=production
(D re-streamed; history from production pass 1). Production pass 2 is built first where a date lacks its table.
Writes reports/stage_e33_briefs/work/b4_runs/LT1_timing.json. Counts and seconds only."""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import build_features33 as bf  # noqa: E402
import cal33  # noqa: E402
import lt1_truncation as lt  # noqa: E402

os.nice(10)
fdir = Path(sys.argv[1])
draw = json.loads(lt.DRAW_PATH.read_text())["times"]
have = {p.name[:10] for p in (fdir / "_p1").glob("*.npz")}
cands = [x for x in draw if x["date"] in have
         and all(h.isoformat() in have for h in cal33.previous_trade_dates(x["date"], 21))]
pick = cands[:5]
out = {"picked": [(x["date"], x["i"]) for x in pick], "runs": []}
for n, x in enumerate(pick):
    t0 = time.time()
    if not (fdir / f"{x['date']}.parquet").exists():
        bf.build([cal33.as_date(x["date"]) if hasattr(cal33, "as_date") else
                  __import__("datetime").date.fromisoformat(x["date"])], 1, fdir.parent)
    t_prod = time.time() - t0
    prior = "recompute" if n == 0 else "production"
    r = lt.check_one(fdir, x, prior)
    r.update({"prior": prior, "seconds_production_pass2": round(t_prod, 1)})
    out["runs"].append(r)
    (HERE.parents[1] / "b4_runs" / "LT1_timing.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(r), flush=True)
