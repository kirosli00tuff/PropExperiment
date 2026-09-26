"""Stage E.2a Task 7: running the research-window bar builds (data.build_bars's CLI).

    uv run python -m data.build_bars --products MNQ NQ      # one subprocess per product
    uv run python -m data.build_bars --group equity         # every admissible product of a group
    uv run python -m data.build_bars --probe ZN             # time the 2025-04 chunk (tmp output)
    uv run python -m data.build_bars --calendar-report      # classify the calendar bar checks
    uv run python -m data.build_bars --mes-regression DIR   # MES through this path, into DIR

Overnight compute profile (CLAUDE.md): one product at a time, each in its own ``nice -n 10``
subprocess with at most 4 threads, a memory check before each start (the peak estimate must stay
under a third of the available memory), resumable (a product whose parquet exists with the same
input sha256s is skipped), and never inside the AiTrader window (15:30-16:00 PT on weekdays).
"""

from __future__ import annotations

import argparse
import json
import os
import resource
import subprocess
import sys
import time as time_mod
from collections.abc import Callable, Sequence
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from data.adapter import boundaries_from_intervals, read_rolls
from data.bars import load_raw_bars
from data.build_bars import (
    BARS_JSON,
    DATA_END_UTC,
    DATA_START_UTC,
    MAX_THREADS,
    OHLCV_1M,
    PROBE_JSON,
    REPORTS,
    RESEARCH_FIRST_TRADE_DATE,
    RESEARCH_LAST_TRADE_DATE,
    ROLLS_DIR,
    InputFile,
    ProductSpec,
    _utc_ns,
    admissible_products,
    build_product,
    degraded_days,
    embedded_intervals,
    ensure_rolls,
    existing_matches,
    ohlcv_record_counts,
    product_spec,
    research_parquet_path,
    write_parquet,
)
from data.config import PROCESSED_ROOT, REPO_ROOT
from data.group_session import MES_POLICY, group_of, load_group_calendar, sha256_file


def report_header() -> dict:
    return {"stage": "E.2a Task 7 (research-window bar builds)",
            "window_trade_dates": [str(RESEARCH_FIRST_TRADE_DATE), str(RESEARCH_LAST_TRADE_DATE)],
            "data_utc": [str(DATA_START_UTC), str(DATA_END_UTC)],
            "notes": [
                "- First trade date 2025-04-01: its evening segment before 2025-04-01 00:00 UTC "
                "is not in the files. As in MES's research build, the trade date is kept "
                "(partial) and the expected-minute grid starts at 2025-04-01 00:00 UTC, so the "
                "missing evening minutes are neither expected nor gaps (a grain session opens "
                "19:00 CT = 00:00 UTC in CDT and is complete).",
                "- Roll blackout = the splice trade date and the 2 group trade dates before it "
                "(data.group_session.roll_blackout, sim.engine.roll_blackout_dates's rule with "
                "the group's full closures); any difference from sim.engine's equity-calendar "
                "version is listed per product.",
                "- Symbology covers UTC dates 2025-04-01..2026-06-20 (resolve end 2026-06-21, "
                "exclusive). A splice dated after 2026-06-20 is not visible from research-window "
                "metadata, so a roll on 2026-06-21/22 would put 2026-06-18/19 into a blackout "
                "this report cannot show.",
                "- Lead ruling L-3 (01:10 PDT): bars inside a scheduled closure are not a hard "
                "failure (MES's convention): kept, flagged in_scheduled_closure, listed per "
                "product (closure_bars). A bar in the close minute takes the trade date of the "
                "session it closes; any closure bar beyond the close minute holds the product for"
                " the lead. Diagnosis recorded for ZN, ZF, ZT: a single print stamped in the "
                "16:00 CT close minute on Fri 2026-03-13 (TN, UB, ZB end at 15:59); not a "
                "calendar question.",
                "- Lead ruling L-4 revised (01:21 PDT): no closed window for the 2025-11-28 CME "
                "outage in any group; it stays a reported gap run (about 20:44-20:49 CT on 11-27 "
                "to 07:30 CT on 11-28) and LATE_OPENS is checked only (the first bar of 2025-11-28 "
                "at or after 07:30 CT).",
                "- NG: the first build (01:21 PDT, 45,872 bars) dropped 345,929 bars because the "
                "outright pattern accepted a one-digit year only, and NG's raw symbols carry two "
                "digits from mid-2025 (NGN25, NGF26). Builder bug, fixed in data.bars."
                "outright_pattern (one or two digits); the wrong parquet was moved to "
                "data/processed/NG/superseded/ (not deleted) and NG rebuilt (391,801 bars). No "
                "other product had a no-outright drop.",
                "- Volume-ranked flip-flops: NG (2026-01-22/23/25), HO and RB switch back and "
                "forth between two contracts on some dates; the per-roll splice test cannot pass "
                "for a flip-flop, so each product also carries a day-level check "
                "(bars_off_symbology_mapping: 0 bars off the symbology mapping for every product).",
                "- Lead ruling L-6 (01:45 PDT): the grains module's 20 LATE_OPENS are SCHEDULED "
                "(no overnight segment; first minute 08:30 CT) and are closed windows (trade "
                "dates, flags, expected minutes). Told apart by the module's own type: the "
                "grains LateOpen has no stop-time field and its entries are named for the "
                "holiday; the rates/FX/energy/metals LateOpen carries halt_from_ct and its one "
                "entry is named an outage/unscheduled halt (data.group_session."
                "is_scheduled_late_open refuses a module where the two disagree).",
                "- Vendor price scale: the grid-scale probe shows 0 off-grid prices at 10x and "
                "100x the E.0 tick for ZC, ZW, ZS, ZL, HE and LE: Databento quotes them in "
                "cents, so their tick in vendor price units is 100 x the E.0 tick_size (USD). "
                "The check ran at the E.0 tick as the brief says (it passes, and is weaker "
                "there); the tick was not changed. ZM (USD per short ton) is on the E.0 scale.",
                "- Crypto (MBT), lead rulings L-9 and L-10 (02:17 PDT): BOOKED_FORWARD holidays "
                "are not trade dates; their regular session belongs to CME's trade date for them "
                "(booked_forward_sessions per product, 7 in the window). 2026-06-19 and the "
                "24/7 weekend are booked to 2026-06-22 (holdout-1): 1,617 bars, Thu 06-18 16:02 "
                "to Sat 06-20 18:59 CT, dropped and written nowhere; MBT's last research trade "
                "date is 2026-06-18. Day-session quantities are read on the trade date's own "
                "CT calendar date (parquet metadata day_session_rule); the flatten flags follow "
                "each CT calendar day (MES's rule) plus TopstepX's weekend closure.",
                "- The manifest's per-file instrument_ids come from the files' embedded "
                "mappings and can list an id with no bar (a mapping interval that starts on the "
                "weekend before the file: MBT 2025-06, 2025-11, 2026-02, 2026-03). The check is "
                "that every bar's id is listed; ids without bars are reported per file.",
                "- Products built before a later code change were re-derived with the final code "
                "(--refresh): each such parquet equals the final code's table row for row "
                "(parquet.rows_equal_to_rebuild_with_current_code); the parquet keeps the builder "
                "sha256s stamped at its write, and the summary carries the current ones.",
            ]}


def _client_factory() -> Any:  # noqa: ANN401
    import databento

    from data.config import require_databento_key

    return databento.Historical(require_databento_key())


def _peak_rss_mb() -> float:
    return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)


def _limit_threads() -> None:
    for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                "NUMEXPR_NUM_THREADS", "POLARS_MAX_THREADS", "RAYON_NUM_THREADS"):
        os.environ[var] = str(MAX_THREADS)
    try:
        import pyarrow as pa

        pa.set_cpu_count(MAX_THREADS)
        pa.set_io_thread_count(MAX_THREADS)
    except Exception:  # noqa: BLE001, S110 — thread caps are best effort
        pass


def _same_rows_as_existing(frame: Any, meta: dict, path: Path) -> bool:  # noqa: ANN401
    """The table this build would write, compared with the existing read-only parquet (values
    and types; schema metadata ignored). Nothing is written."""
    import pyarrow as pa
    import pyarrow.parquet as pq

    fresh = pa.Table.from_pandas(frame.assign(trade_date=frame["trade_date"].astype(str)),
                                 preserve_index=False)
    return pq.read_table(path).equals(fresh)


def run_one(root: str, *, out_base: Path = PROCESSED_ROOT, report: Path = BARS_JSON,
            allow_fetch: bool = True, refresh: bool = False,
            log: Callable[[str], None] = print) -> int:
    """Build one product (resumable). 0 built or already built, 2 refused or held, 5 exists
    with other inputs (never overwritten). ``refresh``: re-derive an existing product's summary
    with the current code and verify its parquet row for row, without rewriting it."""
    from data.build_bars_reports import load_json, merge_product

    t0 = time_mod.monotonic()
    spec = product_spec(root, out_base)
    if spec.out.exists():
        if not refresh and existing_matches(spec) and \
                root in load_json(report).get("products", {}):
            log(f"{root}: parquet exists with the same input sha256s; skipped (resume)")
            return 0
        if not existing_matches(spec):
            log(f"REFUSED: {spec.out} exists and was built from other inputs; not overwritten")
            return 5
    cal = load_group_calendar(spec.group)
    rolls, symbology, source = ensure_rolls(spec, _client_factory if allow_fetch else None, log)
    embedded = embedded_intervals([f.path for f in spec.files if f.path.is_file()],
                                  spec.continuous)
    if not rolls:
        rolls = boundaries_from_intervals(spec.continuous, embedded)
        source = "embedded DBN mappings (symbology.resolve unavailable); raw symbols unknown"
    result = build_product(spec, cal, degraded_days(), rolls, symbology, source,
                           embedded=embedded)
    summary = result.summary
    if result.frame is not None and result.meta is not None:
        if spec.out.exists():  # resume: the same inputs built it; verify, do not rewrite
            import pyarrow.parquet as pq

            stamped = json.loads(pq.read_schema(spec.out).metadata[b"propexperiment"])
            summary["parquet"] = {
                "path": str(spec.out.relative_to(REPO_ROOT)), "sha256": sha256_file(spec.out),
                "rows": len(result.frame), "resumed": True,
                "rows_equal_to_rebuild_with_current_code": _same_rows_as_existing(
                    result.frame, result.meta, spec.out),
                "builder_files_stamped_at_write": stamped.get("builder_files")}
        else:
            sha = write_parquet(result.frame, {**result.meta, "build_summary": summary}, spec.out)
            summary["parquet"] = {"path": str(spec.out.relative_to(REPO_ROOT)), "sha256": sha,
                                  "rows": len(result.frame), "mode": oct(spec.out.stat().st_mode
                                                                        & 0o777)}
    summary["build_seconds"] = round(time_mod.monotonic() - t0, 1)
    summary["peak_rss_mb"] = _peak_rss_mb()
    merge_product(report, summary, report_header())
    log(f"{root}: {summary['status']} {summary.get('bars', '')} bars in "
        f"{summary['build_seconds']} s, peak {summary['peak_rss_mb']} MB"
        + (f"; causes {summary['refusal_causes']}" if summary["refusal_causes"] else ""))
    return 0 if summary["status"] == "built" else 2


def _mem_available_mb() -> float:
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemAvailable:"):
            return int(line.split()[1]) / 1024
    return 0.0


def _wait_out_aitrader_window(log: Callable[[str], None]) -> None:
    """Stay out of the AiTrader collector window (about 15:30-16:00 PT on weekdays)."""
    from zoneinfo import ZoneInfo

    while True:
        now = datetime.now(ZoneInfo("America/Vancouver"))
        minutes = now.hour * 60 + now.minute
        if now.weekday() < 5 and 15 * 60 + 25 <= minutes < 16 * 60 + 5:
            log(f"{now:%H:%M} PT: inside the AiTrader window; waiting")
            time_mod.sleep(120)
            continue
        return


def run_products(roots: Sequence[str], *, peak_estimate_mb: float = 1500.0,
                 refresh: bool = False, log: Callable[[str], None] = print) -> dict[str, int]:
    """One low-priority subprocess per product, one at a time (the overnight profile)."""
    env = {**os.environ, **{v: str(MAX_THREADS) for v in (
        "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
        "POLARS_MAX_THREADS", "RAYON_NUM_THREADS")}}
    codes: dict[str, int] = {}
    for root in roots:
        _wait_out_aitrader_window(log)
        avail = _mem_available_mb()
        if peak_estimate_mb > avail / 3:
            log(f"{root}: peak estimate {peak_estimate_mb:.0f} MB > a third of available "
                f"{avail:.0f} MB; waiting 5 minutes once")
            time_mod.sleep(300)
            avail = _mem_available_mb()
            if peak_estimate_mb > avail / 3:
                log(f"{root}: still short of memory ({avail:.0f} MB available); not started")
                codes[root] = 9
                continue
        cmd = ["nice", "-n", "10", sys.executable, "-m", "data.build_bars", "--one", root,
               *(["--refresh"] if refresh else [])]
        codes[root] = subprocess.run(cmd, env=env, cwd=REPO_ROOT, check=False).returncode
    return codes


def probe(root: str = "ZN", tmp_dir: Path | None = None, out: Path = PROBE_JSON) -> dict:
    """Time the product's first monthly chunk (2025-04) through the full path into a temporary
    directory; figures only (timings, rows, peak memory), written to ``out``."""
    import tempfile

    tmp = Path(tmp_dir or tempfile.mkdtemp(prefix="e2a_probe_"))
    full = product_spec(root)
    t0 = time_mod.monotonic()
    rolls, symbology, source = ensure_rolls(full, _client_factory, print)
    t_rolls = time_mod.monotonic()
    first = full.files[0]
    spec = ProductSpec(root=root, group=full.group, tick=full.tick, tick_source=full.tick_source,
                       files=(first,), rolls_path=full.rolls_path,
                       symbology_path=full.symbology_path, policy=full.policy,
                       out=research_parquet_path(root, tmp), data_end=date(2025, 5, 1))
    cal = load_group_calendar(spec.group)
    t_cal = time_mod.monotonic()
    embedded = embedded_intervals([first.path], spec.continuous)
    t_load0 = time_mod.monotonic()
    raw_rows = len(load_raw_bars([first.path]))
    t_load1 = time_mod.monotonic()
    result = build_product(spec, cal, degraded_days(), rolls, symbology, source,
                           embedded=embedded)
    t_build = time_mod.monotonic()
    wrote = None
    if result.frame is not None and result.meta is not None:
        wrote = write_parquet(result.frame, result.meta, spec.out)
    t_write = time_mod.monotonic()
    figures = {
        "generated_utc": datetime.now(UTC).isoformat(), "product": root,
        "chunk": first.path.name, "calendar_modules": cal.module_sha256(),
        "status": result.summary["status"], "refusal_causes": result.summary["refusal_causes"],
        "raw_rows": raw_rows, "kept_rows": result.summary.get("bars"),
        "seconds": {"rolls_and_symbology": round(t_rolls - t0, 2),
                    "calendar_load": round(t_cal - t_rolls, 2),
                    "embedded_mappings": round(t_load0 - t_cal, 2),
                    "load_raw_only": round(t_load1 - t_load0, 2),
                    "full_build_incl_sha_load_validate_flags_calendar_check":
                        round(t_build - t_load1, 2),
                    "write_parquet": round(t_write - t_build, 2),
                    "total": round(t_write - t0, 2)},
        "peak_rss_mb": _peak_rss_mb(), "mem_available_mb_at_end": round(_mem_available_mb()),
        "output": str(spec.out) if wrote else None,
        "note": "output written to a temporary directory, not data/processed; figures only",
    }
    _write_json_atomic(out, figures)
    return figures


def _write_json_atomic(path: Path, payload: dict) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(payload, indent=1, default=str))
    tmp.replace(path)


# ------------------------------------------------------------------ MES regression ----
MES_REGRESSION_CHUNKS_END = date(2026, 6, 1)  # the 2026-06 chunk is sealed (holdout-1)


def mes_regression_spec(out: Path) -> ProductSpec:
    from data.adapter import MES_CONTINUOUS, raw_path
    from data.pull_mes import monthly_chunks

    paths = [raw_path(MES_CONTINUOUS, OHLCV_1M, s, e)
             for s, e in monthly_chunks(DATA_START_UTC, MES_REGRESSION_CHUNKS_END)]
    return ProductSpec(
        root="MES", group="equity", tick="0.25", tick_source="MES 0.25 (data.bars MES_TICK_FIXED)",
        files=tuple(InputFile(p, None, None) for p in paths),
        rolls_path=ROLLS_DIR / "MES_v_0_2025-04-01_2026-09-16.jsonl", symbology_path=None,
        policy=MES_POLICY, out=out, data_end=MES_REGRESSION_CHUNKS_END)


def mes_regression(tmp_dir: Path) -> dict:
    """The generalized path on MES's research raw files (2025-04..2026-05; June 2026 is sealed)
    into ``tmp_dir``, compared with the MES research parquet row for row."""
    import pyarrow.parquet as pq

    from data.research_bars import RESEARCH_SERIES_PATH

    spec = mes_regression_spec(Path(tmp_dir) / "MES_research_regression.parquet")
    cal = load_group_calendar("equity")
    rolls = read_rolls(spec.rolls_path)
    result = build_product(spec, cal, degraded_days(), rolls, None,
                           "MES roll cache (data.pull_mes, symbology.resolve 2026-09-16)")
    out: dict[str, Any] = {"status": result.summary["status"],
                           "refusal_causes": result.summary["refusal_causes"],
                           "raw_files": [f.path.name for f in spec.files]}
    if result.frame is None or result.meta is None:
        return out
    write_parquet(result.frame, result.meta, spec.out)
    mine = pq.read_table(spec.out)
    theirs = pq.read_table(RESEARCH_SERIES_PATH)
    n = mine.num_rows
    head = theirs.slice(0, n)
    same_fields = [(f.name, str(f.type)) for f in mine.schema] == \
        [(f.name, str(f.type)) for f in theirs.schema]
    mismatched = {c: int(sum(1 for a, b in zip(mine[c].to_pylist(), head[c].to_pylist(),
                                              strict=True) if a != b))
                  for c in mine.column_names if c in theirs.column_names
                  and not mine[c].equals(head[c])}
    next_ts = int(theirs["ts_event"][n].as_py()) if theirs.num_rows > n else None
    out.update({
        "rows_rebuilt": n, "rows_in_research_parquet": theirs.num_rows,
        "same_columns_and_types": same_fields, "rows_equal": head.equals(mine),
        "mismatched_values_by_column": mismatched,
        "next_research_row_at_or_after_rebuild_end": next_ts is not None
        and next_ts >= _utc_ns(MES_REGRESSION_CHUNKS_END),
        "last_rebuilt_trade_date": str(mine["trade_date"][n - 1].as_py()),
        "research_parquet_sha256": sha256_file(RESEARCH_SERIES_PATH),
        "rebuild_sha256": sha256_file(spec.out),
        "file_bytes_equal": sha256_file(RESEARCH_SERIES_PATH) == sha256_file(spec.out),
        "why_bytes_differ": "the rebuild covers trade dates 2025-04-01..2026-06-01 (partial) "
                            "because the 2026-06 raw chunk is sealed (holdout-1); the research "
                            "parquet also holds 2026-06-01..2026-06-19, and its schema metadata "
                            "differs (Stage A.1 stamps vs Stage E stamps)",
    })
    return out


# ------------------------------------------------------------------ CLI ----
def cli(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--one", help="build one product in this process (the driver's child)")
    parser.add_argument("--products", nargs="*", help="build these products, one subprocess each")
    parser.add_argument("--group", help="build every admissible product of a group")
    parser.add_argument("--probe", help="time one month of this product (tmp output)")
    parser.add_argument("--calendar-report", action="store_true")
    parser.add_argument("--mes-regression", help="tmp directory for the MES regression")
    parser.add_argument("--refresh", action="store_true",
                        help="with --one: re-derive an existing product's summary and verify "
                             "its parquet row for row (never rewrites it)")
    args = parser.parse_args(argv)
    if args.one:
        os.nice(10)
        _limit_threads()
        return run_one(args.one, refresh=args.refresh)
    if args.probe:
        os.nice(10)
        _limit_threads()
        print(json.dumps(probe(args.probe), indent=1, default=str))
        return 0
    if args.mes_regression:
        os.nice(10)
        _limit_threads()
        from data.build_bars_reports import set_section

        result = mes_regression(Path(args.mes_regression))
        set_section(BARS_JSON, "mes_regression", result, report_header())
        print(json.dumps(result, indent=1, default=str))
        return 0 if result.get("rows_equal") else 3
    if args.calendar_report:
        from data.build_bars_reports import write_calendar_report

        doc = write_calendar_report(BARS_JSON, REPORTS / "stage_e2a_calendar_bar_checks.json",
                                    ohlcv_record_counts())
        keys = ("status", "most_liquid", "counts_by_classification")
        print(json.dumps({g: {k: v for k, v in x.items() if k in keys}
                          for g, x in doc["groups"].items()}, indent=1))
        return 0
    roots = list(args.products or [])
    if args.group:
        roots += [p for p in admissible_products() if group_of(p) == args.group]
    if not roots:
        parser.error("nothing to do")
    codes = run_products(roots, refresh=args.refresh)
    print(json.dumps(codes))
    return 0

