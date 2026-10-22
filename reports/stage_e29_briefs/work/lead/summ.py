"""Lead's compact summary of E29_cells.json (limit case, primary form): threshold and x10K per firm x basket x rho x setting."""
import json, sys
d = json.load(open('reports/stage_e29_briefs/E29_cells.json'))
cells = [c for c in d['cells'] if c['case'] == 'limit' and c['form'] == 'primary']
def v(x): return x['value'] if isinstance(x, dict) else x
key = lambda c: (c['firm'], c['basket'], c['setting'], c['rho'] if c['rho'] is not None else -1)
for firm in ('topstep', 'lucid', 'tradeify', 'mffu', 'bulenox'):
    for s in ('i', 'ii'):
        row = []
        for c in sorted([c for c in cells if c['firm'] == firm and c['setting'] == s], key=key):
            r = '-' if c['rho'] is None else f"{c['rho']:.2f}"[1:]
            row.append(f"{c['basket']}{r}:{v(c.get('threshold','n/a'))}/{v(c.get('x10K','n/a'))}")
        print(firm, s, ' '.join(row))
c = cells[0]; print('reporting sample', json.dumps(c['reporting'])[:600])
print('S sample', [(c['basket'], c['rho'], round(c['S_usd'],1), round(c['S_over_MLL'],3)) for c in cells if c['firm']=='topstep' and c['setting']=='ii'][:20])
