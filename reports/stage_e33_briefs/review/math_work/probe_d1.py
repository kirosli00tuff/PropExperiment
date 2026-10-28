import sys, json, numpy as np
import hand_replay as hr
D = "2022-09-29"
inst = [hr.ct(D, "10:30:00"), hr.ct(D, "08:40:00"), hr.ct(D, "07:25:00"), hr.ct(D, "08:35:00")]
rep = hr.replay_zm(D, instants=inst)
print("iid", rep["iid"], "n_rec", rep["n_records"], "n_upd", len(rep["u_ts"]), "batch_mixed", rep["batch_mixed_ts"], "anom", rep["anomalies"])
for u in inst:
    s = rep["snaps"][u]
    b, a, two, k = hr.touch_asof(rep, u)
    print("instant", u, "valid", s["valid"], "last_flast", s["last_flast_ts"], "bid/ask", b, a, "mid", hr.mid_asof(rep, u))
    print("  bid lv", s["bid"]); print("  ask lv", s["ask"])
# minute mids 08:35..13:13 and burst scan: B(e) with sigma unknown yet -> print raw 2-min changes in ticks
mk = np.array([hr.ct(D, f"{(515+i)//60:02d}:{(515+i)%60:02d}:00") for i in range(279)])
mids = np.array([np.nan if hr.mid_asof(rep, int(u)) is None else hr.mid_asof(rep, int(u)) for u in mk])
d2 = (mids[2:] - mids[:-2]) / 1e8  # ticks (0.1 USD = 1e8 in 1e-9 units)
order = np.argsort(-np.abs(d2))[:8]
print("largest |2-min moves| (ticks) at mark index e (i = e):", [(int(o)+2, round(float(d2[o]),1)) for o in order])
print("valid marks", int(np.isfinite(mids).sum()), "of 279")
np.savez("d1_minute_mids.npz", mk=mk, mids=mids)
