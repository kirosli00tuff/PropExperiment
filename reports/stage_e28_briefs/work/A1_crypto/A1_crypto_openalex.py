import sys, json, urllib.request, urllib.parse, re
email=''
for line in open('/home/kiros-li/Documents/GitHub/PropExperiment/.env'):
    if line.startswith('OPENALEX_EMAIL='): email=line.split('=',1)[1].strip().strip('"\'')
q=sys.argv[1]; n=sys.argv[2] if len(sys.argv)>2 else '15'
url='https://api.openalex.org/works?'+urllib.parse.urlencode({'search':q,'per-page':n,'mailto':email,'select':'id,title,publication_year,doi,primary_location,open_access,cited_by_count'})
d=json.load(urllib.request.urlopen(url,timeout=60))
for w in d['results']:
    src=((w.get('primary_location') or {}).get('source') or {}).get('display_name','')
    oa=(w.get('open_access') or {}).get('oa_url') or ''
    print(w['publication_year'],w['cited_by_count'],(w['title'] or '')[:110],'|',src[:40],'|',w.get('doi') or '','|',oa[:100])
