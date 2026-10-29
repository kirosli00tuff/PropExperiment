import json, sys, re
d = json.load(open('/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/F4_masked_firms.json'))
fk = sys.argv[1]
groups = {}; order = []
for pk, p in d['pairs'].items():
    f, c = pk.split('|')
    if f != fk: continue
    # normalise: replace the contract label in rule text so identical templates group together
    facts = []
    for it in p['R_facts']:
        facts.append((it['what'], it['rule'].replace(c, '<C>'), str(it.get('binds'))))
    key = (p['listed_on_modelled_plan'], tuple(facts))
    if key not in groups: groups[key] = []; order.append(key)
    groups[key].append((c, [it['id'] for it in p['R_facts']]))
print('firm', fk, 'unique R_fact templates', len(order))
for n, key in enumerate(order):
    print('\n=== T%d listed=%s  contracts(%d): %s' % (n, key[0], len(groups[key]), ' '.join(c for c, _ in groups[key])))
    for what, rule, binds in key[1]:
        print('  -', what, '| binds:', binds); print('    rule:', rule)
