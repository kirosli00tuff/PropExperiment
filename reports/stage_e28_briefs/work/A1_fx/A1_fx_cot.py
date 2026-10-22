# TFF (Traders in Financial Futures, futures-only) shares for Euro FX and AUD, report dates 2022-11-01..2023-10-31 only.
import csv, statistics as st
codes = {'099741': '6E Euro FX', '232741': '6A Australian Dollar'}
cats = ['Dealer', 'Asset_Mgr', 'Lev_Money', 'Other_Rept', 'NonRept']
rows = {c: [] for c in codes}
for f in ['cot/y2022/FinFutYY.txt', 'cot/y2023/FinFutYY.txt']:
    for r in csv.DictReader(open(f, encoding='latin-1')):
        d = r['Report_Date_as_YYYY-MM-DD'][:10]
        if r['CFTC_Contract_Market_Code'] in codes and '2022-11-01' <= d <= '2023-10-31':
            rows[r['CFTC_Contract_Market_Code']].append(r)
for c, rs in rows.items():
    print(codes[c], 'n_reports', len(rs), 'dates', min(x['Report_Date_as_YYYY-MM-DD'][:10] for x in rs), max(x['Report_Date_as_YYYY-MM-DD'][:10] for x in rs))
    oi = [float(x['Open_Interest_All']) for x in rs]
    print('  OI mean %.0f median %.0f min %.0f max %.0f' % (st.mean(oi), st.median(oi), min(oi), max(oi)))
    for k in cats:
        if k == 'NonRept':
            L, S, Sp = 'NonRept_Positions_Long_All', 'NonRept_Positions_Short_All', None
        else:
            L, S, Sp = k + '_Positions_Long_All', k + '_Positions_Short_All', k + '_Positions_Spread_All'
        sh = []
        for x in rs:
            tot = float(x[L]) + float(x[S]) + (2 * float(x[Sp]) if Sp and Sp in x and x[Sp].strip() else 0)
            sh.append(100 * tot / (2 * float(x['Open_Interest_All'])))
        print('  %-10s share of gross OI (long+short+2*spread)/(2*OI): mean %.1f%% min %.1f max %.1f' % (k, st.mean(sh), min(sh), max(sh)))
    tr = [k for k in rs[0] if k.startswith('Traders_Tot_All')]
    if tr:
        t = [float(x[tr[0]]) for x in rs]
        print('  total reportable traders mean %.0f' % st.mean(t))
