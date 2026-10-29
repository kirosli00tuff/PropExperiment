"""Print E.28 firm JSON leaf values compactly (skip products). Usage: FIRMS_dump.py firm [section...]"""
import json, sys
firm = sys.argv[1]
secs = sys.argv[2:]
d = json.load(open(f'/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/A2_firm_{firm}.json'))
def leaf(v):
    if isinstance(v, dict) and 'value' in v:
        return f"{str(v.get('value'))[:160]} | src={str(v.get('source_file') or '').split('/')[-1]}"
    return None
def walk(x, p):
    l = leaf(x)
    if l is not None:
        print(p, '=', l); return
    if isinstance(x, dict):
        for k, v in x.items():
            walk(v, p + '.' + k)
    elif isinstance(x, list):
        for i, v in enumerate(x):
            if isinstance(v,(dict,list)): walk(v, f'{p}[{i}]')
            else: print(f'{p}[{i}] = {str(v)[:160]}')
    else:
        print(p, '=', str(x)[:160])
for k, v in d.items():
    if k in ('products', 'e19_diff'): continue
    if secs and k not in secs: continue
    walk(v, k)
