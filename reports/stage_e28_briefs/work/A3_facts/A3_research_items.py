"""A3 helper: normalize A1 research evidence into a list of items per candidate."""
import json
RK = {'crude': 'microstructure_research', 'crypto': 'microstructure_studies', 'equity': 'microstructure_studies',
      'fx': 'microstructure_research', 'grains': 'microstructure_research', 'metals': 'research',
      'natgas': 'microstructure_research', 'rates': 'microstructure_research'}
BASE = '/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs'

def items_for(fam, row):
    k = RK[fam]; v = row.get(k)
    out = []
    def add(x, extra=None):
        if isinstance(x, dict) and ('study' in x or 'relation' in x):
            out.append(x)
        elif isinstance(x, dict) and 'value' in x:
            val = x['value']
            if isinstance(val, list):
                for y in val: add(y, x)
            elif isinstance(val, dict):
                d = dict(val); d.setdefault('quote', x.get('quote')); d.setdefault('source_file', x.get('source_file')); d.setdefault('note', x.get('note'))
                out.append(d)
            else:
                out.append({'study': val, 'relation': None, 'result': None, 'quote': x.get('quote'),
                            'source_file': x.get('source_file'), 'note': x.get('note')})
        elif isinstance(x, list):
            for y in x: add(y)
        elif isinstance(x, str):
            out.append({'study': x})
    add(v)
    return out

if __name__ == '__main__':
    for fam in RK:
        for r in json.load(open(f'{BASE}/A1_{fam}.json')):
            c = r.get('candidate') or r.get('code')
            for it in items_for(fam, r):
                print(fam, c, '|', str(it.get('id', ''))[:3], str(it.get('study'))[:60], '|', str(it.get('relation'))[:70], '|', str(it.get('result'))[:45])
