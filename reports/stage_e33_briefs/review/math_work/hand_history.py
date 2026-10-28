"""History pass for the hand check of date D1: per-date summaries over the 20 trade dates before
D1 (burn-in included as history, 0.3): mids at the 279 marks 08:35..13:13 (ZM, ZS, ZL), |OFI_1|
at each mark (ZM top of book; ZS top of book), level 1..5 depth at each mark, V_ZM(15) at each
mark (wall-clock window), M_ZM at 08:35 and 13:15, crush C at 08:35 and 13:15.
Usage: uv run python hand_history.py D1 OUTDIR
"""
from __future__ import annotations

import json
import sys
import time

import numpy as np

import hand_replay as hr

D1 = sys.argv[1]
OUT = sys.argv[2]
NS_MIN = hr.NS_MIN
MARK_HHMM = [(8 * 60 + 35 + i) for i in range(279)]  # 08:35 .. 13:13 in minutes of day


def marks_ns(day) -> np.ndarray:
    return np.array([hr.ct(day, f"{m // 60:02d}:{m % 60:02d}:00") for m in MARK_HHMM], dtype=np.int64)


def ofi_terms(bid, ask, qb, qa, computable_pair):
    """e_n for n = 1..N-1 (CKS 2014 on consecutive updates); returns (e, computable)."""
    pb0, pb1, pa0, pa1 = bid[:-1], bid[1:], ask[:-1], ask[1:]
    e = ((pb1 >= pb0) * qb[1:] - (pb1 <= pb0) * qb[:-1]
         - (pa1 <= pa0) * qa[1:] + (pa1 >= pa0) * qa[:-1]).astype(np.float64)
    return e, computable_pair


def window_sum_at_marks(u_ts, e, comp, valid_pair, mk, k_min=1):
    """Variant A: sum of e over updates n with ts in (mark - k, mark]; NaN if any term in the
    window is not computable (A: both updates two-sided and not bad). Variant B: terms where both
    updates are valid (bid < ask) count, others are 0."""
    ts_n = u_ts[1:]  # the time of update n (the term e_n belongs to update n)
    lo = np.searchsorted(ts_n, mk - k_min * NS_MIN, side="right")
    hi = np.searchsorted(ts_n, mk, side="right")
    ce = np.concatenate([[0.0], np.cumsum(e)])
    cnc = np.concatenate([[0], np.cumsum(~comp)])
    eb = np.where(valid_pair, e, 0.0)
    ceb = np.concatenate([[0.0], np.cumsum(eb)])
    sum_a = ce[hi] - ce[lo]
    n_nc = cnc[hi] - cnc[lo]
    a = np.where(n_nc > 0, np.nan, sum_a)
    b = ceb[hi] - ceb[lo]
    return a, b, hi - lo


def one_date(day) -> dict:
    t0 = time.time()
    rep = hr.replay_zm(day)
    mk = marks_ns(day)
    u_ts, bid, ask = rep["u_ts"], rep["u_bid"], rep["u_ask"]
    two, valid = rep["u_two"], rep["u_valid"]
    idx = np.searchsorted(u_ts, mk, side="right") - 1
    ok = idx >= 0
    mid = np.full(279, np.nan)
    sel = ok & valid[np.maximum(idx, 0)]
    mid[sel] = (bid[idx[sel]] + ask[idx[sel]]) / 2.0
    # depth per level at marks where the mid is valid (missing level counts 0)
    depth = np.full((5, 279), np.nan)
    for m in range(5):
        depth[m, sel] = (rep["u_qb"][m][idx[sel]] + rep["u_qa"][m][idx[sel]]) / 2.0
    # OFI level 1 on the ZM top of book
    e, comp = ofi_terms(bid, ask, rep["u_qb"][0], rep["u_qa"][0], two[:-1] & two[1:])
    vpair = valid[:-1] & valid[1:]
    ofi_a, ofi_b, n_upd = window_sum_at_marks(u_ts, e, comp, vpair, mk)
    ofi5_a, ofi5_b, _ = window_sum_at_marks(u_ts, e, comp, vpair, mk, 5)
    ofi15_a, ofi15_b, _ = window_sum_at_marks(u_ts, e, comp, vpair, mk, 15)
    # V_ZM(15) at marks (wall clock; marks >= 08:50 never cross the pause)
    cs = np.concatenate([[0], np.cumsum(rep["t_sz"])])
    lo = np.searchsorted(rep["t_ts"], mk - 15 * NS_MIN, side="right")
    hi = np.searchsorted(rep["t_ts"], mk, side="right")
    v15 = (cs[hi] - cs[lo]).astype(np.float64)
    m0835 = hr.mid_asof(rep, hr.ct(day, "08:35:00"))
    m1315 = hr.mid_asof(rep, hr.ct(day, "13:15:00"))
    out = {"day": str(day), "iid": rep["iid"], "batch_mixed_ts": rep["batch_mixed_ts"],
           "anomalies": rep["anomalies"], "n_updates": int(len(u_ts)),
           "mid_zm": mid, "depth": depth, "ofi_zm1_a": ofi_a, "ofi_zm1_b": ofi_b,
           "ofi_zm5_a": ofi5_a, "ofi_zm5_b": ofi5_b, "ofi_zm15_a": ofi15_a, "ofi_zm15_b": ofi15_b,
           "n_upd_1min": n_upd, "v15": v15,
           "m0835": m0835, "m1315": m1315}
    # ZS and ZL (MBP-1): mids at marks and level-1 OFI (F_LAST updates; also all records)
    for root in ("ZS", "ZL"):
        m = hr.load_mbp1(root, day)
        for tag, mask in (("fl", m["last"]), ("all", np.ones(m["n"], dtype=bool))):
            ts, b, a = m["ts"][mask], m["bid"][mask], m["ask"][mask]
            qb, qa, tw, va = m["qb"][mask], m["qa"][mask], m["two"][mask] & ~m["bad"][mask], m["valid"][mask]
            j = np.searchsorted(ts, mk, side="right") - 1
            okj = j >= 0
            mm = np.full(279, np.nan)
            s2 = okj & va[np.maximum(j, 0)]
            mm[s2] = (b[j[s2]] + a[j[s2]]) / 2.0
            e2, c2 = ofi_terms(b, a, qb, qa, tw[:-1] & tw[1:])
            oa, ob, nu = window_sum_at_marks(ts, e2, c2, va[:-1] & va[1:], mk)
            oa5, ob5, _ = window_sum_at_marks(ts, e2, c2, va[:-1] & va[1:], mk, 5)
            out[f"mid_{root}_{tag}"] = mm
            out[f"ofi_{root}1_a_{tag}"] = oa
            out[f"ofi_{root}1_b_{tag}"] = ob
            out[f"ofi_{root}5_a_{tag}"] = oa5
            out[f"ofi_{root}5_b_{tag}"] = ob5
            out[f"n_upd_{root}_{tag}"] = nu
        out[f"iid_{root}"] = m["iid"]
        out[f"n_{root}_records"] = int(m["n"])
        out[f"n_{root}_flast"] = int(m["last"].sum())
    out["seconds"] = round(time.time() - t0, 2)
    return out


def main() -> None:
    import cal33
    hist = cal33.previous_trade_dates(D1, 20)
    assert len(hist) == 20, hist
    log = open(f"{OUT}/history_{D1}.log", "a")
    summary = []
    for day in hist:
        r = one_date(day)
        np.savez(f"{OUT}/hist_{day}.npz", **{k: v for k, v in r.items() if isinstance(v, np.ndarray)})
        meta = {k: v for k, v in r.items() if not isinstance(v, np.ndarray)}
        meta["n_valid_marks"] = int(np.isfinite(r["mid_zm"]).sum())
        meta["n_ofi_a_defined"] = int(np.isfinite(r["ofi_zm1_a"]).sum())
        meta["n_ZS_fl_valid_marks"] = int(np.isfinite(r["mid_ZS_fl"]).sum())
        meta["n_ZL_fl_valid_marks"] = int(np.isfinite(r["mid_ZL_fl"]).sum())
        summary.append(meta)
        log.write(json.dumps(meta) + "\n")
        log.flush()
    json.dump(summary, open(f"{OUT}/history_{D1}_summary.json", "w"), indent=1)
    log.write("DONE\n")
    log.close()


if __name__ == "__main__":
    main()
