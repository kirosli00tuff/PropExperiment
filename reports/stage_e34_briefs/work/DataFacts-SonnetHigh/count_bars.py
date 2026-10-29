"""Per-file counts of ohlcv-1m bars for ZL, ZS, ZM (v.0), fields read: ts_event, instrument_id, rtype only
(no open/high/low/close/volume indexed, no record printed). Trade date D = E.33 window rule on ts_event
([D-1 16:00 CT, D 16:00 CT)), restricted to the 816 calendar trade dates. Day-session bars: ts_event CT
time-of-day in [08:30, 13:20). Resumable: bars/<root>_<name>.json skipped when present."""
from __future__ import annotations
import json, os, sys, time
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np
os.nice(10)
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import guard34
import databento as db
CT = ZoneInfo("America/Chicago"); NS = 1_000_000_000; DAY_NS = 86400 * NS
OUT = HERE / "bars"; OUT.mkdir(exist_ok=True)
TD_SET = set(date.fromisoformat(x) for x in json.loads((HERE / "trade_dates_e33rule.json").read_text()))
CAL = [date(2020, 11, 30) + timedelta(days=i) for i in range((date(2024, 3, 2) - date(2020, 11, 30)).days + 1)]
def ct_ns(d, h): return int(datetime(d.year, d.month, d.day, h, tzinfo=CT).timestamp()) * NS
WIN_LO = np.array([ct_ns(d - timedelta(days=1), 16) for d in CAL], dtype=np.int64)
IS_TD = np.array([d in TD_SET for d in CAL])
H0 = int(datetime(2020, 11, 30, tzinfo=timezone.utc).timestamp()) // 3600
OFF = np.array([int(datetime.fromtimestamp((H0 + i) * 3600, CT).utcoffset().total_seconds()) for i in range((len(CAL) + 2) * 24)], dtype=np.int64) * NS
SES_LO, SES_HI = (8 * 3600 + 30 * 60) * NS, (13 * 3600 + 20 * 60) * NS

def process(path: Path) -> dict:
    guard34.check(path)
    store = db.DBNStore.from_file(path)
    arr = store.to_ndarray()
    te = arr["ts_event"].astype(np.int64); iid = arr["instrument_id"].astype(np.int64); rt = arr["rtype"].astype(np.int64)
    guard34.check_ts(te, path.name)
    out = {"file": path.name, "records": int(len(te)), "rtypes": {str(k): int(v) for k, v in zip(*np.unique(rt, return_counts=True))},
           "ts_event_decreases": int(np.count_nonzero(np.diff(te) < 0)),
           "duplicate_ts_event_iid": int(len(te) - len(np.unique(te * 1_000_003 + iid)))}
    meta = store.metadata
    out["metadata"] = json.loads(json.dumps({"version": meta.version, "dataset": meta.dataset, "schema": str(meta.schema), "stype_in": str(meta.stype_in),
                       "stype_out": str(meta.stype_out), "start": str(meta.start), "end": str(meta.end), "symbols": list(meta.symbols),
                       "mappings": {k: [dict(v) if hasattr(v, "keys") else v for v in vs] for k, vs in meta.mappings.items()}}, default=str))
    cidx = np.searchsorted(WIN_LO, te, side="right") - 1
    ok = IS_TD[cidx]
    out["outside_trade_dates"] = int(np.count_nonzero(~ok))
    tod = (te + OFF[(te // (3600 * NS)) - H0]) % DAY_NS
    ses = ((tod >= SES_LO) & (tod < SES_HI))
    days = {}
    for ci in np.unique(cidx[ok]):
        m = ok & (cidx == ci)
        ids, c = np.unique(iid[m], return_counts=True)
        days[CAL[ci].isoformat()] = {"bars": int(m.sum()), "ses": int((m & ses).sum()),
                                    "iid": {str(a): int(b) for a, b in zip(ids, c)}}
    out["per_day"] = days
    return out

def main() -> None:
    for root in ("ZL", "ZS", "ZM"):
        for p in sorted(guard34.OHLCV[root].glob("range=*.dbn.zst")):
            real = p.resolve()
            if str(real) not in guard34.ALLOWED:
                continue
            out = OUT / f"{root}_{p.name}.json"
            if out.exists(): continue
            res = process(p); res["root"] = root
            out.write_text(json.dumps(res))
        print(root, "done", flush=True)
main()
