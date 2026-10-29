"""Apply lead rulings LR-D1, LR-D2, FL-9 to F2_data_access.json (idempotent: reads p_brief if already set)."""
import json, collections
P='/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/F2_data_access.json'
d=json.load(open(P)); C=d['codes']; r=d['ratios']['r']; RZM=3.06
band=lambda k: 0 if k<=10 else (1 if k<=50 else 2)
changed=[]
for c,v in C.items():
    # LR-D1 variant k_ZM
    if v['k_usd_month'] is None:
        kz={'k_usd_month':None,'band':1,'note':'unknown, band 1'}
    elif v['k_method']=='ledger MBO':
        kz={'k_usd_month':v['k_usd_month'],'band':v['k'],'note':'ledger MBO: no r applied, same as primary'}
    else:
        k=v['k_usd_month']/r*RZM; kz={'k_usd_month':round(k,4),'band':band(k),'note':'primary k / 0.9195 x 3.06'}
    v['k_ZM']={'label':'variant k_ZM (lead ruling LR-D1)','r':RZM,**kz}
    # LR-D2: primary p = spec text
    if 'p_brief' not in v:
        v['p_brief']={'label':'variant p_brief (lead ruling LR-D2)','value':v['p_all_read'],'basis':v['p_basis']}
    old=v['p_brief']['value']
    new=v['p_spec_reading']
    v['p_all_read']=new; v['p']=new
    seals=[s for s in v['sealed_windows']]
    pre=[s for s in seals if s['end']<'2024-03-01']
    post=[s for s in seals if s['end']>='2024-03-01']
    reasons=[]
    if v['p_unread_stretches']:
        reasons.append('unread unsealed stretch(es) of 36 months or more before 2024-03-01: '+'; '.join(f"{x['start']}..{x['end_exclusive']} ({x['months']} months)" for x in v['p_unread_stretches']))
    if pre:
        reasons.append('pre-2024-03 window(s) sealed for a future test: '+'; '.join(f"{s['name']} {s['start']}..{s['end']}" for s in pre))
    if not reasons:
        reasons.append(f"history {v['p_history_start']}..2024-02-29 ({v['p_history_months']} months): no unread unsealed stretch of 36 months or more, no pre-2024-03 window sealed")
    if post:
        reasons.append('(post-2024-03 seal ignored under the spec-text reading: '+'; '.join(f"{s['name']} {s['start']}..{s['end']}" for s in post)+')')
    v['p_basis']='; '.join(reasons)
    v['D5_informational']=max(0,4-v['h']-v['k']-v['o']-v['p'])
    v['D5_informational_k_ZM']=max(0,4-v['h']-v['k_ZM']['band']-v['o']-v['p'])
    if old!=new: changed.append(c)
d['lead_rulings']={
 'LR-D1':'Primary r = 0.9195 (ES-proxy, same 5 days). Variant field per code k_ZM = k and band with r = 3.06 (ZM ratio); primary k fields unchanged. FL-1 accepted: one sampled day x 21 trading days = one month.',
 'LR-D2':'Primary p_all_read follows the spec text: only seals of pre-2024-03 windows count; holdout 2 (2024-03-01..2025-03-31) does not by itself set p = 0. The brief-based value is kept as p_brief. Codes where they differ: '+', '.join(changed),
 'FL-9 rule':'A registration counts as a read only for the windows its search actually ran on. E22-F1 (r007) was registered but parked without running: not a read. This census never counted r007 (read windows come from r002-E16, r005-E20S, r006-E21, r009-E33 only; r008-E23 and r001/r003 listed but not used), so no p value changed on this ruling.',
 'accepted_as_applied':['FL-3','FL-4','FL-5','FL-6','FL-8','FL-10','FL-11'],
 'p_changed_primary_vs_previous_file':changed}
for f in d['for_lead']:
    if f['id'] in('FL-1','FL-2','FL-7','FL-9'): f['status']='ruled by lead (see lead_rulings)'
    elif f['id'] in d['lead_rulings']['accepted_as_applied']: f['status']='accepted by lead'
d['assumptions']['p_rule_reading']='PRIMARY (LR-D2): spec text, pre-2024-03 seals only. p_brief = brief reading.'
json.dump(d,open(P,'w'),indent=1)
cnt=lambda f: dict(sorted(collections.Counter(f(v) for v in C.values()).items()))
print('h',cnt(lambda v:v['h']),'k',cnt(lambda v:v['k']),'o',cnt(lambda v:v['o']),'p',cnt(lambda v:v['p']))
print('k_ZM',cnt(lambda v:v['k_ZM']['band']),'p_brief',cnt(lambda v:v['p_brief']['value']))
print('p changed',changed)
print('k_ZM band differs',[c for c,v in C.items() if v['k_ZM']['band']!=v['k']])
print('D5 primary', cnt(lambda v:v['D5_informational']))
