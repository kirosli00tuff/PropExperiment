"""r3_score.py: spec section 8.3, the R3 rule. Q4 to Q7 by script, C, the ties and the R4 selection, from a
combinations file (schema: SCHEMA.md section "combinations file"). Q1 to Q3 come from the CombinationScorer.

Run: uv run python reports/stage_e32b_briefs/work/score/r3_score.py --combos <combinations.json> --out <out.json>
Refuses to run unless the spec's sha256 is the frozen one.
"""
from __future__ import annotations

import argparse
import math
import os
import sys
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from s32b_common import (  # noqa: E402
    FAMILY_OF,
    FIRMS,
    INF,
    SPEC_PATH,
    InputError,
    SpecHashError,
    band_le,
    blind_rated,
    cap_extreme_0_4,
    check_doc_hash,
    check_spec,
    file_sha256,
    load_json,
    now_pdt,
    positive,
    q,
    round2,
    write_json,
)

OWN_BROKER_VENUES = ("ibkr",)
BAND_H = ("5", "15", "30", "60", "120", "240", "OC")
W_C = {"Q1": F("0.20"), "Q2": F("0.10"), "Q3": F("0.10"), "Q4": F("0.15"), "Q5": F("0.15"), "Q6": F("0.15"),
       "Q7": F("0.15")}
Q4_STEPS = ((F("0.025"), 4), (F("0.05"), 3), (F("0.10"), 2), (F("0.20"), 1))
Q5_STEPS = ((F("0.05"), 4), (F("0.10"), 3), (F("0.20"), 2), (F("0.40"), 1))
T_TEST = 870                         # spec 9.2
ENTRY_CAP = 20                       # spec 9.2: the program's entry cap
DLL_TIGHT, DLL_MID = F("1.5"), F(3)
NEWS_EVENTS_MIN = 2
CEILING_DEFAULT = F(6000)            # spec 8.3 Q6: when DECISIONS.md records no own-account ceiling (u)
SIGMA_DAY_SHARE = F("0.02")
DISC_COST_MAX, ALL_COST_MAX = F(50), F(200)
WIN_FULL, WIN_MIN = 36, 24
RHO_SAME_CLASS, RHO_CROSS_CLASS = F("0.5"), F("0.3")
C_STRONG = F(2)
R4_N = 5
GATE_FLAGS = ("news_window_covers_event_trade", "overnight_needed_but_prohibited", "holds_past_flat_by_close")


# ------------------------------------------------------------------------------------------------ Q4 to Q7
def q4_score(c_f: F, sigma_hc: F) -> tuple[int, F]:
    """x = c_f / sigma_hc; <= 0.025: 4; <= 0.05: 3; <= 0.10: 2; <= 0.20: 1; else 0."""
    x = c_f / sigma_hc
    return band_le(x, Q4_STEPS), x


def q5_score(sr80_test: F, k: F) -> tuple[int, float]:
    """q = SR80_test sqrt(870) / sqrt(K); <= 0.05: 4; <= 0.10: 3; <= 0.20: 2; <= 0.40: 1; else 0.
    Compared exactly as q^2 = SR80^2 x 870 / K against the squared limits."""
    if k <= 0:
        return 0, INF
    q2 = sr80_test * sr80_test * T_TEST / k
    score = next((s for lim, s in Q5_STEPS if q2 <= lim * lim), 0)
    return score, math.sqrt(float(q2))


def n_cap(h_c: str, l_main) -> int:
    """n_cap(h) = min(20, floor(L_main / h)); OC and overnight holds: 1 a day (spec 7)."""
    if h_c == "OC":
        return 1
    return min(ENTRY_CAP, int(math.floor(l_main / int(h_c))))


def g_value(c_f: F, sigma_hc: F, sr80_test: F, ncap: int) -> float:
    """G(h_c) = c_f / sigma_hc + SR80_test / sqrt(n_cap(h_c)) (spec 7), the second tie level."""
    if ncap <= 0:
        return INF
    return float(c_f / sigma_hc) + float(sr80_test) / math.sqrt(ncap)


def gate_reasons(member: dict) -> list:
    g = member.get("gate") or {}
    return [f"{member['code']}: {k}" for k in GATE_FLAGS if g.get(k) is True]


def q6_prop(m: dict) -> tuple:
    """(Q6, deductions, notes) at a prop venue: 4 minus 2 if DLL_f / (sigma_hc v) < 1.5, else 1 if < 3; 1 if the
    daily payout-qualification threshold exceeds sqrt(n/day) sigma_hc v; 1 if news windows stop the family around
    2 or more scheduled events a week; floor 0. DLL "none": the firm's MLL is used (spec 4 D convention)."""
    notes, deds = [], {}
    sv = m["sigma_hc_ticks"] * m["tick_value_usd"]
    dll = m.get("dll_usd")
    dll = m.get("mll_usd") if dll == "none" else dll
    if dll is None:
        deds["dll"] = 2
        notes.append(f"Q6 {m['code']}: DLL unknown -> 2 (script choice, conservative)")
    else:
        ratio = dll / sv
        deds["dll"] = 2 if ratio < DLL_TIGHT else (1 if ratio < DLL_MID else 0)
    thr, n = m.get("payout_threshold_usd"), m.get("n_per_day")
    if thr is None or n is None:
        deds["payout"] = 1
        notes.append(f"Q6 {m['code']}: payout threshold or trades a day unknown -> 1 (script choice)")
    else:
        deds["payout"] = 1 if thr * thr > n * sv * sv else 0    # thr > sqrt(n) sigma v, exact
    ev = m.get("news_stop_events_per_week")
    if ev is None:
        deds["news"] = 1
        notes.append(f"Q6 {m['code']}: news-window event count unknown -> 1 (script choice)")
    else:
        deds["news"] = 1 if ev >= NEWS_EVENTS_MIN else 0
    return max(0, 4 - sum(deds.values())), deds, notes


def q6_own(m: dict, ceiling: F) -> tuple:
    """(Q6, deductions, notes) at the own-broker venue: 4 minus 2 if one contract's initial margin exceeds the
    capital ceiling, minus 1 if sigma_day at one contract exceeds 2% of it."""
    notes, deds = [], {}
    margin = m.get("initial_margin_usd")
    if margin is None:
        deds["margin"] = 2
        notes.append(f"Q6 {m['code']}: initial margin unknown -> 2 (script choice)")
    else:
        deds["margin"] = 2 if margin > ceiling else 0
    sd = m.get("sigma_day_ticks")
    if sd is None:
        deds["sigma_day"] = 1
        notes.append(f"Q6 {m['code']}: sigma_day unknown -> 1 (script choice)")
    else:
        deds["sigma_day"] = 1 if sd * m["tick_value_usd"] > SIGMA_DAY_SHARE * ceiling else 0
    return max(0, 4 - sum(deds.values())), deds, notes


def q7_score(data: dict) -> tuple:
    """(Q7, deductions, notes): 4 minus 1 if discovery data costs more than USD 50; 1 more if all data needed
    costs more than USD 200; 1 if no clean test window of 36 months before 2024-03, 2 if none of 24; floor 0."""
    notes, deds = [], {}
    disc = q(data.get("discovery_cost_usd"), "data.discovery_cost_usd")
    alld = q(data.get("all_data_cost_usd"), "data.all_data_cost_usd")
    months = q(data.get("clean_test_window_months"), "data.clean_test_window_months")
    if disc is None:
        notes.append("Q7: discovery data cost unknown -> 1 (script choice)")
    deds["discovery_over_50"] = 1 if disc is None or disc > DISC_COST_MAX else 0
    if alld is None:
        notes.append("Q7: all-data cost unknown -> 1 (script choice)")
    deds["all_over_200"] = 1 if alld is None or alld > ALL_COST_MAX else 0
    if months is None:
        notes.append("Q7: clean test window unknown -> 2 (script choice)")
        deds["test_window"] = 2
    else:
        deds["test_window"] = 0 if months >= WIN_FULL else (1 if months >= WIN_MIN else 2)
    return max(0, 4 - sum(deds.values())), deds, notes


def pool_rho(codes_classes: list, measured: dict) -> tuple[F, list]:
    """Mean pairwise rho over the pool's members: measured (E.29 3.2) where given, else 0.5 within an asset class
    and 0.3 across classes. Returns (rho, notes)."""
    vals, notes = [], []
    for i in range(len(codes_classes)):
        for j in range(i + 1, len(codes_classes)):
            (a, ca), (b, cb) = codes_classes[i], codes_classes[j]
            meas = measured.get(f"{a}|{b}") or measured.get(f"{b}|{a}")
            if meas is not None and meas.get("value") is not None:
                vals.append(q(meas["value"], f"rho {a}|{b}"))
                notes.append(f"rho {a}|{b} measured {meas['value']}")
            else:
                vals.append(RHO_SAME_CLASS if ca == cb else RHO_CROSS_CLASS)
    return (sum(vals) / len(vals)) if vals else F(0), notes


def k_eff(k_total: F, m: int, rho: F) -> F:
    """K_eff = K_total / (1 + (m - 1) rho) (spec 8.3 pools)."""
    return k_total / (1 + (m - 1) * rho)


# ------------------------------------------------------------------------------------------------ one combination
def _member(raw: dict, cid: str, h_c: str) -> dict:
    code = raw.get("code")
    if code not in FAMILY_OF:
        raise InputError(f"combination {cid}: member code {code!r} not a spec code")
    m = {"code": code, "asset_class": raw.get("asset_class") or FAMILY_OF[code],
         "c_f_ticks": positive(raw.get("c_f_ticks"), f"{cid} {code} c_f_ticks"),
         "sigma_hc_ticks": positive(raw.get("sigma_hc_ticks"), f"{cid} {code} sigma_hc_ticks"),
         "tick_value_usd": positive(raw.get("tick_value_usd"), f"{cid} {code} tick_value_usd"),
         "K_test": positive(raw.get("K_test"), f"{cid} {code} K_test"),
         "L_main": positive(raw.get("L_main"), f"{cid} {code} L_main"),
         "dll_usd": "none" if raw.get("dll_usd") == "none" else positive(raw.get("dll_usd"), f"{cid} dll"),
         "mll_usd": positive(raw.get("mll_usd"), f"{cid} {code} mll_usd"),
         "payout_threshold_usd": q(raw.get("payout_threshold_usd"), f"{cid} payout"),
         "n_per_day": positive(raw.get("n_per_day"), f"{cid} {code} n_per_day"),
         "news_stop_events_per_week": q(raw.get("news_stop_events_per_week"), f"{cid} news"),
         "initial_margin_usd": q(raw.get("initial_margin_usd"), f"{cid} margin"),
         "sigma_day_ticks": positive(raw.get("sigma_day_ticks"), f"{cid} sigma_day"),
         "gate": raw.get("gate") or {}}
    for k in ("c_f_ticks", "sigma_hc_ticks", "tick_value_usd", "K_test"):
        if m[k] is None:
            raise InputError(f"combination {cid}: member {code} lacks {k}")
    if m["L_main"] is None and h_c != "OC":
        raise InputError(f"combination {cid}: member {code} lacks L_main")
    return m


def _rating(c: dict, key: str, cid: str):
    r = c.get(key)
    if not isinstance(r, dict) or r.get("value") is None or r.get("unknown") is True:
        raise InputError(f"combination {cid}: {key} rating missing (CombinationScorer rates every Q1 to Q3)")
    cap = cap_extreme_0_4 if key == "Q2" else None
    v, note = blind_rated(r, 0, (0, 1, 2, 3, 4), cap, f"{key}")
    return v, note


def combo_row(c: dict, sr80: F, ceiling: F, ceiling_u: bool, measured: dict) -> dict:
    cid = str(c.get("id"))
    venue = c.get("venue")
    if venue not in FIRMS + OWN_BROKER_VENUES:
        raise InputError(f"combination {cid}: venue {venue!r} not one of {FIRMS + OWN_BROKER_VENUES}")
    kind = "own_broker" if venue in OWN_BROKER_VENUES else "prop"
    band = [str(h) for h in c.get("band") or []]
    h_c = str(c.get("h_c"))
    if not band or any(h not in BAND_H for h in band) or h_c not in band:
        raise InputError(f"combination {cid}: band {band} must be within {BAND_H} and contain h_c {h_c}")
    product, pool = c.get("product"), c.get("pool")
    if (product is None) == (pool is None):
        raise InputError(f"combination {cid}: exactly one of product and pool")
    members = [_member(m, cid, h_c) for m in c.get("members") or []]
    codes = [m["code"] for m in members]
    if product is not None and codes != [product]:
        raise InputError(f"combination {cid}: a product combination has one member, the product")
    if pool is not None and (len(codes) < 2 or sorted(codes) != sorted(pool.get("members") or [])):
        raise InputError(f"combination {cid}: pool members must match the member entries (at least 2)")
    name = product if product is not None else pool.get("name")
    notes, lead = [], []

    qv = {}
    for k in ("Q1", "Q2", "Q3"):
        qv[k], note = _rating(c, k, cid)
        notes += [note] if note else []

    q4s = [q4_score(m["c_f_ticks"], m["sigma_hc_ticks"]) for m in members]
    worst4 = min(range(len(members)), key=lambda i: (q4s[i][0], -q4s[i][1]))
    qv["Q4"], x = F(q4s[worst4][0]), q4s[worst4][1]
    if pool is not None:
        lead.append("Q4 pool: worst member's x used (spec names the worst member only for Q6)")

    if pool is None:
        k_used, rho = members[0]["K_test"], None
    else:
        rho, rnotes = pool_rho([(m["code"], m["asset_class"]) for m in members], measured)
        notes += rnotes
        k_used = k_eff(sum(m["K_test"] for m in members), len(members), rho)
    q5v, qval = q5_score(sr80, k_used)
    qv["Q5"] = F(q5v)

    gates = [g for m in members for g in gate_reasons(m)]
    q6s = []
    for m in members:
        s6, d6, n6 = q6_own(m, ceiling) if kind == "own_broker" else q6_prop(m)
        q6s.append((s6, d6, m["code"]))
        lead += n6
    if kind == "own_broker" and ceiling_u:
        notes.append("Q6: own-account capital ceiling not recorded -> USD 6,000 (u)")
    qv["Q6"] = F(min(s for s, _, _ in q6s))
    if pool is not None and gates:
        lead.append("pool gate: a member's core trades are prohibited -> the pool is excluded (script choice)")

    q7v, d7, n7 = q7_score(c.get("data") or {})
    qv["Q7"] = F(q7v)
    lead += n7
    if qv["Q3"] == 0:
        gates.append("Q3 = 0: re-tests a closed line")

    cval = sum(W_C[k] * qv[k] for k in W_C)
    gs = [g_value(m["c_f_ticks"], m["sigma_hc_ticks"], sr80, n_cap(h_c, m["L_main"])) for m in members]
    return {"id": cid, "product": product, "pool": pool, "name": name, "venue": venue, "venue_kind": kind,
            "family": c.get("family"), "band": band, "h_c": h_c, **qv, "C": cval, "C_rounded": round2(cval),
            "x": x, "q": qval, "K_used": k_used, "rho": rho, "G_hc": max(gs),
            "Q6_by_member": {code: {"Q6": s, "deductions": d} for s, d, code in q6s}, "Q7_deductions": d7,
            "status": "excluded" if gates else "eligible", "gate_reasons": gates, "u": notes, "lead": lead}


# ------------------------------------------------------------------------------------------------ ordering
TIE_LEVELS = ("C rounded", "Q1", "G(h_c)", "product code", "venue", "family name")


def rank_key(r: dict) -> tuple:
    """Spec 8.3: C equal at 2 decimals (half-up); then higher Q1, lower G(h_c), product code, venue, family name."""
    return (-r["C_rounded"], -r["Q1"], r["G_hc"], r["name"], r["venue"], r["family"] or "")


def find_ties(ranked: list) -> list:
    out, i = [], 0
    while i < len(ranked):
        j = i
        while j + 1 < len(ranked) and ranked[j + 1]["C_rounded"] == ranked[i]["C_rounded"]:
            j += 1
        if j > i:
            g = ranked[i:j + 1]
            steps = []
            for a, b in zip(g, g[1:], strict=False):
                ka, kb = rank_key(a), rank_key(b)
                lvl = next((n for n in range(len(ka)) if ka[n] != kb[n]), len(ka) - 1)
                steps.append({"higher": a["id"], "lower": b["id"], "decided_by": TIE_LEVELS[lvl]})
            out.append({"C_rounded": g[0]["C_rounded"], "ids": [r["id"] for r in g], "steps": steps})
        i = j + 1
    return out


def r4_select(ordered: list, prop_only: bool = False) -> dict:
    """The top 5 distinct (product or pool, idea family) by their best C, each with its best venue and band;
    C < 2.00 marked weak; says whether fewer than 3 reach 2.00."""
    picks, seen = [], set()
    for r in ordered:
        if prop_only and r["venue_kind"] != "prop":
            continue
        key = (r["name"], r["family"])
        if key in seen:
            continue
        seen.add(key)
        picks.append({"rank": len(picks) + 1, "product_or_pool": r["name"], "family": r["family"], "id": r["id"],
                      "best_venue": r["venue"], "band": r["band"], "h_c": r["h_c"], "C": r["C"],
                      "C_rounded": r["C_rounded"], "weak": r["C"] < C_STRONG})
        if len(picks) == R4_N:
            break
    n_strong = sum(1 for p in picks if not p["weak"])
    return {"candidates": picks, "n_reaching_2": n_strong, "fewer_than_3_reach_2": n_strong < 3}


def run_r3(doc: dict, spec_path=SPEC_PATH, input_meta: dict | None = None) -> dict:
    spec = check_spec(spec_path)
    check_doc_hash(doc, "combinations file")
    sr80 = positive((doc.get("sr80_test") or {}).get("value"), "sr80_test.value")
    if sr80 is None:
        raise InputError("combinations file: sr80_test.value required (from briefs/work/F5/SR80.json)")
    ceil_raw = (doc.get("own_account_capital_ceiling_usd") or {}).get("value")
    ceiling = positive(ceil_raw, "own_account_capital_ceiling_usd") or CEILING_DEFAULT
    measured = doc.get("rho_measured") or {}
    combos = doc.get("combinations") or []
    ids = [str(c.get("id")) for c in combos]
    if len(set(ids)) != len(ids):
        raise InputError("combinations file: ids must be unique")
    rows = [combo_row(c, sr80, ceiling, ceil_raw is None, measured) for c in combos]
    eligible = sorted((r for r in rows if r["status"] == "eligible"), key=rank_key)
    ranked = [{**r, "rank": i} for i, r in enumerate(eligible, 1)]
    rest = sorted(({**r, "rank": None} for r in rows if r["status"] != "eligible"), key=lambda r: r["id"])
    own = [r for r in ranked if r["venue_kind"] == "own_broker"]
    for_lead = [{"where": r["id"], "note": n} for r in ranked + rest for n in dict.fromkeys(r["lead"])]
    return {"spec_sha256": spec, "generated_pdt": now_pdt(), "script": "r3_score.py", "inputs": input_meta or {},
            "sr80_test": sr80, "capital_ceiling_usd": ceiling, "capital_ceiling_u": ceil_raw is None,
            "combinations": ranked + rest, "ties": find_ties(ranked), "R4": r4_select(ranked),
            "R4_prop_only": r4_select(ranked, prop_only=True),
            "best_own_broker": own[0] if own else None, "for_lead": for_lead}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--combos", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--spec", default=str(SPEC_PATH))
    args = ap.parse_args(argv)
    try:
        check_spec(args.spec)
        doc = load_json(args.combos)
        out = run_r3(doc, args.spec, {"combos": {"path": args.combos, "sha256": file_sha256(args.combos)}})
    except (SpecHashError, InputError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    write_json(args.out, out)
    r4 = out["R4"]
    print(f"combinations {len(out['combinations'])}; R4: "
          f"{[(p['product_or_pool'], p['family'], p['best_venue'], float(p['C'])) for p in r4['candidates']]}; "
          f"fewer than 3 reach 2.00: {r4['fewer_than_3_reach_2']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
