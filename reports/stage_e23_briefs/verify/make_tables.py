"""Render the verification JSONs as markdown tables (tables.md beside this script)."""
from __future__ import annotations

import json
import os

OUT_DIR = "/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e23_briefs/verify"
IDS = ["E23-MEZFh5", "E23-MEZNh5", "E23-MEZBh5", "E23-H6NQh5", "E23-H6NQh20"]


def f(x, d=6):
    if x is None:
        return "-"
    if isinstance(x, bool):
        return "yes" if x else "no"
    if isinstance(x, float):
        return f"{x:.{d}g}"
    return str(x)


def main() -> None:
    fb = json.load(open(f"{OUT_DIR}/recompute_file_based.json"))
    sp_path = f"{OUT_DIR}/spot_audit.json"
    sp = json.load(open(sp_path)) if os.path.exists(sp_path) else {}
    rows = {r["name"]: r for r in fb["rows"]}
    out = []

    def get(name):
        return rows.get(name, {"run": None, "mine": None, "match": None})

    out.append("### T1. Per trigger-hold statistics (run value / recomputed value / match within 1e-9 relative)\n")
    for case in ("base", "stress"):
        out.append(f"\n**{case} case**\n")
        out.append("| id | n | mean | sd | Sharpe | raw t | raw NW t (lags h) | alpha | alpha HAC t | alpha plain t | p_plain | p_nw | p_alpha | R2 |")
        out.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        for tid in IDS:
            cells = []
            for key in ("raw/n", "raw/mean", "raw/sd", "raw/sharpe", "raw/t", "raw/t_nw", "alpha/alpha", "alpha/t_nw",
                        "alpha/t_plain", "alpha/p_plain", "alpha/p_nw", "alpha/p_alpha", "alpha/r2"):
                r = get(f"{tid}/{case}/{key}")
                cells.append(f"{f(r['run'])} / {f(r['mine'])} / {'ok' if r['match'] else 'DIFF'}")
            out.append(f"| {tid} | " + " | ".join(cells) + " |")
    out.append("\n### T2. Screen (Holm one-sided 0.05 over five on base p_alpha; survivor rule)\n")
    out.append("| id | holm_rejects run/mine | alpha t >= 2.0 run/mine | base Sharpe >= 0.3 run/mine |")
    out.append("|---|---|---|---|")
    for tid in IDS:
        a, b, c = get(f"{tid}/screen/holm_rejects"), get(f"{tid}/screen/t_nw_at_least_2"), get(f"{tid}/screen/sharpe_at_least_0.3")
        out.append(f"| {tid} | {f(a['run'])}/{f(a['mine'])} | {f(b['run'])}/{f(b['mine'])} | {f(c['run'])}/{f(c['mine'])} |")
    s = get("screen/survivors")
    out.append(f"\nSurvivors: run {s['run']} / mine {s['mine']} / match {f(s['match'])}. Smallest p_alpha: run {f(get('screen/smallest_p_alpha')['run'])} / mine {f(get('screen/smallest_p_alpha')['mine'])}.\n")
    out.append("\n### T3. DSR at N 538 and CSCV PBO (descriptive)\n")
    out.append("| quantity | run | mine | match |")
    out.append("|---|---|---|---|")
    for name in ("dsr/n_trials", "dsr/sharpe_variance", "dsr/expected_max_daily_sharpe_under_null", *[f"dsr/{t}" for t in IDS],
                 "pbo/pbo", "pbo/n_splits", "pbo/n_days", "pbo/block_days", "pbo/winner_mean_oos_ticks_per_micro",
                 "pbo/p_winner_positive_oos", "pbo/aligned_dates", "pbo/first", "pbo/last"):
        r = get(name)
        out.append(f"| {name} | {f(r['run'], 12)} | {f(r['mine'], 12)} | {'ok' if r['match'] else 'DIFF (see notes)'} |")
    out.append("\n### T4. Power table and the W_cf confirmation gate\n")
    out.append("| id | window | E[t] run/mine | power_gate run/mine | power_holm1 (K 5) run/mine | inconclusive run/mine |")
    out.append("|---|---|---|---|---|---|")
    for tid in IDS:
        for w in ("W_ext", "W_cf"):
            a, b, c, d = (get(f"power/{tid}/{w}/expected_t"), get(f"power/{tid}/{w}/power_gate"),
                          get(f"power/{tid}/{w}/power_holm1"), get(f"power/{tid}/{w}/inconclusive_by_design"))
            out.append(f"| {tid} | {w} | {f(a['run'])}/{f(a['mine'])} | {f(b['run'])}/{f(b['mine'])} | {f(c['run'])}/{f(c['mine'])} | {f(d['run'])}/{f(d['mine'])} |")
    g = fb["w_cf_gate"]
    out.append("\nW_cf power at the hurdle b = max(2.0, z(1 - 0.05/S)), recomputed from the power table's W_cf n_dates (1170 rates, 1204 NQ):\n")
    out.append("| S | b | ZF/ZN/ZB (1170 dates) | NQ (1204 dates) | all < 0.2 |")
    out.append("|---|---|---|---|---|")
    for s_ in ("1", "2", "3", "4"):
        out.append(f"| {s_} | {f(g[s_]['hurdle'])} | {f(g[s_]['E23-MEZFh5'])} | {f(g[s_]['E23-H6NQh5'])} | {f(g[s_]['all_below_0.2'])} |")
    if sp:
        out.append("\n### T5. Independent re-simulation of the books from the ext2010 stores (spot audit)\n")
        out.append("| id | units run/mine | unit_counts match | nonoverlap run/mine | n_dates run/mine | in-market run/mine | fills run/mine | base series: dates equal, max abs diff, values differing | stress series: same | alpha3 t_nw run/mine | all exits h marks after entry | all entries on d0 |")
        out.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
        for root in ("ZF", "ZN", "ZB", "NQ"):
            if root not in sp:
                continue
            for tid, t in sp[root]["trigger_holds"].items():
                b, s_ = t["series_compare"]["base"], t["series_compare"]["stress"]
                a3 = t["alpha3"]["t_nw"]
                out.append(f"| {tid} | {t['units']['run']}/{t['units']['mine']} | {f(t['unit_counts']['match'])} | {t['nonoverlapping']['run']}/{t['nonoverlapping']['mine']} | "
                           f"{t['n_dates']['run']}/{t['n_dates']['mine']} | {f(t['in_market_fraction']['run'])}/{f(t['in_market_fraction']['mine'])} | "
                           f"{t['fills_total']['run']}/{t['fills_total']['mine']} | {f(b['dates_equal'])}, {f(b['max_abs_diff'], 3)}, {b['n_values_differ_gt_1e-9rel']} | "
                           f"{f(s_['dates_equal'])}, {f(s_['max_abs_diff'], 3)}, {s_['n_values_differ_gt_1e-9rel']} | {f(a3['run'])}/{f(a3['mine'])} ({'ok' if a3['match'] else 'DIFF'}) | "
                           f"{f(t['all_units_exit_h_marks_after_entry'])} | {f(t['all_units_entry_eq_d0'])} |")
        out.append("\n### T6. Spot units\n")
        for root in ("ZF", "ZN", "ZB", "NQ"):
            if root not in sp:
                continue
            for tid, t in sp[root]["trigger_holds"].items():
                out.append(f"\n**{tid}** (store {sp[root]['store']['path'].split('/')[-1]}, sha256 matches the marker's preflight: {f(sp[root]['store']['sha256_equals_marker_preflight'])})\n")
                out.append("| unit | d0 | tau (CT) | settle minute | tau before S | d_e | d_x | marks between | u | mark price (ticks) | sigma(d_e) | returns before d_e | contracts per $ capital | entry cost c/side base/stress | stress = comm + 2 x slip | value d_e run/mine (base) | entry day is cost only | next mark value run/mine (base) | next value from mark move | value d_x run/mine (base) | splices in hold |")
                out.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
                for name, u in t["spot_units"].items():
                    o = u.get("order_on_d_e") or {}
                    ec = u.get("entry_cost_cents_per_side") or {}
                    e1 = u.get("entry_day_value_is_cost_only") or {}
                    e2 = u.get("next_day_value_from_mark_move") or {}
                    out.append(f"| {name} | {u['d0']} | {u['tau_ct']} | {u['settle_minute_ct']} | {f(u['tau_before_settle_open'])} | {u['d_e']} | {u['d_x']} | {u['marks_between']} | {u['u']} | "
                               f"{u['mark_price_ticks_d_e']}{' (close of S-1)' if u['mark_is_close_of_S-1'] else ''} | {f(u['sigma_d_e'])} | {u['n_returns_before_d_e']} | "
                               f"{f(o.get('target_contracts_per_capital'))} ({o.get('kind', 'no order: net unchanged')}) | {ec.get('base', '-')}/{ec.get('stress', '-')} | {f(ec.get('stress_eq_comm_plus_2x_slip'))} | "
                               f"{f(u['run_value_d_e']['base'])}/{f(u['mine_value_d_e']['base'])} | {f(e1.get('match'))} | {f(u['run_value_next']['base'])}/{f(u['mine_value_next']['base'])} | {f(e2.get('match'))} | "
                               f"{f(u['run_value_d_x']['base'])}/{f(u['mine_value_d_x']['base'])} | {u['splices_in_hold']} |")
                if t["spot_excluded_examples"]:
                    out.append("\nExcluded-unit examples (reason: d0, d_e, d_x): " + "; ".join(f"{k}: {v}" for k, v in t["spot_excluded_examples"].items()))
    out.append("\n### T7. Every recomputed row\n")
    out.append("| name | run | mine | match |")
    out.append("|---|---|---|---|")
    for r in fb["rows"]:
        out.append(f"| {r['name']} | {f(r['run'], 12)} | {f(r['mine'], 12)} | {'ok' if r['match'] else 'DIFF'} |")
    open(f"{OUT_DIR}/tables.md", "w").write("\n".join(out) + "\n")
    print("tables.md:", len(out), "lines")


if __name__ == "__main__":
    main()
