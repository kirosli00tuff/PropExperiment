"""Flatten Bulenox CMS help_items JSON to 'key: text' lines (English only). Usage: in out"""
import json, sys, re, html
d = json.load(open(sys.argv[1]))
out = []
def strip(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s or ''))).strip()
def walk(x, acc):
    if isinstance(x, dict):
        for v in x.values(): walk(v, acc)
    elif isinstance(x, list):
        for v in x: walk(v, acc)
    elif isinstance(x, str):
        t = strip(x)
        if t: acc.append(t)
for it in d['data']:
    for tr in it.get('translations', []):
        if not str(tr.get('languages_code', '')).startswith('en'):
            continue
        acc = []
        walk({k: v for k, v in tr.items() if k != 'languages_code'}, acc)
        for t in acc:
            out.append(f"{it.get('key')}: {t}")
open(sys.argv[2], 'w').write('\n'.join(out) + '\n')
print(len(out))
