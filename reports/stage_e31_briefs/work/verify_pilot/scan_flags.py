"""Count, per Z1 file, records with F_MAYBE_BAD_BOOK (4), F_BAD_TS_RECV (8, split snapshot / non-snapshot), by instrument.
Counts only; read-only on the raw files."""
import json, os, time
import databento as db
import numpy as np
os.nice(10)
M = json.load(open("/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e31_briefs/work/pilot/runs/manifest31.json"))
files = sorted((f["month"], f["path"]) for f in M["files"] if f["series"] == "Z1")
out = {}
for mon, path in files:
    t0 = time.time()
    st = db.DBNStore.from_file(path)
    agg = {}
    n = 0
    for df in st.to_df(price_type="fixed", pretty_ts=False, map_symbols=False, count=2_000_000):
        n += len(df)
        fl = df["flags"].to_numpy().astype("int64"); iid = df.instrument_id.to_numpy()
        snap = (fl & 32) > 0
        for name, m in (("bit4", (fl & 4) > 0), ("bit8_snapshot", ((fl & 8) > 0) & snap), ("bit8_nonsnapshot", ((fl & 8) > 0) & ~snap),
                        ("bit4_nonsnapshot", ((fl & 4) > 0) & ~snap), ("tob64", (fl & 64) > 0), ("mbp16", (fl & 16) > 0)):
            if m.any():
                u, c = np.unique(iid[m], return_counts=True)
                for a, b in zip(u, c):
                    agg.setdefault(name, {}).setdefault(int(a), 0)
                    agg[name][int(a)] += int(b)
    out[mon] = {"records": n, "agg": agg, "secs": round(time.time() - t0, 1)}
    json.dump(out, open("scan_flags.json", "w"), indent=1)
    print(mon, n, {k: sum(v.values()) for k, v in agg.items()}, out[mon]["secs"], flush=True)
