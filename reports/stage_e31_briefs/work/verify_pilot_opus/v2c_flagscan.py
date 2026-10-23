"""Step 2c: every Z1 month file: ZM.v.0 records flagged MAYBE_BAD_BOOK / TOB / MBP after the date's first R.

Trade date of a record: the D with ts_recv in [D-1 16:00 CT, D 16:00 CT). Front instrument from the DBN's own
symbology mappings. Output: v2c_flagscan.json (per included date with any post-start flag)."""
import json, os
from pathlib import Path
import numpy as np, pandas as pd, pyarrow.parquet as pq
import databento as db
os.nice(10)
HERE = Path(__file__).resolve().parent
RUNS = Path("/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e31_briefs/work/pilot/runs")
CUTOFF = pd.Timestamp("2024-03-01", tz="UTC").value
man = json.loads((RUNS / "manifest31.json").read_text())
files = sorted((f["month"], f["path"]) for f in man["files"] if f["series"] == "Z1")
dy = pd.concat([pq.read_table(p).to_pandas() for p in sorted((RUNS / "measure31").glob("*/days.parquet"))])
inc = dy[(dy.symbol == "ZM.v.0") & dy.included]
inc_set = set(inc.trade_date.astype(str))
res, tot = {}, {"files": 0, "flag_records_kept": 0, "max_ts": 0}
for month, path in files:
    st = db.DBNStore.from_file(path)
    front = {}
    for iv in st.mappings["ZM.v.0"]:
        dd = pd.date_range(iv["start_date"], pd.Timestamp(iv["end_date"]) - pd.Timedelta(days=1))
        for x in dd:
            front[x.date().isoformat()] = int(iv["symbol"])
    keep = []
    for ch in st.to_ndarray(count=2_000_000):
        tot["max_ts"] = max(tot["max_ts"], int(ch["ts_recv"].max()), int(ch["ts_event"].max()))
        a = ch["action"]; a = a.view(np.uint8) if a.dtype.kind == "S" else a
        m = ((ch["flags"].astype(np.int64) & (4 | 64 | 16)) != 0) | (a == 82)
        if m.any():
            keep.append(ch[m][["ts_recv", "instrument_id", "flags", "action"]].copy())
    tot["files"] += 1
    if not keep:
        continue
    k = np.concatenate(keep)
    t = pd.to_datetime(k["ts_recv"].astype(np.int64), utc=True).tz_convert("America/Chicago") + pd.Timedelta(hours=8)
    df = pd.DataFrame({"td": t.date.astype(str), "inst": k["instrument_id"].astype(np.int64),
                       "fl": k["flags"].astype(np.int64),
                       "R": (k["action"].view(np.uint8) if k["action"].dtype.kind == "S" else k["action"]) == 82,
                       "ts": k["ts_recv"].astype(np.int64)})
    tot["flag_records_kept"] += int((~df.R).sum())
    for td, g in df.groupby("td"):
        if td not in inc_set or front.get(td) is None:
            continue
        g = g[g.inst == front[td]]
        rs = g[g.R]
        flagged = g[~g.R & ((g.fl & (4 | 64 | 16)) != 0)]
        if len(flagged) == 0:
            continue
        r0 = rs.ts.min() if len(rs) else None
        post = flagged[flagged.ts > r0] if r0 is not None else flagged
        res[td] = {"flagged": int(len(flagged)), "post_first_R": int(len(post)),
                   "post_times_ct": [str(pd.Timestamp(x, tz="UTC").tz_convert("America/Chicago")) for x in post.ts.head(5)],
                   "n_R": int(len(rs))}
tot["max_ts_before_cutoff"] = tot["max_ts"] < CUTOFF
out = {"totals": tot, "dates_with_flags": len(res), "dates_with_post_start_flags": sorted(k for k, v in res.items() if v["post_first_R"] > 0), "per_date": res}
(HERE / "v2c_flagscan.json").write_text(json.dumps(out, indent=1))
print(tot, "dates_with_flags", len(res), "post-start", out["dates_with_post_start_flags"][:10])
