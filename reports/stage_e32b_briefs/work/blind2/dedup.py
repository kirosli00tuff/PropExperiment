import json, sys
# usage: dedup.py LIST [fields] [trunc] [labels]
lst = sys.argv[1]
fields = sys.argv[2].split(',') if len(sys.argv) > 2 else ['field', 'value', 'window', 'detail', 'quote']
tr = int(sys.argv[3]) if len(sys.argv) > 3 else 100000
labs = sys.argv[4].split(',') if len(sys.argv) > 4 else None
d = json.load(open('/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/F4_masked_contracts.json'))['contracts']
AB = {'a same-underlying sibling': 'SIB', 'the asset class broadly or a multi-asset study': 'BROAD', 'the product group': 'GROUP',
      'this contract': 'THIS', 'another venue of the same underlying': 'OTHVEN', 'a close cousin (same asset class on CME Globex)': 'COUSIN'}
VB = {"reused from an earlier stage's full-text fact (level as stated in the text)": 'REUSED-FT', 'snippet [unverified]': 'SNIP',
      'full text': 'FT', 'abstract [unverified]': 'ABS', 'abstract [unverified] (reused from an earlier stage)': 'ABS-RE'}
groups = {}
order = []
for k, c in d.items():
    if labs and k not in labs: continue
    for it in (c.get(lst) or []):
        key = tuple(str(it.get(f) or '') for f in ['field', 'value', 'window', 'detail', 'quote'])
        if key not in groups:
            groups[key] = []; order.append(key)
        tag = '%s:%s:%s' % (k, it['id'], AB.get(it['applies_to'], it['applies_to']))
        groups[key].append((tag, VB.get(it['verified'], it['verified']), it.get('pointer_only'), it.get('negative_finding'),
                            (it.get('after_2010'), it.get('out_of_sample'), it.get('net_of_costs'), it.get('horizon'), it.get('flags_note'))))
print('unique', len(order))
for n, key in enumerate(order):
    g = groups[key]
    vs = sorted(set(x[1] for x in g)); ptr = any(x[2] for x in g); neg = any(x[3] for x in g)
    print('=== U%d' % n, 'verified=' + '/'.join(vs), 'PTR' if ptr else '', 'NEG' if neg else '')
    if lst.startswith('D6'):
        fl = sorted(set(str(x[4]) for x in g)); print('  flags:', ' ;; '.join(fl)[:400])
    print('  in:', ' '.join(x[0] for x in g))
    fm = dict(zip(['field', 'value', 'window', 'detail', 'quote'], key))
    for f in fields:
        s = fm[f]
        if len(s) > tr: s = s[:tr] + '..'
        print('  ' + f + ':', s)
