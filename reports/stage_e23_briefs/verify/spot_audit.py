"""VerdictVerifier-FableXHigh, Stage E.23: independent re-simulation of the five trigger-hold
books from the ext2010 parquet stores (own code; nothing imported from the project).

Reads, one root at a time and only inside 2010-07-01..2019-04-30 (the ext2010 stores), the bar
columns ts_event, open, close, raw_symbol, trade_date, in_scheduled_closure plus the store's
sidecar metadata (rolls, roll blackout dates, tick). Rebuilds marks, chained daily returns, the
EWMA sigma, the per-contract path with roll legs, D8 costs per side (base; stress = commission +
2 x slippage), the units from the frozen events, the capped net position, the orders and the
daily net series; compares every series value with the run's, recomputes alpha3 and reports the
spot units the brief asks for. Refuses to start while the pytest suite runs or under 4 GB free.
Writes spot_audit.json beside this script. Usage: python spot_audit.py [ROOT ...]
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
import sys
from bisect import bisect_right
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import numpy as np
import pyarrow.parquet as pq
from scipy.stats import norm
from scipy.stats import t as student_t

ROOT = "/home/kiros-li/Documents/GitHub/PropExperiment"
OUT_DIR = f"{ROOT}/reports/stage_e23_briefs/verify"
CT = ZoneInfo("America/Chicago")
START, W_FIRST, W_LAST = date(2010, 7, 1), date(2011, 7, 27), date(2019, 4, 30)
TARGET_VOL, COM, ANN, WARMUP = 0.40, 60.0, 261.0, 60
GROUP = {"ZF": "rates", "ZN": "rates", "ZB": "rates", "NQ": "equity"}
VEHICLE = {"ZF": "ZF", "ZN": "ZN", "ZB": "ZB", "NQ": "MNQ"}
NS_MIN = 60_000_000_000


def load(p: str):
    with open(f"{ROOT}/{p}") as f:
        return json.load(f)


def ct_ns(d: date, minute: int) -> int:
    dt = datetime(d.year, d.month, d.day, minute // 60, minute % 60, tzinfo=CT)
    return int(dt.timestamp()) * 1_000_000_000


def hhmm(s: str) -> int:
    h, m = s.split(":")
    return int(h) * 60 + int(m)


# ------------------------------------------------------------------ calendar ----
class Cal:
    def __init__(self, group: str):
        c = load(f"data/calendars/hist2010/{group}.json")
        first, last = date.fromisoformat(c["coverage"]["first"]), date.fromisoformat(c["coverage"]["last"])
        closures = {date.fromisoformat(e["day"]) for e in c["entries"] if e["kind"] == "full_closure"}
        self.halt = {date.fromisoformat(e["day"]): hhmm(e["halt_ct"]) for e in c["entries"]
                     if e["kind"] == "early_halt"}
        self.late = {date.fromisoformat(e["day"]): hhmm(e["open_ct"]) for e in c["entries"]
                     if e["kind"] == "late_open" and e.get("open_ct")}
        self.sessions = c["sessions"]
        days, d = [], first
        while d <= last:
            if d.weekday() < 5 and d not in closures:
                days.append(d)
            d += timedelta(days=1)
        self.days = days
        self.index = {d: i for i, d in enumerate(days)}
        self.counts = c["counts"]

    def is_trade(self, d: date) -> bool:
        return d in self.index

    def previous(self, d: date) -> date | None:
        i = self.index.get(d)
        if i is None:
            i = bisect_right(self.days, d)
        return self.days[i - 1] if i and i - 1 >= 0 else None

    def intervals(self, d: date) -> list[tuple[int, int]]:
        row = next(s for s in self.sessions
                   if date.fromisoformat(s["valid_from"]) <= d <= date.fromisoformat(s["valid_to"]))
        out = []
        for seg in row["segments"]:
            lo = ct_ns(d + timedelta(days=seg["start_offset_days"]), hhmm(seg["start_ct"]))
            hi = ct_ns(d + timedelta(days=seg["end_offset_days"]), hhmm(seg["end_ct"]))
            out.append((lo, hi))
        if d in self.halt:
            h = ct_ns(d, self.halt[d])
            out = [(lo, min(hi, h)) for lo, hi in out if lo < h]
        if d in self.late:
            o = ct_ns(d, self.late[d])
            out = [(max(lo, o), hi) for lo, hi in out if hi > o]
        return out

    def closure_at(self, d: date, minute: int) -> bool:
        ts = ct_ns(d, minute)
        iv = self.intervals(d)
        return not any(lo <= ts < hi for lo, hi in iv) and any(hi == ts for _lo, hi in iv)


# ------------------------------------------------------------------ bars ----
class Bars:
    def __init__(self, root: str, path: str, expect_sha: str):
        data = open(f"{ROOT}/{path}", "rb").read()
        self.sha = hashlib.sha256(data).hexdigest()
        del data
        if self.sha != expect_sha:
            raise SystemExit(f"{root}: store sha256 {self.sha} != marker preflight {expect_sha}")
        meta = json.loads(pq.read_metadata(f"{ROOT}/{path}").metadata[b"propexperiment"])
        tick = float(meta["tick"]["tick"])
        tab = pq.read_table(f"{ROOT}/{path}", columns=["ts_event", "open", "close", "raw_symbol",
                                                     "trade_date", "in_scheduled_closure"])
        ts = tab["ts_event"].to_numpy()
        order = np.argsort(ts, kind="stable")
        self.ts = ts[order].astype(np.int64)
        op = tab["open"].to_numpy()[order]
        cl = tab["close"].to_numpy()[order]
        self.open_t = np.rint(op / tick).astype(np.int64)
        self.close_t = np.rint(cl / tick).astype(np.int64)
        if np.abs(self.open_t * tick - op).max() > 1e-6 or np.abs(self.close_t * tick - cl).max() > 1e-6:
            raise SystemExit(f"{root}: a price is off the tick grid")
        sym = tab["raw_symbol"].to_numpy().astype(str)[order]
        self.symbols, self.sym = np.unique(sym, return_inverse=True)
        tds = tab["trade_date"].to_numpy().astype(str)[order]
        uniq, inv = np.unique(tds, return_inverse=True)
        ords = np.array([date.fromisoformat(s).toordinal() for s in uniq], dtype=np.int64)
        self.td = ords[inv]
        self.usable = ~tab["in_scheduled_closure"].to_numpy()[order].astype(bool)
        del tab, op, cl, sym, tds
        self.splices = sorted(int(r["ts_ns"]) for r in meta["rolls"])
        self.blackout = {date.fromisoformat(s) for s in meta["roll_blackout_dates"]}
        self.meta = {"rows": int(len(self.ts)), "rolls": len(self.splices), "blackout_dates": len(self.blackout),
                     "tick": tick, "first_td": str(date.fromordinal(int(self.td.min()))),
                     "last_td": str(date.fromordinal(int(self.td.max())))}

    def bar(self, d: date, minute: int) -> int | None:
        target = ct_ns(d, minute)
        i = int(np.searchsorted(self.ts, target))
        if i < len(self.ts) and int(self.ts[i]) == target and int(self.td[i]) == d.toordinal() and bool(self.usable[i]):
            return i
        return None

    def last_before(self, t: int) -> int | None:
        i = int(np.searchsorted(self.ts, t)) - 1
        while i >= 0 and not self.usable[i]:
            i -= 1
        return i if i >= 0 else None

    def first_at_or_after(self, t: int) -> int | None:
        i = int(np.searchsorted(self.ts, t))
        while i < len(self.ts) and not self.usable[i]:
            i += 1
        return i if i < len(self.ts) else None

    def splices_between(self, lo: int, hi: int) -> list[int]:
        return [s for s in self.splices if lo < s <= hi]

    def contract(self, i: int) -> str:
        return str(self.symbols[self.sym[i]])


# ------------------------------------------------------------------ costs (D8) ----
class Costs:
    def __init__(self, vehicle: str):
        t = load("reports/stage_e2a_costs.json")["products"][vehicle]
        self.comm_side = int(round(t["commission_rt_usd"] * 100)) // 2
        self.tv = t["tick_value_usd"] * 100.0  # cents
        self.buckets = [(b["start_min"], b["end_min"], b["side_ticks"]) for b in t["buckets"] if not b["fallback"]]
        self.max_side = {s: max(b[2][s] for b in self.buckets) for s in ("buy", "sell")}
        self.vehicle = vehicle

    def per_side(self, ts_ns: int, side: str) -> tuple[int, int, bool]:
        dt = datetime.fromtimestamp(ts_ns / 1e9, tz=ZoneInfo("UTC")).astimezone(CT)
        minute = dt.hour * 60 + dt.minute
        found = [b for b in self.buckets if b[0] <= minute < b[1]]
        uncal = len(found) != 1
        slip = found[0][2][side] if not uncal else self.max_side[side]
        base = self.comm_side + math.ceil(round(slip * self.tv, 6))
        stress = self.comm_side + 2 * (base - self.comm_side)
        return base, stress, uncal


# ------------------------------------------------------------------ statistics (own) ----
def ols_hac(y: np.ndarray, regs: list[np.ndarray], lags: int) -> dict:
    n = len(y)
    X = np.column_stack([np.ones(n), *regs])
    k = X.shape[1]
    inv = np.linalg.inv(X.T @ X)
    beta = inv @ (X.T @ y)
    e = y - X @ beta
    sse, sst = float(e @ e), float(((y - y.mean()) ** 2).sum())
    se_plain = math.sqrt(sse / (n - k) * inv[0, 0])
    xe = X * e[:, None]
    S = xe.T @ xe
    for lag in range(1, min(lags, n - 1) + 1):
        G = xe[lag:].T @ xe[:-lag]
        S = S + (1.0 - lag / (lags + 1.0)) * (G + G.T)
    se_hac = math.sqrt((inv @ S @ inv)[0, 0])
    a = float(beta[0])
    tp, tn = a / se_plain, a / se_hac
    pp, pn = float(student_t.sf(tp, n - k)), float(norm.sf(tn))
    return {"alpha": a, "betas": [float(b) for b in beta[1:]], "t_plain": tp, "t_nw": tn,
            "p_plain": pp, "p_nw": pn, "p_alpha": max(pp, pn), "r2": 1 - sse / sst,
            "se_plain": se_plain, "se_hac": se_hac}


def close(a, b, rel=1e-9, ab=1e-12) -> bool:
    return math.isclose(float(a), float(b), rel_tol=rel, abs_tol=ab)


# ------------------------------------------------------------------ one root ----
def audit_root(root: str, ths: list[dict], disc: dict, settle: dict, manifest: dict,
               marker: dict, trend: dict) -> dict:
    out: dict = {"root": root}
    cal = Cal(GROUP[root])
    ref = manifest["stores"][root]["ext2010"]
    pre = next(p for p in marker["preflight"] if p["root"] == root and p["era"] == "ext2010")
    bars = Bars(root, ref["path"], pre["sha256"])
    out["store"] = {"path": ref["path"], "sha256": bars.sha, **bars.meta,
                    "sha256_equals_marker_preflight": bars.sha == pre["sha256"]}
    costs = Costs(VEHICLE[root])
    tv = costs.tv

    def settle_minute(d: date) -> int | None:
        for r in settle["products"][root]["settle"]:
            if date.fromisoformat(r["from"]) <= d <= date.fromisoformat(r["to"]):
                return hhmm(r["minute_ct"])
        return None

    # marks
    marks = []  # (day, i, pt_close, price, ts, contract)
    window_days = [d for d in cal.days if START <= d <= W_LAST]
    for d in window_days:
        s = settle_minute(d)
        if s is None:
            continue
        if cal.closure_at(d, s):
            i = bars.bar(d, s - 1)
            if i is None:
                continue
            marks.append((d, i, True, int(bars.close_t[i]), int(bars.ts[i]), bars.contract(i)))
        else:
            i = bars.bar(d, s)
            if i is None:
                continue
            marks.append((d, i, False, int(bars.open_t[i]), int(bars.ts[i]), bars.contract(i)))
    mdays = [m[0] for m in marks]
    midx = {d: k for k, d in enumerate(mdays)}
    out["marks"] = {"count": len(marks), "first": str(mdays[0]), "last": str(mdays[-1]),
                    "pt_close_share": sum(1 for m in marks if m[2]) / len(marks),
                    "window_trade_dates": len(window_days)}

    def price_at(i: int, pt_close: bool) -> int:
        return int(bars.close_t[i] if pt_close else bars.open_t[i])

    # chained daily returns
    rets: list[tuple[date, float]] = []
    rcount: dict[str, int] = {}
    for k, (d, i, pc, price, ts, con) in enumerate(marks):
        prev = cal.previous(d)
        pk = midx.get(prev) if prev is not None else None
        if pk is None:
            rcount["previous mark missing"] = rcount.get("previous mark missing", 0) + 1
            continue
        pd_, pi, ppc, pprice, pts, pcon = marks[pk]
        start_price, start_i, ratio, ok = pprice, pi, 1.0, True
        for s in bars.splices_between(int(bars.ts[pi]), int(bars.ts[i])):
            i_out, i_in = bars.last_before(s), bars.first_at_or_after(s)
            if i_out is None or i_in is None or i_out < start_i or bars.contract(i_out) != bars.contract(start_i):
                ok = False
                break
            ratio *= int(bars.close_t[i_out]) / start_price
            start_price, start_i = int(bars.open_t[i_in]), i_in
        if not ok or bars.contract(i) != bars.contract(start_i) or start_price <= 0:
            rcount["undefined (roll/contract)"] = rcount.get("undefined (roll/contract)", 0) + 1
            continue
        rets.append((d, ratio * price / start_price - 1.0))
    out["returns"] = {"defined": len(rets), **rcount}

    # EWMA sigma strictly before each mark date
    delta = COM / (COM + 1.0)
    sigma: dict[date, float | None] = {}
    s0 = s1 = s2 = 0.0
    n_r, j = 0, 0
    for d in mdays:
        while j < len(rets) and rets[j][0] < d:
            r = rets[j][1]
            s0, s1, s2 = delta * s0 + 1.0, delta * s1 + r, delta * s2 + r * r
            n_r, j = n_r + 1, j + 1
        if n_r < WARMUP:
            sigma[d] = None
        else:
            mu = s1 / s0
            sigma[d] = math.sqrt(ANN * max(s2 / s0 - mu * mu, 0.0))

    # per-contract path: intervals[k] ends at marks[k]
    intervals: list[dict | None] = [None]
    for k in range(1, len(marks)):
        a, b = marks[k - 1], marks[k]
        t_a = a[4] + (NS_MIN if a[2] else 0)
        t_b = b[4] + (NS_MIN if b[2] else 0)
        contract, refp = a[5], a[3]
        incs, legs, fail = [], [], None
        for s in bars.splices_between(t_a, t_b):
            i_out, i_in = bars.last_before(s), bars.first_at_or_after(s)
            if i_out is None or i_in is None or i_out < a[1] or i_in > b[1]:
                fail = "missing roll bar"
                break
            if bars.contract(i_out) != contract or bars.contract(i_in) == contract:
                fail = "contract change"
                break
            d_out, d_in = date.fromordinal(int(bars.td[i_out])), date.fromordinal(int(bars.td[i_in]))
            incs.append((d_out, (int(bars.open_t[i_out]) - refp) * tv))
            legs.append(("roll_out", d_out, int(bars.ts[i_out]), int(bars.open_t[i_out])))
            legs.append(("roll_in", d_in, int(bars.ts[i_in]), int(bars.open_t[i_in])))
            contract, refp = bars.contract(i_in), int(bars.open_t[i_in])
        if fail is None and b[5] != contract:
            fail = "contract change"
        if fail is None:
            incs.append((b[0], (b[3] - refp) * tv))
        intervals.append({"incs": incs, "legs": legs, "fail": fail})
    out["path"] = {"intervals": len(intervals) - 1, "failed": sum(1 for iv in intervals if iv and iv["fail"]),
                   "roll_legs": sum(len(iv["legs"]) for iv in intervals if iv)}

    # buy-and-hold regressor (alpha3): per-contract move / notional at the opening mark
    bh: dict[date, float] = {}
    for k, iv in enumerate(intervals):
        if iv is None or iv["fail"]:
            continue
        p0 = marks[k - 1][3]
        if p0 <= 0:
            continue
        for day, cents in iv["incs"]:
            bh[day] = bh.get(day, 0.0) + cents / (p0 * tv)

    # eligibility
    def action_why(d: date) -> str | None:
        if not (START <= d <= W_LAST):
            return "outside window"
        if not cal.is_trade(d):
            return "not a trade date"
        if d in bars.blackout:
            return "roll blackout"
        if d in cal.halt:
            return "early halt"
        if d not in midx:
            return "missing bar (mark)"
        s = settle_minute(d)
        if bars.bar(d, s - 1) is None:
            return "missing bar (signal)"
        return None

    def fill_cost_at(k: int, side: str) -> tuple[int, int, bool]:
        return costs.per_side(marks[k][4], side)

    out["trigger_holds"] = {}
    for th in ths:
        tid, h, m = th["id"], th["h"], th["m"]
        run = disc["trigger_holds"][tid]
        ev = load(th["events"]["W_ext"])["events"]
        win_first = max(W_FIRST, mdays[0])
        units, uc, moved = [], {}, 0
        spot_excluded = {}

        def count(key):
            uc[key] = uc.get(key, 0) + 1

        for e in sorted(ev, key=lambda x: (x["d0"], x["tau_ns"])):
            count("events")
            d0 = date.fromisoformat(e["d0"])
            if not (win_first <= d0 <= W_LAST):
                count("excluded: event outside the window")
                continue
            s = settle_minute(d0)
            if s is not None and e["tau_ns"] < ct_ns(d0, s):
                d_e = d0
            else:
                kk = bisect_right(mdays, d0)
                d_e = mdays[kk] if kk < len(mdays) else None
                moved += 1
            if d_e is None:
                count("excluded: no mark date after d0")
                continue
            if not (win_first <= d_e <= W_LAST):
                count("excluded: entry outside the window (window edge)")
                continue
            why = action_why(d_e)
            if why:
                count(f"excluded: entry: {why}")
                spot_excluded.setdefault(f"entry: {why}", (str(d0), str(d_e), None))
                continue
            kx = midx[d_e] + h
            if kx >= len(mdays):
                count("excluded: exit: no h-th mark date")
                spot_excluded.setdefault("exit: no h-th mark date", (str(d0), str(d_e), None))
                continue
            d_x = mdays[kx]
            if not (win_first <= d_x <= W_LAST):
                count("excluded: exit outside the window (window edge)")
                continue
            why = action_why(d_x)
            if why:
                count(f"excluded: exit: {why}")
                spot_excluded.setdefault(f"exit: {why}", (str(d0), str(d_e), str(d_x)))
                continue
            units.append({"d0": d0, "d_e": d_e, "d_x": d_x, "u": e["side"] * m, "tau_ns": e["tau_ns"]})
            count("units")
        # non-overlapping (greedy)
        non, last_x = 0, None
        for un in sorted(units, key=lambda u: (u["d_e"], u["d_x"])):
            if last_x is None or un["d_e"] >= last_x:
                non += 1
                last_x = un["d_x"]
        # net path
        delta_u: dict[date, int] = {}
        for un in units:
            delta_u[un["d_e"]] = delta_u.get(un["d_e"], 0) + un["u"]
            delta_u[un["d_x"]] = delta_u.get(un["d_x"], 0) - un["u"]
        orders = []  # (day, target, kind, info)
        total, net = 0, 0
        bc: dict[str, int] = {}
        for d in sorted(delta_u):
            total += delta_u[d]
            new = max(-1, min(1, total))
            if new == net:
                continue
            kind = "open" if net == 0 else ("close" if new == 0 else "flip")
            bc[f"net changes: {kind}"] = bc.get(f"net changes: {kind}", 0) + 1
            target, info = 0.0, {}
            if new != 0:
                sg = sigma.get(d)
                price = marks[midx[d]][3]
                V = price * tv / 100.0
                info = {"sigma": sg, "price_ticks": price, "V_usd": V}
                if sg is None or sg <= 0:
                    bc["opening skipped: sigma undefined"] = bc.get("opening skipped: sigma undefined", 0) + 1
                elif V <= 0:
                    bc["opening skipped: non-positive notional"] = bc.get("opening skipped: non-positive notional", 0) + 1
                else:
                    bc["openings sized"] = bc.get("openings sized", 0) + 1
                    target = new * TARGET_VOL / sg / V
            orders.append((d, target, kind, info))
            net = new
        at = {midx[o[0]]: j for j, o in enumerate(orders)}
        # simulate
        gross: dict[date, float] = {}
        cost = {"base": {}, "stress": {}}
        fills: list[dict] = []
        n = 0.0
        backstop = 0
        hold_fail = 0
        for k in range(len(marks)):
            iv = intervals[k]
            if n != 0.0 and iv is not None:
                if iv["fail"]:
                    hold_fail += 1
                else:
                    for day, cents in iv["incs"]:
                        gross[day] = gross.get(day, 0.0) + n * cents / 100.0
                    for kind, day, ts, price in iv["legs"]:
                        side = ("sell" if n > 0 else "buy") if kind == "roll_out" else ("buy" if n > 0 else "sell")
                        b_, s_, unc = costs.per_side(ts, side)
                        cost["base"][day] = cost["base"].get(day, 0.0) + abs(n) * b_ / 100.0
                        cost["stress"][day] = cost["stress"].get(day, 0.0) + abs(n) * s_ / 100.0
                        fills.append({"date": str(day), "kind": kind, "trade": (-n if kind == "roll_out" else n),
                                      "base_c": b_, "stress_c": s_, "uncal": unc})
            j = at.get(k)
            if j is None:
                continue
            d, target, kind, info = orders[j]
            trade = target - n
            if trade != 0.0:
                side = "buy" if trade > 0 else "sell"
                b_, s_, unc = fill_cost_at(k, side)
                cost["base"][d] = cost["base"].get(d, 0.0) + abs(trade) * b_ / 100.0
                cost["stress"][d] = cost["stress"].get(d, 0.0) + abs(trade) * s_ / 100.0
                fills.append({"date": str(d), "kind": kind, "trade": trade, "base_c": b_, "stress_c": s_,
                              "uncal": unc, **{k2: (v if not isinstance(v, float) else v) for k2, v in info.items()}})
            n = target
        if n != 0.0:
            backstop += 1
        # series
        days = [d for d in mdays if win_first <= d <= W_LAST and units and d >= min(u["d_e"] for u in units)]
        grid = set(days)
        booked = set(gross) | set(cost["base"]) | set(cost["stress"])
        extra = {d for d in booked if d not in grid and days and days[0] <= d <= days[-1]}
        outside = {d for d in booked if days and (d < days[0] or d > days[-1])}
        grid |= extra
        mine = {}
        for case in ("base", "stress"):
            mine[case] = {d: gross.get(d, 0.0) - cost[case].get(d, 0.0) for d in sorted(grid)}
        cmp = {}
        for case in ("base", "stress"):
            run_s = {date.fromisoformat(d): v for d, v in run["series"][case]}
            common = sorted(set(run_s) & set(mine[case]))
            diffs = [(d, run_s[d], mine[case][d]) for d in common if not close(run_s[d], mine[case][d], 1e-9, 1e-12)]
            cmp[case] = {"run_n": len(run_s), "mine_n": len(mine[case]), "dates_equal": set(run_s) == set(mine[case]),
                         "max_abs_diff": max((abs(run_s[d] - mine[case][d]) for d in common), default=None),
                         "n_values_differ_gt_1e-9rel": len(diffs),
                         "first_diffs": [(str(d), a, b) for d, a, b in diffs[:5]],
                         "sum_run": sum(run_s.values()), "sum_mine": sum(mine[case].values())}
        # in-market fraction (units), fills by kind
        imf = sum(1 for d in days if max(-1, min(1, sum(u["u"] for u in units if u["d_e"] < d <= u["d_x"]))) != 0) / len(days)
        fbk: dict[str, int] = {}
        for f in fills:
            fbk[f["kind"]] = fbk.get(f["kind"], 0) + 1
        # alpha3 on my buy-hold regressor and the run's base series dates
        dates = [d for d, _ in run["series"]["base"]]
        y = np.array([v for _, v in run["series"]["base"]])
        x1 = np.array([trend["v_T1"].get(d, 0.0) for d in dates])
        x2 = np.array([trend["v_T2"].get(d, 0.0) for d in dates])
        x3 = np.array([bh.get(date.fromisoformat(d), 0.0) for d in dates])
        a3 = ols_hac(y, [x1, x2, x3], h)
        ra3 = run["cases"]["base"]["alpha3_descriptive"]
        a3cmp = {k2: {"run": ra3[k2], "mine": a3[k2], "match": close(ra3[k2], a3[k2])}
                 for k2 in ("alpha", "t_plain", "t_nw", "p_plain", "p_nw", "p_alpha", "r2")}
        a3cmp["beta3"] = {"run": ra3["betas"][2], "mine": a3["betas"][2], "match": close(ra3["betas"][2], a3["betas"][2])}
        ys = np.array([v for _, v in run["series"]["stress"]])
        a3s = ols_hac(ys, [x1, x2, x3], h)
        ra3s = run["cases"]["stress"]["alpha3_descriptive"]
        a3cmp["stress_t_nw"] = {"run": ra3s["t_nw"], "mine": a3s["t_nw"], "match": close(ra3s["t_nw"], a3s["t_nw"])}
        a3cmp["stress_alpha"] = {"run": ra3s["alpha"], "mine": a3s["alpha"], "match": close(ra3s["alpha"], a3s["alpha"])}
        # spot units
        run_base = {date.fromisoformat(d): v for d, v in run["series"]["base"]}
        run_stress = {date.fromisoformat(d): v for d, v in run["series"]["stress"]}
        us = sorted(units, key=lambda u: (u["d_e"], u["d_x"]))
        chosen = {"first": us[0], "last": us[-1]}
        for un in us:
            lo, hi = marks[midx[un["d_e"]]][4], marks[midx[un["d_x"]]][4]
            if bars.splices_between(lo, hi):
                chosen["spans_roll"] = un
                break
        flip_dates = [o[0] for o in orders if o[2] == "flip"]
        if flip_dates:
            fd = flip_dates[0]
            chosen["enters_at_first_flip"] = next(u for u in us if u["d_e"] == fd)
        open_dates = {o[0]: o for o in orders}

        def describe(un: dict) -> dict:
            d_e, d_x = un["d_e"], un["d_x"]
            ke = midx[d_e]
            tau_ct = datetime.fromtimestamp(un["tau_ns"] / 1e9, tz=ZoneInfo("UTC")).astimezone(CT)
            s = settle_minute(un["d0"])
            o = open_dates.get(d_e)
            nxt = mdays[ke + 1]
            rec = {"d0": str(un["d0"]), "tau_ct": tau_ct.strftime("%Y-%m-%d %H:%M"), "settle_minute_ct": f"{s // 60:02d}:{s % 60:02d}",
                   "tau_before_settle_open": un["tau_ns"] < ct_ns(un["d0"], s), "d_e": str(d_e), "d_x": str(d_x),
                   "marks_between": midx[d_x] - ke, "u": un["u"], "mark_price_ticks_d_e": marks[ke][3],
                   "mark_is_close_of_S-1": marks[ke][2], "sigma_d_e": sigma.get(d_e),
                   "n_returns_before_d_e": sum(1 for r in rets if r[0] < d_e),
                   "splices_in_hold": len(bars.splices_between(marks[ke][4], marks[midx[d_x]][4])),
                   "order_on_d_e": None if o is None else {"kind": o[2], "target_contracts_per_capital": o[1], **o[3]},
                   "run_value_d_e": {"base": run_base.get(d_e), "stress": run_stress.get(d_e)},
                   "mine_value_d_e": {"base": mine["base"].get(d_e), "stress": mine["stress"].get(d_e)},
                   "run_value_next": {"base": run_base.get(nxt), "stress": run_stress.get(nxt)},
                   "mine_value_next": {"base": mine["base"].get(nxt), "stress": mine["stress"].get(nxt)},
                   "run_value_d_x": {"base": run_base.get(d_x), "stress": run_stress.get(d_x)},
                   "mine_value_d_x": {"base": mine["base"].get(d_x), "stress": mine["stress"].get(d_x)}}
            if o is not None and o[1] != 0.0:
                side = "buy" if o[1] > 0 else "sell"
                b_, s_, unc = fill_cost_at(ke, side)
                rec["entry_cost_cents_per_side"] = {"base": b_, "stress": s_, "commission_side": costs.comm_side,
                                                    "stress_eq_comm_plus_2x_slip": s_ == costs.comm_side + 2 * (b_ - costs.comm_side)}
                rec["entry_day_value_is_cost_only"] = {
                    "expected_base": -abs(o[1]) * b_ / 100.0, "run_base": run_base.get(d_e),
                    "match": close(-abs(o[1]) * b_ / 100.0, run_base.get(d_e, float("nan")), 1e-9, 1e-15)}
                p1 = marks[ke + 1][3]
                iv1 = intervals[ke + 1]
                if iv1 and not iv1["fail"] and not iv1["legs"]:
                    exp_next = o[1] * (p1 - marks[ke][3]) * tv / 100.0 - cost["base"].get(nxt, 0.0)
                    rec["next_day_value_from_mark_move"] = {"expected_base": exp_next, "run_base": run_base.get(nxt),
                                                           "match": close(exp_next, run_base.get(nxt, float("nan")), 1e-9, 1e-15)}
            return rec

        spot = {name: describe(un) for name, un in chosen.items()}
        out["trigger_holds"][tid] = {
            "h": h, "m": m, "events": len(ev), "entries_moved_to_next_mark": moved,
            "unit_counts": {"run": run["unit_counts"], "mine": dict(sorted(uc.items())),
                            "match": run["unit_counts"] == dict(sorted(uc.items()))},
            "units": {"run": run["units"], "mine": len(units)},
            "nonoverlapping": {"run": run["nonoverlapping"], "mine": non},
            "n_dates": {"run": run["n_dates"], "mine": len(days)},
            "in_market_fraction": {"run": run["in_market_fraction_units"], "mine": imf,
                                   "match": close(run["in_market_fraction_units"], imf)},
            "book_counters": {"run": run["book_counters"], "mine": dict(sorted(bc.items()))},
            "fills_by_kind": {"run": {k2: v["fills"] for k2, v in run["fills_by_kind"].items()}, "mine": dict(sorted(fbk.items()))},
            "fills_total": {"run": run["fill_diagnostics"]["fills"], "mine": len(fills)},
            "uncalibrated_fills": sum(1 for f in fills if f["uncal"]),
            "gross_costs": {"run": run["gross_costs"], "mine": {c: {"gross": sum(gross.values()), "costs": sum(cost[c].values()),
                                                                   "net": sum(gross.values()) - sum(cost[c].values())} for c in ("base", "stress")}},
            "series_added_dates": len(extra), "series_outside_span": len(outside), "backstop_closes": backstop,
            "holds_over_failed_interval": hold_fail,
            "all_units_exit_h_marks_after_entry": all(midx[u["d_x"]] - midx[u["d_e"]] == h for u in units),
            "all_units_entry_eq_d0": all(u["d_e"] == u["d0"] for u in units),
            "series_compare": cmp, "alpha3": a3cmp, "spot_units": spot,
            "spot_excluded_examples": spot_excluded}
    del bars
    return out


def main(argv: list[str]) -> None:
    if subprocess.run(["pgrep", "-f", "pytest -q -p no:cacheprovider"], capture_output=True).returncode == 0:
        raise SystemExit("REFUSED: the pytest suite is running (lead's instruction)")
    avail = int(next(l for l in open("/proc/meminfo") if l.startswith("MemAvailable")).split()[1]) // 1024
    if avail < 4000:
        raise SystemExit(f"REFUSED: only {avail} MB available (< 4 GB)")
    os.nice(10)
    roots = argv or ["ZF", "ZN", "ZB", "NQ"]
    disc = load("reports/stage_e23_runs/discovery/discovery_result.json")
    reg = load("reports/stage_e23_registration.json")
    settle = load("reports/stage_e16_settlement.json")
    manifest = load("reports/stage_e17_run_manifest.json")
    marker = load("reports/stage_e23_RUN_ONCE_discovery.json")
    path = f"{OUT_DIR}/spot_audit.json"
    result = json.load(open(path)) if os.path.exists(path) else {}
    for root in roots:
        ths = [t for t in reg["trigger_holds"] if t["root"] == root]
        trend = load(f"reports/stage_e23_trend_per_root/{root}.json")
        t0 = datetime.now()
        result[root] = audit_root(root, ths, disc, settle, manifest, marker, trend)
        result[root]["elapsed_s"] = (datetime.now() - t0).total_seconds()
        result[root]["run_at_local"] = datetime.now(tz=ZoneInfo("America/Vancouver")).isoformat(timespec="seconds")
        with open(path, "w") as f:
            json.dump(result, f, indent=1, default=str)
        r = result[root]
        print(f"== {root}: marks {r['marks']['count']} ({r['marks']['first']}..{r['marks']['last']}), returns {r['returns']}, "
              f"path {r['path']}, store sha ok {r['store']['sha256_equals_marker_preflight']}, {r['elapsed_s']:.0f}s")
        for tid, t in r["trigger_holds"].items():
            print(f"   {tid}: units run/mine {t['units']}, nonoverlap {t['nonoverlapping']}, n_dates {t['n_dates']}, "
                  f"unit_counts match {t['unit_counts']['match']}, imf match {t['in_market_fraction']['match']}, "
                  f"fills {t['fills_total']}, moved {t['entries_moved_to_next_mark']}, uncal {t['uncalibrated_fills']}")
            for case in ("base", "stress"):
                c = t["series_compare"][case]
                print(f"      {case}: dates_equal {c['dates_equal']} n {c['run_n']}/{c['mine_n']} max_abs_diff {c['max_abs_diff']} "
                      f"differ {c['n_values_differ_gt_1e-9rel']} sum run {c['sum_run']:.9f} mine {c['sum_mine']:.9f} first {c['first_diffs'][:2]}")
            print(f"      alpha3: " + ", ".join(f"{k}={'ok' if v['match'] else 'DIFF'}" for k, v in t["alpha3"].items()))
            print(f"      book_counters run {t['book_counters']['run']} mine {t['book_counters']['mine']}")
            print(f"      fills_by_kind run {t['fills_by_kind']['run']} mine {t['fills_by_kind']['mine']}")
            if not t["unit_counts"]["match"]:
                print(f"      unit_counts run {t['unit_counts']['run']} mine {t['unit_counts']['mine']}")


if __name__ == "__main__":
    main(sys.argv[1:])
