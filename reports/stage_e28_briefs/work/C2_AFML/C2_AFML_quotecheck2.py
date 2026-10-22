import re,glob
norm=lambda s: re.sub(r'\s+',' ',s).strip()
body=open('C2_AFML.md').read().split('## References')[0]
corpus=[norm(open(f,errors='ignore').read()) for f in glob.glob('pages/C2_AFML/*.txt')+glob.glob('pages/C2_AFML/*.md')+glob.glob('pages/C2_AFML/*.html')]
miss=0
for q in re.findall(r'"([^"\n]{25,}?)"',body.replace('\n',' ')):
    qn=norm(q)
    if not any(qn in c for c in corpus):
        miss+=1; print('MISS:',qn[:120])
print('misses',miss)
