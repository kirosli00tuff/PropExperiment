import json
R='reports/stage_e32b_briefs/'
d=json.load(open(R+'F2_grains.json'))
I={i['id']:i for i in d['items']}
U=[("Corn",["ZC","XC","MZC"]),("Soybeans",["ZS","XK","MZS"]),("Wheat (Chicago SRW)",["ZW","XW","MZW"]),("Soybean oil",["ZL","MZL"]),("Soybean meal",["ZM","MZM"])]
L=[]
L.append("# F2 grains: family reader facts (Stage E.32b, step F2)")
L.append("")
L.append(f"Worker {d['worker']}; started {d['started_pdt']}, finished {d['finished_pdt']}. WebSearch calls {d['websearch_calls']} of 80; T6 full-text reads {d['fulltext_reads_t6']} of 12. Items {len(d['items'])} in F2_grains.json (ids GRAINS-n). Facts only, no scores. Pages and log: pages/GRAINS/ (log.tsv). Reused E.28 facts cite reports/stage_e28_briefs/A1_grains.json by index and field.")
L.append("")
L.append("Shared sources not read here: CFTC automated-trading reports (F2_shared_cftc_automation.json, RatesReader) and Baltussen et al. 2021 (F2_shared_baltussen.json, EquityReader). E.28's CFTC figures for ZC/ZS/ZW remain in A1_grains.json hft_automated_share.")
L.append("")
L.append("## Per code")
L.append("")
L.append("| Code | Leader | Spread (ticks; item) | Touch (item) | Settlement (item) |")
L.append("|---|---|---|---|---|")
for c in ["ZC","XC","MZC","ZS","XK","MZS","ZW","XW","MZW","ZL","MZL","ZM","MZM"]:
    p=d['per_code'][c]
    sp = f"{p['median_spread_ticks']} (mean; {p['spread_item']})" if p['median_spread_ticks'] is not None else "not found"
    tc = f"{p['touch_item']}" if p['touch_size'] else "not found"
    L.append(f"| {c} | {p['leader']} | {sp} | {tc} | {p['settlement_basis']} ({p['settlement_item']}) |")
L.append("")
L.append("No MEDIAN spread or touch size was found for any code; every figure is a mean. Notes per code:")
L.append("")
for c,p in d['per_code'].items():
    L.append(f"- {c}: {p['notes']}")
L.append("")
def line(i):
    it=I[i]; v=it['value']; v=json.dumps(v) if not isinstance(v,str) else v
    flags=[it['verified']]+(['pointer'] if it['pointer'] else [])+(['negative'] if it['negative'] else [])
    return f"- {i} [{it['topic']}, {', '.join(flags)}; codes {','.join(it['codes'])}]: {v}. Window: {it['window']}."
L.append("## Facts by topic (one line each; detail, quote and source in the JSON)")
for t,title in [("T1","T1 Spread and touch"),("T2a","T2a Automated share"),("T2b","T2b Market-maker and incentive programs"),("T2c","T2c Retail share"),("T3","T3 Structural relationships"),("T4","T4 Scheduled events and absorption"),("T5","T5 Settlement and price discovery"),("T6","T6 Intraday directional evidence"),("T7","T7 Session structure and handoffs"),("F1","F1 Changed E.28 facts")]:
    L.append(""); L.append(f"### {title}"); L.append("")
    xs=[i for i in I if I[i]['topic']==t]
    if not xs: L.append("- None recorded from new sources (see searched-not-found).")
    for i in xs: L.append(line(i))
    if t=="T2a": L.append("- E.28 reuse (not re-fetched; CFTC source owned by RatesReader): A1_grains.json [0..4].hft_automated_share; Grain and Oilseed group ATS share 39.0% (2012-14) and 49.0% (2014-16).")
    if t=="T2c": L.append("- No retail share found. E.28: Haynes-Roberts 'small traders' share is not a retail share (A1_grains.json retail_share).")
L.append("")
L.append("## Key readings for the lead (facts, not ratings)")
L.append("")
L.append("- D2 b: E.28 found no current program; CFTC filings show the CBOT Grain & Oilseed Futures ETH Market Maker Program (ZC, ZS, ZM, ZL, ZW outrights, overnight session) in force from 2017 through at least 2024-07-31, and a deferred-month market-maker program through at least 2025-07-31 (GRAINS-30, -32, F1 GRAINS-31). Minis and micros are not named.")
L.append("- D3 s1: the soybean crush has peer-reviewed full-text evidence of intraday cointegration at 1-minute sampling in the day session (180 of 243 days, 2015), much weaker overnight (52 days) (GRAINS-15, -16). No half-life or trading test is reported. Corn nearby/deferred calendar intraday cointegration about 70% of days (GRAINS-46, working paper). Corn-soy-wheat only weekly (GRAINS-47).")
L.append("- D3 s2: conflicting. Anderson, McKenzie, Noyes 2024 (NCCC-134 working paper, full text, 2010-2021) find the WASDE soybean reaction grows from 30 min to the close; corn mostly done by 30 min (GRAINS-18). Lehecka et al. 2014 (abstract) and Joseph-Garcia (full text) find about 10 min / 5-6 min and no under- or overreaction; Adjemian-Irwin 2018 (abstract) is volatility-only (GRAINS-19 to -21).")
L.append("- D3 s3: settlement period 13:14-13:15 CT verified for ZC, ZS, ZW (GRAINS-28); daily pause 07:45-08:30 CT (GRAINS-14, -29); U-shaped day-session volatility (volatility-only, GRAINS-36); pre-2012 settlement-window reversals declined after the rule change (GRAINS-17).")
L.append("- D4 Sat (ii): micros are financially settled to the full-size settlement (GRAINS-8). Minis are physically delivered, but their daily and final settlement price is derived directly from the full-size settlement (GRAINS-27); this changes E.28's plain 'physical delivery' reading.")
L.append("- D6: no CBOT-grain product-level study of intraday directional predictability found. Other venue: DCE soybean and soybean meal first-half-hour momentum (full text, in sample, gross, 2002-2013 and 2008-2013; GRAINS-25); DCE overreaction to US overnight moves stopped working after night trading (abstract, negative; GRAINS-42). The program's own ZM search is negative net of costs but explicitly not a proof of absence (GRAINS-49).")
L.append("")
L.append("## Searched, not found")
L.append("")
for s in d['searched_not_found']:
    L.append(f"- {s['topic']} ({','.join(s['codes'])}): {s['note']} Queries: {'; '.join(s['queries'])}.")
L.append("")
L.append("## Gaps")
L.append("")
for g in d['gaps']: L.append(f"- {g}")
L.append("")
L.append("## Notices")
L.append("")
L.append("- " + ("; ".join(n['time_pdt']+' '+n['text'] for n in d['notices']) if d['notices'] else "No WebSearch budget notice was received."))
open(R+'F2_grains.md','w').write('\n'.join(L)+'\n')
print(len(L))
