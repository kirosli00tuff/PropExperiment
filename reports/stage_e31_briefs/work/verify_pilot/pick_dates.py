"""Sampling rule (stated before any per-date result is looked at): the 10th included ZM.v.0 DAY trade date
(days.parquet included==True, ascending) of each calendar year 2021, 2022, 2023."""
import pandas as pd, json
from pathlib import Path
MEAS = Path("/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e31_briefs/work/pilot/runs/measure31")
rows = []
for d in sorted(p.name for p in MEAS.iterdir() if p.is_dir()):
    x = pd.read_parquet(MEAS / d / "days.parquet")
    x = x[x.symbol == "ZM.v.0"]
    rows.append(x[["trade_date", "included", "instrument_id", "raw_symbol"]])
D = pd.concat(rows, ignore_index=True)
D["year"] = pd.to_datetime(D.trade_date).dt.year
pick = {}
for y in (2021, 2022, 2023):
    inc = D[(D.year == y) & D.included].sort_values("trade_date")
    pick[y] = str(inc.iloc[9].trade_date)
print(pick)
json.dump(pick, open("picked_dates.json", "w"))
