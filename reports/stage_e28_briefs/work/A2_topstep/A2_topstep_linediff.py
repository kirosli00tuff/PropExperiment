"""A2_topstep: sentence-set diff of an E.19 page text against today's text.

Both texts are joined into one string (drop table pipes, collapse spaces, remove space before punctuation),
cut to the article body (after 'Table of contents', before 'Related Articles'), split into sentences, and the
sentences present in only one version are printed ('-' E.19 only, '+' today only).
"""
import re, sys
def body(p):
    t=open(p,encoding='utf-8',errors='replace').read()
    t=re.sub(r'^DATEMODIFIED:.*\n','',t)
    t=t.replace('|',' ').replace('​',' ').replace(' ',' ')
    t=re.sub(r'\s+',' ',t)
    t=re.sub(r'\s+([.,:;!?)])',r'\1',t)
    i=t.find('Table of contents'); j=t.find('Related Articles', i+1)
    if i>=0: t=t[i+17:j if j>0 else None]
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+|(?<=\S)\s+(?=[A-Z][a-z]+ [A-Z]?[a-z]*\?)', t) if s.strip()]
o,n=body(sys.argv[1]),body(sys.argv[2])
so,sn=set(o),set(n)
for s in o:
    if s not in sn: print('- '+s[:500])
for s in n:
    if s not in so: print('+ '+s[:500])
