"""Layer 1 (spec section 3): D1 to D6, the Layer 1 gate and L1, one code at a time.

Each row carries two note lists: "u" (a spec unknown rule applied, or a spec evidence cap) and "lead" (a case the spec
does not settle; the script's handling is stated and the lead rules on it).
"""
from __future__ import annotations

from datetime import date
from fractions import Fraction as F

from s32b_common import (
    FAMILIES,
    FAMILY_OF,
    HALF,
    INF,
    NQ,
    SAME_PRICE_OF,
    InputError,
    Params,
    band_le,
    blind_rated,
    cap_extreme_0_4,
    cap_s12,
    fmt_num,
    fmt_two,
    nonneg,
    positive,
    q,
)

D1_H = ("30", "60", "120", "240")                          # spec 3 D1: the user's prior band
D1_ALL_H = ("5", "15", "30", "60", "120", "240", "OC")     # variant D1_all
R_REPORTED = ("5", "15", "30", "60", "120", "240", "OC")   # r_5, r_15 and r_OC reported, not scored
W_L1 = {"D1": F("0.30"), "D2": F("0.15"), "D3": F("0.15"), "D4": F("0.15"), "D5": F("0.10"), "D6": F("0.15")}
D1_STEPS = ((F("0.025"), 4), (F("0.05"), 3), (F("0.10"), 2), (F("0.20"), 1))
DLL_REF = F(1000)                  # spec 3 D4 J and 9.2
ADV_THIN, ADV_MID = F(1000), F(10000)
SPREAD_WIDE, SPREAD_MID = F(2), F(1)
TOUCH_THIN, TOUCH_MID = F(2), F(5)
SAT_RATIO = F(5)                   # "at least 5 times" (inclusive, as written)
H_CUT_EARLY, H_CUT_LATE = date(2017, 6, 30), date(2020, 12, 31)
K_LOW, K_HIGH = F(10), F(50)
L1_MIN = F(2)


# ------------------------------------------------------------------------------------------- pure criterion rules
def d1_band(r: F) -> int:
    """r_h <= 0.025: 4; <= 0.05: 3; <= 0.10: 2; <= 0.20: 1; else 0 (boundaries to the higher score)."""
    return band_le(r, D1_STEPS)


def d1_score(c_rt: F, disp: dict, horizons) -> tuple:
    """(D1 or None, bands, missing horizons): the mean band score over `horizons`; None if any sigma is unknown."""
    missing = [h for h in horizons if disp.get(h) is None]
    if missing:
        return None, {}, missing
    bands = {h: d1_band(c_rt / disp[h]) for h in horizons}
    return F(sum(bands.values()), len(horizons)), bands, []


def sigma_gate(disp60, s: F, slip: F, label: str = "sigma_60") -> tuple[bool, str]:
    """(fails, arithmetic): the gate sigma_60 < 2 x c_RT, shown as "sigma_60 = x ticks vs 2 x (S + 0.5) = y ticks".
    Equality passes (the boundary goes to the higher score). Unknown sigma_60 fails."""
    need = 2 * (s + slip)
    if disp60 is None:
        return True, f"{label} unknown (no owned bars and no sibling under 2.4)"
    x, y = fmt_two(disp60, need)
    return disp60 < need, f"{label} = {x} ticks vs 2 x ({fmt_num(s)} + {fmt_num(slip)}) = {y} ticks"


def l_score(adv, spread, touch) -> tuple[int, list]:
    """D4 L. spread and touch are the sourced values or None (an unsourced spread or touch does not count).
    Unknown ADV: L = 1 (u); a sourced spread or touch can still raise it to 2."""
    notes = []
    if adv is None:
        lv = 1
        notes.append("D4 L: ADV unknown -> L = 1 (u)")
    elif adv < ADV_THIN:
        lv = 2
    elif adv < ADV_MID:
        lv = 1
    else:
        lv = 0
    if spread is not None:
        if spread > SPREAD_WIDE:
            lv = 2
        elif spread > SPREAD_MID:
            lv = max(lv, 1)
    if touch is not None:
        if touch < TOUCH_THIN:
            lv = 2
        elif touch < TOUCH_MID:
            lv = max(lv, 1)
    return lv, notes


def j_score(rd_p99_ticks, tick_value) -> tuple[int, list]:
    """D4 J: 1 if the p99 daily range of one contract exceeds DLL_ref = USD 1,000 (equality: 0); unknown: 1."""
    if rd_p99_ticks is None or tick_value is None:
        return 1, ["D4 J: R_d p99 or tick value unknown -> J = 1 (u)"]
    return (1 if rd_p99_ticks * tick_value > DLL_REF else 0), []


def below_l1_min(l1) -> bool:
    """L1 < 2.00 (flagged; the L1min2 gate). L1 = 2.00 exactly is not below (boundary to the higher score)."""
    return l1 is not None and l1 < L1_MIN


def parse_start(text) -> date | None:
    """YYYY-MM-DD, or YYYY-MM (read as the 1st: every h boundary is a month end, so the month decides)."""
    if text is None:
        return None
    s = str(text).strip()
    try:
        if len(s) == 7:
            return date.fromisoformat(s + "-01")
        return date.fromisoformat(s[:10])
    except ValueError as exc:
        raise InputError(f"mbo_start: not YYYY-MM-DD or YYYY-MM: {text!r}") from exc


def d5_h(mbo_start) -> tuple[int, str | None]:
    """MBO history start: on or before 2017-06-30: 0; to 2020-12-31: 1; 2021-01-01 or later: 2; unknown: 1."""
    d = parse_start(mbo_start)
    if d is None:
        return 1, "D5 h: MBO start unknown -> 1 (u)"
    return (0 if d <= H_CUT_EARLY else 1 if d <= H_CUT_LATE else 2), None


def d5_k(k_usd_month, k_kind) -> tuple[int, str | None]:
    """One month of front-contract MBO: at most USD 10: 0; at most 50: 1; above 50: 2; unknown: 1."""
    k = nonneg(k_usd_month, "D5 k")
    if k is None or str(k_kind or "").strip().lower() == "unknown":
        return 1, "D5 k: price unknown -> 1 (u)"
    return (0 if k <= K_LOW else 1 if k <= K_HIGH else 2), None


def d5_o(owned_36m) -> tuple[int, str | None]:
    """0 if owned bars or book data cover >= 36 months before 2024-03-01 outside every seal; else 1 (unknown: 1)."""
    if owned_36m is True:
        return 0, None
    return 1, (None if owned_36m is False else "D5 o: unknown -> 1 (u, the spec's else branch)")


def d5_p(all_read) -> tuple[int, str | None]:
    """1 if every pre-2024-03 window of >= 36 months has been read and none is sealed; else 0; unknown 0."""
    if all_read is True:
        return 1, None
    return 0, (None if all_read is False else "D5 p: unknown -> 0 (u)")


def attention_count(entry) -> int | None:
    """The OpenAlex meta.count, if the call succeeded (status 200 or "ok") and the count is a non-negative int."""
    cnt, st = entry.get("count"), entry.get("status")
    if isinstance(cnt, bool) or not isinstance(cnt, int) or cnt < 0:
        return None
    return cnt if st in (200, "200", "ok") else None


def attention_tiers(counts: dict) -> dict:
    """{underlying: (d, unknown)}. Terciles by count among underlyings with a count: with k = the number of
    underlyings with a strictly larger count and n = the number with a count, top (d = 1) if k < n/3, middle (0.5)
    if k < 2n/3, else bottom (0). Equal counts share k, so they take the higher tier. No count: d = 0.5 (u)."""
    known = [c for c in counts.values() if c is not None]
    n = len(known)
    out = {}
    for name, c in counts.items():
        if c is None:
            out[name] = (HALF, True)
            continue
        k = sum(1 for v in known if v > c)
        out[name] = ((F(1) if 3 * k < n else HALF if 3 * k < 2 * n else F(0)), False)
    return out


def code_attention(att_doc: dict, codes) -> dict:
    """{code: (d, note or None, underlying)} from F2_attention.json; every code on an underlying shares its d."""
    unders = (att_doc or {}).get("underlyings")
    if not isinstance(unders, dict):
        raise InputError("F2_attention.json: 'underlyings' object missing")
    counts, owner = {}, {}
    for name, entry in unders.items():
        counts[name] = attention_count(entry)
        for c in entry.get("codes", []):
            if c in owner:
                raise InputError(f"F2_attention.json: code {c} under two underlyings ({owner[c]}, {name})")
            owner[c] = name
    tiers = attention_tiers(counts)
    out = {}
    for c in codes:
        name = owner.get(c)
        if name is None:
            out[c] = (HALF, "D2 d: code under no underlying in F2_attention.json -> 0.5 (u)", None)
            continue
        d, unknown = tiers[name]
        out[c] = (d, (f"D2 d: count for {name} not obtained -> 0.5 (u)" if unknown else None), name)
    return out


# ------------------------------------------------------------------------------------------- per-code facts
class Layer1:
    """Layer 1 scores for every code under one Params."""

    def __init__(self, docs: dict, params: Params):
        self.p = params
        self.f3 = docs["F3"]["roots"]
        self.f4 = docs["F4"]["codes"]
        self.blind = (docs.get("blind") or {}).get("codes", {})
        self.att = code_attention(docs["attention"], list(self.f4))

    # F3 access ------------------------------------------------------------------------------------------
    def f3_status(self, code: str) -> str:
        """owned, OC1 or unknown; under OC1_off an OC1 code has no transfer, so its statistics are unknown."""
        st = (self.f3.get(code) or {}).get("status")
        if st == "OC1" and self.p.oc1_off:
            return "unknown"
        return st if st in ("owned", "OC1") else "unknown"

    def disp(self, code: str, h: str, field: str):
        """sigma_h (field "sigma") or m_h (field "m") in ticks; OC from the "OC" block; None if unknown."""
        if self.f3_status(code) == "unknown":
            return None
        root = self.f3[code]
        cell = root.get("OC") if h == "OC" else (root.get("h") or {}).get(h)
        return positive((cell or {}).get(field), f"F3 {code} {h} {field}")

    def rd(self, code: str, which: str):
        if self.f3_status(code) == "unknown":
            return None
        return positive((self.f3[code].get("R_d") or {}).get(which), f"F3 {code} R_d {which}")

    def _raw_close(self, code: str):
        return positive((self.f3.get(code) or {}).get("median_close"), f"F3 {code} median_close")

    def close(self, code: str) -> tuple:
        """F3 median close (price units); a code without one takes a same-price sibling's close (same price)."""
        own = self._raw_close(code)
        if own is not None:
            return own, None
        for s in sorted(SAME_PRICE_OF.get(code, ())):
            v = self._raw_close(s) if s != code else None
            if v is not None:
                return v, f"close of same-price sibling {s}"
        return None, None

    # F4 access ------------------------------------------------------------------------------------------
    def adv(self, code: str):
        return nonneg(((self.f4.get(code) or {}).get("adv") or {}).get("value"), f"F4 {code} adv")

    def mult(self, code: str):
        return positive((self.f4.get(code) or {}).get("multiplier"), f"F4 {code} multiplier")

    def siblings(self, code: str) -> list:
        return [s for s in (self.f4[code].get("siblings") or []) if s != code]

    def notional(self, code: str):
        """USD-notional ADV = ADV x multiplier x median close (spec 3 D2 c); None if any part is unknown."""
        if code not in self.f4:
            return None
        a, m = self.adv(code), self.mult(code)
        cl, _ = self.close(code)
        return None if a is None or m is None or cl is None else a * m * cl

    @staticmethod
    def same_price(a: str, b: str) -> bool:
        return b in SAME_PRICE_OF.get(a, ())

    def adv_ratio(self, sib: str, code: str):
        """USD-notional ADV of sib over code's; the price cancels between same-price siblings. None if unknown."""
        if sib not in self.f4:
            return None
        if self.same_price(sib, code):
            parts = (self.adv(sib), self.mult(sib), self.adv(code), self.mult(code))
            if any(v is None for v in parts):
                return None
            num, den = parts[0] * parts[1], parts[2] * parts[3]
        else:
            num, den = self.notional(sib), self.notional(code)
            if num is None or den is None:
                return None
        if den == 0:
            return INF if num > 0 else None
        return num / den

    def larger_size(self, sib: str, code: str):
        """True if sib's contract is larger (multiplier x price); None if that cannot be told."""
        ms, mc = (self.mult(sib) if sib in self.f4 else None), self.mult(code)
        if ms is None or mc is None:
            return None
        if self.same_price(sib, code):
            return ms > mc
        cs, cc = self.close(sib)[0], self.close(code)[0]
        return None if cs is None or cc is None else ms * cs > mc * cc

    def leader(self, code: str) -> tuple:
        """(leader, note): the sibling (or the code itself) with the largest USD-notional ADV on the underlying.
        Falls back to F4's leader field when the notionals cannot all be computed."""
        group = [code] + self.siblings(code)
        f4_leader = self.f4[code].get("leader")
        if all(self.same_price(code, g) for g in group[1:]):
            vals = {}
            for g in group:
                a, m = (self.adv(g), self.mult(g)) if g in self.f4 else (None, None)
                vals[g] = None if a is None or m is None else a * m
        else:
            vals = {g: self.notional(g) for g in group}
        if any(v is None for v in vals.values()):
            if f4_leader:
                return f4_leader, "leader from F4 (notional ADV not computable for every sibling)"
            return code, "leader unknown: own facts used"
        best = max(vals.values())
        tops = sorted(g for g in group if vals[g] == best)
        lead = f4_leader if f4_leader in tops else tops[0]
        note = (None if f4_leader in (None, lead)
                else f"F4 leader {f4_leader} differs from computed {lead}; computed used")
        return lead, note

    def family_c(self, code: str) -> tuple:
        """(c, lead note): 1 if code has the largest USD-notional ADV in its E.28 family (NQ included), else 0.
        Codes with an unknown notional cannot be compared: c is then provisional and the case goes to the lead."""
        members = [c for c in FAMILIES[FAMILY_OF[code]] if c in self.f4]
        vals = {c: self.notional(c) for c in members}
        known = {c: v for c, v in vals.items() if v is not None}
        unknown = sorted(c for c, v in vals.items() if v is None)
        own = vals.get(code)
        c = 1 if own is not None and own == max(known.values()) else 0
        if not unknown:
            return F(c), None
        return F(c), (f"D2 c ({code}): provisional, notional ADV unknown for {', '.join(unknown)} in family "
                      f"{FAMILY_OF[code]} (ADV, multiplier or F3 median close unknown); compared "
                      "among known codes only")

    def sat(self, code: str) -> dict:
        """D4 Sat by rule (i), (ii) and (iii), with notes."""
        out = {"i": False, "ii": False, "iii": False, "ratio_max": None, "u": [], "lead": []}
        for s in self.siblings(code):
            r = self.adv_ratio(s, code)
            if r is not None:
                out["ratio_max"] = r if out["ratio_max"] is None else max(out["ratio_max"], r)
                if r >= SAT_RATIO:
                    out["i"] = True
                continue
            larger = self.larger_size(s, code)
            if larger is True:
                out["i"] = True
                out["u"].append(f"Sat (i): ADV ratio to larger-size sibling {s} unknown -> holds (u)")
            elif larger is None:
                out["i"] = True
                out["lead"].append(f"Sat (i): ADV ratio and relative size to sibling {s} unknown -> counted as "
                                   "holding (script choice; spec only covers a known larger-size sibling)")
        so = self.f4[code].get("settles_off_sibling") or {}
        if so.get("value") is True:
            if so.get("item"):
                out["ii"] = True
            else:
                out["u"].append("Sat (ii): settlement off a sibling not sourced -> does not count")
        v, note = blind_rated(self.blind.get(code, {}).get("sat_iii"), 0, (0, 1), what="Sat (iii)")
        out["iii"] = v == 1
        if note:
            out["u"].append(note)
        return out

    def blind_cell(self, code: str, key: str):
        return (self.blind.get(code) or {}).get(key)

    # one code -------------------------------------------------------------------------------------------
    def spread(self, code: str) -> tuple:
        """(S, sourced S or None, note): the sourced median spread, else 1 (u); spread1 sets S = 1 everywhere."""
        sp = self.f4[code].get("spread_S") or {}
        if self.p.spread1:
            return F(1), None, None
        if sp.get("sourced") is True and sp.get("value") is not None:
            s = positive(sp["value"], f"F4 {code} spread_S")
            return s, s, None
        return F(1), None, "S: no sourced spread -> 1 tick (u)"

    def row(self, code: str) -> dict:
        base = {"code": code, "family": FAMILY_OF[code]}
        if code == NQ:
            return {**base, "status": "excluded (V49)", "gate_pass": False, "gate_reasons": ["excluded (V49)"]}
        p, f4 = self.p, self.f4[code]
        u, lead = [], []

        s, s_sourced, note = self.spread(code)
        u += [note] if note else []
        c_rt = s + p.slip
        field = "m" if p.dispersion == "mad" else "sigma"
        disp = {h: self.disp(code, h, field) for h in R_REPORTED}
        horizons = D1_ALL_H if p.d1_all else D1_H
        d1, bands, missing = d1_score(c_rt, disp, horizons)
        r = {h: (None if disp[h] is None else c_rt / disp[h]) for h in R_REPORTED}

        sat = self.sat(code)
        u += sat["u"]
        lead += sat["lead"]
        ldr, lnote = self.leader(code)
        lead += [f"leader: {lnote}"] if lnote else []
        follows_leader = (sat["i"] or sat["ii"]) and ldr != code
        src2 = ldr if follows_leader and not p.d2_own else code
        a, na = blind_rated(self.blind_cell(src2, "D2a"), 1, (0, 1), what=f"D2 a ({src2})")
        b, nb = blind_rated(self.blind_cell(src2, "D2b"), HALF, (0, HALF, 1), what=f"D2 b ({src2})")
        c, nc = self.family_c(src2)
        d, nd, under = self.att[code]
        u += [n for n in (na, nb, nd) if n]
        lead += [nc] if nc else []
        d2 = max(F(0), 4 - a - b - c - d)

        s1, n1 = blind_rated(self.blind_cell(code, "s1"), 0, (0, 1, 2), cap_s12, "D3 s1")
        s2, n2 = blind_rated(self.blind_cell(code, "s2"), 0, (0, 1, 2), cap_s12, "D3 s2")
        s3, n3 = blind_rated(self.blind_cell(code, "s3"), 0, (0, 1), what="D3 s3")
        u += [n for n in (n1, n2, n3) if n]
        d3 = min(F(4), s1 + s2 + s3)

        touch = f4.get("touch") or {}
        touch_v = (nonneg(touch["value"], f"F4 {code} touch") if touch.get("sourced") is True
                   and touch.get("value") is not None else None)
        lv, nl = l_score(self.adv(code), s_sourced, touch_v)
        jv, nj = j_score(self.rd(code, "p99"), positive(f4.get("tick_value_usd"), f"F4 {code} tick_value_usd"))
        u += nl + nj
        sat_any = 1 if (sat["i"] or sat["ii"] or sat["iii"]) else 0
        d4 = max(F(0), F(4 - lv - jv - p.sat_deduction * sat_any))

        da = f4.get("data_access") or {}
        hv, nh = d5_h(da.get("mbo_start"))
        kv, nk = d5_k(da.get("k_usd_month"), da.get("k_kind"))
        ov, no = d5_o(da.get("o_owned_36m"))
        pv, np_ = d5_p(da.get("p_all_read"))
        u += [n for n in (nh, nk, no, np_) if n]
        d5 = max(F(0), F(4 - hv - kv - ov - pv))

        src6 = ldr if follows_leader else code
        d6, n6 = blind_rated(self.blind_cell(src6, "D6"), 1, (0, 1, 2, 3, 4), cap_extreme_0_4, f"D6 ({src6})")
        u += [n6] if n6 else []

        crit = {"D1": d1, "D2": d2, "D3": d3, "D4": d4, "D5": d5, "D6": d6}
        l1 = None if d1 is None else sum(W_L1[k] * v for k, v in crit.items())

        label = "m_60" if p.dispersion == "mad" else "sigma_60"
        fails60, arith = sigma_gate(disp["60"], s, p.slip, label)
        reasons = []
        if disp["60"] is None:
            raw = (self.f3.get(code) or {}).get("status")
            reasons.append(arith + (" [variant OC1_off: no sibling transfer]" if p.oc1_off and raw == "OC1" else ""))
        else:
            if fails60:
                reasons.append(arith)
            if missing:
                reasons.append(f"{field}_{'/'.join(missing)} unknown: D1 cannot be scored (spec 3 D1: unknown sigma "
                               "fails the gate)")
                lead.append(f"gate: sigma_60 known but {field}_{'/'.join(missing)} unknown -> gate fails (script "
                            "reading of spec 3 D1 'Unknown sigma: the contract fails the Layer 1 gate')")
        if d4 == 0:
            reasons.append("D4 = 0")
        if p.l1min2 and below_l1_min(l1):
            reasons.append(f"L1 = {float(l1):.4f} < 2.00 (variant L1min2)")

        return {
            **base, "status": "scored", "f3_status": self.f3_status(code), "S": s, "S_sourced": s_sourced is not None,
            "slip": p.slip, "c_RT": c_rt, "dispersion": field, "disp": disp, "r": r,
            "r_5": r["5"], "r_15": r["15"], "r_OC": r["OC"], "D1_horizons": list(horizons), "D1_bands": bands,
            "sigma_240": self.disp(code, "240", "sigma"), "rd_median": self.rd(code, "median"),
            "rd_p99": self.rd(code, "p99"),
            "D1": d1, "D2": d2, "D3": d3, "D4": d4, "D5": d5, "D6": d6,
            "D2_parts": {"a": a, "b": b, "c": c, "d": d, "facts_of": src2, "underlying": under},
            "D3_parts": {"s1": s1, "s2": s2, "s3": s3},
            "D4_parts": {"L": lv, "J": jv, "Sat": sat_any, "sat_i": sat["i"], "sat_ii": sat["ii"],
                         "sat_iii": sat["iii"], "sib_ratio_max": sat["ratio_max"], "leader": ldr,
                         "sat_deduction": p.sat_deduction},
            "D5_parts": {"h": hv, "k": kv, "o": ov, "p": pv},
            "D6_parts": {"evidence_of": src6},
            "L1": l1, "L1_below_2": below_l1_min(l1),
            "gate_pass": not reasons, "gate_reasons": reasons, "gate_arithmetic": arith,
            "u": u, "lead": lead,
        }


def layer1_rows(docs: dict, params: Params) -> dict:
    l1 = Layer1(docs, params)
    return {c: l1.row(c) for c in sorted(docs["F4"]["codes"])}


__all__ = ["Layer1", "layer1_rows", "d1_band", "d1_score", "sigma_gate", "l_score", "j_score", "d5_h", "d5_k",
           "d5_o", "d5_p", "attention_tiers", "attention_count", "code_attention", "W_L1", "q"]
