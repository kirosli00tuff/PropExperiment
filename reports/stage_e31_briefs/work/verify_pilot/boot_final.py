import json, os
from pathlib import Path
import numpy as np, pandas as pd, pyarrow.parquet as pq
os.nice(10)
RUNS = Path("/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e31_briefs/work/pilot/runs")
exp = RUNS.joinpath("expected31.txt").read_text().split()
rows = []; loops = []; inc = {}
for d in exp:
    p = pq.read_table(RUNS / f"measure31/{d}/placements.parquet", columns=["symbol", "session", "model", "filled", "c_half", "mo_10", "mo_nd_10"]).to_pandas()
    p = p[(p.symbol == "ZM.v.0") & (p.session == "DAY") & (p.model == "c")]
    z = pd.read_parquet(RUNS / f"measure31/{d}/days.parquet"); inc[d] = bool(z[z.symbol == "ZM.v.0"].included.iloc[0])
    f = p[p.filled]
    rows.append((d, len(f), float((f.mo_10 + f.c_half - 0.264).sum()), float((f.mo_nd_10 + f.c_half - 0.264).sum()), int(f.mo_10.notna().sum()), int(f.mo_nd_10.notna().sum())))
    l = pd.read_parquet(RUNS / f"measure31/{d}/loop.parquet"); l = l[(l.symbol == "ZM.v.0") & (l.model == "c")]
    loops.append(int(l.round_trips.iloc[0]) if len(l) else -1)
T = pd.DataFrame(rows, columns=["d", "nf", "sn", "sn_nd", "nv", "nv_nd"]); T["inc"] = T.d.map(inc); T["rt"] = loops
def boot(num, den, seed, nrep=2000):
    rng = np.random.default_rng(seed); n = len(num)
    idx = rng.integers(0, n, size=(nrep, n))
    r = num[idx].sum(1) / den[idx].sum(1)
    return np.percentile(r, 2.5), np.percentile(r, 97.5)
out = {}
A = T[T.inc]; 
for name, sub in (("pop764", A), ("pool816_excluded_dates_empty", T.assign(sn=np.where(T.inc, T.sn, 0.0), sn_nd=np.where(T.inc, T.sn_nd, 0.0), nv=np.where(T.inc, T.nv, 0), nv_nd=np.where(T.inc, T.nv_nd, 0)))):
    for var, (s, nvv) in {"drop": ("sn", "nv"), "nodrop": ("sn_nd", "nv_nd")}.items():
        num = sub[s].to_numpy(float); den = sub[nvv].to_numpy(float)
        est = num.sum() / den.sum()
        res = {f"seed{sd}": [round(float(x), 5) for x in boot(num, den, sd)] for sd in (31, 7, 101, 20260, 555)}
        out[f"{name}/{var}"] = {"est": round(float(est), 6), "n": int(den.sum()), **res}
        # fee 0.528: subtract another 0.264 per valid fill
        num2 = num - 0.264 * den
        out[f"{name}/{var}/fee0.528"] = {"est": round(float(num2.sum() / den.sum()), 6), **{f"seed{sd}": [round(float(x), 5) for x in boot(num2, den, sd)] for sd in (31, 7)}}
# K3
rt = A.rt.to_numpy(float)
k3 = {"mean": float(rt.mean()), "n_dates": int(len(rt)), "min": float(rt.min())}
for name, v in (("pop764", rt), ("pool816", np.where(T.inc, T.rt, 0).astype(float))):
    rng = np.random.default_rng(31); idx = rng.integers(0, len(v), size=(2000, len(v))); m = v[idx].mean(1)
    k3[name + "_ci_seed31"] = [round(float(np.percentile(m, 2.5)), 3), round(float(np.percentile(m, 97.5)), 3)]
out["K3"] = k3
Path("boot_final.json").write_text(json.dumps(out, indent=1))
for k, v in out.items(): print(k, v)

# K3 as a ratio of sums over the 816-date pool (excluded dates weight 0)
num = np.where(T.inc, T.rt, 0).astype(float); den = T.inc.to_numpy(float)
rng = np.random.default_rng(31); idx = rng.integers(0, len(num), size=(2000, len(num)))
r = num[idx].sum(1) / den[idx].sum(1)
print("K3 ratio-of-sums over 816-date pool, seed31:", [round(float(x), 5) for x in (np.percentile(r, 2.5), np.percentile(r, 97.5))])
out["K3"]["pool816_ratio_of_sums_ci_seed31"] = [round(float(x), 5) for x in (np.percentile(r, 2.5), np.percentile(r, 97.5))]
Path("boot_final.json").write_text(json.dumps(out, indent=1))
