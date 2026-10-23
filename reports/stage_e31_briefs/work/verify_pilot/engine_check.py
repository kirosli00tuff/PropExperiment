"""PilotVerifier step 2: independent re-derivation of model (c) fills and E_10 from raw Z1 MBO records.

Own minimal book (no producer code used). Input: raw_extract/<T>.parquet (records of the ZM.v.0 instrument
for the UTC date T, from 23:55Z on T-1 to 19:30Z on T, in file order). Output: per-day comparison.

Conventions (from the spec text, stated before any comparison):
- replay starts at the synthetic 00:00:00Z clear (action R, flags SNAPSHOT) of the UTC date T;
- action A adds, C reduces/removes, M re-prices/re-sizes; T, F and N do not change the book
  (checked empirically below: zero anomalies under this reading);
- the book is read only after a record carrying F_LAST (128); the state history has one entry per such record;
- time axis = running max of ts_event over file order;
- grid g = 08:35..13:10 CT every 5 min; j = g + 50 ms; book at j = last history entry with t <= j;
  p = best bid (buy) / best ask (sell) at j; window = (j, j + 60 s + 50 ms];
- fill = first T record with aggressor side A or B, price strictly through p (buy: price < p; sell: price > p);
- mid0 = mid of the last completed state when the T record is read; c = s (mid0 - p)/tick;
- E_10 = s (mid(t_f + 10 s) - p)/tick, mid(t) from the last history entry with t <= t_f + 10 s
  (drop variant: NaN if that state is crossed/locked/one-sided; no-drop variant: last valid state at or before).
"""
from __future__ import annotations

import bisect
import heapq
import json
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
MEAS = ROOT / "reports/stage_e31_briefs/work/pilot/runs/measure31"

TICK = 100_000_000  # 0.10 USD in 1e-9 fixed units
F_LAST = 128
HORIZON_NS = 10_000_000_000
LATENCY_NS = 50_000_000
CANCEL_NS = 60_000_000_000
CHI = ZoneInfo("America/Chicago")
UTC = ZoneInfo("UTC")


@dataclass
class Book:
    orders: dict = field(default_factory=dict)  # id -> [side, price, size]
    lv: dict = field(default_factory=lambda: {"B": {}, "A": {}})
    hb: list = field(default_factory=list)  # max-heap via negative price
    ha: list = field(default_factory=list)
    anomalies: dict = field(default_factory=lambda: {
        "c_unknown": 0, "c_over": 0, "c_partial": 0, "c_full": 0, "c_price_mismatch": 0,
        "m_unknown": 0, "m_resize_up": 0, "m_same_price_down": 0, "m_reprice": 0, "a_dup": 0,
        "m_side_mismatch": 0})

    def _lv_add(self, side, price, size):
        d = self.lv[side]
        if price in d:
            d[price] += size
        else:
            d[price] = size
            heapq.heappush(self.hb, -price) if side == "B" else heapq.heappush(self.ha, price)

    def _lv_sub(self, side, price, size):
        d = self.lv[side]
        left = d[price] - size
        if left <= 0:
            del d[price]
        else:
            d[price] = left

    def clear(self):
        self.orders.clear(); self.lv["B"].clear(); self.lv["A"].clear(); self.hb.clear(); self.ha.clear()

    def add(self, oid, side, price, size):
        if oid in self.orders:
            self.anomalies["a_dup"] += 1
            o = self.orders.pop(oid)
            self._lv_sub(o[0], o[1], o[2])
        self.orders[oid] = [side, price, size]
        self._lv_add(side, price, size)

    def cancel(self, oid, price, size):
        o = self.orders.get(oid)
        if o is None:
            self.anomalies["c_unknown"] += 1
            return
        if o[1] != price:
            self.anomalies["c_price_mismatch"] += 1
        if size > o[2]:
            self.anomalies["c_over"] += 1
        if size >= o[2]:
            self.anomalies["c_full"] += 1
            self._lv_sub(o[0], o[1], o[2])
            del self.orders[oid]
        else:
            self.anomalies["c_partial"] += 1
            self._lv_sub(o[0], o[1], size)
            o[2] -= size

    def modify(self, oid, side, price, size):
        o = self.orders.get(oid)
        if o is None:
            self.anomalies["m_unknown"] += 1
            self.add(oid, side, price, size)
            return
        if o[0] != side:
            self.anomalies["m_side_mismatch"] += 1
        if o[1] == price:
            if size > o[2]:
                self.anomalies["m_resize_up"] += 1
            else:
                self.anomalies["m_same_price_down"] += 1
        else:
            self.anomalies["m_reprice"] += 1
        self._lv_sub(o[0], o[1], o[2])
        o[0], o[1], o[2] = side, price, size
        self._lv_add(side, price, size)

    def best(self):
        d = self.lv["B"]
        while self.hb and -self.hb[0] not in d:
            heapq.heappop(self.hb)
        bid = -self.hb[0] if self.hb else 0
        d = self.lv["A"]
        while self.ha and self.ha[0] not in d:
            heapq.heappop(self.ha)
        ask = self.ha[0] if self.ha else 0
        return bid, ask


def replay(X: pd.DataFrame, T: str):
    """Return history arrays (t, bid, ask), trades arrays, book anomaly counts."""
    t0 = pd.Timestamp(T, tz="UTC").value
    ts_recv = X.ts_recv.to_numpy()
    act = X.action.to_numpy().astype(str)
    side = X.side.to_numpy().astype(str)
    price = X.price.to_numpy().astype("int64")
    size = X["size"].to_numpy().astype("int64")
    oid = X.order_id.to_numpy().astype("int64")
    flg = X["flags"].to_numpy().astype("int64")
    tev = X.ts_event.to_numpy().astype("int64")
    r_idx = np.flatnonzero((act == "R") & (ts_recv == t0))
    assert len(r_idx) == 1, f"{T}: expected exactly one 00:00Z clear, found {len(r_idx)}"
    start = int(r_idx[0])
    act, side, price, size, oid, flg, tev = (v.tolist() for v in (act, side, price, size, oid, flg, tev))
    book = Book()
    ht, hb_, ha_ = [], [], []
    tr_t, tr_p, tr_s, tr_sz, tr_state = [], [], [], [], []
    mono = tev[start]
    n_inv = 0
    for i in range(start, len(act)):
        te = tev[i]
        if te < mono:
            n_inv += 1
        else:
            mono = te
        a = act[i]
        if a == "A":
            book.add(oid[i], side[i], price[i], size[i])
        elif a == "C":
            book.cancel(oid[i], price[i], size[i])
        elif a == "M":
            book.modify(oid[i], side[i], price[i], size[i])
        elif a == "R":
            book.clear()
        elif a == "T":
            tr_t.append(mono); tr_p.append(price[i]); tr_s.append(side[i]); tr_sz.append(size[i])
            tr_state.append(len(ht) - 1)  # last completed state when the trade is read
        # F and N: no book effect
        if flg[i] & F_LAST:
            b, k = book.best()
            ht.append(mono); hb_.append(b); ha_.append(k)
    H = dict(t=np.array(ht, dtype="int64"), bid=np.array(hb_, dtype="int64"), ask=np.array(ha_, dtype="int64"))
    TR = dict(t=np.array(tr_t, dtype="int64"), p=np.array(tr_p, dtype="int64"), s=np.array(tr_s),
              sz=np.array(tr_sz, dtype="int64"), st=np.array(tr_state, dtype="int64"))
    return H, TR, book.anomalies, n_inv, int(start)


def grid_ns(T: str):
    d = date.fromisoformat(T)
    out = []
    g = datetime.combine(d, time(8, 35), tzinfo=CHI)
    end = datetime.combine(d, time(13, 10), tzinfo=CHI)
    while g <= end:
        out.append(int(g.astimezone(UTC).timestamp()) * 1_000_000_000)
        g += timedelta(minutes=5)
    return out


def valid_state(H, k):
    return k >= 0 and H["bid"][k] > 0 and H["ask"][k] > 0 and H["bid"][k] < H["ask"][k]


def mid_ticks_x2(H, k):
    return int(H["bid"][k] + H["ask"][k])  # 2 x mid, fixed units


def day_placements(T: str, X: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    H, TR, anom, n_inv, start = replay(X, T)
    rows = []
    n_state_invalid_total = int(sum(1 for k in range(len(H["t"])) if not valid_state(H, k)))
    for g in grid_ns(T):
        j = g + LATENCY_NS
        end = j + CANCEL_NS + LATENCY_NS
        kj = bisect.bisect_right(H["t"], j) - 1
        for s in (+1, -1):
            row = dict(trade_date=T, g_ns=g, side=s, j_ns=j)
            if not valid_state(H, kj):
                row.update(mine_valid_join=False)
                rows.append(row)
                continue
            p = int(H["bid"][kj]) if s == 1 else int(H["ask"][kj])
            row.update(mine_valid_join=True, mine_price=p, mine_bid_j=int(H["bid"][kj]), mine_ask_j=int(H["ask"][kj]))
            lo = bisect.bisect_right(TR["t"], j)
            hi = bisect.bisect_right(TR["t"], end)
            hit = None
            ties = 0
            for q in range(lo, hi):
                if TR["s"][q] not in ("A", "B"):
                    continue
                through = TR["p"][q] < p if s == 1 else TR["p"][q] > p
                if through:
                    hit = q
                    break
            # tie sensitivity: a through trade exactly at j (excluded here) or exactly at the window end (included)
            for q in np.flatnonzero(TR["t"] == j):
                if TR["s"][q] in ("A", "B") and ((TR["p"][q] < p) if s == 1 else (TR["p"][q] > p)):
                    ties += 1
            row.update(mine_filled=hit is not None, mine_tie_at_j=ties)
            if hit is not None:
                tf = int(TR["t"][hit])
                k0 = int(TR["st"][hit])
                row.update(mine_t_fill=tf, mine_trade_price=int(TR["p"][hit]), mine_trade_side=str(TR["s"][hit]),
                           mine_wait_s=(tf - j) / 1e9, mine_at_window_end=bool(tf == end))
                if valid_state(H, k0):
                    row["mine_c_half"] = s * (mid_ticks_x2(H, k0) / 2.0 - p) / TICK
                else:
                    row["mine_c_half"] = np.nan
                kh = bisect.bisect_right(H["t"], tf + HORIZON_NS) - 1
                row["mine_E10_drop"] = (s * (mid_ticks_x2(H, kh) / 2.0 - p) / TICK) if valid_state(H, kh) else np.nan
                kk = kh
                while kk >= 0 and not valid_state(H, kk):
                    kk -= 1
                row["mine_E10_nodrop"] = (s * (mid_ticks_x2(H, kk) / 2.0 - p) / TICK) if kk >= 0 else np.nan
                # any invalid state inside (t_f, t_f+10s]
                a = bisect.bisect_right(H["t"], tf)
                b = bisect.bisect_right(H["t"], tf + HORIZON_NS)
                row["mine_invalid_in_horizon"] = int(sum(1 for q in range(a, b) if not valid_state(H, q)))
            rows.append(row)
    info = dict(T=T, anomalies=anom, ts_event_inversions=n_inv, start_record=start, n_states=int(len(H["t"])),
                n_states_invalid=n_state_invalid_total, n_trades=int(len(TR["t"])),
                trades_side_counts={k: int(v) for k, v in pd.Series(TR["s"]).value_counts().items()})
    return pd.DataFrame(rows), info


def compare(T: str, mine: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    pl = pd.read_parquet(MEAS / T / "placements.parquet")
    pl = pl[(pl.symbol == "ZM.v.0") & (pl.session == "DAY") & (pl.model == "c")].copy()
    pl["trade_date"] = pl.trade_date.astype(str)
    pl["prod_E10_drop"] = pl.mo_10 + pl.c_half
    pl["prod_E10_nodrop"] = pl.mo_nd_10 + pl.c_half
    m = mine.merge(pl[["trade_date", "g_ns", "side", "j_ns", "price", "filled", "t_fill_ns", "trigger", "wait_s",
                       "c_half", "prod_E10_drop", "prod_E10_nodrop", "stale", "instrument_id", "raw_symbol"]],
                   on=["trade_date", "g_ns", "side"], how="outer", suffixes=("", "_prod"), indicator=True)
    return m, {}


def main(dates: list[str]):
    out = {}
    for T in dates:
        X = pd.read_parquet(HERE / "raw_extract" / f"{T}.parquet")
        mine, info = day_placements(T, X)
        m, _ = compare(T, mine)
        m.to_parquet(HERE / f"engine_rows_{T}.parquet")
        out[T] = dict(info=info)
        print(T, "rows", len(m), "merge", m._merge.value_counts().to_dict(), "anom", info["anomalies"],
              "invalid states", info["n_states_invalid"], "of", info["n_states"])
    (HERE / "engine_info.json").write_text(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main(sys.argv[1:] or list(json.load(open(HERE / "picked_dates.json")).values()))
