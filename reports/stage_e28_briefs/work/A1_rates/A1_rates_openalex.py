import sys,urllib.request,urllib.parse,json,time,re
em=''
for l in open('/home/kiros-li/Documents/GitHub/PropExperiment/.env'):
    if l.startswith('OPENALEX_EMAIL='): em=l.split('=',1)[1].strip().strip('"\'')
out=open('work/A1_rates/A1_rates_openalex_hits.txt','a')
for q in sys.argv[1:]:
    p={'search':q,'per-page':25,'select':'id,doi,title,publication_year,primary_location,cited_by_count,open_access'}
    if em: p['mailto']=em
    url='https://api.openalex.org/works?'+urllib.parse.urlencode(p)
    try: d=json.load(urllib.request.urlopen(url,timeout=60))
    except Exception as e: out.write(f'## {q} ERROR {e}\n'); print(q,'ERR',e); continue
    out.write(f'## {q} n={d["meta"]["count"]}\n')
    for w in d['results']:
        src=((w.get('primary_location') or {}).get('source') or {}).get('display_name')
        oa=(w.get('open_access') or {}).get('oa_url')
        out.write(f"{w['publication_year']}\t{w['cited_by_count']}\t{w['title']}\t{src}\t{w.get('doi')}\t{oa}\n")
    print(q,d['meta']['count']); time.sleep(2)
