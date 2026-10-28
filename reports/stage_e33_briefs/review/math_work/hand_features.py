"""Hand recomputation of features on D1 = 2022-09-29 (i = 115, t1 = 10:30:00 CT; i = 5, t0 =
08:40:00 CT) and the burst on D2 = 2021-08-16 (i = 112, 10:27:00 CT), step by step from the
protocol text (P4, 0.3). Intermediates go to features_work.txt; values to hand_values.json.
"""
from __future__ import annotations

import json
import math
import sys

import numpy as np

import hand_replay as hr

OUT = "/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e33_briefs/review/math_work"
TICK_ZM = 100_000_000  # 0.10 USD/short ton in 1e-9 units
NS_MIN = hr.NS_MIN
log = open(f"{OUT}/features_work.txt", "w")
vals: dict[str, float] = {}


def p(*a):
    print(*a, file=log)
    log.flush()


def clip5(x):
    return float(min(5.0, max(-5.0, x)))


def hist(day):
    return np.load(f"{OUT}/hist_{day}.npz")


def sigma_from_hist(days) -> float:
    """0.3 sigma_X(D): population SD of 1-minute mid changes (ticks) over the intervals between
    consecutive marks 08:35..13:13 of the 20 dates, valid mids at both ends, chained across rolls."""
    d = []
    for day in days:
        m = hist(day)["mid_zm"]
        dm = (m[1:] - m[:-1]) / TICK_ZM
        d.append(dm[np.isfinite(dm)])
    x = np.concatenate(d)
    sd = float(np.sqrt(np.mean((x - x.mean()) ** 2)))
    p(f"  sigma: n_intervals {len(x)} mean {x.mean():.6f} ticks, pop SD {sd:.12f}")
    return sd


def main() -> None:
    import cal33
    D1 = "2022-09-29"
    days20 = cal33.previous_trade_dates(D1, 20)
    p("D1", D1, "history dates", [str(d) for d in days20])
    t1 = hr.ct(D1, "10:30:00")
    t0 = hr.ct(D1, "08:40:00")
    rep = hr.replay_zm(D1, instants=[t1, t0])
    p("replay", {k: rep[k] for k in ("iid", "n_records", "batch_mixed_ts", "anomalies")}, "updates", len(rep["u_ts"]))

    # ---- sigma_ZM(D1), C.6
    sigma = sigma_from_hist(days20)
    vals["C_6@115"] = math.log(sigma)
    vals["sigma_zm"] = sigma
    p(f"C.6 = log(sigma) = {vals['C_6@115']!r}")

    # ---- as-of state at t1: C.3, C.4, F3.7, F3.8
    b, a, two, k = hr.touch_asof(rep, t1)
    s = rep["snaps"][t1]
    p(f"as of t1: update idx {k} ts {rep['u_ts'][k]} bid {b} ask {a} valid {rep['u_valid'][k]}; snapshot {s}")
    assert not s.get("missing") and s["last_flast_ts"] == rep["u_ts"][k], "snapshot must be the F_LAST state"
    assert s["bid"][0]["price"] == b and s["ask"][0]["price"] == a
    spread_ticks = (a - b) / TICK_ZM
    vals["C_3@115"] = float(min(spread_ticks, 5.0))
    qb1, qa1 = s["bid"][0]["displayed"], s["ask"][0]["displayed"]
    vals["C_4@115"] = math.log(1 + qb1 + qa1)
    sb = [lv["seasoned"] for lv in s["bid"]]
    sa = [lv["seasoned"] for lv in s["ask"]]
    p(f"C.3: spread {spread_ticks} ticks -> {vals['C_3@115']}; C.4: qb1 {qb1} qa1 {qa1} -> {vals['C_4@115']!r}")
    p(f"seasoned bid {sb} ask {sa} (displayed bid {[lv['displayed'] for lv in s['bid']]} ask {[lv['displayed'] for lv in s['ask']]})")
    vals["F3_7@115"] = (sb[0] - sa[0]) / (sb[0] + sa[0]) if (sb[0] + sa[0]) else 0.0
    sb3, sa3 = sum(sb), sum(sa)
    vals["F3_8@115"] = (sb3 - sa3) / (sb3 + sa3) if (sb3 + sa3) else 0.0
    p(f"F3.7 = ({sb[0]}-{sa[0]})/({sb[0]}+{sa[0]}) = {vals['F3_7@115']!r}; F3.8 = ({sb3}-{sa3})/({sb3}+{sa3}) = {vals['F3_8@115']!r}")

    # ---- C.5 at t1
    cs = np.concatenate([[0], np.cumsum(rep["t_sz"])])
    lo = np.searchsorted(rep["t_ts"], t1 - 15 * NS_MIN, side="right")
    hi = np.searchsorted(rep["t_ts"], t1, side="right")
    v15 = float(cs[hi] - cs[lo])
    vb = [float(hist(d)["v15"][115]) for d in days20]
    vbar = float(np.mean(vb))
    vals["C_5@115"] = clip5(math.log((v15 + 1) / (vbar + 1)))
    p(f"C.5: V15(t1) {v15} (trades {hi - lo}); V15 at 10:30 on the 20 dates {vb}; Vbar {vbar!r}; C.5 {vals['C_5@115']!r}")

    # ---- F4.1 at t1, F4.4 at t0 (open-time axis across 08:30)
    m_t1 = hr.mid_asof(rep, t1)
    m_t1m1 = hr.mid_asof(rep, t1 - NS_MIN)
    vals["F4_1@115"] = clip5((m_t1 - m_t1m1) / TICK_ZM / (sigma * 1.0))
    p(f"F4.1: M(t1) {m_t1} M(t1-1) {m_t1m1} -> {vals['F4_1@115']!r}")
    m_t0 = hr.mid_asof(rep, t0)
    u30 = hr.open_axis_mark(D1, t0, 30)
    m_u30 = hr.mid_asof(rep, u30)
    p(f"F4.4 at 08:40: mark t-30 on the open axis = {u30} (= {(u30 - hr.ct(D1, '00:00:00')) / 3.6e12:.4f} h CT, i.e. 07:25); M(08:40) {m_t0} M(07:25) {m_u30}")
    vals["F4_4@5"] = clip5((m_t0 - m_u30) / TICK_ZM / (sigma * math.sqrt(30)))
    p(f"F4.4 = {vals['F4_4@5']!r}")

    # ---- F3.1, F3.2 at t1 with trailing references (two readings of a non-computable term)
    u_ts, bid, ask = rep["u_ts"], rep["u_bid"], rep["u_ask"]
    qb, qa = rep["u_qb"][0], rep["u_qa"][0]
    pb0, pb1, pa0, pa1 = bid[:-1], bid[1:], ask[:-1], ask[1:]
    e = ((pb1 >= pb0) * qb[1:] - (pb1 <= pb0) * qb[:-1] - (pa1 <= pa0) * qa[1:] + (pa1 >= pa0) * qa[:-1]).astype(float)
    comp = rep["u_two"][:-1] & rep["u_two"][1:]
    vpair = rep["u_valid"][:-1] & rep["u_valid"][1:]
    ts_n = u_ts[1:]
    for kmin in (1, 5):
        lo = np.searchsorted(ts_n, t1 - kmin * NS_MIN, side="right")
        hi = np.searchsorted(ts_n, t1, side="right")
        n_nc = int((~comp[lo:hi]).sum())
        n_inv = int((~vpair[lo:hi]).sum())
        ofi = float(e[lo:hi].sum())
        p(f"OFI_ZM_{kmin}(t1): {hi - lo} updates in window, sum e_n {ofi}, non-computable terms {n_nc}, invalid-state terms {n_inv}")
        ra = np.concatenate([hist(d)[f"ofi_zm{kmin}_a"] for d in days20])
        rb = np.concatenate([hist(d)[f"ofi_zm{kmin}_b"] for d in days20])
        obar_a = float(np.nanmean(np.abs(ra)))
        obar_b = float(np.mean(np.abs(rb)))
        p(f"  Obar_ZM_{kmin}: reading A (crossed allowed, any non-computable term -> mark dropped): {obar_a!r} over {int(np.isfinite(ra).sum())} marks; reading B (terms with an invalid state -> 0): {obar_b!r} over {len(rb)} marks")
        vals[f"F3_{1 if kmin == 1 else 2}@115_readingA"] = clip5(ofi / obar_a)
        vals[f"F3_{1 if kmin == 1 else 2}@115_readingB"] = clip5(ofi / obar_b)
        p(f"  F3.{1 if kmin == 1 else 2} = {vals[f'F3_{1 if kmin == 1 else 2}@115_readingA']!r} (A), {vals[f'F3_{1 if kmin == 1 else 2}@115_readingB']!r} (B)")

    # ---- F2.8 at t1: ZS top-of-book OFI, k = 1 (MBP-1 F_LAST updates; also all records)
    zs = hr.load_mbp1("ZS", D1)
    for tag, mask in (("fl", zs["last"]), ("all", np.ones(zs["n"], dtype=bool))):
        ts, b2, a2, q2b, q2a = zs["ts"][mask], zs["bid"][mask], zs["ask"][mask], zs["qb"][mask], zs["qa"][mask]
        tw, va = zs["two"][mask] & ~zs["bad"][mask], zs["valid"][mask]
        e2 = ((b2[1:] >= b2[:-1]) * q2b[1:] - (b2[1:] <= b2[:-1]) * q2b[:-1] - (a2[1:] <= a2[:-1]) * q2a[1:] + (a2[1:] >= a2[:-1]) * q2a[:-1]).astype(float)
        lo = np.searchsorted(ts[1:], t1 - NS_MIN, side="right")
        hi = np.searchsorted(ts[1:], t1, side="right")
        c2 = tw[:-1] & tw[1:]
        ofi = float(e2[lo:hi].sum())
        p(f"OFI_ZS_1(t1) [{tag}]: {hi - lo} updates, sum {ofi}, non-computable {int((~c2[lo:hi]).sum())}")
        ra = np.concatenate([hist(d)[f"ofi_ZS1_a_{tag}"] for d in days20])
        rb = np.concatenate([hist(d)[f"ofi_ZS1_b_{tag}"] for d in days20])
        obar_a, obar_b = float(np.nanmean(np.abs(ra))), float(np.mean(np.abs(rb)))
        p(f"  Obar_S_1 [{tag}]: A {obar_a!r} ({int(np.isfinite(ra).sum())} marks), B {obar_b!r}")
        vals[f"F2_8@115_{tag}_A"] = clip5(ofi / obar_a)
        vals[f"F2_8@115_{tag}_B"] = clip5(ofi / obar_b)
        p(f"  F2.8 [{tag}] = {vals[f'F2_8@115_{tag}_A']!r} (A) {vals[f'F2_8@115_{tag}_B']!r} (B)")

    # ---- F1.3 at t1: 10-date OLS inside the segment, release-clear marks
    seg = cal33.segment_id(D1)
    days10 = [d for d in cal33.previous_trade_dates(D1, 10) if cal33.segment_id(d) == seg]
    p(f"F1.3: segment {seg}; 10 dates before D1 in the segment: {[str(d) for d in days10]}")
    Y, XS, XL = [], [], []
    n_by_date = {}
    for d in days10:
        h = hist(d)
        mk = np.array([hr.ct(d, f"{(515 + i) // 60:02d}:{(515 + i) % 60:02d}:00") for i in range(279)], dtype=np.int64)
        clear = np.ones(279, dtype=bool)
        for R in cal33.releases(d):
            clear &= ~((mk >= R - 2 * NS_MIN) & (mk <= R + 30 * NS_MIN))
        ok = clear & np.isfinite(h["mid_zm"]) & np.isfinite(h["mid_ZS_fl"]) & np.isfinite(h["mid_ZL_fl"])
        n_by_date[str(d)] = int(ok.sum())
        Y.append(h["mid_zm"][ok] / 1e9); XS.append(h["mid_ZS_fl"][ok] / 1e9); XL.append(h["mid_ZL_fl"][ok] / 1e9)
    y, xs, xl = np.concatenate(Y), np.concatenate(XS), np.concatenate(XL)
    n = len(y)
    X = np.column_stack([np.ones(n), xs - xs.mean(), xl - xl.mean()])
    coef, res, rank, sv = np.linalg.lstsq(X, y, rcond=None)
    yhat = X @ coef
    ssr = float(np.sum((y - yhat) ** 2))
    bS, bL = float(coef[1]), float(coef[2])
    a_nat = float(y.mean() - bS * xs.mean() - bL * xl.mean())
    sd_e = math.sqrt(ssr / n) / 0.10
    p(f"  samples per date {n_by_date}; n {n}; rank {rank}; centred fit intercept {coef[0]!r} b_S {bS!r} b_L {bL!r}; a (natural) {a_nat!r}; SSR {ssr!r}; sd_e {sd_e!r} ticks")
    ms = hr.mbp1_mid_asof(zs, t1) / 1e9
    zl = hr.load_mbp1("ZL", D1)
    ml = hr.mbp1_mid_asof(zl, t1) / 1e9
    mz = m_t1 / 1e9
    e_t = (mz - a_nat - bS * ms - bL * ml) / 0.10
    vals["F1_3@115"] = clip5(e_t / sd_e)
    p(f"  at t1: M_ZM {mz} M_ZS {ms} M_ZL {ml}; e(t) {e_t!r} ticks; zR {vals['F1_3@115']!r}")

    # ---- F1.1 zC30 at t1 (bonus; A and B differ at 1e-14)
    C = []
    for j in range(0, 31):
        u = t1 - j * NS_MIN
        mzm, mzs, mzl = hr.mid_asof(rep, u), hr.mbp1_mid_asof(zs, u), hr.mbp1_mid_asof(zl, u)
        C.append(11 * mzl / 1e9 + 2.2 * mzm / 1e9 - mzs / 1e9)
    C = np.array(C)
    hist30 = C[1:]
    mean30, sd30 = float(hist30.mean()), float(np.sqrt(np.mean((hist30 - hist30.mean()) ** 2)))
    vals["F1_1@115"] = clip5((C[0] - mean30) / sd30)
    p(f"F1.1: C(t1) {C[0]!r} mean_30 {mean30!r} sd_30 {sd30!r} -> {vals['F1_1@115']!r}")

    # ---- burst F4.11 / F4.12 on D2 = 2021-08-16 at i = 112 (10:27)
    D2 = "2021-08-16"
    days20b = cal33.previous_trade_dates(D2, 20)
    sig2 = sigma_from_hist(days20b)
    vals["sigma_zm_D2"] = sig2
    rep2 = hr.replay_zm(D2)
    t2 = hr.ct(D2, "10:27:00")
    Bs = []
    for j in range(14):
        e_ = t2 - j * NS_MIN
        m_e, m_e2 = hr.mid_asof(rep2, e_), hr.mid_asof(rep2, e_ - 2 * NS_MIN)
        Bs.append((m_e - m_e2) / TICK_ZM / (sig2 * math.sqrt(2)))
    Bs = np.array(Bs)
    jstar = int(np.argmax(np.abs(Bs)))  # argmax returns the first = latest e on ties
    Bstar = float(Bs[jstar])
    DB = Bstar if abs(Bstar) >= 3 else 0.0
    vals["F4_11@112_D2"] = clip5(DB)
    vals["F4_12@112_D2"] = clip5(DB * math.exp(-jstar / 5.0))
    p(f"F4.11 on {D2} at 10:27: sigma {sig2!r}; B(e) for j=0..13 {Bs.tolist()}; j* {jstar} B* {Bstar!r}; DB {DB!r}; F4.12 {vals['F4_12@112_D2']!r}")
    vals["C_6@112_D2"] = math.log(sig2)
    json.dump(vals, open(f"{OUT}/hand_values.json", "w"), indent=1)
    p("DONE")


if __name__ == "__main__":
    main()
