"""Second implementation (pandas) of the headline medians. Reads ts_event, instrument_id, volume only."""
import sys, json, datetime as dt
import numpy as np, pandas as pd, databento as db
s = db.DBNStore.from_file(sys.argv[1]); a = s.to_ndarray()
df = pd.DataFrame({"ts": a["ts_event"].astype("int64"), "iid": a["instrument_id"].astype("int64"), "vol": a["volume"].astype("int64")})
del a
df["date"] = pd.to_datetime(df.ts, unit="ns").dt.normalize()
rows = []
for raw, lst in s.metadata.mappings.items():
    for e in lst:
        rows.append((int(e["symbol"]), pd.Timestamp(e["start_date"]), pd.Timestamp(e["end_date"]), raw))
mp = pd.DataFrame(rows, columns=["iid", "sd", "ed", "raw"])
m = df.merge(mp, on="iid", how="left")
m = m[(m.date >= m.sd) & (m.date < m.ed)]
print("rows after interval join", len(m), "of", len(df), "| distinct ids in data", df.iid.nunique())
m["root"] = m.raw.str[:2]
o = m[~m.raw.str.contains("-") & (m.date.dt.dayofweek < 5)]
g = o.groupby(["root", "date"]).vol.sum().unstack("root").fillna(0)
w = g[(g.index >= "2025-10-01") & (g.index <= "2026-09-30")]
print("universe days", len(w), "median", w.median().to_dict())
own = {r: o[o.root == r].groupby("date").vol.sum() for r in ("QM", "ZM")}
print("own medians", {r: float(v[(v.index >= "2025-10-01") & (v.index <= "2026-09-30")].median()) for r, v in own.items()})
print("own days", {r: int(((v.index >= "2025-10-01") & (v.index <= "2026-09-30")).sum()) for r, v in own.items()})
