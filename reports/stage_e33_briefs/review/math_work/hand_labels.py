"""Hand recomputation of labels (P3.2-P3.7) on chosen dates and minutes, step by step.
Label values are written only to labels_work.txt and compared row by row (INTERFACE rule 1);
no statistic of labels is computed anywhere.
"""
from __future__ import annotations

import json
import math

import numpy as np

import hand_replay as hr

OUT = "/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e33_briefs/review/math_work"
TICK = 100_000_000
L = 1_000_000_000
F = 0.528
NS_MIN = hr.NS_MIN
log = open(f"{OUT}/labels_work.txt", "w")
res: dict = {}


def p(*a):
    print(*a, file=log)
    log.flush()


def limits_asof_0830(day, iid) -> tuple | None:
    """P3.6 rule 5: HL, LL of the front's last definition record with ts_recv <= 08:30:00 CT."""
    import data33
    d = data33.definitions(outright_only=True)
    cut = hr.ct(day, "08:30:00")
    sel = d[(d["instrument_id"] == iid) & (d["ts_recv"] <= cut)]
    if len(sel) == 0:
        return None
    r = sel[-1]
    hl, ll = int(r["high_limit_price"]), int(r["low_limit_price"])
    p(f"  limits as of 08:30 on {day}: record ts_recv {int(r['ts_recv'])} HL {hl} LL {ll} (n candidate records {len(sel)})")
    if hl == hr.UNDEF or ll == hr.UNDEF or hl == 0 or ll == 0:
        return None
    return hl, ll


def grid(day, h: int):
    n = 278 - h  # i = 0..277-h
    return [(i, hr.ct(day, "08:35:00") + i * NS_MIN) for i in range(n)]


def fh_date(day, h: int, releases, excluded: bool, limits) -> dict:
    """Every grid minute of an FH label: entry_ok, row_ok, y, n_long, n_short, span_end, w."""
    rep = hr.replay_zm(day)
    u_ts, bid, ask, two, valid = rep["u_ts"], rep["u_bid"], rep["u_ask"], rep["u_two"], rep["u_valid"]
    rows = {}
    for i, t in grid(day, h):
        end = t + L + h * NS_MIN
        r = {"i": i, "t": t, "span_end": end}
        # rules known at t
        rule1 = t >= hr.ct(day, "08:35:00")
        rule2 = end <= hr.ct(day, "13:13:00")
        rule3 = all(not (t <= R + 30 * NS_MIN and end >= R - 2 * NS_MIN) for R in releases)  # closed window
        rule4 = not excluded
        k = hr.asof_index(u_ts, t)
        book_t = k >= 0 and bool(two[k])
        m_t = hr.mid_asof(rep, t)
        if limits is None:
            rule5_lim = True
        elif m_t is None:
            rule5_lim = False  # the distance to the limit cannot be shown clear
        else:
            hl, ll = limits
            s2 = int(bid[k]) + int(ask[k])
            rule5_lim = not (50 * s2 >= 99 * hl - ll or 50 * s2 <= 101 * ll + hl)
        r["entry_ok"] = bool(rule1 and rule2 and rule3 and rule4 and book_t and rule5_lim)
        r["rule3_hit"] = not rule3
        r["rule5_lim_hit"] = not rule5_lim
        # row rule: every update in [t, end] two-sided and not bad; valid M_ZM(t)
        lo = np.searchsorted(u_ts, t, side="left")
        hi = np.searchsorted(u_ts, end, side="right")
        locked = not bool(two[lo:hi].all())
        r["row_ok"] = bool(r["entry_ok"] and m_t is not None and not locked)
        r["locked_hit"] = locked
        if r["row_ok"]:
            b0, a0, _, _ = hr.touch_asof(rep, t + L)
            b1, a1, _, _ = hr.touch_asof(rep, end)
            nl = (b1 - a0) / TICK - F
            ns = (b0 - a1) / TICK - F
            r.update(n_long=nl, n_short=ns, y=(1 if nl > 0 else (-1 if ns > 0 else 0)),
                     ask_tL=a0, bid_tL=b0, bid_end=b1, ask_end=a1,
                     mid_move=((b1 + a1) - (b0 + a0)) / 2 / TICK)
        rows[i] = r
    # P3.7 weights: clock-minute intervals; a span [t, t + h + L] overlaps h intervals by > 1 s
    c = {}
    for i, r in rows.items():
        if r["row_ok"]:
            for m in range(i, i + h):
                c[m] = c.get(m, 0) + 1
    for i, r in rows.items():
        if r["row_ok"]:
            r["w"] = math.fsum(1.0 / c[m] for m in range(i, i + h)) / h
            r["c_m"] = [c[m] for m in range(i, i + h)]
    rows["_rep"] = rep
    return rows


def tb_row(rep, day, t: int, h: int, sigma: float) -> dict:
    """P3.4 triple barrier at one minute (exact form: S_u - S_0 >= 2b with S = bid + ask in ticks)."""
    u_ts, bid, ask, valid, two = rep["u_ts"], rep["u_bid"], rep["u_ask"], rep["u_valid"], rep["u_two"]
    k0 = hr.asof_index(u_ts, t + L)
    assert k0 >= 0 and valid[k0], "m0 undefined"
    s0 = (int(bid[k0]) + int(ask[k0])) / TICK
    b = 1.0 * sigma * math.sqrt(h)
    vert = t + L + h * NS_MIN
    lo = np.searchsorted(u_ts, t + L, side="right")  # updates in (t + L, t + L + h]
    hi = np.searchsorted(u_ts, vert, side="right")
    tau_up = tau_dn = None
    n_undef = 0
    for u in range(lo, hi):
        if not valid[u]:
            n_undef += 1
            continue
        su = (int(bid[u]) + int(ask[u])) / TICK
        if tau_up is None and su - s0 >= 2 * b:
            tau_up = int(u_ts[u])
        if tau_dn is None and s0 - su >= 2 * b:
            tau_dn = int(u_ts[u])
        if tau_up is not None or tau_dn is not None:
            break
    cands = [(vert, 0)] + ([(tau_up, 1)] if tau_up else []) + ([(tau_dn, -1)] if tau_dn else [])
    tau, y = min(cands)
    b0, a0, _, _ = hr.touch_asof(rep, t + L)
    b1, a1, _, _ = hr.touch_asof(rep, tau + L)
    nl = (b1 - a0) / TICK - F
    ns = (b0 - a1) / TICK - F
    # row rule (locked book) over the union span [t, max(t + L + h, tau + L)] and over [t, t + L + h]
    lo2 = np.searchsorted(u_ts, t, side="left")
    hi_u = np.searchsorted(u_ts, max(vert, tau + L), side="right")
    hi_p = np.searchsorted(u_ts, vert, side="right")
    return {"t": t, "m0_ticks": s0 / 2, "b": b, "n_updates_scanned": hi - lo, "n_undefined_skipped": n_undef,
            "tau_up": tau_up, "tau_dn": tau_dn, "tau": tau, "y": y, "n_long": nl, "n_short": ns,
            "span_end": tau + L, "ask_tL": a0, "bid_tL": b0, "bid_tauL": b1, "ask_tauL": a1,
            "locked_union": not bool(two[lo2:hi_u].all()), "locked_possible": not bool(two[lo2:hi_p].all())}


def main() -> None:
    import cal33
    import pandas as pd
    DER = "/mnt/large-storage/market_data/PropExperiment/derived/e33/"
    A = DER + "labels/17934b7b23b1/"
    B = DER + "implB/labels/"
    hv = json.load(open(f"{OUT}/hand_values.json"))
    sigma = hv["sigma_zm"]

    # ---------------- D1 = 2022-09-29: F15 every row, T15 chosen rows
    D1 = "2022-09-29"
    iid = cal33.fronts(D1)["ZM"]
    lim = limits_asof_0830(D1, iid)
    p(f"D1 {D1}: releases {cal33.releases(D1)}, excluded {cal33.excluded(D1)}, limits {lim}, cal33.limits {cal33.limits(D1)}")
    rows = fh_date(D1, 15, cal33.releases(D1), cal33.excluded(D1)[0], lim)
    rep = rows.pop("_rep")
    n_rows = sum(1 for r in rows.values() if r["row_ok"])
    p(f"  F15 rows kept {n_rows} of {len(rows)}; entry_ok {sum(1 for r in rows.values() if r['entry_ok'])}; locked hits {sum(1 for r in rows.values() if r['locked_hit'])}; limit hits {sum(1 for r in rows.values() if r['rule5_lim_hit'])}")
    a = pd.read_parquet(A + f"F15/{D1}.parquet").set_index("i")
    b = pd.read_parquet(B + f"F15/{D1}.parquet").set_index("i")
    res["F15_D1"] = {}
    for i in (0, 1, 115, 150, 262):
        r = rows[i]
        p(f"  F15 i={i}: mine {{entry_ok {r['entry_ok']} row_ok {r['row_ok']} ask(t+L) {r.get('ask_tL')} bid(t+L) {r.get('bid_tL')} bid(end) {r.get('bid_end')} ask(end) {r.get('ask_end')} n_long {r.get('n_long')!r} n_short {r.get('n_short')!r} y {r.get('y')} w {r.get('w')!r} c_m {r.get('c_m')} span_end {r['span_end']}}}")
        for name, tbl in (("A", a), ("B", b)):
            x = tbl.loc[i]
            agree = (bool(x["entry_ok"]) == r["entry_ok"] and bool(x["row_ok"]) == r["row_ok"]
                     and int(x["y"]) == r.get("y", 0) and int(x["span_end_ns"]) == r["span_end"]
                     and (not r["row_ok"] or (x["n_long"] == r["n_long"] and x["n_short"] == r["n_short"]
                                              and abs(x["w"] - r["w"]) <= 1e-12)))
            p(f"    {name}: entry_ok {bool(x['entry_ok'])} row_ok {bool(x['row_ok'])} y {int(x['y'])} n_long {x['n_long']!r} n_short {x['n_short']!r} w {x['w']!r} span_end {int(x['span_end_ns'])} mid_move {x.get('mid_move', float('nan'))!r} -> {'AGREE' if agree else 'DISAGREE'}")
            res["F15_D1"][f"{i}_{name}"] = bool(agree)
    # whole-date flag agreement (counts only)
    for name, tbl in (("A", a), ("B", b)):
        ok_e = sum(1 for i, r in rows.items() if bool(tbl.loc[i]["entry_ok"]) == r["entry_ok"])
        ok_r = sum(1 for i, r in rows.items() if bool(tbl.loc[i]["row_ok"]) == r["row_ok"])
        ok_y = sum(1 for i, r in rows.items() if r["row_ok"] and int(tbl.loc[i]["y"]) == r["y"] and tbl.loc[i]["n_long"] == r["n_long"] and tbl.loc[i]["n_short"] == r["n_short"])
        ok_w = sum(1 for i, r in rows.items() if r["row_ok"] and abs(tbl.loc[i]["w"] - r["w"]) <= 1e-12)
        p(f"  F15 whole date vs {name}: entry_ok agree {ok_e}/{len(rows)}, row_ok agree {ok_r}/{len(rows)}, (y, n_long, n_short) agree {ok_y}/{n_rows}, w agree {ok_w}/{n_rows}")
        res[f"F15_D1_whole_{name}"] = [ok_e, ok_r, ok_y, ok_w, len(rows), n_rows]

    # T15 on D1: scan for rows with each tau outcome
    res["T15_D1"] = {}
    tb_rows = {}
    for i, t in grid(D1, 15):
        if rows[i]["row_ok"]:
            tb_rows[i] = tb_row(rep, D1, t, 15, sigma)
    pick = []
    for want in (1, -1, 0):
        cand = [i for i, r in tb_rows.items() if r["y"] == want]
        if cand:
            pick.append(cand[len(cand) // 2])
    pick = sorted(set(pick + [115]))
    have_a = True
    try:
        at = pd.read_parquet(A + f"T15/{D1}.parquet").set_index("i")
    except Exception as ex:  # noqa: BLE001
        have_a = False
        p(f"  A T15 not available yet: {ex}")
    bt = pd.read_parquet(B + f"T15/{D1}.parquet").set_index("i")
    for i in pick:
        r = tb_rows[i]
        p(f"  T15 i={i}: mine {r}")
        for name, tbl in ((("A", at),) if have_a else ()) + (("B", bt),):
            x = tbl.loc[i]
            agree = (bool(x["row_ok"]) and int(x["y"]) == r["y"] and x["n_long"] == r["n_long"]
                     and x["n_short"] == r["n_short"] and int(x["span_end_ns"]) == r["span_end"])
            p(f"    {name}: row_ok {bool(x['row_ok'])} y {int(x['y'])} n_long {x['n_long']!r} n_short {x['n_short']!r} span_end {int(x['span_end_ns'])} w {x['w']!r} -> {'AGREE' if agree else 'DISAGREE'}")
            res["T15_D1"][f"{i}_{name}"] = bool(agree)
    # whole-date T15 vs B (and A if present): counts only
    for name, tbl in ((("A", at),) if have_a else ()) + (("B", bt),):
        ok = sum(1 for i, r in tb_rows.items() if int(tbl.loc[i]["y"]) == r["y"] and tbl.loc[i]["n_long"] == r["n_long"] and tbl.loc[i]["n_short"] == r["n_short"] and int(tbl.loc[i]["span_end_ns"]) == r["span_end"])
        okr = sum(1 for i, r in tb_rows.items() if bool(tbl.loc[i]["row_ok"]))
        p(f"  T15 whole date vs {name}: (y, n_long, n_short, span_end) agree {ok}/{len(tb_rows)}; rows my row_ok that {name} keeps {okr}/{len(tb_rows)}; locked_union differs from locked_possible on {sum(1 for r in tb_rows.values() if r['locked_union'] != r['locked_possible'])} rows")
        res[f"T15_D1_whole_{name}"] = [ok, okr, len(tb_rows)]

    # ---------------- 2023-08-11: F05 flags around the 11:00 release
    D3 = "2023-08-11"
    iid3 = cal33.fronts(D3)["ZM"]
    lim3 = limits_asof_0830(D3, iid3)
    rel = cal33.releases(D3)
    p(f"D3 {D3}: releases {rel} (= 11:00 CT? {rel[0] == hr.ct(D3, '11:00:00')}), limits {lim3}")
    rows3 = fh_date(D3, 5, rel, cal33.excluded(D3)[0], lim3)
    rows3.pop("_rep")
    a3 = pd.read_parquet(A + f"F05/{D3}.parquet").set_index("i")
    b3 = pd.read_parquet(B + f"F05/{D3}.parquet").set_index("i")
    res["F05_D3"] = {}
    for hhmm in ("10:52", "10:53", "11:29", "11:30", "11:31"):
        t = hr.ct(D3, hhmm + ":00")
        i = int((t - hr.ct(D3, "08:35:00")) // NS_MIN)
        r = rows3[i]
        p(f"  F05 {hhmm} i={i}: mine entry_ok {r['entry_ok']} row_ok {r['row_ok']} rule3_hit {r['rule3_hit']} span_end {r['span_end']} y {r.get('y')} n_long {r.get('n_long')!r} n_short {r.get('n_short')!r} w {r.get('w')!r}")
        for name, tbl in (("A", a3), ("B", b3)):
            x = tbl.loc[i]
            agree = (bool(x["entry_ok"]) == r["entry_ok"] and bool(x["row_ok"]) == r["row_ok"]
                     and (not r["row_ok"] or (int(x["y"]) == r["y"] and x["n_long"] == r["n_long"] and x["n_short"] == r["n_short"] and abs(x["w"] - r["w"]) <= 1e-12)))
            p(f"    {name}: entry_ok {bool(x['entry_ok'])} row_ok {bool(x['row_ok'])} y {int(x['y'])} n_long {x['n_long']!r} n_short {x['n_short']!r} w {x['w']!r} -> {'AGREE' if agree else 'DISAGREE'}")
            res["F05_D3"][f"{hhmm}_{name}"] = bool(agree)
    n3 = sum(1 for r in rows3.values() if r["rule3_hit"])
    p(f"  F05 {D3}: minutes removed by rule 3 (mine) {n3}; A entry_ok false count {int((~a3['entry_ok']).sum())}; B {int((~b3['entry_ok']).sum())}")

    # ---------------- 2021-04-01: rule 5 limit proximity
    D4 = "2021-04-01"
    iid4 = cal33.fronts(D4)["ZM"]
    lim4 = limits_asof_0830(D4, iid4)
    p(f"D4 {D4}: limits (mine) {lim4}, cal33.limits {cal33.limits(D4)}; HL - 0.02c = {0.99 * lim4[0] - 0.01 * lim4[1]:.0f}; LL + 0.02c = {1.01 * lim4[1] + 0.01 * lim4[0]:.0f}")
    rows4 = fh_date(D4, 5, cal33.releases(D4), cal33.excluded(D4)[0], lim4)
    rows4.pop("_rep")
    hits = [i for i, r in rows4.items() if r["rule5_lim_hit"]]
    p(f"  minutes failing the limit part (mine): {len(hits)} -> i {hits[:5]}..{hits[-5:] if hits else ''}")
    a4 = pd.read_parquet(A + f"F05/{D4}.parquet").set_index("i")
    b4 = pd.read_parquet(B + f"F05/{D4}.parquet").set_index("i")
    res["F05_D4"] = {}
    chosen = [hits[0], hits[0] - 1 if hits[0] > 0 else hits[-1] + 1] if hits else [0, 1]
    for i in chosen:
        r = rows4[i]
        t = r["t"]
        p(f"  F05 i={i} ({(t - hr.ct(D4, '00:00:00')) / 3.6e12:.4f} h CT): mine entry_ok {r['entry_ok']} row_ok {r['row_ok']} rule5_lim_hit {r['rule5_lim_hit']} y {r.get('y')} n_long {r.get('n_long')!r} n_short {r.get('n_short')!r}")
        for name, tbl in (("A", a4), ("B", b4)):
            x = tbl.loc[i]
            agree = (bool(x["entry_ok"]) == r["entry_ok"] and bool(x["row_ok"]) == r["row_ok"]
                     and (not r["row_ok"] or (int(x["y"]) == r["y"] and x["n_long"] == r["n_long"] and x["n_short"] == r["n_short"])))
            p(f"    {name}: entry_ok {bool(x['entry_ok'])} row_ok {bool(x['row_ok'])} y {int(x['y'])} n_long {x['n_long']!r} n_short {x['n_short']!r} -> {'AGREE' if agree else 'DISAGREE'}")
            res["F05_D4"][f"{i}_{name}"] = bool(agree)
    for name, tbl in (("A", a4), ("B", b4)):
        ok_e = sum(1 for i, r in rows4.items() if bool(tbl.loc[i]["entry_ok"]) == r["entry_ok"])
        p(f"  F05 {D4} entry_ok agreement with {name}: {ok_e}/{len(rows4)}; {name} entry_ok false count {int((~tbl['entry_ok']).sum())}, mine {sum(1 for r in rows4.values() if not r['entry_ok'])}")
        res[f"F05_D4_whole_{name}"] = ok_e

    # ---------------- 2022-12-13 (after a roll): every flag false
    D5 = "2022-12-13"
    for name, root in (("A", A), ("B", B)):
        x = pd.read_parquet(root + f"F15/{D5}.parquet")
        p(f"  {D5} F15 {name}: rows {len(x)}, entry_ok true {int(x['entry_ok'].sum())}, row_ok true {int(x['row_ok'].sum())}")
        res[f"excluded_{D5}_{name}"] = [int(x["entry_ok"].sum()), int(x["row_ok"].sum())]
    json.dump(res, open(f"{OUT}/hand_label_results.json", "w"), indent=1)
    p("DONE")


if __name__ == "__main__":
    main()
