"""Inspect out['panel'] (Panel object) and the filter dict (read-only; structure only)."""
import os, pickle
os.nice(10)
import numpy as np, pandas as pd
S = os.path.expanduser("~/.cache/propexp_e12_phase1/stages/")
d = pickle.load(open(S + "phase1_panel.pkl", "rb"))
out = d["out"]
p = out["panel"]
print("Panel type:", type(p).__name__, "attrs:", [a for a in dir(p) if not a.startswith("_")])
for a in ("horizons", "signal_names", "feature_cols", "vehicles", "roots"):
    if hasattr(p, a):
        v = getattr(p, a); print(a, len(v), list(v)[:12], "...", list(v)[-6:])
fr = p.frame
print("frame", fr.shape, "index", fr.index.names, type(fr.index).__name__)
cols = list(fr.columns)
print("non-z/non-feature cols:", [c for c in cols if not c.startswith("z_") and c not in set(p.feature_cols)])
print("feature cols not z_:", [c for c in p.feature_cols if not c.startswith("z_")])
print("z cols not in feature_cols:", [c for c in cols if c.startswith("z_") and c not in set(p.feature_cols)])
td = fr["trade_date"]; print("trade_date dtype", td.dtype, "min", td.min(), "max", td.max(), "nunique", td.nunique())
print("roots:", sorted(map(str, fr["root"].unique())), "n", fr["root"].nunique())
cal = out["calendar"]; print("calendar len", len(cal), "first", cal[0], "last", cal[-1], type(cal[0]).__name__)
print("vehicles", out["vehicles"]); print("covered", len(out["covered"]), "uncovered", out["uncovered"])
print("created_pdt", out["created_pdt"], "input_fp", out["input_fingerprint"][:16])
print("inputs keys", list(out["inputs"].keys()))
print("report keys", list(out["report"].keys()))
for h in p.horizons:
    print(h, "ok rows", int(fr[f"ok_{h}"].sum()))
f = pickle.load(open(S + "phase1_filter.pkl", "rb"))
fo = f["out"]; print("filter out keys", list(fo.keys()))
for k, v in fo.items():
    if isinstance(v, pd.DataFrame): print(" ", k, v.shape, list(v.columns))
    elif isinstance(v, (list, tuple)): print(" ", k, "len", len(v), list(v)[:4])
    else: print(" ", k, type(v).__name__, str(v)[:120])
print("dtypes:", fr.dtypes.value_counts().to_dict())
