"""A1_natgas: CFTC disaggregated futures-only COT shares for NYMEX natural gas codes.
Rows with report date >= 2023-11-01 are dropped before any field is used (pilot window kept clean)."""
import csv, sys, statistics as st
D = sys.argv[1]
CODES = {'023651': 'NG (NAT GAS NYME)', '03565B': 'HENRY HUB 2,500 MMBtu (HH look-alike)', '023A55': 'HENRY HUB LAST DAY FIN (NN)'}
LO, HI = '2022-11-01', '2023-10-31'
rows = {c: [] for c in CODES}
for y in ('2022', '2023'):
    for r in csv.DictReader(open(f'{D}/cot_unzip_{y}/f_year.txt')):
        d = r['Report_Date_as_YYYY-MM-DD']
        if d >= '2023-11-01' or d < LO: continue
        c = r['CFTC_Contract_Market_Code'].strip()
        if c in rows: rows[c].append(r)
def f(r, k): return float(r[k])
for c, rs in rows.items():
    if not rs: continue
    out = {}
    for lab, keys in {
        'prod_merc_long': ['Prod_Merc_Positions_Long_All'], 'prod_merc_short': ['Prod_Merc_Positions_Short_All'],
        'swap_long': ['Swap_Positions_Long_All', 'Swap__Positions_Spread_All'], 'swap_short': ['Swap__Positions_Short_All', 'Swap__Positions_Spread_All'],
        'mm_long': ['M_Money_Positions_Long_All', 'M_Money_Positions_Spread_All'], 'mm_short': ['M_Money_Positions_Short_All', 'M_Money_Positions_Spread_All'],
        'other_long': ['Other_Rept_Positions_Long_All', 'Other_Rept_Positions_Spread_All'], 'other_short': ['Other_Rept_Positions_Short_All', 'Other_Rept_Positions_Spread_All'],
        'nonrep_long': ['NonRept_Positions_Long_All'], 'nonrep_short': ['NonRept_Positions_Short_All']}.items():
        out[lab] = st.mean(100 * sum(f(r, k) for k in keys) / f(r, 'Open_Interest_All') for r in rs)
    oi = [f(r, 'Open_Interest_All') for r in rs]
    tr = [f(r, 'Traders_Tot_All') for r in rs] if 'Traders_Tot_All' in rs[0] else []
    trpm = [f(r, 'Traders_Prod_Merc_Long_All') + f(r, 'Traders_Prod_Merc_Short_All') for r in rs] if 'Traders_Prod_Merc_Long_All' in rs[0] else []
    print(f"{c} {CODES[c]} weeks={len(rs)} first={min(r['Report_Date_as_YYYY-MM-DD'] for r in rs)} last={max(r['Report_Date_as_YYYY-MM-DD'] for r in rs)}")
    print('  OI mean=%.0f median=%.0f min=%.0f max=%.0f' % (st.mean(oi), st.median(oi), min(oi), max(oi)))
    if tr: print('  total reportable traders mean=%.0f' % st.mean(tr))
    if trpm: print('  prod/merc trader count (long+short) mean=%.0f' % st.mean(trpm))
    print('  mean % of OI: ' + ', '.join(f'{k}={v:.1f}' for k, v in out.items()))
    pm = (out['prod_merc_long'] + out['prod_merc_short']) / 2; nr = (out['nonrep_long'] + out['nonrep_short']) / 2
    print(f'  avg(long,short) producer/merchant={pm:.1f}  nonreportable={nr:.1f}')
