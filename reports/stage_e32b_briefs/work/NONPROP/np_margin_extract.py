import sys,json,re
codes="MCL QM CL MNG QG NG MGC GC SIL SI MHG HG M6E 6E M6A 6A MET ETH MBT BTC M2K RTY MYM YM MNQ NQ 2YY 5YY 10Y 30Y ZT ZF ZN ZB MZC MZS MZW MZL MZM XC XK XW ZC ZS ZW ZL ZM".split()
assert len(codes)==47,len(codes)
rows=[l.rstrip('\n').split(' || ') for l in open(sys.argv[1])]
hdr=rows[0]
out={c:[] for c in codes}
for r in rows[1:]:
    if len(r)<12 or r[0] not in('CME','CBOT','NYMEX','COMEX','CBOT/CME','CME/CBOT'): continue
    for c in codes:
        if r[1]==c or r[3]==c:
            out[c].append(r)
for c in codes:
    print(c,len(out[c]),'|',' ;; '.join(' / '.join(x[:12]) for x in out[c])[:400])
json.dump(out,open(sys.argv[2],'w'))
