#!/usr/bin/env python3
"""VerdictVerifier-K8 item 5: rebuild each run trial's daily series from its trip list and the frozen cost tables.

Own cost model from docs/STAGE_E_DESIGN.md D8 and reports/stage_e2a_costs.json (frozen, sha f4360bb7...):
  per trip: cost = commission_rt_usd x 100 x qty cents (round turn)
                 + per side ceil(round(qty x s x cents_per_tick, 6)) cents,
  s = the fill instant's 30-minute CT bucket side_ticks (half-spread + depth term; depth 0 on every MGC and
  6C bucket, buy = sell), or the product's event_window_side_ticks (the largest s_b) when the fill instant
  lies in [release, release + 30 min) of a frozen-calendar release whose products name the root.
  net_cents = gross_cents - cost. Daily series: per trade date, sum(net_cents / cents_per_tick / contracts);
  zeros on the other window dates. Exact (Fraction) arithmetic. No bar data is read.
The MGC-on-GC check: gross_cents must be whole MGC ticks at $1.00 (multiples of 100 c, not all multiples of
1000 c), the commission must be MGC's 192 c (GC's is 432 c) and slippage dollars must be side_ticks x $1.00.
"""
from __future__ import annotations

import json
import math
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from fractions import Fraction
from pathlib import Path
from zoneinfo import ZoneInfo

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
RUN_DIR = REPO / "reports/stage_e22_confirm_k8"
COSTS = json.loads((REPO / "reports/stage_e2a_costs.json").read_text())
CAL = json.loads((REPO / "reports/stage_e2b_release_calendar.json").read_text())
CT = ZoneInfo("America/Chicago")
OUT = REPO / "reports/stage_e22_briefs/verify_k8/rebuild_trips.json"

MEMBERS = {
    "K8-flight-01 HEOD MGC": "MGC",  # Tier A (the brief's item 5 trial)
    "K8-flight-01 H30 MGC": "MGC",
    "K8-oilcad-01 6C": "6C",
}


def parse_utc(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(timezone.utc)


def side_cents(prod: dict, events: list[tuple[datetime, datetime]], ts: datetime, qty: int, cents_per_tick: int) -> tuple[int, str]:
    in_event = any(a <= ts < b for a, b in events)
    local = ts.astimezone(CT)
    minute = local.hour * 60 + local.minute
    bucket = next((b for b in prod["buckets"] if b["start_min"] <= minute < b["end_min"]), None)
    if bucket is None:
        raise ValueError(f"no bucket for {ts.isoformat()} ({local.strftime('%H:%M')} CT)")
    if in_event:
        s = prod["event_window_side_ticks"]["buy"] + bucket["depth_ticks"]["buy"]
        tag = "event"
    else:
        s = bucket["side_ticks"]["buy"]
        tag = bucket["key"]
    return math.ceil(round(qty * s * cents_per_tick, 6)), tag


def rebuild(member: str, root: str) -> dict:
    stem = f"K8_{member.replace(' ', '_')}_confirmation"
    rec = json.loads((RUN_DIR / f"{stem}.json").read_text())
    trips = json.loads((RUN_DIR / f"{stem}_trips.json").read_text())["trips"]
    prod = COSTS["products"][root]
    cents_per_tick = int(round(prod["tick_value_usd"] * 100))
    commission_c = int(round(prod["commission_rt_usd"] * 100))
    events = [(parse_utc(r["instant_utc"]), parse_utc(r["instant_utc"]) + timedelta(minutes=30)) for r in CAL["releases"] if root in r["products"]]
    mism, tags, event_sides = [], Counter(), 0
    by_day: dict[str, Fraction] = defaultdict(Fraction)
    usd_by_day: dict[str, Fraction] = defaultdict(Fraction)
    gross_mod100 = sum(1 for t in trips if Fraction(t["gross_cents"]) % 100 != 0)
    gross_mod1000 = sum(1 for t in trips if Fraction(t["gross_cents"]) % 1000 != 0)
    for t in trips:
        qty = t["contracts"]
        oc, otag = side_cents(prod, events, parse_utc(t["open_utc"]), qty, cents_per_tick)
        cc, ctag = side_cents(prod, events, parse_utc(t["close_utc"]), qty, cents_per_tick)
        event_sides += (otag == "event") + (ctag == "event")
        tags[(otag == "event", ctag == "event")] += 1
        cost = commission_c * qty + oc + cc
        gross = Fraction(t["gross_cents"])
        net = Fraction(t["net_cents"])
        if gross - cost != net:
            mism.append({"open_utc": t["open_utc"], "close_utc": t["close_utc"], "gross": str(gross), "net": str(net), "my_cost": cost, "their_cost": str(gross - net), "buckets": (otag, ctag)})
        by_day[t["trade_date"]] += net / cents_per_tick / qty
        usd_by_day[t["trade_date"]] += net / 100
    series = dict(zip(rec["series"]["dates"], rec["series"]["values"]))
    usd = dict(zip(rec["series"]["dates"], rec["daily_net_usd"]))
    series_mism = [(d, float(by_day.get(d, 0)), series[d]) for d in series if abs(float(by_day.get(d, 0)) - series[d]) > 1e-9]
    usd_mism = [(d, float(usd_by_day.get(d, 0)), usd[d]) for d in usd if abs(float(usd_by_day.get(d, 0)) - usd[d]) > 1e-9]
    off_window = [d for d in by_day if d not in series]
    first = trips[0]
    f_oc, f_ot = side_cents(prod, events, parse_utc(first["open_utc"]), first["contracts"], cents_per_tick)
    f_cc, f_ct = side_cents(prod, events, parse_utc(first["close_utc"]), first["contracts"], cents_per_tick)
    return {
        "member": member, "root": root, "n_trips": len(trips), "contracts": dict(Counter(t["contracts"] for t in trips)),
        "close_reasons": dict(Counter(t["close_reason"] for t in trips)),
        "tick_value_usd": prod["tick_value_usd"], "cents_per_tick": cents_per_tick, "commission_rt_cents": commission_c,
        "releases_naming_root": len(events), "event_window_sides": event_sides, "event_pattern_counts": {str(k): v for k, v in tags.items()},
        "trips_net_reproduced": len(trips) - len(mism), "trip_mismatches": mism[:10], "n_trip_mismatches": len(mism),
        "series_mismatches": len(series_mism), "series_mismatch_sample": series_mism[:5],
        "daily_net_usd_mismatches": len(usd_mism), "trade_dates_off_window": off_window,
        "gross_cents_not_multiple_of_100": gross_mod100, "gross_cents_not_multiple_of_1000": gross_mod1000,
        "first_trip": {"open_utc": first["open_utc"], "close_utc": first["close_utc"], "gross_cents": first["gross_cents"], "net_cents": first["net_cents"],
                        "gross_ticks_at_tick_value": float(Fraction(first["gross_cents"]) / cents_per_tick),
                        "cost_decomposition_cents": {"commission": commission_c, "open_side": f_oc, "open_bucket": f_ot, "close_side": f_cc, "close_bucket": f_ct, "total": commission_c + f_oc + f_cc}},
        "gc_contrast": {"GC_tick_value_usd": COSTS["products"]["GC"]["tick_value_usd"], "GC_commission_rt_usd": COSTS["products"]["GC"]["commission_rt_usd"]} if root == "MGC" else None,
    }


def main() -> None:
    out = {}
    for member, root in MEMBERS.items():
        res = rebuild(member, root)
        out[member] = res
        print(f"{member}: {res['trips_net_reproduced']}/{res['n_trips']} trips reproduced; series mismatches {res['series_mismatches']}; "
              f"usd mismatches {res['daily_net_usd_mismatches']}; event sides {res['event_window_sides']} (releases naming {root}: {res['releases_naming_root']}); "
              f"gross not x100: {res['gross_cents_not_multiple_of_100']}, not x1000: {res['gross_cents_not_multiple_of_1000']}; off-window dates {len(res['trade_dates_off_window'])}")
        print(f"   first trip: {json.dumps(res['first_trip'])}")
        if res["n_trip_mismatches"]:
            print(f"   first mismatches: {json.dumps(res['trip_mismatches'][:3])}")
    OUT.write_text(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
