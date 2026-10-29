import sys,re,html
from html.parser import HTMLParser
class P(HTMLParser):
    def __init__(s):
        super().__init__(); s.rows=[]; s.cur=None; s.cell=None; s.skip=0
    def handle_starttag(s,t,a):
        if t in('script','style'): s.skip+=1
        if t=='tr': s.cur=[]
        if t in('td','th') and s.cur is not None: s.cell=[]
        if t=='sup' and s.cell is not None: s.cell.append('^[')
        if t=='br' and s.cell is not None: s.cell.append(' / ')
    def handle_endtag(s,t):
        if t in('script','style'): s.skip-=1
        if t=='sup' and s.cell is not None: s.cell.append(']')
        if t in('td','th') and s.cell is not None and s.cur is not None:
            s.cur.append(re.sub(r'\s+',' ',''.join(s.cell)).strip()); s.cell=None
        if t=='tr' and s.cur is not None:
            if any(s.cur): s.rows.append(s.cur)
            s.cur=None
    def handle_data(s,d):
        if s.cell is not None and not s.skip: s.cell.append(d)
f=sys.argv[1]
p=P(); p.feed(open(f,errors='ignore').read())
for r in p.rows: print(' || '.join(r))
