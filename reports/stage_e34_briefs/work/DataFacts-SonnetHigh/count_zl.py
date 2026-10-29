"""Per-file counts of the owned ZL MBP-1 front-month files (fields read: ts_recv, ts_event, action, side,
flags, instrument_id only; no price or size field is indexed; no record printed).
Trade date D = E.33 rule: ts_recv in [D-1 16:00 CT, D 16:00 CT) (data33.window); D kept only if D is one of
the 816 calendar trade dates (trade_dates_e33rule.json); other records are counted as 'outside'.
Segment: day session = ts_recv CT time-of-day in [08:30, 13:20); 'rest' = everything else.
Resumable: counts/zl_<month>.json is skipped when present. Usage: count_zl.py [month ...]
"""
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

CT = ZoneInfo("America/Chicago")
NS = 1_000_000_000
OUT = HERE / "counts"; OUT.mkdir(exist_ok=True)
TD = [date.fromisoformat(x) for x in json.loads((HERE / "trade_dates_e33rule.json").read_text())]
TD_SET = set(TD)
# calendar days D covering every possible record: window start ns of each calendar day
CAL0, CAL1 = date(2020, 11, 30), date(2024, 3, 2)
CAL = [CAL0 + timedelta(days=i) for i in range((CAL1 - CAL0).days + 1)]
def ct_ns(d: date, h: int) -> int:
    return int(datetime(d.year, d.month, d.day, h, tzinfo=CT).timestamp()) * NS
WIN_LO = np.array([ct_ns(d - timedelta(days=1), 16) for d in CAL], dtype=np.int64)  # window start of D
TD_IDX = np.array([CAL.index(d) if d in TD_SET else -1 for d in CAL], dtype=np.int64)  # cal idx -> flag
IS_TD = np.array([d in TD_SET for d in CAL])
# CT UTC offset per UTC hour
H0 = int(datetime(2020, 11, 30, tzinfo=timezone.utc).timestamp()) // 3600
NH = (len(CAL) + 2) * 24
OFF = np.array([int(datetime.fromtimestamp((H0 + i) * 3600, CT).utcoffset().total_seconds()) for i in range(NH)],
               dtype=np.int64) * NS
DAY_NS = 86400 * NS
SES_LO, SES_HI = (8 * 3600 + 30 * 60) * NS, (13 * 3600 + 20 * 60) * NS
ACT = [ord(c) for c in "ACMRTFN"]
FLAGS = {"F_LAST": 128, "F_TOB": 64, "F_SNAPSHOT": 32, "F_MBP": 16, "F_BAD_TS_RECV": 8, "F_MAYBE_BAD_BOOK": 4}


def as_u8(a: np.ndarray) -> np.ndarray:
    return a.view(np.uint8) if a.dtype.kind == "S" else a.astype(np.uint8, copy=False)


def process(path: Path, month: str) -> dict:
    guard34.check(path)
    store = db.DBNStore.from_file(path)
    hour_all = np.zeros(24, dtype=np.int64); hour_T = np.zeros(24, dtype=np.int64)
    tot = defaultdict(int); day_act = defaultdict(int); day_iid = defaultdict(int)
    flags = defaultdict(int); side = defaultdict(int); act_tot = defaultdict(int)
    last_ts = None; t0 = time.time(); n = 0
    for chunk in store.to_ndarray(count=1_000_000):
        if len(chunk) == 0:
            continue
        tr = chunk["ts_recv"].astype(np.int64); te = chunk["ts_event"].astype(np.int64)
        guard34.check_ts(tr, str(path.name))
        a = as_u8(chunk["action"]); s = as_u8(chunk["side"]); fl = as_u8(chunk["flags"])
        iid = chunk["instrument_id"].astype(np.int64)
        n += len(tr)
        tot["ts_recv_decreases"] += int(np.count_nonzero(np.diff(tr) < 0)) + (int(last_ts is not None and tr[0] < last_ts))
        last_ts = int(tr[-1])
        tot["ts_event_after_ts_recv"] += int(np.count_nonzero(te > tr))
        tot["ts_event_before_ts_recv_by_over_1s"] += int(np.count_nonzero(tr - te > NS))
        tot["ts_event_before_ts_recv_by_over_1d"] += int(np.count_nonzero(tr - te > DAY_NS))
        tot["ts_event_undef"] += int(np.count_nonzero(te == 2**63 - 1)) 
        for name, bit in FLAGS.items():
            flags[name] += int(np.count_nonzero(fl & bit))
        for v, c in zip(*np.unique(s, return_counts=True)):
            side[chr(int(v))] += int(c)
        for v, c in zip(*np.unique(a, return_counts=True)):
            act_tot[chr(int(v))] += int(c)
        cidx = np.searchsorted(WIN_LO, tr, side="right") - 1          # calendar index of D
        ok = IS_TD[cidx]
        tot["outside_trade_dates"] += int(np.count_nonzero(~ok))
        hours = (tr // (3600 * NS)) - H0
        tod = (tr + OFF[hours]) % DAY_NS
        hr = (tod // (3600 * NS)).astype(np.int64)
        hour_all += np.bincount(hr, minlength=24); hour_T += np.bincount(hr[a == ord('T')], minlength=24)
        seg = ((tod >= SES_LO) & (tod < SES_HI)).astype(np.int64)
        # key: cal idx, action index (0..7), seg
        aidx = np.full(len(a), 7, dtype=np.int64)
        for k, code in enumerate(ACT):
            aidx[a == code] = k
        key = ((cidx * 8 + aidx) * 2 + seg)[ok]
        u, c = np.unique(key, return_counts=True)
        for kk, cc in zip(u.tolist(), c.tolist()):
            day_act[kk] += cc
        key2 = (cidx * (1 << 32) + iid)[ok]
        u, c = np.unique(key2, return_counts=True)
        for kk, cc in zip(u.tolist(), c.tolist()):
            day_iid[kk] += cc
    days = {}
    for kk, cc in day_act.items():
        rest, sg = divmod(kk, 2); ci, ai = divmod(rest, 8)
        d = CAL[ci].isoformat()
        days.setdefault(d, {}).setdefault("ACMRTFNX"[ai], [0, 0])[sg] += cc
    iids = {}
    for kk, cc in day_iid.items():
        ci, ii = divmod(kk, 1 << 32)
        iids.setdefault(CAL[ci].isoformat(), {})[str(ii)] = cc
    meta = store.metadata
    return {"month": month, "file": path.name, "records": n, "seconds": round(time.time() - t0, 1),
            "metadata": {"version": meta.version, "dataset": meta.dataset, "schema": str(meta.schema),
                         "stype_in": str(meta.stype_in), "stype_out": str(meta.stype_out),
                         "start": str(meta.start), "end": str(meta.end), "symbols": list(meta.symbols),
                         "limit": meta.limit, "ts_out": meta.ts_out},
            "dtypes": {k: str(v[0]) for k, v in store.to_ndarray(count=1).__next__().dtype.fields.items()}
                      if False else None,
            "hour_ct_all": hour_all.tolist(), "hour_ct_T": hour_T.tolist(), "tot": dict(tot), "flags": dict(flags), "side": dict(side), "action_total": dict(act_tot),
            "per_day_action_by_seg": days,   # {D: {action: [rest, day_session]}}
            "per_day_instrument": iids}


def main(months: list[str]) -> None:
    files = sorted(guard34.MBP1_DIR.glob("range=*.dbn.zst"))
    man = json.loads((HERE / "manifest_facts.json").read_text())
    z3 = {f["name"]: f["month"] for f in man["files"] if f["series"] == "Z3"}
    for p in files:
        month = z3[p.name]
        if months and month not in months:
            continue
        out = OUT / f"zl_{month}.json"
        if out.exists():
            print("skip", month); continue
        res = process(p, month)
        out.write_text(json.dumps(res))
        print(month, res["records"], res["seconds"], "s", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
