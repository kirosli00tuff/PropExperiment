import json,collections
from datetime import datetime
def p(s):
    s=s.replace('Z','')
    if 'T' not in s: s+='T00:00:00'
    return datetime.fromisoformat(s)
def span(dt):
    a,b=dt.split('..'); return (p(b)-p(a)).total_seconds()/86400
rows=collections.defaultdict(lambda: collections.defaultdict(set))
for l in open('ledger/databento_spend.jsonl'):
    d=json.loads(l)
    if d['event']!='quote' or d['schema'] not in('mbo','mbp-1','tbbo','mbp-10'): continue
    try: q=round(float(d['quoted_usd']),6)
    except: continue
    rows[(d['symbol'],d['schema'])][d['date']].add(q)
for k in [('ZM.v.0,ZM.v.1','mbo'),('ZS.v.0','mbp-1'),('ZL.v.0','mbp-1')]:
    r=rows[k]; print(k,'distinct ranges',len(r),'ranges with >1 distinct usd:',sum(1 for v in r.values() if len(v)>1))
    sp=collections.Counter(round(span(d)) for d in r); print(' span days hist',dict(sorted(sp.items())))
    ds=sorted(r)
    print(' first3',[(d,sorted(r[d])) for d in ds[:3]]); print(' last3',[(d,sorted(r[d])) for d in ds[-3:]])
