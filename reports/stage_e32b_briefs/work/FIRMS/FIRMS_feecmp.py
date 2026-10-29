"""Compare a firm's fee table (text file, 'Name (CODE)|$x.xx' pairs) to E.28 A3_firm_products fee_rt_usd.
Usage: FIRMS_feecmp.py firm textfile startline endline"""
import json, re, sys
firm, path, a, b = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
lines = open(path).read().splitlines()[a-1:b]
fees = {}
cur = None
for ln in lines:
    m = re.search(r'\(([A-Z0-9]{2,4})\)', ln)
    if m: cur = m.group(1); continue
    m2 = re.match(r'^\$?([0-9]+\.[0-9]+)$', ln.strip())
    if m2 and cur:
        fees[cur] = float(m2.group(1)); cur = None
d = json.load(open('/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/A3_firm_products.json'))
old = {r['code']: (r['listed_50k']['value'], r['fee_rt_usd']['value']) for r in d['pairs'] if r['firm'] == firm}
for code, (lst, f) in old.items():
    new = fees.get(code)
    flag = '' if (new is None and lst != 'yes') or (new is not None and f is not None and abs(new - f) < 1e-9) else ' <-- DIFF'
    print(f'{code}: listed={lst} e28_fee={f} now={new}{flag}')
print('codes in page not in 47:', sorted(set(fees) - set(old)))
