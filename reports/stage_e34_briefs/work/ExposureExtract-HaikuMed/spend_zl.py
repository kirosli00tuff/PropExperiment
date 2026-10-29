import json, collections
SRC = '/home/kiros-li/Documents/GitHub/PropExperiment/ledger/databento_spend.jsonl'
groups = collections.OrderedDict()
for ln, l in enumerate(open(SRC), 1):
    d = json.loads(l)
    req = d.get('request') or {}
    syms = req.get('symbols') or []
    s = ' '.join([str(d.get('symbol') or '')] + [str(x) for x in syms])
    if 'ZL' not in s:
        continue
    start = (req.get('start') or d.get('date') or '')[:10]
    end = (req.get('end') or '')[:10]
    key = (d.get('event'), d.get('schema'), ','.join(syms) if syms else d.get('symbol'), d.get('dataset'))
    g = groups.setdefault(key, {'n': 0, 'first': ln, 'last': ln, 'min_start': start, 'max_end': end, 'overlap': 0, 'quoted': 0, 'actual': 0.0})
    g['n'] += 1
    g['last'] = ln
    if start and (not g['min_start'] or start < g['min_start']): g['min_start'] = start
    if end and (not g['max_end'] or end > g['max_end']): g['max_end'] = end
    if start and end and start <= '2024-02-29' and end >= '2020-12-01':
        g['overlap'] += 1
    if d.get('event') == 'commit' and d.get('actual_usd') is not None:
        g['actual'] += float(d['actual_usd'])
for k, g in groups.items():
    print('|'.join(str(x) for x in k), '| n=', g['n'], '| lines', g['first'], '-', g['last'], '| window', g['min_start'], '..', g['max_end'], '| overlap_rows', g['overlap'])
