"""Step 1c: K1 bound under alternative resampling calls (rng.choice; per-replicate loop) and per-side means."""
import os
from pathlib import Path
import numpy as np, pandas as pd, pyarrow.parquet as pq
os.nice(10)
R = Path("/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e31_briefs/work/pilot/runs")
ds = R.joinpath("expected31.txt").read_text().split()
parts = []
for d in ds:
    t = pq.read_table(R/"measure31"/d/"placements.parquet", columns=["session","symbol","model","side","filled","mo_10","mo_nd_10","c_half"]).to_pandas()
    t = t[(t.session=="DAY")&(t.symbol=="ZM.v.0")&(t.model=="c")]
    if len(t): t = t.assign(td=d); parts.append(t)
p = pd.concat(parts); f = p[p.filled]
dates = sorted(p.td.unique())
for col in ("mo_10","mo_nd_10"):
    e = (f[col]+f.c_half)-0.264
    s = e.groupby(f.td).sum().reindex(dates, fill_value=0).values; n = e.groupby(f.td).size().reindex(dates, fill_value=0).values
    rng = np.random.default_rng(31); st = np.array([ (lambda i: s[i].sum()/n[i].sum())(rng.choice(len(dates), len(dates), replace=True)) for _ in range(2000)])
    print(col, "choice-loop seed31 CI", np.round(np.percentile(st,[2.5,97.5]),5), "mean", round(e.mean(),5),
          "buy", round(e[f.side==1].mean(),5), "sell", round(e[f.side==-1].mean(),5), "share E10>0", round(((f[col]+f.c_half)>0).mean(),4))
