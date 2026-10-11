"""E.20 lead tool: per-feature availability matrix from the 17 product_<ROOT>.json files (Part A item 2).
Prints, per frozen covered signal, each root's 2010-2019 / 2019-2024 status (y, n, p=partial, u=undetermined).
Reads reader JSONs and reports/stage_e12_gate0_list.json (covered signal names only)."""
import json, glob, re, sys
cov = json.load(open('reports/stage_e12_gate0_list.json'))['covered_signals']
names = sorted(set(cov) | {'g17_mes', 'k8_flight_ret', 'k8_flight_tail'}, key=lambda s: cov.index(s) if s in cov else 999)
S = {'yes': 'y', 'no': 'n', 'partial': 'p', 'undetermined': 'u'}
mat = {n: {} for n in names}
for f in sorted(glob.glob('reports/stage_e20_briefs/product_*.json')):
    d = json.load(open(f)); r = d['root']
    for a in d.get('availability', []):
        feat = a.get('feature', '')
        hits = [n for n in names if re.search(r'(?<![a-z0-9_])' + re.escape(n) + r'(?![a-z0-9_])', feat)]
        # expand shorthand like "g17_nq/zn/6e" and "cp1/cp2"
        if not hits:
            m = re.match(r'(g17_)([a-z0-9]+(?:\s*/\s*[a-z0-9]+)+)', feat)
            if m: hits = ['g17_' + x.strip() for x in m.group(2).split('/') if 'g17_' + x.strip() in names]
        for n in hits:
            mat[n][r] = S.get(a.get('exists_2010_2019'), '?') + S.get(a.get('exists_2019_2024'), '?')
roots = ["NQ","RTY","ZT","ZF","ZN","TN","ZB","UB","6E","CL","NG","GC","ZC","ZS","ZL","HE","LE"]
print('feature'.ljust(20), ' '.join(r.rjust(3) for r in roots))
for n in names:
    print(n.ljust(20), ' '.join(mat[n].get(r, '.').rjust(3) for r in roots))
