import sys,re,json
def parse(path):
    L=[l.strip() for l in open(path,encoding='utf-8',errors='replace') if l.strip()]
    out={}
    for i,l in enumerate(L):
        if re.fullmatch(r'[A-Z0-9]{2,4}',l) and i>0 and i+1<len(L) and not re.fullmatch(r'(CME|CBOT|NYMEX|COMEX|EST|CT)',l):
            # following rows: hours lines..., tick size, tick value, RT
            j=i+1; vals=[]
            while j<len(L) and len(vals)<3:
                if re.fullmatch(r'\$?[0-9.,]+',L[j]): vals.append(L[j])
                elif vals: break
                j+=1
            if len(vals)==3: out[l]={'name':L[i-1],'tick_size':vals[0],'tick_value':vals[1],'rt':vals[2],'line':i+1}
    return out
a=parse(sys.argv[1]); 
if len(sys.argv)>2:
    b=parse(sys.argv[2])
    for k in sorted(set(a)|set(b)):
        ra=a.get(k,{}).get('rt'); rb=b.get(k,{}).get('rt')
        if ra!=rb: print(k,ra,'->',rb)
else:
    print(json.dumps(a))
