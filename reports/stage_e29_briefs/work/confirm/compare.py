"""Compare grid-confirmed thresholds (work/confirm/out + work/review/out confirm/alone) with the bisection values in
work/basket/cells; write reports/stage_e29_briefs/E29_confirmation.md. Also the section 7 'vanish' table (R_review
SHOULD FIX 8) on the confirmed values."""
import json
from pathlib import Path

ROOT = Path('reports/stage_e29_briefs/work')
conf = {}
for d in (ROOT / 'review' / 'out', ROOT / 'confirm' / 'out'):
    for p in d.glob('*.json'):
        tag, cid = p.stem.split('__', 1)
        if tag in ('confirm', 'alone'):
            conf[cid] = json.loads(p.read_text())
def val(x):
    return x.get('value') if isinstance(x, dict) else x
rows, moved, n = [], [], 0
vals = {}
for p in sorted((ROOT / 'basket' / 'cells').glob('*.json')):
    cid = p.stem
    a = json.loads(p.read_text())
    c = conf.get(cid)
    if cid.startswith('alone__'):
        pairs = [('lim', val(a['limit']['mu_star']), c and val(c['limit']['mu_star'])),
                 ('mkt', val(a['market']['mu_star']), c and val(c['market']['mu_star']))]
    else:
        pairs = [('thr', val(a.get('threshold')), c and val(c.get('threshold'))),
                 ('x10K', val(a.get('x10K')), c and val(c.get('x10K')))]
    for name, b, k in pairs:
        if c is None:
            rows.append((cid, name, b, 'NOT CONFIRMED')); continue
        n += 1
        if b != k:
            moved.append((cid, name, b, k))
    if c is not None and not cid.startswith('alone__'):
        vals[cid] = (val(c.get('threshold')), val(c.get('x10K')))
out = [f"# Stage E.29 grid confirmation (A3_econ.md 2.4) of every threshold (R_review.md SHOULD FIX 7)\n",
       f"Confirmed records: {len(conf)} of {len(list((ROOT / 'basket' / 'cells').glob('*.json')))}; thresholds compared: {n}; "
       f"moved: {len(moved)}; not confirmed: {len(rows)}.\n"]
out += ["| cell | quantity | bisection | confirmed |", "|---|---|---|---|"]
out += [f"| {a} | {b} | {c} | {d} |" for a, b, c, d in moved] or ["| (none) | | | |"]
if rows:
    out += ["", "Not confirmed:"] + [f"- {a} {b}" for a, b, c, d in rows]
# vanish table (declaration section 7), limit primary, on confirmed values
def num(x):
    return float(x) if isinstance(x, (int, float)) else float('inf')
out += ["", "## Section 7: rho at which the benefit vanishes (limit case, confirmed values)", "",
        "| firm | basket | setting | beats B0 at rho | vanishes at |", "|---|---|---|---|---|"]
for f in ('topstep', 'lucid', 'tradeify', 'mffu', 'bulenox'):
    for s in ('i', 'ii'):
        t0, x0 = vals[f'limit__primary__{f}__B0__{s}__rNA']
        for b in ('B1', 'B2', 'B3', 'B4'):
            beats = []
            for r in ('0.00', '0.25', '0.50', '0.75'):
                v = vals.get(f'limit__primary__{f}__{b}__{s}__r{r}')
                if v is None or v[0] is None:
                    beats.append(None); continue
                beats.append(num(v[0]) < num(t0) - 0.01 - 1e-9 and num(v[1]) <= num(x0))
            if all(x is None for x in beats):
                txt = 'n/a'
            elif not any(beats):
                txt = 'never beats B0'
            elif all(beats):
                txt = 'not on the grid (beats B0 at every rho up to 0.75)'
            elif beats[0]:
                txt = f"vanishes at rho {['0','0.25','0.5','0.75'][beats.index(False)]}"
            else:
                txt = f"appears at rho {['0','0.25','0.5','0.75'][beats.index(True)]} (absent at rho 0; grows with rho)"
            out.append(f"| {f} | {b} | {s} | {' '.join(['-' if x is None else ('yes' if x else 'no') for x in beats])} | {txt} |")
Path('reports/stage_e29_briefs/E29_confirmation.md').write_text('\n'.join(out) + '\n')
print(f"confirmed {len(conf)}, compared {n}, moved {len(moved)}, not confirmed {len(rows)}")
