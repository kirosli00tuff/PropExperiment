# OpenAlex work lookup by id: title, authors, venue, OA locations, abstract (reconstructed). Email from .env, never printed.
import sys, json, urllib.request, urllib.parse, re
env=open('/home/kiros-li/Documents/GitHub/PropExperiment/.env').read()
m=re.search(r'^OPENALEX_EMAIL=(.*)$',env,re.M); mail=m.group(1).strip().strip('"\'') if m else ''
for wid in sys.argv[1:]:
    u='https://api.openalex.org/works/'+wid+'?'+urllib.parse.urlencode({'mailto':mail})
    try: w=json.load(urllib.request.urlopen(u,timeout=40))
    except Exception as e: print('ERR',wid,type(e).__name__); continue
    au=', '.join(a['author']['display_name'] for a in w.get('authorships',[])[:5])
    print('##',wid,w.get('publication_year'),w.get('title'),'|',au,'| doi',w.get('doi'))
    for l in w.get('locations',[]):
        if l.get('pdf_url') or l.get('is_oa'): print('  loc',l.get('pdf_url'),l.get('landing_page_url'))
    ii=w.get('abstract_inverted_index')
    if ii:
        pos={p:k for k,v in ii.items() for p in v}; print('  ABS:',' '.join(pos[i] for i in sorted(pos)))
