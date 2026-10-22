import sys, re, html
from html.parser import HTMLParser
class P(HTMLParser):
    def __init__(s): super().__init__(); s.out=[]; s.skip=0
    def handle_starttag(s,t,a):
        if t in ('script','style','noscript'): s.skip+=1
        if t in ('br','p','div','tr','li','h1','h2','h3','h4','td','th','dt','dd'): s.out.append('\n')
    def handle_endtag(s,t):
        if t in ('script','style','noscript') and s.skip: s.skip-=1
    def handle_data(s,d):
        if not s.skip: s.out.append(d)
for f in sys.argv[1:]:
    p=P(); p.feed(open(f,encoding='utf-8',errors='replace').read())
    t=re.sub(r'[ \t\r\f\v]+',' ','' .join(p.out)); t=re.sub(r'\n\s*\n+','\n',t)
    open(f+'.txt','w').write(t); print(f, len(t.splitlines()))
