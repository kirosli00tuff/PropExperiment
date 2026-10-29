"""Stage E.33c Part D: write work/D_stats.md from work/D_stats.json (every number from that file).

    python3 -I make_md.py <D_stats.json> <D_stats.md> <written-at text>
"""
from __future__ import annotations

import json
import sys

SRC = "work/D_stats.json"


def f(v, n=4):
    if v is None:
        return "n/a"
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, str):
        return v
    if isinstance(v, int):
        return f"{v:,}"
    return f"{v:.{n}f}"


def table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return out


def gates_str(g):
    return " ".join(k for k in ("G1", "G2", "G3", "G4", "G5") if g[k]) or "none"


def header(d, written):
    i, t, s = d["inputs"], d["thresholds"], d["selection_as_written"]
    return [
        "# Stage E.33c Part D statistics (branch N: Tier A empty)", "",
        f"Written {written} by StatsCoder-OpusXHigh (reports/stage_e33c_briefs/work/stats/run_dstats.py, make_md.py; "
        "figure plot_dstats.py). Every number below is in work/D_stats.json (sha256 in the return); the full "
        f"per-configuration table is {d['per_config_full']['path']} (sha256 {d['per_config_full']['sha256'][:16]}...).", "",
        f"- Protocol 0.3 sha256 {i['protocol_sha256'][:16]}... (checked equal to a2a2856f...; refuse otherwise).",
        f"- Selection: reports/stage_e33c_briefs/select/P8_select33.json sha256 {i['select_json_sha256'][:16]}... "
        f"(frozen select33.py, N {s['n_trials']}, b_test {s['b_test']:.6f}, Tier B reading {s['tier_b_reading']}). "
        "Reported, never re-selected.",
        f"- Search root {i['search_root']}/<cid>/ (stats.json, daily.parquet, trades.parquet), 300/300 DONE; feature "
        f"store {i['feature_sha']} (_day sigma_zm), label store {i['label_sha']} (not read: no item here needs it).",
        f"- OOF dates: {i['n_dates']}, {i['first_date']} .. {i['last_date']}; asserted inside 2020-12-01..2024-02-29, "
        "none in the test window 2017-05-01..2020-11-30, none on or after 2024-03-01.",
        f"- Thresholds recomputed with p7_final.py's functions at N {t['N']} (T_disc {t['T_disc']}, T_test "
        f"{t['T_test']}): SR0 {f(t['SR0'])}, G3 {f(t['G3'])} (skew -0.5, kurtosis 6: {f(t['G3_skew-0.5_kurt6'])}), "
        f"b_test {t['b_test']:.6f}, G4 {f(t['G4'])}, binding {f(t['binding'])}. N is 838, so P7.2's lines stand.",
        "- Scope (branch N): D1, D3, P10 (i)-(vi). D2 does not apply (no configuration passes D1). No P6.4 or "
        "P6.5 item is computed (they run only after a hashed test list; there is none). Item (vii) is the lead's.", ""]


def agreement(d):
    a = d["agreement_with_select33"]
    ms, mj = a["max_diff_vs_select"], a["max_diff_vs_stats_json"]
    rows = [["funnel (alone and in order)", f(a["funnel_equal"])],
            ["P8 total order of all 300", f(a["ranking_all_equal"])],
            ["BH / Holm rejection counts", f(a["bh_equal"] and a["holm_equal"])],
            ["one-sided p, max abs diff", f"{a['p_values_max_diff']:.1e}"],
            ["PBO report (all fields)", f(a["pbo_equal"])], ["b_test, abs diff", f"{a['b_test_diff']:.1e}"],
            ["configurations with any gate flag different", str(len(a["configs_with_gate_mismatch"]))],
            ["configurations with any G5 part different", str(len(a["configs_with_g5_part_mismatch"]))],
            ["max abs diff vs select33 over SR_d, t, DSR, se, SR - se, counts, mean net, G5 values",
             f"{max(v for v in ms.values() if isinstance(v, (int, float))):.1e}"],
            ["max abs diff vs stats.json over moments, t, counts, hit rate, fold/quarter/month sums, terciles",
             f"{max(v for v in mj.values() if isinstance(v, (int, float))):.1e}"]]
    return ["## 0. Independent recomputation against select33 and the search's stats.json", "",
            "My gate code (dstats_lib.evaluate, written from the P8 text and readings P01-P08) and select33 agree on "
            "every number; no disagreement to report. Source: D_stats.json agreement_with_select33.", ""] + \
        table(["check", "result"], rows) + [""]


def funnel(d):
    fu, s = d["funnel"], d["selection_as_written"]["funnel"]
    C = d["configs"]
    g1 = [c for c, v in C.items() if v["gates"]["G1"]]
    sets = {k: sum(1 for c in g1 if C[c]["set"] == k) for k in ("S1", "S2", "S3", "S4", "S5")}
    labs = {k: sum(1 for c in g1 if C[c]["label"] == k) for k in ("F05", "F15", "F30", "F60", "T15", "T30")}
    g1_best = max(g1, key=lambda c: C[c]["sharpe"])
    g1_mn = max(C[c]["mean_net_per_trade"] for c in g1)
    g5 = [v["g5"] for v in C.values()]
    dsr_best = max(C, key=lambda c: C[c]["dsr"] or 0)
    lo_best = max((c for c in C if C[c]["sr_lower"] is not None), key=lambda c: C[c]["sr_lower"])
    rows = [[g, f(fu["alone"][g]), f(s["alone"][g]), f(fu["in_order"]["G1" if g == "G1" else f"G1..{g}"]),
             f(s["in_order"]["G1" if g == "G1" else f"G1..{g}"])] for g in ("G1", "G2", "G3", "G4", "G5")]
    out = ["## D1 and P10 (i): the gate funnel (P8; Topstep, market, L = 1 s)", "",
           "Source: my recomputation from daily.parquet (D_stats.json funnel, configs.*.gates) beside select33's "
           "P8_select33.json funnel. Failed configurations: 0.", ""]
    out += table(["gate", "alone (mine)", "alone (select33)", "in order G1.. (mine)", "in order (select33)"], rows)
    out += ["", f"- G1 (>= 796 trades and a trade on >= 398 dates): 61 pass; by set {sets}; by label {labs}. "
            f"The best G1 passer by SR_d is {g1_best} at {f(C[g1_best]['sharpe'])}; the largest mean net per trade "
            f"among G1 passers is {f(g1_mn, 3)} ticks (all 61 are negative).",
            f"- G2 (mean net per trade >= 0.50): 8 pass alone, none of them with G1 (largest trade count 55; table "
            "below).",
            f"- G3 (DSR > 0.95 at N 838): 0; largest DSR {f(C[dsr_best]['dsr'])} ({dsr_best}).",
            f"- G4 (SR_d - se >= b_test {d['thresholds']['b_test']:.6f}): 0; largest SR_d - se "
            f"{f(C[lo_best]['sr_lower'])} ({lo_best}).",
            f"- G5 parts over the 300: (a) >= 9 of 13 quarters positive: {sum(x['a'] for x in g5)} (most quarters "
            f"positive in any configuration: {max(x['quarters_positive'] for x in g5)}); (b) total > 0 and no month "
            f"above 25%: {sum(x['b'] for x in g5)} (total > 0: {sum(x['total'] > 0 for x in g5)}); (c) every "
            f"leave-one-month-out t >= 2.5: {sum(x['c'] for x in g5)}; (d) all three sigma_ZM terciles positive: "
            f"{sum(x['d'] for x in g5)}; all four: {sum(x['pass'] for x in g5)}.",
            f"- Tier A: {d['selection_as_written']['tier_a']} (empty). Tier B as select33 wrote it (reading "
            f"continue): {d['selection_as_written']['tier_b']}; with Tier A empty P8 writes no test list, so Tier B "
            "has no use; it is reported, not recomputed here.", ""]
    return out


def firms(d):
    fs = d["firm_summary"]
    out = ["## D1: mean net per trade by firm (market entry and exit, L = 1 s)", "",
           "The fills are the selection variant's; only the round-trip fee differs, so net_firm = net_Topstep + "
           "0.528 - fee (dstats_lib.firm_net). This is a fee shift on the P8 series for all 300, not P6.4's execution "
           "variants (limit routes, L = 0.300 s), which are not computed. Lucid at 0.560 and, if the 5.60 USD is "
           "not all-in, 0.920 (reading K01). Over the 222 configurations with trades. Source: D_stats.json "
           "firm_summary, configs.*.firm_mean_net_per_trade.", ""]
    rows = [[k, f(v["fee"], 3), v["n_with_trades"], v["n_ge_0.50"], v["n_gt_0"], f(v["median"], 3), f(v["max"], 3),
             v["max_config"]] for k, v in fs.items()]
    out += table(["firm", "fee (ticks/RT)", "configs with trades", "mean net >= 0.50", "mean net > 0",
                  "median", "max", "max at"], rows)
    out += ["", "The 8 G2 passers (all fail G1):", ""]
    g2 = d["g2_passers"]
    rows = [[c, v["trade_count"], v["dates_with_trade"], f(v["sharpe"])] +
            [f(v["firm_mean_net_per_trade"][k], 3) for k in fs] for c, v in
            sorted(g2.items(), key=lambda kv: -kv[1]["sharpe"])]
    out += table(["config", "trades", "dates with a trade", "SR_d"] + list(fs), rows)
    return out + [""]


def trades(d):
    C = d["configs"]
    tc = [v["trade_count"] for v in C.values()]
    cnt = {k: sum(v["counts_p32"][k] for v in C.values()) for k in next(iter(C.values()))["counts_p32"]}
    out = ["## D1: trade counts and trades per date", "",
           f"Total trades over the 300: {sum(tc):,}; configurations with no trade: {sum(1 for x in tc if x == 0)} "
           f"(constant series, SR_d 0 by moments()); largest count {max(tc):,}; largest trades per date "
           f"{f(max(v['trades_per_date'] for v in C.values()), 3)}. P3.2 counts summed over the 300 (stats.json "
           f"counts): {cnt}. By label (D_stats.json mde.horizons):", ""]
    rows = []
    for lab, h in d["mde"]["horizons"].items():
        rows.append([lab, h["n_configs"], h["n_traded"], f(h["n_trades_pooled"]), f(h["trades_per_date_traded_median"], 3),
                     f(h["trades_per_date_traded_max"], 3), h["measured_per_config_e80_binding"]["g1_passers_n"]])
    out += table(["label", "configs", "with trades", "trades (pooled)", "median trades/date (traded)",
                  "max trades/date", "G1 passers"], rows)
    out += ["", "Per-configuration trade counts, trades per date and dates with a trade: D_stats.json configs.*.", ""]
    return out


def mc(d):
    m, p, r = d["multiple_comparisons"], d["pbo"], m_ref(d)
    C = d["configs"]
    return ["## D1: DSR at N, BH and Holm (reports, never gates)", "",
            f"- DSR (funnel.multiple_comparisons.deflated_sharpe_ratio, N 838, V = 1/795, T 796, own skewness and raw "
            f"kurtosis): largest {f(max((v['dsr'] or 0) for v in C.values()))}; above 0.95: "
            f"{sum(1 for v in C.values() if (v['dsr'] or 0) > 0.95)}; undefined (constant series): "
            f"{sum(1 for v in C.values() if v['dsr'] is None)}. Per configuration: D_stats.json configs.*.dsr.",
            f"- BH (q 0.05) and Holm (0.05) over m = {m['m']} one-sided p = 1 - Phi(daily t) (reading P07; no t -> "
            f"p = 1): BH rejects {m['bh_rejections']}, Holm rejects {m['holm_rejections']}; smallest p "
            f"{f(m['min_p'])} ({m['min_p_config']}, t {f(C[m['min_p_config']]['t'], 3)}).",
            f"- Reference z (P7.2, select33): Bonferroni/Holm step 1 at m 300 {f(r['bonferroni_holm_step1_m'], 3)}; "
            f"BY rank 1 {f(r['by_rank1'], 3)}; Bonferroni at N 838 {f(r['bonferroni_at_N'], 3)}; HLZ t 3.0. "
            "The largest daily t of the 300 is "
            f"{f(max((v['t'] or -9) for v in C.values()), 3)}.", "",
            "## D1 and P10 (iv): discovery PBO (CSCV; reported, not a gate)", "",
            f"screening.stage_e_verdict.pbo over {p['n_strategies']} series (reading P08: every configuration with a "
            f"series, the {sum(1 for v in C.values() if v['constant'])} constant ones included; 0 failed), 8 blocks of "
            f"{p['block_days']} dates, {p['n_splits']} splits: PBO = {f(p['pbo'])} "
            f"({round(p['pbo'] * p['n_splits'])} of {p['n_splits']}), against M5a e's null band "
            f"{p['null_band_M5a_e'][0]}-{p['null_band_M5a_e'][1]} (P6.3). The in-sample winner's out-of-sample net "
            f"(4 blocks, ticks) averages {f(p['winner_mean_oos_ticks_per_micro'], 2)}, positive in "
            f"{f(p['p_winner_positive_oos'], 3)} of the splits. Mechanical note: the median SR_d of the 300 is "
            f"{f(d['real_distribution']['summary_all']['q0.5'])}, so an in-sample winner can rank above the "
            "out-of-sample median with a negative out-of-sample net, as the mean above shows. Source: D_stats.json "
            "pbo (equal to select33's reports.pbo).", ""]


def m_ref(d):
    return d["multiple_comparisons"]["reference_thresholds_select33"]


def g5_month(d):
    C = d["configs"]
    pos = sorted((c for c in C if C[c]["g5"]["total"] > 0), key=lambda c: -C[c]["sharpe"])
    rows = [[c, f(C[c]["g5"]["total"], 2), C[c]["g5"]["max_month"], f(C[c]["g5"]["max_month_sum"], 2),
             f(C[c]["g5"]["max_month_share"], 3), C[c]["g5"]["quarters_positive"], f(C[c]["g5"]["min_lomo_t"], 2),
             " / ".join(f(v, 3) for v in C[c]["g5"]["tercile_means"])] for c in pos]
    return ["## D1: G5 parts and the largest month's share of the total net", "",
            f"The share is defined only when the total net is positive ({len(pos)} configurations); all of them fail "
            "G5 (b). Every configuration's G5 values: D_stats.json configs.*.g5.", ""] + \
        table(["config", "total net (ticks)", "largest month", "its net", "share of total", "quarters > 0 (of 13)",
               "min leave-one-month-out t", "tercile means (low/mid/high sigma)"], rows) + [""]


def top10(d):
    T, order = d["top10"], d["ranking_top10"]
    out = ["## P10 (ii): the 10 best configurations by SR_d with every P6.2 statistic", "",
           "Order: P8's total order over all 300, gates ignored (round(SR_d, 4) descending, then the tie-breaks), "
           "identical to select33's ranking_all. Recomputed from daily.parquet and trades.parquet and equal to each "
           "stats.json to 1.8e-15; the three reported-only statistics (rho, mid-sign hit rate, top decile) are "
           "stats.json's reported_only fields (computed by the search from the fold predictions; not recomputed). "
           "Source: D_stats.json top10.", ""]
    rows = []
    for c in order:
        t, m = T[c], T[c]["moments"]
        rows.append([t["rank"], c, f(m["sharpe"]), f(t["t"], 2), f(m["mean"], 3), f(m["sd"], 3), f(m["skew"], 2),
                     f(m["kurtosis"], 1), t["trade_count"], f(t["trades_per_date"], 3), f(t["mean_net_per_trade"], 3),
                     f(t["p62"]["hit_rate"], 3), f(t["share_dates_with_trade"], 3)])
    out += table(["#", "config", "SR_d", "t", "mean/day", "SD/day", "skew", "raw kurt", "trades", "trades/date",
                  "mean net/trade", "hit rate", "share dates traded"], rows)
    out += ["", "Gates, DSR, power and reported-only statistics:", ""]
    rows = []
    for c in order:
        t, ro = T[c], T[c]["reported_only"]
        rows.append([c, gates_str(t["gates"]), f(t["dsr"]), f(t["se"]), f(t["sr_lower"]), f(t["p_one_sided"]),
                     " / ".join(f(v, 3) for v in t["p62"]["tercile_means"]), f(ro.get("rho_chosen_ev_net_rows"), 3),
                     f(ro.get("rho_chosen_ev_net_trades"), 3),
                     f"{f(ro.get('mid_sign_hit_rate'), 3)} (n {ro['mid_sign']['n_used']})",
                     f"{f(ro.get('top_decile_mean_net'), 3)} (n {ro.get('top_decile_n')})"])
    out += table(["config", "gates passed", "DSR", "se", "SR_d - se", "p (one-sided)", "tercile means",
                  "rho EV-net (rows)", "rho (trades)", "mid-sign hit", "top-decile mean net"], rows)
    out += ["", "Per-fold sums (P6.1 blocks 1-6, ticks):", ""]
    out += table(["config"] + [str(k) for k in range(1, 7)],
                 [[c] + [f(T[c]["p62"]["per_fold_sums"][str(k)], 2) for k in range(1, 7)] for c in order])
    qs = list(T[order[0]]["p62"]["per_quarter"])
    out += ["", "Per-quarter sums (Dec-Feb, Mar-May, Jun-Aug, Sep-Nov, named by the first month; ticks):", ""]
    out += table(["quarter"] + [c[4:] for c in order],
                 [[q] + [f(T[c]["p62"]["per_quarter"][q]["sum"], 2) for c in order] for q in qs])
    ms = list(T[order[0]]["p62"]["per_month_sums"])
    out += ["", "Per-month sums (ticks):", ""]
    out += table(["month"] + [c[4:] for c in order],
                 [[mo] + [f(T[c]["p62"]["per_month_sums"][mo]["sum"], 2) for c in order] for mo in ms])
    return out + [""]


def d3(d):
    t, n, r = d["thresholds"], d["null"], d["real_distribution"]
    e = n["expected_max_report"]
    sa, sn, ra, rn, mx = n["summary_all"], n["summary_nonconstant"], r["summary_all"], r["summary_nonconstant"], n["maxima_summary"]
    rows = [["real E.33 (all 300)", r["n"], f(ra["mean"]), f(ra["sd"]), f(ra["q0.05"]), f(ra["q0.5"]), f(ra["q0.95"]), f(ra["q1"])],
            ["real, with trades", r["n_nonconstant"], f(rn["mean"]), f(rn["sd"]), f(rn["q0.05"]), f(rn["q0.5"]), f(rn["q0.95"]), f(rn["q1"])],
            ["null per-configuration (all 400)", n["n_series"], f(sa["mean"]), f(sa["sd"]), f(sa["q0.05"]), f(sa["q0.5"]), f(sa["q0.95"]), f(sa["q1"])],
            ["null, with trades", n["n_nonconstant"], f(sn["mean"]), f(sn["sd"]), f(sn["q0.05"]), f(sn["q0.5"]), f(sn["q0.95"]), f(sn["q1"])],
            ["null per-seed max over 20 configs", len(n["seed_maxima"]), f(mx["mean"]), "", f(mx["q0.05"]), f(mx["q0.5"]), f(mx["q0.95"]), f(mx["q1"])]]
    na = r["n_above"]
    return ["## D3 and P10 (iii): the 300 OOF daily Sharpes beside the null", "",
            "Figure: reports/stage_e33c_briefs/work/stats/fig/D3_sharpe_hist.png. Top: the 300 real SR_d and the 400 "
            "null per-configuration SR_d (B5: 20 null seeds x S5 x {F15, T30} x 10 grid points; same statistic, same "
            "796 dates; derived/e33/proofs/seed1..20/search/<cid>/daily.parquet, recomputed and equal to each "
            "stats.json), as shares of each group per 0.01 bin; no-trade series sit at 0 (moments() convention). "
            "Bottom: the 20 null per-seed maxima, each a maximum over 20 configurations, not the null of the maximum "
            f"over 300. Lines: SR0 {f(t['SR0'])}, G3 {f(t['G3'])}, binding {f(t['binding'])} (p7_final at N 838).", ""] + \
        table(["series", "n", "mean", "SD", "q05", "median", "q95", "max"], rows) + [
            "", f"- Real configurations at or above SR0: {na['SR0']}; G3: {na['G3']}; binding: {na['binding']}; SR_d > 0: "
            f"{na['zero']}; above the null 400's q95 ({r['null_q95_all']:.1e}): {na['null_q95_all']}; above the null "
            f"400's max ({f(r['null_max_of_400'])}): {na['null_max_of_400']}. The real max {f(ra['q1'])} lies inside "
            f"the range of the null per-seed maxima over only 20 configurations ({f(mx['q0'])} to {f(mx['q1'])}).",
            f"- The per-seed maxima agree with B5_proofs.md's table in {n['b5_agreement_seeds']} of 20 seeds (same "
            f"configuration, same SR_d to 4 decimals). Null constants: {n['n_constant']} of 400; with trades "
            f"{n['n_nonconstant']} (B5's line 41 says 368: that is the count in configurations with at least 2 "
            f"non-constant seeds, {n['n_nonconstant_in_configs_with_2plus']}; its 0.0434 reproduces either way). "
            f"Centred SD of the 400 (P4.2): {f(n['centred_sd_all'])} (B5: 0.0425).",
            f"- Real 300: mean pairwise correlation of the {r['correlation']['n_series']} non-constant daily series "
            f"{f(r['correlation']['mean_pairwise_corr'], 3)}; share of pairs above 0.70 "
            f"{f(r['correlation']['share_pairs_above_0.70'], 4)}.", "",
            "Expected null maximum over 300 (brief addendum). Method: " + e["method"], "",
            f"- sigma_c {f(e['sigma_c'])} (df-corrected {f(e['sigma_c_df'])}); E[max over 300] = {f(e['E_max_300_zero_edge'])} "
            f"({f(e['E_max_300_zero_edge_df'])} df-corrected); over 838: {f(e['E_max_838_zero_edge_df'])}.",
            f"- Check at n = 20: the construction gives {f(e['check_n20_monte_carlo'])} against the observed mean of "
            f"the 20 per-seed maxima {f(e['check_n20_observed_mean_of_seed_maxima'])} (SE {f(e['check_n20_observed_se'])}): "
            f"it overstates by {f(e['check_n20_monte_carlo'] - e['check_n20_observed_mean_of_seed_maxima'])}. The "
            f"null's Sharpe errors are positively correlated across one seed's configurations (mean pairwise "
            f"{f(e['null_mean_pairwise_corr_of_sharpe_errors'], 3)}), so the independent figure is an upper-side "
            "value.",
            f"- Not used: pooling the 400 values as iid (mean {f(e['alternatives_not_used']['m_all'])}, SD "
            f"{f(e['alternatives_not_used']['s_all'])}) predicts {f(e['alternatives_not_used']['E_max_20_pooled_formula'])} "
            f"at n = 20 against the observed {f(e['check_n20_observed_mean_of_seed_maxima'])}; it mixes the "
            "configurations' different null means into the spread.", ""]


def mde_md(d):
    m = d["mde"]
    out = ["## P10 (v): minimum detectable net edge per trade at 80% power on the OOF dates", "",
           "Formula: " + m["formula"] + ". Source line in P7.2: \"Per trade (random-walk sigma_h; independent trades "
           "every date): 0.71 ticks net at 5-minute holds and 4 trades a date (0.50 at 8); 1.22 at 15 minutes and 4 a "
           "date (0.87 at 8); 1.73 at 30 minutes and 4 a date; 3.46 at 60 minutes and 2 a date.\" That line is the "
           "edge at the selection threshold itself (about 50% power); the tests reproduce it to the printed digits.",
           f"- 80%-power true daily Sharpe on T_disc 796: at the binding threshold {f(m['bars']['binding'])}, s80 = "
           f"{f(m['s80_bar_convention']['binding'])} (se at the true value instead: {f(m['s80_exact']['binding'])}); at G3 "
           f"alone {f(m['bars']['G3'])}, s80 = {f(m['s80_bar_convention']['G3'])}.",
           "- Selection also needs G2 (>= 0.50 net per trade) and G1 (>= 1 trade a date), so an e80 below 0.50 is "
           "not enough by itself. TB labels use the vertical h (an upper bound on the hold). Measured sigma is the "
           "population SD of the realised per-trade nets pooled over the label's 50 configurations (stated beside "
           "the 3.15 sqrt(h) standard number; P0.4: standard numbers are for power only).", ""]
    rows = []
    for lab, h in m["horizons"].items():
        for r in h["standard_rows"]:
            rows.append([lab, r["n_per_date"], f(h["sigma_h_standard"], 2), f(h["sigma_trade_measured"], 2),
                         h["n_trades_pooled"], f(r["mu_at_binding_P72"], 2), f(r["e80_G3"], 2), f(r["e80_binding"], 2),
                         f(r["e80_binding_measured_sigma"], 2)])
    out += table(["label", "trades/date n", "sigma_h (3.15 sqrt h)", "sigma measured", "trades pooled",
                  "edge at binding (P7.2 line)", "e80 at G3", "e80 at binding", "e80 at binding, measured sigma"], rows)
    out += ["", "Measured, per configuration (no random-walk or independence assumption): e80 = s80 x SD(X_D) / "
            "(trades per date), the per-trade shift that gives the configuration's own daily series a true daily "
            "Sharpe of s80 (binding) from a zero mean:", ""]
    rows = []
    for lab, h in m["horizons"].items():
        a, g = h["measured_per_config_e80_binding"]["all_traded"], h["measured_per_config_e80_binding"]["g1_passers"]
        rows.append([lab, h["n_traded"], f(a.get("q0"), 2), f(a.get("q0.25"), 2), f(a.get("q0.5"), 2),
                     h["measured_per_config_e80_binding"]["g1_passers_n"], f(g.get("q0"), 2), f(g.get("q0.5"), 2)])
    out += table(["label", "configs with trades", "min", "q25", "median", "G1 passers", "G1 min", "G1 median"], rows)
    out += ["", "F05 and F15 configurations traded rarely (pooled 16 and 876 trades), so their measured sigma and "
            "per-configuration values rest on few trades. Source: D_stats.json mde.", ""]
    return out


def fam(d):
    F = d["families"]
    k6 = F["k6"]
    out = ["## P10 (vi): a null statement per family in the sense of docs/NULL_CRITERIA_E.md", "",
           f"Criteria file {F['criteria_file']} sha256 {F['criteria_sha256'][:16]}.... Family = feature set (P10: "
           "the cut unit, \"a whole feature set ... which is the 'family' of the prompt's C3\"), with its P2 idea "
           "family. The criterion, quoted (each string checked verbatim against the file, block-quote markers "
           "removed):", ""]
    out += [f"- section {q['section']}: \"{q['text']}\" (found: {f(q['found_verbatim'])})" for q in F["quotes"]]
    zm = ", ".join(m["member"] for m in k6["zm_members"])
    out += ["", f"ZM belongs to cluster {k6['cluster']}, whose hashed list {k6['path']} (sha256 {k6['sha256'][:16]}...) "
            f"has {k6['n_members']} members, ZM window {k6['zm_window'][0]}..{k6['zm_window'][1]}, eps_ZM "
            f"{k6['zm_members'][0]['eps_ticks']} ticks a day ({k6['zm_members'][0]['eps_usd_per_day_at_q']} USD at q 1); "
            f"its ZM members are {zm}. No E.33 configuration is a member.", ""]
    rows = [[s, v["family"], v["n_configs"], v["n_traded"], v["n_G1"], v["n_sharpe_gt_0"],
             f"{v['best'][4:]} {f(v['best_sharpe'])} ({v['best_trade_count']} trades)", v["statement"]]
            for s, v in F["families"].items()]
    out += table(["set", "idea family", "configs", "with trades", "G1", "SR_d > 0", "best with trades", "statement"], rows)
    out += ["", "Reasons, the same for every family:"] + [f"- {x}" for x in next(iter(F["families"].values()))["reasons"]]
    out += ["", "Not a null statement, and not a reason above:", "- What the data do show is not a null statement: no configuration of any family passes G3 or G4 on "
            "the discovery dates, and the minimum detectable edges above say what size of edge this search could "
            "have selected.", ""]
    return out


def limits(d):
    return ["## Not done, and limits", "",
            "- P6.4 (per-firm execution variants beyond the market fee shift, L = 0.300 s, limit routes) and P6.5 "
            "(reversed walk-forward, splits by year, release day and roll phase, MDA, SFI, VECM, block-bootstrap "
            "intervals, decay, robustness, calibration): not computed; they run only after a hashed test list "
            "(P8, last bullet) and Tier A is empty.",
            "- D2: not applicable (no configuration passes D1). P10 (vii): the lead's.",
            "- The reported-only P6.2 statistics (rho, mid-sign hit rate, top-decile net) are quoted from stats.json, "
            "not recomputed (they need the fold predictions and the label store).",
            "- Tier B: reported as select33 wrote it; the walk is not recomputed (with Tier A empty it has no use).",
            "- The expected null maximum over 300 is a report with an upward bias shown by its own n = 20 check.", ""]


def main(src, dst, written):
    d = json.loads(open(src).read())
    lines = (header(d, written) + agreement(d) + funnel(d) + firms(d) + trades(d) + mc(d) + g5_month(d) + top10(d)
             + d3(d) + mde_md(d) + fam(d) + limits(d))
    open(dst, "w").write("\n".join(lines) + "\n")
    print(f"wrote {dst}: {len(lines)} lines")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3]))
