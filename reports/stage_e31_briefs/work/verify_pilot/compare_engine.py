import pandas as pd, numpy as np, json
from pathlib import Path
HERE = Path(__file__).resolve().parent
TICK = 100_000_000
import sys
dates = sys.argv[1:] or list(json.load(open(HERE / "picked_dates.json")).values())
out = {}
allm = []
for T in dates:
    m = pd.read_parquet(HERE / f"engine_rows_{T}.parquet")
    m["price_prod_fixed"] = np.round(m.price * 1e9).astype("int64")
    n = len(m)
    r = {"rows": n}
    r["valid_join_mine"] = int(m.mine_valid_join.sum())
    r["join_time_match"] = int((m.j_ns_prod == m.j_ns).sum()) if "j_ns_prod" in m else None
    r["price_match"] = int((m.mine_price == m.price_prod_fixed).sum())
    r["filled_match"] = int((m.mine_filled == m.filled).sum())
    r["filled_prod"] = int(m.filled.sum()); r["filled_mine"] = int(m.mine_filled.fillna(False).sum())
    both = m[m.filled & m.mine_filled.fillna(False)]
    r["both_filled"] = int(len(both))
    r["tfill_exact_match"] = int((both.mine_t_fill == both.t_fill_ns).sum())
    r["tfill_maxabs_ns"] = int((both.mine_t_fill - both.t_fill_ns).abs().max()) if len(both) else None
    r["through_trigger_all"] = bool((m[m.filled].trigger == "through").all())
    r["c_half_match(1e-9)"] = int((np.abs(both.mine_c_half - both.c_half) < 1e-9).sum())
    r["c_half_maxabs"] = float(np.nanmax(np.abs(both.mine_c_half - both.c_half))) if len(both) else None
    r["E10_drop_match"] = int((np.abs(both.mine_E10_drop - both.prod_E10_drop) < 1e-9).sum())
    r["E10_drop_maxabs"] = float(np.nanmax(np.abs(both.mine_E10_drop - both.prod_E10_drop))) if len(both) else None
    r["E10_nodrop_match"] = int((np.abs(both.mine_E10_nodrop - both.prod_E10_nodrop) < 1e-9).sum())
    r["E10_nodrop_maxabs"] = float(np.nanmax(np.abs(both.mine_E10_nodrop - both.prod_E10_nodrop))) if len(both) else None
    r["mine_nan_E10_drop"] = int(both.mine_E10_drop.isna().sum()); r["prod_nan_E10_drop"] = int(both.prod_E10_drop.isna().sum())
    r["mine_E10_mean"] = float(both.mine_E10_drop.mean()); r["prod_E10_mean"] = float(both.prod_E10_drop.mean())
    r["mine_invalid_in_horizon_rows"] = int((both.mine_invalid_in_horizon > 0).sum())
    r["ties_at_j"] = int(m.mine_tie_at_j.fillna(0).sum()); r["fills_at_window_end"] = int(m.mine_at_window_end.fillna(False).sum())
    r["stale_prod"] = int(m.stale.sum())
    r["instrument_id_prod"] = int(m.instrument_id.iloc[0]); r["raw_symbol_prod"] = str(m.raw_symbol.iloc[0])
    out[T] = r
    allm.append(m)
json.dump(out, open(HERE / ("engine_compare.json" if len(sys.argv)<2 else "engine_compare_" + sys.argv[1] + ".json"), "w"), indent=1)
for T, r in out.items():
    print(T, r)
A = pd.concat(allm)
mis = A[(A.mine_filled != A.filled) | (A.mine_price != A.price_prod_fixed)]
print("mismatch rows (filled or price):", len(mis))
print(mis[["trade_date","g_ns","side","mine_price","price_prod_fixed","mine_filled","filled","mine_t_fill","t_fill_ns"]].head(10).to_string())
