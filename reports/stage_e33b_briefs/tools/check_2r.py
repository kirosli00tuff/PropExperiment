"""Lead check of LT1 prior=recompute (PipelineReview N24). Prints counts only."""
import collections
import json
from pathlib import Path

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
RES = REPO / "reports/stage_e33_briefs/work/b4_runs/LT1_recompute_2b30cb0e953b.json"
DRAW = REPO / "reports/stage_e33_briefs/work/LT1_draw.json"
FOLD = Path("/mnt/large-storage/market_data/PropExperiment/derived/e33/b4/lt_features/2b30cb0e953b/_lt1")

d = json.loads(RES.read_text())
r = d["results"]
draw = json.loads(DRAW.read_text())["times"]
want = {(x["date"], x["i"]) for x in draw}
got = {(x["date"], x["i"]) for x in r}
print("prior", d.get("prior"), "draws_picked", d.get("draws_picked"), "results", len(r),
      "unique", len(got), "no_production_table", len(d.get("no_production_table", [])))
print("set equal to draw:", got == want, "missing", len(want - got), "extra", len(got - want))
bad = [x for x in r if x["rows_after_t"] or x["bad_cols"]]
print("draws with rows_after_t > 0 or bad_cols:", len(bad))
t_by = {(x["date"], x["i"]): x["t_ns"] for x in draw}
counts = collections.Counter()
short = []
for key in sorted(got):
    folder = FOLD / str(t_by[key])
    n = len(list((folder / "_p1").glob("*.DONE"))) if folder.exists() else -1
    counts[n] += 1
    if n != 22:
        short.append((key[0], n))
print("pass-1 DONE markers per recompute folder:", dict(sorted(counts.items())))
print("folders not at 22:", short[:10], "..." if len(short) > 10 else "")
