import json, re, sys
mc=json.load(open('A3_masked_contracts.json')); mf=json.load(open('A3_masked_firms.json')); br=json.load(open('A3_blind_ratings.json'))
errs=[]
for lab,c in br['contracts'].items():
    if c.get('C1a') not in ('high','medium','low'): errs.append((lab,'C1a',c.get('C1a')))
    if c.get('C1b') not in ('low','medium','high'): errs.append((lab,'C1b',c.get('C1b')))
    if not (isinstance(c.get('C6'),int) and 0<=c['C6']<=4): errs.append((lab,'C6',c.get('C6')))
    a={'high':1,'medium':0,'low':-1}[c['C1a']]; b={'low':1,'medium':0,'high':-1}[c['C1b']]
    if c.get('C1_computed')!=2+a+b: errs.append((lab,'C1_computed',c.get('C1_computed')))
    for k in ('C1a','C1b','C6'):
        r=c.get('reasons',{}).get(k,'')
        if len(r)<15: errs.append((lab,'reason',k))
# firms
def find_classes(fsheet):
    # look for keys naming product classes in the masked firm sheet
    out=set()
    def walk(o,path=''):
        if isinstance(o,dict):
            for k,v in o.items():
                if k in ('restrictions_by_class','product_classes','classes','R_by_class','restrictions'):
                    if isinstance(v,dict): out.update(v.keys())
                    elif isinstance(v,list): out.update(x if isinstance(x,str) else x.get('class','?') for x in v)
                walk(v,path+'/'+k)
        elif isinstance(o,list):
            for x in o: walk(x,path)
    walk(fsheet); return out
for lab,f in br['firms'].items():
    R=f.get('R',{})
    if not isinstance(R,dict) or not R: errs.append((lab,'R',R))
    for k,v in R.items():
        if not (isinstance(v,int) and 0<=v<=4): errs.append((lab,'R',k,v))
    if not (isinstance(f.get('A'),int) and 0<=f['A']<=4): errs.append((lab,'A',f.get('A')))
    if f.get('F') not in (1,2,4): errs.append((lab,'F',f.get('F')))
    d=f.get('Rel_deductions',{})
    allowed={'under_2_years':(0,1),'payout_delays_denials_disputes_12m':(0,1),'two_plus_adverse_rule_changes_12m':(0,1),'regulatory_action_vs_firm':(0,2)}
    for k,ok in allowed.items():
        if d.get(k) not in ok: errs.append((lab,'Rel_ded',k,d.get(k)))
    if f.get('Rel')!=max(0,4-sum(d.values())): errs.append((lab,'Rel',f.get('Rel')))
    for k in ('R','A','F','Rel'):
        if len(f.get('reasons',{}).get(k,''))<15: errs.append((lab,'reason',k))
    cls=find_classes(mf['firms'][lab])
    print(lab,'sheet classes:',sorted(cls),'| rated:',sorted(R.keys()),'| A',f['A'],'F',f['F'],'Rel',f['Rel'])
print('errors:',errs if errs else 'none')
print('mf top keys F01:', list(mf['firms']['F01'].keys()))
print('class_context keys:', list(mf['_class_context'].keys())[:20] if isinstance(mf['_class_context'],dict) else type(mf['_class_context']).__name__)
