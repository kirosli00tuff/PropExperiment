import json, re, html, os, glob
R="/home/kiros-li/Documents/GitHub/PropExperiment/"
P=R+"reports/stage_e28_briefs/pages/A2_platforms/"
def norm(s):
    s=html.unescape(s)
    s=s.replace('’',"'").replace('‘',"'").replace('“','"').replace('”','"').replace('\\|','|')
    return re.sub(r'\s+',' ',s).strip()
def text_of(fn):
    raw=open(fn,errors='ignore').read()
    if fn.endswith('.json'):
        d=json.loads(raw)
        if 'post_stream' in d:
            raw=' '.join(re.sub('<[^>]+>',' ',p['cooked']) for p in d['post_stream']['posts'])
    return norm(raw)
cache={}
def T(fn):
    if fn not in cache: cache[fn]=text_of(fn)
    return cache[fn]
D=json.load(open(R+"reports/stage_e28_briefs/A2_platforms.json"))
bad=0
for k,v in D.items():
    if k=="_meta": continue
    for item,fct in v.items():
        q=fct["quote"]; sf=fct["source_file"]
        if not q: continue
        ok=norm(q) in T(R+sf)
        if not ok: bad+=1; print("JSON MISS",k,item,q[:80])
print("json misses",bad)
# markdown: every "..." span in table rows with a source file mentioned
md=open(R+"reports/stage_e28_briefs/A2_platforms.md").read()
alltxt={os.path.basename(f):T(f) for f in glob.glob(P+"*") if f.endswith(('.txt','.md','.json'))}
miss=0
for line in md.split('\n'):
    for q in re.findall(r'"([^"]{12,})"', line):
        nq=norm(q)
        if not any(nq in t for t in alltxt.values()):
            miss+=1; print("MD MISS:", q[:110])
print("md misses",miss)
