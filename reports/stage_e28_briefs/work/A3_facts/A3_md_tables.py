"""A3 helper: append generated fact tables to A3_facts.md."""
import json, sys
sys.path.insert(0, '.')
from A3_common import BR, CANDIDATES, FIRMS, load
f = load('A3_facts.json')['candidates']; fp = load('A3_firm_products.json')
def v(c, k, nd=3):
    x = c[k]['value']
    return '-' if x is None else (f'{x:.{nd}g}' if isinstance(x, float) else str(x))
L = ['', '### 8a. Layer 1 facts per candidate (primary; "u" = unknown default)', '',
     '| Code | Tick | Tick USD | sigma_1m | R_d | QV or r | ADV | ADV source | Gate 60 | C4 rel / wknd / limit / 4SD | Flags |',
     '|---|---|---|---|---|---|---|---|---|---|---|']
for code in CANDIDATES:
    c = f[code]
    q = c['QV_or_r']; qs = '-' if q['value'] is None else (('r ' if 'proxy' in q['flags'] else 'QV ') + f"{q['value']:.3g}")
    adv = c['ADV']; src = 'A0 v_0' if 'OC2_owned_v0_front' in adv['flags'] else ('A1 ' + str(adv.get('window')) if adv['value'] is not None else 'u')
    c4 = ' / '.join({True: 'T', False: 'F', 'unknown': 'u'}[x['value']] + ('*' if 'ambiguous' in x['flags'] else '') for x in c['C4'].values())
    fl = sorted(set(x for k in ('sigma_1m', 'R_d') for x in c[k]['flags']))
    L.append(f"| {code} | {v(c,'tick_size')} | {v(c,'tick_value')} | {v(c,'sigma_1m')} | {v(c,'R_d')} | {qs} | {'-' if c['ADV']['value'] is None else format(c['ADV']['value'], ',.0f')} | {src} | "
             f"{v(c,'gate_60_dates')} | {c4} | {', '.join(fl)} |")
L += ['', '(* = reader-flagged judgment, counted as holding in the C4_conservative variant.)', '',
      '### 8b. Listing and round-trip fees per firm (USD; ticks in brackets; "no" = not listed for 50K)', '',
      '| Code | ' + ' | '.join(FIRMS) + ' |', '|---|' + '---|' * len(FIRMS)]
idx = {(p['firm'], p['code']): p for p in fp['pairs']}
for code in CANDIDATES:
    cells = []
    for firm in FIRMS:
        p = idx[(firm, code)]
        if p['listed_50k']['value'] != 'yes':
            cells.append(p['listed_50k']['value'])
        else:
            fee = p['fee_rt_usd']['value']; t = p['fee_rt_ticks']['value']
            cells.append('fee u' if fee is None else f'{fee:.2f} ({t:.2f})' + (f"; {p['product_cap']}" if p['product_cap'] else ''))
    L.append(f'| {code} | ' + ' | '.join(cells) + ' |')
L.append('')
L.append('Listed pairs per firm: ' + ', '.join(f"{firm} {sum(1 for p in fp['pairs'] if p['firm']==firm and p['listed_50k']['value']=='yes')}" for firm in FIRMS)
         + f". Total {sum(1 for p in fp['pairs'] if p['listed_50k']['value']=='yes')}.")
md = open(f'{BR}/A3_facts.md').read()
head = md.split('## 8. Generated tables')[0] + '## 8. Generated tables\n'
open(f'{BR}/A3_facts.md', 'w').write(head + '\n'.join(L) + '\n')
print(L[-1])
