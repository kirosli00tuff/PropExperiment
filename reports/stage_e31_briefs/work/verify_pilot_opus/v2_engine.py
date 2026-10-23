"""OpusVerifier step 2: independent model (c) check from the raw Z1 MBO file for one trade date.

Own minimal book (order map + price levels, best levels committed only after F_LAST records), own
trade list, own grid. Usage: v2_engine.py <key> where key is a key of sample_dates.json.
Writes v2_rows_<date>.parquet and v2_cmp_<date>.json beside itself. Reads the DBN file read-only.
"""
import heapq
import json
import os
import sys
from datetime import datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import databento as db
import databento_dbn as dbn

os.nice(10)
HERE = Path(__file__).resolve().parent
MEAS = Path("/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e31_briefs/work/pilot/runs/measure31")
CT = ZoneInfo("America/Chicago")
TICK = 100_000_000  # 0.10 USD in 1e-9 units
F_LAST, F_SNAP = int(dbn.F_LAST), int(dbn.F_SNAPSHOT)
F_BADBOOK, F_TOB, F_MBP = int(dbn.F_MAYBE_BAD_BOOK), int(dbn.F_TOB), int(dbn.F_MBP)
LAT = 50_000_000
LIFE = 60_000_000_000 + LAT
H10 = 10_000_000_000
CUTOFF = pd.Timestamp("2024-03-01", tz="UTC").value


def ct_ns(d, hh, mm):
    return pd.Timestamp(datetime.combine(d, time(hh, mm)), tz=CT).tz_convert("UTC").value


def as_u8(a):
    a = np.asarray(a)
    return a.view(np.uint8) if a.dtype.kind == "S" else a.astype(np.int64)


def front_instrument(store, d):
    for iv in store.mappings["ZM.v.0"]:
        if iv["start_date"] <= d < iv["end_date"]:
            return int(iv["symbol"])
    raise RuntimeError("no mapping")


def load_records(path, d):
    store = db.DBNStore.from_file(path)
    inst = front_instrument(store, d)
    lo = ct_ns(d - timedelta(days=1), 16, 0)
    hi = ct_ns(d, 16, 0)
    keep = []
    for ch in store.to_ndarray(count=2_000_000):
        tr = ch["ts_recv"]
        if tr[0] >= hi:
            break
        m = (ch["instrument_id"] == inst) & (tr >= lo) & (tr < hi)
        if m.any():
            keep.append(ch[m].copy())
    r = np.concatenate(keep)
    assert int(r["ts_event"].max()) < CUTOFF and int(r["ts_recv"].max()) < CUTOFF
    return inst, r


class Book:
    def __init__(self):
        self.clear()

    def clear(self):
        self.orders = {}
        self.lv = {66: {}, 65: {}}  # 'B' bids, 'A' asks: price -> qty
        self.hp = {66: [], 65: []}

    def _addq(self, side, px, q):
        lv = self.lv[side]
        old = lv.get(px, 0)
        new = old + q
        if new <= 0:
            lv.pop(px, None)
        else:
            lv[px] = new
            if old <= 0:
                heapq.heappush(self.hp[side], -px if side == 66 else px)

    def best(self, side):
        h, lv = self.hp[side], self.lv[side]
        while h:
            px = -h[0] if side == 66 else h[0]
            if lv.get(px, 0) > 0:
                return px, lv[px]
            heapq.heappop(h)
        return None, 0


def build(r):
    act, side = as_u8(r["action"]), as_u8(r["side"])
    cols = [r[c].tolist() for c in ("ts_event", "ts_recv", "price", "size", "order_id", "flags")]
    act, side = act.tolist(), side.tolist()
    bk = Book()
    started = False
    tmax = 0
    hist = []  # (t, rec_idx, bid, ask, bsz, asz)
    trades = []  # (t, rec_idx, price, side)
    cnt = {"pre_start": 0, "badbook_flag": 0, "tob_mbp_flag": 0, "unknown_cancel": 0, "dup_add": 0,
           "mod_unknown": 0, "trades_N": 0, "R": 0, "badbook_times": []}
    for i in range(len(act)):
        te, trv, px, sz, oid, fl = cols[0][i], cols[1][i], cols[2][i], cols[3][i], cols[4][i], cols[5][i]
        t = trv if fl & F_SNAP else te
        tmax = t if t > tmax else tmax
        a = act[i]
        if a == 82:  # R
            bk.clear(); started = True; cnt["R"] += 1
        if not started:
            cnt["pre_start"] += 1
            continue
        if fl & F_BADBOOK:
            cnt["badbook_flag"] += 1
            if len(cnt["badbook_times"]) < 50:
                cnt["badbook_times"].append(tmax)
        if fl & (F_TOB | F_MBP):
            cnt["tob_mbp_flag"] += 1
        s = side[i]
        if a == 65:  # A
            if oid in bk.orders:
                cnt["dup_add"] += 1
                os_, op, oq = bk.orders[oid]; bk._addq(os_, op, -oq)
            bk.orders[oid] = (s, px, sz); bk._addq(s, px, sz)
        elif a == 67:  # C
            o = bk.orders.get(oid)
            if o is None:
                cnt["unknown_cancel"] += 1
            else:
                os_, op, oq = o
                nq = oq - sz
                bk._addq(os_, op, -min(sz, oq))
                if nq <= 0:
                    del bk.orders[oid]
                else:
                    bk.orders[oid] = (os_, op, nq)
        elif a == 77:  # M
            o = bk.orders.get(oid)
            if o is None:
                cnt["mod_unknown"] += 1
            else:
                bk._addq(o[0], o[1], -o[2])
            bk.orders[oid] = (s, px, sz); bk._addq(s, px, sz)
        elif a == 84:  # T
            if s in (65, 66):
                trades.append((tmax, i, px, s))
            else:
                cnt["trades_N"] += 1
        if fl & F_LAST:
            b, bq = bk.best(66)
            k, kq = bk.best(65)
            if not hist or hist[-1][2:] != (b, k, bq, kq):
                hist.append((tmax, i, b, k, bq, kq))
    return hist, trades, cnt


def loop_c(d, hist, ht, tt, tp):
    """Section 6 loop under model (c), own reading: replacement decided at j + 60 s, joins at j + 60.05 s."""
    t_dec, end, close = ct_ns(d, 8, 35), ct_ns(d, 13, 15), ct_ns(d, 13, 20)
    rts = entries = placed = 0
    side_entry, in_pos = 1, False
    while t_dec < end:
        j = t_dec + LAT
        k = np.searchsorted(ht, j, side="right") - 1
        if k < 0 or not valid(hist[k][2], hist[k][3]):
            nxt = [x for x in range(k + 1, len(hist)) if valid(hist[x][2], hist[x][3])]
            if not nxt:
                break
            t_dec = int(ht[nxt[0]]); continue
        s = -side_entry if in_pos else side_entry
        p = hist[k][2] if s == 1 else hist[k][3]
        c = min(j + LIFE, close)
        placed += 1
        lo_ = np.searchsorted(tt, j, side="right"); hi2 = np.searchsorted(tt, c, side="left")
        seg = tp[lo_:hi2]
        hit = np.nonzero(seg < p)[0] if s == 1 else np.nonzero(seg > p)[0]
        if len(hit) == 0:
            t_dec = j + 60_000_000_000; continue
        tf = int(tt[lo_ + hit[0]])
        if not in_pos:
            in_pos = True; entries += 1
        else:
            in_pos = False; rts += 1; side_entry = -side_entry
        t_dec = tf
    return {"round_trips": rts, "entries_filled": entries, "orders_placed": placed}


def valid(b, k):
    return b is not None and k is not None and b < k


def run(key):
    sd = json.loads((HERE / "sample_dates.json").read_text())
    dstr = sd["dates"][key]
    path = sd["z1"][key][0]
    d = datetime.strptime(dstr, "%Y-%m-%d").date()
    inst, r = load_records(path, d)
    hist, trades, cnt = build(r)
    ht = np.array([h[0] for h in hist], dtype=np.int64)
    hi_ = np.array([h[1] for h in hist], dtype=np.int64)
    tt = np.array([t[0] for t in trades], dtype=np.int64)
    ti = np.array([t[1] for t in trades], dtype=np.int64)
    tp = np.array([t[2] for t in trades], dtype=np.int64)
    rows = []
    g = ct_ns(d, 8, 35)
    gend = ct_ns(d, 13, 10)
    while g <= gend:
        j = g + LAT
        c = j + LIFE
        k = np.searchsorted(ht, j, side="right") - 1
        b, a = (hist[k][2], hist[k][3]) if k >= 0 else (None, None)
        for s in (1, -1):
            row = {"g_ns": g, "side": s, "valid_join": valid(b, a), "t_fill_ns": -1}
            if not row["valid_join"]:
                rows.append(row); continue
            p = b if s == 1 else a
            row["price_i"] = p
            lo_ = np.searchsorted(tt, j, side="right")
            hi2 = np.searchsorted(tt, c, side="left")
            seg = tp[lo_:hi2]
            hit = np.nonzero(seg < p)[0] if s == 1 else np.nonzero(seg > p)[0]
            if len(hit) == 0:
                row["filled"] = False
            else:
                q = lo_ + hit[0]
                tf, rec = int(tt[q]), int(ti[q])
                row.update(filled=True, t_fill_ns=tf, fill_px=int(tp[q]))
                m0 = np.searchsorted(hi_, rec, side="left") - 1
                hb, ha = hist[m0][2], hist[m0][3]
                row["mid0"] = (hb + ha) / 2 / 1e9 if valid(hb, ha) else np.nan
                kk = np.searchsorted(ht, tf + H10, side="right") - 1
                inval = False
                while kk >= 0 and not valid(hist[kk][2], hist[kk][3]):
                    kk -= 1; inval = True
                # invalid states strictly inside (tf, tf+10s]
                k1 = np.searchsorted(ht, tf, side="right")
                k2 = np.searchsorted(ht, tf + H10, side="right")
                inval_h = any(not valid(hist[x][2], hist[x][3]) for x in range(k1, k2))
                mid10 = (hist[kk][2] + hist[kk][3]) / 2
                row["E10_nodrop"] = s * (mid10 - p) / TICK
                row["horizon_invalid"] = bool(inval or inval_h)
            rows.append(row)
        g += 5 * 60 * 1_000_000_000
    mine = pd.DataFrame(rows)
    lp_mine = loop_c(d, hist, ht, tt, tp)
    mine.to_parquet(HERE / f"v2_rows_{dstr}.parquet", index=False)
    cnt["badbook_times_ct"] = [str(pd.Timestamp(x, tz="UTC").tz_convert(CT)) for x in cnt.pop("badbook_times")]
    return compare(dstr, inst, mine, cnt, len(r), len(hist), len(trades), lp_mine)


def compare(dstr, inst, mine, cnt, nrec, nhist, ntr, lp_mine):
    pl = pq.read_table(MEAS / dstr / "placements.parquet").to_pandas()
    pl = pl[(pl.session == "DAY") & (pl.symbol == "ZM.v.0") & (pl.model == "c")].copy()
    dy = pq.read_table(MEAS / dstr / "days.parquet").to_pandas()
    prod_inst = int(dy[dy.symbol == "ZM.v.0"].instrument_id.iloc[0])
    m = mine.merge(pl, on=["g_ns", "side"], how="outer", indicator=True, suffixes=("_v", "_p"))
    both = m[m._merge == "both"].copy()
    out = {"date": dstr, "instrument_raw": inst, "instrument_producer": prod_inst,
           "records_window": nrec, "bbo_changes": nhist, "trades_AB": ntr, "counts": cnt,
           "mine_rows": int(len(mine)), "mine_valid_joins": int(mine.valid_join.sum()),
           "producer_rows": int(len(pl)), "only_mine": int((m._merge == "left_only").sum()),
           "only_producer": int((m._merge == "right_only").sum()), "matched": int(len(both))}
    both["price_ok"] = np.abs(both.price_i / 1e9 - both.price) < 1e-9
    both["filled_v"] = both.filled_v.fillna(False).astype(bool)
    both["fill_ok"] = both.filled_v == both.filled_p
    fb = both[both.filled_v & both.filled_p].copy()
    fb["tf_ok"] = fb.t_fill_ns_v.astype("int64") == fb.t_fill_ns_p.astype("int64")
    fb["E10_p"] = fb.mo_10 + fb.c_half
    fb["E10nd_p"] = fb.mo_nd_10 + fb.c_half
    fb["E10_ok"] = np.abs(fb.E10_nodrop - fb.E10_p) < 1e-6
    fb["E10nd_ok"] = np.abs(fb.E10_nodrop - fb.E10nd_p) < 1e-6
    fb["mid0_ok"] = np.abs(fb.mid0_v - fb.mid0_p) < 1e-9
    out.update(price_match=int(both.price_ok.sum()), fill_flag_match=int(both.fill_ok.sum()),
               fills_mine=int(both.filled_v.sum()), fills_producer=int(both.filled_p.sum()),
               both_filled=int(len(fb)), t_fill_match=int(fb.tf_ok.sum()),
               E10_drop_match=int(fb.E10_ok.sum()), E10_nodrop_match=int(fb.E10nd_ok.sum()),
               mid0_match=int(fb.mid0_ok.sum()), horizon_invalid_mine=int(fb.horizon_invalid.sum()),
               mean_E10_mine=float(fb.E10_nodrop.mean()) if len(fb) else None,
               mean_E10_producer=float(fb.E10_p.mean()) if len(fb) else None)
    bad = both[~(both.price_ok & both.fill_ok)]
    out["examples_price_or_fill"] = bad[["g_ns", "side", "price_i", "price", "filled_v", "filled_p",
                                         "t_fill_ns_v", "t_fill_ns_p"]].head(8).astype(str).to_dict("records")
    badf = fb[~(fb.tf_ok & fb.E10_ok & fb.E10nd_ok)]
    out["examples_fill_values"] = badf[["g_ns", "side", "t_fill_ns_v", "t_fill_ns_p", "E10_nodrop", "E10_p",
                                        "E10nd_p", "mid0_v", "mid0_p"]].head(8).astype(str).to_dict("records")
    lp = pq.read_table(MEAS / dstr / "loop.parquet").to_pandas()
    lp = lp[(lp.symbol == "ZM.v.0") & (lp.model == "c")]
    out["loop_mine"] = lp_mine
    out["loop_producer"] = lp[["round_trips", "entries_filled", "orders_placed"]].iloc[0].astype(int).to_dict() if len(lp) else None
    (HERE / f"v2_cmp_{dstr}.json").write_text(json.dumps(out, indent=1, default=str))
    keys = ["date", "instrument_raw", "instrument_producer", "mine_valid_joins", "producer_rows", "matched",
            "only_mine", "only_producer", "price_match", "fill_flag_match", "fills_mine", "fills_producer",
            "both_filled", "t_fill_match", "E10_drop_match", "E10_nodrop_match", "mid0_match",
            "horizon_invalid_mine", "loop_mine", "loop_producer"]
    print({k: out[k] for k in keys})
    print("counts", {k: v for k, v in cnt.items() if k != "badbook_times_ct"}, cnt["badbook_times_ct"][:3])
    return out


if __name__ == "__main__":
    run(sys.argv[1])
