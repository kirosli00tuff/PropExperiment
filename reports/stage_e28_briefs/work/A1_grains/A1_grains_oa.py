"""A1_grains OpenAlex search: prints title | year | venue | doi | oa_url for a query. Email read from .env, never printed."""
import sys, json, urllib.request, urllib.parse, re
env = open('/home/kiros-li/Documents/GitHub/PropExperiment/.env').read()
m = re.search(r'^OPENALEX_EMAIL=(.*)$', env, re.M)
mail = m.group(1).strip().strip('"\'') if m else ''
q = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
url = 'https://api.openalex.org/works?' + urllib.parse.urlencode({'search': q, 'per-page': n, 'mailto': mail})
r = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'A1_grains'}), timeout=60))
for w in r.get('results', []):
    loc = (w.get('primary_location') or {}).get('source') or {}
    oa = (w.get('open_access') or {}).get('oa_url')
    print(f"{w.get('title')} | {w.get('publication_year')} | {loc.get('display_name')} | {w.get('doi')} | {oa} | cited {w.get('cited_by_count')}")
