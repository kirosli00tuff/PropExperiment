"""Stage E.31 canary check (spec v2 section 9; SpecReviewer pass 1 item 3): structure only.

    canary_check31.py [--month YYYY-MM ...] [--chunk-records N]

Run from the repo root as ``uv run python reports/stage_e31_briefs/work/pilot/canary_check31.py``
at nice 10 (README31.md). Default months: 2024-01 and 2024-02. Reads the purchased files of those
months (pilot31_common.target_path) and writes runs/canary31.json and runs/canary31.md.

Per month:
- Z4 (definitions): for the ZM, ZS and ZL outrights (instrument_class F): match_algorithm,
  min_price_increment, min_price_increment_amount, unit_of_measure_qty as found. Findings: a
  match algorithm other than K; ZM's tick not 0.10; a root with more than one tick; tick x the
  contract size (100 short tons, 5,000 bu, 60,000 lb) not 10.00, 12.50, 6.00 USD (prices in
  USD) or 1000, 1250, 600 (prices in US cents); a stated unit_of_measure_qty that disagrees.
  min_price_increment_amount is reported as found, as a note (lead, 2026-10-23: the engine
  uses min_price_increment x unit_of_measure_qty, ZS and ZL in cents). Also the
  instrument_id -> raw_symbol map for Z1.
- Z1 (MBO): the v.0/v.1 instrument mapping per UTC date from the DBN metadata; the snapshot
  presence table, every UTC weekday 00:00Z inside the request x each instrument mapped that
  date (an R record flagged F_SNAPSHOT, ts_recv within 60 s after the midnight, with its A
  record count and F_LAST); counts of T and F records; and whether every T is followed (in
  its instrument's records, file order) by F records summing to its size or less. Findings: a
  missing snapshot cell; a T with no F after it; F records summing above their T's size; F
  records that follow no T. Info only (no finding): the same records grouped as T runs (one or
  more consecutive T, then the F records right after them), with the F sum against the run's T
  sum (equal, twice, below, above, no F).
- Z2, Z3 (MBP-1): record counts per grains trade date (data.group_session.assign_trade_dates:
  in session, or before the session they are booked to). Finding: a trade date of the month
  with no in-session record.

It computes no fill, markout, spread statistic or price summary: it never reads a price field
of an MBO or MBP-1 record, and only the tick fields of the definitions. Exit codes: 0 the
structure holds (no finding); 3 findings (listed in both outputs); 2 refused (a month outside
the plan, a missing file), nothing opened.
"""
# ruff: noqa: I001 - pilot31_common is imported first on purpose (sys.path)

from __future__ import annotations

import argparse
import contextlib
import json
import os
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np

import pilot31_common as pc  # first: puts the repo root on sys.path
import verify31 as vf

from data.group_session import (  # noqa: E402
    assign_trade_dates,
    open_intervals,
    trade_dates_between,
)

RUNS_DIR = Path(__file__).resolve().parent / "runs"
JSON_FILE = "canary31.json"
MD_FILE = "canary31.md"
DEFAULT_MONTHS = ("2024-01", "2024-02")
PRICE_SCALE = 1_000_000_000  # DBN fixed-point prices: 1e-9
UNDEF_PRICE = 2**63 - 1
EXPECTED_MATCH_ALGORITHM = "K"
EXPECTED: dict[str, dict[str, Any]] = {  # spec section 0
    "ZM": {"contract_size": 100, "tick": 0.10, "tick_usd": 10.00},
    "ZS": {"contract_size": 5000, "tick": None, "tick_usd": 12.50},
    "ZL": {"contract_size": 60000, "tick": None, "tick_usd": 6.00},
}
MAX_EXAMPLES = 10
SCOPE = "structure only: no fill, markout, spread statistic or price summary is computed"


def _text(value: Any) -> str:
    raw = value.tobytes() if hasattr(value, "tobytes") else value
    if isinstance(raw, bytes):
        return raw.split(b"\x00", 1)[0].decode("ascii", "replace").strip()
    return str(raw).strip()


def _scaled(raw: Any) -> float | None:
    value = int(raw)
    return None if value == UNDEF_PRICE else round(value / PRICE_SCALE, 9)


# ------------------------------------------------------------------ Z4 ----
def definitions(path: Path, chunk_records: int) -> tuple[dict[int, str], dict[str, Any]]:
    """instrument_id -> raw_symbol (every record) and, per root, the outrights' tick fields."""
    import databento  # lazy

    symbols: dict[int, str] = {}
    roots: dict[str, dict[str, Any]] = {r: {"n_outright_records": 0, "outrights": set(),
                                            "match_algorithm": Counter(), "tick": Counter(),
                                            "tick_amount": Counter(), "contract_qty": Counter()}
                                        for r in EXPECTED}
    for chunk in databento.DBNStore.from_file(path).to_ndarray(count=chunk_records):
        for rec in chunk:
            raw = _text(rec["raw_symbol"])
            symbols[int(rec["instrument_id"])] = raw
            root = _text(rec["asset"])
            if root not in roots or _text(rec["instrument_class"]) != "F":
                continue
            row = roots[root]
            row["n_outright_records"] += 1
            row["outrights"].add(raw)
            row["match_algorithm"][_text(rec["match_algorithm"])] += 1
            row["tick"][_scaled(rec["min_price_increment"])] += 1
            row["tick_amount"][_scaled(rec["min_price_increment_amount"])] += 1
            row["contract_qty"][_scaled(rec["unit_of_measure_qty"])] += 1
    return symbols, roots


def tick_findings(root: str, row: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    exp, out = EXPECTED[root], []
    if row["n_outright_records"] == 0:
        return {"root": root, "found": False}, [f"{root}: no outright definition found"]
    algos = sorted(row["match_algorithm"])
    if algos != [EXPECTED_MATCH_ALGORITHM]:
        out.append(f"{root}: outright match_algorithm {algos}, expected "
                   f"{EXPECTED_MATCH_ALGORITHM}")
    ticks = sorted(t for t in row["tick"] if t is not None)
    summary: dict[str, Any] = {
        "root": root, "found": True, "n_outright_records": row["n_outright_records"],
        "outrights": sorted(row["outrights"]), "match_algorithm": dict(row["match_algorithm"]),
        "min_price_increment": {str(k): v for k, v in row["tick"].items()},
        "min_price_increment_amount": {str(k): v for k, v in row["tick_amount"].items()},
        "unit_of_measure_qty": {str(k): v for k, v in row["contract_qty"].items()},
        "contract_size_spec": exp["contract_size"], "tick_usd_spec": exp["tick_usd"]}
    if len(ticks) != 1:
        return summary, [*out, f"{root}: outright min_price_increment values {ticks}"]
    tick = ticks[0]
    if exp["tick"] is not None and abs(tick - exp["tick"]) > 1e-9:
        out.append(f"{root}: min_price_increment {tick}, expected {exp['tick']}")
    product = round(tick * exp["contract_size"], 6)
    unit = ("USD" if abs(product - exp["tick_usd"]) < 1e-6 else
            "US cents" if abs(product - 100 * exp["tick_usd"]) < 1e-4 else None)
    if unit is None:
        out.append(f"{root}: tick {tick} x contract size {exp['contract_size']} = {product}, "
                   f"neither {exp['tick_usd']} USD nor {100 * exp['tick_usd']} US cents")
    # min_price_increment_amount is reported as found, not checked: the real definitions give
    # 1.0, 1.0 and 0.06 for ZM, ZS and ZL, which is not the USD tick value (canary 2026-10-23)
    qty = sorted(q for q in row["contract_qty"] if q is not None)
    if qty and qty != [float(exp["contract_size"])]:
        out.append(f"{root}: unit_of_measure_qty {qty}, expected {exp['contract_size']}")
    summary.update({"tick": tick, "tick_x_contract_size": product, "price_unit": unit,
                    "tick_usd": None if unit is None else exp["tick_usd"]})
    return summary, out


# ------------------------------------------------------------------ Z1 ----
@dataclass
class _Group:
    head_is_t: bool
    t_size: int
    t_recv: int
    f_sum: int = 0
    f_count: int = 0


@dataclass
class TFPairing:
    """T and F records per instrument, in file order: each T opens a group that the F records
    right after it (in that instrument's records) join; any other action closes it."""

    n_t: int = 0
    n_f: int = 0
    t_without_f: int = 0
    f_sum_equal: int = 0
    f_sum_below: int = 0
    f_sum_above: int = 0
    f_orphans: int = 0
    t_by_side: Counter = field(default_factory=Counter)
    by_instrument: Counter = field(default_factory=Counter)
    examples: list[dict[str, Any]] = field(default_factory=list)
    open: dict[int, _Group] = field(default_factory=dict)

    def _close(self, iid: int, group: _Group) -> None:
        if not group.head_is_t:
            self.f_orphans += group.f_count
            return
        if group.f_count == 0:
            self.t_without_f += 1
        elif group.f_sum == group.t_size:
            self.f_sum_equal += 1
        elif group.f_sum < group.t_size:
            self.f_sum_below += 1
        else:
            self.f_sum_above += 1
        if (group.f_count == 0 or group.f_sum > group.t_size) and \
                len(self.examples) < MAX_EXAMPLES:
            self.examples.append({"instrument_id": iid, "t_ts_recv": pc.iso_ns(group.t_recv),
                                  "t_size": group.t_size, "f_count": group.f_count,
                                  "f_size_sum": group.f_sum})

    def feed(self, iid: int, act: np.ndarray, size: np.ndarray, side: np.ndarray,
             recv: np.ndarray) -> None:
        is_f, is_t = act == b"F", act == b"T"
        self.n_f += int(is_f.sum())
        self.n_t += int(is_t.sum())
        self.by_instrument[f"{iid}:T"] += int(is_t.sum())
        self.by_instrument[f"{iid}:F"] += int(is_f.sum())
        for s, n in Counter(side[is_t].tolist()).items():
            self.t_by_side[_text(s)] += n
        heads = np.flatnonzero(~is_f)
        lead = int(heads[0]) if len(heads) else len(act)
        carry = self.open.pop(iid, None)
        if carry is None:
            self.f_orphans += lead
        else:
            carry.f_sum += int(size[:lead].sum())
            carry.f_count += lead
        if not len(heads):
            if carry is not None:
                self.open[iid] = carry
            return
        if carry is not None:
            self._close(iid, carry)
        rest_f, rest_size = is_f[lead:], size[lead:].astype(np.int64)
        gid = np.cumsum(~rest_f) - 1
        f_sum = np.bincount(gid, weights=np.where(rest_f, rest_size, 0), minlength=len(heads))
        f_cnt = np.bincount(gid, weights=rest_f.astype(np.int64), minlength=len(heads))
        head_t, head_size = is_t[heads], size[heads].astype(np.int64)
        f_sum, f_cnt = f_sum.astype(np.int64), f_cnt.astype(np.int64)
        k = len(heads) - 1  # the last group may continue into the next chunk
        self.open[iid] = _Group(bool(head_t[k]), int(head_size[k]), int(recv[heads[k]]),
                                int(f_sum[k]), int(f_cnt[k]))
        t, t_size, t_sum, t_cnt = head_t[:k], head_size[:k], f_sum[:k], f_cnt[:k]
        self.f_orphans += int(t_cnt[~t].sum())
        with_f = t & (t_cnt > 0)
        self.t_without_f += int((t & (t_cnt == 0)).sum())
        self.f_sum_equal += int((with_f & (t_sum == t_size)).sum())
        self.f_sum_below += int((with_f & (t_sum < t_size)).sum())
        self.f_sum_above += int((with_f & (t_sum > t_size)).sum())
        bad = np.flatnonzero(t & ((t_cnt == 0) | (t_sum > t_size)))
        for j in bad[:max(0, MAX_EXAMPLES - len(self.examples))].tolist():
            self.examples.append({"instrument_id": iid,
                                  "t_ts_recv": pc.iso_ns(int(recv[heads[j]])),
                                  "t_size": int(t_size[j]), "f_count": int(t_cnt[j]),
                                  "f_size_sum": int(t_sum[j])})

    def finish(self) -> None:
        for iid, group in sorted(self.open.items()):
            self._close(iid, group)
        self.open = {}

    def summary(self) -> dict[str, Any]:
        return {"n_T": self.n_t, "n_F": self.n_f, "T_without_F": self.t_without_f,
                "T_F_sum_equal_size": self.f_sum_equal, "T_F_sum_below_size": self.f_sum_below,
                "T_F_sum_above_size": self.f_sum_above, "F_without_T": self.f_orphans,
                "T_by_side": dict(self.t_by_side), "by_instrument": dict(self.by_instrument),
                "examples": self.examples}


@dataclass
class _Run:
    t_sum: int = 0
    t_cnt: int = 0
    f_sum: int = 0
    f_cnt: int = 0
    last_is_t: bool = False


@dataclass
class TFRuns:
    """Info only: per instrument in file order, a run is one or more consecutive T records and
    the F records right after them; any other action closes it."""

    counts: Counter = field(default_factory=Counter)
    open: dict[int, _Run] = field(default_factory=dict)

    def _tally(self, t_cnt: np.ndarray, t_sum: np.ndarray, f_cnt: np.ndarray,
               f_sum: np.ndarray) -> None:
        run = t_cnt > 0
        with_f = run & (f_cnt > 0)
        self.counts["runs"] += int(run.sum())
        self.counts["runs_with_several_T"] += int((t_cnt > 1).sum())
        self.counts["runs_without_F"] += int((run & (f_cnt == 0)).sum())
        self.counts["F_sum_equal_T_sum"] += int((with_f & (f_sum == t_sum)).sum())
        self.counts["F_sum_twice_T_sum"] += int((with_f & (f_sum == 2 * t_sum)).sum())
        self.counts["F_sum_below_T_sum"] += int((with_f & (f_sum < t_sum)).sum())
        self.counts["F_sum_above_T_sum_not_twice"] += int(
            (with_f & (f_sum > t_sum) & (f_sum != 2 * t_sum)).sum())

    def feed(self, iid: int, act: np.ndarray, size: np.ndarray) -> None:
        is_f, is_t = act == b"F", act == b"T"
        n, carry = len(act), self.open.pop(iid, None)
        prev_t = np.empty(n, dtype=bool)
        prev_t[0] = carry.last_is_t if carry is not None else False
        prev_t[1:] = is_t[:-1]
        head_mask = (is_t & ~prev_t) | (~is_t & ~is_f)
        heads = np.flatnonzero(head_mask)
        lead = int(heads[0]) if len(heads) else n
        if carry is not None:
            carry.t_sum += int(size[:lead][is_t[:lead]].sum())
            carry.t_cnt += int(is_t[:lead].sum())
            carry.f_sum += int(size[:lead][is_f[:lead]].sum())
            carry.f_cnt += int(is_f[:lead].sum())
            carry.last_is_t = bool(is_t[n - 1]) if lead == n else carry.last_is_t
        if not len(heads):
            if carry is not None:
                self.open[iid] = carry
            return
        if carry is not None:
            self._tally(*(np.array([v]) for v in (carry.t_cnt, carry.t_sum, carry.f_cnt,
                                                  carry.f_sum)))
        gid = np.cumsum(head_mask[lead:]) - 1
        sz = size[lead:].astype(np.int64)
        t, f = is_t[lead:], is_f[lead:]
        k = len(heads)
        sums = [np.bincount(gid, weights=w, minlength=k).astype(np.int64)
                for w in (t.astype(np.int64), np.where(t, sz, 0), f.astype(np.int64),
                          np.where(f, sz, 0))]
        t_cnt, t_sum, f_cnt, f_sum = sums
        self._tally(t_cnt[:-1], t_sum[:-1], f_cnt[:-1], f_sum[:-1])
        self.open[iid] = _Run(int(t_sum[-1]), int(t_cnt[-1]), int(f_sum[-1]), int(f_cnt[-1]),
                              bool(is_t[n - 1]))

    def finish(self) -> dict[str, int]:
        for run in self.open.values():
            self._tally(*(np.array([v]) for v in (run.t_cnt, run.t_sum, run.f_cnt,
                                                  run.f_sum)))
        self.open = {}
        return dict(self.counts)


def _snapshot_parts(chunk: np.ndarray, clears: Counter, adds: Counter, last: Counter) -> int:
    flags = chunk["flags"].astype(np.uint16)
    snap = (flags & vf.F_SNAPSHOT) != 0
    if not snap.any():
        return 0
    recv = chunk["ts_recv"][snap].astype(np.int64)
    mid = recv - recv % vf.DAY_NS
    near = (recv - mid) < vf.SNAPSHOT_TOLERANCE_NS
    act, iid = chunk["action"][snap], chunk["instrument_id"][snap].astype(np.int64)
    is_last = (flags[snap] & 128) != 0
    off = 0
    for m, a, i, ok, fl in zip(mid.tolist(), act.tolist(), iid.tolist(), near.tolist(),
                               is_last.tolist(), strict=True):
        if not ok:
            off += a == b"R"
            continue
        if a == b"R":
            clears[(m, i)] += 1
        elif a == b"A":
            adds[(m, i)] += 1
        if fl:
            last[(m, i)] += 1
    return off


def mapping_table(hdr: dict[str, Any], item: pc.Planned, symbols: dict[int, str]
                  ) -> list[dict[str, Any]]:
    start = pc.parse_utc(item.params.start).date()
    end = pc.parse_utc(item.params.end).date()
    rows = []
    for n in range((end - start).days + 1):
        day = start + timedelta(days=n)
        mapped = vf.mapped_on(hdr, day)
        rows.append({"date": day.isoformat(), **{
            sym: [{"instrument_id": i, "raw_symbol": symbols.get(i)} for i in ids]
            for sym, ids in mapped.items()}})
    return rows


def check_z1(path: Path, item: pc.Planned, symbols: dict[int, str], chunk_records: int
             ) -> tuple[dict[str, Any], list[str]]:
    import databento  # lazy

    store = databento.DBNStore.from_file(path)
    hdr = vf.header(store.metadata)
    clears: Counter = Counter()
    adds: Counter = Counter()
    last: Counter = Counter()
    pairing, runs, off_midnight, records = TFPairing(), TFRuns(), 0, 0
    for chunk in store.to_ndarray(count=chunk_records):
        records += len(chunk)
        off_midnight += _snapshot_parts(chunk, clears, adds, last)
        iid = chunk["instrument_id"].astype(np.int64)
        for u in np.unique(iid).tolist():
            m = iid == u
            act, size = chunk["action"][m], chunk["size"][m]
            pairing.feed(u, act, size, chunk["side"][m], chunk["ts_recv"][m].astype(np.int64))
            runs.feed(u, act, size)
    pairing.finish()
    scan = vf.Scan(snapshot_clears=clears)
    start_ns, end_ns = pc.bound_ns(item.params.start), pc.bound_ns(item.params.end)
    table = vf.snapshot_table(scan, hdr, start_ns, end_ns)
    for row in table:
        key = (row["midnight_ns"], row["instrument_id"])
        row.update({"raw_symbol": symbols.get(row["instrument_id"]),
                    "snapshot_adds": adds.get(key, 0), "f_last": last.get(key, 0) > 0})
    findings = [f"Z1 {item.month_label}: no snapshot at {r['midnight']} for {r['symbol']} "
                f"(instrument {r['instrument_id']})" for r in table
                if r["instrument_id"] is None or r["snapshot_clears"] == 0]
    tf = pairing.summary()
    for name, label in (("T_without_F", "T records with no F after them"),
                        ("T_F_sum_above_size", "T records whose F sizes sum above the T size"),
                        ("F_without_T", "F records that follow no T")):
        if tf[name]:
            findings.append(f"Z1 {item.month_label}: {tf[name]} {label}")
    mapped_ids = {r["instrument_id"] for r in table}
    extra = sorted({f"{pc.iso_ns(m)}:{i}" for (m, i) in clears if i not in mapped_ids})
    return {"path": str(path), "records": records, "mapping": mapping_table(hdr, item, symbols),
            "snapshots": table, "snapshot_clears_unmapped_instrument": extra[:50],
            "snapshot_clears_off_midnight": off_midnight, "t_f": tf,
            "t_runs_info": runs.finish()}, findings


# ------------------------------------------------------------------ Z2, Z3 ----
def check_daily(path: Path, item: pc.Planned, chunk_records: int
                ) -> tuple[dict[str, Any], list[str]]:
    import databento  # lazy

    cal = pc.calendar_for(item.series.roots[0])
    first, last = item.month, pc.last_day(item.month)
    opened = open_intervals(cal, first, last)
    inside, before = Counter(), Counter()
    unassigned = records = 0
    for chunk in databento.DBNStore.from_file(path).to_ndarray(count=chunk_records):
        records += len(chunk)
        got = assign_trade_dates(opened, chunk["ts_event"].astype(np.int64))
        nat = np.isnat(got.days)
        unassigned += int(nat.sum())
        for mask, counter in ((~got.in_closure & ~nat, inside), (got.in_closure & ~nat, before)):
            days, counts = np.unique(got.days[mask], return_counts=True)
            for d, n in zip(days.tolist(), counts.tolist(), strict=True):
                counter[d.isoformat()] += n
    rows = [{"trade_date": d.isoformat(), "in_session": inside.get(d.isoformat(), 0),
             "before_session": before.get(d.isoformat(), 0)}
            for d in trade_dates_between(cal, first, last)]
    findings = [f"{item.label}: no in-session record on trade date {r['trade_date']}"
                for r in rows if r["in_session"] == 0]
    return {"path": str(path), "records": records, "per_trade_date": rows,
            "after_the_last_session": unassigned}, findings


# ------------------------------------------------------------------ outputs ----
def _md(report: dict[str, Any]) -> str:
    lines = ["# Stage E.31 canary check (structure only)", "",
             f"Written {report['written']}. {SCOPE}. Exit code {report['exit_code']}.", "",
             "## Findings", ""]
    lines += [f"- {f}" for f in report["findings"]] or ["- none: the structure holds"]
    lines += ["", "## Notes (not findings)", ""] + ([f"- {n}" for n in report["notes"]]
                                                   or ["- none"])
    for month, m in report["months"].items():
        lines += ["", f"## {month}", "", "### Z4 outrights", "",
                  "| root | match_algorithm | tick | tick x size | unit | tick USD | outrights |",
                  "|---|---|---|---|---|---|---|"]
        for s in m["Z4"]["roots"]:
            lines.append(f"| {s['root']} | {s.get('match_algorithm')} | {s.get('tick')} | "
                         f"{s.get('tick_x_contract_size')} | {s.get('price_unit')} | "
                         f"{s.get('tick_usd')} | {len(s.get('outrights', []))} |")
        z1 = m["Z1"]
        miss = [r for r in z1["snapshots"] if not r["snapshot_clears"]]
        lines += ["", "### Z1", "", f"- records {z1['records']:,}; snapshot cells "
                  f"{len(z1['snapshots'])}, missing {len(miss)}; T/F: "
                  + ", ".join(f"{k} {v}" for k, v in z1["t_f"].items()
                              if not isinstance(v, dict | list)),
                  "- T runs (info only): " + ", ".join(
                      f"{k} {v}" for k, v in sorted(z1["t_runs_info"].items())), "",
                  "| midnight | symbol | instrument | raw | clear | adds | F_LAST |",
                  "|---|---|---|---|---|---|---|"]
        for r in z1["snapshots"]:
            lines.append(f"| {r['midnight'][:10]} | {r['symbol']} | {r['instrument_id']} | "
                         f"{r['raw_symbol']} | {'yes' if r['snapshot_clears'] else 'MISSING'} | "
                         f"{r['snapshot_adds']} | {'yes' if r['f_last'] else 'no'} |")
        for name in ("Z2", "Z3"):
            rows = m[name]["per_trade_date"]
            lines += ["", f"### {name} records per trade date", "",
                      "| trade date | in session | before session |", "|---|---|---|"]
            lines += [f"| {r['trade_date']} | {r['in_session']:,} | {r['before_session']:,} |"
                      for r in rows]
    return "\n".join(lines) + "\n"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def _items(months: list[str]) -> dict[str, dict[str, pc.Planned]]:
    out = {}
    for label in months:
        month = pc.parse_month(label)
        out[f"{month:%Y-%m}"] = {s.name: pc.Planned(s, month, pc.check_request(
            pc.request_for(s, month))) for s in pc.SERIES}
    return out


def check_month(items: dict[str, pc.Planned], vendor_root: Path, chunk_records: int
                ) -> tuple[dict[str, Any], list[str]]:
    path = {name: pc.target_path(item, vendor_root) for name, item in items.items()}
    symbols, roots = definitions(path["Z4"], chunk_records)
    summaries, findings, notes = [], [], []
    for root, row in roots.items():
        summary, found = tick_findings(root, row)
        summaries.append(summary)
        findings += [f"Z4 {items['Z4'].month_label}: {f}" for f in found]
        amounts = sorted(k for k in summary.get("min_price_increment_amount", {}) if k != "None")
        if amounts:
            notes.append(f"Z4 {items['Z4'].month_label}: {root} min_price_increment_amount "
                         f"{amounts} as found (not checked: not the USD tick value, and the "
                         "engine uses min_price_increment x unit_of_measure_qty)")
    z1, f1 = check_z1(path["Z1"], items["Z1"], symbols, chunk_records)
    out: dict[str, Any] = {"Z4": {"path": str(path["Z4"]), "roots": summaries}, "Z1": z1,
                           "notes": notes}
    findings += f1
    for name in ("Z2", "Z3"):
        out[name], found = check_daily(path[name], items[name], chunk_records)
        findings += found
    return out, findings


def main(argv: list[str] | None = None, *, vendor_root: Path = pc.PILOT_VENDOR_ROOT,
         runs_dir: Path = RUNS_DIR) -> int:
    ap = argparse.ArgumentParser(prog="canary_check31.py", description=__doc__.split("\n\n")[0])
    ap.add_argument("--month", action="append", help="YYYY-MM (repeat); default 2024-01, 2024-02")
    ap.add_argument("--chunk-records", type=int, default=vf.DEFAULT_CHUNK_RECORDS)
    args = ap.parse_args(argv)
    try:
        plan = _items(args.month or list(DEFAULT_MONTHS))
        missing = [str(pc.target_path(i, vendor_root)) for m in plan.values() for i in m.values()
                   if not pc.target_path(i, vendor_root).is_file()]
        if missing:
            raise pc.PilotRefused(f"{len(missing)} purchased file(s) missing: {missing[:4]}")
    except pc.PilotRefused as exc:
        print(f"REFUSED, nothing opened: {exc}", file=sys.stderr)
        return pc.RC_REFUSED
    with contextlib.suppress(OSError):  # a long read: low priority (CLAUDE.md limits)
        os.nice(10)
    months, findings = {}, []
    for label, items in plan.items():
        months[label], found = check_month(items, Path(vendor_root), args.chunk_records)
        findings += found
    code = pc.RC_QUALITY if findings else pc.RC_OK
    notes = [n for m in months.values() for n in m["notes"]]
    report = {"scope": SCOPE, "months": months, "findings": findings, "notes": notes,
              "exit_code": code,
              "written": datetime.now(pc.PT).isoformat(timespec="seconds"),
              "written_utc": datetime.now(UTC).isoformat(timespec="seconds")}
    runs_dir = Path(runs_dir)
    _write(runs_dir / JSON_FILE, json.dumps(report, indent=1, default=str) + "\n")
    _write(runs_dir / MD_FILE, _md(report))
    print(f"canary_check31: exit {code}; {len(findings)} finding(s): "
          f"{findings[:6] or 'none'}{' ...' if len(findings) > 6 else ''}; wrote "
          f"{runs_dir / JSON_FILE} and {runs_dir / MD_FILE}")
    return code


if __name__ == "__main__":
    sys.exit(main())
