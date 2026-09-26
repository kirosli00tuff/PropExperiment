"""Calibrate the Stage E per-product slippage tables from the mbp-1 sample (design D8, Task 8).

    nice -n 10 uv run python -m sim.calibrate_costs run [ROOT ...]   # stream, resumable
    nice -n 10 uv run python -m sim.calibrate_costs build             # frozen table + report

``run`` streams each contract's five trade dates of mbp-1 (sha256-verified against the E.1
manifest before decoding) and writes one line per contract of raw, exact time-weighted
histograms to the scratch JSONL; a restart skips contracts already there. ``build`` applies the
D8 rule (``sim.cost_rule``) to those lines and writes reports/stage_e2a_costs.{json,md}
(``sim.cost_report``). MES's model (sim/costs.py, sim/fill_model.py, sim/slippage_calibration.json)
is not touched.

Method, stated once (the template is sim/calibrate_slippage.py, D.1's MES calibration):
- Time axis: ``ts_recv`` (Databento's capture time, monotone within a file; the E.1 files are
  selected by it). Every record carries the full top of book after its event; the book state it
  gives lasts from its ``ts_recv`` until the next record's ``ts_recv`` (exact time weighting, no
  sampling grid). Records sharing a ``ts_recv`` give zero-length states except the last.
- Gaps: a quiet book produces no records, so a state simply persists; there is no gap inference
  inside a stream. The state is UNKNOWN (not counted) before the trade date's first record and
  after the last file's request end (which is the session end, so this never cuts open time).
  The MNQ trade dates split into three contiguous request pieces are streamed as one stream.
- The first state of a bucket is the state carried in from the last record before the bucket
  starts (the book is standing), whether that record fell in the previous bucket or in a closed
  window; the 1-second reopen grace after every closure keeps a pre-open or auction state out.
- Open time: the group calendar's segments for the trade date (``data.group_session``), minus a
  1-second reopen-auction grace at every segment start (as sim/calibrate_slippage.py), split at
  CT clock half-hours; a partial half-hour at a segment edge is its own bucket, keyed by its CT
  start. Everything else (the daily maintenance hour, the grain pause 07:45-08:30 CT, a group's
  closed hours) is excluded.
- Books: empty (a side missing or zero size), locked (ask = bid) and crossed (ask < bid) states
  are dropped and counted (records and nanoseconds, per bucket and date). A valid state
  contributes its spread (ask - bid) in vendor ticks and its bid and ask top sizes, each
  weighted by its duration in nanoseconds (exact integer histograms).
- Continuous-contract switch: RB's v.0 changes instrument at a UTC midnight on three dates; the
  new instrument's first record is Databento's midnight snapshot, so the old state ends exactly
  there. Any other instrument change is refused.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections import Counter
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path

import numpy as np

from data.calendars import GROUP_OF_PRODUCT
from data.config import REPO_ROOT
from data.group_session import GroupCalendar, load_group_calendar, session_intervals
from data.session import CME_TZ, ct_ns
from sim.cost_inputs import BUCKET_MINUTES, SAMPLE_DATES, TickSpec, load_ticks, mbp1_files

NS = 1_000_000_000
REOPEN_GRACE_NS = 1 * NS  # as sim/calibrate_slippage.py REOPEN_GRACE_S
NULL_PRICE = 9_223_372_036_854_775_807
F_SNAPSHOT = 32
F_BAD_TS_RECV = 8
F_MAYBE_BAD_BOOK = 4
CHUNK_RECORDS = 1_000_000
KEY_SHIFT = 1 << 32
INT64_MIN = -(1 << 63)

VALID, EMPTY, LOCKED, CROSSED = 0, 1, 2, 3
CLASS_NAMES = ("valid", "empty", "locked", "crossed")

SCRATCH_DIR = Path(os.environ.get(
    "E2A_COSTS_SCRATCH",
    "/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/"
    "ee707266-bbda-4ccb-84dc-81ce0d628d05/scratchpad/costs"))
RAW_PREFIX = "calibration_raw"  # one JSONL per run tag: calibration_raw[_<tag>].jsonl


class CalibrationError(RuntimeError):
    """The data or the calendar do not allow the D8 quantity to be computed as stated."""


# ------------------------------------------------------------------ buckets ----
@dataclass(frozen=True)
class Piece:
    """One bucket's open time on one trade date: [start_ns, end_ns) UTC."""

    key: str  # CT "HH:MM" of the bucket's wall-clock start
    start_ns: int  # after the reopen grace for a segment's first piece
    end_ns: int
    start_min: int  # CT minute of day of the wall-clock start
    end_min: int  # CT minute of day of the end (1440 for midnight)


def _ct_of(ns: int) -> datetime:
    if ns % NS:
        raise CalibrationError(f"segment boundary {ns} is not a whole second")
    return datetime.fromtimestamp(ns // NS, tz=UTC).astimezone(CME_TZ)


def _next_half_hour_ns(local: datetime) -> int:
    minute = (local.hour * 60 + local.minute) // BUCKET_MINUTES * BUCKET_MINUTES + BUCKET_MINUTES
    day = local.date() + timedelta(days=minute // 1440)
    minute %= 1440
    return ct_ns(day, time(minute // 60, minute % 60))


def bucket_pieces(cal: GroupCalendar, day: date, grace_ns: int = REOPEN_GRACE_NS) -> list[Piece]:
    """Trade date ``day``'s open time split into 30-minute CT clock buckets (see module doc)."""
    pieces: list[Piece] = []
    for lo, hi in session_intervals(cal, day):
        cursor = lo
        while cursor < hi:
            local = _ct_of(cursor)
            nxt = min(hi, _next_half_hour_ns(local))
            start = max(cursor, lo + grace_ns)
            end_local = _ct_of(nxt)
            end_min = end_local.hour * 60 + end_local.minute
            start_min = local.hour * 60 + local.minute
            if end_min <= start_min:
                end_min += 1440 if end_min == 0 else 0
            if end_min <= start_min:
                raise CalibrationError(f"{cal.group} {day}: bucket {local} ends at {end_local}")
            if start < nxt:
                pieces.append(Piece(f"{local:%H:%M}", start, nxt, start_min, end_min))
            cursor = nxt
    starts = [p.start_ns for p in pieces]
    if starts != sorted(starts) or any(a.end_ns > b.start_ns
                                         for a, b in zip(pieces, pieces[1:], strict=False)):
        raise CalibrationError(f"{cal.group} {day}: overlapping or unsorted pieces")
    if len({p.key for p in pieces}) != len(pieces):
        raise CalibrationError(f"{cal.group} {day}: two pieces share a CT key")
    return pieces


def region_table(pieces: list[Piece]) -> tuple[np.ndarray, np.ndarray]:
    """Contiguous regions covering the whole time line: (starts, labels); label -1 = closed or
    outside the trade date, else the piece index. Region r is [starts[r], starts[r+1])."""
    starts: list[int] = []
    labels: list[int] = []
    prev_end = INT64_MIN
    for idx, piece in enumerate(pieces):
        if piece.start_ns > prev_end:
            starts.append(prev_end)
            labels.append(-1)
        starts.append(piece.start_ns)
        labels.append(idx)
        prev_end = piece.end_ns
    starts.append(prev_end)
    labels.append(-1)
    return np.array(starts, dtype=np.int64), np.array(labels, dtype=np.int64)


# ------------------------------------------------------------------ accumulator ----
@dataclass
class Chunk:
    """Book records, time-ordered, as plain arrays (the DBN reader or a test builds them)."""

    ts_recv: np.ndarray  # int64 ns
    instrument_id: np.ndarray
    flags: np.ndarray
    bid_px: np.ndarray  # int64 fixed 1e-9
    ask_px: np.ndarray
    bid_sz: np.ndarray  # int64
    ask_sz: np.ndarray

    def __len__(self) -> int:
        return int(self.ts_recv.size)

    @staticmethod
    def concat(a: Chunk, b: Chunk) -> Chunk:
        return Chunk(*(np.concatenate([getattr(a, f), getattr(b, f)]) for f in _FIELDS))

    def tail(self) -> Chunk:
        return Chunk(*(getattr(self, f)[-1:].copy() for f in _FIELDS))


_FIELDS = ("ts_recv", "instrument_id", "flags", "bid_px", "ask_px", "bid_sz", "ask_sz")


def classify(bid: np.ndarray, ask: np.ndarray, bsz: np.ndarray, asz: np.ndarray) -> np.ndarray:
    empty = (bid == NULL_PRICE) | (ask == NULL_PRICE) | (bsz <= 0) | (asz <= 0)
    cls = np.full(bid.shape, VALID, dtype=np.int64)
    cls[~empty & (ask == bid)] = LOCKED
    cls[~empty & (ask < bid)] = CROSSED
    cls[empty] = EMPTY
    return cls


def _hist_add(target: Counter, labels: np.ndarray, values: np.ndarray, weights: np.ndarray
              ) -> None:
    if labels.size == 0:
        return
    if values.min() < 0 or values.max() >= KEY_SHIFT // 2:
        raise CalibrationError(f"histogram value out of range [{values.min()}, {values.max()}]")
    keys = labels * KEY_SHIFT + values
    uniq, inverse = np.unique(keys, return_inverse=True)
    sums = np.bincount(inverse.reshape(-1), weights=weights.astype(np.float64))
    if sums.max() >= 2 ** 53:
        raise CalibrationError("a histogram cell exceeds exact float range")
    for key, ns in zip(uniq.tolist(), np.rint(sums).astype(np.int64).tolist(), strict=True):
        target[(key // KEY_SHIFT, key % KEY_SHIFT)] += ns


@dataclass
class DayAccumulator:
    """Exact time-weighted book statistics of one product and trade date, fed in chunks."""

    pieces: list[Piece]
    vendor_tick: int
    knowledge_end_ns: int
    starts: np.ndarray = field(init=False)
    labels: np.ndarray = field(init=False)
    spread: Counter = field(default_factory=Counter)  # (piece, spread ticks) -> ns
    bid_size: Counter = field(default_factory=Counter)  # (piece, size) -> ns
    ask_size: Counter = field(default_factory=Counter)
    class_ns: np.ndarray = field(init=False)
    class_records: np.ndarray = field(init=False)
    stats: Counter = field(default_factory=Counter)
    instruments: list[int] = field(default_factory=list)
    switches: list[dict] = field(default_factory=list)
    min_spread_ticks: int | None = None
    first_ts: int | None = None
    _carry: Chunk | None = None

    def __post_init__(self) -> None:
        self.starts, self.labels = region_table(self.pieces)
        self.class_ns = np.zeros((len(self.pieces), 4), dtype=np.int64)
        self.class_records = np.zeros((len(self.pieces), 4), dtype=np.int64)

    # -------------------------------------------------------------- feeding ----
    def feed(self, chunk: Chunk) -> None:
        if len(chunk) == 0:
            return
        self.stats["records"] += len(chunk)
        self.stats["snapshot_records"] += int(((chunk.flags & F_SNAPSHOT) != 0).sum())
        self.stats["bad_ts_recv_records"] += int(((chunk.flags & F_BAD_TS_RECV) != 0).sum())
        self.stats["maybe_bad_book_records"] += int(((chunk.flags & F_MAYBE_BAD_BOOK) != 0).sum())
        if self.first_ts is None:
            self.first_ts = int(chunk.ts_recv[0])
            self.instruments.append(int(chunk.instrument_id[0]))
        full = chunk if self._carry is None else Chunk.concat(self._carry, chunk)
        if np.any(np.diff(full.ts_recv) < 0):
            raise CalibrationError("ts_recv regresses inside the stream")
        self._check_switches(full)
        self._intervals(full, full.ts_recv[1:])
        self._carry = full.tail()

    def finish(self) -> None:
        if self._carry is None:
            return
        end = np.array([max(self.knowledge_end_ns, int(self._carry.ts_recv[0]))], dtype=np.int64)
        tail = Chunk(*(np.concatenate([getattr(self._carry, f), getattr(self._carry, f)])
                       for f in _FIELDS))  # a sentinel copy: only the first row is a state
        self._intervals(tail, end)
        self._carry = None

    def _check_switches(self, full: Chunk) -> None:
        change = np.flatnonzero(full.instrument_id[1:] != full.instrument_id[:-1]) + 1
        for idx in change.tolist():
            ts = int(full.ts_recv[idx])
            snap = bool(full.flags[idx] & F_SNAPSHOT)
            if not snap or ts % (86_400 * NS):
                raise CalibrationError(
                    f"instrument changes to {int(full.instrument_id[idx])} at {ts} without a "
                    f"UTC-midnight snapshot")
            self.instruments.append(int(full.instrument_id[idx]))
            self.switches.append({"at_utc": _iso(ts), "from": int(full.instrument_id[idx - 1]),
                                  "to": int(full.instrument_id[idx])})

    def _intervals(self, full: Chunk, ends: np.ndarray) -> None:
        """States full[i] for i < len(ends) last from full.ts_recv[i] to ends[i]."""
        n = ends.size
        a = full.ts_recv[:n]
        bid, ask = full.bid_px[:n], full.ask_px[:n]
        bsz, asz = full.bid_sz[:n], full.ask_sz[:n]
        cls = classify(bid, ask, bsz, asz)
        valid = cls == VALID
        vt = self.vendor_tick
        off = valid & ((bid % vt != 0) | (ask % vt != 0))
        if off.any():
            i = int(np.flatnonzero(off)[0])
            raise CalibrationError(f"{int(off.sum())} valid states off the vendor tick grid {vt}: "
                                   f"first bid {int(bid[i])} ask {int(ask[i])}")
        # scale check (lead, 01:57 PDT): every valid bid and ask lies on the vendor-unit tick
        # grid (else refused above), and some lie off the grid of 10 x that tick
        self.stats["valid_prices_checked"] += 2 * int(valid.sum())
        self.stats["valid_prices_off_10x_grid"] += int(
            ((bid[valid] % (10 * vt)) != 0).sum() + ((ask[valid] % (10 * vt)) != 0).sum())
        spread = np.where(valid, (ask - bid) // vt, 0)
        if valid.any():
            low = int(spread[valid].min())
            self.min_spread_ticks = low if self.min_spread_ticks is None else min(
                self.min_spread_ticks, low)
        ra = np.searchsorted(self.starts, a, side="right") - 1
        lab_a = self.labels[ra]
        inside = lab_a >= 0
        self.class_records += np.bincount(
            lab_a[inside] * 4 + cls[inside], minlength=len(self.pieces) * 4
        ).astype(np.int64).reshape(len(self.pieces), 4)
        self.stats["records_in_closed_time"] += int((~inside).sum())
        dur = ends - a
        pos = dur > 0
        rb = np.searchsorted(self.starts, ends - 1, side="right") - 1
        single = np.flatnonzero(pos & (ra == rb))
        lab_parts = [self.labels[ra[single]]]
        dur_parts = [dur[single]]
        idx_parts = [single]
        multi = np.flatnonzero(pos & (ra != rb))
        if multi.size:
            ml, md, mi = self._split(multi, a, ends, ra, rb)
            lab_parts.append(ml)
            dur_parts.append(md)
            idx_parts.append(mi)
        lab = np.concatenate(lab_parts)
        dd = np.concatenate(dur_parts)
        ii = np.concatenate(idx_parts)
        keep = lab >= 0
        lab, dd, ii = lab[keep], dd[keep], ii[keep]
        if lab.size == 0:
            return
        cell = lab * 4 + cls[ii]
        sums = np.bincount(cell, weights=dd.astype(np.float64), minlength=len(self.pieces) * 4)
        self.class_ns += np.rint(sums).astype(np.int64).reshape(len(self.pieces), 4)
        ok = cls[ii] == VALID
        lab_v, dd_v, ii_v = lab[ok], dd[ok], ii[ok]
        _hist_add(self.spread, lab_v, spread[ii_v], dd_v)
        _hist_add(self.bid_size, lab_v, bsz[ii_v], dd_v)
        _hist_add(self.ask_size, lab_v, asz[ii_v], dd_v)

    def _split(self, multi: np.ndarray, a: np.ndarray, ends: np.ndarray, ra: np.ndarray,
               rb: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        labs: list[int] = []
        durs: list[int] = []
        idxs: list[int] = []
        last = self.starts.size - 1
        for i in multi.tolist():
            lo, hi = int(a[i]), int(ends[i])
            for r in range(int(ra[i]), int(rb[i]) + 1):
                r_lo = int(self.starts[r])
                r_hi = int(self.starts[r + 1]) if r < last else hi
                seg = min(hi, r_hi) - max(lo, r_lo)
                if seg > 0:
                    labs.append(int(self.labels[r]))
                    durs.append(seg)
                    idxs.append(i)
        return (np.array(labs, dtype=np.int64), np.array(durs, dtype=np.int64),
                np.array(idxs, dtype=np.int64))

    # -------------------------------------------------------------- output ----
    def result(self) -> dict:
        buckets: dict[str, dict] = {}
        for idx, piece in enumerate(self.pieces):
            open_ns = piece.end_ns - piece.start_ns
            counted = int(self.class_ns[idx].sum())
            if counted > open_ns:
                raise CalibrationError(f"piece {piece.key}: counted {counted} > open {open_ns}")
            buckets[piece.key] = {
                "start_min": piece.start_min, "end_min": piece.end_min,
                "start_utc": _iso(piece.start_ns), "end_utc": _iso(piece.end_ns),
                "open_ns": open_ns, "unknown_ns": open_ns - counted,
                "class_ns": dict(zip(CLASS_NAMES, self.class_ns[idx].tolist(), strict=True)),
                "class_records": dict(zip(CLASS_NAMES, self.class_records[idx].tolist(),
                                          strict=True)),
                "spread_ticks_ns": _hist_of(self.spread, idx),
                "bid_size_ns": _hist_of(self.bid_size, idx),
                "ask_size_ns": _hist_of(self.ask_size, idx),
            }
        return {"buckets": buckets, "stats": dict(self.stats),
                "first_ts_recv_utc": None if self.first_ts is None else _iso(self.first_ts),
                "knowledge_end_utc": _iso(self.knowledge_end_ns),
                "instruments": self.instruments, "instrument_switches": self.switches,
                "min_spread_ticks": self.min_spread_ticks}


def _hist_of(counter: Counter, idx: int) -> dict[str, int]:
    return {str(v): ns for (lab, v), ns in sorted(counter.items()) if lab == idx and ns > 0}


def _iso(ns: int) -> str:
    sec, frac = divmod(int(ns), NS)
    return datetime.fromtimestamp(sec, tz=UTC).strftime("%Y-%m-%dT%H:%M:%S") + f".{frac:09d}Z"


# ------------------------------------------------------------------ files ----
def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _utc_ns(text: str) -> int:
    stamp = datetime.fromisoformat(text.replace("Z", "+00:00"))
    return int(stamp.timestamp()) * NS


def trade_date_of_request(row: dict) -> date:
    """The CT trade date a request piece belongs to (a 17:00 CT evening belongs to the next day)."""
    local = _ct_of(_utc_ns(row["request_end"]) - NS)
    return local.date() + timedelta(days=1) if local.time() >= time(17, 0) else local.date()


def files_by_date(rows: list[dict]) -> dict[date, list[dict]]:
    out: dict[date, list[dict]] = {}
    for row in rows:
        out.setdefault(trade_date_of_request(row), []).append(row)
    if sorted(out) != sorted(SAMPLE_DATES):
        raise CalibrationError(f"files cover {sorted(out)}, not the five sample dates")
    for day, pieces in out.items():
        for left, right in zip(pieces, pieces[1:], strict=False):
            if left["request_end"] != right["request_start"]:
                raise CalibrationError(f"{day}: request pieces are not contiguous")
    return out


def dbn_chunks(path: Path, count: int = CHUNK_RECORDS) -> Iterator[Chunk]:
    import databento

    store = databento.DBNStore.from_file(path)
    if store.schema != databento.Schema.MBP_1:
        raise CalibrationError(f"{path} is {store.schema}, not mbp-1")
    for arr in store.to_ndarray(count=count):
        if np.any(arr["rtype"] != 1):
            raise CalibrationError(f"{path}: a record is not rtype 1 (mbp-1)")
        yield Chunk(arr["ts_recv"].astype(np.int64), arr["instrument_id"].astype(np.int64),
                    arr["flags"].astype(np.int64), arr["bid_px_00"].astype(np.int64),
                    arr["ask_px_00"].astype(np.int64), arr["bid_sz_00"].astype(np.int64),
                    arr["ask_sz_00"].astype(np.int64))


def calibrate_day(cal: GroupCalendar, day: date, rows: list[dict], tick: TickSpec,
                  chunks_of: callable = dbn_chunks) -> tuple[dict, list[dict]]:  # type: ignore[valid-type]
    pieces = bucket_pieces(cal, day)
    if not pieces:
        raise CalibrationError(f"{cal.group} {day}: no open time")
    first_req, last_req = _utc_ns(rows[0]["request_start"]), _utc_ns(rows[-1]["request_end"])
    if first_req > pieces[0].start_ns - REOPEN_GRACE_NS or last_req < pieces[-1].end_ns:
        raise CalibrationError(f"{day}: files do not span the trade date's open time")
    acc = DayAccumulator(pieces, tick.vendor_tick_fixed, last_req)
    files: list[dict] = []
    for row in rows:
        path = REPO_ROOT / row["path"]
        digest = sha256_file(path)
        if digest != row["sha256"]:
            raise CalibrationError(f"{row['path']}: sha256 {digest} != manifest {row['sha256']}")
        before = acc.stats["records"]
        for chunk in chunks_of(path):
            acc.feed(chunk)
        read = acc.stats["records"] - before
        if read != int(row["record_count"]):
            raise CalibrationError(f"{row['path']}: {read} records, manifest {row['record_count']}")
        files.append({"path": row["path"], "sha256": digest, "sha256_verified": True,
                      "records": read, "request_start": row["request_start"],
                      "request_end": row["request_end"]})
    acc.finish()
    return acc.result(), files


def calibrate_product(root: str, rows: list[dict], tick: TickSpec) -> dict:
    group = GROUP_OF_PRODUCT[root]
    cal = load_group_calendar(group)
    by_date = files_by_date(rows)
    out_dates: dict[str, dict] = {}
    files: list[dict] = []
    for day in SAMPLE_DATES:
        result, day_files = calibrate_day(cal, day, by_date[day], tick)
        out_dates[day.isoformat()] = result
        files.extend(day_files)
    return {"product": root, "group": group, "vendor_tick_fixed": tick.vendor_tick_fixed,
            "vendor_factor": tick.vendor_factor, "calendar_sha256": cal.module_sha256(),
            "code_sha256": {str(Path(m).relative_to(REPO_ROOT)): sha256_file(Path(m))
                            for m in (__file__, REPO_ROOT / "sim" / "cost_inputs.py")},
            "generated_utc": datetime.now(UTC).isoformat(), "files": files, "dates": out_dates}


# ------------------------------------------------------------------ driver ----
def raw_path(tag: str = "") -> Path:
    return SCRATCH_DIR / (f"{RAW_PREFIX}_{tag}.jsonl" if tag else f"{RAW_PREFIX}.jsonl")


def done_products(scratch: Path | None = None) -> dict[str, dict]:
    """Every contract already calibrated, from all run tags' JSONL files."""
    out: dict[str, dict] = {}
    for path in sorted((scratch or SCRATCH_DIR).glob(f"{RAW_PREFIX}*.jsonl")):
        for line in path.read_text().splitlines():
            if line.strip():
                row = json.loads(line)
                if row["product"] in out:
                    raise CalibrationError(f"{row['product']} calibrated twice in the scratch")
                out[row["product"]] = row
    return out


def append_line(row: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as fh:
        fh.write(json.dumps(row, separators=(",", ":")) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


def run(roots: Iterable[str] | None = None, tag: str = "") -> int:
    os.nice(10)
    files = mbp1_files()
    ticks = load_ticks()
    done = done_products()
    todo = [r for r in (roots or sorted(files)) if r not in done]
    for root in todo:
        started = datetime.now(UTC)
        try:
            row = calibrate_product(root, files[root], ticks[root])
        except Exception as exc:  # noqa: BLE001 - reported per contract, the run continues
            print(f"{root}: FAILED {type(exc).__name__}: {exc}", flush=True)
            continue
        row["seconds"] = round((datetime.now(UTC) - started).total_seconds(), 1)
        append_line(row, raw_path(tag))
        print(f"{root}: done in {row['seconds']} s", flush=True)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_run = sub.add_parser("run")
    p_run.add_argument("roots", nargs="*")
    p_run.add_argument("--tag", default="")
    sub.add_parser("build")
    args = parser.parse_args(argv)
    if args.cmd == "run":
        return run(args.roots or None, args.tag)
    from sim.cost_report import build

    return build()


if __name__ == "__main__":
    sys.exit(main())
