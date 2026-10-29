import json, sys
# usage: show.py LIST LABELS(comma or ALL) FIELDS(comma) [trunc]
lst = sys.argv[1]; labs = sys.argv[2]; fields = sys.argv[3].split(','); tr = int(sys.argv[4]) if len(sys.argv) > 4 else 400
d = json.load(open('/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/F4_masked_contracts.json'))['contracts']
keys = list(d) if labs == 'ALL' else labs.split(',')
AB = {'a same-underlying sibling': 'SIB', 'the asset class broadly or a multi-asset study': 'BROAD', 'the product group': 'GROUP',
      'this contract': 'THIS', 'another venue of the same underlying': 'OTHVEN', 'a close cousin (same asset class on CME Globex)': 'COUSIN'}
VB = {"reused from an earlier stage's full-text fact (level as stated in the text)": 'REUSED-FT', 'snippet [unverified]': 'SNIP',
      'full text': 'FT', 'abstract [unverified]': 'ABS', 'abstract [unverified] (reused from an earlier stage)': 'ABS-RE'}
for k in keys:
    items = d[k].get(lst) or []
    note = d[k].get(lst + '_note')
    print('##', k, len(items), ('NOTE: ' + note) if note else '')
    for it in items:
        head = [it['id'], AB.get(it['applies_to'], it['applies_to']), VB.get(it['verified'], it['verified'])]
        if it.get('pointer_only'): head.append('PTR')
        if it.get('negative_finding'): head.append('NEG')
        if lst.startswith('D6'):
            head.append('a10=%s oos=%s net=%s hz=%s' % (it.get('after_2010'), it.get('out_of_sample'), it.get('net_of_costs'), it.get('horizon')))
        out = ' '.join(str(h) for h in head)
        for f in fields:
            s = str(it.get(f) or '')
            if len(s) > tr: s = s[:tr] + '..'
            out += ' | ' + f[0].upper() + ': ' + s
        print(out)
