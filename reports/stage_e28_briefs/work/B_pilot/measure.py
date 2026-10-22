"""Stage E.28 Part B: the pilot measurement (spec sections 2 to 4, and nothing else).

    uv run python reports/stage_e28_briefs/work/B_pilot/measure.py --root ROOT --tick TICK \\
        --fee-side FEE_SIDE [--fee-side-alt FEE ...] --sim-rule SIMRULE --dbn <file.dbn.zst> \\
        --out-dir <dir> [--workers N]

Frozen spec section 0 for QM: --root QM --tick 0.025 --fee-side 0.1368 --fee-side-alt 0.296
--sim-rule trade_through_only (README.md step 6 has the full command).

Runs at nice 10. Phase 1 (per trade date, resumable): up to 4 worker processes each stream the
DBN file once and measure only their own trade dates (date k goes to worker k mod N), one date
at a time, writing <out-dir>/days/<date>.json atomically. Every rule of measure_core.RULES is
computed for every date, so the sim rule is chosen at phase 2 without re-reading data. A rerun
skips every date already on disk with the same fingerprint (parameters, code version, input
file names and sizes); a different fingerprint is refused (use a new --out-dir). Phase 2
(aggregate, also --aggregate-only): applies the exclusions of spec section 2 (holidays and
early closes, roll days and the day after, MAIN gaps above 60 s, incomplete coverage, no
records, any trade date on or after 2024-03-01), then section 4's statistics for the spec rule
and the selected sim rule, writing <out-dir>/results.json and results.md (one table per cell).
Net quantities use --fee-side; --fee-side-alt adds the mean net markout and VPO at each further
fee (spec section 0: QM's conservative 0.296 tick per side) beside them. Fees enter phase 2
only, so they are not part of the fingerprint.
"""
# ruff: noqa: I001 - pilot_common is imported first on purpose (sys.path)

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import multiprocessing as mp
import os
import resource
import sys
import traceback
from collections.abc import Callable, Sequence
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pilot_common as pc  # first: puts the repo root on sys.path
import measure_core as mc
import measure_stats as ms
import pilot_stream as ps

CODE_VERSION = "e28-b-measure-3"  # 2: SpecReviewer fixes RS-01..RS-13; 3: QM spec, --fee-side-alt
SPEC_REF = ("reports/stage_e28_pilot_spec.md sections 0-4 (frozen, contract QM, sha256 "
            "8937740338e81103...), with the fixes of reports/stage_e28_briefs/R_spec.md")
MAX_WORKERS = 4
WORKER_BASE_BYTES = 350 * 2**20
WORKER_DAY_BYTES = 450 * 2**20  # bound on one reduced trade date (trades + price changes)
MEM_FRACTION = 0.7


def log_line(message: str) -> None:
    print(f"[{datetime.now(pc.PT):%Y-%m-%d %H:%M:%S %Z}] {message}", flush=True)


def lower_priority() -> None:
    with contextlib.suppress(OSError):  # already lower, or not permitted: keep going
        os.nice(10)


def mem_available_bytes() -> int | None:
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) * 1024
    except OSError:
        return None
    return None


def worker_peak_bytes(chunk_records: int) -> int:
    return WORKER_BASE_BYTES + WORKER_DAY_BYTES + chunk_records * 80 * 5


def choose_workers(requested: int, chunk_records: int, pending: int,
                   available: int | None, log: Callable[[str], None]) -> int:
    n = max(1, min(requested, MAX_WORKERS, max(pending, 1)))
    per = worker_peak_bytes(chunk_records)
    if available is not None:
        fit = max(1, int(MEM_FRACTION * available // per))
        if fit < n:
            log(f"memory: {n} workers x {per / 2**30:.2f} GB estimated peak exceed "
                f"{MEM_FRACTION:.0%} of MemAvailable {available / 2**30:.2f} GB; using {fit}")
            n = fit
    return n


# ------------------------------------------------------------------ inputs ----
class FileInfo:
    """One input DBN file: guards passed, coverage and symbology from its header."""

    def __init__(self, path: Path, root: str) -> None:
        self.path = Path(path)
        reasons = pc.file_name_refusals(self.path, root)
        if reasons:
            raise pc.PilotRefused("; ".join(reasons))
        if not self.path.is_file():
            raise pc.PilotRefused(f"{self.path} does not exist")
        meta = ps.open_store(self.path).metadata
        reasons = pc.metadata_refusals(meta, root)
        if reasons:
            raise pc.PilotRefused(f"{self.path.name}: " + "; ".join(reasons))
        self.cover_lo, self.cover_hi = int(meta.start), int(meta.end)
        self.size = self.path.stat().st_size
        self.intervals = list((meta.mappings or {}).get(pc.symbol_for(root), []))

    def describe(self) -> dict[str, Any]:
        return {"name": self.path.name, "path": str(self.path), "bytes": self.size,
                "start": pc.iso_ns(self.cover_lo), "end": pc.iso_ns(self.cover_hi)}


def fingerprint(root: str, tick: float, files: Sequence[FileInfo]) -> tuple[str, dict[str, Any]]:
    payload = {"code": CODE_VERSION, "root": root, "tick": tick, "rules": list(mc.RULES),
               "latency_ns": pc.LATENCY_NS, "life_ns": pc.LIFE_NS,
               "horizons_s": list(pc.HORIZONS_S), "grid_ns": pc.GRID_NS, "edge_ns": pc.EDGE_NS,
               "main_pt": [str(pc.MAIN_START_PT), str(pc.MAIN_END_PT)],
               "files": [{"name": f.path.name, "bytes": f.size} for f in files]}
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    return digest, payload


def day_path(out_dir: Path, day: date) -> Path:
    return out_dir / "days" / f"{day.isoformat()}.json"


def write_json_atomic(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(payload, indent=1, default=str) + "\n", encoding="utf-8")
    tmp.replace(path)


def read_day(out_dir: Path, day: date, digest: str) -> dict[str, Any] | None:
    path = day_path(out_dir, day)
    if not path.is_file():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("fingerprint") != digest:
        raise pc.PilotRefused(f"{path} was written with another fingerprint "
                              f"({payload.get('fingerprint')!r} != {digest!r}): parameters, code "
                              "or inputs changed. Use a new --out-dir; nothing is overwritten")
    return payload


class Plan:
    """Candidate trade dates, the file that holds each whole, and static exclusions."""

    def __init__(self, root: str, files: Sequence[FileInfo]) -> None:
        self.cal = pc.calendar_for(root)
        self.files = list(files)
        self.days: dict[date, pc.DayPlan] = {}
        self.owner: dict[date, int | None] = {}
        self.static: dict[date, list[str]] = {}
        per_day: dict[date, list[tuple[int, list[str]]]] = {}
        for idx, info in enumerate(self.files):
            for day in pc.candidate_days(self.cal, info.cover_lo, info.cover_hi):
                plan = self.days.setdefault(day, pc.build_day_plan(self.cal, day))
                per_day.setdefault(day, []).append(
                    (idx, pc.static_exclusions(plan, info.cover_lo, info.cover_hi)))
        for day, entries in per_day.items():
            whole = [(i, r) for i, r in entries if pc.EXCL_COVERAGE not in r]
            # a date must lie whole inside one file; else it is excluded (incomplete coverage)
            self.owner[day], self.static[day] = whole[0] if whole else (None, entries[0][1])

    def measurable(self, day: date) -> bool:
        return self.owner.get(day) is not None and not self.static.get(day)

    def sorted_days(self) -> list[date]:
        return sorted(self.days)


# ------------------------------------------------------------------ phase 1 ----
def static_day_payload(day: date, digest: str, reasons: list[str], status: str) -> dict[str, Any]:
    return {"fingerprint": digest, "code": CODE_VERSION, "date": day.isoformat(),
            "status": status, "static_exclusions": reasons,
            "written": datetime.now(pc.PT).isoformat(timespec="seconds")}


def measured_day_payload(book: ps.DayBook, digest: str, file_name: str) -> dict[str, Any]:
    if book.counts.get("off_tick_prices"):
        raise ps.OffTickError(f"{book.day}: {book.counts['off_tick_prices']} prices are not whole "
                              "ticks: the --tick parameter is wrong for this contract")
    cols, skipped = mc.day_orders(book, mc.MeasureParams(rules=mc.RULES))
    return {**static_day_payload(book.day, digest, [], "measured"), "file": file_name,
            "summary": mc.day_summary_counts(book), "skipped_placements": skipped,
            "orders": cols}


def run_worker(worker: int, root: str, tick_1e9: int, files: list[str], days: list[str],
               out_dir: str, digest: str, chunk_records: int) -> None:
    """One worker: stream each owning file once, measure its own dates, one at a time."""
    try:
        infos = [FileInfo(Path(f), root) for f in files]
        plan = Plan(root, infos)
        remaining = {date.fromisoformat(d) for d in days}
        for idx, info in enumerate(infos):
            mine = {d for d in remaining if plan.owner.get(d) == idx}
            if not mine:
                continue
            store = ps.open_store(info.path)
            for book in ps.iter_days(store, lambda d: plan.days[d], lambda d, m=mine: d in m,
                                     tick_1e9, chunk_records=chunk_records):
                payload = measured_day_payload(book, digest, info.path.name)
                write_json_atomic(day_path(Path(out_dir), book.day), payload)
                mine.discard(book.day)
                remaining.discard(book.day)
                log_line(f"worker {worker}: {book.day} measured "
                         f"({len(payload['orders']['type'])} placements, "
                         f"{book.counts.get('records', 0):,} records)")
        for day in sorted(remaining):
            write_json_atomic(day_path(Path(out_dir), day),
                              static_day_payload(day, digest, [pc.EXCL_NO_RECORDS], "no_records"))
            log_line(f"worker {worker}: {day} had no records")
        peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**20
        log_line(f"worker {worker}: done, peak RSS {peak:.2f} GB")
    except Exception:  # noqa: BLE001 - reported in full, the parent stops with rc 1
        traceback.print_exc()
        sys.exit(1)


def phase1(root: str, tick: float, plan: Plan, out_dir: Path, digest: str, workers: int,
           chunk_records: int, log: Callable[[str], None]) -> int:
    pending: list[date] = []
    for day in plan.sorted_days():
        if read_day(out_dir, day, digest) is not None:
            continue
        if plan.measurable(day):
            pending.append(day)
        else:
            write_json_atomic(day_path(out_dir, day), static_day_payload(
                day, digest, plan.static[day], "excluded_static"))
    log(f"phase 1: {len(plan.days)} candidate dates, {len(pending)} to measure")
    if not pending:
        return pc.RC_OK
    n = choose_workers(workers, chunk_records, len(pending), mem_available_bytes(), log)
    shards = [[d.isoformat() for d in pending[k::n]] for k in range(n)]
    files = [str(f.path) for f in plan.files]
    tick_1e9 = ps.tick_units(tick)
    if n == 1:
        try:
            run_worker(0, root, tick_1e9, files, shards[0], str(out_dir), digest, chunk_records)
        except SystemExit as exc:
            return pc.RC_STOPPED if exc.code else pc.RC_OK
        return pc.RC_OK
    ctx = mp.get_context("spawn")  # fork from a threaded parent can deadlock
    procs = [ctx.Process(target=run_worker, args=(k, root, tick_1e9, files, shard, str(out_dir),
                                                  digest, chunk_records))
             for k, shard in enumerate(shards)]
    log(f"phase 1: {n} worker processes, chunk {chunk_records:,} records")
    for p in procs:
        p.start()
    for p in procs:
        p.join()
    failed = [k for k, p in enumerate(procs) if p.exitcode != 0]
    if failed:
        log(f"phase 1 STOPPED: worker(s) {failed} failed; finished dates are on disk, rerun "
            "the same command to resume")
        return pc.RC_STOPPED
    return pc.RC_OK


# ------------------------------------------------------------------ phase 2 ----
def ids_by_day(plan: Plan, payloads: dict[date, dict[str, Any]]) -> dict[date, list[str]]:
    out = {}
    for day, dplan in plan.days.items():
        lo = dplan.open_lo if dplan.open_lo is not None else pc.day_window_ns(day)[0]
        hi = dplan.open_hi if dplan.open_hi is not None else pc.day_window_ns(day)[1]
        mapped: list[str] = []
        for info in plan.files:
            mapped = pc.ordered_union(mapped, pc.mapped_ids(info.intervals, lo, hi))
        seen = (payloads.get(day, {}).get("summary") or {}).get("instrument_ids_in_records", [])
        out[day] = pc.ordered_union(mapped, [str(s) for s in seen])
    return out


def exclusions(plan: Plan, payloads: dict[date, dict[str, Any]]) -> dict[date, list[str]]:
    ids = ids_by_day(plan, payloads)
    rolls = pc.roll_exclusions(plan.sorted_days(), ids, plan.cal)
    out: dict[date, list[str]] = {}
    for day in plan.sorted_days():
        payload = payloads[day]
        reasons = list(payload.get("static_exclusions") or [])
        gap = (payload.get("summary") or {}).get("main_max_gap_s")
        if payload["status"] == "measured" and gap is not None \
                and gap > pc.MAX_MAIN_GAP_NS / pc.NS:
            reasons.append(pc.EXCL_GAP)
        if day in rolls:
            reasons.append(rolls[day])
        out[day] = reasons
    return out


def _sum_counts(payloads: list[dict[str, Any]], key: str) -> dict[str, int]:
    total: dict[str, int] = {}
    for payload in payloads:
        table = payload.get(key) if key == "skipped_placements" else \
            (payload.get("summary") or {}).get(key, {})
        for name, n in (table or {}).items():
            total[name] = total.get(name, 0) + int(n)
    return dict(sorted(total.items()))


def phase2(plan: Plan, out_dir: Path, digest: str, payload_meta: dict[str, Any], fee_side: float,
           sim_rule: str, label: str, log: Callable[[str], None],
           fee_side_alt: Sequence[float] = ()) -> dict[str, Any]:
    payloads = {}
    for day in plan.sorted_days():
        payload = read_day(out_dir, day, digest)
        if payload is None:
            raise pc.PilotRefused(f"{day} has no day file yet: run phase 1 first")
        payloads[day] = payload
    excl = exclusions(plan, payloads)
    included = [d for d in plan.sorted_days() if not excl[d]]
    rules = list(dict.fromkeys([mc.RULE_SPEC, sim_rule]))
    used = [payloads[d] for d in included]
    tab = ms.order_table(used, rules)
    results = ms.all_cells(tab, rules, len(included), fee_side, fee_side_alt=fee_side_alt)
    reasons: dict[str, int] = {}
    for rs in excl.values():
        for r in rs:
            reasons[r] = reasons.get(r, 0) + 1
    out = {"spec": SPEC_REF, "code": CODE_VERSION, "fingerprint": digest, "label": label,
           "parameters": {**payload_meta, "fee_side_ticks": fee_side,
                          "fee_side_alt_ticks": list(fee_side_alt), "sim_rule": sim_rule,
                          "bootstrap": {"replicates": ms.BOOT_REPLICATES, "seed": ms.BOOT_SEED,
                                        "unit": "trade date"}},
           "days": {"candidates": len(plan.days), "included": [d.isoformat() for d in included],
                    "excluded": {d.isoformat(): r for d, r in excl.items() if r},
                    "exclusion_counts": dict(sorted(reasons.items()))},
           "data_checks_included_days": {
               "record_counts": _sum_counts(used, "counts"),
               "skipped_placements": _sum_counts(used, "skipped_placements")},
           "per_day": [_day_row(d, payloads[d], excl[d]) for d in plan.sorted_days()],
           "results": results,
           "written": datetime.now(pc.PT).isoformat(timespec="seconds")}
    write_json_atomic(out_dir / "results.json", out)
    md = out_dir / "results.md"
    tmp = md.with_name(md.name + ".tmp")
    tmp.write_text(render_markdown(out), encoding="utf-8")
    tmp.replace(md)
    log(f"phase 2: {len(included)} of {len(plan.days)} dates included; wrote "
        f"{out_dir / 'results.json'} and results.md")
    return out


def _day_row(day: date, payload: dict[str, Any], reasons: list[str]) -> dict[str, Any]:
    summary = payload.get("summary") or {}
    orders = payload.get("orders") or {}
    return {"date": day.isoformat(), "status": payload["status"], "excluded": reasons,
            "records": (summary.get("counts") or {}).get("records"),
            "main_max_gap_s": summary.get("main_max_gap_s"),
            "placements": len(orders.get("type", [])),
            "instrument_ids": summary.get("instrument_ids_in_records")}


def _alt_note(alt: Sequence[float] | None) -> str:
    if not alt:
        return ""
    return " (net markouts and VPO also at " + ", ".join(f"{a:g}" for a in alt) + " ticks)"


def render_markdown(out: dict[str, Any]) -> str:
    p = out["parameters"]
    lines = [f"# Stage E.28 pilot measurement: {p['root']} ({out.get('label') or 'no label'})\n",
             f"Spec: {out['spec']}. Code {out['code']}, fingerprint `{out['fingerprint'][:16]}`.",
             f"Tick {p['tick']}, FEE_SIDE {p['fee_side_ticks']} ticks"
             f"{_alt_note(p.get('fee_side_alt_ticks'))}, sim rule "
             f"`{p['sim_rule']}`, bootstrap {p['bootstrap']['replicates']} day-block replicates "
             f"(seed {p['bootstrap']['seed']}). Written {out['written']}.\n",
             f"Dates: {out['days']['candidates']} candidates, {len(out['days']['included'])} "
             "included. Exclusions (a date can have several):\n",
             "| reason | dates |", "|---|---:|"]
    lines += [f"| {r} | {n} |" for r, n in out["days"]["exclusion_counts"].items()]
    lines += ["", "Data checks over the included dates (records, and placements not made):\n",
              "| count | n |", "|---|---:|"]
    checks = out["data_checks_included_days"]
    lines += [f"| {k.replace('|', ' / ')} | {v:,} |" for k, v in
              {**checks["record_counts"], **checks["skipped_placements"]}.items()]
    lines += ["", "| date | status | excluded | records | MAIN max gap (s) | placements |",
              "|---|---|---|---:|---:|---:|"]
    for row in out["per_day"]:
        gap = "" if row["main_max_gap_s"] is None else f"{row['main_max_gap_s']:.1f}"
        lines.append(f"| {row['date']} | {row['status']} | {', '.join(row['excluded'])} | "
                     f"{row['records'] or ''} | {gap} | {row['placements']} |")
    lines.append("")
    return "\n".join(lines) + "\n" + ms.render_cells_markdown(out["results"])


# ------------------------------------------------------------------ CLI ----
def _parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="measure.py", description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", required=True)
    ap.add_argument("--tick", type=float, required=True, help="tick size in price units")
    ap.add_argument("--fee-side", type=float, required=True, help="FEE_SIDE in ticks")
    ap.add_argument("--fee-side-alt", type=float, nargs="*", default=[],
                    help="further fees per side in ticks at which net markouts and VPO are also "
                         "reported (spec section 0, QM: 0.296)")
    ap.add_argument("--sim-rule", required=True, choices=mc.SIM_RULE_CHOICES)
    ap.add_argument("--dbn", nargs="+", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--workers", type=int, default=2, help=f"1..{MAX_WORKERS}")
    ap.add_argument("--chunk-records", type=int, default=ps.DEFAULT_CHUNK_RECORDS)
    ap.add_argument("--aggregate-only", action="store_true")
    ap.add_argument("--label", default="", help="free text for the report (e.g. the firm)")
    return ap


def main(argv: list[str] | None = None, *, log: Callable[[str], None] = log_line) -> int:
    args = _parser().parse_args(argv)
    lower_priority()
    try:
        pc.require_root(args.root)
        if not 1 <= args.workers <= MAX_WORKERS:
            raise pc.PilotRefused(f"--workers must be 1..{MAX_WORKERS}")
        if args.fee_side < 0 or args.chunk_records < 1000:
            raise pc.PilotRefused("--fee-side must be >= 0 and --chunk-records >= 1000")
        if any(f < 0 for f in args.fee_side_alt):
            raise pc.PilotRefused("--fee-side-alt values must be >= 0")
        fee_alt = [f for f in dict.fromkeys(args.fee_side_alt) if f != args.fee_side]
        ps.tick_units(args.tick)
        files = [FileInfo(Path(f), args.root) for f in args.dbn]
        plan = Plan(args.root, files)
        digest, meta = fingerprint(args.root, args.tick, files)
        out_dir = Path(args.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        for day in plan.sorted_days():
            read_day(out_dir, day, digest)  # refuses a foreign day file before any work
    except (pc.PilotRefused, ValueError, OSError) as exc:
        print(f"REFUSED ({type(exc).__name__}): {exc}", file=sys.stderr)
        return pc.RC_REFUSED
    log(f"measure {args.root}: {len(files)} file(s), fingerprint {digest[:16]}, out {out_dir}")
    if not args.aggregate_only:
        rc = phase1(args.root, args.tick, plan, out_dir, digest, args.workers,
                    args.chunk_records, log)
        if rc != pc.RC_OK:
            return rc
    try:
        phase2(plan, out_dir, digest, {**meta, "files": [f.describe() for f in files]},
               args.fee_side, args.sim_rule, args.label, log, fee_alt)
    except (pc.PilotRefused, ValueError, OSError) as exc:
        print(f"PHASE 2 STOPPED ({type(exc).__name__}): {exc}", file=sys.stderr)
        return pc.RC_STOPPED
    return pc.RC_OK


if __name__ == "__main__":
    sys.exit(main())
