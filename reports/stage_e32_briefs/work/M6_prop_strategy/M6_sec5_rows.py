"""M6 (E.32): print section-5 table rows from M6_variants_out.json (formatting only)."""
import json
from statistics import NormalDist
N = NormalDist(); S15 = 3.15 * 15 ** 0.5
d = json.load(open("M6_variants_out.json"))
fun = {(r["firm"], r["case"]): r for r in d["funnel_S15"]}
def ps(a): return "-" if a is None else f"{N.cdf(a / S15):.4f}"
def f3(a): return "n/a" if a is None else f"{a:.3f}"
for firm in ("topstep", "lucid", "lucid_u", "tradeify", "mffu", "bulenox"):
    F = d["firm"][firm]
    m = F["M"]
    print(f"| {firm} | (i) market | 1 | {m['S15']:.3f} | {m['S15']:.3f} | {f3(m['alpha_be'])} | {ps(m['alpha_be'])} | {f3(m['alpha_net1'])} |")
    for tag, v in F.items():
        if tag == "M" or "|tau=1.0|" not in tag: continue
        s = v["S15"]
        print(f"| {firm} | {tag} L | {s['p']:.3f} | {s['L']:.3f} | {s['L_per_trade']:.3f} | {f3(v['alpha_be_L'])} | {ps(v['alpha_be_L'])} | {f3(v['alpha_net1_per_trade_L'])} |")
        print(f"| {firm} | {tag} LC | 1 | {s['LC']:.3f} | {s['LC']:.3f} | {f3(v['alpha_be_LC'])} | {ps(v['alpha_be_LC'])} | {f3(v['alpha_net1_LC'])} |")
print()
for (firm, case), r in fun.items():
    print(f"| {firm} | {case} | {r['mu_net']:.3f} | {r['T']:.2f} | {r['p_dll_eval_m1']:.4f} | {r['p_breach_eval_m1']:.3f} | {r['p_breach_fund_m1']:.3f} | {r['p_pass_first_attempt']:.3f} | {r['p_paid_within_756']:.3f} | {r['mean_days_to_first_payout']:.1f} | {r['mean_fees_to_first_payout']:.0f} |")
