import json, re
d = json.load(open('/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/F4_masked_firms.json'))
out = json.load(open('/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/F4_blind_ratings_masked.json'))
bad = 0
fid = {fk: {it['id'] for l in f.values() if isinstance(l, list) for it in l} for fk, f in d['firms'].items()}
for fk, crits in out['firms'].items():
    for c, R in crits.items():
        for i in re.findall(r'I-\d{7}', R['reason']):
            if i not in fid[fk]: print('BAD firm id', fk, c, i); bad += 1
for pk, crits in out['pairs'].items():
    f = pk.split('|')[0]
    pid = {it['id'] for it in d['pairs'][pk]['R_facts']} | fid[f]
    for c, R in crits.items():
        for i in re.findall(r'I-\d{7}', R['reason']):
            if i not in pid: print('BAD pair id', pk, c, i); bad += 1
missing = [pk for pk in d['pairs'] if set(out['pairs'].get(pk, {})) != {'R', 'A'}]
missf = [fk for fk in d['firms'] if set(out['firms'].get(fk, {})) != {'rel_age', 'rel_payout', 'rel_rules', 'rel_regulatory'}]
print('pairs', len(out['pairs']), 'firms', len(out['firms']), 'codes', len(out['codes']), 'bad ids', bad, 'missing pairs', len(missing), 'missing firms', len(missf))
