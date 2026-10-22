import re,glob,json
def norm(s):
    s=s.replace('“','"').replace('”','"').replace('’',"'").replace('‘',"'").replace('–','-').replace('—','-').replace('ﬁ','fi').replace('‐','-')
    return re.sub(r'\s+',' ',s).strip()
corpus=''
for f in glob.glob('pages/A1_rates/*.txt')+glob.glob('pages/A1_rates/*.json')+glob.glob('pages/A1_rates/*.xml'):
    corpus+=' '+norm(open(f,errors='ignore').read())
corpus+=' '+norm(' | '.join(' | '.join(map(str,c)) for sh,c in json.load(open('work/A1_rates/A1_rates_589_rows.json'))))
md=open('A1_rates.md').read()
qs=[q for q in re.findall(r"\"([^\"]*)\"",md) if len(q)>=25]
miss=[q for q in qs if norm(q).replace(' ... ',' ') not in corpus and not all(norm(p) in corpus for p in norm(q).split(' ... '))]
print(len(qs),'quotes;',len(miss),'missing')
for q in miss: print('-',q[:150])
