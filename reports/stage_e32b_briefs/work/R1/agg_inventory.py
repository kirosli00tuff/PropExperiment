"""R1 helper: aggregate E.23 inventory rows by member (merging roots). Prints/writes compact fields only."""
import json, glob, re, collections, sys
OUT = 'reports/stage_e32b_briefs/work/R1/members.json'
members = collections.OrderedDict()
for f in sorted(glob.glob('reports/stage_e23_briefs/inventory/*.json')):
    d = json.load(open(f))
    for r in d['rows']:
        mid = r.get('member_id') or r['trigger_id']
        key = (d['assignment'], mid)
        m = members.setdefault(key, dict(file=f, cluster=r['cluster_or_stage'], member_id=mid, roots=[], tiers=set(),
             side_kind=r.get('side_kind'), decision=r.get('decision_time_ct'), hold=r.get('intraday_hold'),
             windows=set(), verdicts=set(), trigger_ids=[]))
        m['roots'].append(r.get('traded_root'))
        m['trigger_ids'].append(r['trigger_id'])
        m['tiers'].add(str(r.get('tier')))
        for s in r.get('stages_read', []):
            m['windows'].add((s.get('stage'), s.get('purpose'), (s.get('window_dates') or '')[:140]))
        for v in r.get('verdicts', []):
            m['verdicts'].add(v[:160])
out = []
for (a, mid), m in members.items():
    m['tiers'] = sorted(m['tiers']); m['windows'] = sorted(m['windows']); m['verdicts'] = sorted(m['verdicts'])
    m['n_rows'] = len(m['roots']); m['roots'] = sorted(set(map(str, m['roots'])))
    m['assignment'] = a
    out.append(m)
json.dump(out, open(OUT, 'w'), indent=1)
print(len(out), 'members;', sum(m['n_rows'] for m in out), 'rows')
for m in out:
    print(m['assignment'], m['member_id'], m['n_rows'], ','.join(m['roots']), m['side_kind'] and m['side_kind'][:20], m['tiers'])
