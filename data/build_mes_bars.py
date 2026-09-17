"""Stage A.1 Tasks 2-3: build the flagged MES continuous series and validate it.

    uv run python -m data.build_mes_bars

Reads only immutable raw files already on disk (plus one free, cached
Databento metadata call for the dataset-condition list). Writes:
- data/processed/MES/ohlcv-1m_MES_v_0_<window>.parquet  (bars + flag columns)
- reports/bar_validation_summary.json                  (machine-readable results)

Refuses to write the Parquet series if any hard integrity check fails.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from dataclasses import asdict
from datetime import UTC, date, datetime

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from data.adapter import MES_CONTINUOUS, OHLCV_1M, raw_path, read_rolls
from data.bars import add_flags, load_raw_bars
from data.config import DATASET, PROCESSED_ROOT, REPO_ROOT, VENDOR_ROOT, require_databento_key
from data.pull_mes import WINDOW_END, WINDOW_START, monthly_chunks
from data.session import closed_windows_range_ns, trade_date
from data.validate import daily_halt_observation, observe_holidays, validate_bars

SUMMARY_PATH = REPO_ROOT / "reports" / "bar_validation_summary.json"
CONDITION_PATH = VENDOR_ROOT / "condition" / f"{DATASET}_{WINDOW_START}_{WINDOW_END}.json"


def _utc_ns(d: date) -> int:
    return int(datetime(d.year, d.month, d.day, tzinfo=UTC).timestamp()) * 1_000_000_000


def degraded_days() -> list[dict]:
    """Databento dataset-condition list (free metadata), cached once, never rewritten."""
    if not CONDITION_PATH.is_file():
        import databento

        client = databento.Historical(require_databento_key())
        cond = client.metadata.get_dataset_condition(
            dataset=DATASET, start_date=str(WINDOW_START), end_date=str(WINDOW_END)
        )
        CONDITION_PATH.parent.mkdir(parents=True, exist_ok=True)
        with CONDITION_PATH.open("x") as fh:
            json.dump(cond, fh, indent=1)
    return [d for d in json.loads(CONDITION_PATH.read_text()) if d["condition"] != "available"]


def splice_check(bars: pd.DataFrame, rolls) -> list[dict]:  # noqa: ANN001
    ts = bars["ts_event"].to_numpy()
    ids = bars["instrument_id"].to_numpy()
    change = np.flatnonzero(np.diff(ids) != 0) + 1
    observed = [(int(ts[i]), int(ids[i - 1]), int(ids[i])) for i in change]
    out = []
    for r in rolls:
        match = [o for o in observed if o[1] == int(r.from_instrument)
                 and o[2] == int(r.to_instrument)]
        first_new = match[0][0] if match else None
        out.append({
            "roll_date_utc": r.date, "from": r.from_raw_symbol, "to": r.to_raw_symbol,
            "symbology_splice_ns": r.ts_ns, "first_bar_of_new_contract_ns": first_new,
            "consistent": first_new is not None and first_new >= r.ts_ns
            and not ((ts >= r.ts_ns) & (ids == int(r.from_instrument))).any()
            and not ((ts < r.ts_ns) & (ids == int(r.to_instrument))).any(),
        })
    return out + [{"unexplained_splices": len(observed) - sum(1 for x in out if x["consistent"])}]


def roll_volume_context(flagged: pd.DataFrame, rolls) -> list[dict]:  # noqa: ANN001
    daily = flagged.groupby(["trade_date", "raw_symbol"])["volume"].sum().reset_index()
    dates = sorted(set(daily["trade_date"]))
    out = []
    for r in rolls:
        td = trade_date(r.ts_ns)
        k = dates.index(td) if td in dates else None
        if k is None:
            continue
        window = dates[max(0, k - 6): k + 3]
        rows = daily[daily["trade_date"].isin(window)]
        out.append({"roll": f"{r.from_raw_symbol}->{r.to_raw_symbol}", "roll_trade_date": str(td),
                    "daily": [{"trade_date": str(x.trade_date), "symbol": x.raw_symbol,
                               "volume": int(x.volume)} for x in rows.itertuples()]})
    return out


def main() -> int:
    paths = [raw_path(MES_CONTINUOUS, OHLCV_1M, s, e) for s, e in
             monthly_chunks(WINDOW_START, WINDOW_END)]
    missing = [p for p in paths if not p.is_file()]
    if missing:
        from data.holdout import is_sealed_raw

        sealed = [p.name for p in missing if is_sealed_raw(p)]
        if sealed:
            print(f"REFUSED: {sealed} are sealed in the holdout store (Stage C Task 6). The "
                  "research series already exists; rebuilding the full window requires the "
                  "data.holdout unlock ceremony and is reserved for Stage D.2.")
            return 4
        print(f"raw files missing: {missing}")
        return 1
    rolls = read_rolls(VENDOR_ROOT / "rolls" / f"MES_v_0_{WINDOW_START}_{WINDOW_END}.jsonl")
    rolls_c = read_rolls(VENDOR_ROOT / "rolls" / f"MES_c_0_{WINDOW_START}_{WINDOW_END}.jsonl")
    degraded = degraded_days()

    raw = load_raw_bars(paths)
    closed = closed_windows_range_ns(WINDOW_START, WINDOW_END)
    starts = np.array([w[0] for w in closed], dtype=np.int64)
    ends = np.array([w[1] for w in closed], dtype=np.int64)
    report, gap_before = validate_bars(raw, _utc_ns(WINDOW_START), _utc_ns(WINDOW_END),
                                       starts, ends)
    ts = raw["ts_event"].to_numpy()

    runs = report.gap_runs
    run_hist = Counter(
        "1" if r.minutes == 1 else "2-5" if r.minutes <= 5 else "6-30" if r.minutes <= 30
        else ">30" for r in runs
    )
    degraded_dates = {d["date"] for d in degraded}
    summary = {
        "generated_utc": datetime.now(UTC).isoformat(),
        "window_utc": [str(WINDOW_START), str(WINDOW_END)],
        "symbol": MES_CONTINUOUS, "schema": OHLCV_1M, "raw_files": [p.name for p in paths],
        "rows": report.rows,
        "first_bar_ct": pd.Timestamp(report.first_ns, tz="UTC").tz_convert("America/Chicago")
        .isoformat(),
        "last_bar_ct": pd.Timestamp(report.last_ns, tz="UTC").tz_convert("America/Chicago")
        .isoformat(),
        "hard_failures": report.hard_failures,
        "non_increasing_steps": report.non_increasing_steps,
        "duplicate_timestamps": report.duplicate_timestamps,
        "negative_volume": report.negative_volume,
        "zero_volume_bars": report.zero_volume,
        "off_tick_prices": report.off_tick_prices,
        "ohlc_inconsistent": report.ohlc_inconsistent,
        "bars_in_scheduled_closure": len(report.bars_in_scheduled_closure),
        "bars_in_scheduled_closure_ct": [
            pd.Timestamp(t, tz="UTC").tz_convert("America/Chicago").strftime("%Y-%m-%d %a %H:%M")
            for t in report.bars_in_scheduled_closure[:200]
        ],
        "expected_open_minutes": report.expected_minutes,
        "present_expected_minutes": report.present_expected_minutes,
        "missing_expected_minutes": report.expected_minutes - report.present_expected_minutes,
        "gap_runs_total": len(runs),
        "gap_runs_by_length": dict(run_hist),
        "gap_runs_by_segment": dict(Counter(r.segment for r in runs)),
        "rth_gap_minutes": sum(r.minutes for r in runs if r.segment == "RTH"),
        "gap_runs_rth": [{"start_ct": r.start_ct, "minutes": r.minutes} for r in runs
                         if r.segment == "RTH"],
        "gap_runs_over_5min": [{"start_ct": r.start_ct, "minutes": r.minutes,
                                "segment": r.segment} for r in runs if r.minutes > 5],
        "gap_minutes_on_degraded_days": sum(
            r.minutes for r in runs
            if pd.Timestamp(r.start_ns, tz="UTC").strftime("%Y-%m-%d") in degraded_dates),
        "degraded_vendor_days": degraded,
        "daily_halt": daily_halt_observation(ts),
        "holidays": [asdict(h) | {"day": str(h.day)} for h in observe_holidays(
            ts, starts, ends, WINDOW_START, WINDOW_END)],
        "rolls_v0": [asdict(r) for r in rolls],
        "rolls_c0": [asdict(r) for r in rolls_c],
        "splice_check": splice_check(raw, rolls),
    }

    if report.hard_failures:
        SUMMARY_PATH.write_text(json.dumps(summary, indent=1, default=str))
        print(f"HARD FAILURES — series NOT written: {report.hard_failures}")
        return 2

    flagged = add_flags(raw, rolls, starts, ends, gap_before, degraded_dates)
    summary["roll_volume_context"] = roll_volume_context(flagged, rolls)
    summary["flag_counts"] = {
        c: int(flagged[c].sum()) for c in
        ("in_flatten_window", "in_no_new_positions_window", "in_scheduled_closure",
         "is_roll_session", "vendor_degraded_day")
    } | {"bars_with_gap_before": int((flagged["gap_before_minutes"] > 0).sum())}

    out_dir = PROCESSED_ROOT / "MES"
    out_dir.mkdir(parents=True, exist_ok=True)
    # Holdout rows never reach a plaintext file (Stage C Task 6): write the research slice only.
    from data.holdout import split_research_holdout
    from data.research_bars import RESEARCH_PARQUET_NAME

    flagged, _never_written = split_research_holdout(flagged)
    out = out_dir / RESEARCH_PARQUET_NAME
    if out.exists():
        print(f"REFUSED: {out.name} already exists and is checksummed in the holdout manifest "
              "(docs/HOLDOUT_MANIFEST.json). Rebuilding would break `python -m data.holdout "
              "status`. Move the existing file aside deliberately if you really mean to rebuild.")
        return 5
    table = pa.Table.from_pandas(flagged.assign(trade_date=flagged["trade_date"].astype(str)),
                                 preserve_index=False)
    meta = {
        "source": f"Databento {DATASET} {MES_CONTINUOUS} {OHLCV_1M}, unadjusted prices",
        "flags_doc": "see data/bars.py module docstring",
        "flatten_rule": "Topstep 15:10 CT; 15 min before CME early close; no new positions "
                        "2 min earlier (rules/xfa_rules.py)",
        "daily_halt_ct": "16:00-17:00 (data/session.py)",
        "rolls": [asdict(r) for r in rolls],
        "degraded_vendor_days": degraded,
        "validation": {k: summary[k] for k in ("rows", "hard_failures", "gap_runs_total",
                                               "missing_expected_minutes")},
    }
    table = table.replace_schema_metadata(
        {**(table.schema.metadata or {}), b"propexperiment": json.dumps(meta, default=str).encode()}
    )
    pq.write_table(table, out)
    SUMMARY_PATH.write_text(json.dumps(summary, indent=1, default=str))
    print(f"wrote {out} ({len(flagged):,} bars) and {SUMMARY_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
