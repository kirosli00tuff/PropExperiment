"""Extract, from the raw Z1 MBO file, the records of the ZM.v.0 instrument for one calendar (UTC) date T from
23:55Z on T-1 to 19:30Z on T. Own code; DBNStore only. Output: raw_extract/<T>.parquet (fixed-point prices)."""
import json, sys, os
import databento as db
import numpy as np
import pandas as pd
os.nice(10)
paths = json.load(open("raw_paths.json"))
pick = json.load(open("picked_dates.json"))
CHUNK = 2_000_000
for y, T in pick.items():
    mon = T[:7]
    st = db.DBNStore.from_file(paths[mon])
    mp = st.mappings["ZM.v.0"]
    import datetime as dt
    Td = dt.date.fromisoformat(T)
    iids = [int(x["symbol"]) for x in mp if x["start_date"] <= Td < x["end_date"]]
    assert len(iids) == 1, (T, mp)
    iid = iids[0]
    lo = pd.Timestamp(T, tz="UTC") - pd.Timedelta(minutes=5)
    hi = pd.Timestamp(T, tz="UTC") + pd.Timedelta(hours=19, minutes=30)
    lo_ns, hi_ns = lo.value, hi.value
    keep = []
    n = 0
    for df in st.to_df(price_type="fixed", pretty_ts=False, map_symbols=False, count=CHUNK):
        n += len(df)
        tr = df.index.to_numpy().astype("int64") if df.index.dtype != "int64" else df.index.to_numpy()
        m = (df.instrument_id.to_numpy() == iid) & (tr >= lo_ns) & (tr <= hi_ns)
        if m.any():
            x = df[m].copy()
            x.insert(0, "ts_recv", tr[m])
            keep.append(x.reset_index(drop=True))
        if len(df) and tr.min() > hi_ns:
            pass
    X = pd.concat(keep, ignore_index=True)
    X.to_parquet(f"raw_extract/{T}.parquet")
    print(T, "iid", iid, "records_in_file", n, "extracted", len(X), list(X.columns))
    json.dump({"iid": iid}, open(f"raw_extract/{T}.meta.json", "w"))
