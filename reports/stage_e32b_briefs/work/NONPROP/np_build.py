import json,re,hashlib,subprocess
B='/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/'
P=B+'pages/NONPROP/'
codes="MCL QM CL MNG QG NG MGC GC SIL SI MHG HG M6E 6E M6A 6A MET ETH MBT BTC M2K RTY MYM YM MNQ NQ 2YY 5YY 10Y 30Y ZT ZF ZN ZB MZC MZS MZW MZL MZM XC XK XW ZC ZS ZW ZL ZM".split()
fam={}
for f,l in {'crude':'MCL QM CL','natgas':'MNG QG NG','metals':'MGC GC SIL SI MHG HG','fx':'M6E 6E M6A 6A','crypto':'MET ETH MBT BTC','equity':'M2K RTY MYM YM MNQ NQ','rates':'2YY 5YY 10Y 30Y ZT ZF ZN ZB','grains':'MZC MZS MZW MZL MZM XC XK XW ZC ZS ZW ZL ZM'}.items():
    for c in l.split(): fam[c]=f
# exchange-fee page rows: (file, exchange, row-key text found in .tbl.txt, fee, IBKR product-group, mapping note)
def rows(f): return [l.rstrip('\n') for l in open(P+f)]
R={'CME':rows('ibkrca_fees_CME.tbl.txt'),'CBOT':rows('ibkrca_fees_CBOT.tbl.txt'),'NYMEX':rows('ibkrca_fees_NYMEX.tbl.txt'),'COMEX':rows('ibkrca_fees_COMEX.tbl.txt')}
def find(ex,key):
    for r in R[ex]:
        if r.startswith(key): return r
    raise KeyError((ex,key))
def fee_of(ex,row):
    parts=row.split(' || ')
    if ex=='CME': v=parts[2]
    elif ex=='CBOT': v=parts[1].replace('USD ','')
    elif ex=='NYMEX': v=parts[1].replace('USD ','')
    else: v=parts[1].replace('USD ','')
    return float(re.match(r'[0-9.]+',v).group(0))
M={ # code -> (exchange, row key, mapping note)
'MCL':('NYMEX','MCL ||',''),'QM':('NYMEX','QM ||',''),'CL':('NYMEX','CL, HO, RB',''),
'MNG':('NYMEX','MHNG ||','IBKR fee row is MHNG; margin page shows underlying MHNG trading class MNG'),'QG':('NYMEX','QG ||',''),'NG':('NYMEX','NG ||',''),
'SIL':('COMEX','',''),'MGC':('COMEX','MGC ||',''),'GC':('COMEX','GC, HG, SI',''),'SI':('COMEX','GC, HG, SI',''),'HG':('COMEX','GC, HG, SI',''),'MHG':('COMEX','MHG ||',''),
'M6E':('CME','E-micro Forex Futures',''),'M6A':('CME','E-micro Forex Futures',''),
'6E':('CME','Forex Futures^[9]','IBKR lists FX futures by currency code (EUR); margin page maps 6E to underlying EUR'),'6A':('CME','Forex Futures^[9]','IBKR lists FX futures by currency code (AUD); margin page maps 6A to underlying AUD'),
'MET':('CME','Micro Ether Futures /',''),'ETH':('CME','Ethereum Cryptocurrency Futures /',''),
'MBT':('CME','Bitcoin Micro Futures /','fee row symbol is "BRR - Micro"; margin page shows MBT under MICRO BITCOIN; mapping is an inference'),'BTC':('CME','Bitcoin Futures /','fee row symbols BRR, BTCEURRR; margin page maps BTC to underlying BRR'),
'M2K':('CME','Micro E-Mini Futures Products',''),'MNQ':('CME','Micro E-Mini Futures Products',''),'MYM':('CBOT','Micro E-Mini Futures / MYM',''),
'RTY':('CME','E-mini Equity Futures',''),'NQ':('CME','E-mini Equity Futures','NQ excluded (V49), fact only'),'YM':('CBOT','Mini-sized Dow',''),
'2YY':('CBOT','Micro Treasury Futures',''),'5YY':('CBOT','Micro Treasury Futures',''),'10Y':('CBOT','Micro Treasury Futures',''),'30Y':('CBOT','Micro Treasury Futures',''),
'ZT':('CBOT','U.S. Treasury Futures / ZT',''),'ZF':('CBOT','U.S. Treasury Futures / ZF',''),'ZN':('CBOT','U.S. Treasury Futures / ZN, TN',''),'ZB':('CBOT','U.S. Treasury Futures / ZB, TWE',''),
'MZC':('CBOT','Micro Ags-Electronic Futures',''),'MZS':('CBOT','Micro Ags-Electronic Futures',''),'MZW':('CBOT','Micro Ags-Electronic Futures',''),'MZL':('CBOT','Micro Ags-Electronic Futures',''),'MZM':('CBOT','Micro Ags-Electronic Futures',''),
'XC':('CBOT','Agricultural mini-sized','fee row symbols YC, YK, YW (IBKR); margin page maps XC to YC'),'XK':('CBOT','Agricultural mini-sized','fee row symbols YC, YK, YW; margin maps XK to YK'),'XW':('CBOT','Agricultural mini-sized','fee row symbols YC, YK, YW; margin maps XW to YW'),
'ZC':('CBOT','Ags-Electronic Futures',''),'ZS':('CBOT','Ags-Electronic Futures',''),'ZW':('CBOT','Ags-Electronic Futures',''),'ZL':('CBOT','Ags-Electronic Futures',''),'ZM':('CBOT','Ags-Electronic Futures',''),
}
REG={'CME':(0.011,'ibkrca_fees_CME.tbl.txt: "All Products || USD || 0.011" (Regulatory Fee Recovery Charge, Non-Members & IIP)'),
'CBOT':(0.01,'ibkrca_fees_CBOT.tbl.txt: "All || USD 0.01 || USD 0.00" (Tier I & V, Non-Members & IIP)'),
'NYMEX':(0.01,'ibkrca_fees_NYMEX.tbl.txt: "All || USD 0.01 || USD 0.01 || USD 0.00" (Tier I)'),
'COMEX':(0.01,'ibkrca_fees_COMEX.tbl.txt: "All || USD 0.01" (regulatory fee table, Non-Member)')}
EXEC=0.85
mrg=json.load(open(B+'work/NONPROP/margin_ca_raw.json'))
def mrow(c):
    rs=mrg[c]
    if c in('SI','SIL'): rs=[r for r in rs if r[3]==c]
    r=[x for x in rs if x[3]==c] or rs
    return r[0]
out={}
for c in codes:
    ex,key,note=M[c]
    unpub=False
    if c=='SIL': unpub=True
    entry={'family':fam[c]}
    if unpub:
        entry['fee']={'status':'not published','note':'ibkrca_fees_COMEX.tbl.txt lists ALI, GC/HG/SI, SGU/SGC, HRC, MGC, QO/QI/QC, UX, MHG, 1OZ, SIC; no SIL row (the 1,000 oz silver future). Not guessed.','all_in_usd_per_side':None}
    else:
        row=find(ex,key); e=fee_of(ex,row); reg,regsrc=REG[ex]
        entry['fee']={'status':'published','exchange_page':f'ibkrca_fees_{ex}.html (tbl: ibkrca_fees_{ex}.tbl.txt)','exchange_fee_row_quote':row,'exchange_fee_usd_non_member_tier1':e,'ibkr_execution_usd':EXEC,'clearing_usd':0.00,'regulatory_usd':reg,'regulatory_source':regsrc,
         'all_in_usd_per_side':round(EXEC+e+0.0+reg,4),'sum_formula':f'{EXEC} + {e} + 0.00 + {reg}','mapping_note':note}
    r=mrow(c)
    entry['margin_usd_per_contract']={'ibkr_underlying':r[1],'trading_class':r[3],'description':r[2],'intraday_initial':r[4],'intraday_maintenance':r[5],'overnight_initial':r[6],'overnight_maintenance':r[7],'currency':r[8],'short_overnight_initial':r[10],'short_overnight_maintenance':r[11],
       'source':'ibkrca_margin_fut_ca_us.tbl.txt (resident Canada, trading US)','row_quote':' || '.join(r)}
    out[c]=entry
json.dump(out,open(B+'work/NONPROP/products.json','w'),indent=1)
bad=[c for c in codes if out[c]['fee'].get('all_in_usd_per_side') is None]
print(len(out),'codes; unpublished fee:',bad)
for c in codes: 
    f=out[c]['fee']; m=out[c]['margin_usd_per_contract']
    print(c,f.get('all_in_usd_per_side'),m['intraday_initial'],m['overnight_initial'])
