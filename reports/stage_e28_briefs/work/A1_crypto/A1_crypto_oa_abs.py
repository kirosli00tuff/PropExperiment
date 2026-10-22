import sys, json, urllib.request, urllib.parse, hashlib, datetime, subprocess, os
D='/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/pages/A1_crypto'
email=''
for line in open('/home/kiros-li/Documents/GitHub/PropExperiment/.env'):
    if line.startswith('OPENALEX_EMAIL='): email=line.split('=',1)[1].strip().strip('"\'')
for arg in sys.argv[1:]:
    doi,fn=arg.split('=')
    url='https://api.openalex.org/works/https://doi.org/'+doi
    raw=urllib.request.urlopen(url+'?'+urllib.parse.urlencode({'mailto':email}),timeout=60).read()
    open(f'{D}/{fn}','wb').write(raw)
    utc=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    pdt=subprocess.run(['date','+%Y-%m-%dT%H:%M:%S%Z'],env={'TZ':'America/Vancouver'},capture_output=True,text=True).stdout.strip()
    with open(f'{D}/log.tsv','a') as L: L.write(f"{url}\t{utc}\t{pdt}\tcurl(python urllib, OpenAlex API)\t{hashlib.sha256(raw).hexdigest()}\t{fn}\tOpenAlex work record incl. abstract_inverted_index (abstract only)\n")
    w=json.loads(raw); inv=w.get('abstract_inverted_index') or {}
    pos=sorted((p,t) for t,ps in inv.items() for p in ps)
    ab=' '.join(t for _,t in pos)
    open(f'{D}/{fn}.abstract.txt','w').write(ab)
    print('##',doi,w['title'],w['publication_year'],'|',(w.get('primary_location') or {}).get('source',{}) and w['primary_location']['source'].get('display_name'))
    print(ab[:1600]); print()
