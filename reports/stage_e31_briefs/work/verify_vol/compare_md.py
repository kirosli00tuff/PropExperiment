import json, re
mine = json.load(open('verify_numbers.json'))
txt = open('../../../stage_e31_volume.md').read().splitlines()
sect = None; n = 0; bad = []
for ln in txt:
    m = re.match(r'^## (QM|ZM) by quarter, (primary|own) universe', ln)
    if m: sect = (m.group(1), m.group(2)); continue
    if ln.startswith('## '): sect = None
    if sect and ln.startswith('| 20'):
        c = [x.strip() for x in ln.strip('|').split('|')]
        q = c[0].split(' ')[0]
        r = next(x for x in mine['quarters'][sect[0]] if x['quarter'] == q)
        s = sect[1]
        exp = [str(r[f'days_{s}']), f"{r[f'median_{s}']:,.1f}", f"{r[f'p10_{s}']:,.1f}",
               f"{r['front_share']:.3f}", f"{r['top_share_info']:.3f}"]
        n += 1
        if c[1:] != exp: bad.append((sect, q, c[1:], exp))
        if 'partial' in c[0]: print('partial label', sect, c[0])
print('md rows checked', n, 'mismatch', len(bad))
for b in bad[:5]: print(b)
