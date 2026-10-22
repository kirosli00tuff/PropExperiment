"""A1_grains: list OpenAlex locations (pdf/landing URLs) for DOIs. Email from .env, never printed."""
import sys, json, urllib.request, urllib.parse, re
env = open('/home/kiros-li/Documents/GitHub/PropExperiment/.env').read()
m = re.search(r'^OPENALEX_EMAIL=(.*)$', env, re.M); mail = m.group(1).strip().strip('"\'') if m else ''
for doi in sys.argv[1:]:
    url = f'https://api.openalex.org/works/doi:{doi}?' + urllib.parse.urlencode({'mailto': mail})
    try:
        w = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'A1_grains'}), timeout=60))
    except Exception as e:
        print(doi, 'ERR', e); continue
    print(doi, '|', w.get('title')[:90], '|', [a['author']['display_name'] for a in w.get('authorships', [])][:4])
    for l in w.get('locations', []):
        print('   ', l.get('is_oa'), l.get('pdf_url'), l.get('landing_page_url'))
