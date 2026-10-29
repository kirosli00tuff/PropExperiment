import json,collections,re,sys
# Prints summaries only: per (root,schema) quote counts, sum quoted_usd, distinct date ranges.
rows=collections.defaultdict(list)
for l in open('ledger/databento_spend.jsonl'):
    d=json.loads(l)
    if d['event']!='quote': continue
    sym=d['symbol']; sch=d['schema']
    rows[(sym,sch)].append((d['date'],d['quoted_usd'],d['billable_bytes'],d.get('request','')))
out={}
for (sym,sch),v in sorted(rows.items()):
    tot=0;n=0;bad=0
    for dt,q,b,r in v:
        try: tot+=float(q); n+=1
        except: bad+=1
    ds=sorted(set(x[0] for x in v))
    print(f"{sym:14s} {sch:10s} n={len(v):5d} bad={bad} usd={tot:10.4f} ranges={len(ds)} first={ds[0]} last={ds[-1]}")
