import sys, html, re
from html.parser import HTMLParser
class P(HTMLParser):
    def __init__(s):
        super().__init__(); s.out=[]; s.skip=0; s.on=False
    def handle_starttag(s,t,a):
        if t in ('script','style'): s.skip+=1
        if t in ('p','br','div','li','h1','h2','h3','h4','tr','pre'): s.out.append('\n')
    def handle_endtag(s,t):
        if t in ('script','style') and s.skip: s.skip-=1
    def handle_data(s,d):
        if not s.skip: s.out.append(d)
src=open(sys.argv[1],encoding='utf-8',errors='replace').read()
m=re.search(r"<div class='post-body entry-content'[^>]*>(.*?)<div class='post-footer'",src,re.S)
body=m.group(1) if m else src
p=P(); p.feed(body)
txt=re.sub(r'\n\s*\n+','\n\n',''.join(p.out))
open(sys.argv[2],'w').write(txt)
print(len(txt))
