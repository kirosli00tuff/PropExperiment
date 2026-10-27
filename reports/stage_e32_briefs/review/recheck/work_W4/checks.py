import re, math, itertools
from scipy.stats import binom, norm
_ID = re.compile(r"[A-Z][A-Za-z0-9]{0,15}-[A-Za-z0-9]{1,16}")
sets=[f"S{i}" for i in range(1,6)]
labels=["F05","F15","F30","F60","T15","T30"]
grid=["L001A","L001E","L010A","L010E","L100A","L100E","G2050","G2200","G3050","G3200"]
ids=[f"E33-{s}{l}{g}" for s in sets for l in labels for g in grid]
ok=[bool(_ID.fullmatch(t)) and t.startswith("E33-") for t in ids]
print("IDs:",len(ids),"unique:",len(set(ids)),"all match:",all(ok),"max len after hyphen:",max(len(t)-4 for t in ids))
print("old-style refused:",_ID.fullmatch("E33-S5-FH15-L-C0.01-r0") is None)
# binomials
print("P(>=2 of 20 | 0.05) =",round(binom.sf(1,20,0.05),4))
print("P(>=14 of 20 | 0.8) =",round(binom.sf(13,20,0.8),4))
print("P(>=14 of 20 | 0.914) =",round(binom.sf(13,20,0.914),4))
print("P(>=14 of 20 | 0.492) =",round(binom.sf(13,20,0.492),4))
# normal tails
print("300*P(Z>5.66) =",300*norm.sf(5.66), " 300*P(Z>4.86)=",300*norm.sf(4.86))
print("0.2007*sqrt(796)=",0.2007*math.sqrt(796)," 0.1724*sqrt(796)=",0.1724*math.sqrt(796))
print("1/sqrt(796)=",1/math.sqrt(796))
# folds
blocks=[133,133,133,133,132,132]; assert sum(blocks)==796
dates=list(range(796)); starts=[sum(blocks[:k]) for k in range(6)]
E=21; sizes=[]
for k in range(6):
    s,e=starts[k],starts[k]+blocks[k]
    last=e-1
    emb=set(range(last+1,min(last+1+E,796)))
    train=[d for d in dates if not (s<=d<e) and d not in emb]
    sizes.append(len(train))
print("training sizes:",sizes)
print("SFI 59*6=",59*6," x5=",59*6*5, " 40 searches*1800=",40*1800, " subset 20cfg*6folds=",20*6," x40=",20*6*40)
print("est loss margin (0.35-0.25)/0.35=",(0.35-0.25)/0.35)
