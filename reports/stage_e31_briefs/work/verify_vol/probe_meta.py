import databento as db, sys, collections
P = sys.argv[1]
s = db.DBNStore.from_file(P)
m = s.metadata
mp = m.mappings
print("n raw symbols in mappings", len(mp))
for x in list(mp)[:2]:
    print(x, mp[x][:3])
iv = collections.defaultdict(list)
for raw, lst in mp.items():
    for e in lst:
        iv[e['symbol']].append((raw, e['start_date'], e['end_date']))
print("distinct id strings", len(iv), "ids with >1 raw", sum(1 for v in iv.values() if len({r for r,_,_ in v})>1))
print("n partial", len(m.partial), "n not_found", len(m.not_found))
a = s.to_ndarray()
print(a.dtype.names, len(a))
