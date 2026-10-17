import json, sys
S='/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e22_briefs/datasrc_pages/_scripts'
out='/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e22_briefs/ibkr_margins.json'
a=json.load(open(S+'/m_ibkr_margin_fut_us.json'))
log=[l.rstrip('\n').split('\t') for l in open(S+'/../fetch_log.tsv')]
L={r[0]:r for r in log}
micros=['MNQ','M2K','MGC','MCL','MNG','M6E','2YY','10Y','30Y','MZC','MZS','MZL','SIL','MHG','M6A','M6B','MCD','MJY','MZW','MZM','MES']
full=['NQ','RTY','GC','CL','NG','6E','ZT','ZN','ZB','ZC','ZS','ZL']
US_EXCH={'CBOT','CME','COMEX','NYMEX'}
rates={}; nf=[]
for k in micros+full:
    rows=[x for x in a.get(k,[]) if x['row'][0] in US_EXCH and x['row'][8]=='USD']
    if len(rows)!=1: nf.append(k); continue
    r=rows[0]['row']; h=rows[0]['hdr']
    rates[k]={'initial':float(r[6]),'maintenance':float(r[7]),
      'intraday_initial': None if r[4]=='N/A' else float(r[4]),
      'intraday_maintenance': None if r[5]=='N/A' else float(r[5]),
      'short_overnight_initial': float(r[10]),'short_overnight_maintenance': float(r[11]),
      'exchange':r[0],'underlying':r[1],'description':r[2],'trading_class':r[3],
      'is_micro': k in micros,
      'quote':' | '.join(r)}
n1=L['N001']; n2=L['N002']
doc={'source_url':n1[1],'fetched_utc':n1[2],'saved_file':'reports/stage_e22_briefs/datasrc_pages/'+n1[4],'sha256':n1[5],
 'currency':'USD',
 'columns_on_page':'Exchange | Underlying | Product description | Trading Class | Intraday Initial 1 | Intraday Maintenance 1 | Overnight Initial | Overnight Maintenance | Currency | Has Options | Short Overnight Initial | Short Overnight Maintenance',
 'field_mapping':'initial = Overnight Initial; maintenance = Overnight Maintenance (long side). Intraday and short-overnight columns kept as extra fields. Keyed by Trading Class (6E full-size has underlying EUR; MNG has underlying MHNG; SIL has underlying SI).',
 'page_scope':'US website, US Futures and FOPs Margin Requirements, page text: "For residents of the United States trading futures and FOPs: Risk-based margin". Page shows no as-of date; text says requirements "can change frequently".',
 'cross_check':{'source_url':n2[1],'fetched_utc':n2[2],'saved_file':'reports/stage_e22_briefs/datasrc_pages/'+n2[4],'sha256':n2[5],
   'result':'Interactive Brokers Canada page (hm=ca, ex=us) parsed the same way: every target row identical to the US page at fetch time.'},
 'notes':['SIL row is labelled "SILVER INDEX" on the page (underlying SI, trading class SIL); its overnight initial 12161.55 is exactly 1/5 of the SI row 60807.73 on the same page, consistent with the 1,000 oz micro vs 5,000 oz standard (ratio computed here, not stated on the page).',
          'Only rows on CBOT/CME/COMEX/NYMEX in USD were taken; same-class rows on other exchanges (KSE CL, LMEOTC ZS) ignored.'],
 'rates':rates,'not_found':nf}
json.dump(doc,open(out,'w'),indent=1)
print(len(rates), nf)
