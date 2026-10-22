import sys,re,json,urllib.request,urllib.parse,time
em=''
for l in open('/home/kiros-li/Documents/GitHub/PropExperiment/.env'):
    if l.startswith('OPENALEX_EMAIL='): em=l.split('=',1)[1].strip().strip('"\'')
for q in sys.argv[1:]:
    u='https://api.openalex.org/works?'+urllib.parse.urlencode({'search':q,'per_page':12,'mailto':em,'select':'id,doi,title,publication_year,cited_by_count,primary_location,open_access'})
    try:
        d=json.loads(urllib.request.urlopen(u,timeout=60).read())
    except Exception as e:
        print('ERR',q,str(e)[:80]); continue
    print('## ',q, d.get('meta',{}).get('count'))
    for w in d['results']:
        src=((w.get('primary_location') or {}).get('source') or {}).get('display_name')
        print(w['publication_year'],w['cited_by_count'],(w.get('doi') or '')[16:],'|',(w['title'] or '')[:110],'|',(src or '')[:40],'|',(w.get('open_access') or {}).get('oa_url'))
    time.sleep(2)
