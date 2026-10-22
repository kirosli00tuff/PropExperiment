import json,os
d=json.load(open('A1_rates.json'))
def fmt(v):
    if isinstance(v,dict): return '; '.join(f'{k}: {fmt(x)}' for k,x in v.items())
    if v is None: return 'null (unknown)'
    return str(v)
out=['## Candidate fact sheets (generated from A1_rates.json by work/A1_rates/A1_rates_render_sheets.py)','',
     'Quotes for every field are in A1_rates.json and in the F sections above. "Source" gives file base names under',
     'pages/A1_rates/ unless another path is shown. Family-wide facts are referenced as F1..F12.','']
for o in d:
    out.append(f"### {o['candidate']}")
    out.append('')
    out.append('| Field | Value | Unit | Window | Source | Note |')
    out.append('|---|---|---|---|---|---|')
    for k,v in o.items():
        if k in ('candidate','family'): continue
        if k=='tff_category_shares' and isinstance(v.get('value'),dict):
            val='see F6 table'
        else: val=fmt(v.get('value'))
        src=v.get('source_file') or ''
        src='; '.join(os.path.basename(s.strip()) if 'pages/A1_rates/' in s else s.strip() for s in src.split(';')) if src else ''
        cells=[k,val,v.get('unit') or '',v.get('window') or '',src,(v.get('note') or '')]
        out.append('| '+' | '.join(c.replace('|','/').replace('\n',' ') for c in cells)+' |')
    out.append('')
open('work/A1_rates/A1_rates_sheets.md','w').write('\n'.join(out)+'\n'); print(len(out))
