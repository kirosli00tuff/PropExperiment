import re,sys,os
P='pages/C2_DeepLOB/'
md=open('C2_DeepLOB.md').read()
rows=[l for l in md.split('## 14. Evidence table')[1].splitlines() if l.startswith('| ') and l[2].isdigit()]
def norm(s): 
    s=s.replace('-\n','').replace('\n',' ')
    return re.sub(r'\s+',' ',s).strip()
cache={}
def text(f):
    if f in cache: return cache[f]
    base=f.rsplit('.',1)[0]
    cands=[P+base+'.raw.txt',P+base+'.txt']
    t=' '.join(open(c,errors='ignore').read() for c in cands if os.path.exists(c))
    cache[f]=norm(t); return cache[f]
bad=0
for r in rows:
    cells=[c.strip() for c in r.strip('|').split('|')]
    n,f=cells[0],cells[-1]
    quotes=re.findall(r'"([^"]+)"',r)
    if f=='none': continue
    t=text(f)
    for q in quotes:
        parts=[p.strip() for p in q.split('...')]
        ok=all(norm(p) in t for p in parts if p)
        if not ok and '|' in q: ok=all(x.strip() in t for x in q.split('|') if x.strip() and x.strip()!='$')
        if not ok: bad+=1; print('MISS',n,f,q[:90])
print('rows',len(rows),'bad',bad)
