"""write_dossiers.py: briefs/R2_dossiers.md (full, spec 8.2) and briefs/R2_dossiers_for_rating.md (only what Q1-Q3
need: no cost, fee, power, prop-fit, data-cost or venue numbers, and no venue names).

Run after build_groundwork.py and build_combos.py:
    uv run python reports/stage_e32b_briefs/work/R2/write_dossiers.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import groundwork_facts as GF  # noqa: E402
from r2_common import (  # noqa: E402
    COMBOS_DETAIL, DOSSIERS_MD, DOSSIERS_RATING_MD, GROUNDWORK_JSON, R1_PATH, SPEC_SHA256, check_spec, fmt, load,
    now_pdt, write_text,
)

ORDER = ("YM", "MYM", "MNQ", "RTY", "ZL", "EQ3", "EQ3m")
# Venue numbers inside R1 closing quotes are elided in the rating file (marked [...]).
RATING_ELISIONS = {"R1-22": (", despite Topstep's 0.44-tick break-even", " [...]")}


def cell(s) -> str:
    return str(s).replace("|", "/").replace("\n", " ")


def dossier_groups(detail: dict) -> dict:
    groups = {}
    for c in detail["combinations"]:
        groups.setdefault(c["dossier"], []).append(c)
    key = lambda k: (ORDER.index(k.split("|")[0]), k.split("|")[1])  # noqa: E731
    return dict(sorted(groups.items(), key=lambda kv: key(kv[0])))


def und_of(g: dict, combo: dict) -> list:
    codes = [combo["product"]] if combo["product"] else combo["pool"]["members"]
    return [g["codes"][c]["underlying"] for c in codes]


def evidence_catalog(g: dict, used: set) -> list:
    rows = {}
    for ud in g["underlyings"].values():
        for fe in ud["families"].values():
            for e in fe.get("evidence", []):
                rows.setdefault(e["row_id"], e)
    return [rows[k] for k in sorted(used)]


def r1_catalog(r1: dict, used: set, rating: bool) -> list:
    L = []
    for ln in r1["lines"]:
        if ln["id"] not in used:
            continue
        cl = ln.get("closing") or {}
        quote = cl.get("quote") or ""
        if rating and ln["id"] in RATING_ELISIONS:
            a, b = RATING_ELISIONS[ln["id"]]
            quote = quote.replace(a, b)
        prods = ", ".join(f"{p['code']} ({p['role']})" for p in ln.get("products") or [])
        L += [f"- **{ln['id']}** [{ln['type']}] {ln['family']}. Products: {prods}. Horizons: {ln.get('horizons')}. "
              f"Windows: {'; '.join(ln.get('windows') or [])}. Trials: {ln.get('n_trials')}. Closing: "
              f"{cl.get('decision')}, \"{quote}\" ({cl.get('source')})."
              + (f" Exceptions: {'; '.join(ln['exceptions'])}." if ln.get("exceptions") else "")]
    return L


def evidence_lines(cat: list) -> list:
    L = ["| row | study | product in study | horizon | data period | sample | net of costs | finding | verified "
         "level | venue type |", "|---|---|---|---|---|---|---|---|---|---|"]
    for e in cat:
        L.append(f"| {e['row_id']} | {cell(e['study'])} ({cell(', '.join(e['item_ids']))}) | {cell(e['product_in_study'])}"
                 f" | {cell(e['horizon'])} | {cell(e['data_period'])} | {cell(e['in_or_out_of_sample'])} | "
                 f"{cell(e['net_of_costs'])} | {cell(e['finding'])} | {cell(e['verified_level'])} | "
                 f"{cell(e['venue_type'])} |")
    L += ["", "Quotes (verbatim from the R2 file, with the saved source):", ""]
    for e in cat:
        L.append(f"- {e['row_id']}: \"{cell(e['quote'])}\" ({e['file']})")
    return L


def family_block(g: dict, unds: list, fid: str, rating: bool, printed: dict, key: str) -> list:
    """Mechanism, horizon, evidence and R1 overlap for one dossier (pools: one block per member underlying). A block
    already written for the same underlying and family is referenced, not repeated."""
    L = []
    seen = []
    for u in unds:
        if u in seen:
            continue
        seen.append(u)
        if (u, fid) in printed:
            L += [f"*{u} ({g['underlyings'][u]['name']})*: mechanism, participant flow, horizon, evidence rows and R1 "
                  f"overlap exactly as in dossier {printed[(u, fid)]} (same underlying, same family).", ""]
            continue
        printed[(u, fid)] = key
        fe = g["underlyings"][u]["families"][fid]
        tm = fe["timing"]
        mech = fe["mechanism"]
        L += [f"*{u} ({g['underlyings'][u]['name']})*", "",
              f"- Applies because: {fe['decided_by']['fact']}",
              f"- Participant flow: {mech.get('whose_flow')}",
              f"- Why predictable: {mech.get('why_predictable')}",
              f"- Why an edge could exist at retail size: {fe['retail_size']}",
              f"- Mechanism quote: \"{mech.get('quote', '-')}\" ({mech.get('file', '-')})" if mech.get("quote")
              else "- Mechanism quote: none recorded in the R2 file for this family",
              f"- Documented horizon: {tm['documented_horizon']}",
              f"- Timing: {tm['timing_pt']}"]
        if not rating:
            L.append(f"- Kind: {tm['kind']}; events a year: {fmt(tm['events_per_year'], 2)} ({tm['events_source']}); "
                     f"trades per event: {fmt(tm['trades_per_event'])}")
        L += [f"- Absorption under 5 minutes (R2): {fe['absorption_under_5min']}",
              "- Evidence rows (relation to this product; full rows in the catalog): "
              + "; ".join(f"{e['row_id']} ({e['relation_to_product']}; {e['verified_level']})" for e in fe["evidence"]),
              "- R1 overlap (closing sentences in the R1 catalog):"]
        for o in fe["r1_overlap"]:
            L.append(f"  - {o['line']} ({o['relation_to_product']}): {o['configuration']}. Reading: {o['lr_r1_reading']}.")
        if not rating:
            L.append(f"- Open questions (R2): {' | '.join(fe['open_questions'])}")
        L.append("")
    return L


def rating_ids_table(combos: list) -> list:
    L = ["| combination id | band | shortest member | documented horizon vs band |", "|---|---|---|---|"]
    for c in combos:
        L.append(f"| {c['id']} | {', '.join(c['band'])} | {c['band_shortest']} | "
                 f"{c['horizon_vs_band']['statement']} |")
    return L


def venue_tables(combos: list) -> list:
    L = ["Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):", "",
         "| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | "
         "K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in combos:
        for m in c["members"]:
            e = m["e80_ticks"]
            L.append(f"| {c['id']} | {c['venue']} | {c['band_shortest']}-{c['band_longest']} | {c['h_c']} | "
                     f"{m['code']} | {fmt(m['c_f_ticks'])} | {fmt(m['sigma_hc_ticks'], 2)} | "
                     f"{fmt(m['x_cost_per_sigma'], 4)} | {fmt(m['p_be_emp'], 4)} / {fmt(m['p_be_norm'], 4)} | "
                     f"{fmt(m['p_1_emp'], 4)} / {fmt(m['p_1_norm'], 4)} | {fmt(m['K_year'], 1)} | "
                     f"{fmt(m['K_disc'], 1)} | {fmt(m['K_test'], 1)} | {fmt(e['disc_G3G4'], 2)} / "
                     f"{fmt(e['disc_G3'], 2)} / {fmt(e['test'], 2)} | "
                     f"{fmt(m['gross_needed_for_detection_ticks']['test'], 2)} |")
    L += ["", "Prop fit (one contract) and own-broker fit:", "",
          "| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout "
          "threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) "
          "| margin, sigma_day |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in combos:
        for m in c["members"]:
            pf = m.get("prop_fit")
            ob = m.get("own_broker_fit")
            q = m.get("queue_limit_variant")
            ql = (f"{fmt(q['c_lim_passive_entry_market_exit_ticks'])} / {fmt(q['c_lim_both_legs_passive_ticks'])}"
                  if q else "-")
            if pf:
                gt = ",".join(k for k, v in pf["gate"].items() if v) or "none"
                L.append(f"| {c['id']} | {c['venue']} | {m['code']} | {pf['dll_usd']} / {pf['mll_usd']} | "
                         f"{fmt(pf['dll_ratio_hc'], 2)} | {pf['flat_by_close_pt']}, {pf['latest_start_pt_hc']} | "
                         f"{fmt(pf['payout_threshold_usd'], 0)} vs {fmt(pf['sqrt_n_sigma_v_usd'], 2)} "
                         f"({'exceeds' if pf['payout_threshold_exceeds'] else 'below'}) | "
                         f"{fmt(pf['news_stop_events_per_week'], 3)} | {gt} | {ql} | - |")
            else:
                gt = ",".join(k for k, v in ob["gate"].items() if v) or "none"
                L.append(f"| {c['id']} | {c['venue']} | {m['code']} | none (own account) | - | none, "
                         f"{ob['latest_start_pt_hc']} | - | 0 | {gt} | not computed | intraday initial USD "
                         f"{fmt(ob['initial_margin_usd'], 2)} (overnight {fmt(ob['margin_overnight_initial_usd'], 2)}); "
                         f"sigma_cc {fmt(ob['sigma_day_ticks'], 2)} ticks = USD {fmt(ob['sigma_day_usd'], 2)} |")
    return L


def data_block(combo: dict) -> list:
    L = []
    for m in combo["members"]:
        dt = m["data"]
        L += [f"- {m['code']}: schema {dt['schema']}. Discovery {dt['windows']['discovery']}; test {dt['windows']['test']}; "
              f"clean test window {dt['windows']['clean_test_window']}. Cost (estimates): discovery USD "
              f"{fmt(dt['discovery_cost_usd'], 2)}, test USD {fmt(dt['test_cost_usd'], 2)}, all USD "
              f"{fmt(dt['all_data_cost_usd'], 2)}; basis: {dt['cost_basis']}. Quotes to obtain: "
              f"{'; '.join(dt['quotes_to_obtain']) or 'none'}."
              + (f" Alternative: {dt['alternative']}." if dt.get("alternative") else "")
              + (f" Not priced: {'; '.join(dt['unpriced_extras'])}." if dt["unpriced_extras"] else "")]
    d = combo["data"]
    L.append(f"- Combination (sums over members; clean window = the shortest member's): discovery USD "
             f"{fmt(d['discovery_cost_usd'], 2)}, all USD {fmt(d['all_data_cost_usd'], 2)}, clean test window "
             f"{d['clean_test_window_months']} months.")
    return L


def header(rating: bool, g: dict, detail: dict) -> list:
    t = now_pdt()
    if rating:
        L = ["# R2 dossiers for rating (Stage E.32b step 3b): Q1-Q3 inputs only", "",
             f"Written {t} by work/R2/write_dossiers.py (DossierWriter-OpusXHigh). This file holds only what Q1 "
             "(mechanism plausibility), Q2 (evidence quality) and Q3 (distance from closed lines) need: mechanism, "
             "participant flow, evidence rows with verified levels, horizons, periods and samples, the R1 overlap "
             "with quotes, and each combination id's band and shortest member. It has no cost, fee, power, prop-fit, "
             "data-cost or venue numbers and no venue names. Numbers inside evidence findings and closing quotes are "
             "the studies' and closed lines' own results; one venue number inside an R1 closing quote is elided as "
             "[...]. Facts only; no rating.", ""]
    else:
        L = ["# R2 dossiers (Stage E.32b step 3b, spec 8.2): DossierWriter-OpusXHigh", "",
             f"Written {t} by work/R2/write_dossiers.py from work/R2/groundwork.json and work/R2/combos_detail.json "
             f"(numbers by work/R2/build_combos.py). Spec sha256 {SPEC_SHA256[:16]}... Facts and arithmetic only; "
             "no outcome. One dossier per product or pool and family, with a venue table by combination id.", "",
             "## Conventions", "",
             f"- SR80 (daily Sharpe, N 838): discovery G3+G4 {detail['SR80']['disc_G3G4']:.4f} (binding), G3 alone "
             f"{detail['SR80']['disc_G3']:.4f}; test {detail['SR80']['test']:.4f} (work/F5/SR80.json). T_disc 796, "
             "T_test 870.",
             "- Band B and h_c: the pair's F5 band (IBKR: LR-F5-IBKR); h_c = the member of B with the lowest G; a "
             "pool's band is the intersection of its members' bands and h_c the member with the lowest worst-member "
             "G (LR-R2b).",
             "- c_f = S + 0.5 + F_rt / v (F5). g_be = c_f, g_1 = c_f + 1; p = 0.5 + g / (2 m_hc), normal "
             "approximation 0.5 + g / (1.596 sigma_hc).",
             "- K_year: continuous families n_cap(h_c) x 252; daily families (F01, F08) 252; event families events a "
             "year x trades per event (1). K_disc = K_year x 796 / 252, K_test = K_year x 870 / 252; n/day = K_year / "
             "252.",
             "- Payout: the firm's daily payout-qualification threshold against sqrt(n/day) sigma_hc v (E.29); "
             "Topstep and Tradeify USD 150 a winning day; Lucid, MFFU, Bulenox state no daily threshold (0).",
             "- News events a week: scheduled events whose firm news window overlaps the family's trading times "
             "(only Topstep blocks, and only full-size RTY and YM among these codes; frozen-calendar rates "
             f"{detail['topstep_t1_event_rates']['per_week']}).",
             "- Queue-limit variant (Rithmic routes: Bulenox, Lucid, Tradeify): c_lim replaces each passive leg's "
             "half-spread and slippage with E.31's measured trade-through markout 0.970 ticks per fill; reported "
             "beside, never scored. Not computed at Topstep (TopstepX trade-through), MFFU (Tradovate) or IBKR.",
             "- Overnight: no firm allows an overnight hold (F4 firms.<firm>.overnight.allowed false); every band is "
             "intraday, so no family here needs one. IBKR allows overnight holds (overnight margin shown beside).",
             "- Own broker (IBKR): initial margin = the intraday initial margin (every band is intraday), against "
             "USD 6,000 (u); sigma_day = sigma_cc (LR-Q6d).",
             "- Data: discovery 2020-12..2024-02 (39 months), test 43 months; costs are census estimates (F2_data_"
             "access k x months for MBO; the E.12 ohlcv-1m quote scaled by months for bars), labelled estimates.",
             ""]
    L += ["How to read an R1 overlap entry: the relation of the closed line to this product, the configuration it "
          "tested, and a 'Reading' that states the line's status under LR-R1 (closed configuration, family closed on "
          "another product, evidence finding, stop, execution line). Whether a combination re-tests a closed line or "
          "is a close variant (Q3) is the CombinationScorer's judgment, not the Reading's. Evidence-row relations "
          "(this product, same underlying, cousin, other venue, pool) are the DossierWriter's extraction.", ""]
    L += ["## Lead rulings and cross-family facts that bear on the ratings", "",
          "- " + GF.CROSS_FACTS[0], "- " + GF.CROSS_FACTS[1], "- " + GF.CROSS_FACTS[2], ""]
    if not rating:
        L += ["- " + x for x in GF.CROSS_FACTS[3:]] + [""]
    return L


def build(rating: bool) -> str:
    g = load(GROUNDWORK_JSON)
    detail = load(COMBOS_DETAIL)
    r1 = load(R1_PATH)
    groups = dossier_groups(detail)
    used_ev, used_r1 = set(), set()
    for key in groups:
        name, fid = key.split("|")
        unds = und_of(g, groups[key][0])
        for u in unds:
            fe = g["underlyings"][u]["families"][fid]
            used_ev |= {e["row_id"] for e in fe["evidence"]}
            used_r1 |= {o["line"] for o in fe["r1_overlap"]}
    L = header(rating, g, detail)
    L += ["## Dossier index", "", "| dossier | combinations | product or pool | family |", "|---|---|---|---|"]
    for key, cs in groups.items():
        L.append(f"| {key} | {cs[0]['id']}-{cs[-1]['id']} ({len(cs)}) | {key.split('|')[0]} | {cs[0]['family_name']} |")
    L += ["", "## Dossiers", ""]
    printed = {}
    for key, cs in groups.items():
        name, fid = key.split("|")
        c0 = cs[0]
        unds = und_of(g, c0)
        title = (f"pool {name} {c0['pool']['members']}" if c0["pool"] else f"product {name}")
        L += [f"### Dossier {key}: {title}, {c0['family_name']}", ""]
        if c0["pool"]:
            pmeta = next(p for p in g["pools"] if p["name"] == name)
            L += [f"Pool mechanism: {pmeta['mechanism']}.", ""]
        else:
            L += [g["underlyings"][unds[0]]["note"], ""]
        L += family_block(g, unds, fid, rating, printed, key)
        if rating:
            L += ["Combinations:", ""] + rating_ids_table(cs) + [""]
        else:
            hv = c0["horizon_vs_band"]
            L += [f"Band and horizon: {hv['statement']} (documented {hv['documented_minutes']} min). "
                  + "; ".join(f"{c['id']} h_c {c['h_c']}" + (" (h_c not a documented horizon)"
                              if int(c['h_c']) not in hv['documented_minutes'] else "") for c in cs), ""]
            L += venue_tables(cs) + ["", "Data needed:", ""] + data_block(cs[0]) + [""]
    L += ["## Evidence row catalog", ""] + evidence_lines(evidence_catalog(g, used_ev))
    L += ["", "## R1 closed-line catalog", ""] + r1_catalog(r1, used_r1, rating) + [""]
    if not rating:
        L += ["## Not built", ""] + [f"- {s['what']}: {s['reason']}" for s in detail["skipped"]]
        L += [f"- {x['candidate']}: {x['reason']}" for x in g["pools_not_built"]] + [""]
    return "\n".join(L) + "\n"


FORBIDDEN_IN_RATING = (r"\bUSD\b", r"\$", r"\bbulenox\b", r"\btopstep\b", r"\btradeify\b", r"\bmffu\b", r"\blucid\b",
                       r"\bibkr\b", r"\bc_f\b", r"\bsigma_hc\b", r"\be80\b", r"\bK_test\b",
                       r"\b(initial|intraday|overnight) margin\b", r"\bfee\b", r"\bpayout\b", r"\bDLL\b")


def rating_leaks(text: str) -> list:
    """Lines of the rating file outside the evidence and R1 catalogs that name a venue or carry cost words."""
    body = text.split("## Evidence row catalog")[0]
    body = body[body.index("## Lead rulings"):]          # the file's own header names the excluded kinds
    out = []
    for ln in body.splitlines():
        for pat in FORBIDDEN_IN_RATING:
            if re.search(pat, ln, flags=re.IGNORECASE):
                out.append((pat, ln[:160]))
    return out


def main() -> int:
    check_spec()
    full = build(rating=False)
    rate = build(rating=True)
    leaks = rating_leaks(rate)
    if leaks:
        for p, ln in leaks[:20]:
            print(f"LEAK {p}: {ln}", file=sys.stderr)
        print(f"REFUSED: {len(leaks)} venue or cost words in the rating file's dossiers", file=sys.stderr)
        return 2
    write_text(DOSSIERS_MD, full)
    write_text(DOSSIERS_RATING_MD, rate)
    print(f"dossiers: {full.count('### Dossier ')} (full {len(full)} chars, rating {len(rate)} chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
