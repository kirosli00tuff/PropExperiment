"""Record dtypes of the three schemas (field names/types only) and ZL definition facts (raw_symbol, expiration,
min_price_increment, asset, class) for the ZL instrument ids seen in the ZL MBP-1 files. No market price field is read."""
import json, os, sys
from pathlib import Path
import numpy as np
os.nice(10)
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import guard34, databento as db
out = {}
def first_dtype(p):
    store = db.DBNStore.from_file(guard34.check(p))
    for c in store.to_ndarray(count=5):
        return {k: str(v[0]) for k, v in c.dtype.fields.items()}, c.dtype.itemsize
out["mbp-1"] = first_dtype(sorted(guard34.MBP1_DIR.glob("range=*.dbn.zst"))[0])
out["ohlcv-1m"] = first_dtype(sorted(guard34.OHLCV["ZL"].glob("range=2020-12-01*"))[0])
defs = sorted(guard34.DEF_DIR.glob("range=*.dbn.zst"))
out["definition"] = first_dtype(defs[0])
agg = json.load(open(HERE / "agg_zl.json"))
ids = set(agg["distinct_instrument_ids"])
rows = {}; n_def = 0; per_file = {}
for p in defs:
    store = db.DBNStore.from_file(guard34.check(p))
    m = store.metadata
    per_file[p.name] = {"schema": str(m.schema), "stype_in": str(m.stype_in), "symbols": list(m.symbols)[:5], "n_symbols": len(m.symbols)}
    for c in store.to_ndarray(count=500_000):
        guard34.check_ts(c["ts_recv"].astype(np.int64), p.name)
        n_def += len(c)
        iid = c["instrument_id"].astype(np.int64)
        for i in np.flatnonzero(np.isin(iid, [int(x) for x in ids])):
            k = str(iid[i])
            if k not in rows:
                rows[k] = {"raw_symbol": bytes(c["raw_symbol"][i]).split(b"\0")[0].decode(),
                           "asset": bytes(c["asset"][i]).split(b"\0")[0].decode(),
                           "instrument_class": chr(int(np.frombuffer(bytes(c["instrument_class"][i]), dtype=np.uint8)[0])) if c["instrument_class"].dtype.kind == "S" else str(c["instrument_class"][i]),
                           "expiration_utc_ns": int(c["expiration"][i]), "min_price_increment": int(c["min_price_increment"][i]),
                           "n_records": 0}
            rows[k]["n_records"] += 1
out["zl_defs"] = rows; out["definition_records_total"] = n_def; out["definition_files"] = per_file
(HERE / "schema_defs.json").write_text(json.dumps(out, indent=1, default=str))
print(out["mbp-1"][1], out["ohlcv-1m"][1], out["definition"][1], "defs seen", len(rows), "of", len(ids), "records", n_def)
