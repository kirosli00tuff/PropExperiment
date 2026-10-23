import json, sys
import databento as db
import pandas as pd
M = json.load(open("/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e31_briefs/work/pilot/runs/manifest31.json"))
paths = {f["month"]: f["path"] for f in M["files"] if f["series"] == "Z1"}
json.dump({k: paths[k] for k in ("2021-01", "2022-01", "2023-01")}, open("raw_paths.json", "w"), indent=1)
for mon in ("2021-01",):
    st = db.DBNStore.from_file(paths[mon])
    md = st.metadata
    print(mon, md.start, md.end, md.schema, md.stype_in, md.stype_out, md.dataset, st.nbytes if hasattr(st,'nbytes') else '')
    mp = st.mappings
    for k, v in mp.items():
        print(k, [(x["start_date"], x["end_date"], x["symbol"]) for x in v][:6])
