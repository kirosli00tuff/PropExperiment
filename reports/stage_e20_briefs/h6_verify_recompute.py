"""Independent bar-level recomputation of H6 (VerdictVerifier-FableXHigh, E.20 Step 4).

Built from reports/stage_e20_prereg_H6.md and the frozen inputs only. Never imports h6_rod.
Writes reports/stage_e20_briefs/h6_verify_independent.json.
"""
from __future__ import annotations

import os

os.nice(10)

import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import statistics  # noqa: E402
from datetime import UTC, date, datetime, time, timedelta  # noqa: E402
from pathlib import Path  # noqa: E402
from zoneinfo import ZoneInfo  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import pyarrow.parquet as pq  # noqa: E402
from scipy.stats import t as student_t  # noqa: E402

from data.group_session import _equity_calendar, previous_trade_date, trade_dates_between  # noqa: E402
from ml_route_v2.gate0 import _b_test  # noqa: E402
from rules.sessions import flatten_time_ct  # noqa: E402
from screening.stage_e_frozen import load_frozen_tables, slippage_cents  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
STORE = REPO / "data/processed_step2/NQ/ohlcv-1m_NQ_v_0_2019-05-06_2024-02-29_step2.parquet"
STORE_SHA = "08fae13f8747883944888f4e7a3dd695c974707df2af59a22ef9036816be30aa"
GEX = REPO / "reports/stage_e14_briefs/gex/DIX.csv"
GEX_SHA = "51bef9ea5ee13af2f72b14f4198de57eeb865a36c1d3e244a3f64b3603e9ce62"
RELEASES = REPO / "reports/stage_e2b_release_calendar.json"
OUT = REPO / "reports/stage_e20_briefs/h6_verify_independent.json"

CT = ZoneInfo("America/Chicago")
NS = 1_000_000_000
MIN_NS = 60 * NS
TICK = 0.25
TICK_CENTS = 50
VERDICT = (date(2020, 6, 1), date(2024, 2, 29))
OVERLAP = (date(2019, 5, 6), date(2020, 5, 29))
NEVER_AFTER = date(2024, 2, 29)
T2_LOOKBACK = 60
ALPHA = 0.025
EVENT_WINDOW_NS = 30 * MIN_NS
FILL_GUARD_NS = 2 * MIN_NS


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ct_ns(d: date, t: time) -> int:
    return int(datetime.combine(d, t, tzinfo=CT).astimezone(UTC).timestamp()) * NS


def utc_dt(ns: int) -> datetime:
    return datetime.fromtimestamp(ns / NS, UTC)


def ct_str(ns: int) -> str:
    return utc_dt(ns).astimezone(CT).strftime("%Y-%m-%d %H:%M")


# ------------------------------------------------------------------ inputs ----
assert sha256(STORE) == STORE_SHA, "NQ store sha256 differs from the prereg"
assert sha256(GEX) == GEX_SHA, "GEX CSV sha256 differs from the prereg"

store = pq.read_table(STORE, columns=["ts_event", "open", "close", "instrument_id", "trade_date"])
bars = store.to_pandas()
ts = bars["ts_event"].to_numpy(dtype=np.int64)
assert np.all(np.diff(ts) > 0), "store ts_event not strictly increasing"
opn = bars["open"].to_numpy(dtype=np.float64)
cls = bars["close"].to_numpy(dtype=np.float64)
iid = bars["instrument_id"].to_numpy(dtype=np.int64)
tdate = bars["trade_date"].to_numpy(dtype=object)
max_tdate = max(tdate)
assert max_tdate <= NEVER_AFTER.isoformat(), f"store carries a bar dated {max_tdate}"
max_ct_date = utc_dt(int(ts[-1])).astimezone(CT).date()
assert max_ct_date <= NEVER_AFTER, f"store carries a bar whose CT date is {max_ct_date}"
N = len(ts)


def bar_at(ns: int) -> int | None:
    i = int(np.searchsorted(ts, ns, side="left"))
    return i if i < N and ts[i] == ns else None


def first_at_or_after(ns: int) -> int | None:
    i = int(np.searchsorted(ts, ns, side="left"))
    return i if i < N else None


# GEX: date and gex columns only; rows dated 2024-03-01 or later are never used.
gex_rows = pd.read_csv(GEX, usecols=["date", "gex"], dtype={"date": str})
gex_rows = gex_rows[gex_rows["date"] <= NEVER_AFTER.isoformat()]
gex_by_date: dict[date, float] = {date.fromisoformat(r.date): float(r.gex)
                                  for r in gex_rows.itertuples(index=False)}

# Release calendar (D8 event window, D9.5a fill guard), for MNQ and for NQ.
rel = json.loads(RELEASES.read_text(encoding="utf-8"))["releases"]


def release_instants(root: str) -> np.ndarray:
    out = []
    for r in rel:
        if root in r.get("products", []):
            dt = datetime.fromisoformat(r["instant_utc"].replace("Z", "+00:00"))
            out.append(int(dt.timestamp()) * NS)
    return np.array(sorted(out), dtype=np.int64)


REL_MNQ = release_instants("MNQ")
REL_NQ = release_instants("NQ")


def in_window(instants: np.ndarray, fill_ns: int, width_ns: int) -> bool:
    i = int(np.searchsorted(instants, fill_ns, side="right")) - 1
    return i >= 0 and fill_ns < int(instants[i]) + width_ns


tables = load_frozen_tables()
mnq_costs = tables.costs["MNQ"]
COMM_SIDE = mnq_costs.commission_side_cents

# ------------------------------------------------------------------ calendar ----
cal = _equity_calendar()
all_dates = trade_dates_between(cal, OVERLAP[0], VERDICT[1])
verdict_dates = [d for d in all_dates if VERDICT[0] <= d <= VERDICT[1]]
overlap_dates = [d for d in all_dates if OVERLAP[0] <= d <= OVERLAP[1]]
i_v0 = all_dates.index(VERDICT[0])
warmup_start = all_dates[i_v0 - T2_LOOKBACK]
warmup_dates = all_dates[i_v0 - T2_LOOKBACK:i_v0]

# MNQ roll blackout (prereg: the v2 engine stage's set for MNQ, its root's and its price
# path's). No MNQ store exists for 2019-2024 (E.2a's covers 2025-04-01..), so the set is the
# NQ store's own roll_blackout_dates (schema metadata; splice date + 2 prior sessions).
store_meta = json.loads(pq.read_schema(STORE).metadata[b"propexperiment"])
blackout = frozenset(date.fromisoformat(s) for s in store_meta["roll_blackout_dates"])
splices = frozenset(date.fromisoformat(s) for s in store_meta["splice_trade_dates"])


def close_ct(d: date) -> tuple[time, bool]:
    halt = cal.early_halt_ct(d)
    return (halt, True) if halt is not None else (time(15, 0), False)


# ------------------------------------------------------------------ per date ----
rows: list[dict] = []
for d in all_dates:
    C, shortened = close_ct(d)
    c_ns = ct_ns(d, C)
    prev = previous_trade_date(cal, d)
    Cp, prev_short = close_ct(prev)
    rec: dict = {"date": d, "C": C.strftime("%H:%M"), "shortened": shortened, "prev": prev,
                 "prev_shortened": prev_short, "window": (
                     "verdict" if VERDICT[0] <= d <= VERDICT[1] else
                     "overlap" if OVERLAP[0] <= d <= OVERLAP[1] else
                     "warmup" if warmup_start <= d < VERDICT[0] else "gap")}
    i_sig = bar_at(c_ns - 31 * MIN_NS)
    i_pri = bar_at(ct_ns(prev, Cp) - MIN_NS)
    if i_sig is None:
        rec["reason"] = "missing_signal_bar"
    elif i_pri is None:
        rec["reason"] = "missing_prior_bar"
    elif iid[i_sig] != iid[i_pri]:
        rec["reason"] = "instrument_change"
    else:
        r = cls[i_sig] / cls[i_pri] - 1.0
        if r == 0.0:
            rec["reason"] = "zero_signal"
        else:
            rec["reason"] = "eligible"
            rec["r_rod"] = r
            rec["p_sig"] = cls[i_sig]
            rec["p_prior"] = cls[i_pri]
            rec["sig_tdate_ok"] = tdate[i_sig] == d.isoformat()
            rec["pri_tdate_ok"] = tdate[i_pri] == prev.isoformat()
    rows.append(rec)

by_date = {r["date"]: r for r in rows}
eligible_dates = [r["date"] for r in rows if r["reason"] == "eligible"]

# ------------------------------------------------------------------ T2 / T3 masks ----
for r in rows:
    if r["reason"] != "eligible":
        continue
    d = r["date"]
    lo = warmup_start if r["window"] == "verdict" else OVERLAP[0]
    pool = [e for e in eligible_dates if lo <= e < d][-T2_LOOKBACK:]
    if r["window"] in ("verdict", "overlap"):
        if len(pool) < T2_LOOKBACK:
            r["t2"] = None
            r["t2_reason"] = "t2_warmup"
        else:
            med = float(np.median([abs(by_date[e]["r_rod"]) for e in pool]))
            r["t2_threshold"] = med
            r["t2"] = abs(r["r_rod"]) > med
        g = gex_by_date.get(r["prev"])
        if g is None:
            r["t3"] = None
            r["t3_reason"] = "gex_missing"
        else:
            r["gex_prev"] = g
            r["t3"] = g < 0.0

# ------------------------------------------------------------------ trades ----
flags_count: dict[str, int] = {}


def flag(name: str) -> None:
    flags_count[name] = flags_count.get(name, 0) + 1


for r in rows:
    if r["reason"] != "eligible" or r["window"] not in ("verdict", "overlap"):
        continue
    d = r["date"]
    C = time.fromisoformat(r["C"])
    c_ns = ct_ns(d, C)
    F = flatten_time_ct("MNQ", d)
    F_ns = ct_ns(d, F)
    r["F"] = F.strftime("%H:%M")
    side = 1 if r["r_rod"] > 0 else -1
    r["side"] = "buy" if side > 0 else "sell"
    entry_ns = c_ns - 30 * MIN_NS
    i_e = first_at_or_after(entry_ns)
    if i_e is None or tdate[i_e] != d.isoformat():
        r["refusal"] = "no_entry_bar_on_date"
        flag("no_entry_bar_on_date")
        continue
    if ts[i_e] != entry_ns:
        r["entry_bar_gap_min"] = int((ts[i_e] - entry_ns) // MIN_NS)
        flag("entry_fill_bar_missing_used_next")
    if d in blackout:
        r["refusal"] = "engine_roll_blackout"
        continue
    if ts[i_e] >= F_ns:
        r["refusal"] = "engine_flatten_window"
        continue
    if in_window(REL_MNQ, int(ts[i_e]), FILL_GUARD_NS):
        flag("entry_in_d95a_fill_guard")
        r["d95a_entry"] = True
    exit_intent_ns = c_ns - 2 * MIN_NS
    i_x = first_at_or_after(exit_intent_ns)
    if i_x is None or tdate[i_x] != d.isoformat():
        r["refusal"] = "no_exit_intent_bar"
        flag("no_exit_intent_bar")
        continue
    if ts[i_x] != exit_intent_ns:
        flag("exit_intent_bar_missing_used_next")
        r["exit_intent_gap_min"] = int((ts[i_x] - exit_intent_ns) // MIN_NS)
    if ts[i_x] >= F_ns:
        flag("exit_intent_at_or_after_F")
    i_xf = i_x + 1
    if i_xf >= N or tdate[i_xf] != d.isoformat():
        r["refusal"] = "no_exit_fill_bar"
        flag("no_exit_fill_bar")
        continue
    if ts[i_xf] - ts[i_x] != MIN_NS:
        flag("exit_fill_bar_not_adjacent")
        r["exit_fill_gap_min"] = int((ts[i_xf] - ts[i_x]) // MIN_NS)
    if ts[i_xf] >= F_ns:
        flag("exit_fill_at_or_after_F")
        r["exit_fill_at_or_after_F"] = True
    if in_window(REL_MNQ, int(ts[i_xf]), FILL_GUARD_NS):
        flag("exit_in_d95a_fill_guard")
        r["d95a_exit"] = True
    e_dt, x_dt = utc_dt(int(ts[i_e])), utc_dt(int(ts[i_xf]))
    ev_e = in_window(REL_MNQ, int(ts[i_e]), EVENT_WINDOW_NS)
    ev_x = in_window(REL_MNQ, int(ts[i_xf]), EVENT_WINDOW_NS)
    if ev_e != in_window(REL_NQ, int(ts[i_e]), EVENT_WINDOW_NS) or \
            ev_x != in_window(REL_NQ, int(ts[i_xf]), EVENT_WINDOW_NS):
        flag("event_window_differs_mnq_vs_nq")
    if ev_e or ev_x:
        flag("fill_in_d8_event_window")
    entry_side = "buy" if side > 0 else "sell"
    exit_side = "sell" if side > 0 else "buy"
    slip_e = mnq_costs.side_slippage_ticks(e_dt, entry_side, ev_e)
    slip_x = mnq_costs.side_slippage_ticks(x_dt, exit_side, ev_x)
    slip_e_c = slippage_cents(1, slip_e, TICK_CENTS)
    slip_x_c = slippage_cents(1, slip_x, TICK_CENTS)
    c_cents = 2 * COMM_SIDE + slip_e_c + slip_x_c
    c_ticks = c_cents / TICK_CENTS
    entry_px, exit_px = float(opn[i_e]), float(opn[i_xf])
    gross_ticks = side * round((exit_px - entry_px) / TICK)
    r.update({
        "entry_ts_ct": ct_str(int(ts[i_e])), "exit_ts_ct": ct_str(int(ts[i_xf])),
        "entry_px": entry_px, "exit_px": exit_px, "entry_iid": int(iid[i_e]),
        "exit_iid": int(iid[i_xf]), "gross_ticks": float(gross_ticks),
        "slip_entry_ticks": slip_e, "slip_exit_ticks": slip_x,
        "slip_entry_cents": slip_e_c, "slip_exit_cents": slip_x_c,
        "c_cents": c_cents, "c_ticks": c_ticks, "net_ticks": float(gross_ticks) - c_ticks,
        "event_entry": ev_e, "event_exit": ev_x,
    })
    if iid[i_e] != iid[i_xf]:
        flag("instrument_changed_within_trade")


# ------------------------------------------------------------------ statistics ----
def hand_t_p(values: np.ndarray) -> tuple[float, float]:
    n = values.size
    if n < 2:
        return float("nan"), 1.0
    m, sd = float(values.mean()), float(values.std(ddof=1))
    t = m / (sd / math.sqrt(n))
    return t, float(student_t.sf(t, n - 1))


def test_block(test: str, window: str, trades: list[dict], window_dates: list[date]) -> dict:
    out: dict = {"test": test, "window": window, "n_trades": len(trades)}
    if not trades:
        out.update({"t_b": float("nan"), "p": 1.0, "mean_gross_ticks": float("nan"),
                    "mean_c_ticks": float("nan"), "mean_net_ticks": float("nan"),
                    "sharpe_net_annual": float("nan")})
        return out
    df = pd.DataFrame({
        "g_ticks": [t["net_ticks"] for t in trades],
        "cost_ticks": [t["c_ticks"] for t in trades],
        "trade_date": pd.to_datetime([t["date"] for t in trades]),
    })
    b = _b_test(f"E20H6-{test}", "MNQ", "rod", df, len(df))
    gross = np.array([t["gross_ticks"] for t in trades])
    c = np.array([t["c_ticks"] for t in trades])
    net = np.array([t["net_ticks"] for t in trades])
    t_hand, p_hand = hand_t_p(net)
    daily = {t["date"]: t["net_ticks"] * TICK_CENTS / 100.0 for t in trades}
    pnl = np.array([daily.get(d, 0.0) for d in window_dates])
    sharpe = float(pnl.mean() / pnl.std(ddof=1) * math.sqrt(252))
    out.update({
        "n_dates": b.n_dates, "t_b": b.t, "p": b.p, "t_hand": t_hand, "p_hand": p_hand,
        "mean_gross_ticks": float(gross.mean()), "mean_c_ticks": float(c.mean()),
        "mean_c_from_b_test": b.cost_ticks, "mean_net_ticks": float(net.mean()),
        "mean_net_from_b_test": b.mean, "sum_net_usd": float(net.sum() * TICK / 1 * 2.0),
        "sharpe_net_annual": sharpe, "n_window_dates": len(window_dates),
        "wins": int((gross > 0).sum()), "losses": int((gross < 0).sum()),
        "flat": int((gross == 0).sum()), "buys": sum(t["side"] == "buy" for t in trades),
        "sells": sum(t["side"] == "sell" for t in trades),
        "cost_bar_1_5x_mean_c": 1.5 * float(c.mean()),
        "cost_bar_ok": bool(gross.mean() >= 1.5 * c.mean()),
    })
    return out


def holm(tests: dict[str, dict]) -> dict[str, dict]:
    order = sorted(tests.items(), key=lambda kv: (kv[1]["p"], kv[0]))
    m = len(order)
    still = True
    out = {}
    for k, (name, t) in enumerate(order):
        thr = ALPHA / (m - k)
        still = still and t["p"] <= thr
        out[name] = {"rank": k + 1, "threshold": thr, "rejected": still}
    return out


def select(window: str, test: str) -> list[dict]:
    sel = []
    for r in rows:
        if r["window"] != window or r["reason"] != "eligible" or "gross_ticks" not in r:
            continue
        if test == "T2" and not r.get("t2"):
            continue
        if test == "T3" and not r.get("t3"):
            continue
        sel.append(r)
    return sel


MIN_TRADES = {"T1": 100, "T2": 100, "T3": 30}
results: dict[str, dict] = {}
for window, wdates in (("verdict", verdict_dates), ("overlap", overlap_dates)):
    blocks = {t: test_block(t, window, select(window, t), wdates) for t in ("T1", "T2", "T3")}
    h = holm(blocks)
    for t, b in blocks.items():
        b["holm"] = h[t]
        b["min_trades"] = MIN_TRADES[t]
        b["pass_components"] = {
            "holm_rejected": h[t]["rejected"],
            "cost_bar": bool(b.get("cost_bar_ok", False)),
            "min_trades": b["n_trades"] >= MIN_TRADES[t],
            "sharpe_ge_0_5": bool(b["sharpe_net_annual"] >= 0.5)
            if not math.isnan(b["sharpe_net_annual"]) else False,
        }
        b["verdict"] = "PASS" if all(b["pass_components"].values()) else "FAIL"
    results[window] = blocks


# ------------------------------------------------------------------ counts ----
def counts(window: str) -> dict:
    wrows = [r for r in rows if r["window"] == window]
    out: dict = {"trade_dates": len(wrows),
                 "shortened": sum(r["shortened"] for r in wrows),
                 "eligibility": {}, "refusals": {}, "t2": {}, "t3": {},
                 "blackout_dates_in_window": sum(r["date"] in blackout for r in wrows)}
    for r in wrows:
        out["eligibility"][r["reason"]] = out["eligibility"].get(r["reason"], 0) + 1
        if r["reason"] == "eligible":
            ref = r.get("refusal", "traded")
            out["refusals"][ref] = out["refusals"].get(ref, 0) + 1
            k2 = r.get("t2_reason", "t2_date" if r.get("t2") else "not_t2")
            out["t2"][k2] = out["t2"].get(k2, 0) + 1
            k3 = r.get("t3_reason", "t3_date" if r.get("t3") else "not_t3")
            out["t3"][k3] = out["t3"].get(k3, 0) + 1
    out["t2_dates_refused_by_engine"] = sum(
        1 for r in wrows if r["reason"] == "eligible" and r.get("t2") and "refusal" in r)
    out["t3_dates_refused_by_engine"] = sum(
        1 for r in wrows if r["reason"] == "eligible" and r.get("t3") and "refusal" in r)
    out["shortened_eligible"] = sum(1 for r in wrows if r["shortened"] and r["reason"] == "eligible")
    return out


def per_year(window: str) -> dict:
    out: dict = {}
    for t in ("T1", "T2", "T3"):
        for r in select(window, t):
            y = str(r["date"].year)
            e = out.setdefault(t, {}).setdefault(y, {"n": 0, "gross": 0.0, "net": 0.0})
            e["n"] += 1
            e["gross"] += r["gross_ticks"]
            e["net"] += r["net_ticks"]
    return out


def jsonable(o):
    if isinstance(o, (date, datetime)):
        return o.isoformat()
    if isinstance(o, (np.floating, np.integer, np.bool_)):
        return o.item()
    if isinstance(o, float) and math.isnan(o):
        return None
    raise TypeError(str(type(o)))


trade_rows = [{k: v for k, v in r.items()} for r in rows
              if r["window"] in ("verdict", "overlap") and r["reason"] == "eligible"]

out = {
    "written_by": "VerdictVerifier-FableXHigh (reports/stage_e20_briefs/h6_verify_recompute.py)",
    "written_pdt": datetime.now(ZoneInfo("America/Vancouver")).isoformat(timespec="seconds"),
    "inputs": {
        "nq_store": str(STORE.relative_to(REPO)), "nq_store_sha256": STORE_SHA,
        "gex_csv": str(GEX.relative_to(REPO)), "gex_sha256": GEX_SHA,
        "gex_rows_used_max_date": max(gex_by_date).isoformat(),
        "costs_table_sha256": tables.hashes["costs"],
        "store_rows": int(N), "store_max_trade_date": max_tdate,
        "store_max_ct_date": max_ct_date.isoformat(),
        "mnq_commission_side_cents": COMM_SIDE,
        "mnq_max_half_spread_ticks": mnq_costs.max_half_spread_ticks,
        "releases_mnq": int(REL_MNQ.size), "releases_nq": int(REL_NQ.size),
    },
    "calendar": {
        "verdict_trade_dates": len(verdict_dates), "overlap_trade_dates": len(overlap_dates),
        "warmup_start": warmup_start.isoformat(), "warmup_dates": len(warmup_dates),
        "verdict_shortened": sum(by_date[d]["shortened"] for d in verdict_dates),
        "blackout_dates_total": len(blackout),
        "blackout_dates_in_verdict": sorted(d.isoformat() for d in blackout
                                            if VERDICT[0] <= d <= VERDICT[1]),
        "splice_dates_in_verdict": sorted(d.isoformat() for d in splices
                                          if VERDICT[0] <= d <= VERDICT[1]),
    },
    "counts": {"verdict": counts("verdict"), "overlap": counts("overlap"),
               "warmup": counts("warmup")},
    "flags": flags_count,
    "tests": results,
    "per_year": {"verdict": per_year("verdict")},
    "trades": trade_rows,
}
OUT.write_text(json.dumps(out, indent=1, default=jsonable), encoding="utf-8")

# Short summary to stdout only.
print("verdict dates", len(verdict_dates), "shortened", out["calendar"]["verdict_shortened"],
      "blackout in verdict", len(out["calendar"]["blackout_dates_in_verdict"]))
print("warmup_start", warmup_start, "overlap dates", len(overlap_dates))
print("counts verdict", json.dumps(out["counts"]["verdict"]))
print("flags", json.dumps(flags_count))
for t in ("T1", "T2", "T3"):
    b = results["verdict"][t]
    print(t, {k: (round(v, 6) if isinstance(v, float) else v) for k, v in b.items()
              if k in ("n_trades", "mean_gross_ticks", "mean_c_ticks", "mean_net_ticks", "t_b",
                       "p", "t_hand", "p_hand", "sharpe_net_annual", "verdict")},
          b["holm"], b["pass_components"])
print("wrote", OUT)
