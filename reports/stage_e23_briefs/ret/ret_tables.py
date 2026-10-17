"""E.23 return tables from the run files (discovery result, power table). Prints markdown."""
import json
from pathlib import Path

R = Path(__file__).resolve().parents[3]
disc = json.loads((R / "reports/stage_e23_runs/discovery/discovery_result.json").read_text())
power = json.loads((R / "reports/stage_e23_power.json").read_text())
IDS = ["E23-MEZFh5", "E23-MEZNh5", "E23-MEZBh5", "E23-H6NQh5", "E23-H6NQh20"]


def f(x, n=2):
    return "n/a" if x is None else f"{x:.{n}f}"


print("| Id | Root, m, h | Units (events) | Non-overlap | In market | Case | Net Sharpe | Raw t (NW) | Alpha t_NW (plain) | p_alpha | alpha3 t_NW | R^2 | Net (gross, costs) capital units |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for i in IDS:
    t = disc["trigger_holds"][i]
    for case in ("base", "stress"):
        c = t["cases"][case]; raw, al, a3 = c["raw"], c["alpha"], c["alpha3_descriptive"]
        gc = t["gross_costs"][case]
        head = (f"| {i} | {t['root']}, {t['m']:+d}, {t['h']} | {t['units']} ({t['unit_counts']['events']}) | "
                f"{t['nonoverlapping']} | {t['in_market_fraction_units']:.2f}") if case == "base" else "| | | | |"
        print(f"{head} | {case} | {f(raw['sharpe'])} | {f(raw['t'])} ({f(raw['t_nw'])}) | {f(al['t_nw'])} ({f(al['t_plain'])}) | "
              f"{f(al['p_alpha'],3)} | {f(a3['t_nw'])} | {f(al['r2'],3)} | {gc['net']:.3f} ({gc['gross']:.3f}, {gc['costs']:.3f}) |")
s = disc["screen"]
print()
print(f"Screen: K = {s['k']}, Holm one-sided {s['holm_alpha']}; eligible {s['eligible']}; survivors {s['survivors']}.")
print("Checks: " + "; ".join(f"{i}: Holm {v['holm_rejects']}, t>=2 {v['t_nw_at_least_2']}, Sharpe>=0.3 {v['sharpe_at_least_0.3']}" for i, v in s["checks"].items()))
dd = disc["dsr_descriptive"]; pb = disc["pbo_descriptive"]
print(f"DSR at N {dd['n_trials']} (variance over {dd['variance_over_n_members']} discovery Sharpes): " + ", ".join(f"{i} {dd['dsr'][i]:.4f}" for i in IDS))
print(f"CSCV PBO (8 blocks of {pb['block_days']} days, {pb['n_splits']} splits, {pb['n_days']} aligned dates {pb['first']}..{pb['last']}): {pb['pbo']:.3f}")
print()
print("| Id | Window | Book dates (first) | Events | Units | Non-overlap | In market | E[t] | power_gate | power_holm1 (K 5) | Label |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
for i in IDS:
    for w in ("W_ext", "W_cf"):
        r = power["rows"][i][w]
        lab = "inconclusive by design" if r["inconclusive_by_design"] else "read"
        print(f"| {i} | {w} | {r['n_dates']} ({r['first_book_date']}) | {r['events']} | {r['units']} | {r['nonoverlapping']} | "
              f"{r['in_market_fraction']:.2f} | {r['expected_t']:.3f} | {r['power_gate']:.3f} | {r['power_holm1']:.3f} | {lab} |")
print()
print("Per year, base net Sharpe (n):")
for i in IDS:
    py = disc["trigger_holds"][i]["cases"]["base"]["per_year"]
    print(f"- {i}: " + ", ".join(f"{y} {f(v.get('sharpe') if isinstance(v, dict) else None)}" for y, v in py.items()))
