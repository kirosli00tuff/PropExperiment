"""Step 1b: drop accounting across cells; equality of mo_10 and mo_nd_10 in the primary cell."""
import os
from pathlib import Path
import numpy as np, pandas as pd, pyarrow.parquet as pq
os.nice(10)
M = Path("/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e31_briefs/work/pilot/runs/measure31")
cols = ["trade_date","session","symbol","model","filled","mo_1","mo_10","mo_60","mo_nd_1","mo_nd_10","mo_nd_60","c_half"]
parts, dys = [], []
for d in sorted(p.name for p in M.iterdir() if p.is_dir()):
    t = pq.read_table(M/d/"placements.parquet", columns=cols).to_pandas()
    parts.append(t[t.filled]); dys.append(pq.read_table(M/d/"days.parquet").to_pandas())
f = pd.concat(parts, ignore_index=True); dy = pd.concat(dys, ignore_index=True)
g = f.groupby(["session","symbol","model"])
print(g.apply(lambda x: pd.Series({"fills": len(x), **{c+"_nan": int(x[c].isna().sum()) for c in ["mo_1","mo_10","mo_60","mo_nd_1","mo_nd_10","mo_nd_60"]}})).to_string())
p = f[(f.session=="DAY")&(f.symbol=="ZM.v.0")&(f.model=="c")]
print("primary mo_10==mo_nd_10:", int((p.mo_10==p.mo_nd_10).sum()), "of", len(p), "max abs diff", float(np.nanmax(np.abs(p.mo_10-p.mo_nd_10))))
inc = dy[dy.included]
print("crossed_moments sum by symbol:", inc.groupby("symbol").crossed_moments.sum().to_dict(), "bad_flag_records:", inc.groupby("symbol").bad_flag_records.sum().to_dict())
print("first date row:", dy[dy.trade_date.astype(str)=="2020-12-01"][["symbol","included","reason","instrument_id"]].to_string())
