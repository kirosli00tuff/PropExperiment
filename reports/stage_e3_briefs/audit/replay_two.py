"""Auditor Task 6 item 3 (determinism half): replay K2-cp1-01 ZN and K2-aucpost-01 ZN through the
runner's own functions, compare with the recorded series, and dump the fills and trips. Prints counts."""
import sys, json, os; sys.path.insert(0, ".")
from collections import Counter
from datetime import datetime, UTC
from pathlib import Path
from fractions import Fraction
from zoneinfo import ZoneInfo
from screening import harness_freeze
from screening.stage_e_freeze import load_cluster_freeze, verify_cluster_code, resolve_member
from screening.stage_e_runner import (_legs_inputs, _load_frames, _run_member, extract_trips, _series,
                                      RESEARCH_WINDOW, RESEARCH)
from screening.stage_e_align import member_window
from screening.stage_e_rules import load_release_calendar
from screening.stage_e_engine import Fill, AccountStart, DayClose
CT = ZoneInfo("America/Chicago")
HARNESS = "cf939270f0a00be74aa29a43f0c7de964256411a9cdcebc36f22fd3bdc021a45"
OUT = Path("reports/stage_e3_briefs/audit")
def ct(ns): return datetime.fromtimestamp(ns / 1e9, tz=UTC).astimezone(CT).isoformat(timespec="minutes")
def num(x): return float(x) if isinstance(x, Fraction) else x
print("preflight", harness_freeze.preflight(HARNESS)[:16])
freeze = load_cluster_freeze("K2"); verify_cluster_code(freeze); print("freeze", freeze.sha256[:16], len(freeze.members))
releases = load_release_calendar()
for label in ("K2-cp1-01 ZN", "K2-aucpost-01 ZN"):
    decl, factory = resolve_member(freeze, label, None)
    legs = decl.legs; inputs = _legs_inputs(legs)
    frames, extra = _load_frames(legs, inputs, RESEARCH_WINDOW, Path("data/processed"), Path("data/processed_step2"))
    mw = member_window(frames, RESEARCH)
    member = factory()
    result = _run_member(member, legs, inputs, frames, mw.dates, mw.blackout_union, releases)
    trips = extract_trips(result)
    series = _series(label, legs, inputs, trips, mw.dates)
    rec = json.load(open(f"reports/stage_e3_k2_screen/K2_{label.replace(" ", "_")}_research.json"))
    same_vals = list(series.values) == rec["series"]["values"]
    same_dates = [d.isoformat() for d in series.dates] == rec["series"]["dates"]
    same_n = series.n_trips == rec["series"]["n_trips"]
    same_counters = dict(result.counters) == rec["engine"]["counters"]
    same_bars = {r: f.sha256 for r, f in frames.items()} == {r: v["sha256"] for r, v in rec["bars"].items()}
    print(f"{label}: values equal {same_vals}, dates equal {same_dates}, n_trips {series.n_trips} equal {same_n}, counters equal {same_counters}, bar sha equal {same_bars}, fills {len(result.events(Fill))}, accounts {result.accounts_started}")
    fills = []
    for f in result.events(Fill):
        fills.append({"fill_ct": ct(f.fill_ts_ns), "decision_ct": ct(f.decision_ts_ns), "fill_ts_ns": f.fill_ts_ns,
                      "reason": f.reason, "side": f.side, "qty": f.qty, "price": f.price,
                      "commission_cents": f.commission_cents, "slippage_cents": f.slippage_cents,
                      "slippage_ticks": f.slippage_ticks, "gross_realized_cents": num(f.gross_realized_cents),
                      "position_after": f.position_after, "trade_date": str(f.trade_date),
                      "event_window": f.event_window, "opening": f.opening, "account_index": f.account_index,
                      "minutes_after_decision": f.minutes_after_decision, "order_type": f.order_type,
                      "locked_bars_waited": f.locked_bars_waited, "closure_gap": f.closure_gap})
    # my own pairing flat -> flat
    my_trips = []; cur = None
    for fl in fills:
        if cur is None:
            cur = {"entry_ct": fl["fill_ct"], "entry_decision_ct": fl["decision_ct"], "side": fl["side"], "qty": fl["qty"],
                   "entry_price": fl["price"], "entry_event_window": fl["event_window"], "fills": []}
        cur["fills"].append(fl)
        if fl["position_after"] == 0:
            cur.update(exit_ct=fl["fill_ct"], exit_decision_ct=fl["decision_ct"], exit_price=fl["price"], exit_reason=fl["reason"],
                       exit_event_window=fl["event_window"], trade_date=fl["trade_date"],
                       gross_cents=sum(x["gross_realized_cents"] for x in cur["fills"]),
                       commission_cents=sum(x["commission_cents"] for x in cur["fills"]),
                       slippage_cents=sum(x["slippage_cents"] for x in cur["fills"]))
            cur["net_cents"] = cur["gross_cents"] - cur["commission_cents"] - cur["slippage_cents"]
            my_trips.append(cur); cur = None
    runner_trips = [{"trade_date": str(t.trade_date), "net_cents": num(t.net_cents), "contracts": t.contracts,
                     "close_reason": t.close_reason, "open_ct": ct(t.open_ts_ns), "close_ct": ct(t.close_ts_ns)} for t in trips]
    same_trips = len(my_trips) == len(runner_trips) and all(abs(a["net_cents"] - b["net_cents"]) < 1e-9 and a["trade_date"] == b["trade_date"] for a, b in zip(my_trips, runner_trips))
    starts = [{"ct": ct(e.ts_ns), "trade_date": str(e.trade_date), "account_index": e.account_index, "balance_cents": num(e.balance_cents)} for e in result.events(AccountStart)]
    breaches = [{"trade_date": str(e.trade_date), "account_index": e.account_index, "status_after": e.status_after, "breach": str(e.breach)} for e in result.events(DayClose) if e.breach is not None or e.status_after != "active"]
    print(f"  my trips {len(my_trips)} == runner trips {same_trips}; exit reasons {Counter(t['exit_reason'] for t in my_trips)}; event-window fills {sum(f['event_window'] for f in fills)}; deferred fills {sum(f['minutes_after_decision'] > 1 for f in fills)}; account starts {starts}; breaches {breaches[:4]}")
    json.dump({"member": label, "replayed_series_equals_record": same_vals and same_dates and same_n,
               "counters": dict(result.counters), "bars": {r: {"sha256": f.sha256, "rows": len(f.frame)} for r, f in frames.items()},
               "window": {"n": len(mw.dates), "first": str(mw.dates[0]), "last": str(mw.dates[-1])},
               "trips": my_trips, "runner_trips": runner_trips, "account_starts": starts, "day_close_breaches": breaches,
               "series_values": list(series.values), "series_dates": [d.isoformat() for d in series.dates]},
              open(OUT / f"trips_{label.replace(' ', '_')}.json", "w"), indent=1)
print("done")
