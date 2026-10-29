"""Tables for reports/stage_e32b_ranking.md (RankingWriter, Stage E.32b D3).

Reads the score run and its inputs (read-only) and writes markdown fragments to work/rankmd/out/ plus
facts.json (numbers quoted in the narrative). assemble.py fills template.md with the fragments.
Nothing here scores anything: every value is copied from score32b_out.json / econ32b.json / F4 facts,
except the arithmetic named in each table note (unit conversions, deviations from the ranked-pair mean).
"""
import json
from pathlib import Path

B = Path(__file__).resolve().parents[2]  # reports/stage_e32b_briefs
OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(exist_ok=True)

SC = json.loads((B / "score32b_out.json").read_text())
EC = json.loads((B / "econ32b.json").read_text())
F4 = json.loads((B / "F4_facts_unmasked.json").read_text())
PRI = SC["primary"]
L1 = PRI["layer1"]
PAIRS = PRI["pairs"]
W2 = {"E": 0.40, "R": 0.15, "A": 0.15, "D": 0.15, "Rel": 0.10, "P": 0.05}
W1 = {"D1": 0.30, "D2": 0.15, "D3": 0.15, "D4": 0.15, "D5": 0.10, "D6": 0.15}
HS = ["30", "60", "120", "240"]
FIRM = {"bulenox": "Bulenox", "lucid": "Lucid", "mffu": "MFFU", "topstep": "Topstep", "tradeify": "Tradeify"}


def f(x, n=2):
    if x is None:
        return "-"
    if isinstance(x, bool):
        return "yes" if x else "no"
    if isinstance(x, (int, float)):
        return f"{x:.{n}f}"
    return str(x)


def table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out) + "\n"


def sat_rule(r):
    p = r["D4_parts"]
    if not p["Sat"]:
        why = "Sat 0"
        if p.get("sib_ratio_max") is not None and p["leader"] != r["code"]:
            why += f" (largest sibling ratio {p['sib_ratio_max']:.2f}x < 5)"
        return why
    parts = []
    if p["sat_i"]:
        unk = [u for u in r["u"] if u.startswith("Sat (i)")]
        if unk:
            parts.append("(i) ratio unknown -> holds (u)")
        else:
            parts.append(f"(i) {p['leader']} has {p['sib_ratio_max']:.1f}x its notional ADV")
    if p["sat_ii"]:
        parts.append(f"(ii) settles off a sibling")
    if p["sat_iii"]:
        parts.append("(iii) rated")
    return "Sat 1: " + "; ".join(parts)


def tick_value(code):
    return F4["codes"][code]["tick_value_usd"]


# ---------------- Section 2: Layer 1 ----------------
def sec2():
    codes = sorted(L1)
    rows_a, rows_b, rows_c = [], [], []
    for c in codes:
        r = L1[c]
        if r.get("status") != "scored":
            rows_a.append([c, "excluded (V49)"] + [""] * 10)
            rows_b.append([c, "excluded (V49)"] + [""] * 11)
            rows_c.append([c, "excluded (V49)", "not ranked", ""])
            continue
        s_lab = f"{r['S']:g}" + ("" if r["S_sourced"] else " (u)")
        if c == "HG":
            s_lab = "1 (u, erratum LR-S1e; F4 says sourced)"
        disp = r["disp"]
        hcells = []
        for h in HS:
            if disp.get(h) is None:
                hcells.append("-")
            else:
                hcells.append(f"{disp[h]:.1f} / {r['r'][h]:.3f} / {r['D1_bands'][h]}")
        rows_a.append([c, r["f3_status"], s_lab, f(r["c_RT"], 2)] + hcells
                      + [f(r["r_5"], 3), f(r["r_15"], 3), f(r["r_OC"], 3), f(r["D1"])])
        d2 = r["D2_parts"]
        d3 = r["D3_parts"]
        d4 = r["D4_parts"]
        d5 = r["D5_parts"]
        rd = r["rd_p99"]
        tv = tick_value(c)
        j_txt = f"{d4['J']}" + (f" (p99 R_d {rd:.0f} t x {tv:g} = {rd*tv:,.0f} USD)" if rd is not None else " (u)")
        adv = F4["codes"][c]["adv"]["value"]
        rows_b.append([
            c, F4["codes"][c]["family"],
            f"{f(r['D2'])} (a {d2['a']:g}, b {d2['b']:g}, c {d2['c']:g}, d {d2['d']:g}; facts of {d2['facts_of']})",
            f"{f(r['D3'])} ({d3['s1']:g}/{d3['s2']:g}/{d3['s3']:g})",
            f"{f(r['D4'])}", f"{d4['L']}" + (f" (ADV {adv:,.0f})" if adv is not None else " (ADV unknown, u)"),
            j_txt, sat_rule(r),
            f"{f(r['D5'])} (h {d5['h']}, k {d5['k']}, o {d5['o']}, p {d5['p']})",
            f"{f(r['D6'])} ({r['D6_parts']['evidence_of']})",
            f(r["L1"]) if r["L1"] is not None else "-",
            "L1 < 2.00" if r["L1_below_2"] else "",
            "pass" if r["gate_pass"] else "FAIL",
        ])
        rows_c.append([c, r["f3_status"], ("pass" if r["gate_pass"] else "FAIL: " + "; ".join(r["gate_reasons"])),
                       r["gate_arithmetic"]])
    a = table(["code", "F3", "S (ticks)", "c_RT", "h30: sigma / r / band", "h60", "h120", "h240",
               "r_5", "r_15", "r_OC", "D1"], rows_a)
    b = table(["code", "family", "D2 (parts)", "D3 (s1/s2/s3)", "D4", "L", "J", "Sat rule", "D5 (parts)",
               "D6 (evidence of)", "L1", "flag", "gate"], rows_b)
    cc = table(["code", "F3", "gate result", "arithmetic (spec 3 gate)"], rows_c)
    (OUT / "sec2a.md").write_text(a)
    (OUT / "sec2b.md").write_text(b)
    (OUT / "sec2c.md").write_text(cc)


# ---------------- Section 3: pairs ----------------
def econ(key):
    p = EC["pairs"].get(key)
    return p["primary"] if p else None


def sec3():
    ranked = sorted([p for p in PAIRS if p["status"] == "ranked"], key=lambda p: p["rank"])
    rows = []
    for p in ranked:
        e = econ(p["key"])
        s60 = e["sigma60"]
        cap = e["above_cap"]
        capt = f"> cap {e['grid_cap']:g} t (scores 0)"
        mst = capt if cap["mu_star"] else f"{e['mu_star_mkt']:.2f} t / {p['m_star']:.3f}"
        m10 = capt if cap["mu10K"] else f"{e['mu10K_mkt']:.2f} t / {p['m10K']:.3f}"
        rd = p["Rel_deductions"]
        rel_txt = f"{f(p['Rel'],0)} (" + ",".join(k.replace("rel_", "") for k, v in rd.items() if v) + ")"
        rel_txt = rel_txt.replace(" ()", "")
        rows.append([p["rank"], FIRM[p["firm"]], p["code"], f(p["S"], 3), f(p["S_rounded"]), f(p["L1"]),
                     f(p["L2"], 3), f(p["E"], 3), mst, m10, f"{s60:.1f}", f(p["R"], 0), f(p["A"], 0),
                     f"{f(p['D'],1)} ({p['room_a']:.2f}/{p['room_b']:.2f})", rel_txt, f(p["P"], 0),
                     f"{p['cost_per_attempt']:.0f}", f"{p['cost_per_attempt_lim']:.0f}",  # RV1 S1: market, limit
                     f"{p['fee_rt_usd']:.2f}" + ("" if p["fee_kind"] == "stated" else f" ({p['fee_kind']})")])
    head = ["rank", "firm", "code", "S", "S 2dp", "L1", "L2", "E", "m* (ticks / sigma_60)", "m10K (ticks / sigma_60)",
            "sigma_60 (t)", "R", "A", "D (room_a/room_b)", "Rel (deductions)", "P", "tie-break cost/attempt USD (market case)",
            "cost/attempt USD (limit case, reported)", "fee RT USD"]
    (OUT / "sec3a.md").write_text(table(head, rows))
    # excluded
    rows_x = []
    for p in sorted([p for p in PAIRS if p["status"] != "ranked"], key=lambda p: (p["status"], p["code"], p["firm"])):
        rows_x.append([FIRM[p["firm"]], p["code"], p["status"], "; ".join(p["gate_reasons"])])
    (OUT / "sec3b.md").write_text(table(["firm", "code", "status", "reason"], rows_x))
    # compact grid: firm x code status
    codes = sorted({p["code"] for p in PAIRS})
    grid = {(p["firm"], p["code"]): p for p in PAIRS}
    rows_g = []
    for c in codes:
        cells = []
        for fm in FIRM:
            p = grid[(fm, c)]
            if p["status"] == "ranked":
                cells.append(str(p["rank"]))
            elif p["status"] == "excluded (V49)":
                cells.append("V49")
            else:
                g = p["gate_reasons"]
                t = []
                if any("sigma_60 unknown" in x for x in g):
                    t.append("L1 sigma?")
                if any("D4 = 0" in x for x in g):
                    t.append("L1 D4=0")
                if any("not listed" in x for x in g):
                    t.append("unlisted")
                cells.append(", ".join(t))
        rows_g.append([c] + cells)
    (OUT / "sec3c.md").write_text(table(["code"] + list(FIRM.values()), rows_g))


# ---------------- Section 4: top 15 drivers ----------------
def sec4(facts):
    ranked = [p for p in PAIRS if p["status"] == "ranked"]
    n = len(ranked)
    crit1 = list(W1)
    mean1 = {k: sum(L1[p["code"]][k] for p in ranked) / n for k in crit1}
    mean2 = {k: sum(p[k] for p in ranked) / n for k in W2}
    facts["ranked_mean"] = {**{k: round(v, 3) for k, v in mean1.items()}, **{k: round(v, 3) for k, v in mean2.items()},
                            "S": round(sum(p["S"] for p in ranked) / n, 3)}
    rows = []
    for t in PRI["top15"]:
        p = next(q for q in PAIRS if q["firm"] == t["firm"] and q["code"] == t["code"])
        dev = {}
        for k, w in W1.items():
            dev[k] = 0.5 * w * (L1[p["code"]][k] - mean1[k])
        for k, w in W2.items():
            dev[k] = 0.5 * w * (p[k] - mean2[k])
        pos = sorted([(v, k) for k, v in dev.items() if v > 0.0005], reverse=True)[:3]
        neg = sorted([(v, k) for k, v in dev.items() if v < -0.0005])[:2]
        r1 = L1[p["code"]]
        rows.append([t["rank"], FIRM[p["firm"]], p["code"], f(p["S"], 3), f(p["L1"]), f(p["L2"], 3),
                     f"{r1['D1']:g}/{r1['D2']:g}/{r1['D3']:g}/{r1['D4']:g}/{r1['D5']:g}/{r1['D6']:g}",
                     f"{p['E']:.2f}/{p['R']:g}/{p['A']:g}/{p['D']:g}/{p['Rel']:g}/{p['P']:g}",
                     ", ".join(f"{k} +{v:.3f}" for v, k in pos), ", ".join(f"{k} {v:.3f}" for v, k in neg) or "-"])
    head = ["rank", "firm", "code", "S", "L1", "L2", "D1/D2/D3/D4/D5/D6", "E/R/A/D/Rel/P",
            "largest gains vs mean ranked pair (S units)", "largest losses"]
    (OUT / "sec4.md").write_text(table(head, rows))


# ---------------- Section 5: moves ----------------
def sec5(facts):
    mv = SC["moves_vs_e28"]
    rows = []
    for r in sorted(mv["rows"], key=lambda r: (r["rank_here"] is None, r["rank_here"] or 0, r.get("rank_e28") or 999)):
        c = r.get("contrib") or {}
        up = ", ".join(f"{k} +{v:.3f}" for k, v in sorted(c.items(), key=lambda kv: -kv[1]) if v > 0.0005)
        dn = ", ".join(f"{k} {v:.3f}" for k, v in sorted(c.items(), key=lambda kv: kv[1]) if v < -0.0005)
        e28 = r["rank_e28"] if r["status_e28"] == "ranked" else r["status_e28"]
        here = r["rank_here"] if r["status_here"] == "ranked" else r["status_here"]
        chg = r.get("rank_change")
        rows.append([FIRM[r["firm"]], r["code"], e28, here, ("+" if (chg or 0) > 0 else "") + str(chg) if chg is not None else "-",
                     f(r.get("S_e28"), 3), f(r.get("S_here"), 3), up or "-", dn or "-"])
    head = ["firm", "code", "E.28 v2 rank", "rank here", "change", "S E.28", "S here",
            "moved up by (S units)", "moved down by (S units)"]
    (OUT / "sec5.md").write_text(table(head, rows))
    listed = {p["key"] for p in PAIRS if p["status"] in ("ranked", "excluded (V49)") or
              (p["status"] == "Layer 1 gate" and not any("not listed" in g for g in p["gate_reasons"]))}
    inmv = {r["firm"] + "|" + r["code"] for r in mv["rows"]}
    facts["listed_pairs"] = len(listed)
    facts["moves_rows"] = len(mv["rows"])
    facts["listed_not_in_e28_rows"] = sorted(listed - inmv)
    facts["e28_rows_not_listed_here"] = sorted(inmv - listed)
    from collections import Counter
    facts["moves_status"] = {f"{a} -> {b}": n for (a, b), n in Counter((r["status_e28"], r["status_here"]) for r in mv["rows"]).items()}


# ---------------- Section 6: variants ----------------
def key(t):
    return f"{t['firm']}|{t['code']}"


def pk(k):
    fm, code = k.split("|")
    return f"{FIRM[fm]} x {code}"


def sec6(facts):
    prim = [key(t) for t in PRI["top15"][:5]]
    prim_codes = sorted({k.split("|")[1] for k in prim})
    rows = []
    vf = {}
    for name, v in SC["variants"].items():
        top = [key(t) for t in v["top5"]]
        same_set = set(top) == set(prim)
        same_order = top == prim
        cls = "identical" if same_order else ("order only" if same_set else "SET CHANGES")
        enter = [k for k in top if k not in prim]
        leave = [k for k in prim if k not in top]
        codes = sorted({k.split("|")[1] for k in top})
        c_in = [c for c in codes if c not in prim_codes]
        c_out = [c for c in prim_codes if c not in codes]
        assert v["top5_same_as_primary"] == same_order, name
        top_txt = "; ".join(f"{t['rank']} {FIRM[t['firm']]} {t['code']} {t['S']:.3f}" for t in v["top5"])
        mnq = v["MNQ_ranks"]
        mnq_txt = ", ".join(f"{FIRM[k][:3]} {mnq[k]}" for k in FIRM) if all(isinstance(mnq[k], int) for k in FIRM) \
            else ", ".join(f"{FIRM[k][:3]} {mnq[k]}" for k in FIRM)
        kind = v["kind"] + (f" ({v['ruling']})" if v.get("ruling") else "")
        rows.append([name, kind, top_txt, cls,
                     (", ".join(pk(k) for k in enter) or "-") + " / " + (", ".join(pk(k) for k in leave) or "-"),
                     (", ".join(c_in) or "-") + " / " + (", ".join(c_out) or "-"),
                     mnq_txt, v["n_ranked"], len(v["layer1_survivors"])])
        vf[name] = {"class": cls, "enter": enter, "leave": leave, "codes_in": c_in, "codes_out": c_out,
                    "n_ranked": v["n_ranked"], "n_surv": len(v["layer1_survivors"]),
                    "surv_lost": sorted(set(PRI["layer1_survivors"]) - set(v["layer1_survivors"])),
                    "surv_gained": sorted(set(v["layer1_survivors"]) - set(PRI["layer1_survivors"]))}
    head = ["variant", "kind", "top 5 (rank firm code S)", "top 5 vs primary", "pairs in / out", "products in / out",
            "MNQ ranks (Bul, Luc, MFF, Top, Tra)", "ranked pairs", "L1 survivors"]
    (OUT / "sec6.md").write_text(table(head, rows))
    facts["variants"] = vf
    facts["primary_top5"] = prim


def main():
    facts = {"generated_from": {k: v["sha256"] for k, v in SC["inputs"].items() if isinstance(v, dict) and "sha256" in v},
             "score_generated": SC["generated_pdt"], "n_ranked": PRI["n_ranked"],
             "n_survivors": len(PRI["layer1_survivors"]), "L1_below_2": PRI["L1_below_2"],
             "MNQ_ranks": PRI["MNQ_ranks"]}
    sec2()
    sec3()
    sec4(facts)
    sec5(facts)
    sec6(facts)
    (OUT / "facts.json").write_text(json.dumps(facts, indent=1))
    print("fragments:", sorted(p.name for p in OUT.iterdir()))


if __name__ == "__main__":
    main()
