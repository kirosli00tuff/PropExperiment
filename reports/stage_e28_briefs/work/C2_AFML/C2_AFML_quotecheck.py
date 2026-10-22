import re,sys
P='pages/C2_AFML/'
md=open('C2_AFML.md').read()
sec=md.split('## Evidence table')[1].split('## Gaps')[0]
norm=lambda s: re.sub(r'\s+',' ',s).strip()
bad=0
for row in sec.splitlines():
    if not row.startswith('| ') or row.startswith('| Claim') or row.startswith('|---'): continue
    cols=[c.strip() for c in row.strip('|').split(' | ')]
    if len(cols)<4: print('COLS?',row[:60]); continue
    q=cols[2]; fs=re.findall(r'([\w.\-]+\.(?:txt|html|md))',cols[3])
    qs=re.findall(r'"(.+?)"(?: \(|$)',q) or [q.strip('"')]
    for qq in qs:
        qn=norm(qq.replace('\\"','"'))
        ok=False
        for f in fs:
            fn=f if not f.endswith('.html') else f
            for cand in (fn, fn.rsplit('.',1)[0]+'.txt'):
                try: t=norm(open(P+cand,errors='ignore').read())
                except FileNotFoundError: continue
                if qn in t or qn.replace("'",'’') in t or qn.replace("’","'") in t: ok=True
        if not ok: bad+=1; print('MISS:',cols[0][:40],'|',qn[:90])
print('checked; misses',bad)
