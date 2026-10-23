"""Step 3a (after opening stats31): K1/K3 bounds with the producer's stated pool (all 816 done dates, one draw matrix)."""
import os
from pathlib import Path
import numpy as np, pandas as pd, pyarrow.parquet as pq
os.nice(10)
R = Path("/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e31_briefs/work/pilot/runs")
ds = sorted(R.joinpath("expected31.txt").read_text().split())
S = np.zeros(len(ds)); N = np.zeros(len(ds)); L = np.zeros(len(ds)); LN = np.zeros(len(ds))
for i, d in enumerate(ds):
    t = pq.read_table(R/"measure31"/d/"placements.parquet", columns=["session","symbol","model","filled","mo_10","c_half"]).to_pandas()
    t = t[(t.session=="DAY")&(t.symbol=="ZM.v.0")&(t.model=="c")&t.filled]
    S[i] = (t.mo_10 + t.c_half - 0.264).sum(); N[i] = len(t)
    l = pq.read_table(R/"measure31"/d/"loop.parquet").to_pandas(); l = l[(l.symbol=="ZM.v.0")&(l.model=="c")]
    if len(l): L[i] = l.round_trips.iloc[0]; LN[i] = 1
for how in ("integers", "choice"):
    rng = np.random.default_rng(31)
    idx = rng.integers(0, len(ds), size=(2000, len(ds))) if how == "integers" else rng.choice(len(ds), size=(2000, len(ds)), replace=True)
    k1 = S[idx].sum(1)/N[idx].sum(1); k3 = L[idx].sum(1)/LN[idx].sum(1)
    print(how, "K1", np.round(np.percentile(k1,[2.5,97.5]),6), "K1@0.528", np.round(np.percentile(k1-0.264,[2.5,97.5]),6), "K3", np.round(np.percentile(k3,[2.5,97.5]),6))
