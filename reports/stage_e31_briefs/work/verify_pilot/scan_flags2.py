"""List the F_MAYBE_BAD_BOOK (4) and non-snapshot F_BAD_TS_RECV (8) records of the ZM.v.0 instrument of each UTC date,
with their ts_recv, so they can be placed against each trade date's DAY session. Read-only; one row per flagged record."""
import json, os, datetime as dt
import databento as db
import numpy as np, pandas as pd
os.nice(10)
M = json.load(open("/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e31_briefs/work/pilot/runs/manifest31.json"))
files = sorted((f["month"], f["path"]) for f in M["files"] if f["series"] == "Z1")
rows = []
for mon, path in files:
    st = db.DBNStore.from_file(path)
    mp = st.mappings["ZM.v.0"]
    for df in st.to_df(price_type="fixed", pretty_ts=False, map_symbols=False, count=2_000_000):
        fl = df["flags"].to_numpy().astype("int64")
        m = ((fl & 4) > 0) | (((fl & 8) > 0) & ((fl & 32) == 0))
        if not m.any():
            continue
        x = df[m]
        tr = x.index.to_numpy().astype("int64")
        for t, ev, iid, a, f in zip(tr, x.ts_event.to_numpy().astype("int64"), x.instrument_id.to_numpy(), x.action.to_numpy(), x["flags"].to_numpy()):
            d = dt.datetime.fromtimestamp(t / 1e9, dt.timezone.utc).date()
            front = [int(i["symbol"]) for i in mp if i["start_date"] <= d < i["end_date"]]
            rows.append((mon, int(t), int(ev), int(iid), str(a), int(f), str(d), bool(front and front[0] == iid)))
R = pd.DataFrame(rows, columns=["file", "ts_recv", "ts_event", "iid", "action", "flags", "utc_date", "is_zm_v0"])
R.to_parquet("flagged_records.parquet")
print(len(R), R.is_zm_v0.sum())
