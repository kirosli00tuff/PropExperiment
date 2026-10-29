import json, sys
d = json.load(open('/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/F4_masked_firms.json'))
fk = sys.argv[1]
f = d['firms'][fk]
print('FIRM', fk, '| modelled_plan:', f['modelled_plan'])
print('lookup_date:', json.dumps(f['lookup_date'], ensure_ascii=False))
for lk in ['A_facts', 'R_facts_firm_wide', 'Rel_facts', 'plan_facts', 'payout_context']:
    print('\n####', lk, len(f.get(lk) or []))
    for it in f.get(lk) or []:
        print('--', it['id'], '|', it.get('what'), '| date:', it.get('date'), '| ver:', it.get('verified'), ('| binds: ' + str(it.get('binds'))) if 'binds' in it else '')
        for x in ['value', 'quote', 'note', 'old_value_e28', 'changed_since_e28']:
            if it.get(x) not in (None, ''):
                print('   ' + x + ':', it[x])
