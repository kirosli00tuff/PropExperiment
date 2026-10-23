"""Sensitivity of the two verdicts to definition choices. Reads ts_event, instrument_id, volume only."""
import sys, numpy as np, pandas as pd, databento as db
s = db.DBNStore.from_file(sys.argv[1]); a = s.to_ndarray()
df = pd.DataFrame({"ts": a["ts_event"].astype("int64"), "iid": a["instrument_id"].astype("int64"), "vol": a["volume"].astype("int64")}); del a
df["date"] = pd.to_datetime(df.ts, unit="ns").dt.normalize()
rows = [(int(e["symbol"]), pd.Timestamp(e["start_date"]), pd.Timestamp(e["end_date"]), raw) for raw, l in s.metadata.mappings.items() for e in l]
mp = pd.DataFrame(rows, columns=["iid", "sd", "ed", "raw"])
m = df.merge(mp, on="iid"); m = m[(m.date >= m.sd) & (m.date < m.ed)].copy()
m["root"] = m.raw.str[:2]; m["dow"] = m.date.dt.dayofweek
W0, W1 = pd.Timestamp("2025-10-01"), pd.Timestamp("2026-09-30")
def med(frame, root, extra_days=None):
    g = frame[frame.root == root].groupby("date").vol.sum()
    uni = sorted(set(frame[frame.dow < 5].date))
    g = g.reindex(uni, fill_value=0); g = g[(g.index >= W0) & (g.index <= W1)]
    return float(g.median()), len(g)
o = m[~m.raw.str.contains("-")]
base = o[o.dow < 5]
print("base", {r: med(base, r) for r in ("QM", "ZM")})
print("ZM without 'ZM:CF' colon spreads", med(base[~base.raw.str.contains(":")], "ZM"))
# Sunday volume folded into the next Monday
f = o.copy(); f.loc[f.dow == 6, "date"] += pd.Timedelta(days=1); f.loc[f.dow == 6, "dow"] = 0
print("weekend folded into Monday", {r: med(f[f.dow < 5], r) for r in ("QM", "ZM")})
# including hyphen spreads (upper bound)
al = m[m.dow < 5]
print("with spreads (not the rule)", {r: med(al, r) for r in ("QM", "ZM")})
# lowest median over any single calendar quarter in the span (primary universe, outrights)
g = base.groupby(["root", "date"]).vol.sum().unstack("root").fillna(0)
q = g.groupby(g.index.to_period("Q")).median()
print("min quarterly median QM/ZM", q.min().to_dict(), "at", q.idxmin().to_dict())
# month by month in the window
gm = g[(g.index >= W0) & (g.index <= W1)].groupby(g[(g.index >= W0) & (g.index <= W1)].index.to_period("M")).median()
print("window monthly medians min QM/ZM", gm.min().to_dict())
