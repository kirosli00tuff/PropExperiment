import sys, json, urllib.request, urllib.parse
email=''
for line in open('/home/kiros-li/Documents/GitHub/PropExperiment/.env'):
    if line.startswith('OPENALEX_EMAIL='): email=line.split('=',1)[1].strip().strip('"\'')
for doi in sys.argv[1:]:
    url='https://api.openalex.org/works/https://doi.org/'+doi+'?'+urllib.parse.urlencode({'mailto':email})
    try: w=json.load(urllib.request.urlopen(url,timeout=60))
    except Exception as e: print(doi,'ERR',e); continue
    print('##',doi,(w['title'] or '')[:90], '| authors:', ', '.join(a['author']['display_name'] for a in w['authorships'][:5]))
    for l in w.get('locations',[]):
        print('   ',l.get('pdf_url') or '', '|', l.get('landing_page_url') or '')
