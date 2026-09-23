"""Stage A.1 Tasks 2-3: build the flagged MES continuous series and validate it.

    uv run python -m data.build_mes_bars

Reads only immutable raw files already on disk (plus one free, cached
Databento metadata call for the dataset-condition list). Writes:
- data/processed/MES/ohlcv-1m_MES_v_0_<window>.parquet  (bars + flag columns)
- reports/bar_validation_summary.json                  (machine-readable results)

Refuses to write the Parquet series if any hard integrity check fails.

Stage D.1f confirmation build (run session only, on data bought then; see
``build_confirmation`` and reports/stage_d1f_confirmation_list.md 1.1, 1.3, 1.5 steps 2-4b):

    uv run python -m data.build_mes_bars --confirmation

which first runs the D.1f preflight's file-hash checks (``data.pull_mes.d1f_freeze_check``) and
refuses on any problem; the freeze manifest's sha256 is written into the build summary and the
parquet metadata, and the list runner refuses a build made under another manifest (review F2).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from collections.abc import Callable, Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from data.adapter import MES_CONTINUOUS, OHLCV_1M, raw_path, read_rolls
from data.bars import add_flags, bar_trade_dates, load_raw_bars, raw_symbols_on_bar_dates
from data.cme_calendar import CALENDAR_COVERAGE
from data.config import DATASET, PROCESSED_ROOT, REPO_ROOT, VENDOR_ROOT, require_databento_key
from data.pull_mes import (
    D1F_ROLLS_END,
    D1F_ROLLS_START,
    WINDOW_END,
    WINDOW_START,
    d1f_freeze_check,
    monthly_chunks,
    refuse_unless_frozen,
)
from data.research_bars import (
    CONFIRMATION_EARLIEST_TRADE_DATE,
    CONFIRMATION_LAST_TRADE_DATE,
    CONFIRMATION_RAW_CHUNKS,
    CONFIRMATION_SERIES_PATH,
    HOLDOUT2_RAW_CHUNKS,
    assert_confirmation_rows,
)
from data.session import HALT_END, closed_windows_range_ns, ct_ns, trade_date
from data.validate import (
    daily_halt_observation,
    observe_holidays,
    validate_bars,
    validate_calendar_step4b,
)

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


# ---------------------------------------------------------------- Stage D.1f ----
CONFIRMATION_SUMMARY_PATH = REPO_ROOT / "reports" / "stage_d1f_confirmation_build.json"
D1F_CONDITION_START, D1F_CONDITION_END = date(2019, 4, 1), date(2025, 4, 1)  # the D.1e range
CHUNKS_START = date.fromisoformat(CONFIRMATION_RAW_CHUNKS[0][0])  # 2019-05-01 00:00 UTC
CHUNKS_END = date.fromisoformat(CONFIRMATION_RAW_CHUNKS[-1][1])  # 2024-03-01 00:00 UTC
# The vendor-degraded dates known at declaration (list 1.3); any difference is logged.
DEGRADED_DATES_AT_DECLARATION = ("2020-02-27", "2020-02-28", "2020-05-05", "2020-06-30",
                                 "2020-07-01", "2021-12-05", "2022-01-02", "2024-09-18")
# A raw-symbol drop on or after this trade date stops the run for a lead decision before
# step 5 (list 1.1, D-4, NEW-6); strategy.research._d1f_confirmation refuses while it is set.
RAW_SYMBOL_DROP_STOP_FROM = date(2019, 5, 6)
STOP_KEY = "stop_for_lead_decision"
RC_STOP_FOR_LEAD = 7  # files written, but the run must stop for the lead
RC_FREEZE_REFUSED = 6  # the harness differs from the committed freeze manifest: nothing read


class ConfirmationBuildRefused(RuntimeError):
    """The confirmation build was asked to read something it must never read."""


@dataclass(frozen=True)
class ConfirmationInputs:
    """Every path the confirmation build reads or writes (tests point these at tmp_path)."""

    vendor_root: Path
    rolls: Path  # written by `python -m data.pull_mes --d1f-rolls`
    condition: Path  # dataset-condition list 2019-04-01..2025-04-01, fetched once, frozen
    symbology: Path  # instrument_id -> raw_symbol intervals 2019-04-01..2024-03-01, frozen
    out: Path
    summary: Path

    @classmethod
    def under(cls, vendor_root: Path, out: Path = CONFIRMATION_SERIES_PATH,
              summary: Path = CONFIRMATION_SUMMARY_PATH) -> ConfirmationInputs:
        span = f"{D1F_ROLLS_START}_{D1F_ROLLS_END}"
        return cls(
            vendor_root=vendor_root,
            rolls=vendor_root / "rolls" / f"MES_v_0_{span}.jsonl",
            condition=vendor_root / "condition"
            / f"{DATASET}_{D1F_CONDITION_START}_{D1F_CONDITION_END}.json",
            symbology=vendor_root / "symbology" / f"MES_v_0_instrument_raw_symbol_{span}.json",
            out=out, summary=summary)


def confirmation_raw_paths(root: Path = VENDOR_ROOT) -> list[Path]:
    """The 58 unsealed raw chunks 2019-05..2024-02, oldest first."""
    return [raw_path(MES_CONTINUOUS, OHLCV_1M, s, e, root) for s, e in CONFIRMATION_RAW_CHUNKS]


def check_confirmation_paths(paths: Sequence[Path], root: Path = VENDOR_ROOT) -> None:
    """Refuse any holdout-2 chunk (by file name, wherever it sits) and any path that is not one
    of the 58 confirmation chunks under ``root``."""
    sealed = {raw_path(MES_CONTINUOUS, OHLCV_1M, s, e, root).name for s, e in HOLDOUT2_RAW_CHUNKS}
    allowed = {p.resolve() for p in confirmation_raw_paths(root)}
    for path in map(Path, paths):
        if path.name in sealed:
            raise ConfirmationBuildRefused(
                f"REFUSED: {path.name} is a holdout-2 chunk (sealed, 2024-03..2025-03); the "
                "confirmation build never reads it")
        if path.resolve() not in allowed:
            raise ConfirmationBuildRefused(
                f"REFUSED: {path} is not one of the 58 confirmation chunks "
                f"({CONFIRMATION_RAW_CHUNKS[0][0]}..{CONFIRMATION_RAW_CHUNKS[-1][1]})")


def _frozen_json(path: Path, fetch: Callable[[], Any]) -> Any:
    """Free vendor metadata: fetched only if the file is absent, written once (mode 'x',
    read-only), never rewritten (the ``degraded_days`` pattern)."""
    if not path.is_file():
        payload = fetch()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x") as fh:
            json.dump(payload, fh, indent=1, default=str)
        path.chmod(0o444)
    return json.loads(path.read_text())


def _databento_client() -> Any:  # noqa: ANN401 — run session only, never in tests
    import databento

    return databento.Historical(require_databento_key())


def fetch_condition_d1f() -> list[dict]:
    return _databento_client().metadata.get_dataset_condition(
        dataset=DATASET, start_date=str(D1F_CONDITION_START), end_date=str(D1F_CONDITION_END))


def fetch_raw_symbols_d1f(instrument_ids: list[str]) -> dict:
    response = _databento_client().symbology.resolve(
        dataset=DATASET, symbols=instrument_ids, stype_in="instrument_id",
        stype_out="raw_symbol", start_date=str(D1F_ROLLS_START), end_date=str(D1F_ROLLS_END))
    return {"queried_instrument_ids": instrument_ids, "start_date": str(D1F_ROLLS_START),
            "end_date": str(D1F_ROLLS_END), "response": response}


def compare_degraded_dates(degraded: Sequence[dict],
                           declared: Sequence[str] = DEGRADED_DATES_AT_DECLARATION) -> dict:
    """The frozen degraded-date list against the eight dates known at declaration (list 1.3)."""
    frozen = sorted({str(d["date"]) for d in degraded})
    return {"declared_at_d1e": sorted(declared), "frozen": frozen,
            "added_since_declaration": sorted(set(frozen) - set(declared)),
            "missing_since_declaration": sorted(set(declared) - set(frozen)),
            "identical": set(frozen) == set(declared)}


def confirmation_drops(raw: pd.DataFrame, raw_intervals: dict) -> tuple[np.ndarray, np.ndarray,
                                                                        dict]:
    """(keep mask, per-bar raw symbol, drop log). Drops: trade dates outside
    2019-05-01..2024-02-29 (list 1.3), then bars with no MES outright on their date (1.1)."""
    ts = raw["ts_event"].to_numpy()
    tdates = np.array(bar_trade_dates(ts), dtype="datetime64[D]")
    early = tdates < np.datetime64(CONFIRMATION_EARLIEST_TRADE_DATE)
    late = tdates > np.datetime64(CONFIRMATION_LAST_TRADE_DATE)
    symbols, _ = raw_symbols_on_bar_dates(ts, raw["instrument_id"].to_numpy(), raw_intervals)
    no_outright = (symbols == "") & ~early & ~late

    def by_date(mask: np.ndarray) -> dict[str, int]:
        days, counts = np.unique(tdates[mask], return_counts=True)
        return {str(d): int(n) for d, n in zip(days, counts, strict=True)}

    groups = []
    if no_outright.any():
        frame = pd.DataFrame({"ts": ts[no_outright], "trade_date": tdates[no_outright].astype(str),
                              "instrument_id": raw["instrument_id"].to_numpy()[no_outright]})
        frame["utc_date"] = pd.to_datetime(frame["ts"], utc=True).dt.strftime("%Y-%m-%d")
        for (utc_day, iid), grp in frame.groupby(["utc_date", "instrument_id"]):
            _, mapped = raw_symbols_on_bar_dates(grp["ts"].to_numpy()[:1], np.array([iid]),
                                                 raw_intervals)
            groups.append({"utc_date": utc_day, "instrument_id": int(iid), "bars": len(grp),
                           "trade_dates": sorted(set(grp["trade_date"])),
                           "mapped_symbols": mapped[0]["mapped_symbols"],
                           "first_bar_utc": str(pd.Timestamp(int(grp["ts"].min()), tz="UTC")),
                           "last_bar_utc": str(pd.Timestamp(int(grp["ts"].max()), tz="UTC"))})
    stop_mask = no_outright & (tdates >= np.datetime64(RAW_SYMBOL_DROP_STOP_FROM))
    months = Counter(str(d)[:7] for d in tdates[no_outright])
    log = {
        "trade_date_window_drops": {"before_first_trade_date": by_date(early),
                                    "after_last_trade_date": by_date(late)},
        "raw_symbol_drops": {
            "rule": "kept iff an MES outright (MES + month letter + year digit) is what "
                    "symbology maps the bar's instrument_id to on the bar's UTC date",
            "total": int(no_outright.sum()), "by_trade_month": dict(sorted(months.items())),
            "on_or_after_stop_date": int(stop_mask.sum()),
            "stop_date": str(RAW_SYMBOL_DROP_STOP_FROM), "groups": groups},
    }
    return ~early & ~late & ~no_outright, symbols, log


def _check_loaded(raw: pd.DataFrame, paths: Sequence[Path], symbology: dict) -> None:
    names = {Path(p).name for p in paths}
    if "source_file" in raw.columns and not set(raw["source_file"].unique()) <= names:
        raise ConfirmationBuildRefused("bars came from a file outside the 58 confirmation chunks")
    ids = {str(int(i)) for i in raw["instrument_id"].unique()}
    queried = set(map(str, symbology.get("queried_instrument_ids", [])))
    if not ids <= queried:
        raise ConfirmationBuildRefused(
            f"the frozen symbology file does not cover instrument ids {sorted(ids - queried)}; "
            "it was fetched for other bars. Move it aside deliberately and re-run.")


def _summary_base(inputs: ConfirmationInputs, paths: Sequence[Path], degraded: list[dict],
                  raw_report: Any, rolls: list, manifest_sha256: str | None
                  ) -> dict:  # noqa: ANN401
    return {
        "generated_utc": datetime.now(UTC).isoformat(),
        "stage": "D.1f step 4 (confirmation build)", "symbol": MES_CONTINUOUS,
        "manifest_sha256": manifest_sha256,
        "schema": OHLCV_1M, "raw_files": [p.name for p in paths],
        "inputs": {"rolls": str(inputs.rolls), "condition": str(inputs.condition),
                   "symbology": str(inputs.symbology)},
        "calendar_coverage": [str(d) for d in CALENDAR_COVERAGE],
        "raw_rows": raw_report.rows, "raw_hard_failures": raw_report.hard_failures,
        "degraded_vendor_days": degraded,
        "degraded_dates_comparison": compare_degraded_dates(degraded),
        "rolls_v0": [asdict(r) for r in rolls],
        STOP_KEY: False, "stop_reasons": [],
    }


def _validation_summary(report: Any) -> dict:  # noqa: ANN401
    runs = report.gap_runs
    return {
        "rows": report.rows, "hard_failures": report.hard_failures,
        "non_increasing_steps": report.non_increasing_steps,
        "duplicate_timestamps": report.duplicate_timestamps,
        "negative_volume": report.negative_volume, "zero_volume_bars": report.zero_volume,
        "off_tick_prices": report.off_tick_prices, "ohlc_inconsistent": report.ohlc_inconsistent,
        "bars_in_scheduled_closure": len(report.bars_in_scheduled_closure),
        "expected_open_minutes": report.expected_minutes,
        "missing_expected_minutes": report.expected_minutes - report.present_expected_minutes,
        "gap_runs_total": len(runs),
        "gap_runs_by_segment": dict(Counter(r.segment for r in runs)),
        "gap_runs_over_5min": [{"start_ct": r.start_ct, "minutes": r.minutes,
                                "segment": r.segment} for r in runs if r.minutes > 5][:500],
    }


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=1, default=str))


def _write_read_only_parquet(flagged: pd.DataFrame, out: Path, meta: dict) -> None:
    table = pa.Table.from_pandas(flagged.assign(trade_date=flagged["trade_date"].astype(str)),
                                 preserve_index=False)
    blob = json.dumps(meta, default=str).encode()
    schema_meta = {**(table.schema.metadata or {}), b"propexperiment": blob}
    table = table.replace_schema_metadata(schema_meta)
    out.parent.mkdir(parents=True, exist_ok=True)
    partial = out.with_name(out.name + ".partial")
    partial.unlink(missing_ok=True)
    pq.write_table(table, partial)
    try:
        os.link(partial, out)  # never replaces an existing file
    finally:
        partial.unlink(missing_ok=True)
    out.chmod(0o444)


def build_confirmation(
    inputs: ConfirmationInputs | None = None, *,
    load_bars: Callable[[list[Path]], pd.DataFrame] = load_raw_bars,
    fetch_condition: Callable[[], list[dict]] = fetch_condition_d1f,
    fetch_raw_symbols: Callable[[list[str]], dict] = fetch_raw_symbols_d1f,
    log: Callable[[str], None] = print,
    manifest_sha256: str | None = None,
) -> int:
    """Stage D.1f step 4. Order: refuse non-confirmation paths -> refuse an existing output ->
    rolls -> frozen condition list -> load the 58 chunks -> frozen raw-symbol symbology ->
    validate the raw bars (hard failure: summary only, no parquet) -> drop trade dates outside
    2019-05-01..2024-02-29 and bars with no MES outright on their date -> validate the kept
    bars -> step-4b calendar validation (recorded) -> add_flags (asserts calendar coverage) ->
    confirmation-row re-check -> write the parquet read-only and the summary JSON.
    Returns 0, or 7 when a raw-symbol drop on/after 2019-05-06 sets the stop flag (files are
    written; the run stops for the lead before step 5), or a refusal code as ``main``.
    ``manifest_sha256`` (the freeze manifest ``cli`` verified) is written into the summary and
    the parquet metadata; the list runner refuses a build whose value is not its own (None
    included)."""
    inputs = inputs or ConfirmationInputs.under(VENDOR_ROOT)
    paths = confirmation_raw_paths(inputs.vendor_root)
    check_confirmation_paths(paths, inputs.vendor_root)
    if inputs.out.exists():
        log(f"REFUSED: {inputs.out} already exists (read-only). Move it aside deliberately.")
        return 5
    missing = [p.name for p in paths if not p.is_file()]
    if missing:
        log(f"raw files missing ({len(missing)}): {missing}")
        return 1
    rolls = read_rolls(inputs.rolls)
    if not rolls:
        log(f"rolls missing or empty: {inputs.rolls} (python -m data.pull_mes --d1f-rolls)")
        return 1
    condition = _frozen_json(inputs.condition, fetch_condition)
    degraded = [d for d in condition if d["condition"] != "available"]
    raw = load_bars(paths)
    ids = sorted({str(int(i)) for i in raw["instrument_id"].unique()})
    symbology = _frozen_json(inputs.symbology, lambda: fetch_raw_symbols(ids))
    _check_loaded(raw, paths, symbology)

    closed = closed_windows_range_ns(CHUNKS_START, CHUNKS_END)
    starts = np.array([w[0] for w in closed], dtype=np.int64)
    ends = np.array([w[1] for w in closed], dtype=np.int64)
    ts_raw = raw["ts_event"].to_numpy()
    raw_report, _ = validate_bars(raw, int(ts_raw.min()) // 60_000_000_000 * 60_000_000_000,
                                  int(ts_raw.max()) + 60_000_000_000, starts, ends)
    summary = _summary_base(inputs, paths, degraded, raw_report, rolls, manifest_sha256)
    if raw_report.hard_failures:
        _write_json(inputs.summary, summary)
        log(f"HARD FAILURES in the raw bars: series NOT written: {raw_report.hard_failures}")
        return 2
    return _build_kept(raw, rolls, degraded, symbology, starts, ends, inputs, summary, log)


def _build_kept(raw: pd.DataFrame, rolls: list, degraded: list[dict], symbology: dict,
                starts: np.ndarray, ends: np.ndarray, inputs: ConfirmationInputs,
                summary: dict, log: Callable[[str], None]) -> int:
    keep, symbols, drops = confirmation_drops(raw, symbology["response"]["result"])
    summary.update(drops)
    kept = raw[keep].reset_index(drop=True)
    if kept.empty:
        _write_json(inputs.summary, summary)
        log("no bar survives the confirmation drops: series NOT written")
        return 3
    kept_dates = bar_trade_dates(kept["ts_event"].to_numpy())
    first_ns = int(kept["ts_event"].iloc[0]) // 60_000_000_000 * 60_000_000_000
    report, gap_before = validate_bars(kept, first_ns, ct_ns(max(kept_dates), HALT_END),
                                       starts, ends)
    summary["validation"] = _validation_summary(report)
    summary["trade_date_range"] = [str(min(kept_dates)), str(max(kept_dates))]
    if report.hard_failures:
        _write_json(inputs.summary, summary)
        log(f"HARD FAILURES in the kept bars: series NOT written: {report.hard_failures}")
        return 2
    step4b = validate_calendar_step4b(kept["ts_event"].to_numpy())
    summary["calendar_validation_step4b"] = step4b.as_dict()
    flagged = add_flags(kept, rolls, starts, ends, gap_before, {str(d["date"]) for d in degraded},
                        raw_symbols=symbols[keep])
    assert_confirmation_rows(flagged)
    summary["splice_check"] = splice_check(kept, rolls)
    summary["roll_volume_context"] = roll_volume_context(flagged, rolls)
    summary["flag_counts"] = {c: int(flagged[c].sum()) for c in (
        "in_flatten_window", "in_no_new_positions_window", "in_scheduled_closure",
        "is_roll_session", "vendor_degraded_day")}
    stop_n = summary["raw_symbol_drops"]["on_or_after_stop_date"]
    if stop_n:
        summary[STOP_KEY] = True
        summary["stop_reasons"].append(
            f"{stop_n} bars dropped for no MES outright on or after trade date "
            f"{RAW_SYMBOL_DROP_STOP_FROM}: a lead decision is required before step 5")
    meta = {
        "source": f"Databento {DATASET} {MES_CONTINUOUS} {OHLCV_1M}, unadjusted prices; "
                  "Stage D.1f confirmation window 2019-05-01..2024-02-29",
        "flags_doc": "see data/bars.py module docstring",
        "flatten_rule": "Topstep 15:10 CT; 15 min before CME early close; no new positions "
                        "2 min earlier (rules/xfa_rules.py)",
        "daily_halt_ct": "16:00-17:00 (data/session.py)",
        "rolls": [asdict(r) for r in rolls], "degraded_vendor_days": degraded,
        "manifest_sha256": summary["manifest_sha256"],
        "raw_symbol_rule": summary["raw_symbol_drops"]["rule"],
        "raw_symbol_drops_total": summary["raw_symbol_drops"]["total"],
        STOP_KEY: summary[STOP_KEY],
        "calendar_validation_step4b_passed": step4b.passed,
        "degraded_dates_comparison": summary["degraded_dates_comparison"],
        "trade_date_range": summary["trade_date_range"], "raw_files": summary["raw_files"],
        "validation": {k: summary["validation"][k] for k in (
            "rows", "hard_failures", "gap_runs_total", "missing_expected_minutes")},
    }
    if inputs.out.exists():
        log(f"REFUSED: {inputs.out} appeared during the build; nothing overwritten.")
        return 5
    _write_read_only_parquet(flagged, inputs.out, meta)
    _write_json(inputs.summary, summary)
    log(f"wrote {inputs.out} ({len(flagged):,} bars, read-only) and {inputs.summary}; "
        f"step 4b passed: {step4b.passed}")
    if summary[STOP_KEY]:
        log(f"STOP FOR LEAD DECISION before step 5: {summary['stop_reasons']}")
        return RC_STOP_FOR_LEAD
    return 0


def cli(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--confirmation", action="store_true",
                        help="Stage D.1f: build the confirmation parquet from the 58 unsealed "
                             "chunks (the run session only)")
    args = parser.parse_args(argv)
    if not args.confirmation:
        return main()
    manifest_sha = refuse_unless_frozen("confirmation build", d1f_freeze_check)
    if manifest_sha is None:
        return RC_FREEZE_REFUSED
    return build_confirmation(manifest_sha256=manifest_sha)


if __name__ == "__main__":
    sys.exit(cli())
