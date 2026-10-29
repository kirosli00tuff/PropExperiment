import json, re
d = json.load(open('/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/F4_masked_contracts.json'))['contracts']
out = json.load(open('/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/F4_blind_ratings_masked.json'))
crit_list = {'D2a': 'D2a_automated_share', 'D2b': 'D2b_programs', 's1': 'D3_s1_relationships', 's2': 'D3_s2_scheduled_releases',
             's3': 'D3_s3_session_structure', 'sat_iii': 'Sat_iii_price_discovery', 'D6': 'D6_directional_evidence'}
bad = 0; wrong_list = 0; missing = 0
for k, c in d.items():
    ids_all = {it['id'] for l in c.values() if isinstance(l, list) for it in l}
    for crit, lst in crit_list.items():
        R = out['codes'].get(k, {}).get(crit)
        if R is None: print('MISSING', k, crit); missing += 1; continue
        ids_list = {it['id'] for it in (c.get(lst) or [])}
        for i in re.findall(r'I-\d{7}', R['reason']):
            if i not in ids_all: print('BADID', k, crit, i); bad += 1
            elif i not in ids_list: print('OTHERLIST', k, crit, i); wrong_list += 1
print('contracts', len(out['codes']), 'missing', missing, 'bad ids', bad, 'ids from another list', wrong_list)
