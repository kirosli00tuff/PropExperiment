"""Apply LR-D3 to F2_data_access.json: C1b and E23 read windows (role/counts_for_p), C1 not a read; recheck p."""
import json
from datetime import date
P='/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/F2_data_access.json'
d=json.load(open(P)); C=d['codes']
SRC12='reports/stage_e32b_briefs/R1_closed_lines.json R1-12 (docs/DECISIONS.md:564,578-580; docs/STAGES.md:159-162)'
SRC18='reports/stage_e32b_briefs/R1_closed_lines.json R1-18 (docs/DECISIONS.md:749-754; docs/STAGES.md:190-198)'
def mk(reg,line,s,e,role,counts,src,note=''):
    return {'registration':reg,'ledger_line':line,'start':s,'end':e,'role':role,'counts_for_p':counts,'bar_based_directional':True,'source':src,'note':note}
add={'NG':[mk('r003-C1b (evaluated once)',4,'2010-07-01','2019-04-30','traded',True,SRC12,'NG store 2010-06-07..2019-04-30, W_ext 2010-07..2019-04')],
     'NQ':[mk('r003-C1b feature leg',4,'2010-07-01','2019-04-30','feature leg',False,SRC12,'LR-D3: feature leg, not a read')],
     'ZN':[mk('r003-C1b feature leg',4,'2010-07-01','2019-04-30','feature leg',False,SRC12,'LR-D3: feature leg, not a read')],
     '6E':[mk('r003-C1b feature leg',4,'2010-07-01','2019-04-30','feature leg',False,SRC12,'LR-D3: feature leg, not a read')],
     'GC':[mk('r003-C1b feature leg',4,'2010-07-01','2019-04-30','feature leg',False,SRC12,'feature leg per R1-12 (not named in LR-D3; same rule)')],
     'ZC':[mk('r003-C1b feature leg',4,'2010-07-01','2019-04-30','feature leg',False,SRC12,'feature leg per R1-12 (not named in LR-D3; same rule)')]}
for r in ('ZF','ZN','ZB','NQ'):
    add.setdefault(r,[]).append(mk('r008-E23 (K2-monthend-01 / E20H6-T1) discovery W_ext',9,'2011-07-27','2019-04-30','traded',True,SRC18,'confirmation W_cf 2019-05..2024-02 not computed: not a read'))
under={}
for c,v in C.items(): under.setdefault(v['underlying'],[]).append(c)
changed=[]
for c,v in C.items():
    # drop the earlier combined C1/C1b entry (r001 is not a read)
    v['read_windows']=[w for w in v['read_windows'] if not w['registration'].startswith('r001-C1')]
    for w in v['read_windows']:
        w.setdefault('role','traded'); w.setdefault('counts_for_p',True)
    for g in under[v['underlying']]:
        for w in add.get(g,[]):
            v['read_windows'].append({'root':g,**w})
    # recheck: does any new counting window overlap an unread >=36-month stretch?
    for s in v['p_unread_stretches']:
        a,b=date.fromisoformat(s['start']),date.fromisoformat(s['end_exclusive'])
        for g in under[v['underlying']]:
            for w in add.get(g,[]):
                if w['counts_for_p'] and date.fromisoformat(w['start'])<b and date.fromisoformat(w['end'])>=a:
                    print('OVERLAP (stretch may shrink):',c,s,w['registration'])
d['lead_rulings']['LR-D3']=("FL-9 further ruling: r003-C1b (evaluated once) is a read of NG's window 2010-07..2019-04 (traded leg); its feature legs NQ, ZN, 6E (and GC, ZC per R1-12) are listed in read_windows with role 'feature leg' and counts_for_p false. "
 "r001-C1 (stopped at guard C10 before any statistic) is not a read (its entry removed). r008-E23 discovery W_ext 2011-07-27..2019-04-30 is a read for traded legs ZF, ZN, ZB, NQ (NQ counts for the Nasdaq underlying, MNQ); its confirmation window 2019-05..2024-02 was not computed: not a read. Source: R1_closed_lines.json R1-12, R1-18. "
 "Effect on p: none, because E16 (r002) already covers NG, ZF, ZN, ZB and NQ over 2010-07..2024-02; p and p_brief unchanged.")
json.dump(d,open(P,'w'),indent=1)
import collections
print('p',dict(collections.Counter(v['p'] for v in C.values())),'p_brief',dict(collections.Counter(v['p_brief']['value'] for v in C.values())))
print('p_unread for NG/ZF/ZN/ZB/NQ groups:',{c:C[c]['p_unread_stretches'] for c in ('NG','ZF','ZN','ZB','NQ','MNQ')})
