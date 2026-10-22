import re,sys
md=open(sys.argv[1]).read(); root=sys.argv[2]
sec=md[md.index('## 11. Evidence table'):md.index('## 12. Run notes')]
def norm(x): return re.sub(r'\s+',' ',x.replace('-\n','')).strip()
bad=0
for line in sec.splitlines():
    if not line.startswith('| ') or line.startswith('| Claim') or line.startswith('|---'): continue
    cells=[c.strip() for c in line.strip('|').split('|')]
    q=cells[2].strip('"'); f=cells[3]
    try: t=norm(open(root+'/'+f,errors='ignore').read())
    except Exception as e: print('NOFILE',f); bad+=1; continue
    parts=[p.strip(' "') for p in q.split('...')]
    parts=[p for p in parts if p and not p.startswith('(')]
    for p in parts:
        p=norm(p.split('" (')[0])
        if p not in t: print('MISS',f,'|',p[:90]); bad+=1
print('bad',bad)
