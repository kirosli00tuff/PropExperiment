import json
from pathlib import Path
H = Path(__file__).resolve().parent
my = json.load(open(H / "my_numbers.json")); bf = json.load(open(H / "boot_final.json")); lp = json.load(open(H / "loop_check.json"))
gr = json.load(open(H / "gross_e10.json"))
cmp_ = {}
for f in ("engine_compare.json", "engine_compare_extra.json", "engine_compare_2021-07-16.json"):
    cmp_.update(json.load(open(H / f)))
label = {"2021-01-15": "rule: 10th incl. 2021", "2022-01-14": "rule: 10th incl. 2022", "2023-01-17": "rule: 10th incl. 2023",
         "2021-07-16": "summer (CDT) 2021", "2022-07-19": "summer (CDT) 2022", "2023-07-18": "summer (CDT) 2023",
         "2021-01-04": "extra: Monday, bad-flag day", "2022-12-27": "extra: 19 crossed moments", "2023-01-03": "extra: 14 crossed moments"}
order = ["2021-01-15", "2022-01-14", "2023-01-17", "2021-07-16", "2022-07-19", "2023-07-18", "2021-01-04", "2022-12-27", "2023-01-03"]
L = []
L.append("| trade date | sample | raw instr. (= days.parquet) | placements | price match | filled match (mine/prod) | t_fill exact (ns) | c_half match | E_10 drop match | E_10 no-drop match | mismatches |")
L.append("|---|---|---|---|---|---|---|---|---|---|---|")
tot = dict(rows=0, price=0, fill=0, both=0, tf=0, ch=0, ed=0, en=0, fm=0, fp=0)
for T in order:
    r = cmp_[T]
    mism = (r["rows"] - r["price_match"]) + (r["rows"] - r["filled_match"]) + (r["both_filled"] - r["tfill_exact_match"]) + (r["both_filled"] - r["c_half_match(1e-9)"]) + (r["both_filled"] - r["E10_drop_match"]) + (r["both_filled"] - r["E10_nodrop_match"])
    L.append(f"| {T} | {label[T]} | {r['raw_symbol_prod']} ({r['instrument_id_prod']}) | {r['rows']} | {r['price_match']}/{r['rows']} | {r['filled_match']}/{r['rows']} ({r['filled_mine']}/{r['filled_prod']}) | {r['tfill_exact_match']}/{r['both_filled']} | {r['c_half_match(1e-9)']}/{r['both_filled']} | {r['E10_drop_match']}/{r['both_filled']} | {r['E10_nodrop_match']}/{r['both_filled']} | {mism} |")
    tot["rows"] += r["rows"]; tot["price"] += r["price_match"]; tot["fill"] += r["filled_match"]; tot["both"] += r["both_filled"]
    tot["tf"] += r["tfill_exact_match"]; tot["ch"] += r["c_half_match(1e-9)"]; tot["ed"] += r["E10_drop_match"]; tot["en"] += r["E10_nodrop_match"]
    tot["fm"] += r["filled_mine"]; tot["fp"] += r["filled_prod"]
L.append(f"| **total** | 9 dates | | **{tot['rows']}** | **{tot['price']}/{tot['rows']}** | **{tot['fill']}/{tot['rows']}** ({tot['fm']}/{tot['fp']}) | **{tot['tf']}/{tot['both']}** | **{tot['ch']}/{tot['both']}** | **{tot['ed']}/{tot['both']}** | **{tot['en']}/{tot['both']}** | **0** |")
(H / "tbl_engine.md").write_text("\n".join(L))
M = ["| trade date | producer RT / entries / orders / mean RT s | mine, replacement decided at the cancel decision (j+60 s) | mine, replacement at cancel effective (j+60.05 s) |", "|---|---|---|---|"]
for T in order:
    p = lp[T]["prod"]; a = lp[T]["A_repl_at_cancel_decision"]; b = lp[T]["B_repl_at_cancel_effective"]
    f = lambda x: f"{x['round_trips']} / {x['entries_filled']} / {x['orders_placed']} / {x['mean_rt_s']:.2f}"
    ok = "exact" if (a["round_trips"], a["entries_filled"], a["orders_placed"]) == (p["round_trips"], p["entries_filled"], p["orders_placed"]) and abs(a["mean_rt_s"] - p["mean_rt_s"]) < 1e-3 else "DIFF"
    M.append(f"| {T} | {f(p)} | {f(a)} ({ok}) | {f(b)} |")
(H / "tbl_loop.md").write_text("\n".join(M))
print((H / "tbl_engine.md").read_text()); print(); print((H / "tbl_loop.md").read_text())
