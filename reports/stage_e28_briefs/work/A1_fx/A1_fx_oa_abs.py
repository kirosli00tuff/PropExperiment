import sys,json,urllib.request,urllib.parse,time,hashlib,datetime,os
em=''
for l in open('/home/kiros-li/Documents/GitHub/PropExperiment/.env'):
    if l.startswith('OPENALEX_EMAIL='): em=l.split('=',1)[1].strip().strip('"\'')
D='/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/pages/A1_fx/'
for doi in sys.argv[1:]:
    u='https://api.openalex.org/works/doi:'+doi+'?'+urllib.parse.urlencode({'mailto':em})
    raw=urllib.request.urlopen(u,timeout=60).read()
    w=json.loads(raw)
    fn='openalex_'+doi.replace('/','_')+'.json'
    open(D+fn,'wb').write(raw)
    inv=w.get('abstract_inverted_index') or {}
    pos=sorted((p,t) for t,ps in inv.items() for p in ps)
    ab=' '.join(t for p,t in pos)
    open(D+fn.replace('.json','_abstract.txt'),'w').write(w['title']+'\n'+str(w.get('publication_year'))+'\n'+ab+'\n')
    utc=datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    sha=hashlib.sha256(raw).hexdigest()
    print('https://api.openalex.org/works/doi:'+doi, utc, 'OpenAlex API', sha, fn, 'abstract via OpenAlex inverted index: '+w['title'][:80], sep='\t', file=open(D+'log.tsv','a'))
    print(doi, w['title'][:90], '| authors:', ', '.join(a['author']['display_name'] for a in w['authorships'][:4]))
    print('  ABS:', ab[:1500])
    time.sleep(2)
