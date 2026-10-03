"""Inspect the saved phase-1 panel/filter pickles (read-only; prints structure only)."""
import os, pickle
os.nice(10)
import numpy as np, pandas as pd
S = os.path.expanduser("~/.cache/propexp_e12_phase1/stages/")
with open(S + "phase1_panel.pkl", "rb") as fh:
    d = pickle.load(fh)
print("panel dict keys:", list(d.keys()))
for k, v in d.items():
    if isinstance(v, pd.DataFrame):
        print(f"  {k}: DataFrame {v.shape}; index {v.index.names}")
        cols = list(v.columns)
        print("    non-z cols:", [c for c in cols if not c.startswith("z_")])
        zc = [c for c in cols if c.startswith("z_")]
        print("    z cols:", len(zc), zc[:70])
        if "trade_date" in v:
            td = v["trade_date"]
            print("    trade_date dtype", td.dtype, "min", td.min(), "max", td.max(), "nunique", td.nunique())
        if "root" in v:
            print("    roots:", sorted(map(str, v["root"].unique())))
    elif isinstance(v, (list, tuple)):
        print(f"  {k}: {type(v).__name__} len {len(v)} first {list(v)[:8]} last {list(v)[-3:]}")
    elif isinstance(v, dict):
        print(f"  {k}: dict keys {list(v.keys())[:30]}")
    else:
        print(f"  {k}: {type(v).__name__} {str(v)[:200]}")
with open(S + "phase1_filter.pkl", "rb") as fh:
    f = pickle.load(fh)
print("filter type:", type(f).__name__)
if isinstance(f, dict):
    for k, v in f.items():
        if isinstance(v, pd.DataFrame):
            print(f"  {k}: DataFrame {v.shape} cols {list(v.columns)}")
        elif isinstance(v, (list, tuple)):
            print(f"  {k}: len {len(v)} first {list(v)[:5]}")
        else:
            print(f"  {k}: {type(v).__name__} {str(v)[:150]}")
