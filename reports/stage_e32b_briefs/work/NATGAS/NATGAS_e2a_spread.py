"""NATGAS reader: summarise E.2a program-measured half-spread and median touch size (reports/stage_e2a_costs.json).
Reads only the program's cost report (not market data). Prints day-session (D6) and all-bucket summaries."""
import json, statistics as st, sys
P = "/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e2a_costs.json"
d = json.load(open(P))
for code in ("NG", "QG", "MNG"):
    p = d["products"][code]
    b = p["buckets"]
    rows = b if isinstance(b, list) else list(b.values())
    day = [r for r in rows if r["day_session"]]
    hs = [r["half_spread_ticks"] for r in day]
    bid = [r["median_top_size"]["bid"] for r in day]; ask = [r["median_top_size"]["ask"] for r in day]
    allhs = [r["half_spread_ticks"] for r in rows]
    print(code, "day_session_ct", p["day_session_ct"], "n_day_buckets", len(day),
          "mean_half_spread_day %.4f" % st.mean(hs), "=> mean_full_spread_day %.3f" % (2*st.mean(hs)),
          "min/max half %.4f/%.4f" % (min(hs), max(hs)),
          "touch bid min/med/max", min(bid), st.median(bid), max(bid), "ask", min(ask), st.median(ask), max(ask),
          "all-bucket full spread mean %.3f max %.3f" % (2*st.mean(allhs), 2*max(allhs)))
print("sample_dates", d["sample_dates"])
