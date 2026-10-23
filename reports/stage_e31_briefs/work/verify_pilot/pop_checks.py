"""Population-wide checks: (1) DAY grid in Chicago clock for every included date (DST), (2) days.instrument_id vs raw-file mapping."""
import json, os, datetime as dt
from zoneinfo import ZoneInfo
import numpy as np, pandas as pd, pyarrow.parquet as pq
import databento as db
os.nice(10)
ROOT = "/home/kiros-li/Documents/GitHub/PropExperiment/"
RUNS = ROOT + "reports/stage_e31_briefs/work/pilot/runs/"
exp = open(RUNS + "expected31.txt").read().split()
CHI = ZoneInfo("America/Chicago")
bad_grid, n_ok, dst_dates = [], 0, 0
want = [(8 * 60 + 35 + 5 * i) for i in range(56)]
D = []
for d in exp:
    p = pq.read_table(RUNS + f"measure31/{d}/placements.parquet", columns=["session", "symbol", "model", "g_ns", "j_ns", "price", "side"]).to_pandas()
    D.append(pd.read_parquet(RUNS + f"measure31/{d}/days.parquet").assign(td=d))
    q = p[(p.symbol == "ZM.v.0") & (p.session == "DAY") & (p.model == "c")]
    if len(q) == 0:
        continue
    t = pd.to_datetime(q.g_ns, unit="ns", utc=True).dt.tz_convert(CHI)
    hm = (t.dt.hour * 60 + t.dt.minute).to_numpy(); sec_ok = bool(((t.dt.second == 0) & (t.dt.microsecond == 0) & (t.dt.nanosecond == 0)).all())
    local_date_ok = bool((t.dt.date.astype(str) == d).all())
    ok = sec_ok and local_date_ok and sorted(set(hm.tolist())) == want and (q.groupby("g_ns").size() == 2).all()
    if t.iloc[0].dst() != dt.timedelta(0): dst_dates += 1
    (n_ok := n_ok + 1) if ok else bad_grid.append(d)
print("grid: dates ok", n_ok, "bad", bad_grid[:5], "dates in CDT", dst_dates)
D = pd.concat(D, ignore_index=True); Z = D[D.symbol == "ZM.v.0"]
# mapping check
M = json.load(open(RUNS + "manifest31.json")); paths = {f["month"]: f["path"] for f in M["files"] if f["series"] == "Z1"}
mism, checked = [], 0
for mon, path in sorted(paths.items()):
    mp = db.DBNStore.from_file(path).mappings["ZM.v.0"]
    zz = Z[Z.td.str.startswith(mon)]
    for _, r in zz.iterrows():
        Td = dt.date.fromisoformat(r.td)
        iids = [int(i["symbol"]) for i in mp if i["start_date"] <= Td < i["end_date"]]
        checked += 1
        if iids != [int(r.instrument_id)]:
            mism.append((r.td, iids, int(r.instrument_id)))
print("mapping: dates checked", checked, "mismatches", len(mism), mism[:5])
