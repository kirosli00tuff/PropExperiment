"""Step 2b: flag-bit census of the ZM.v.0 window records of one sample date (pre-start included)."""
import sys, json
from datetime import datetime
import numpy as np, pandas as pd
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from v2_engine import load_records, as_u8, CT, HERE
sd = json.loads((HERE / "sample_dates.json").read_text())
key = sys.argv[1]; d = datetime.strptime(sd["dates"][key], "%Y-%m-%d").date()
inst, r = load_records(sd["z1"][key][0], d)
fl = r["flags"].astype(np.int64); act = as_u8(r["action"])
first_R = int(np.nonzero(act == 82)[0][0])
out = {"date": str(d), "n": len(r), "first_R_idx": first_R}
for name, bit in (("LAST",128),("TOB",64),("SNAPSHOT",32),("MBP",16),("BAD_TS_RECV",8),("MAYBE_BAD_BOOK",4)):
    m = (fl & bit) != 0
    out[name] = [int(m[:first_R].sum()), int(m[first_R:].sum())]
pre = r[:first_R]
out["pre_actions"] = {chr(k): int(v) for k, v in zip(*np.unique(as_u8(pre["action"]), return_counts=True))}
out["pre_ts_recv_ct"] = [str(pd.Timestamp(int(pre["ts_recv"][0]), tz="UTC").tz_convert(CT)), str(pd.Timestamp(int(pre["ts_recv"][-1]), tz="UTC").tz_convert(CT))] if first_R else None
out["R_ts_recv_ct"] = str(pd.Timestamp(int(r["ts_recv"][first_R]), tz="UTC").tz_convert(CT))
print(json.dumps(out))
