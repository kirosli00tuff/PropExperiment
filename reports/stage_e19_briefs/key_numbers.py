"""Stage E.19 lead: key-number tables for reports/stage_e19_results.md, read from reports/stage_e19_results.json.
Prints markdown. Usage: python3 reports/stage_e19_briefs/key_numbers.py > reports/stage_e19_briefs/key_numbers.md"""
import json

D = json.load(open("reports/stage_e19_results.json"))
R = D["records"]
OPT = {(o["size"], o["path"], o["dll"], o["pricing"], o["edge"]): o for o in D["derived"]["optimum_band"]}
BE = {(b["size"], b["path"], b["dll"], b["pricing"]): b for b in D["derived"]["break_even"]}


def rec(size, path, dll, pricing, edge, f, b2f=False, family="headline", variant="base"):
    m = [r for r in R if r["family"] == family and r["variant"] == variant and r["size"] == size and r["path"] == path
         and r["dll"] == dll and r["pricing"] == pricing and r["edge"] == edge and abs(r["f"] - f) < 1e-9
         and r["b2f"] == b2f]
    assert len(m) == 1, (size, path, dll, pricing, edge, f, b2f, len(m))
    return m[0]


def money(x):
    return f"{x:,.0f}"


print("| size | path | DLL | edge | best band f | cycle net (SE) | net ex API | P(no payout) | P(pass) | net per purchase "
      "| per funded XFA | purchases | cycle days | days to 1st payout | B2F on: net | break-even S (best f) |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for size in ("50K", "100K", "150K"):
    for path in ("standard", "consistency"):
        for dll in (False, True):
            for edge in ("zero_k1", "S0.5"):
                o = OPT[(size, path, dll, "standard", edge)]
                r = rec(size, path, dll, "standard", edge, o["best_f"])
                rb = rec(size, path, dll, "standard", edge, o["best_f"], b2f=True)
                be = BE[(size, path, dll, "standard")]["best_band_f"]
                be = be if isinstance(be, str) else f"{be:.2f}"
                print(f"| {size} | {path} | {'on' if dll else 'off'} | {edge} | {o['best_f']:.2f} | {money(r['net_mean'])} "
                      f"({r['net_se']:.0f}) | {money(r['net_ex_api_mean'])} | {r['p_no_payout']:.3f} | "
                      f"{r['att_p_pass']:.3f} | {money(r['net_per_purchase'])} | {money(r['per_funded_xfa'])} | "
                      f"{r['mean_purchases']:.1f} | {r['mean_cycle_days']:.0f} | {r['mean_days_to_first_payout']:.0f} | "
                      f"{money(rb['net_mean'])} ({rb['net_se']:.0f}) | {be} |")
print()
print("Zero edge, every band f (DLL off, standard pricing, Back2Funded off): cycle mean net")
print()
print("| size | path | f 0.05 | f 0.10 | f 0.15 | f 0.20 | f 0.25 | f 0.35 (diag) | f 0.50 (diag) | best band f gap to runner-up (paired SE) |")
print("|---|---|---|---|---|---|---|---|---|---|")
ALL = {(o["size"], o["path"], o["dll"], o["pricing"], o["edge"]): o for o in D["derived"]["optimum_all_f"]}
for size in ("50K", "100K", "150K"):
    for path in ("standard", "consistency"):
        o = OPT[(size, path, False, "standard", "zero_k1")]
        a = ALL[(size, path, False, "standard", "zero_k1")]["all_f"]["means"]
        cells = " | ".join(money(a[k]) for k in ("0.05", "0.10", "0.15", "0.20", "0.25", "0.35", "0.50"))
        print(f"| {size} | {path} | {cells} | {o['best_f']:.2f} vs {o['runner_up_f']:.2f}: {money(o['gap'])} "
              f"({o['gap_paired_se']:.0f}) |")
