"""Build reports/stage_e32b_holding_scope.md from F5_holding.json, econ32b.json and a prose template.

ScopeWriter (E.32b, D4). Facts only: reads F5 script output and econ model blocks; no market data, no
strategy outcome. Tables are generated here; prose lives in scope_template.md with {{T:name}} markers.

Run: python3 reports/stage_e32b_briefs/work/scope/build_scope.py
"""
import hashlib
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BRIEFS = HERE.parent.parent
REPORTS = BRIEFS.parent
F5 = BRIEFS / "F5_holding.json"
ECON = BRIEFS / "econ32b.json"
TEMPLATE = HERE / "scope_template.md"
OUT = REPORTS / "stage_e32b_holding_scope.md"

H = ["1", "2", "5", "15", "30", "60", "120", "240", "OC"]
ON = ["cc", "on"]
TOP_CODES = ["YM", "MNQ", "RTY", "MYM", "ZL"]
EDIR_H = ["30", "120", "240"]


def f(x, nd=2):
    if x is None:
        return "u"
    if isinstance(x, bool):
        return "yes" if x else "no"
    if isinstance(x, (int,)) and not isinstance(x, bool):
        return f"{x:,}" if abs(x) >= 10000 else str(x)
    return f"{x:.{nd}f}"


def table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def allrows(e):
    rows = dict(e["rows"])
    rows.update(e.get("overnight_rows", {}))
    return rows


def crossover(e):
    """First intraday h (1..OC) where the power term reaches the cost term (README reading 10)."""
    for h in H:
        r = e["rows"].get(h)
        if r and r.get("G_power_term") is not None and r["G_power_term"] >= r["G_cost_term"]:
            return h
    return "none"


def mins(h, L):
    return L if h == "OC" else int(h)


def rw_ratios(e):
    """sigma(h1)/sigma(h2) x sqrt(h2/h1): 1 = square-root-of-time growth; >1 slower; <1 faster."""
    L = e["L_main"]
    out = []
    for a, b in zip(H[:-1], H[1:]):
        ra, rb = e["rows"].get(a), e["rows"].get(b)
        if not ra or not rb or not ra.get("sigma") or not rb.get("sigma"):
            out.append("u")
            continue
        out.append(f"{ra['sigma'] / rb['sigma'] * math.sqrt(mins(b, L) / mins(a, L)):.3f}")
    return out


def argmin_s(e):
    return ", ".join(e["G_argmin"])


# ---------------- survivors ----------------
def t_surv_k(d):
    rows = []
    for code, s in d["survivors"].items():
        r = allrows(s)
        rows.append([code, s["L_main"], f(s["c_RT"]) + (" u" if s["S_unknown"] else "")]
                    + [f(r[h]["k_RT"], 4) if h in r else "u" for h in H + ON]
                    + [crossover(s), argmin_s(s)])
    return table(["code", "L_main", "c_RT"] + [f"k {h}" for h in H + ON] + ["power >= cost from", "min G_RT at"], rows)


def t_surv_rw(d):
    rows = [[code] + rw_ratios(s) for code, s in d["survivors"].items()]
    return table(["code"] + [f"{a}->{b}" for a, b in zip(H[:-1], H[1:])], rows)


def t_surv_G(d):
    rows = []
    for code, s in d["survivors"].items():
        r = allrows(s)
        cells = []
        for h in H + ON:
            g = r.get(h, {}).get("G")
            c = f(g, 4)
            if h in s["G_argmin"]:
                c = f"**{c}**"
            cells.append(c)
        rows.append([code] + cells + [f(s["G_min"], 4), argmin_s(s)])
    return table(["code"] + [f"G {h}" for h in H + ON] + ["min G_RT", "at"], rows)


def t_surv_p(d):
    rows = []
    for code, s in d["survivors"].items():
        r = allrows(s)
        rows.append([code] + [f"{r[h]['p_be_emp']:.3f} / {r[h]['p_1_emp']:.3f}" if h in r else "u" for h in H + ON])
    return table(["code"] + [f"p {h}" for h in H + ON], rows)


def t_surv_e80(d):
    rows = []
    for code, s in d["survivors"].items():
        r = allrows(s)
        rows.append([code] + [f(r[h]["e80_test"], 2) if h in r else "u" for h in H + ON])
    return table(["code"] + [f"e80 {h}" for h in H + ON], rows)


def t_trades(d):
    seen = {}
    for s in d["survivors"].values():
        seen.setdefault(s["L_main"], s)
    rows = []
    for L, s in sorted(seen.items()):
        r = allrows(s)
        rows.append([L] + [f"{r[h]['n_cap']} ({r[h]['trades_per_year']:,})" for h in H + ON])
    return table(["L_main"] + [f"{h}" for h in H + ON], rows)


# ---------------- pairs ----------------
def news_short(p):
    items = p.get("news_window_items") or []
    if not items:
        return "none named for this product"
    return "; ".join(f"{i.get('effect')}" for i in items)


def t_pair_summary(d):
    rows = []
    for key, p in d["pairs"].items():
        r = p["rows"]
        rows.append([p["rank"], key, f(p["tick_value_usd"]), f"{f(p['fee_rt_usd'])} ({p['fee_kind']})",
                     f(p["fee_ticks"], 3), f(p["c_RT"]) + (" u" if p["S_unknown"] else ""), f(p["c_f"], 3),
                     f"{p['DLL_f']:,.0f}", f"{p['MLL_f']:,.0f}", p["flat_by_close"].get("pt", "u"),
                     p["flat_minus_main_end_min"], f(p["overnight_allowed"]), argmin_s(p), f(p["G_min"], 4),
                     ", ".join(p["band"]["members"]) or "empty", p["band"]["power_term_exceeds_cost_from"],
                     p["verdict"]["value"]])
    return table(["#", "pair", "v USD", "fee RT USD", "fee ticks", "c_RT", "c_f", "DLL used", "MLL",
                  "flat by PT", "flat - main end (min)", "overnight", "min G at", "min G", "B",
                  "power >= cost from", "prior"], rows)


def pair_tables(p, prop=True):
    ra = []
    rb = []
    for h in H + ON:
        r = allrows(p).get(h)
        if r is None:
            continue
        ra.append([h, f(r["sigma"]), f(r["k_RT"], 4), f(r["k"], 4), f(r["g_be"], 3), f(r["g_1"], 3),
                   f(r["p_be_emp"], 3), f(r["p_be_norm"], 3), f(r["p_1_emp"], 3), f(r["p_1_norm"], 3)])
        base = [h, r["n_cap"], f"{r['trades_per_year']:,}", f(r["e80_disc_G3"]), f(r["e80_disc_G3G4"]),
                f(r["e80_test"]), f(r["gross_detect_test"]), f(r["G"], 4), f(r.get("G_over_min"), 3)]
        if prop:
            base += [f(r.get("dll_ratio")), f(r.get("mll_ratio")), r.get("latest_start_pt") or "u",
                     f(r.get("fits_flat_by_close")), f(r.get("in_band"))]
        else:
            ov = r.get("margin_overnight_initial_usd")
            base += [r.get("latest_start_pt") or "u", f(r.get("in_band")), f"{ov:,.0f}" if ov else ""]
        rb.append(base)
    ta = table(["h", "sigma_h", "k_RT", "k_f", "g_be", "g_1", "p_be emp", "p_be norm", "p_1 emp", "p_1 norm"], ra)
    hb = ["h", "n_cap/day", "trades/yr", "e80 disc G3", "e80 disc G3+G4", "e80 test", "c_f + e80 test", "G",
          "G/minG"]
    hb += (["DLL/(sigma v)", "MLL/(sigma v)", "latest start PT", "fits flat-by", "in B"] if prop
           else ["latest start PT", "in B", "overnight IM USD"])
    return ta + "\n\n" + table(hb, rb)


def pause_text(p):
    out = []
    for q in p.get("pauses", []):
        x = q["pause"]
        out.append(f"{x['start_pt']}-{x['end_pt']} PT {x['days']} ({x['what']}; {x['item']}): "
                   f"{q['relation_to_main_session']}")
    return "; ".join(out) or "none recorded"


def news_text(p):
    items = p.get("news_window_items") or []
    if not items:
        return "no window names this product at this firm"
    return "; ".join(f"{i.get('rule')} -> {i.get('effect')} ({i.get('item')})" for i in items)


def t_pairs_detail(d):
    out = []
    for key, p in d["pairs"].items():
        b = p["band"]
        fbc = p["flat_by_close"]
        ex = "; ".join(f"{h}: {', '.join(v)}" for h, v in b["excluded"].items()) or "none"
        hdr = [f"### {p['rank']}. {key}",
               "",
               f"- Costs: S {f(p['S'])} tick{' (u)' if p['S_unknown'] else ''} + 0.5 slippage = c_RT {f(p['c_RT'])}; "
               f"fee USD {f(p['fee_rt_usd'])} RT ({p['fee_kind']}) / v {f(p['tick_value_usd'])} = {f(p['fee_ticks'], 3)} "
               f"ticks; c_f {f(p['c_f'], 3)} ticks (g_be), g_1 {f(p['c_f'] + 1, 3)} ticks.",
               f"- Limits: DLL used USD {p['DLL_f']:,.0f} ({p['dll_source']}); MLL USD {p['MLL_f']:,.0f} "
               f"({p['mll_type']}).",
               f"- Session: main {p['main_session_pt'][0]}-{p['main_session_pt'][1]} PT; flat by {fbc['raw']['time']} "
               f"{fbc['raw']['tz']} = {fbc.get('pt')} PT ({p['flat_minus_main_end_min']} min after the main-session "
               f"end); overnight {f(p['overnight_allowed'])} (evaluation {f(p['overnight'].get('evaluation'))}, funded "
               f"{f(p['overnight'].get('funded'))}, weekend {f(p['overnight'].get('weekend'))}).",
               f"- News: {news_text(p)}.",
               *([topstep_news(p)] if topstep_news(p) else []),
               f"- Pauses: {pause_text(p)}.",
               f"- G: min {f(p['G_min'], 4)} at {argmin_s(p)}; power term >= cost term from h = "
               f"{b['power_term_exceeds_cost_from']}. B = {', '.join(b['members']) or 'empty'} "
               f"(contiguous {f(b['contiguous'])}); excluded: {ex}. Prior: {p['verdict']['value']} "
               f"({p['verdict']['reason']}).",
               f"- u: {'; '.join(p['u']) or 'none'}.",
               "", ""]
        out.append("\n".join(hdr) + pair_tables(p, prop=True))
    return "\n\n".join(out)


# ---------------- own broker ----------------
def t_ibkr_summary(d):
    rows = []
    for key, r in d["own_broker"]["rows"].items():
        q = r["Q6_inputs"]
        rows.append([key, f(r["c_f"]), f(r["fee_ticks"]), argmin_s(r), ", ".join(r["band"]["members"]) or "empty",
                     ibkr_label(r),
                     f"{q['margin_intraday_initial_usd']:,.0f}" + (" >" if q["margin_intraday_exceeds_ceiling"] else ""),
                     f"{q['margin_overnight_initial_usd']:,.0f}" + (" >" if q["margin_overnight_exceeds_ceiling"] else ""),
                     f"{q['sigma_day_usd']:,.0f}" + (" >" if q["sigma_day_exceeds_limit"] else ""),
                     f"{q['sigma_OC_usd']:,.0f}"])
    return table(["row", "c_f", "fee ticks", "min G at", "B", "prior", "IM intraday USD", "IM overnight USD",
                  "sigma_day USD (cc)", "sigma_OC USD"], rows)


def t_ibkr_detail(d):
    out = []
    for code in TOP_CODES:
        key = f"ibkr|{code}"
        r = d["own_broker"]["rows"][key]
        q = r["Q6_inputs"]
        b = r["band"]
        of = r.get("overnight_position_fee") or {}
        ofv = of.get("usd_per_contract_per_night")
        ex = "; ".join(f"{h}: {', '.join(v)}" for h, v in b["excluded"].items()) or "none"
        hdr = [f"### {key}",
               "",
               f"- Costs: fee USD {f(r['fee_per_side_usd'])} a side, F_rt USD {f(r['fee_rt_usd'])} "
               f"({r['fee_status']}) = {f(r['fee_ticks'], 3)} ticks; c_RT {f(r['c_RT'])}"
               f"{' (S u)' if r['S_unknown'] else ''}; c_f {f(r['c_f'], 3)} ticks.",
               f"- Margin (initial): intraday USD {q['margin_intraday_initial_usd']:,.2f}, overnight USD "
               f"{q['margin_overnight_initial_usd']:,.2f} (maintenance USD {r['margin_overnight_maintenance_usd']:,.2f}); "
               f"ceiling USD {q['capital_ceiling_usd']:,.0f} (u): intraday exceeds {f(q['margin_intraday_exceeds_ceiling'])}, "
               f"overnight exceeds {f(q['margin_overnight_exceeds_ceiling'])}.",
               f"- sigma_day (sigma_cc {f(q['sigma_cc_ticks'])} ticks x v) USD {q['sigma_day_usd']:,.0f} against 2% of the "
               f"ceiling (USD {q['sigma_day_limit_usd']:,.0f}): exceeds {f(q['sigma_day_exceeds_limit'])}; sigma_OC USD "
               f"{q['sigma_OC_usd']:,.0f}.",
               f"- Overnight: allowed; overnight position fee (Tiered only) USD/contract/night {json.dumps(ofv)}.",
               f"- G: min {f(r['G_min'], 4)} at {argmin_s(r)}; power term >= cost term from h = "
               f"{b['power_term_exceeds_cost_from']}. B = {', '.join(b['members']) or 'empty'}; excluded: {ex}. "
               f"Prior: {r['verdict']['value']} ({r['verdict']['reason']}).",
               f"- u: {'; '.join(r['u']) or 'none'}.",
               "", ""]
        out.append("\n".join(hdr) + pair_tables(r, prop=False))
    return "\n\n".join(out)


def t_venue_compare(d):
    rows = []
    for code in TOP_CODES:
        props = [(k, p) for k, p in d["pairs"].items() if p["code"] == code]
        ib = d["own_broker"]["rows"][f"ibkr|{code}"]
        for k, p in props:
            rows.append([code, k, f(p["c_f"], 3), argmin_s(p), f(p["G_min"], 4), ", ".join(p["band"]["members"]),
                         p["verdict"]["value"]])
        rows.append([code, f"ibkr|{code}", f(ib["c_f"], 3), argmin_s(ib), f(ib["G_min"], 4),
                     ", ".join(ib["band"]["members"]) or "empty", ib["verdict"]["value"]])
    return table(["code", "venue row", "c_f", "min G at", "min G", "B", "prior"], rows)


def t_overnight(d):
    rows = []
    for key, p in d["pairs"].items():
        o = p["overnight_rows"]
        rows.append([key, f(p["overnight_allowed"]), f(p["G_min"], 4), argmin_s(p), f(p["rows"]["OC"]["G"], 4),
                     f(o["cc"]["G"], 4), f(o["on"]["G"], 4), f(p["rows"]["OC"]["dll_ratio"]),
                     f(o["cc"]["dll_ratio"]), f(o["on"]["dll_ratio"])])
    for code in TOP_CODES:
        r = d["own_broker"]["rows"][f"ibkr|{code}"]
        o = r["overnight_rows"]
        rows.append([f"ibkr|{code}", "yes", f(r["G_min"], 4), argmin_s(r), f(r["rows"]["OC"]["G"], 4),
                     f(o["cc"]["G"], 4), f(o["on"]["G"], 4), "n/a", "n/a", "n/a"])
    return table(["row", "overnight allowed", "min G", "at", "G OC", "G cc", "G on", "DLL/(sigma v) OC",
                  "DLL/(sigma v) cc", "DLL/(sigma v) on"], rows)


# ---------------- econ ----------------
def t_edir(d, econ):
    rows = []
    for key, p in d["pairs"].items():
        e = econ["pairs"].get(key, {})
        b = e.get("E_dir60")
        Lm = d["survivors"][p["code"]]["L_main"]
        Ts = {h: min(20, Lm // int(h)) for h in ["30", "60", "120", "240"]}
        if b:
            ac = b.get("above_cap", {})
            c60 = (f"{f(b['mu_star_mkt'])}{' (>cap)' if ac.get('mu_star') else ''} / "
                   f"{f(b['mu10K_mkt'])}{' (>cap)' if ac.get('mu10K') else ''} / {f(b['m_star'], 3)} / "
                   f"{f(b['m10K'], 3)} / {f(b['grid_cap'], 0)}")
        else:
            c60 = "not in econ32b.json"
        cells = []
        for h in EDIR_H:
            blk = (e.get("E_dir") or {}).get(h) if isinstance(e.get("E_dir"), dict) else None
            if blk:
                ac = blk.get("above_cap", {})
                cells.append(f"{f(blk['mu_star_mkt'])}{' (>cap)' if ac.get('mu_star') else ''} / "
                             f"{f(blk['mu10K_mkt'])}{' (>cap)' if ac.get('mu10K') else ''} / {f(blk['m_star'], 3)} / "
                             f"{f(blk['m10K'], 3)}")
            else:
                cells.append("**[PENDING: lead fills]**")
        rows.append([key, "/".join(str(Ts[h]) for h in ["30", "60", "120", "240"]), c60] + cells)
    return table(["pair", "T at 30/60/120/240", "E_dir60: mu*_mkt / mu10K_mkt / m* / m10K / cap (ticks)",
                  "E_dir30", "E_dir120", "E_dir240"], rows)


# ---------------- prior ----------------
def t_prior(d):
    import collections
    rows = []
    pv = collections.Counter(p["verdict"]["value"] for p in d["pairs"].values())
    rows.append(["top-15 prop pairs", 15, pv["holds"], pv["partly"], pv["fails"]])
    ib = d["own_broker"]["rows"]
    iv = collections.Counter(r["verdict"]["value"] for r in ib.values())
    rows.append(["ibkr, all 35 survivor codes", len(ib), iv["holds"], iv["partly"], iv["fails"]])
    tv = collections.Counter(ib[f"ibkr|{c}"]["verdict"]["value"] for c in TOP_CODES)
    rows.append(["ibkr, the five top-15 codes", 5, tv["holds"], tv["partly"], tv["fails"]])
    return table(["group", "rows", "holds", "partly", "fails"], rows)


def t_surv_argmin(d):
    import collections
    c = collections.defaultdict(list)
    for code, s in d["survivors"].items():
        c[argmin_s(s)].append(code)
    order = H + ON
    rows = [[k, len(v), " ".join(v)] for k, v in sorted(c.items(), key=lambda kv: order.index(kv[0].split(",")[0]))]
    return table(["min G_RT at", "codes", "list"], rows)


def ibkr_label(r):
    """Lead ruling 6: a fail whose B is non-empty and whose min G lies only overnight/OC."""
    v = r["verdict"]["value"]
    if v == "fails" and r["band"]["members"]:
        return "fails (min G overnight)"
    return v


def intraday_b(r):
    return ", ".join(h for h in r["band"]["members"] if h != "OC") or "none"


def topstep_news(p):
    if p["firm"] != "topstep":
        return None
    items = p.get("news_window_items") or []
    eff = " ".join(str(i.get("effect")) for i in items)
    if "blocked" in eff:
        return ("- Topstep news block (excluded entry minutes; not a band condition, spec 7): no new opens 10:55-11:05 "
                "and 11:25-11:35 PT on FOMC decision days (20 main-session minutes a day, about 160 a year on the usual "
                "8-meeting schedule); the CPI/PPI/NFP windows (05:25-05:35 PT, about 3 a month) lie before the main "
                "session. Holds may span the windows.")
    if "capped" in eff:
        return "- Topstep news window: micro capped at 3 (one lot allowed): no entry minute excluded at one lot."
    return "- Topstep news window: product not named (grains): no entry minute excluded."


def t_ibkr_fails(d):
    rows = []
    for key, r in d["own_broker"]["rows"].items():
        if r["verdict"]["value"] != "holds":
            rows.append([key, ", ".join(r["band"]["members"]) or "empty", intraday_b(r), argmin_s(r), f(r["G_min"], 4),
                         f(min(r["rows"][h]["G"] for h in H if r["rows"][h].get("G") is not None), 4),
                         ibkr_label(r), r["verdict"]["reason"]])
    return table(["row", "B", "intraday B", "min G at", "min G", "min intraday G", "prior", "reason"], rows)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    d = json.loads(F5.read_text())
    econ = json.loads(ECON.read_text())
    tables = {
        "surv_k": t_surv_k(d), "surv_rw": t_surv_rw(d), "surv_G": t_surv_G(d), "surv_p": t_surv_p(d),
        "surv_e80": t_surv_e80(d), "trades": t_trades(d), "surv_argmin": t_surv_argmin(d),
        "pair_summary": t_pair_summary(d), "pairs_detail": t_pairs_detail(d),
        "ibkr_summary": t_ibkr_summary(d), "ibkr_detail": t_ibkr_detail(d), "venue_compare": t_venue_compare(d),
        "overnight": t_overnight(d), "edir": t_edir(d, econ), "prior": t_prior(d), "ibkr_fails": t_ibkr_fails(d),
        "sources": table(["input", "sha256"], [[str(p.relative_to(REPORTS.parent)), sha(p)]
                                                for p in [F5, ECON, BRIEFS / "F4_facts.md", BRIEFS / "F2_firms.md",
                                                          REPORTS / "E.33c_RETURN.md",
                                                          BRIEFS / "work/F5/README.md", BRIEFS / "RULINGS.md"]]),
        "f5_generated": d["generated_pdt"],
    }
    tmpl = TEMPLATE.read_text()
    missing = set(re.findall(r"\{\{T:(\w+)\}\}", tmpl)) - set(tables)
    if missing:
        sys.exit(f"unknown markers: {missing}")
    text = re.sub(r"\{\{T:(\w+)\}\}", lambda m: tables[m.group(1)], tmpl)
    OUT.write_text(text)
    print(f"wrote {OUT} ({len(text.splitlines())} lines)")


if __name__ == "__main__":
    main()
