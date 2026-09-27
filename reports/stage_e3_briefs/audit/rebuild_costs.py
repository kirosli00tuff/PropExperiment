"""Auditor Task 6 item 3 (rebuild half): from the dumped trips, rebuild each day's net ticks per
contract in the auditor's OWN code from the frozen cost table (reports/stage_e2a_costs.json read
directly), the release calendar JSON (D8 event window) and rules.products' commission and tick value.
Compares per-fill commission and slippage with the engine's, and the daily series with the record
to 1e-9 relative. Also checks every trip's fill minutes against the rule (item 4b). Prints counts."""
import sys, json, math; sys.path.insert(0, ".")
from collections import Counter
from datetime import datetime, UTC
from decimal import Decimal
from fractions import Fraction
from zoneinfo import ZoneInfo

CT = ZoneInfo("America/Chicago")
NS_MIN = 60_000_000_000
EVENT_NS = 30 * NS_MIN
costs = json.load(open("reports/stage_e2a_costs.json"))["products"]["ZN"]
cal = json.load(open("reports/stage_e2b_release_calendar.json"))
zn_releases = sorted({int(datetime.fromisoformat(e["instant_utc"].replace("Z", "+00:00")).timestamp()) * 1_000_000_000
                      for e in cal["releases"] if "ZN" in e["products"]})
TICK = Decimal(costs["vendor_tick"])  # 0.015625
TICK_VALUE_CENTS = Fraction(Decimal(str(costs["tick_value_usd"])) * 100)  # 1562.5
COMMISSION_SIDE_CENTS = int(round(costs["commission_rt_usd"] * 100)) // 2  # 131
buckets = [(b["start_min"], b["end_min"], b["half_spread_ticks"], b["depth_ticks"], b["fallback"]) for b in costs["buckets"]]
assert not any(b[4] for b in buckets), "fallback bucket present: event rule for fallback not encoded"
MAX_S_B = max(b[2] for b in buckets)
print("ZN: commission/side", COMMISSION_SIDE_CENTS, "tick value cents", TICK_VALUE_CENTS, "buckets", len(buckets), "max s_b", MAX_S_B, "releases concerning ZN", len(zn_releases))


def in_event_window(ts_ns: int) -> bool:
    import bisect
    i = bisect.bisect_right(zn_releases, ts_ns) - 1
    return i >= 0 and ts_ns < zn_releases[i] + EVENT_NS


def bucket_of(ts_ns: int):
    local = datetime.fromtimestamp(ts_ns / 1e9, tz=UTC).astimezone(CT)
    minute = local.hour * 60 + local.minute
    found = [b for b in buckets if b[0] <= minute < b[1]]
    assert len(found) == 1, (local, minute)
    return found[0]


def slippage_cents(qty: int, ts_ns: int, side: str) -> tuple[int, float, bool]:
    start, end, s_b, depth, _ = bucket_of(ts_ns)
    event = in_event_window(ts_ns)
    slip = (MAX_S_B + depth[side]) if event else (s_b + depth[side])
    return math.ceil(round(qty * slip * float(TICK_VALUE_CENTS), 6)), slip, event


def price_ticks(price: float) -> Fraction:
    return Fraction(Decimal(repr(price)) / TICK)


DEC = {"K2-cp1-01 ZN": ("13:29", "13:58"), "K2-aucpost-01 ZN": ("12:04", "15:04")}  # rule decision bars
RULE = {  # expected fill minutes (CT) per member: entry, exit; documented deviations handled below
    "K2-cp1-01 ZN": ("13:30", "13:59"),
    "K2-aucpost-01 ZN": ("12:05", "15:05"),  # every 10-year auction is a 13:00 ET close (T_a 12:00 CT)
}
verdict = {}
for label in RULE:
    d = json.load(open(f"reports/stage_e3_briefs/audit/trips_{label.replace(' ', '_')}.json"))
    rec = json.load(open(f"reports/stage_e3_k2_screen/K2_{label.replace(' ', '_')}_research.json"))
    assert d["replayed_series_equals_record"], "determinism failed; stop"
    fill_mismatch = []; gross_mismatch = []; ev_mismatch = []
    by_day = {}
    for t in d["trips"]:
        qty = t["qty"]; sign = 1 if t["side"] == "buy" else -1
        # gross from prices, in cents, exact
        entry_ticks = price_ticks(t["entry_price"])
        gross = Fraction(0)
        commission = 0; slippage = 0
        for f in t["fills"]:
            c = qty_f = f["qty"]
            commission += c * COMMISSION_SIDE_CENTS
            s_cents, s_ticks, event = slippage_cents(c, f["fill_ts_ns"], f["side"])
            slippage += s_cents
            if s_cents != f["slippage_cents"] or abs(s_ticks - f["slippage_ticks"]) > 1e-12 or c * COMMISSION_SIDE_CENTS != f["commission_cents"]:
                fill_mismatch.append((f["fill_ct"], s_cents, f["slippage_cents"], s_ticks, f["slippage_ticks"]))
            if event != f["event_window"]:
                ev_mismatch.append((f["fill_ct"], event, f["event_window"]))
            if not f["opening"]:
                gross += sign * (price_ticks(f["price"]) - entry_ticks) * c * TICK_VALUE_CENTS
        if abs(float(gross) - t["gross_cents"]) > 1e-6:
            gross_mismatch.append((t["entry_ct"], float(gross), t["gross_cents"]))
        net_cents = gross - commission - slippage
        net_usd = float(net_cents / 100)
        by_day[t["trade_date"]] = by_day.get(t["trade_date"], 0.0) + net_usd / (qty * float(TICK_VALUE_CENTS) / 100)
    mine = [by_day.get(day, 0.0) for day in rec["series"]["dates"]]
    theirs = rec["series"]["values"]
    worst = max(abs(a - b) / max(1.0, abs(a), abs(b)) for a, b in zip(mine, theirs))
    days_off = sum(1 for a, b in zip(mine, theirs) if abs(a - b) > 1e-9 * max(1.0, abs(a), abs(b)))
    # item 4b: fill minutes
    entry_exp, exit_exp = RULE[label]
    dev = Counter(); odd = []
    for t in d["trips"]:
        e_min, x_min = t["entry_ct"][11:16], t["exit_ct"][11:16]
        e_ok = e_min == entry_exp
        x_ok = x_min == exit_exp
        if not e_ok:
            fl = t["fills"][0]
            if fl["minutes_after_decision"] > 1: dev["entry deferred (D9.5a guard or missing bar)"] += 1
            else: odd.append(("entry", t["entry_ct"], t["entry_decision_ct"]))
        if not x_ok:
            if t["exit_reason"] == "mll_liquidation": dev["exit by mll_liquidation"] += 1
            elif t["exit_reason"] != "strategy": dev[f"exit by {t['exit_reason']}"] += 1
            elif t["fills"][-1]["minutes_after_decision"] > 1 or t["exit_decision_ct"][11:16] != DEC[label][1]:
                dev["exit on a later bar (missing bar or D9.5a)"] += 1
            else: odd.append(("exit", t["exit_ct"], t["exit_decision_ct"], t["exit_reason"]))
    ok = not fill_mismatch and not gross_mismatch and not ev_mismatch and days_off == 0
    verdict[label] = "VERIFIED" if ok and not odd else ("DISCREPANCY" if not ok else "VERIFIED WITH NOTES")
    print(f"{label}: trips {len(d['trips'])}, fills {sum(len(t['fills']) for t in d['trips'])}, per-fill cost mismatches {len(fill_mismatch)}, gross mismatches {len(gross_mismatch)}, event-window flag mismatches {len(ev_mismatch)}, event-window fills {sum(f['event_window'] for t in d['trips'] for f in t['fills'])}, days off (>1e-9) {days_off}, worst rel diff {worst:.3e}; fill-minute deviations {dict(dev)}; unexplained {odd[:6]}; verdict {verdict[label]}")
    if fill_mismatch[:3]: print("   first cost mismatches", fill_mismatch[:3])
    reasons = Counter(t["exit_reason"] for t in d["trips"]); holds = [ (datetime.fromisoformat(t["exit_ct"]) - datetime.fromisoformat(t["entry_ct"])).total_seconds() / 60 for t in d["trips"]]
    print(f"   exit reasons {dict(reasons)}; hold min/mean {min(holds):.0f}/{sum(holds)/len(holds):.1f}; account starts {len(d['account_starts'])}; day-close breaches {d['day_close_breaches']}")
    liq = [t for t in d["trips"] if t["exit_reason"] == "mll_liquidation"]
    for t in liq: print(f"   mll_liquidation trip: entry {t['entry_ct']} {t['side']} @ {t['entry_price']}, exit {t['exit_ct']} @ {t['exit_price']}, net cents {t['net_cents']}")
print("verdicts", verdict)
