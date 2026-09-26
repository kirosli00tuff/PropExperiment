"""Build the frozen Stage E cost table and its report (design D8; Stage E.2a Task 8).

    nice -n 10 uv run python -m sim.calibrate_costs build

Reads the raw calibration lines (``sim.calibrate_costs`` scratch JSONL), applies the D8 rule
(``sim.cost_rule``) with the commission and tick tables of ``sim.cost_inputs`` and, when it
exists, q_c per contract from reports/stage_e2a_vehicle_sizes.json (Task 9), and writes
reports/stage_e2a_costs.json (the frozen table ``sim.product_costs`` loads) and
reports/stage_e2a_costs.md. Without the sizes file the depth term is recorded as PENDING and the
table is provisional (the loader refuses it unless asked to accept a provisional table).
"""

from __future__ import annotations

import json
from datetime import UTC, date, datetime, time
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from zoneinfo import ZoneInfo

from data.config import REPO_ROOT
from data.group_session import load_group_calendar
from sim.calibrate_costs import bucket_pieces, done_products, sha256_file
from sim.cost_inputs import (
    BUCKET_MINUTES,
    FEE_INCREASE_2026_10_01_RT,
    MIN_DATES_WITH_QUOTES,
    SAMPLE_DATES,
    TickSpec,
    load_commissions,
    load_ticks,
)
from sim.cost_rule import (
    READINGS,
    SIDES,
    BucketCost,
    ProductRule,
    UncalibratableError,
    aggregate,
    apply_rule,
    day_session_buckets,
    headline,
)

OUT_JSON = REPO_ROOT / "reports" / "stage_e2a_costs.json"
OUT_MD = REPO_ROOT / "reports" / "stage_e2a_costs.md"
SIZES_JSON = REPO_ROOT / "reports" / "stage_e2a_vehicle_sizes.json"
MES_D1_TABLE = REPO_ROOT / "sim" / "slippage_calibration.json"
PDT = ZoneInfo("America/Vancouver")
NS = 1_000_000_000
MES_COMMISSION_RT = Decimal("1.22")  # sim/costs.py MES_ROUND_TURN_COMMISSION_USD
MES_TICK_VALUE = Decimal("1.25")

LIMITATIONS = (
    "tbbo was not bought (user decisions U4 and U8), so D8's tbbo cross-check (trade-weighted "
    "effective half-spread beside s_b) does not exist; nothing replaces it.",
    "All five sample dates are Wednesdays, EIA crude-inventory release days, so energy's 09:30 "
    "CT bucket includes the release on every date (recorded, not corrected; D8 known "
    "limitation).",
    "Five dates is thin for a time-of-day table; no latency or adverse-selection model (as for "
    "MES). Calibrated on 2025-26 books, the table understates costs in thinner earlier years "
    "(D8 early-era bias: any member passing confirmation gets a period-appropriate re-check).",
    "The event-window cost needs E.2b's release calendar; the table gives the per-side value.",
)


def f(x: Fraction | Decimal | None, nd: int | None = None) -> float | None:
    if x is None:
        return None
    value = float(x)
    return round(value, nd) if nd is not None else value


def hhmm(minute: int) -> str:
    minute %= 1440
    return f"{minute // 60:02d}:{minute % 60:02d}"


def day_session_of(product: str, group: str) -> tuple[time, time]:
    """Design D6's (O, C) for the product from its group calendar's SessionSpec."""
    cal = load_group_calendar(group)
    table = cal.spec_for(SAMPLE_DATES[-1]).day_session_ct
    if product in table:
        return table[product]
    if "*" in table:
        return table["*"]
    sub = dict(getattr(cal, "subgroup_of_product", {}) or {}).get(product)
    if sub is None and len(set(table.values())) == 1:  # one (O, C) for the group (as
        return next(iter(table.values()))  # GroupCalendar.day_session_close reads it)
    if sub is None or sub not in table:
        raise KeyError(f"{group} SessionSpec has no day session for {product}")
    return table[sub]


def load_sizes(path: Path = SIZES_JSON) -> dict[str, int] | None:
    """q_c per contract from Task 9's file, or None when it does not exist yet."""
    if not path.exists():
        return None
    raw = json.loads(path.read_text())
    rows = raw.get("contracts", raw.get("products", raw)) if isinstance(raw, dict) else raw
    out: dict[str, int] = {}
    items = rows.items() if isinstance(rows, dict) else ((r.get("contract") or r.get("product")
                                                          or r.get("root"), r) for r in rows)
    for root, row in items:
        if not isinstance(row, dict) or "q_c" not in row:
            continue
        if row.get("status", "computed") != "computed" or row["q_c"] is None:
            raise ValueError(f"{path}: {root} is {row.get('status')!r} with q_c {row['q_c']!r}")
        q_c = row["q_c"]
        if isinstance(q_c, bool) or not isinstance(q_c, int) or q_c < 1:
            raise ValueError(f"{path}: {root} q_c {q_c!r} is not a positive integer")
        out[str(root)] = q_c
    if not out:
        raise ValueError(f"{path} has no q_c entries")
    return out


# ------------------------------------------------------------------ table ----
def _bucket_json(c: BucketCost, tick_value: Decimal, day_keys: set[str]) -> dict:
    s = c.stats
    tv = Fraction(tick_value)
    return {
        "key": s.key, "start": hhmm(s.start_min), "end": hhmm(s.end_min),
        "start_min": s.start_min, "end_min": s.end_min, "day_session": s.key in day_keys,
        "dates_present": s.dates_present, "dates_with_quotes": s.dates_with_quotes,
        "fallback": c.fallback,
        "half_spread_ticks": f(s.half_spread),
        "half_spread_ticks_equal_date_weights": f(s.half_spread_equal_dates),
        "valid_seconds": s.valid_ns / NS,
        "per_date": {d: {"valid_seconds": v["valid_ns"] / NS,
                         "half_spread_ticks": (v["spread_tick_ns"] / (2 * v["valid_ns"])
                                               if v["valid_ns"] else None)}
                     for d, v in s.per_date.items()},
        "median_top_size": dict(s.median_size),
        "depth_ticks": {side: f(c.depth[side]) for side in SIDES},
        "side_ticks": {side: f(c.side_ticks[side]) for side in SIDES},
        "side_slippage_usd": {side: f(c.side_ticks[side] * tv) for side in SIDES},
        "round_turn_ticks": f(c.round_turn_ticks),
        "round_turn_usd": f(c.round_turn_ticks * tv),
        "dropped": {k: {"records": s.dropped_records[k], "seconds": s.dropped_ns[k] / NS}
                    for k in ("empty", "locked", "crossed")},
        "unknown_seconds": s.unknown_ns / NS,
    }


def product_entry(raw: dict, tick: TickSpec, commission: Decimal, q_c: int | None,
                  session: tuple[time, time], calendar_at_build: dict | None = None) -> dict:
    """One contract's frozen table entry (pure given its inputs)."""
    calendar_at_build = calendar_at_build or {}
    root = raw["product"]
    if raw["vendor_tick_fixed"] != tick.vendor_tick_fixed:
        raise ValueError(f"{root}: raw vendor tick {raw['vendor_tick_fixed']} != "
                         f"{tick.vendor_tick_fixed}")
    min_spread = min(d["min_spread_ticks"] for d in raw["dates"].values()
                     if d["min_spread_ticks"] is not None)
    checked = sum(int(d["stats"].get("valid_prices_checked", 0)) for d in raw["dates"].values())
    off10 = sum(int(d["stats"].get("valid_prices_off_10x_grid", 0))
                for d in raw["dates"].values())
    rule = ProductRule(commission, tick.tick_value_usd, q_c)
    stats = aggregate(raw["dates"])
    base = {
        "product": root, "group": raw["group"], "tick_size": str(tick.tick_size),
        "tick_size_source": f"reports/stage_e0_liquidity.json tick_size {tick.source_text!r}",
        "tick_value_usd": f(tick.tick_value_usd), "vendor_price_factor": tick.vendor_factor,
        "vendor_tick": str(tick.vendor_tick),
        "vendor_tick_check": {
            "vendor_price_factor": tick.vendor_factor, "vendor_tick": str(tick.vendor_tick),
            "valid_bid_ask_prices_checked": checked,
            "prices_off_vendor_tick_grid": 0,  # any would have refused the calibration
            "prices_off_10x_vendor_tick_grid": off10,
            "min_quoted_spread_ticks": min_spread,
            "passed": min_spread == 1 and off10 > 0 and checked > 0},
        "commission_rt_usd": f(commission), "commission_rt_ticks": f(rule.commission_ticks),
        "commission_source": ("reports/stage_e0_topstep_facts.json F3.7" + (
            f" + F3.6 (+${FEE_INCREASE_2026_10_01_RT[root]} round turn from the 2026-10-01 "
            "trading day, applied now per D8)" if root in FEE_INCREASE_2026_10_01_RT else "")),
        "q_c": q_c, "depth_term": "applied" if q_c is not None else "pending",
        "day_session_ct": {"open": session[0].strftime("%H:%M"),
                           "close": session[1].strftime("%H:%M")},
        "files": raw["files"],
        "date_stats": {d: {**v["stats"], "first_ts_recv_utc": v["first_ts_recv_utc"],
                           "knowledge_end_utc": v["knowledge_end_utc"],
                           "instruments": v["instruments"],
                           "instrument_switches": v["instrument_switches"],
                           "min_spread_ticks": v["min_spread_ticks"]}
                       for d, v in raw["dates"].items()},
        "calendar_sha256": raw["calendar_sha256"], "code_sha256": raw["code_sha256"],
        "calendar_sha256_at_build": calendar_at_build.get(raw["group"], raw["calendar_sha256"]),
    }
    try:
        costs, event = apply_rule(stats, rule)
    except UncalibratableError as exc:
        return {**base, "calibrated": False, "uncalibrated_reason": str(exc),
                "buckets": [{"key": s.key, "dates_with_quotes": s.dates_with_quotes}
                            for s in stats]}
    day = day_session_buckets(costs, *session)
    head = headline(costs, rule, *session)
    tv = Fraction(tick.tick_value_usd)
    return {
        **base, "calibrated": True,
        "headline_day_session": {
            "n_buckets": head["n_buckets"], "first_bucket": head["first"],
            "last_bucket": head["last"], "fallback_buckets": head["fallback_buckets"],
            "round_turn_ticks": {k: f(v) for k, v in head["round_turn_ticks"].items()},
            "round_turn_usd": {k: f(v) for k, v in head["round_turn_usd"].items()}},
        "event_window_side_ticks": {s: f(v) for s, v in event.items()},
        "event_window_side_slippage_usd": {s: f(v * tv) for s, v in event.items()},
        "event_window_round_turn_ticks": f(rule.commission_ticks + event["buy"] + event["sell"]),
        "fallback_buckets": [c.stats.key for c in costs if c.fallback],
        "buckets": [_bucket_json(c, tick.tick_value_usd, {d.stats.key for d in day})
                    for c in costs],
    }


# ------------------------------------------------------------------ MES check ----
def mes_check(mnq: dict | None, table_path: Path = MES_D1_TABLE) -> dict:
    """D.1's recorded MES table under D8's arithmetic, beside the MNQ table (no MES file read)."""
    d1 = json.loads(table_path.read_text())
    if int(d1["bucket_minutes"]) != 15:
        raise ValueError("D.1's MES table is not in 15-minute buckets")
    b15 = d1["buckets_ct"]
    comm_ticks = Fraction(MES_COMMISSION_RT) / Fraction(MES_TICK_VALUE)
    rows: list[dict] = []
    mnq_by_key = {b["key"]: b for b in (mnq or {}).get("buckets", [])}
    for minute in range(0, 1440, BUCKET_MINUTES):
        key, half2 = hhmm(minute), hhmm(minute + 15)
        halves = [b15.get(key), b15.get(half2)]
        if all(h is None for h in halves):
            continue
        if any(h is None for h in halves):
            rows.append({"key": key, "note": "one 15-minute half missing in D.1's table"})
            continue
        s_b = (Fraction(str(halves[0]["half_spread_ticks_mean"]))
               + Fraction(str(halves[1]["half_spread_ticks_mean"]))) / 2
        rt = comm_ticks + 2 * s_b
        row = {"key": key, "mes_d1_15min": [halves[0]["half_spread_ticks_mean"],
                                            halves[1]["half_spread_ticks_mean"]],
               "mes_s_b_ticks": f(s_b), "mes_round_turn_ticks": f(rt),
               "mes_round_turn_usd": f(rt * Fraction(MES_TICK_VALUE))}
        m = mnq_by_key.get(key)
        if m is not None:
            row.update({"mnq_half_spread_ticks": m["half_spread_ticks"],
                        "mnq_round_turn_ticks": m["round_turn_ticks"],
                        "mnq_round_turn_usd": m["round_turn_usd"]})
        rows.append(row)
    day = [r for r in rows if "mes_s_b_ticks" in r and 8 * 60 + 30 <= _min(r["key"]) < 15 * 60]
    full = [r for r in rows if "mes_s_b_ticks" in r]

    def stat(key: str, among: list[dict] | None = None) -> dict | None:
        vals = [r[key] for r in (day if among is None else among) if r.get(key) is not None]
        if not vals:
            return None
        return {"mean": sum(vals) / len(vals), "min": min(vals), "max": max(vals), "n": len(vals)}

    return {
        "source": "sim/slippage_calibration.json (D.1; read as recorded; no MES book file opened)",
        "method": "30-minute s_b = mean of the two 15-minute 'half_spread_ticks_mean' values "
                  "(each half equally weighted, as both are 1800 s of open time in D.1's "
                  "uniform-second sampling); MES round turn = 1.22/1.25 + 2 s_b. No depth "
                  "term: D.1's table records no top-of-book size (its size-5 walk is within "
                  "0.03 ticks of size 1 in the day session, so a 2-micro order would add at "
                  "most about that).",
        "mes_commission_rt_usd": float(MES_COMMISSION_RT), "mes_tick_value_usd": 1.25,
        "rows": rows,
        "day_session_0830_1500": {k: stat(k) for k in (
            "mes_s_b_ticks", "mes_round_turn_ticks", "mes_round_turn_usd",
            "mnq_half_spread_ticks", "mnq_round_turn_ticks", "mnq_round_turn_usd")},
        "all_buckets": {k: stat(k, full) for k in (
            "mes_round_turn_ticks", "mes_round_turn_usd", "mnq_round_turn_ticks",
            "mnq_round_turn_usd")},
        "d8_text_reference": "D8's reasoning cites MES's model at 'about 2.11 ticks a round "
                             "turn' (commission plus a time-of-day half-spread table).",
        "differences": [
            "D.1: two days of MES mbp-10 (2026-07-15, 2026-07-31, UTC-date files in "
            "MLCryptoEngine, inside holdout-1); D8: five full trade dates of mbp-1 (2025-05-14 "
            "to 2026-04-15) for MNQ.",
            "Different contracts: MES (tick $1.25, commission $1.22) against MNQ (tick $0.50, "
            "commission $1.22); the same exchange's micro equity index futures, not the same "
            "book.",
            "15-minute buckets from uniform 1-second sampling (D.1) against 30-minute buckets "
            "time-weighted exactly by event time (D8); D.1's 15-minute means are recorded to "
            "4 decimals.",
            "D.1 excluded seconds in closures and a 1 s grace like this calibration; its "
            "overnight buckets mix two trade dates (UTC-date files).",
        ],
    }


def _min(key: str) -> int:
    hh, mm = key.split(":")
    return int(hh) * 60 + int(mm)


# ------------------------------------------------------------------ build ----
def check_calendar_unchanged(raw: dict) -> None:
    """The buckets the raw line was calibrated on are still the calendar's buckets. A calendar
    module may change after the run (the builders were still writing); that is harmless unless
    the sample dates' open time changed, which refuses the build until the contract is re-run."""
    cal = load_group_calendar(raw["group"])
    if cal.module_sha256() == raw["calendar_sha256"]:
        return
    # changed module: accepted only if every sample date's buckets are unchanged to the ns
    for day in SAMPLE_DATES:
        now = {p.key: (p.start_ns, p.end_ns) for p in bucket_pieces(cal, day)}
        then = {k: (_utc_ns_exact(b["start_utc"]), _utc_ns_exact(b["end_utc"]))
                for k, b in raw["dates"][day.isoformat()]["buckets"].items()}
        if now != then:
            raise ValueError(f"{raw['product']}: the {raw['group']} calendar changed the open "
                             f"time of {day} since calibration; re-run the contract")


def _utc_ns_exact(text: str) -> int:
    head, frac = text.rstrip("Z").split(".")
    sec = int(datetime.fromisoformat(head).replace(tzinfo=UTC).timestamp())
    return sec * NS + int(frac)


def build_table(raws: dict[str, dict], sizes: dict[str, int] | None) -> dict:
    commissions = load_commissions()
    ticks = load_ticks()
    products: dict[str, dict] = {}
    for root in sorted(raws):
        raw = raws[root]
        check_calendar_unchanged(raw)
        q_c = None if sizes is None else sizes.get(root)
        if sizes is not None and q_c is None:
            raise KeyError(f"{root}: no q_c in {SIZES_JSON.name}")
        products[root] = product_entry(
            raw, ticks[root], commissions[root], q_c, day_session_of(root, raw["group"]),
            {raw["group"]: load_group_calendar(raw["group"]).module_sha256()})
    now = datetime.now(UTC)
    return {
        "stage": "E.2a", "task": 8,
        "rule": "docs/STAGE_E_DESIGN.md D8 (frozen, commit ba67073)",
        "generated_utc": now.isoformat(),
        "generated_pdt": now.astimezone(PDT).strftime("%Y-%m-%d %H:%M %Z"),
        "sample_dates": [d.isoformat() for d in SAMPLE_DATES],
        "bucket_minutes": BUCKET_MINUTES, "min_dates_with_quotes": MIN_DATES_WITH_QUOTES,
        "depth_term": "applied" if sizes is not None else "pending",
        "vehicle_sizes": ({"path": str(SIZES_JSON.relative_to(REPO_ROOT)),
                           "sha256": sha256_file(SIZES_JSON)} if sizes is not None else None),
        "units": "slippage per side per contract in ticks of the contract; USD = ticks x tick "
                 "value; commission is the round-turn total per contract",
        "readings": list(READINGS),
        "limitations": list(LIMITATIONS),
        "tbbo_check": "not available: no tbbo was bought (U4, U8)",
        "products_expected": 45,
        "products_calibrated": sorted(r for r, p in products.items() if p["calibrated"]),
        "products_uncalibrated": sorted(r for r, p in products.items() if not p["calibrated"]),
        "products": products,
        "mes_check": mes_check(products.get("MNQ")),
    }


def build() -> int:
    from sim.cost_report_md import write_md

    raws = done_products()
    if not raws:
        print("no calibrated contracts in the scratch")
        return 2
    sizes = load_sizes()
    table = build_table(raws, sizes)
    OUT_JSON.write_text(json.dumps(table, indent=1) + "\n")
    write_md(table, OUT_MD)
    print(f"wrote {OUT_JSON} and {OUT_MD}: {len(table['products'])} contracts, depth term "
          f"{table['depth_term']}")
    return 0


__all__ = ["build", "build_table", "date", "load_sizes", "mes_check", "product_entry"]
