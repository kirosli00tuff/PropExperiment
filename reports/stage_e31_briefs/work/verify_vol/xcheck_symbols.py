"""Per-record symbol resolution: my half-open interval rule vs the producer's symbol_for (imported read-only)."""
import sys, importlib.util, datetime as dt, collections
import databento as db
spec = importlib.util.spec_from_file_location("vm", "../pilot/vol_measure.py")
vm = importlib.util.module_from_spec(spec); spec.loader.exec_module(vm)
s = db.DBNStore.from_file(sys.argv[1]); a = s.to_ndarray()
ts = a["ts_event"].astype("int64"); iid = a["instrument_id"].astype("int64"); del a
inv = vm.invert_mappings(s.metadata.mappings)
mine = collections.defaultdict(list)
for raw, l in s.metadata.mappings.items():
    for e in l: mine[int(e["symbol"])].append((e["start_date"], e["end_date"], raw))
diff = 0; outside = 0
for t, i in zip(ts.tolist(), iid.tolist()):
    d = vm.ns_to_date(t)
    c = [r for sd, ed, r in mine[i] if sd <= d < ed]
    if not c: outside += 1
    if (c[0] if c else None) != vm.symbol_for(i, d, inv): diff += 1
print("records", len(ts), "symbol differences", diff, "records outside every interval", outside)
reused = [i for i, v in mine.items() if len({r for _, _, r in v}) > 1]
print("reused ids", len(reused), "with bars in file", len(set(reused) & set(iid.tolist())))
# boundary behaviour of the producer on a reused id: the day the first interval ends (exclusive end)
i = 42014428; d = dt.date(2024, 2, 25)
print("producer on exclusive-end day of reused id:", vm.symbol_for(i, d, inv))
try:
    print("producer in a gap day:", vm.symbol_for(i, dt.date(2024, 6, 1), inv))
except Exception as e:
    print("producer in a gap day raises:", type(e).__name__)
