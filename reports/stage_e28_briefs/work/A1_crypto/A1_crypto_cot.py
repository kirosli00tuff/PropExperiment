import csv, sys, statistics as st, glob
W='/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/work/A1_crypto/cot'
rows=[]
for y in ['2022','2023','2025','2026']:
    with open(f'{W}/{y}/FinFutYY.txt',newline='') as f:
        for r in csv.DictReader(f):
            r={k.strip():v for k,v in r.items()}
            n=r['Market_and_Exchange_Names'].upper()
            if 'BITCOIN' in n or 'ETHER' in n: rows.append(r)
names=sorted({(r['Market_and_Exchange_Names'].strip(),r['CFTC_Contract_Market_Code'].strip()) for r in rows})
print('MARKETS:'); [print(' ',n) for n in names]
wins={'W1_2022-11-01..2023-10-31':('2022-11-01','2023-10-31'),'W2_2025-10-21..2026-10-20':('2025-10-21','2026-10-20')}
cats=[('Dealer','Dealer_Positions'),('AssetMgr','Asset_Mgr_Positions'),('LevMoney','Lev_Money_Positions'),('OtherRept','Other_Rept_Positions')]
def f(x):
    try: return float(x)
    except: return 0.0
for wn,(a,b) in wins.items():
    print('\n==',wn)
    for name,code in names:
        sel=[r for r in rows if r['CFTC_Contract_Market_Code'].strip()==code and a<=r['Report_Date_as_YYYY-MM-DD'].strip()<=b]
        if not sel: continue
        oi=[f(r['Open_Interest_All']) for r in sel]
        sh={c:[] for c,_ in cats}; sh['NonRept']=[]
        tr=[f(r.get('Traders_Tot_All','0')) for r in sel]
        for r in sel:
            O=f(r['Open_Interest_All'])
            if O<=0: continue
            for c,p in cats:
                sh[c].append((f(r[p+'_Long_All'])+f(r[p+'_Short_All'])+2*f(r[p+'_Spread_All']))/(2*O))
            sh['NonRept'].append((f(r['NonRept_Positions_Long_All'])+f(r['NonRept_Positions_Short_All']))/(2*O))
        print(f"{code} {name[:45]} n={len(sel)} dates={min(r['Report_Date_as_YYYY-MM-DD'] for r in sel)}..{max(r['Report_Date_as_YYYY-MM-DD'] for r in sel)} OI mean={st.mean(oi):.0f} median={st.median(oi):.0f} min={min(oi):.0f} max={max(oi):.0f} traders_mean={st.mean(tr):.1f}")
        print('   '+' '.join(f"{c}={100*st.mean(v):.1f}%" for c,v in sh.items())+f"  NonRept range={100*min(sh['NonRept']):.1f}-{100*max(sh['NonRept']):.1f}%")
