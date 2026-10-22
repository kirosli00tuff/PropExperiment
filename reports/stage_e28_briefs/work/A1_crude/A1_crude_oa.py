# OpenAlex title search; prints id, year, title, venue, OA url. Email read from .env, never printed.
import sys, json, urllib.request, urllib.parse, re
env=open('/home/kiros-li/Documents/GitHub/PropExperiment/.env').read()
m=re.search(r'^OPENALEX_EMAIL=(.*)$',env,re.M); mail=m.group(1).strip().strip('"\'') if m else ''
for q in sys.argv[1:]:
    u='https://api.openalex.org/works?'+urllib.parse.urlencode({'search':q,'per-page':6,'mailto':mail})
    try: d=json.load(urllib.request.urlopen(u,timeout=40))
    except Exception as e: print('ERR',q,type(e).__name__); continue
    print('##',q)
    for w in d.get('results',[]):
        oa=(w.get('best_oa_location') or {}); src=((w.get('primary_location') or {}).get('source') or {}).get('display_name')
        print(' ',w['id'].split('/')[-1],w.get('publication_year'),(w.get('title') or '')[:100],'|',src,'|',oa.get('pdf_url') or oa.get('landing_page_url'),'| doi',w.get('doi'))
