"""Extra sample rule (the first rule drew three January dates, so DST/CDT was not exercised; stated before any
summer-date result is looked at): the 10th included ZM.v.0 DAY trade date on or after 1 July of 2021, 2022, 2023."""
import pandas as pd, json
from pathlib import Path
MEAS = Path("/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e31_briefs/work/pilot/runs/measure31")
rows = []
for d in sorted(p.name for p in MEAS.iterdir() if p.is_dir()):
    x = pd.read_parquet(MEAS / d / "days.parquet"); x = x[x.symbol == "ZM.v.0"]
    rows.append(x[["trade_date", "included"]])
D = pd.concat(rows, ignore_index=True); D["td"] = D.trade_date.astype(str)
pick = {}
for y in (2021, 2022, 2023):
    inc = D[(D.td >= f"{y}-07-01") & D.included].sort_values("td")
    pick[f"summer{y}"] = inc.iloc[9].td
print(pick); json.dump(pick, open("picked_summer.json", "w"))
