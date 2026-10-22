import json,re
d=json.load(open('A1_rates.json'))
def norm(s): return re.sub(r'\s+',' ',s).strip()
X=' | '.join(' | '.join(map(str,c)) for sh,c in json.load(open('work/A1_rates/A1_rates_589_rows.json')))
bad=0;checked=0
for o in d:
    for k,v in o.items():
        if not isinstance(v,dict) or not v.get('quote') or not v.get('source_file'): continue
        srcs=[s.strip() for s in v['source_file'].split(';')]
        for q in v['quote'].split('||'):
            for part in q.split('; ') if 'report)' in q else [q]:
                part=norm(re.sub(r'\((Mar 2024|Oct 2025) report\)','',part))
                found=False
                for s in srcs:
                    txt=X if s.endswith('.xlsx') else open('/home/kiros-li/Documents/GitHub/PropExperiment/'+s,errors='ignore').read()
                    if part in norm(txt): found=True;break
                checked+=1
                if not found: bad+=1; print('MISS',o['candidate'],k,part[:100])
print('checked',checked,'missing',bad)
