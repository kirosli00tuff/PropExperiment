"""Write the markdown tables for D4_verify.md and a per-configuration CSV from the own results
and the two comparison files. Prints line counts only."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_common as vc  # noqa: E402

own = json.load(open(vc.OUT / "gates_own.json"))
S, G, SUM = own["stats"], own["gates"], own["summary"]
P = json.load(open(vc.REPO / "reports/stage_e33c_briefs/select/P8_select33.json"))
PC = {r["config"]: r for r in P["configs"]}
D = json.load(open(vc.WORK / "D_stats.json"))
DC = D["configs"]
ids = vc.all_config_ids()


def f(x, nd=6):
    if x is None:
        return "None"
    if isinstance(x, bool):
        return "T" if x else "F"
    if isinstance(x, int):
        return str(x)
    return f"{x:.{nd}g}"


def ag(a, b) -> str:
    return "agree" if (a == b if isinstance(a, (bool, int, str)) and not isinstance(a, float) else vc.rel_equal(a, b)) else "DIFFER"


lines = []
L = lines.append
L("## T1. Funnel (count passing each gate alone and in order)")
L("| gate | own | P8_select33 | D_stats |")
L("|---|---|---|---|")
for k in ("G1", "G2", "G3", "G4", "G5"):
    L(f"| {k} alone | {SUM['funnel_alone'][k]} | {P['funnel']['alone'][k]} | {D['funnel']['alone'][k]} |")
for k in ("G1", "G1..G2", "G1..G3", "G1..G4", "G1..G5"):
    L(f"| {k} in order | {SUM['funnel_in_order'][k]} | {P['funnel']['in_order'][k]} | {D['funnel']['in_order'][k]} |")
L(f"| G3 alone, own DSR formula | {SUM['G3_alone_own_formula']} | - | - |")
L(f"| failed configurations | 0 | {P['funnel']['failed_configs']} | - |")
L("")
bt = SUM["b_test_values"]
L("## T2. Thresholds")
L("| quantity | own (program function) | own (own formula, NormalDist) | P8_select33 | D_stats |")
L("|---|---|---|---|---|")
L(f"| b_test (max of 3/sqrt(870) and SR with DSR 0.95 at N 838, V 1/869, normal moments) | {bt['b_test_program']!r} | {bt['b_test_own']!r} | {P['b_test']!r} | {D['thresholds']['b_test']!r} |")
L(f"| 3/sqrt(T_test) | {bt['t_bar']!r} | - | - | - |")
L(f"| G3 SR threshold at normal moments (information) | {bt['g3_sr_threshold_normal_program']!r} | {bt['g3_sr_threshold_normal_own']!r} | - | {D['thresholds']['G3']!r} |")
L(f"| SR0 = E[max SR] at N 838, V 1/795 | {G[ids[0]]['dsr_program']['sr0']!r} | {G[ids[0]]['dsr_own']['sr0']!r} | - | {D['thresholds']['SR0']!r} |")
L(f"| N, T_disc, T_test | {vc.N_TRIALS}, {vc.T_DISC}, {vc.T_TEST} | - | {P['n_trials']}, {P['t_disc']}, - | {D['thresholds']['N']}, {D['thresholds']['T_disc']}, {D['thresholds']['T_test']} |")
L("")
L("## T3. The 10 best configurations by the P8 ranking key (SR_d rounded to 4 dp, then tiebreaks): own values, with agreement flags against P8_select33 (P) and D_stats (D)")
L("| rank | config | trades | dates w/ trade | mean net/trade | hit rate | mean X_D | pop SD | SR_d | skew | kurtosis | t | DSR program | DSR own formula | se | SR_d - se | G5 quarters>0 | max month share | min LOMO t | tercile means | gates G1..G5 | P | D |")
L("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for r, cid in enumerate(SUM["top10"], start=1):
    s, g, p, d = S[cid], G[cid], PC[cid], DC[cid]
    m = s["moments"]
    pa = all([vc.rel_equal(m["sharpe"], p["sharpe"]), vc.rel_equal(g["dsr_program"]["dsr"], p["dsr"]),
              vc.rel_equal(g["se_sharpe"], p["se"]), s["trade_count"] == p["trade_count"],
              vc.rel_equal(s["mean_net_per_trade"], p["mean_net_per_trade"]), vc.rel_equal(s["t_stat"], p["t"]),
              all(g[k] == p["gates"][k] for k in ("G1", "G2", "G3", "G4", "G5")),
              vc.rel_equal(g["G5c_min_t"], p["g5"]["min_lomo_t"]), vc.rel_equal(g["G5b_max_month_share"], p["g5"]["max_month_share"]),
              g["G5a_quarters_positive"] == p["g5"]["quarters_positive"],
              all(vc.rel_equal(a, b) for a, b in zip(g["G5d_tercile_means"], p["g5"]["tercile_means"]))])
    da = all([vc.rel_equal(m["sharpe"], d["sharpe"]), vc.rel_equal(g["dsr_program"]["dsr"], d["dsr"]),
              vc.rel_equal(g["se_sharpe"], d["se"]), s["trade_count"] == d["trade_count"],
              vc.rel_equal(s["mean_net_per_trade"], d["mean_net_per_trade"]), vc.rel_equal(s["hit_rate"], d["hit_rate"]),
              vc.rel_equal(s["t_stat"], d["t"]), all(g[k] == d["gates"][k] for k in ("G1", "G2", "G3", "G4", "G5")),
              vc.rel_equal(g["G5c_min_t"], d["g5"]["min_lomo_t"]), vc.rel_equal(g["G5b_max_month_share"], d["g5"]["max_month_share"]),
              g["G5a_quarters_positive"] == d["g5"]["quarters_positive"],
              all(vc.rel_equal(a, b) for a, b in zip(g["G5d_tercile_means"], d["g5"]["tercile_means"])),
              D["top10"][cid]["rank"] == r])
    gates = "".join("T" if g[k] else "F" for k in ("G1", "G2", "G3", "G4", "G5"))
    L(f"| {r} | {cid} | {s['trade_count']} | {s['dates_with_trade']} | {f(s['mean_net_per_trade'])} | {f(s['hit_rate'])} | {f(m['mean'])} | {f(m['sd'])} | {f(m['sharpe'], 10)} | {f(m['skew'])} | {f(m['kurtosis'])} | {f(s['t_stat'])} | {f(g['dsr_program']['dsr'], 10)} | {f(g['dsr_own']['dsr'], 10)} | {f(g['se_sharpe'])} | {f(g['sr_minus_se'])} | {g['G5a_quarters_positive']}/13 | {f(g['G5b_max_month_share'])} | {f(g['G5c_min_t'])} | {', '.join(f(x, 4) for x in g['G5d_tercile_means'])} | {gates} | {'agree' if pa else 'DIFFER'} | {'agree' if da else 'DIFFER'} |")
L("")
L("## T4. Reported-only P6.2 statistics of the 10 best (own; agreement with stats.json (E) and D_stats top10 (D))")
L("| config | rows (row_ok) | rho(EV chosen, net) rows | rho trades | top-decile n | top-decile mean net | mid-sign hit rate | n_used/n_nan/n_zero | E | D |")
L("|---|---|---|---|---|---|---|---|---|---|")
for cid in SUM["top10"]:
    r = json.load(open(vc.OUT / "resim" / f"{cid}.json"))["reported_only"]
    e = json.load(open(vc.SEARCH / cid / "stats.json"))["reported_only"]
    d = D["top10"][cid]["reported_only"]
    keys = ("n_rows", "rho_chosen_ev_net_rows", "rho_chosen_ev_net_trades", "top_decile_n", "top_decile_mean_net", "mid_sign_hit_rate")
    ea = all(vc.rel_equal(r[k], e[k]) for k in keys) and all(r["mid_sign"][k] == e["mid_sign"][k] for k in ("n_used", "n_nan", "n_zero"))
    da = all(vc.rel_equal(r[k], d[k]) for k in keys) and all(r["mid_sign"][k] == d["mid_sign"][k] for k in ("n_used", "n_nan", "n_zero"))
    ms = r["mid_sign"]
    L(f"| {cid} | {r['n_rows']} | {f(r['rho_chosen_ev_net_rows'])} | {f(r['rho_chosen_ev_net_trades'])} | {r['top_decile_n']} | {f(r['top_decile_mean_net'])} | {f(r['mid_sign_hit_rate'])} | {ms['n_used']}/{ms['n_nan']}/{ms['n_zero']} | {'agree' if ea else 'DIFFER'} | {'agree' if da else 'DIFFER'} |")
L("")
L("## T5. Configurations within 10% of a non-zero gate threshold (own values; every one was fully re-simulated)")
L("| config | gate | value | threshold | gate result (own / P8 / D) |")
L("|---|---|---|---|---|")
gate_of = {"G1 trade_count": "G1", "G1 dates_with_trade": "G1", "G2 mean_net_per_trade": "G2", "G3 DSR": "G3",
           "G4 SR-se": "G4", "G5a quarters_positive": "G5", "G5b max_month_share": "G5", "G5c min_loo_t": "G5"}
n_zero_items = 0
for cid, items in SUM["near_threshold"].items():
    for it in items:
        if it["gate"] in gate_of:
            gk = gate_of[it["gate"]]
            L(f"| {cid} | {it['gate']} | {f(it['value'], 8)} | {f(it['threshold'], 8)} | {f(G[cid][gk])} / {f(PC[cid]['gates'][gk])} / {f(DC[cid]['gates'][gk])} |")
        else:
            n_zero_items += 1
L("")
nz_cfg = {c for c, items in SUM["near_threshold"].items() if any(i["gate"] not in gate_of for i in items)}
nz_nonconst = sorted(c for c in nz_cfg if not S[c]["constant_series"])
L(f"Zero-threshold items (G5 b total > 0 and G5 d tercile means > 0, 'within 10%' read as within 0.1 standard errors of 0): {n_zero_items} items on {len(nz_cfg)} configurations, of which {len(nz_cfg) - len(nz_nonconst)} are the constant (no-trade) series sitting exactly on 0 and {len(nz_nonconst)} trade: {', '.join(nz_nonconst)}. All 300 were re-simulated, so the list does not limit the check.")
L("")
L("## T6. Gate passers alone")
g1 = [c for c in ids if G[c]["G1"]]
g2 = [c for c in ids if G[c]["G2"]]
L(f"G1 alone ({len(g1)}): {', '.join(g1)}")
L("")
L(f"G2 alone ({len(g2)}): " + "; ".join(f"{c} (trades {S[c]['trade_count']}, mean net {S[c]['mean_net_per_trade']:.4f}, G1 {f(G[c]['G1'])})" for c in g2))
L("")
L(f"G1 and G2 both: {[c for c in ids if G[c]['G1'] and G[c]['G2']]}")
L("")
L("## T7. Tier walks (own)")
L(f"Passers of G1-G5: {SUM['passers']}; Tier A: {SUM['tier_a']}; Tier B (continue from position 0, gates ignored, constant series skipped): {SUM['tier_b']} with correlations {SUM['tier_b_corr']}; P8: tier_a {P['tier_a']}, tier_b {P['tier_b']}, start_position {P['tier_b_detail']['continue']['start_position']}.")
L("")
L(f"Constant (no-trade) series: {SUM['n_constant_series']}; configurations with trades: {SUM['n_with_trades']}.")
L(f"Sigma_ZM tercile bounds: t1 max {SUM['sigma_terciles_bounds']['t1_max_sigma']:.6f}, t2 {SUM['sigma_terciles_bounds']['t2_min_sigma']:.6f}-{SUM['sigma_terciles_bounds']['t2_max_sigma']:.6f}, t3 min {SUM['sigma_terciles_bounds']['t3_min_sigma']:.6f}.")

out_md = vc.OUT / "report_tables.md"
out_md.write_text("\n".join(lines) + "\n")

# per-configuration CSV
with open(vc.OUT / "gates_table.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["rank", "config", "trade_count", "dates_with_trade", "mean_net_per_trade", "hit_rate", "mean", "sd",
                "sharpe", "skew", "kurtosis", "t", "dsr_program", "dsr_own", "se", "sr_minus_se", "quarters_positive",
                "max_month_share", "min_lomo_t", "terc1", "terc2", "terc3", "G1", "G2", "G3", "G4", "G5",
                "P8_gates_equal", "D_gates_equal", "P8_sharpe_equal", "D_sharpe_equal"])
    for r, cid in enumerate(SUM["ranking"], start=1):
        s, g, p, d = S[cid], G[cid], PC[cid], DC[cid]
        m = s["moments"]
        w.writerow([r, cid, s["trade_count"], s["dates_with_trade"], s["mean_net_per_trade"], s["hit_rate"], m["mean"], m["sd"],
                    m["sharpe"], m["skew"], m["kurtosis"], s["t_stat"], g["dsr_program"]["dsr"], g["dsr_own"]["dsr"],
                    g["se_sharpe"], g["sr_minus_se"], g["G5a_quarters_positive"], g["G5b_max_month_share"], g["G5c_min_t"],
                    *g["G5d_tercile_means"], g["G1"], g["G2"], g["G3"], g["G4"], g["G5"],
                    all(g[k] == p["gates"][k] for k in ("G1", "G2", "G3", "G4", "G5")),
                    all(g[k] == d["gates"][k] for k in ("G1", "G2", "G3", "G4", "G5")),
                    vc.rel_equal(m["sharpe"], p["sharpe"]), vc.rel_equal(m["sharpe"], d["sharpe"])])
print("report_tables.md lines", len(lines), "; gates_table.csv rows 300")
