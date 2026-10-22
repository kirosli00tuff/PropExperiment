"""A1_grains: print OpenAlex abstract (rebuilt from inverted index) for DOIs; saves raw JSON to pages/A1_grains."""
import sys, json, urllib.request, urllib.parse, re, hashlib, datetime
from zoneinfo import ZoneInfo
D = '/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/pages/A1_grains/'
env = open('/home/kiros-li/Documents/GitHub/PropExperiment/.env').read()
m = re.search(r'^OPENALEX_EMAIL=(.*)$', env, re.M); mail = m.group(1).strip().strip('"\'') if m else ''
for doi in sys.argv[1:]:
    url = f'https://api.openalex.org/works/doi:{doi}'
    raw = urllib.request.urlopen(urllib.request.Request(url + '?' + urllib.parse.urlencode({'mailto': mail}), headers={'User-Agent': 'A1_grains'}), timeout=60).read()
    out = 'openalex_' + re.sub(r'[^A-Za-z0-9]+', '_', doi) + '.json'
    open(D + out, 'wb').write(raw)
    utc = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'); pdt = datetime.datetime.now(ZoneInfo('America/Vancouver')).strftime('%Y-%m-%dT%H:%M:%S%Z')
    open(D + 'log.tsv', 'a').write(f"{url}\t{utc}\t{pdt}\tcurl(urllib) OpenAlex API\t{hashlib.sha256(raw).hexdigest()}\t{out}\tOpenAlex record (abstract only)\n")
    w = json.loads(raw); inv = w.get('abstract_inverted_index') or {}
    pos = sorted((p, t) for t, ps in inv.items() for p in ps)
    print('##', doi, '|', w.get('title'), '|', w.get('publication_year'), '|', out)
    print(' '.join(t for _, t in pos)[:1500])
