"""RV1: every number in reports/stage_e32b_ranking.md's tables against score32b_out.json (and econ32b.json, F4).
Prints mismatches per table. Tolerance: the printed precision of each cell."""
import json, re, math
B = '/home/kiros-li/Documents/GitHub/PropExperiment/reports'
md = open(f'{B}/stage_e32b_ranking.md').read().split('\n')
out = json.load(open(f'{B}/stage_e32b_briefs/score32b_out.json'))
econ = json.load(open(f'{B}/stage_e32b_briefs/econ32b.json'))
f4 = json.load(open(f'{B}/stage_e32b_briefs/F4_facts_unmasked.json'))
f3 = json.load(open(f'{B}/stage_e32b_briefs/F3_vol.json'))['roots']
P = out['primary']; L1 = P['layer1']; PR = {p['key']: p for p in P['pairs']}
FIRM = {'Bulenox': 'bulenox', 'Lucid': 'lucid', 'MFFU': 'mffu', 'Topstep': 'topstep', 'Tradeify': 'tradeify'}
bad = []


def table_after(heading_sub):
    """Rows (lists of cells) of the first markdown table after the line containing heading_sub."""
    i = next(k for k, l in enumerate(md) if heading_sub in l)
    while not md[i].startswith('|'):
        i += 1
    hdr = [c.strip() for c in md[i].strip('|').split('|')]
    rows = []
    i += 2
    while i < len(md) and md[i].startswith('|'):
        rows.append([c.strip() for c in md[i].strip('|').split('|')])
        i += 1
    return hdr, rows


def close(printed, value, tag):
    """Compare a printed number with a value at the printed precision (half-up or round-to-nearest both accepted)."""
    if printed in ('-', '', 'None'):
        return value is None
    m = re.match(r'^-?[\d,]*\.?\d*$', printed)
    if not m:
        return None
    p = float(printed.replace(',', ''))
    dec = len(printed.split('.')[1]) if '.' in printed else 0
    if value is None:
        bad.append((tag, printed, None)); return False
    v = float(value)
    ok = abs(p - v) <= 0.5 * 10 ** (-dec) + 1e-9
    if not ok:
        bad.append((tag, printed, v))
    return ok


# ---- 2a
hdr, rows = table_after('### 2a.')
n2a = 0
for r in rows:
    code = r[0]; row = L1[code]; n2a += 1
    if code == 'NQ':
        continue
    close(r[2].split()[0], row['S'], f'2a {code} S')
    close(r[3], row['c_RT'], f'2a {code} c_RT')
    for cell, h in zip(r[4:8], ('30', '60', '120', '240')):
        if cell == '-':
            assert row['disp'][h] is None, (code, h); continue
        sg, rr, bd = [x.strip() for x in cell.split('/')]
        close(sg, row['disp'][h], f'2a {code} sigma{h}'); close(rr, row['r'][h], f'2a {code} r{h}')
        close(bd, row['D1_bands'].get(h), f'2a {code} band{h}')
    for cell, h in zip(r[8:11], ('5', '15', 'OC')):
        close(cell, row['r'][h], f'2a {code} r_{h}')
    close(r[11], row['D1'], f'2a {code} D1')
print('2a rows', n2a)

# ---- 2b
hdr, rows = table_after('### 2b.')
for r in rows:
    code = r[0]; row = L1[code]
    if code == 'NQ':
        continue
    m = re.match(r'([\d.]+) \(a ([\d.]+), b ([\d.]+), c ([\d.]+), d ([\d.]+); facts of (\w+)\)', r[2])
    close(m.group(1), row['D2'], f'2b {code} D2')
    for g, k in zip(m.groups()[1:5], 'abcd'):
        close(g, row['D2_parts'][k], f'2b {code} D2.{k}')
    if m.group(6) != row['D2_parts']['facts_of']: bad.append((f'2b {code} facts_of', m.group(6), row['D2_parts']['facts_of']))
    m = re.match(r'([\d.]+) \((\d+)/(\d+)/(\d+)\)', r[3])
    close(m.group(1), row['D3'], f'2b {code} D3')
    for g, k in zip(m.groups()[1:], ('s1', 's2', 's3')):
        close(g, row['D3_parts'][k], f'2b {code} {k}')
    close(r[4], row['D4'], f'2b {code} D4')
    close(r[5].split()[0], row['D4_parts']['L'], f'2b {code} L')
    close(r[6].split()[0], row['D4_parts']['J'], f'2b {code} J')
    sat = int(re.search(r'Sat (\d)', r[7]).group(1))
    if sat != row['D4_parts']['Sat']: bad.append((f'2b {code} Sat', sat, row['D4_parts']['Sat']))
    m = re.match(r'([\d.]+) \(h (\d), k (\d), o (\d), p (\d)\)', r[8])
    close(m.group(1), row['D5'], f'2b {code} D5')
    for g, k in zip(m.groups()[1:], 'hkop'):
        close(g, row['D5_parts'][k], f'2b {code} D5.{k}')
    m = re.match(r'([\d.]+) \((\w+)\)', r[9])
    close(m.group(1), row['D6'], f'2b {code} D6')
    if m.group(2) != row['D6_parts']['evidence_of']: bad.append((f'2b {code} evidence_of', m.group(2), row['D6_parts']['evidence_of']))
    close(r[10], row['L1'], f'2b {code} L1')
    flag_lt2 = 'L1 < 2' in r[11] or '< 2.00' in r[11]
    if flag_lt2 != bool(row['L1_below_2']): bad.append((f'2b {code} flag', r[11], row['L1_below_2']))
    gate = r[12].strip().lower().startswith('pass')
    if gate != bool(row['gate_pass']): bad.append((f'2b {code} gate', r[12], row['gate_pass']))
print('2b rows', len(rows))

# ---- 2c
hdr, rows = table_after('### 2c.')
for r in rows:
    code = r[0]; row = L1[code]
    if code == 'NQ':
        continue
    res = r[2]
    if res.strip().lower().startswith('pass') != bool(row['gate_pass']): bad.append((f'2c {code} gate', res, row['gate_pass']))
    if r[3].strip() != str(row['gate_arithmetic']).strip() and not r[3].startswith(str(row['gate_arithmetic'])[:40]):
        bad.append((f'2c {code} arithmetic', r[3][:80], str(row['gate_arithmetic'])[:80]))
    # re-derive the arithmetic string numbers
    m = re.search(r'sigma_60 = ([\d.]+) ticks vs 2 x \(S \+ 0\.5\) = ([\d.]+) ticks', r[3])
    if m:
        close(m.group(1), row['disp']['60'], f'2c {code} sigma60'); close(m.group(2), 2 * row['c_RT'], f'2c {code} 2cRT')
print('2c rows', len(rows))

# ---- 3a
hdr, rows = table_after('### 3a.')
seen = set()
for r in rows:
    rank = int(r[0]); key = FIRM[r[1]] + '|' + r[2]; p = PR[key]; seen.add(key)
    if p['rank'] != rank: bad.append((f'3a {key} rank', rank, p['rank']))
    close(r[3], p['S'], f'3a {key} S'); close(r[4], p['S_rounded'], f'3a {key} S2dp')
    close(r[5], p['L1'], f'3a {key} L1'); close(r[6], p['L2'], f'3a {key} L2'); close(r[7], p['E'], f'3a {key} E')
    eb = econ['pairs'][key]['primary']; s60 = eb['sigma60']
    for cell, mu, mm, tag in ((r[8], eb['mu_star_mkt'], eb['m_star'], 'm*'), (r[9], eb['mu10K_mkt'], eb['m10K'], 'm10K')):
        if 'above cap' in cell or '>' in cell:
            if not (eb['above_cap']['mu_star'] if tag == 'm*' else eb['above_cap']['mu10K']): bad.append((f'3a {key} {tag} cap', cell))
            continue
        mt, ms = [x.strip() for x in cell.split('/')]
        close(mt.replace(' t', ''), mu, f'3a {key} {tag} ticks'); close(ms, mm, f'3a {key} {tag} sigma')
    close(r[10], s60, f'3a {key} sigma60')
    close(r[11], p['R'], f'3a {key} R'); close(r[12], p['A'], f'3a {key} A')
    m = re.match(r'([\d.]+) \(([\d.]+|-)/([\d.]+|-)\)', r[13])
    close(m.group(1), p['D'], f'3a {key} D'); close(m.group(2), p['room_a'], f'3a {key} room_a'); close(m.group(3), p['room_b'], f'3a {key} room_b')
    close(r[14].split()[0], p['Rel'], f'3a {key} Rel')
    ded = re.search(r'\((.*)\)', r[14]); dl = set(x.strip() for x in ded.group(1).split(',')) if ded else set()
    exp = {k.replace('rel_', '') for k, v in p['Rel_deductions'].items() if v}
    if dl - {'none', '-'} != exp: bad.append((f'3a {key} Rel deductions', dl, exp))
    close(r[15], p['P'], f'3a {key} P'); close(r[16], p['cost_per_attempt'], f'3a {key} cost'); close(r[17], p['fee_rt_usd'], f'3a {key} fee')
ranked = {k for k, p in PR.items() if p['status'] == 'ranked'}
if seen != ranked: bad.append(('3a coverage', len(seen), len(ranked)))
print('3a rows', len(rows))

# ---- 3c
hdr, rows = table_after('### 3c.')
seen = set()
for r in rows:
    key = FIRM[r[0]] + '|' + r[1]; p = PR[key]; seen.add(key)
    if r[2] != p['status']: bad.append((f'3c {key} status', r[2], p['status']))
    listed = f4['pairs'][key]['listed_50k']
    if ('not listed' in r[3]) == bool(listed): bad.append((f'3c {key} listed text', r[3][:60], listed))
    if p['status'] == 'Layer 1 gate':
        for g in L1[r[1]]['gate_reasons']:
            if g.split(' (')[0][:20] not in r[3]: bad.append((f'3c {key} reason', r[3][:80], g[:60]))
nr = {k for k, p in PR.items() if p['status'] != 'ranked'}
if seen != nr: bad.append(('3c coverage', len(seen), len(nr)))
print('3c rows', len(rows))

# ---- 4 (top 15 + deviations)
hdr, rows = table_after('## 4. The top 15')
rk = [p for p in P['pairs'] if p['status'] == 'ranked']
W1 = {'D1': 0.30, 'D2': 0.15, 'D3': 0.15, 'D4': 0.15, 'D5': 0.10, 'D6': 0.15}
W2 = {'E': 0.40, 'R': 0.15, 'A': 0.15, 'D': 0.15, 'Rel': 0.10, 'P': 0.05}
means = {}
for k in W1: means[k] = sum(L1[p['code']][k] for p in rk) / len(rk)
for k in W2: means[k] = sum(p[k] for p in rk) / len(rk)
means['S'] = sum(p['S'] for p in rk) / len(rk)
mtext = next(l for l in md if 'The ranked-pair means are' in l)
for k, v in means.items():
    m = re.search(rf'\b{k} ([\d.]+)', mtext)
    if m: close(m.group(1), v, f'4 mean {k}')
for r in rows:
    rank = int(r[0]); key = FIRM[r[1]] + '|' + r[2]; p = PR[key]
    if p['rank'] != rank: bad.append((f'4 {key} rank', rank, p['rank']))
    close(r[3], p['S'], f'4 {key} S'); close(r[4], p['L1'], f'4 {key} L1'); close(r[5], p['L2'], f'4 {key} L2')
    for cell, k in zip(r[6].split('/'), ('D1', 'D2', 'D3', 'D4', 'D5', 'D6')): close(cell, L1[p['code']][k], f'4 {key} {k}')
    for cell, k in zip(r[7].split('/'), ('E', 'R', 'A', 'D', 'Rel', 'P')): close(cell, p[k], f'4 {key} {k}')
    dev = {k: 0.5 * W1[k] * (L1[p['code']][k] - means[k]) for k in W1}
    dev.update({k: 0.5 * W2[k] * (p[k] - means[k]) for k in W2})
    gains = sorted([(k, v) for k, v in dev.items() if v > 0], key=lambda kv: -kv[1])[:3]
    losses = sorted([(k, v) for k, v in dev.items() if v < 0], key=lambda kv: kv[1])[:2]
    for cell, exp in ((r[8], gains), (r[9], losses)):
        got = re.findall(r'(\w+) ([+-][\d.]+)', cell)
        if [g[0] for g in got] != [e[0] for e in exp]: bad.append((f'4 {key} dev names', got, [(e[0], round(e[1], 3)) for e in exp]))
        for (gk, gv), (ek, ev) in zip(got, exp): close(gv, ev, f'4 {key} dev {gk}')
print('4 rows', len(rows))

# ---- 5 moves
hdr, rows = table_after('## 5. Moves')
mv = {(r['firm'], r['code']): r for r in out['moves_vs_e28']['rows']}
for r in rows:
    key = (FIRM[r[0]], r[1]); m = mv[key]
    if r[2] not in ('-', '') and str(m.get('rank_e28')) != r[2] and not (m.get('rank_e28') is None and not r[2].isdigit()): bad.append((f'5 {key} rank_e28', r[2], m.get('rank_e28')))
    if r[3].isdigit() and int(r[3]) != m.get('rank_here'): bad.append((f'5 {key} rank_here', r[3], m.get('rank_here')))
    if r[4].lstrip('+-').isdigit() and int(r[4]) != m.get('rank_change'): bad.append((f'5 {key} change', r[4], m.get('rank_change')))
    close(r[5], m.get('S_e28'), f'5 {key} S_e28'); close(r[6], m.get('S_here'), f'5 {key} S_here')
    for cell in (r[7], r[8]):
        for name, val in re.findall(r'([\w ()]+?) ([+-][\d.]+)', cell):
            name = name.strip()
            if name in m.get('contrib', {}): close(val, m['contrib'][name], f'5 {key} contrib {name}')
            else: bad.append((f'5 {key} contrib name', name))
if len(rows) != len(mv): bad.append(('5 coverage', len(rows), len(mv)))
print('5 rows', len(rows))

# ---- 6 variants
hdr, rows = table_after('## 6. Variants')
V = out['variants']
for r in rows:
    name = r[0]; v = V[name]
    tops = re.findall(r'(\d) (\w+) (\w+) ([\d.]+)', r[2])
    for (rk_, fm, cd, s), t in zip(tops, v['top5']):
        if int(rk_) != t['rank'] or FIRM[fm] != t['firm'] or cd != t['code']: bad.append((f'6 {name} top5', (rk_, fm, cd), (t['rank'], t['firm'], t['code'])))
        close(s, t['S'], f'6 {name} S {cd}')
    for fm, rkk in re.findall(r'(Bul|Luc|MFF|Top|Tra) (\d+|Layer 1 gate)', r[6]):
        firm = {'Bul': 'bulenox', 'Luc': 'lucid', 'MFF': 'mffu', 'Top': 'topstep', 'Tra': 'tradeify'}[fm]
        if str(v['MNQ_ranks'][firm]) != rkk: bad.append((f'6 {name} MNQ {firm}', rkk, v['MNQ_ranks'][firm]))
    if int(r[7]) != v['n_ranked']: bad.append((f'6 {name} n_ranked', r[7], v['n_ranked']))
    if int(r[8]) != len(v['layer1_survivors']): bad.append((f'6 {name} survivors', r[8], len(v['layer1_survivors'])))
    prim = [(t['firm'], t['code']) for t in P['top15'][:5]]; this = [(t['firm'], t['code']) for t in v['top5']]
    kind = 'identical' if this == prim else ('order only' if set(this) == set(prim) else 'SET CHANGES')
    if kind not in r[3]: bad.append((f'6 {name} kind', r[3], kind))
if len(rows) != len(V): bad.append(('6 coverage', len(rows), len(V)))
print('6 rows', len(rows))

# ---- 7 sat1 ranks table against my recomputation
try:
    mine = json.load(open(f'{B}/stage_e32b_briefs/work/rv1/recomp_sat1.json'))['ranked']
    mr = {(p['firm'], p['code']): (p['rank'], float(p['S'])) for p in mine}
    hdr, rows = table_after('| code | sat1 ranks')
    for r in rows:
        code = r[0]
        for fm, rk_, s in re.findall(r'(\w+) (\d+) \(([\d.]+)\)', r[1]):
            got = mr.get((FIRM[fm], code))
            if got is None or got[0] != int(rk_): bad.append((f'7 sat1 {fm} {code} rank', rk_, got))
            elif not close(s, got[1], f'7 sat1 {fm} {code} S'): pass
    print('7 sat1 rows', len(rows))
except Exception as e:
    print('sat1 table check skipped:', e)

print('TOTAL mismatches:', len(bad))
for b in bad[:60]:
    print('  ', b)
