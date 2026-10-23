import pandas as pd, numpy as np
from pathlib import Path
MEAS = Path("/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e31_briefs/work/pilot/runs/measure31")
exp = MEAS.parent.joinpath("expected31.txt").read_text().split()
D = pd.concat([pd.read_parquet(MEAS/d/"days.parquet") for d in exp], ignore_index=True)
Z = D[D.symbol=="ZM.v.0"].copy(); Z["td"]=pd.to_datetime(Z.trade_date)
Z = Z.sort_values("td").reset_index(drop=True)
chg = (Z.instrument_id != Z.instrument_id.shift(1)); chg.iloc[0]=False
nxt = chg.shift(1, fill_value=False)
print("change dates", int(chg.sum()), "next-day dates", int(nxt.sum()))
print("next-day dates not included:", int((nxt & ~Z.included).sum()), "; by reason:", Z[nxt & ~Z.included].reason.value_counts().to_dict())
print("next-day dates that are included:", Z[nxt & Z.included].td.dt.date.astype(str).tolist())
print("change dates included:", int((chg & Z.included).sum()))
# included set derivation
print("included total", int(Z.included.sum()))
inc = Z[Z.included]
print("bad_flag_records>0 on included days:", int((inc.bad_flag_records>0).sum()), "of", len(inc), "; quantiles", inc.bad_flag_records.quantile([.5,.9,1]).tolist())
print("crossed_moments>0 on included:", int((inc.crossed_moments>0).sum()), "; max", int(inc.crossed_moments.max()), " inversions>0", int((inc.inversions>0).sum()))
print(inc[inc.bad_flag_records>0][["trade_date","bad_flag_records","crossed_moments","n_records","placements_day","placements_on"]].head(8).to_string())
print("placements_day distribution", inc.placements_day.value_counts().to_dict())
print("placements_on distribution (top)", inc.placements_on.value_counts().head(6).to_dict())
print("excluded rows reasons for bad flags", Z[~Z.included].bad_flag_records.describe()[["count","mean","max"]].to_dict())
