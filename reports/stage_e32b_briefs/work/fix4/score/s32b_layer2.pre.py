"""Layer 2 (spec section 4): E, R, A, D, Rel, P, the Layer 2 gates, L2 and S for every (firm, code) pair."""
from __future__ import annotations

from fractions import Fraction as F

from s32b_common import (
    INF,
    NQ,
    InputError,
    Params,
    band_ge,
    blind_rated,
    fmt_num,
    positive,
    q,
    s_fn,
)

W_L2 = {"E": F("0.40"), "R": F("0.15"), "A": F("0.15"), "D": F("0.15"), "Rel": F("0.10"), "P": F("0.05")}
ROOM_STEPS = ((F(4), 4), (F(3), 3), (F(2), 2), (F(1), 1))
E_X0_MSTAR, E_X0_M10K = F("0.20"), F("0.30")
REL_KEYS = {"rel_age": (0, 1), "rel_payout": (0, 1), "rel_rules": (0, 1), "rel_regulatory": (0, 2)}
P_RATE_MIN = F(10)


def e_score(block: dict, what: str = "E") -> tuple:
    """(E, m*, m10K, cost per attempt). E = 0.75 s(m*; 0.20) + 0.25 s(m10K; 0.30); a threshold above the grid cap
    scores 0 for its component and counts as m = inf in the tie rule."""
    cap = block.get("above_cap") or {}

    def comp(key: str, flag: str, x0: F):
        if cap.get(flag) is True:
            return F(0), INF
        v = q(block.get(key), f"{what} {key}")
        if v is None:
            raise InputError(f"{what}: {key} missing and above_cap.{flag} is not true")
        if v < 0:
            raise InputError(f"{what}: {key} negative")
        return s_fn(v, x0), v

    c1, m_star = comp("m_star", "mu_star", E_X0_MSTAR)
    c2, m10k = comp("m10K", "mu10K", E_X0_M10K)
    cost = q(block.get("cost_per_attempt"), f"{what} cost_per_attempt")
    return F("0.75") * c1 + F("0.25") * c2, m_star, m10k, cost


def room_band(room) -> int:
    """>= 4: 4; >= 3: 3; >= 2: 2; >= 1: 1; < 1: 0 (boundaries to the higher score)."""
    return band_ge(room, ROOM_STEPS)


def d_score(dll, mll, sigma240, rd_median, v) -> tuple:
    """(D, room_a, room_b, u notes, lead notes). room_a = DLL_f / (sigma_240 v), DLL_f = the MLL where the firm has
    no daily limit (dll == "none"); room_b = MLL_f / (R_d v). Unknown sigma_240 or R_d: that band scores 1 (u).
    Unknown DLL or MLL is not covered by the spec: the same band-1 rule is applied and the lead is told."""
    u, lead = [], []
    dll_f = mll if dll == "none" else dll
    room_a = room_b = None
    if sigma240 is None or v is None:
        band_a = 1
        u.append("D room_a: sigma_240 or tick value unknown -> 1 (u)")
    elif dll_f is None:
        band_a = 1
        lead.append("D room_a: firm DLL (or MLL where no DLL) unknown -> band 1 (script choice, E.28 OC-A3-2 analogue)")
    else:
        room_a = dll_f / (sigma240 * v)
        band_a = room_band(room_a)
    if rd_median is None or v is None:
        band_b = 1
        u.append("D room_b: R_d median or tick value unknown -> 1 (u)")
    elif mll is None:
        band_b = 1
        lead.append("D room_b: firm MLL unknown -> band 1 (script choice, E.28 OC-A3-2 analogue)")
    else:
        room_b = mll / (rd_median * v)
        band_b = room_band(room_b)
    return F(band_a + band_b, 2), room_a, room_b, u, lead


def rel_score(firm_blind: dict, what: str = "Rel") -> tuple:
    """(Rel, deductions, lead notes): 4 minus the blind deductions (age 1, payout 1, rules 1, regulatory 2), floor
    0. An unknown deduction counts 0 (a deduction needs a documented fact; E.28 score.py did the same)."""
    deds, lead = {}, []
    for key, allowed in REL_KEYS.items():
        r = (firm_blind or {}).get(key)
        if not isinstance(r, dict) or r.get("unknown") is True or r.get("value") is None:
            deds[key] = F(0)
            lead.append(f"{what} {key}: unknown -> no deduction (spec names no default; E.28 practice)")
            continue
        v = q(r["value"], f"{what} {key}")
        if v not in {F(a) for a in allowed}:
            raise InputError(f"{what} {key}: deduction {r['value']} not in {allowed}")
        deds[key] = v
    return max(F(0), 4 - sum(deds.values())), deds, lead


def p_score(p_inputs: dict) -> tuple:
    """(P, deductions, u notes): 4 minus one for each: no native or documented API; no native OCO or bracket orders
    on the API; a VPS near Chicago prohibited or unknown; a documented API rate limit below 10 orders a second, or
    unknown. Unknown items count as holding (E.28 rubric). "no_limit" = a documented absence of any rate limit."""
    pin = p_inputs or {}
    u = []
    native, oco, vps, rate = (pin.get(k) for k in ("native_api", "oco_api", "vps_chicago", "api_rate_limit_per_s"))
    deds = {"no_native_api": native is not True, "no_api_oco": oco is not True,
            "vps_prohibited_or_unknown": not (vps is True or vps == "allowed")}
    for k, v in (("native_api", native), ("oco_api", oco)):
        if v is None:
            u.append(f"P {k}: unknown -> deduction (u)")
    if vps is None or vps == "unknown":
        u.append("P vps_chicago: unknown -> deduction (u)")
    if rate == "no_limit":
        deds["rate_below_10_or_unknown"] = False
    elif rate is None or rate == "unknown":
        deds["rate_below_10_or_unknown"] = True
        u.append("P api_rate_limit_per_s: unknown -> deduction (u)")
    else:
        deds["rate_below_10_or_unknown"] = positive(rate, "P api_rate_limit_per_s") < P_RATE_MIN
    return max(F(0), F(4 - sum(deds.values()))), deds, u


def pair_row(key: str, docs: dict, params: Params, l1rows: dict) -> dict:
    firm, code = key.split("|")
    base = {"key": key, "firm": firm, "code": code, "rank": None}
    if code == NQ:
        return {**base, "status": "excluded (V49)", "gate_reasons": ["excluded (V49)"]}
    f4 = docs["F4"]
    pf, ff = f4["pairs"][key], f4["firms"][firm]
    bl = docs.get("blind") or {}
    l1 = l1rows[code]
    u, lead, gates = [], [], []

    listed = pf.get("listed_50k")
    if listed is False:
        gates.append("not listed for the 50K plan")
    elif listed is not True:
        gates.append("50K listing unknown")
        lead.append("gate: listed_50k unknown -> excluded (script choice; spec gates on 'does not list')")
    bc = ff.get("bc_accepts")
    if bc is False:
        gates.append("British Columbia residents not accepted")
    elif bc is not True:
        gates.append("BC acceptance unknown")
        lead.append("gate: bc_accepts unknown -> excluded (script choice; spec gates on 'does not accept')")

    pb = (bl.get("pairs") or {}).get(key) or {}
    r_v, nr = blind_rated(pb.get("R"), 1, (1, 2, 3, 4), what="R")
    a_v, na = blind_rated(pb.get("A"), 1, (0, 1, 2, 3, 4), what="A")
    u += [n for n in (nr, na) if n]
    if a_v == 0:
        gates.append("A = 0")

    block_name = params.econ_block()
    block = ((docs["econ"].get("pairs") or {}).get(key) or {}).get(block_name)
    e_v = m_star = m10k = cost = None
    if block is not None:
        e_v, m_star, m10k, cost = e_score(block, f"econ {key} {block_name}")
    elif l1.get("gate_pass") and not gates:
        raise InputError(f"econ32b.json: pair {key} has no '{block_name}' block but is eligible for ranking")

    code_f4 = f4["codes"][code]
    v = positive(code_f4.get("tick_value_usd"), f"F4 {code} tick_value_usd")
    sig240, rdm = l1.get("sigma_240"), l1.get("rd_median")   # D uses sigma_240 in every variant (mad: D1 and gate)
    dll = ff.get("dll_50k")
    dll = "none" if dll == "none" else positive(dll, f"F4 {firm} dll_50k")
    mll = positive(ff.get("mll_50k"), f"F4 {firm} mll_50k")
    d_v, room_a, room_b, du, dlead = d_score(dll, mll, sig240, rdm, v)
    u += du
    lead += dlead

    rel_v, rel_d, rel_lead = rel_score((bl.get("firms") or {}).get(firm), f"Rel ({firm})")
    lead += rel_lead
    p_v, p_d, pu = p_score(ff.get("p_inputs"))
    u += pu

    crit = {"E": e_v, "R": r_v, "A": a_v, "D": d_v, "Rel": rel_v, "P": p_v}
    l2 = None if e_v is None else sum(W_L2[k] * val for k, val in crit.items())
    l1v = l1.get("L1")
    s_v = None if l1v is None or l2 is None else (l1v + l2) / 2

    if not l1.get("gate_pass"):
        status = "Layer 1 gate"
    elif gates:
        status = "Layer 2 gate"
    else:
        status = "ranked"
    return {
        **base, "status": status,
        "gate_reasons": ([] if l1.get("gate_pass") else ["Layer 1: " + "; ".join(l1.get("gate_reasons", []))])
        + gates,
        "L1": l1v, "L2": l2, "S": s_v, **crit, "m_star": m_star, "m10K": m10k, "cost_per_attempt": cost,
        "econ_block": block_name, "room_a": room_a, "room_b": room_b, "Rel_deductions": rel_d, "P_deductions": p_d,
        "fee_rt_usd": pf.get("fee_rt_usd"), "fee_kind": pf.get("fee_kind"), "u": u, "lead": lead,
    }


def layer2_rows(docs: dict, params: Params, l1rows: dict) -> list:
    return [pair_row(k, docs, params, l1rows) for k in sorted(docs["F4"]["pairs"])]


__all__ = ["e_score", "room_band", "d_score", "rel_score", "p_score", "pair_row", "layer2_rows", "W_L2", "fmt_num"]
