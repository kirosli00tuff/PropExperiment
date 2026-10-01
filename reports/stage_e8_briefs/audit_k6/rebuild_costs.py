"""Auditor's cost rebuild for K6-cp2-01 ZC and K6-limitcont-01 HE (Stage E.8 Task 6, Part 2 item 3).

    PYTHONPATH=. uv run python reports/stage_e8_briefs/audit_k6/rebuild_costs.py

No replay. For every trip in the runner's trip list: net = gross - commission (two sides, half the
round turn each) - slippage per fill, where a fill's slippage in ticks is the frozen table's bucket
half-spread + depth at the fill bar's CT minute (depth is 0 in every ZC and HE bucket, so the side
does not matter), or the product's largest half-spread + depth when the fill is in D8's event window
([release, release + 30 min) of a release whose products include the root) or is D9.7's forced exit
(price_limit_exit, force_event); slippage cents = ceil(round(qty x ticks x tick value cents, 6));
then summed per trade date and converted to ticks per contract (net cents / tick value cents / q_c)
and compared with series.values and daily_net_usd. The cost table and calendar are read through
screening.stage_e_frozen / stage_e_rules loaders (frozen inputs), the trips from the JSON. Gross
cannot be checked without prices. Prints counts and differences; writes nothing.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from zoneinfo import ZoneInfo

from screening.stage_e_frozen import leg_inputs, load_frozen_tables
from screening.stage_e_rules import load_release_calendar

CT = ZoneInfo("America/Chicago")
OUT = Path("reports/stage_e8_k6_screen")
NS = 1_000_000_000
EVENT_NS = 30 * 60 * NS
TRIALS = {"K6-cp2-01 ZC": ("K6_K6-cp2-01_ZC", "ZC"), "K6-limitcont-01 HE": ("K6_K6-limitcont-01_HE", "HE")}
problems: list[str] = []


def cents(v) -> Fraction:
    return Fraction(v) if isinstance(v, str) else Fraction(int(v))


def build_by_root(root: str) -> list[int]:
    raw = json.loads(Path("reports/stage_e2b_release_calendar.json").read_text())
    out = []
    for r in raw["releases"]:
        if root in r.get("products", []):
            out.append(int(datetime.fromisoformat(r["instant_utc"].replace("Z", "+00:00")).timestamp()) * NS)
    return sorted(out)


def in_event(by_root: list[int], ts_ns: int) -> bool:
    import bisect
    i = bisect.bisect_right(by_root, ts_ns) - 1
    return i >= 0 and ts_ns < by_root[i] + EVENT_NS


def main() -> None:
    tables = load_frozen_tables()
    releases = load_release_calendar()
    for member, (stem, root) in TRIALS.items():
        rec_path = OUT / f"{stem}_research.json"
        rec = json.loads(rec_path.read_text())
        trips = json.loads((OUT / f"{stem}_research_trips.json").read_text())
        sha_ok = trips["record_sha256"] == hashlib.sha256(rec_path.read_bytes()).hexdigest()
        li = leg_inputs(root, traded=True, tables=tables)
        costs = li.costs
        tv = li.tick_value_cents
        q = tables.vehicles[root].q_c
        by_root = build_by_root(root)
        print(f"== {member}: trips {len(trips['trips'])}, record_sha256 ok {sha_ok}, commission/side {costs.commission_side_cents}, "
              f"tick value {tv} cents, q_c {q}, max half-spread {costs.max_half_spread_ticks:.6f}, releases for {root} {len(by_root)}")
        per_day: dict[str, Fraction] = defaultdict(Fraction)
        mismatches = []
        event_fills = 0
        sides_by_bucket = all(b.depth_ticks["buy"] == b.depth_ticks["sell"] == 0.0 for b in costs.buckets)
        for x in trips["trips"]:
            qty = x["contracts"]
            total_cost = Fraction(0)
            for which, ts_ns, reason in (("open", x["open_ts_ns"], "strategy"), ("close", x["close_ts_ns"], x["close_reason"])):
                ts = datetime.fromtimestamp(ts_ns // NS, tz=UTC)
                ev_mine = reason == "price_limit_exit" or in_event(by_root, ts_ns)
                ev_engine = reason == "price_limit_exit" or releases.in_event_window(root, ts_ns)
                if ev_mine != ev_engine:
                    problems.append(f"{member} {x['trade_date']} {which}: my event window {ev_mine} != the loader's {ev_engine}")
                event_fills += ev_mine
                bucket = costs.bucket_at(ts)
                slip = (costs.max_half_spread_ticks + bucket.depth_ticks["buy"]) if ev_mine else bucket.side_ticks["buy"]
                slip_cents = math.ceil(round(qty * slip * float(tv), 6))
                total_cost += qty * costs.commission_side_cents + slip_cents
            net_mine = cents(x["gross_cents"]) - total_cost
            if net_mine != cents(x["net_cents"]):
                mismatches.append((x["trade_date"], str(x["gross_cents"]), str(x["net_cents"]), str(net_mine), x["close_reason"]))
            per_day[x["trade_date"]] += cents(x["net_cents"])
        print(f"   depth 0 in every bucket (side irrelevant): {sides_by_bucket}; fills in an event window or D9.7 exits: {event_fills}; "
              f"trip net mismatches: {len(mismatches)} {mismatches[:5]}")
        if mismatches:
            problems.append(f"{member}: {len(mismatches)} trip nets differ")
        day_bad = []
        for d, v, usd in zip(rec["series"]["dates"], rec["series"]["values"], rec["daily_net_usd"], strict=True):
            c = per_day.get(d, Fraction(0))
            if abs(float(c / 100) - usd) > 1e-9 * max(1.0, abs(usd)) or abs(float(c / tv / q) - v) > 1e-9 * max(1.0, abs(v)):
                day_bad.append((d, str(c), usd, v))
        print(f"   days {len(rec['series']['dates'])}, days with a trip {len(per_day)}, day mismatches (sum of trip nets vs daily_net_usd and series.values): {len(day_bad)} {day_bad[:3]}")
        if day_bad:
            problems.append(f"{member}: {len(day_bad)} day mismatches")
        # the event-window fills, listed
        listed = []
        for x in trips["trips"]:
            for which, ts_ns, reason in (("open", x["open_ts_ns"], "strategy"), ("close", x["close_ts_ns"], x["close_reason"])):
                if reason == "price_limit_exit" or in_event(by_root, ts_ns):
                    listed.append((x["trade_date"], which, datetime.fromtimestamp(ts_ns // NS, tz=UTC).astimezone(CT).strftime("%H:%M"), reason))
        print(f"   event-cost fills: {listed}")
    print("PROBLEMS:", problems if problems else "none")


if __name__ == "__main__":
    main()
