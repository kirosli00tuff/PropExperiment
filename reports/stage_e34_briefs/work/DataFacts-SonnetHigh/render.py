import json, glob
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
a = json.load(open(HERE / "agg_zl.json")); b = json.load(open(HERE / "agg_bars.json")); man = json.load(open(HERE / "manifest_facts.json"))
TD = json.load(open(HERE / "trade_dates_e33rule.json"))
L = []
f = lambda s: f"{s['median']:,.0f} ({s['p5']:,.0f}-{s['p95']:,.0f})"
L.append("| group | dates | all | trades T | adds A | cancels C | modifies M | other | day session | rest |")
L.append("|---|---|---|---|---|---|---|---|---|---|")
names = {"all_816": "all 816", "2020-12": "2020 (Dec)", "2021": "2021", "2022": "2022", "2023": "2023", "2024": "2024 (Jan-Feb)", "OOF_796": "OOF 796"}
for g, nm in names.items():
    s = a["stats"][g]
    L.append(f"| {nm} | {s['all']['n_dates']} | " + " | ".join(f(s[k]) for k in ("all", "T", "A", "C", "M", "other", "ses", "rest")) + " |")
open(HERE / "tab_daily.md", "w").write("\n".join(L) + "\n")
# totals by action x segment
t = a["action_by_segment_total"]; tot = sum(sum(v) for v in t.values())
L = ["| action | rest of day | day session 08:30-13:20 CT | total | share of all |", "|---|---|---|---|---|"]
lab = {"A": "A add", "C": "C cancel", "M": "M modify", "T": "T trade", "F": "F fill", "R": "R clear", "N": "N none"}
for k in "ACMTFRN":
    r, s = t[k]; L.append(f"| {lab[k]} | {r:,} | {s:,} | {r+s:,} | {100*(r+s)/tot:.2f}% |")
r = sum(v[0] for v in t.values()); s = sum(v[1] for v in t.values()); L.append(f"| all | {r:,} | {s:,} | {r+s:,} | 100% |")
open(HERE / "tab_action_seg.md", "w").write("\n".join(L) + "\n")
# bars
L = ["| root | files | bar records | dates | bars per date median (min-max) | p5-p95 | day-session bars median (min-max) |", "|---|---|---|---|---|---|---|"]
for r in ("ZL", "ZS", "ZM"):
    x = b[r]; bp = x["bars_per_date"]; ds = x["day_session_bars"]
    L.append(f"| {r}.v.0 | {x['files']} | {x['records']:,} | {x['n_dates']} | {bp['median']:.0f} ({bp['min']}-{bp['max']}) | {bp['p5']:.0f}-{bp['p95']:.0f} | {ds['median']:.0f} ({ds['min']}-{ds['max']}) |")
open(HERE / "tab_bars.md", "w").write("\n".join(L) + "\n")
# bars by year
L = ["| root | 2020 | 2021 | 2022 | 2023 | 2024 |", "|---|---|---|---|---|---|"]
for r in ("ZL", "ZS", "ZM"):
    L.append(f"| {r} | " + " | ".join(f"{b[r]['by_year'][y]['median']:.0f} ({b[r]['by_year'][y]['min']}-{b[r]['by_year'][y]['max']})" for y in ("2020", "2021", "2022", "2023", "2024")) + " |")
open(HERE / "tab_bars_year.md", "w").write("\n".join(L) + "\n")
# per-date totals, min/max dates (counts only)
day = {}
for fn in glob.glob(str(HERE / "counts" / "zl_*.json")):
    for d, v in json.load(open(fn))["per_day_action_by_seg"].items():
        day[d] = day.get(d, 0) + sum(sum(x) for x in v.values())
o = sorted(TD, key=lambda d: day[d])
print("lowest", [(d, day[d]) for d in o[:6]]); print("highest", [(d, day[d]) for d in o[-4:]])
# per-file TSV
z3 = sorted([x for x in man["files"] if x["series"] == "Z3"], key=lambda x: x["month"])
rows = ["month\tfile\tbytes_zst\trecords\tdelivered_bytes\tinstrument_ids"]
for x in z3:
    rows.append(f"{x['month']}\t{x['name']}\t{x['bytes']}\t{x['records']}\t{x['delivered_record_bytes']}\t" + ",".join(f"{k}:{v}" for k, v in x["records_by_instrument_id"].items()))
(HERE / "file_table_zl_mbp1.tsv").write_text("\n".join(rows) + "\n")
print(open(HERE / "tab_daily.md").read()); print(open(HERE / "tab_action_seg.md").read()); print(open(HERE / "tab_bars.md").read()); print(open(HERE / "tab_bars_year.md").read())
