"""P-1a: replicate the MES TradeDateMismatch refusal from ts_event and trade_date only (no prices);
MBT: count the store's own trade dates from S_X. Training-window stores only."""
from __future__ import annotations

import json
import os
import sys
from datetime import date
from pathlib import Path

os.nice(10)
import numpy as np
import pyarrow.compute as pc
import pyarrow.parquet as pq

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
OUT = REPO / "reports/stage_e12_briefs/gate0verifier"
sys.path.insert(0, str(REPO))
from data.group_session import assign_trade_dates, load_group_calendar, open_intervals  # harness calendar
from rules.products import product

MES = REPO / "data/processed/MES/ohlcv-1m_MES_v_0_2019-05-01_2024-02-29_confirmation.parquet"
tbl = pq.read_table(MES, columns=["ts_event", "trade_date"])
ts = tbl["ts_event"].to_numpy().astype(np.int64)
label = np.array(tbl["trade_date"].to_pylist(), dtype="datetime64[D]")
lo, hi = date.fromisoformat(str(label[0])), date.fromisoformat(str(label[-1]))
opened = open_intervals(load_group_calendar(product("MES").group), lo, hi)
got = assign_trade_dates(opened, ts, close_minute_to_previous=True)
booked = None
for a in dir(got):
    if a.startswith("_"):
        continue
    v = getattr(got, a)
    if isinstance(v, np.ndarray) and v.dtype.kind == "M" and v.shape == ts.shape:
        booked = v.astype("datetime64[D]")
        field = a
        break
assert booked is not None, [a for a in dir(got) if not a.startswith("_")]
mis = np.flatnonzero(booked != label)
rows = [{"ts_utc": str(np.datetime64(int(ts[i]), "ns")), "label": str(label[i]), "booked": str(booked[i]),
         "nat_booking": bool(np.isnat(booked[i]))} for i in mis[:10]]
mes = {"group": product("MES").group, "n_rows": int(ts.size), "first_label": str(label[0]), "last_label": str(label[-1]),
       "booked_field": field, "n_mismatch": int(mis.size), "mismatch_rows": rows,
       "lead_refusal_says": "3 rows, first label 2020-03-30 booked 2020-03-31"}
print(json.dumps(mes))

# MBT trade dates from S_X in the step 2 store (training window only)
mbt_files = sorted((REPO / "data/processed_step2/MBT").glob("*_2019-05-06_2024-02-29_step2.parquet"))
assert len(mbt_files) == 1
t2 = pq.read_table(mbt_files[0], columns=["trade_date"], filters=pc.field("trade_date") >= "2024-01-02")
td = sorted(set(t2["trade_date"].to_pylist()))
mbt = {"n_trade_dates_from_s_x": len(td), "first": td[0], "last": td[-1],
       "missing_weekdays": sorted(set(np.arange(np.datetime64("2024-01-02"), np.datetime64("2024-03-01"),
                                                 dtype="datetime64[D]").astype(str).tolist())
                                  - set(td) - {d for d in np.arange(np.datetime64("2024-01-02"), np.datetime64("2024-03-01"), dtype="datetime64[D]").astype(str).tolist() if np.datetime64(d).astype("datetime64[D]").astype(int) % 7 in (3, 4)})}
print(json.dumps(mbt))
(OUT / "mes_mbt_check.json").write_text(json.dumps({"mes": mes, "mbt": mbt}, indent=1))
