import sys, json, re
from html.parser import HTMLParser
class P(HTMLParser):
    def __init__(s): super().__init__(); s.rows=[]; s.row=None; s.cell=None
    def handle_starttag(s,t,a):
        if t=='tr': s.row=[]
        elif t in('td','th') and s.row is not None: s.cell=[]
    def handle_endtag(s,t):
        if t in('td','th') and s.cell is not None and s.row is not None:
            s.row.append(re.sub(r'\s+',' ',''.join(s.cell)).strip()); s.cell=None
        elif t=='tr' and s.row is not None:
            s.rows.append(s.row); s.row=None
    def handle_data(s,d):
        if s.cell is not None: s.cell.append(d)
p=P(); p.feed(open(sys.argv[1],encoding='utf-8',errors='replace').read())
want=sys.argv[2].split(',')
hdr=None; out={}
for r in p.rows:
    if r and r[0].startswith('Exchange'): hdr=r; continue
    if len(r)>=8 and (r[3] in want or r[1] in want):
        out.setdefault(r[3],[]).append({'hdr':hdr,'row':r})
print(json.dumps(out,indent=0))
