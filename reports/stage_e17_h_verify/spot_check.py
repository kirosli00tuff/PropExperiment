"""Independent spot check of traded units against the stores of the run manifest.

For every H2 and H3 unit and a stratified sample of H1 and H4 units (product x era x direction,
plus units carrying the rare flags), this script re-derives from the bars alone: the fill
instants and prices at the frozen minutes (settlement table; R-B1 close fill at a scheduled
closure), the signal and direction, the gross P&L in exact cents (price-path ticks x the
vehicle's tick value), the per-fill cost (frozen D8 tables through screening.stage_e_frozen,
event window from the two release calendars, R-B2 uncalibrated bucket), the stress (+1 vehicle
tick per side) and slip150 (1.5 x slippage ticks) costs, and for H2/H3 the daily
mark-to-settlement values of the component series. base_rules is never imported.
Every store's sha256 is checked against the manifest before a row is read; one store is in
memory at a time; nothing prints a price."""
from __future__ import annotations

import hashlib
import json
import math
import random
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from decimal import Decimal
from fractions import Fraction
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
sys.path.insert(0, "/home/kiros-li/Documents/GitHub/PropExperiment")
from vv_common import CASES, OUT, REPO, RUNS, iter_units, money, write_json  # noqa: E402
from rules.products import product  # noqa: E402  (frozen module, hashed in the freeze)
from screening.stage_e_frozen import load_frozen_tables, slippage_cents  # noqa: E402  (frozen)

CT = ZoneInfo("America/Chicago")
NS_MIN = 60_000_000_000
EVENT_NS = 30 * NS_MIN
GUARD_NS = 2 * NS_MIN
VEHICLE = {"NQ": "MNQ", "YM": "MYM", "RTY": "M2K", "CL": "MCL", "GC": "MGC", "HG": "MHG"}
HIST_LAST = "2019-04-30"
SEED = 20261010
H14_PER_STRATUM = 1
TABLES = load_frozen_tables()


# ------------------------------------------------------------------ inputs ----
def sha256(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def load_settlement() -> dict:
    with open(REPO / "reports/stage_e16_settlement.json", encoding="utf-8") as handle:
        return json.load(handle)["products"]


def hm(text: str) -> int:
    h, m = text.split(":")
    return int(h) * 60 + int(m)


def settle_minute(settle: dict, root: str, day: str) -> tuple[int | None, str | None]:
    for period in settle[root]["settle"]:
        if period["from"] <= day <= period["to"]:
            if period["minute_ct"] is None:
                return None, None
            return hm(period["minute_ct"]), period["lead_grade"]
    return None, None


def open_minute(settle: dict, root: str, day: str, first_of_week: bool) -> int | None:
    for period in settle[root]["day_open"]:
        if period["from"] <= day <= period["to"]:
            if period["minute_ct"] is None:
                return None
            if first_of_week and period.get("first_business_day_of_week_minute_ct"):
                return hm(period["first_business_day_of_week_minute_ct"])
            return hm(period["minute_ct"])
    return None


def load_releases() -> dict[str, np.ndarray]:
    """root -> sorted release instants (ns) from the frozen 2019-05..2024-02 calendar and E.14's
    2010-2019 rows (FOMC, NGS, WPSR); a release concerns the price-path root or the vehicle."""
    by_root: dict[str, set[int]] = defaultdict(set)
    skipped = 0
    for rel in ("reports/stage_e2b_release_calendar.json", "reports/stage_e14_cal_releases.json"):
        with open(REPO / rel, encoding="utf-8") as handle:
            raw = json.load(handle)
        for entry in raw["releases"]:
            inst = entry.get("instant_utc")
            if not inst:
                skipped += 1
                continue
            dt = datetime.fromisoformat(inst.replace("Z", "+00:00"))
            ns = int(dt.timestamp()) * 1_000_000_000
            for root in entry["products"]:
                by_root[root].add(ns)
    out = {r: np.asarray(sorted(v), dtype=np.int64) for r, v in by_root.items()}
    out["_skipped_without_instant"] = skipped  # type: ignore[assignment]
    return out


def latest_release(releases: dict, roots: tuple[str, ...], ts_ns: int) -> int | None:
    best = None
    for root in roots:
        arr = releases.get(root)
        if arr is None or len(arr) == 0:
            continue
        i = int(np.searchsorted(arr, ts_ns, side="right")) - 1
        if i >= 0:
            best = max(best or -1, int(arr[i]))
    return best


# ------------------------------------------------------------------- store ----
class Store:
    """The bars of one root in one store, restricted to the trade dates asked for."""

    def __init__(self, root: str, path: str, expected_sha: str, dates: set[str]):
        full = REPO / path
        digest = sha256(full)
        if digest != expected_sha:
            raise RuntimeError(f"{path}: sha256 {digest[:12]} != manifest {expected_sha[:12]}")
        self.root = root
        all_dates = pq.read_table(full, columns=["trade_date"]).column(0).to_pylist()
        self.trade_dates = sorted(set(all_dates))
        table = pq.read_table(full, columns=["ts_event", "open", "high", "low", "close", "raw_symbol",
                                             "trade_date", "in_scheduled_closure",
                                             "in_no_new_positions_window"],
                              filters=[("trade_date", "in", sorted(dates))])
        df = table.to_pandas()
        local = pd.to_datetime(df["ts_event"], utc=True).dt.tz_convert(CT)
        df["minute"] = (local.dt.hour * 60 + local.dt.minute).astype(int)
        df = df.sort_values("ts_event").reset_index(drop=True)
        self.df = df
        self.index = {(d, m): i for i, (d, m) in enumerate(zip(df["trade_date"], df["minute"]))}
        self.by_date = {d: g for d, g in df.groupby("trade_date")}
        tick = product(root).vendor_tick
        self.tick = Decimal(str(tick))

    def bar(self, day: str, minute: int):
        i = self.index.get((day, minute))
        if i is None:
            return None
        row = self.df.iloc[i]
        return None if bool(row["in_scheduled_closure"]) else row

    def ticks(self, price: float) -> int:
        q = Decimal(repr(float(price))) / self.tick
        whole = q.to_integral_value()
        if abs(q - whole) > Decimal("1e-6"):
            raise ValueError(f"{self.root}: price off the tick grid")
        return int(whole)

    def prev_trade_date(self, day: str) -> str | None:
        i = self.trade_dates.index(day) if day in self.trade_dates else None
        return None if not i else self.trade_dates[i - 1]

    def first_of_week(self, day: str) -> bool:
        week = datetime.fromisoformat(day).isocalendar()[:2]
        same = [d for d in self.trade_dates if datetime.fromisoformat(d).isocalendar()[:2] == week]
        return bool(same) and same[0] == day

    def first_after_closure(self, day: str, minute: int):
        """The first usable bar of trade date `day` whose instant is after the decision minute's
        bar (day-session clock: the trade date's evening bars of the prior calendar day are
        earlier in time and must not be picked)."""
        g = self.by_date.get(day)
        if g is None:
            return None
        day_bars = g[(g["minute"] <= minute) & (g["minute"] >= 300)]
        if day_bars.empty:
            return None
        ref_ts = int(day_bars["ts_event"].max())
        later = g[(g["ts_event"] > ref_ts) & (~g["in_scheduled_closure"])]
        return None if later.empty else later.iloc[0]


# ------------------------------------------------------------------- costs ----
def tick_value_cents(vehicle: str) -> Fraction:
    return Fraction(str(product(vehicle).tick_value_usd)) * 100


def fill_cost(vehicle: str, ts_ns: int, side: str, qty: int, in_event: bool, uncal_expected: bool,
              case: str) -> tuple[Fraction, bool]:
    """Per-fill cost in exact cents for one case; returns (cents, uncalibrated_bucket_used)."""
    costs = TABLES.costs[vehicle]
    tv = tick_value_cents(vehicle)
    ts = datetime.fromtimestamp(ts_ns / 1e9, tz=timezone.utc)
    uncal = False
    try:
        slip = costs.side_slippage_ticks(ts, side, in_event)
    except Exception:  # no calibrated bucket at this minute: R-B2, the largest per-side slippage
        slip = max(b.side_ticks[side] for b in costs.buckets)
        uncal = True
    if case == "slip150":
        slip *= 1.5
    cents = qty * costs.commission_side_cents + slippage_cents(qty, slip, tv)
    if case == "stress":
        cents += qty * tv
    return Fraction(cents), uncal


# ---------------------------------------------------------------- per unit ----
def compare_fill(rec: dict, name: str, mine_ts, mine_ticks, theirs) -> None:
    if mine_ts is None or mine_ticks is None:
        rec["mismatch"].append(f"{name}: bar missing in my lookup")
        return
    if int(mine_ts) != int(theirs[0]):
        rec["mismatch"].append(f"{name}: instant differs by {(int(theirs[0]) - int(mine_ts)) / NS_MIN:.0f} min")
    if int(mine_ticks) != int(theirs[3]):
        rec["mismatch"].append(f"{name}: price differs by {int(theirs[3]) - int(mine_ticks)} ticks")


def check_costs(rec: dict, row: dict, vehicle: str, releases: dict, fills_mine: list[dict]) -> None:
    """fills_mine: [{ts, side, qty, kind}] in order; compares event flags, uncalibrated flags and
    the three cost totals with the row's costs_cents."""
    roots = (row["key"], vehicle)
    totals = {c: Fraction(0) for c in CASES}
    totals_alt = {c: Fraction(0) for c in CASES}  # flip costed as qty x single-contract cost
    for f_mine, f_theirs in zip(fills_mine, row["fills"]):
        r = latest_release(releases, roots, f_mine["ts"])
        in_event = r is not None and f_mine["ts"] < r + EVENT_NS
        in_guard = r is not None and f_mine["ts"] < r + GUARD_NS
        if in_guard:
            rec["mismatch"].append(f"{f_mine['kind']}: fill inside the D9.5a guard")
        if in_event != bool(f_theirs[4]):
            rec["mismatch"].append(f"{f_mine['kind']}: event flag mine {in_event} theirs {f_theirs[4]}")
        if abs(int(f_theirs[2])) != f_mine["qty"] or (int(f_theirs[2]) > 0) != (f_mine["side"] == "buy"):
            rec["mismatch"].append(f"{f_mine['kind']}: trade sign/qty differs")
        for case in CASES:
            cents, uncal = fill_cost(vehicle, f_mine["ts"], f_mine["side"], f_mine["qty"], in_event,
                                     bool(f_theirs[6]), case)
            totals[case] += cents
            one, _ = fill_cost(vehicle, f_mine["ts"], f_mine["side"], 1, in_event, False, case)
            totals_alt[case] += one * f_mine["qty"]
            if case == "base" and uncal != bool(f_theirs[6]):
                rec["mismatch"].append(f"{f_mine['kind']}: uncalibrated mine {uncal} theirs {f_theirs[6]}")
    for case in CASES:
        theirs = money(row["costs_cents"][case])
        if totals[case] != theirs:
            if totals_alt[case] == theirs:
                rec["notes"].append(f"{case}: cost matches only with per-contract ceil on the flip")
            else:
                rec["mismatch"].append(f"{case}: cost differs by {float(theirs - totals[case]):.2f} cents")


def check_gross(rec: dict, row: dict, vehicle: str, legs: list[tuple[int, int, int]]) -> None:
    """legs: (signed qty, entry_ticks, exit_ticks) per holding segment."""
    tv = tick_value_cents(vehicle)
    gross = sum(Fraction(q) * (b - a) * tv for q, a, b in legs)
    theirs = money(row["gross_cents"])
    if gross != theirs:
        rec["mismatch"].append(f"gross differs by {float(theirs - gross):.2f} cents")
    rec["gross_ticks_ok"] = gross == theirs


def check_intraday(test: str, row: dict, store: Store, settle: dict, releases: dict) -> dict:
    rec = {"test": test, "key": row["key"], "date": row["date"], "mismatch": [], "notes": []}
    root, d, direction = row["key"], row["date"], int(row["direction"])
    vehicle = VEHICLE.get(root, root)
    s_min, grade = settle_minute(settle, root, d)
    if s_min is None or grade not in ("primary", "secondary"):
        rec["mismatch"].append(f"settlement minute/grade on {d}: {s_min} {grade}")
        return rec
    if s_min != int(row["settle_ct"]):
        rec["mismatch"].append(f"settle_ct {row['settle_ct']} != table {s_min}")
    if bool(row["after_1508"]) != (s_min > hm("15:08")):
        rec["mismatch"].append("after_1508 flag")
    o_min = open_minute(settle, root, d, store.first_of_week(d))
    d_prev = store.prev_trade_date(d)
    if d_prev is None:
        rec["mismatch"].append("no previous trade date in the store")
        return rec
    s_prev, g_prev = settle_minute(settle, root, d_prev)
    if s_prev is None:
        rec["mismatch"].append("reference date has no settlement minute")
        return rec
    bar_prev_s = store.bar(d_prev, s_prev)
    bar_prev_s1 = store.bar(d_prev, s_prev - 1)
    if test == "H1":
        if o_min is None or not (s_min - 30 > o_min):
            rec["mismatch"].append(f"S-30 > O violated (O {o_min})")
        sig_bar = store.bar(d, s_min - 31)
        if sig_bar is None or bar_prev_s1 is None:
            rec["mismatch"].append("signal bars missing in my lookup")
            return rec
        if sig_bar["raw_symbol"] != bar_prev_s1["raw_symbol"]:
            rec["mismatch"].append("reference and trade bars differ in contract")
        signal = np.sign(store.ticks(sig_bar["close"]) - store.ticks(bar_prev_s1["close"]))
        if int(signal) != direction:
            rec["mismatch"].append(f"signal {int(signal)} != direction {direction}")
        entry = store.bar(d, s_min - 30)
        exit_bar_s = store.bar(d, s_min)
        at_close = exit_bar_s is None
        if at_close != bool(row["exit_at_close"]):
            rec["mismatch"].append(f"exit_at_close mine {at_close} theirs {row['exit_at_close']}")
        if at_close:
            exit_bar = store.bar(d, s_min - 1)
            exit_ticks = None if exit_bar is None else store.ticks(exit_bar["close"])
        else:
            exit_bar = exit_bar_s
            exit_ticks = None if exit_bar is None else store.ticks(exit_bar["open"])
        if entry is None or exit_bar is None:
            rec["mismatch"].append("entry or exit bar missing in my lookup")
            return rec
        if bool(entry["in_no_new_positions_window"]) != bool(row["entry_no_new"]):
            rec["mismatch"].append("entry_no_new flag")
        entry_ticks = store.ticks(entry["open"])
        compare_fill(rec, "entry", entry["ts_event"], entry_ticks, row["fills"][0])
        compare_fill(rec, "exit", exit_bar["ts_event"], exit_ticks, row["fills"][1])
        fills_mine = [{"ts": int(entry["ts_event"]), "side": "buy" if direction > 0 else "sell", "qty": 1, "kind": "entry"},
                      {"ts": int(exit_bar["ts_event"]), "side": "sell" if direction > 0 else "buy", "qty": 1, "kind": "exit"}]
    else:  # H4
        bar_prev_s30 = store.bar(d_prev, s_prev - 30)
        ref_close = bar_prev_s is None
        if ref_close != bool(row["ref_exit_at_close"]):
            rec["mismatch"].append(f"ref_exit_at_close mine {ref_close} theirs {row['ref_exit_at_close']}")
        ref_exit = (store.ticks(bar_prev_s1["close"]) if ref_close and bar_prev_s1 is not None
                    else (store.ticks(bar_prev_s["open"]) if bar_prev_s is not None else None))
        if bar_prev_s30 is None or ref_exit is None:
            rec["mismatch"].append("reference bars missing in my lookup")
            return rec
        move = ref_exit - store.ticks(bar_prev_s30["open"])
        if -int(np.sign(move)) != direction:
            rec["mismatch"].append(f"-sign(m) {-int(np.sign(move))} != direction {direction}")
        if o_min is None:
            rec["mismatch"].append("no day open in the table")
            return rec
        entry = store.bar(d, o_min + 1)
        exit_bar = store.bar(d, s_min - 31)
        if entry is None or exit_bar is None:
            rec["mismatch"].append("entry or exit bar missing in my lookup")
            return rec
        if entry["raw_symbol"] != bar_prev_s30["raw_symbol"]:
            rec["mismatch"].append("reference and trade bars differ in contract")
        if bool(entry["in_no_new_positions_window"]) != bool(row["entry_no_new"]):
            rec["mismatch"].append("entry_no_new flag")
        entry_ticks, exit_ticks = store.ticks(entry["open"]), store.ticks(exit_bar["open"])
        compare_fill(rec, "entry", entry["ts_event"], entry_ticks, row["fills"][0])
        compare_fill(rec, "exit", exit_bar["ts_event"], exit_ticks, row["fills"][1])
        fills_mine = [{"ts": int(entry["ts_event"]), "side": "buy" if direction > 0 else "sell", "qty": 1, "kind": "entry"},
                      {"ts": int(exit_bar["ts_event"]), "side": "sell" if direction > 0 else "buy", "qty": 1, "kind": "exit"}]
    check_gross(rec, row, vehicle, [(direction, entry_ticks, exit_ticks)])
    check_costs(rec, row, vehicle, releases, fills_mine)
    return rec


def multiday_fills(row: dict, store: Store, settle: dict, decision_ct: int | None) -> list[dict] | None:
    """My fills for an H2 leg or an H3 unit: [{ts, ticks, side, qty, kind, trade_date}], rolls
    at the contract change (last bar before the splice, first bar at or after it)."""
    root = row["key"]
    out = []
    kinds = [f[1] for f in row["fills"]]
    open_dates = row["open_dates"]
    # H3's shape is fixed (short at t-3, flip at t, exit at t+5): the entry is a sell whatever
    # the row's direction field says; H2's leg direction is the row's.
    direction = -1 if "flip" in kinds else int(row["direction"])
    # entry
    d0 = open_dates[0]
    if decision_ct is not None:  # H2
        if row.get("entry_after_closure"):
            bar = store.first_after_closure(d0, decision_ct)
        else:
            bar = store.bar(d0, decision_ct)
    else:  # H3 at S_T
        s0, _ = settle_minute(settle, root, d0)
        bar = store.bar(d0, s0)
    if bar is None:
        return None
    out.append({"ts": int(bar["ts_event"]), "ticks": store.ticks(bar["open"]), "side": "buy" if direction > 0 else "sell",
                "qty": 1, "kind": "entry", "symbol": bar["raw_symbol"]})
    # flip (H3) at t
    if "flip" in kinds:
        t = row["date"]
        s_t, _ = settle_minute(settle, root, t)
        bar = store.bar(t, s_t)
        if bar is None:
            return None
        out.append({"ts": int(bar["ts_event"]), "ticks": store.ticks(bar["open"]), "side": "buy",
                    "qty": 2, "kind": "flip", "symbol": bar["raw_symbol"]})
    # exit
    dL = open_dates[-1]
    s_l, _ = settle_minute(settle, root, dL)
    exit_bar_s = store.bar(dL, s_l)
    if exit_bar_s is None:
        bar = store.bar(dL, s_l - 1)
        if bar is None:
            return None
        ticks = store.ticks(bar["close"])
    else:
        bar, ticks = exit_bar_s, store.ticks(exit_bar_s["open"])
    final_dir = 1 if "flip" in kinds else direction
    out.append({"ts": int(bar["ts_event"]), "ticks": ticks, "side": "sell" if final_dir > 0 else "buy",
                "qty": 1, "kind": "exit", "symbol": bar["raw_symbol"], "at_close": exit_bar_s is None})
    # rolls: a raw_symbol change between the entry and the exit instants
    seg = store.df[(store.df["ts_event"] > out[0]["ts"]) & (store.df["ts_event"] <= out[-1]["ts"])]
    seg = seg[seg["trade_date"].isin(open_dates)]
    change = seg.index[seg["raw_symbol"].values != np.roll(seg["raw_symbol"].values, 1)]
    change = [i for i in change if i != seg.index[0]]
    for i in change:
        before = store.df.iloc[i - 1]
        after = store.df.iloc[i]
        pos_dir = 1 if ("flip" in kinds and int(after["ts_event"]) > out[1]["ts"]) else direction
        out.append({"ts": int(before["ts_event"]), "ticks": store.ticks(before["open"]), "side": "sell" if pos_dir > 0 else "buy",
                    "qty": 1, "kind": "roll_out", "symbol": before["raw_symbol"]})
        out.append({"ts": int(after["ts_event"]), "ticks": store.ticks(after["open"]), "side": "buy" if pos_dir > 0 else "sell",
                    "qty": 1, "kind": "roll_in", "symbol": after["raw_symbol"]})
    out.sort(key=lambda f: (f["ts"], 0 if f["kind"] in ("roll_out", "exit", "flip") else 1))
    return out


def gross_legs(fills: list[dict], direction: int) -> list[tuple[int, int, int]]:
    legs, pos, last = [], 0, None
    for f in fills:
        signed = f["qty"] if f["side"] == "buy" else -f["qty"]
        if pos != 0:
            legs.append((pos, last, f["ticks"]))
        pos += signed
        last = f["ticks"]
    return legs


def check_multiday(test: str, row: dict, store: Store, settle: dict, releases: dict, decision_ct) -> dict:
    rec = {"test": test, "key": row["key"], "date": row["date"], "mismatch": [], "notes": []}
    vehicle = VEHICLE.get(row["key"], row["key"])
    mine = multiday_fills(row, store, settle, decision_ct)
    if mine is None:
        rec["mismatch"].append("a fill bar is missing in my lookup")
        return rec
    theirs = sorted(row["fills"], key=lambda f: f[0])
    if [f["kind"] for f in mine] != [f[1] for f in theirs]:
        rec["mismatch"].append(f"fill kinds mine {[f['kind'] for f in mine]} theirs {[f[1] for f in theirs]}")
        return rec
    for f_mine, f_theirs in zip(mine, theirs):
        compare_fill(rec, f_mine["kind"], f_mine["ts"], f_mine["ticks"], f_theirs)
        if f_mine["kind"] == "exit" and bool(f_theirs[5]) != bool(f_mine.get("at_close")):
            rec["mismatch"].append("exit at_close flag")
    check_gross(rec, row, vehicle, gross_legs(mine, int(row["direction"])))
    row_sorted = dict(row)
    row_sorted["fills"] = theirs
    check_costs(rec, row_sorted, vehicle, releases, mine)
    rec["my_fills"] = mine
    return rec


# ------------------------------------------------------- daily marks (H2, H3) ----
def daily_values(row: dict, fills: list[dict], store: Store, settle: dict, case: str, releases: dict) -> dict[str, float]:
    """The leg's/unit's daily mark-to-settlement values in risk units from the bars: events (marks
    at S or the R-B1 close point, and fills) in time order; P&L booked to the event's trade date."""
    root, vehicle = row["key"], VEHICLE.get(row["key"], row["key"])
    tv = tick_value_cents(vehicle)
    sigma = float(row["sigma"])
    events = []
    for d in row["open_dates"]:
        s, _ = settle_minute(settle, root, d)
        bar = store.bar(d, s)
        if bar is not None:
            events.append((int(bar["ts_event"]), 1, "mark", store.ticks(bar["open"]), 0, d))
        else:
            bar = store.bar(d, s - 1)
            if bar is not None:  # R-B1(a): the close of bar S-1, at its open + 60 s
                events.append((int(bar["ts_event"]) + NS_MIN, 1, "mark", store.ticks(bar["close"]), 0, d))
    roots = (root, vehicle)
    for f in fills:
        r = latest_release(releases, roots, f["ts"])
        in_event = r is not None and f["ts"] < r + EVENT_NS
        cost, _ = fill_cost(vehicle, f["ts"], f["side"], f["qty"], in_event, False, case)
        signed = f["qty"] if f["side"] == "buy" else -f["qty"]
        ts = f["ts"] + (NS_MIN if f.get("at_close") else 0)
        events.append((ts, 0, "fill", f["ticks"], (signed, cost), store.df.loc[store.df["ts_event"] == f["ts"], "trade_date"].iloc[0]))
    events.sort(key=lambda e: (e[0], e[1]))
    out: dict[str, Fraction] = defaultdict(Fraction)
    pos, last = 0, None
    for ts, _, kind, ticks, info, day in events:
        if pos != 0:
            out[day] += Fraction(pos) * (ticks - last) * tv
        if kind == "fill":
            signed, cost = info
            pos += signed
            out[day] -= cost
        last = ticks
    return {d: float(v / 100) / sigma for d, v in out.items()}


# ----------------------------------------------------------------- driver ----
def select_h14(test: str) -> list[dict]:
    rng = random.Random(SEED + len(test))
    strata: dict[tuple, list[dict]] = defaultdict(list)
    flagged: dict[str, list[dict]] = defaultdict(list)
    for row in iter_units(test):
        era = "hist" if row["date"] <= HIST_LAST else "step2"
        strata[(row["key"], era, int(row["direction"]))].append(row)
        for flag in ("exit_at_close", "entry_no_new", "ref_exit_at_close"):
            if row.get(flag):
                flagged[flag].append(row)
        if any(f[4] for f in row["fills"]):
            flagged["event"].append(row)
        if any(f[6] for f in row["fills"]):
            flagged["uncalibrated"].append(row)
    picked: dict[tuple[str, str], dict] = {}
    for key, rows in sorted(strata.items()):
        for row in rng.sample(rows, min(H14_PER_STRATUM, len(rows))):
            picked[(row["key"], row["date"])] = row
    for flag, rows in sorted(flagged.items()):
        for row in rng.sample(rows, min(3, len(rows))):
            picked[(row["key"], row["date"])] = row
    return list(picked.values())


def main() -> None:
    settle = load_settlement()
    releases = load_releases()
    with open(REPO / "reports/stage_e17_run_manifest.json", encoding="utf-8") as handle:
        manifest = json.load(handle)["stores"]
    units = {"H1": select_h14("H1"), "H4": select_h14("H4"),
             "H2": list(iter_units("H2")), "H3": list(iter_units("H3"))}
    # group the work by (root, era) so that each store is loaded once
    work: dict[tuple[str, str], list[tuple[str, dict]]] = defaultdict(list)
    need_dates: dict[tuple[str, str], set[str]] = defaultdict(set)
    for test, rows in units.items():
        for row in rows:
            era = "hist" if row["exit_date"] <= HIST_LAST else "step2"
            work[(row["key"], era)].append((test, row))
            need_dates[(row["key"], era)].update(row.get("open_dates", []) + [row["date"], row["entry_date"], row["exit_date"]])
    results: list[dict] = []
    daily_mine: dict[str, dict[str, dict[str, float]]] = {"H2": defaultdict(dict), "H3": defaultdict(dict)}
    stores_checked = []
    only_roots = set(sys.argv[1:])  # smoke test: restrict to these roots
    for (root, era), items in sorted(work.items()):
        if only_roots and root not in only_roots:
            continue
        entry = manifest[root]["ext2010" if era == "hist" else "step2"]
        if entry is None:
            results.append({"test": "?", "key": root, "date": era, "mismatch": ["no store for this era (fallback root)"], "notes": []})
            continue
        dates = set(need_dates[(root, era)])
        # references for H1/H4 need the previous trade date: widen by reading all dates first
        store_dates = pq.read_table(REPO / entry["path"], columns=["trade_date"]).column(0).to_pylist()
        sorted_dates = sorted(set(store_dates))
        for d in list(dates):
            i = sorted_dates.index(d) if d in sorted_dates else None
            if i:
                dates.add(sorted_dates[i - 1])
        store = Store(root, entry["path"], entry["sha256"], dates)
        stores_checked.append({"root": root, "era": era, "path": entry["path"], "sha256_ok": True, "units": len(items)})
        for test, row in items:
            if test in ("H1", "H4"):
                results.append(check_intraday(test, row, store, settle, releases))
            else:
                decision = int(row["decision_ct"]) if test == "H2" else None
                rec = check_multiday(test, row, store, settle, releases, decision)
                results.append(rec)
                if "my_fills" in rec and not rec["mismatch"]:
                    for case in CASES:
                        vals = daily_values(row, rec["my_fills"], store, settle, case, releases)
                        for d, v in vals.items():
                            daily_mine[test][case][(row["key"], row["date"], d)] = v
                rec.pop("my_fills", None)
        del store
        print(f"{root} {era}: {len(items)} units checked", flush=True)
    # daily component comparison: H2 pair sum per date; H3 sum of open units per date
    comp_cmp = {}
    for test in ("H2", "H3"):
        with open(RUNS / f"{test}_result.json", encoding="utf-8") as handle:
            component = json.load(handle)["component"]
        comp_cmp[test] = {}
        for case in CASES:
            mine_by_date: dict[str, float] = defaultdict(float)
            for (_, _, d), v in daily_mine[test][case].items():
                mine_by_date[d] += v
            diffs = [abs(mine_by_date[d] - component[case].get(d, 0.0)) for d in mine_by_date]
            comp_cmp[test][case] = {"dates_compared": len(diffs), "max_abs_diff": max(diffs) if diffs else None,
                                    "dates_over_1e-9": sum(1 for x in diffs if x > 1e-9)}
    summary = Counter()
    for rec in results:
        summary[f"{rec['test']}_checked"] += 1
        if rec["mismatch"]:
            summary[f"{rec['test']}_with_mismatch"] += 1
        for note in rec["notes"]:
            summary[f"{rec['test']}_note:{note.split(':')[0]}"] += 1
    write_json(OUT / "spot_check.json", {
        "selection_seed": SEED, "stores_checked": stores_checked,
        "releases_without_instant_skipped": releases.get("_skipped_without_instant"),
        "summary": dict(sorted(summary.items())), "daily_component_comparison": comp_cmp,
        "units": [{k: v for k, v in r.items()} for r in results]})
    print("summary:", dict(sorted(summary.items())))
    print("daily component comparison:", json.dumps(comp_cmp))
    mism = [r for r in results if r["mismatch"]]
    print("units with mismatches:", len(mism))
    for r in mism[:40]:
        print("  ", r["test"], r["key"], r["date"], r["mismatch"][:4])


if __name__ == "__main__":
    main()
