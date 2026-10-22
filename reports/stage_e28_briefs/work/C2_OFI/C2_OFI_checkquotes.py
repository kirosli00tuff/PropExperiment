import re, sys
P = 'pages/C2_OFI/'
def norm(s):
    s = s.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')
    s = re.sub(r'-\s*\n\s*', '-', s)
    return re.sub(r'\s+', ' ', s).strip().lower()
rows = [l for l in open('C2_OFI.md').read().split('## 16. Evidence table')[1].splitlines() if l.startswith('| ') and not l.startswith('| Claim') and not l.startswith('|---')]
bad = 0
for l in rows:
    cells = [c.strip() for c in l.strip('|').split('|')]
    quote, f = cells[2], cells[3]
    try:
        txt = open(P + f, errors='ignore').read()
    except Exception:
        txt = open(P + f.replace('.txt', '.html.txt'), errors='ignore').read()
    if f.endswith('.html'):
        txt = re.sub(r'<[^>]+>', ' ', txt)
    nt = norm(txt); nt2 = norm(re.sub(r'-\s*\n\s*', '', txt))
    parts = [p for p in re.split(r'"\s*;\s*"|\.\.\.', quote.strip('"')) ]
    ok = all((norm(p.strip(' "')) in nt) or (norm(p.strip(' "')) in nt2) for p in parts if len(p.strip(' "')) > 3)
    if not ok:
        bad += 1; print('MISS:', cells[0][:50], '|', quote[:90])
print('rows', len(rows), 'missing', bad)
