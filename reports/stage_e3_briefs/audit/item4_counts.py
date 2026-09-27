"""Auditor Task 6 item 4: expected trade counts of the event members vs the records' n_trips. Counts only."""
import sys, json, glob; sys.path.insert(0, ".")
from datetime import date
from data.group_session import load_group_calendar
from strategy.members.k2._releases import TREASURY_AUCTIONS, FOMC_STATEMENT_DATES, ISM_SERVICES_DATES
from strategy.members.k2._month_end import MONTH_END
cal = load_group_calendar("rates")
rec = json.load(open("reports/stage_e3_k2_screen/K2_K2-cp1-01_ZN_research.json"))
window = set(rec["series"]["dates"]); excl = rec["window_dates"]["excluded"]
blackout = set(excl["roll_blackout_any_leg"]) | set(excl["unseen_roll_UR-1"])
lo, hi = "2025-04-01", "2026-06-19"
halt = lambda d: cal.early_halt_ct(date.fromisoformat(d)) is not None
TEN = {"ZT": "2Y", "ZF": "5Y", "ZN": "10Y", "TN": "10Y", "ZB": "30Y", "UB": "30Y"}
def summarize(member, root, events):
    ev = sorted(e for e in events if lo <= e <= hi)
    in_bl = [e for e in ev if e in blackout]; halts = [e for e in ev if e not in blackout and halt(e)]
    expected = [e for e in ev if e in window and not halt(e)]
    r = json.load(open(f"reports/stage_e3_k2_screen/K2_{member}_{root}_research.json"))
    n = r["screen"]["n_trips"]; refused = r["engine"]["counters"].get("engine_not_a_window_date", 0)
    traded = [d for d, v in zip(r["series"]["dates"], r["series"]["values"]) if v != 0.0]
    missing = [e for e in expected if e not in traded]; extra = [d for d in traded if d not in ev]
    print(f"{member:14s} {root}: events {len(ev)}, blackout {len(in_bl)} {in_bl if len(in_bl) < 6 else ''}, halt {halts}, expected {len(expected)}, n_trips {n}, refused_not_window {refused}, unexplained-missing {missing}, traded-not-event {extra}")
for root in ("ZT", "ZF", "ZN", "TN", "ZB", "UB"):
    ev = [d for d, t, _ in TREASURY_AUCTIONS if t == TEN[root]]
    summarize("K2-aucpre-01", root, ev); summarize("K2-aucpost-01", root, ev)
for root in ("ZT", "ZF", "ZN", "TN", "ZB", "UB"): summarize("K2-fomcpost-01", root, list(FOMC_STATEMENT_DATES))
for root in ("ZN", "ZB"): summarize("K2-predrift-01", root, list(ISM_SERVICES_DATES))
me = [d for _, a, b in MONTH_END for d in (a, b)]
for root in ("ZT", "ZF", "ZN", "TN", "ZB", "UB"): summarize("K2-monthend-01", root, me)
print("ports: n_trips of 299 window dates, with counters")
for m in ("K2-cp1-01", "K2-cp2-01", "K2-cp3-01"):
    for root in ("ZT", "ZF", "ZN", "TN", "ZB", "UB"):
        r = json.load(open(f"reports/stage_e3_k2_screen/K2_{m}_{root}_research.json"))
        c = r["engine"]["counters"]; tr = r["trade_rate"]
        print(f"  {m} {root}: n_trips {r['screen']['n_trips']}, refused_not_window {c.get('engine_not_a_window_date',0)}, mll {c.get('mll_liquidation',0)}, forced {c.get('forced_flatten',0)}, deferrals {c.get('fill_guard_deferral',0)}, mean hold {tr['mean_hold_minutes']:.1f}, min hold {tr['min_hold_minutes']}, max entries/day {tr['max_entries_per_product_day']}")
