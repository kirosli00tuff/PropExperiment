"""Lead: compact per-firm tables for the return from E29_cells.json (limit case, primary form).
Cell text: threshold / mu10K analogue; '*' = beats B0 by the declaration's section 7 rule (threshold lower than B0's
by more than 0.01 and mu10K analogue not higher)."""
import json
d = json.load(open('reports/stage_e29_briefs/E29_cells.json'))
cells = [c for c in d['cells'] if c['case'] == 'limit' and c['form'] == 'primary']
def v(x):
    x = x.get('value') if isinstance(x, dict) else x
    return x
def num(x):
    return float(x) if isinstance(x, (int, float)) else float('inf')
out = []
for firm in ('topstep', 'lucid', 'tradeify', 'mffu', 'bulenox'):
    out.append(f"\n**{firm}** (setting (i): k* in units of each member's alone break-even; setting (ii): mu*_QM in ticks)\n")
    out.append("| basket | setting | B0 | rho 0 | rho 0.25 | rho 0.5 | rho 0.75 |")
    out.append("|---|---|---|---|---|---|---|")
    for s in ('i', 'ii'):
        b0 = [c for c in cells if c['firm'] == firm and c['basket'] == 'B0' and c['setting'] == s][0]
        t0, x0 = v(b0['threshold']), v(b0['x10K'])
        for b in ('B1', 'B2', 'B3', 'B4'):
            row = [b, s, f"{t0} / {x0}"]
            for r in (0.0, 0.25, 0.5, 0.75):
                cc = [c for c in cells if c['firm'] == firm and c['basket'] == b and c['setting'] == s and c['rho'] == r]
                if not cc or 'threshold' not in cc[0]:
                    row.append('n/a'); continue
                t, x = v(cc[0]['threshold']), v(cc[0]['x10K'])
                beats = num(t) < num(t0) - 0.01 - 1e-9 and num(x) <= num(x0)
                row.append(f"{t} / {x}{' *' if beats else ''}")
            out.append('| ' + ' | '.join(str(z) for z in row) + ' |')
print('\n'.join(out))
