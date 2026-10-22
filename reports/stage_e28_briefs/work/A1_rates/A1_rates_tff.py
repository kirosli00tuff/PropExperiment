import json,sys,statistics as st
names={'042601':'ZT','044601':'ZF','043602':'ZN','020601':'ZB','04360Y':'10Y'}
out={}
for win,fn in [('2022-11..2023-10','cftc_tff_rates_2022-11_2023-10.json'),('latest','cftc_tff_rates_latest.json')]:
    d=json.load(open('pages/A1_rates/'+fn))
    for code,nm in names.items():
        rows=[r for r in d if r['cftc_contract_market_code']==code]
        if not rows: out[(nm,win)]=None; continue
        dates=sorted(r['report_date_as_yyyy_mm_dd'][:10] for r in rows)
        f=lambda k: st.mean(float(r.get(k,0) or 0) for r in rows)
        res={'n_reports':len(rows),'first':dates[0],'last':dates[-1],'mean_oi':round(f('open_interest_all')),
             'mean_traders_tot':round(f('traders_tot_all'),1)}
        for cat,(l,s) in {'dealer':('pct_of_oi_dealer_long_all','pct_of_oi_dealer_short_all'),
             'asset_mgr':('pct_of_oi_asset_mgr_long','pct_of_oi_asset_mgr_short'),
             'lev_money':('pct_of_oi_lev_money_long','pct_of_oi_lev_money_short'),
             'other_rept':('pct_of_oi_other_rept_long','pct_of_oi_other_rept_short'),
             'nonrept':('pct_of_oi_nonrept_long_all','pct_of_oi_nonrept_short_all')}.items():
            res[cat+'_pct_long']=round(f(l),1); res[cat+'_pct_short']=round(f(s),1)
        out[(nm,win)]=res
for k,v in out.items(): print(k, json.dumps(v))
json.dump({f'{k[0]}|{k[1]}':v for k,v in out.items()},open('work/A1_rates/A1_rates_tff_summary.json','w'),indent=1)
