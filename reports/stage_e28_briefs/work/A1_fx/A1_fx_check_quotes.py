import json,re,os,zipfile
R='/home/kiros-li/Documents/GitHub/PropExperiment/'
d=json.load(open(R+'reports/stage_e28_briefs/A1_fx.json'))
norm=lambda t: re.sub(r'\s+',' ',t).strip()
bad=0; n=0
def walk(code,k,v):
    global bad,n
    q=v.get('quote'); sf=v.get('source_file')
    if not q or not sf or ';' in sf: return
    path=R+sf
    if not os.path.exists(path): print('MISSING FILE',code,k,sf); bad+=1; return
    if path.endswith('.zip'): return
    t=norm(open(path,errors='replace').read()); n+=1
    parts=[norm(x) for x in q.split(' / ')]
    for pq in parts:
        if pq not in t: print('NOT FOUND',code,k,'|',pq[:90]); bad+=1
for c in d:
    for k,v in c.items():
        if isinstance(v,dict): walk(c['code'],k,v)
        if isinstance(v,list):
            for i,x in enumerate(v): walk(c['code'],k+str(i),x)
print('checked',n,'bad',bad)
