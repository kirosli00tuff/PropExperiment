import json,sys
o=json.load(open(sys.argv[1]))
pp=o['productPrices']
p=o['plans']
def cell(sp,sz='s50k'):
    c=sp.get('cells',{}).get(sz)
    if sp.get('pricesFromWoo') and c is not None:
        if isinstance(c,dict): return {k:(v,pp.get(str(v))) for k,v in c.items()}
        return (c,pp.get(str(c)))
    return c
for pt in p['planTypes']:
    print('=== ',pt['id'],pt['label'],'order',pt['order'],'enabled',pt['enabled'])
    print(' sizes',[ (s['id'],s.get('discountPct')) for s in pt['sizes']])
    for sp in pt['front']:
        print('  F',sp['id'],'|',sp.get('label'),'|',cell(sp))
    f=pt.get('funded')
    if f:
        print(' -- funded',f.get('titleSuffix'))
        for sp in f['specs']: print('  D',sp['id'],'|',sp.get('label'),'|',cell(sp))
    for k in ('meta','addon','priceModes','catalogAxisPins'):
        if pt.get(k): print(' ',k,json.dumps(pt[k])[:400])
print('addonFees',json.dumps(o.get('addonFees'))[:600])
print('addonPromos',json.dumps(o.get('addonPromos'))[:400])
print('global',json.dumps(p['global'])[:1000])
