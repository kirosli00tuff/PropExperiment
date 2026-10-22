# Summarise CFTC COT disaggregated (futures only) for crude markets, report dates 2022-11-01..2023-10-31.
import csv, sys, statistics as st
P='/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/pages/A1_crude/'
rows=[]
for f in ('cot22/f_year.txt','cot23/f_year.txt'):
    with open(P+f, newline='') as fh:
        for r in csv.DictReader(fh): rows.append(r)
k=lambda r: r['Market_and_Exchange_Names']
dk=[c for c in rows[0] if 'YYYY-MM-DD' in c][0]
names=sorted({(k(r),r['CFTC_Contract_Market_Code']) for r in rows if ('CRUDE' in k(r) or 'WTI' in k(r)) and 'NEW YORK MERCANTILE' in k(r)})
if sys.argv[1:]==['names']:
    for n in names: print(n)
    sys.exit()
codes=sys.argv[1:]
for code in codes:
    sel=[r for r in rows if r['CFTC_Contract_Market_Code'].strip()==code and '2022-11-01'<=r[dk]<='2023-10-31']
    if not sel: print(code,'none'); continue
    num=lambda r,c: float(r[c])
    def share(r, cols):  # (long+short[+2*spread]) / (2*OI)
        return sum(num(r,c) for c in cols)/(2*num(r,'Open_Interest_All'))
    pm=[share(r,['Prod_Merc_Positions_Long_All','Prod_Merc_Positions_Short_All']) for r in sel]
    sw=[share(r,['Swap_Positions_Long_All','Swap__Positions_Short_All'])+num(r,'Swap__Positions_Spread_All')/num(r,'Open_Interest_All') for r in sel]
    mm=[share(r,['M_Money_Positions_Long_All','M_Money_Positions_Short_All'])+num(r,'M_Money_Positions_Spread_All')/num(r,'Open_Interest_All') for r in sel]
    nr=[share(r,['NonRept_Positions_Long_All','NonRept_Positions_Short_All']) for r in sel]
    oi=[num(r,'Open_Interest_All') for r in sel]
    tr=[float(r.get('Traders_Tot_All') or 'nan') for r in sel]
    print(f"{code} {k(sel[0])} n_reports={len(sel)} dates={min(r[dk] for r in sel)}..{max(r[dk] for r in sel)}")
    print(f"  mean shares of OI (long+short)/2: prod_merc={st.mean(pm):.3f} swap={st.mean(sw):.3f} managed_money={st.mean(mm):.3f} nonreportable={st.mean(nr):.3f} (min {min(nr):.3f} max {max(nr):.3f})")
    print(f"  OI mean={st.mean(oi):.0f} median={st.median(oi):.0f}; total traders mean={st.mean(tr):.0f}")
