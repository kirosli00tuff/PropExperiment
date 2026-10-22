import json,sys,urllib.request,urllib.parse,time,re
env=open('/home/kiros-li/Documents/GitHub/PropExperiment/.env').read()
m=re.search(r'^OPENALEX_EMAIL=["\']?([^"\'\n]+)',env,re.M); e=m.group(1) if m else ''
for d in sys.argv[1:]:
    u="https://api.openalex.org/works/doi:"+urllib.parse.quote(d)+"?mailto="+urllib.parse.quote(e)
    try: w=json.load(urllib.request.urlopen(u,timeout=60))
    except Exception as x: print(d,'ERR',x); continue
    print(d,'|',(w.get('title') or '')[:80],'| OA:',w.get('open_access',{}).get('oa_url'),'| cited',w.get('cited_by_count'))
    for l in w.get('locations',[])[:6]: print('   ',l.get('pdf_url'),l.get('landing_page_url'))
    time.sleep(1)
