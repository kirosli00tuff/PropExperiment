"""Implementation B: the 59 P4 features from day raws (dayB) of D and its 21 previous dates.

Every feature cites its protocol ID. Invalid values (G3) become 0 and set the family flag
(C.11-C.14) to 0 for the row; clipping (G4) is applied after normalisation. Statistics follow
P0.3: population SD (ddof 0), OLS by numpy.linalg.lstsq on centred regressors with an intercept,
residual SD sqrt(SSR / n).
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import calB  # noqa: E402
import dayB  # noqa: E402

N_ROWS = 273  # i = 0..272 (G_5; INTERFACE 4.1)
N_HIST = 20  # P0.3 trailing references, sigma_X
N_FIT = 10  # F1.3
MIN_FIT_DATES = 3  # F1.3
MIN_GAP_DATES = 10  # F1.7, F4.7
CLIP = 5.0  # G4
I_1130 = 175  # 08:35 + 175 min = 11:30 (C.9)
I_1215 = 220  # 08:35 + 220 min = 12:15 (F4.13)
TOD_SPAN = 278.0  # 13:13 - 08:35 in minutes (C.1)

NAMES = ([f"C_{k}" for k in range(1, 16)] + [f"F1_{k}" for k in range(1, 9)]
         + [f"F2_{k}" for k in range(1, 12)] + [f"F3_{k}" for k in range(1, 13)]
         + [f"F4_{k}" for k in range(1, 14)])
CLIPPED = (["C_5"] + [f"F1_{k}" for k in (1, 2, 3, 4, 6, 7, 8)]
           + [f"F2_{k}" for k in range(1, 12)] + [f"F3_{k}" for k in (1, 2, 3, 4, 10, 11, 12)]
           + [f"F4_{k}" for k in (1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13)])
FAMILY = {"F1": "C_11", "F2": "C_12", "F3": "C_13", "F4": "C_14"}


# ------------------------------------------------------------------ history (P0.3) ----
def _last(hist: list[dict], n: int) -> list[dict]:
    return hist[-n:] if len(hist) >= n else []


def sigma(hist: list[dict], inst: str) -> float | None:
    """P0.3 sigma_X(D): population SD of the 1-minute mid changes (ticks of X) over all
    1-minute intervals inside 08:35-13:13 of the 20 trade dates before D with valid mids at both
    ends; None with fewer than 20 dates or no interval (READING B-SIG-1)."""
    h = _last(hist, N_HIST)
    if not h:
        return None
    k = {"zm": 0, "zs": 1, "zl": 2}[inst]
    parts = []
    for r in h:
        m2, ok = r[f"g_{inst}"], r[f"g_{inst}_ok"]
        use = ok[1:] & ok[:-1]
        parts.append((m2[1:] - m2[:-1])[use] / (2.0 * r["ticks"][k]))
    x = np.concatenate(parts)
    if not len(x):
        return None
    return float(np.std(x))


def references(hist: list[dict]) -> dict:
    """P0.3 trailing 20-date references over the minute marks 08:35-13:13 (None if fewer than
    20 dates)."""
    h = _last(hist, N_HIST)
    if not h:
        return {}
    out = {"vbar": np.mean(np.stack([r["v15_zm"] for r in h]), axis=0)}  # C.5 same minute
    for name in [f"ofi_zm_{k}" for k in dayB.OFI_K_ZM] + [
            f"ofi_{x}_{k}" for x in ("zs", "zl") for k in dayB.OFI_K_X]:
        inst = name.split("_")[1]
        if inst != "zm" and not all(r[f"{inst}_present"] for r in h):
            out[name] = None
            continue
        vals = np.concatenate([r[name][r[f"{name}_ok"]] for r in h])  # READING B-OFI-REF
        out[name] = float(np.mean(np.abs(vals))) if len(vals) else None
    dep = []
    for m in range(5):  # F3.4 Dbar_m over marks with a valid book (READING B-DBAR-1)
        vals = [((r["g_bq"][:, m] + r["g_aq"][:, m]) / 2.0)[r["g_zm_state_ok"]] for r in h]
        v = np.concatenate(vals)
        dep.append(float(np.mean(v)) if len(v) else None)
    out["dbar"] = dep
    out["sbar5"] = float(np.mean(np.concatenate([r["swb5"] + r["sws5"] for r in h])))
    out["rbar15"] = float(np.mean(np.abs(np.concatenate([r["rfb15"] - r["rfa15"] for r in h]))))
    lam = np.concatenate([r["lam60"] for r in h])
    lam = lam[np.isfinite(lam)]
    out["lam_med"] = float(np.median(lam)) if len(lam) else None
    return out


def crush_int(m2l: np.ndarray, m2m: np.ndarray, m2s: np.ndarray) -> np.ndarray:
    """F1: 20 C(u) in 1e-9 cents/bu: C = 11 M_ZL + 2.2 M_ZM - M_ZS and mid2 = 2 M, so
    20 C = 110 mid2_ZL + 22 mid2_ZM - 10 mid2_ZS (exact integers)."""
    return 110 * np.asarray(m2l, np.int64) + 22 * np.asarray(m2m, np.int64) - 10 * np.asarray(
        m2s, np.int64)


def _seg(d: date) -> int:
    return calB.segment_ids().get(d, -1)


def fit_f13(d: date, hist: list[dict]) -> tuple[float, float, float, float] | None:
    """F1.3: OLS M_ZM = a + b_S M_ZS + b_L M_ZL (natural units) on the minute marks 08:35-13:13
    clear of P3.6 rule 3 of the 10 trade dates before D inside D's segment (>= 3 dates with
    samples). Returns (a, b_S, b_L, residual SD in natural units) or None."""
    seg = _seg(d)
    xs, xl, ym, n_dates = [], [], [], 0
    for r in hist[-N_FIT:]:
        rd = date.fromisoformat(r["date"])
        if _seg(rd) != seg:
            continue
        use = r["g_zm_ok"] & r["g_zs_ok"] & r["g_zl_ok"] & r["release_clear"]
        if not use.any():
            continue
        n_dates += 1
        ym.append(r["g_zm"][use] / 2e9)
        xs.append(r["g_zs"][use] / 2e9)
        xl.append(r["g_zl"][use] / 2e9)
    if n_dates < MIN_FIT_DATES:
        return None
    y, s, l_ = np.concatenate(ym), np.concatenate(xs), np.concatenate(xl)
    design = np.column_stack([np.ones(len(y)), s - s.mean(), l_ - l_.mean()])
    coef, _, rank, _ = np.linalg.lstsq(design, y, rcond=None)
    if rank < 3:
        return None
    resid = y - design @ coef
    sd = float(np.sqrt(np.sum(resid ** 2) / len(y)))
    b_s, b_l = float(coef[1]), float(coef[2])
    a = float(y.mean() - b_s * s.mean() - b_l * l_.mean())
    return a, b_s, b_l, sd


def _gap_series(d: date, hist: list[dict], by: dict, crush: bool) -> tuple[list, object]:
    """F1.7 (crush) / F4.7 (ZM mid): the raw gap of D and of each of the 20 trade dates before
    D that qualify (F1.7: D' and its previous trade date inside D's segment; F4.7: the ZM front
    the same at both times). Values in exact integer units."""
    def gap(day: date, r: dict) -> int | None:
        p = calB.prev_trade_date(day)
        rp = by.get(p) if p is not None else None
        if rp is None:
            return None
        if crush:
            if not (_seg(day) == _seg(d) and _seg(p) == _seg(d)):
                return None
            if not all(r[f"{x}0835_ok"] and rp[f"{x}1315_ok"] for x in ("zm", "zs", "zl")):
                return None
            c1 = int(crush_int(r["zl0835"], r["zm0835"], r["zs0835"]))
            c0 = int(crush_int(rp["zl1315"], rp["zm1315"], rp["zs1315"]))
            return c1 - c0
        if int(r["fronts"][0]) != int(rp["fronts"][0]) or int(r["fronts"][0]) < 0:
            return None
        if not (r["zm0835_ok"] and rp["zm1315_ok"]):
            return None
        return int(r["zm0835"]) - int(rp["zm1315"])

    series = []
    for r in hist[-N_HIST:]:
        v = gap(date.fromisoformat(r["date"]), r)
        if v is not None:
            series.append(v)
    return series, gap


def gap_feature(d: date, raw: dict, hist: list[dict], crush: bool) -> float | None:
    if len(hist) < N_HIST:
        return None
    by = {date.fromisoformat(r["date"]): r for r in hist}
    by[d] = raw
    series, gap = _gap_series(d, hist, by, crush)
    if len(series) < MIN_GAP_DATES:
        return None
    sd = float(np.std(np.array(series, dtype=np.float64)))
    own = gap(d, raw)
    if own is None or sd == 0.0:
        return None
    return own / sd


# ------------------------------------------------------------------ features ----
class Table:
    def __init__(self, n: int) -> None:
        self.val = {k: np.zeros(n) for k in NAMES}
        self.ok = {k: np.zeros(n, bool) for k in NAMES}

    def put(self, name: str, val: np.ndarray, ok: np.ndarray) -> None:
        ok = np.asarray(ok, bool) & np.isfinite(val)
        self.val[name] = np.where(ok, val, 0.0)
        self.ok[name] = ok


def _div(num: np.ndarray, den: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    den = np.asarray(den, np.float64)
    ok = den != 0
    return np.asarray(num, np.float64) / np.where(ok, den, 1.0), ok


def _sample_days(raw: dict, jmax: int) -> np.ndarray:
    pg = raw["grid_pos"][:N_ROWS]
    j = np.arange(jmax + 1, dtype=np.int64)
    pos = pg[:, None] - j[None, :] * calB.MIN_NS
    mp = raw["mark_pos"]
    idx = np.clip(np.searchsorted(mp, pos), 0, len(mp) - 1)
    found = mp[idx] == pos
    days = np.where(found, raw["mark_day"][idx], -1)
    days[:, 0] = date.fromisoformat(raw["date"]).toordinal()
    return days


def _samples(raw: dict, inst: str, jmax: int) -> tuple[np.ndarray, np.ndarray]:
    m2, ok = dayB.sample(raw, inst, jmax)
    return m2[:N_ROWS], ok[:N_ROWS]


def family_c(t: Table, d: date, raw: dict, ref: dict, sig_zm: float | None) -> None:
    i = np.arange(N_ROWS)
    tod = i / TOD_SPAN
    ones = np.ones(N_ROWS, bool)
    t.put("C_1", tod, ones)  # C.1
    t.put("C_2", tod ** 2, ones)  # C.2
    st = raw["g_zm_state_ok"][:N_ROWS]
    spread = (raw["g_apx1"][:N_ROWS] - raw["g_bpx1"][:N_ROWS]) / float(raw["ticks"][0])
    t.put("C_3", np.minimum(spread, 5.0), st)  # C.3 (READING B-C34)
    depth = raw["g_bq"][:N_ROWS, 0] + raw["g_aq"][:N_ROWS, 0]
    t.put("C_4", np.log1p(depth.astype(np.float64)), st)  # C.4
    if "vbar" in ref:  # C.5
        v = (raw["v15_zm"][:N_ROWS] + 1.0) / (ref["vbar"][:N_ROWS] + 1.0)
        t.put("C_5", np.log(v), ones)
    if sig_zm is not None and sig_zm > 0:  # C.6
        t.put("C_6", np.full(N_ROWS, np.log(sig_zm)), ones)
    if int(raw["expiration"]) >= 0:  # C.7 (READING B-C7)
        n = calB.trade_dates_to(d, calB.trade_date_of_ns(int(raw["expiration"])))
        t.put("C_7", np.full(N_ROWS, min(n, 60) / 60.0), ones)
    c8 = 1.0 if calB.has_release(d) else 0.0
    t.put("C_8", np.full(N_ROWS, c8), ones)  # C.8
    t.put("C_9", c8 * (i >= I_1130), ones)  # C.9
    t.put("C_10", np.full(N_ROWS, 1.0 if calB.is_monday_or_after_closure(d) else 0.0),
          ones)  # C.10
    t.put("C_15", np.full(N_ROWS, 1.0 if d.month in (6, 7, 8) else 0.0), ones)  # C.15


def _zc(cint: np.ndarray, cok: np.ndarray, c0: int, win: int) -> tuple[np.ndarray, np.ndarray]:
    """F1.1/F1.2 z-score of C at column c0 against columns c0+1..c0+win (all valid; READING
    B-MISS-1); sd = 0 is invalid."""
    w = cint[:, c0 + 1:c0 + win + 1].astype(np.float64)
    ok = cok[:, c0] & cok[:, c0 + 1:c0 + win + 1].all(axis=1)
    mu = w.mean(axis=1)
    sd = w.std(axis=1)
    z, nz = _div(cint[:, c0].astype(np.float64) - mu, sd)
    return z, ok & nz


def family_f1(t: Table, d: date, raw: dict, hist: list[dict]) -> None:
    m, mok = _samples(raw, "zm", dayB.LOOKBACK)
    s, sok = _samples(raw, "zs", dayB.LOOKBACK)
    l_, lok = _samples(raw, "zl", dayB.LOOKBACK)
    days = _sample_days(raw, dayB.LOOKBACK)
    seg = _seg(d)
    seg_ok = np.vectorize(lambda o: o >= 0 and _seg(date.fromordinal(int(o))) == seg,
                          otypes=[bool])(days)  # G2 segment rule
    cint = crush_int(l_, m, s)
    cok = mok & sok & lok & seg_ok
    z30, ok30 = _zc(cint, cok, 0, 30)
    t.put("F1_1", z30, ok30)  # F1.1
    z120, ok120 = _zc(cint, cok, 0, 120)
    t.put("F1_2", z120, ok120)  # F1.2
    fit = fit_f13(d, hist)  # F1.3
    if fit is not None and fit[3] > 0:
        a, b_s, b_l, sd = fit
        tick = float(raw["ticks"][0]) / 1e9
        e = (m[:, 0] / 2e9 - a - b_s * s[:, 0] / 2e9 - b_l * l_[:, 0] / 2e9) / tick
        t.put("F1_3", e / (sd / tick), mok[:, 0] & sok[:, 0] & lok[:, 0])
    z30b, ok30b = _zc(cint, cok, 5, 30)
    t.put("F1_4", z30 - z30b, ok30 & ok30b)  # F1.4
    vz, vs, vl = (raw[f"v15_{x}"][:N_ROWS].astype(np.float64) for x in ("zm", "zs", "zl"))
    present = bool(raw["zs_present"]) and bool(raw["zl_present"]) and int(raw["fronts"][0]) >= 0
    vrel, okv = _div(vz, vz + vs + vl)
    t.put("F1_5", vrel, okv & present)  # F1.5
    t.put("F1_6", z30 * vrel, ok30 & okv & present)  # F1.6
    g_c = gap_feature(d, raw, hist, crush=True)  # F1.7
    if g_c is not None:
        i = np.arange(N_ROWS)
        t.put("F1_7", np.full(N_ROWS, g_c), np.ones(N_ROWS, bool))
        t.put("F1_8", g_c * np.exp(-i / 30.0), np.ones(N_ROWS, bool))  # F1.8


def family_f2(t: Table, raw: dict, ref: dict, sig: dict) -> None:
    for inst, base, kx in (("zs", 1, 1), ("zl", 4, 2)):  # F2.1-F2.6
        m2, ok = _samples(raw, inst, 15)
        sg = sig[inst]
        for n, k in enumerate((1, 5, 15)):
            if sg is None or sg <= 0:
                continue
            r = (m2[:, 0] - m2[:, k]) / (2.0 * raw["ticks"][kx]) / (sg * np.sqrt(k))
            t.put(f"F2_{base + n}", r, ok[:, 0] & ok[:, k])
    if sig["zm"] is not None and sig["zm"] > 0:  # F2.7
        dz = {}
        oks = np.ones(N_ROWS, bool)
        for inst in ("zm", "zs", "zl"):
            m2, ok = _samples(raw, inst, 5)
            dz[inst] = m2[:, 0] - m2[:, 5]
            oks &= ok[:, 0] & ok[:, 5]
        num = 10 * dz["zs"] - 110 * dz["zl"] - 22 * dz["zm"]  # 44e9 x USD/ton move
        d5 = num / (44.0 * float(raw["ticks"][0])) / (sig["zm"] * np.sqrt(5.0))
        t.put("F2_7", d5, oks)
    for inst, base in (("zs", 8), ("zl", 10)):  # F2.8-F2.11
        for n, k in enumerate(dayB.OFI_K_X):
            obar = ref.get(f"ofi_{inst}_{k}")
            if obar is None or obar == 0 or not raw[f"{inst}_present"]:
                continue
            t.put(f"F2_{base + n}", raw[f"ofi_{inst}_{k}"][:N_ROWS] / obar,
                  raw[f"ofi_{inst}_{k}_ok"][:N_ROWS])  # FD3 (b)


def family_f3(t: Table, raw: dict, ref: dict) -> None:
    ones = np.ones(N_ROWS, bool)
    zm_ok = int(raw["fronts"][0]) >= 0
    if ref and zm_ok:
        for n, k in enumerate(dayB.OFI_K_ZM):  # F3.1-F3.3
            obar = ref.get(f"ofi_zm_{k}")
            if obar:
                t.put(f"F3_{1 + n}", raw[f"ofi_zm_{k}"][:N_ROWS] / obar,
                      raw[f"ofi_zm_{k}_ok"][:N_ROWS])  # FD3 (b)
        if all(x is not None for x in ref["dbar"]):  # F3.4
            num = sum(raw[f"iofi5_{m}"][:N_ROWS] for m in range(1, 6)).astype(np.float64)
            v, ok = _div(num, np.full(N_ROWS, sum(ref["dbar"])))
            lv_ok = np.all([raw[f"iofi5_{m}_ok"][:N_ROWS] for m in range(1, 6)], axis=0)
            t.put("F3_4", v, ok & lv_ok)  # FD3 (b): every level's window computable
    if not zm_ok:
        return
    for n, (b, s) in enumerate((("b5", "s5"), ("b15", "s15"))):  # F3.5-F3.6
        bb, ss = raw[b][:N_ROWS].astype(np.float64), raw[s][:N_ROWS].astype(np.float64)
        v, ok = _div(bb - ss, bb + ss)
        t.put(f"F3_{5 + n}", v, ok)
    q = raw["seas_q"][:N_ROWS].astype(np.float64)
    sok = raw["seas_ok"][:N_ROWS]
    v, ok = _div(q[:, 0, 0] - q[:, 1, 0], q[:, 0, 0] + q[:, 1, 0])
    t.put("F3_7", v, ok & sok)  # F3.7
    b3, a3 = q[:, 0, :3].sum(axis=1), q[:, 1, :3].sum(axis=1)
    v, ok = _div(b3 - a3, b3 + a3)
    t.put("F3_8", v, ok & sok)  # F3.8
    ca, cb = raw["ca5"][:N_ROWS].astype(np.float64), raw["cb5"][:N_ROWS].astype(np.float64)
    v, ok = _div(ca - cb, ca + cb)
    t.put("F3_9", v, ok)  # F3.9
    if ref:
        if ref["sbar5"]:  # F3.10
            t.put("F3_10", (raw["swb5"][:N_ROWS] - raw["sws5"][:N_ROWS]) / ref["sbar5"], ones)
        if ref["rbar15"]:  # F3.11
            t.put("F3_11", (raw["rfb15"][:N_ROWS] - raw["rfa15"][:N_ROWS]) / ref["rbar15"],
                  ones)
        lam = raw["lam60"][:N_ROWS]
        if ref["lam_med"]:  # F3.12
            t.put("F3_12", lam / ref["lam_med"], np.isfinite(lam))


def family_f4(t: Table, d: date, raw: dict, hist: list[dict], sg: float | None) -> None:
    i = np.arange(N_ROWS)
    ones = np.ones(N_ROWS, bool)
    m2, ok = _samples(raw, "zm", 60)
    tick2 = 2.0 * float(raw["ticks"][0])
    if sg is not None and sg > 0:
        for n, k in enumerate((1, 5, 15, 30, 60)):  # F4.1-F4.5
            t.put(f"F4_{1 + n}", (m2[:, 0] - m2[:, k]) / tick2 / (sg * np.sqrt(k)),
                  ok[:, 0] & ok[:, k])
        ro = (m2[:, 0] - int(raw["zm0835"])) / tick2 / (sg * np.sqrt(np.maximum(1, i)))
        ro = np.where(i == 0, 0.0, ro)  # F4.9 "0 at 08:35"
        rok = ok[:, 0] & bool(raw["zm0835_ok"])
        t.put("F4_9", ro, rok)
        t.put("F4_13", ro * (i >= I_1215), rok)  # F4.13
        dif = (m2[:, :15] - m2[:, 1:16]) / tick2  # F4.10: the 15 changes ending at t
        t.put("F4_10", dif.std(axis=1) / sg, ok[:, :16].all(axis=1))
        b = (m2[:, :14] - m2[:, 2:16]) / tick2 / (sg * np.sqrt(2.0))  # F4.11: e = t - q min
        q_star = np.argmax(np.abs(b), axis=1)  # first max = latest e on ties
        b_star = b[i, q_star]
        db = np.where(np.abs(b_star) >= 3.0, b_star, 0.0)
        dok = ok[:, :16].all(axis=1)
        t.put("F4_11", db, dok)
        t.put("F4_12", db * np.exp(-q_star / 5.0), dok)  # F4.12
    hi, lo = raw["rp_hi"][:N_ROWS], raw["rp_lo"][:N_ROWS]  # F4.6
    rng = (hi - lo).astype(np.float64)
    rp = np.where(rng > 0, (m2[:, 0] - lo) / np.where(rng > 0, rng, 1.0), 0.5)
    t.put("F4_6", rp, ok[:, 0] & raw["rp_ok"][:N_ROWS])
    gp = gap_feature(d, raw, hist, crush=False)  # F4.7
    if gp is not None:
        t.put("F4_7", np.full(N_ROWS, gp), ones)
        t.put("F4_8", gp * np.exp(-i / 30.0), ones)  # F4.8


def features(d: date, raw: dict, hist: list[dict]) -> tuple[np.ndarray, dict]:
    """[273, 59] float64 in NAMES order, plus the day statistics (sigma_X in ticks)."""
    sig = {x: sigma(hist, x) for x in ("zm", "zs", "zl")}
    ref = references(hist)
    t = Table(N_ROWS)
    family_c(t, d, raw, ref, sig["zm"])
    family_f1(t, d, raw, hist)
    family_f2(t, raw, ref, sig)
    family_f3(t, raw, ref)
    family_f4(t, d, raw, hist, sig["zm"])
    for fam, flag in FAMILY.items():  # G3 flags C.11-C.14
        names = [n for n in NAMES if n.startswith(fam + "_")]
        v = np.all(np.stack([t.ok[n] for n in names]), axis=0)
        t.put(flag, v.astype(np.float64), np.ones(N_ROWS, bool))
    for n in CLIPPED:  # G4
        t.val[n] = np.clip(t.val[n], -CLIP, CLIP)
    x = np.column_stack([t.val[n] for n in NAMES]).astype(np.float64)
    return x, {"sigma_zm": sig["zm"], "sigma_zs": sig["zs"], "sigma_zl": sig["zl"]}
