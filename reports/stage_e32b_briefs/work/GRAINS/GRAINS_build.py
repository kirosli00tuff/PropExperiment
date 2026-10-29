"""Assemble reports/stage_e32b_briefs/F2_grains.json from work/GRAINS items + meta.
Items: GRAINS_items.jsonl (one JSON object per line; later lines with same id replace earlier).
Meta: GRAINS_meta.json (family, worker, codes, times, counters, notices, searched_not_found, per_code, gaps).
Source url/fetched_utc/sha256 are filled from pages/GRAINS/log.tsv when source.file is a GRAINS page."""
import json, csv, os, sys
ROOT = '/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs'
W = f'{ROOT}/work/GRAINS'; P = f'{ROOT}/pages/GRAINS'
log = {}
with open(f'{P}/log.tsv') as fh:
    for r in csv.DictReader(fh, delimiter='\t'):
        log[r['file']] = r
items = {}
order = []
with open(f'{W}/GRAINS_items.jsonl') as fh:
    for ln in fh:
        ln = ln.strip()
        if not ln: continue
        it = json.loads(ln)
        if it['id'] not in items: order.append(it['id'])
        items[it['id']] = it
out_items = []
for i in order:
    it = items[i]
    src = it.setdefault('source', {})
    f = os.path.basename(src.get('file') or '')
    base = f[:-4] if f.endswith('.txt') and f[:-4] in log else f
    if base in log:
        r = log[base]
        src.setdefault('url', r['url']); src.setdefault('fetched_utc', r['fetched_utc']); src.setdefault('sha256', r['sha256'])
    for k in ('pointer', 'negative'):
        it.setdefault(k, False)
    out_items.append(it)
meta = json.load(open(f'{W}/GRAINS_meta.json'))
doc = {k: meta[k] for k in ['family','worker','codes','started_pdt','finished_pdt','websearch_calls','fulltext_reads_t6','notices']}
doc['items'] = out_items
for k in ['searched_not_found','per_code','gaps']:
    doc[k] = meta.get(k, [] if k != 'per_code' else {})
json.dump(doc, open(f'{ROOT}/F2_grains.json','w'), indent=1, ensure_ascii=False)
print('items', len(out_items), 'per_code', len(doc['per_code']))
