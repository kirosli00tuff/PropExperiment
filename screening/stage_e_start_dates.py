"""Stage E start dates S_X: the builder per set and the ONE shared loader (lead ruling OC-K).

Design D4 (NULL_CRITERIA 4.1 generalized; docs/NULL_CRITERIA_E.md 4): V_ref,X = the median of the
14 monthly medians (2025-04..2026-05) of the day-session one-minute volume of the bars present;
S_X = the first trade date with bars of the earliest month M* from which every month through
2024-02 has a median >= 0.25 V_ref,X; 0.15 and 0.40 descriptive; earliest S_X 2019-05-06. The rule
itself is screening.stage_e_stats_start.start_rule (imported, not re-implemented).

    python -m screening.stage_e_start_dates --harness-sha256 SHA --set K1|..|K8|ML \
        [--research-root DIR] [--step2-root DIR]

Builder, one SET per file reports/stage_e_start_rule_<SET>.json (schema "stage_e_start_rule/2",
written once, read-only; ``run_set`` calls screening.harness_freeze.preflight first):
- the set's roots come from frozen files only: a cluster K1..K8 = its traded vehicles
  (reports/stage_e2a_vehicles.json, hash-checked) and every leg its frozen members read
  (reports/stage_e_<k#>_member_freeze.json); "ML" = the ML route's 31 price-path contracts
  (ml_route.constants.PRICE_PATH_CONTRACTS);
- per root, the research store (E.2a's recorded sha256 required) gives the 14 reference months and
  the step 2 store (data.step2_store) the months 2019-05..2024-02; only ts_event, volume and
  trade_date are read (never a price), and every row must book to an allowed trade date of its
  store (data.stage_e_bars.check_bookings: holdout, embargo and out-of-store rows refuse the root);
- "day session" = CT clock minutes [O_X, C_X) of the bar's ts_event, the month keyed by the
  bar's trade date, bars present, no exclusions (D.1f: MES RTH 08:30..14:59). Lead ruling OC-S:
  D6's (O_X, C_X) governs for EVERY root, as E.2a recorded it per contract
  (reports/stage_e2a_vehicle_sizes.json, hash-checked; D2 names it "the day-session open and
  close"; E.2a's vehicle readings and the ML route use it; ruling L-1 keeps copper's 07:10 open).
  D1's windows are declared for the coverage proxy only and are not used here. A root without a
  recorded (O_X, C_X) is refused by name (``DaySessionUndeclared``); every refused root of the
  set is named at once, before any bar is read, and nothing is written (a set with any refused
  root is refused whole, lead ruling on Q-2);
- MES (the S&P 500 leg, D1.5) is not read: D4 fixes its S at D.1f's 2020-02-03, and its entry is
  taken from D.1f's record reports/stage_d1f_step5_start_rule.json (sha256 pinned, S checked
  against D4's text, the rule re-run on the recorded medians).

Loader (used by screening.stage_e_runner and ml_route.inputs):
    load_start_dates(root=REPO_ROOT) -> Mapping[str, date]  # every per-set file merged
    start_date(root_symbol, root=REPO_ROOT) -> date
    start_dates_for(root_symbols, root=REPO_ROOT) -> (dates, provenance)  # files and sha256
Two files giving one root a different S_X, V_ref or any monthly median: StartRuleConflict (lead
ruling on Q-4). An absent root: the runner's StartRuleMissing; an empty window (no qualifying
month): StartWindowEmpty, its subclass (``start_dates_for(..., allow_empty=True)`` returns the
provenance instead, for the power check's supply of 0 days, lead ruling on Q-3). A file that is
not a valid set file: StartRuleInvalid. (The classes live in screening.stage_e_runner.)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime, time
from pathlib import Path
from types import MappingProxyType
from typing import Any
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from data.build_bars import research_parquet_path
from data.config import PROCESSED_ROOT, REPO_ROOT, STEP2_ROOT
from data.group_session import load_group_calendar
from data.stage_e_bars import (
    RESEARCH,
    STEP2,
    ConfirmationStoreMissing,
    ParquetHashMismatch,
    StageEBarRefusal,
    check_bookings,
)
from data.step2_store import step2_parquet_path
from rules.products import UnknownProduct, product
from screening import harness_freeze
from screening.stage_e_frozen import FrozenTables, load_frozen_tables, sha256_file
from screening.stage_e_stats_start import (
    EARLIEST_START,
    EXTENSION_MONTHS,
    LAST_CONFIRMATION_DATE,
    REFERENCE_MONTHS,
    SENSITIVITY_FRACTIONS,
    StartRule,
    first_trade_dates_by_month,
    start_rule,
)

SCHEMA = "stage_e_start_rule/2"
REPORTS_DIR = Path("reports")
FILE_GLOB = "stage_e_start_rule_*.json"
FILE_PATTERN = re.compile(r"^stage_e_start_rule_(K[1-8]|ML)\.json$")
SETS = tuple(f"K{i}" for i in range(1, 9)) + ("ML",)
READ_COLUMNS = ("ts_event", "volume", "trade_date")
CT = ZoneInfo("America/Chicago")
PDT = ZoneInfo("America/Vancouver")

# Lead ruling OC-S (Stage E.2b, 2026-09-26): the start rule's day session is D6's (O_X, C_X) for
# every root, [O_X, C_X) on the bar's CT minute, from E.2a's hashed per-contract record.
DAY_SESSION_RULE = ("D6 (O_X, C_X) per contract from reports/stage_e2a_vehicle_sizes.json, "
                    "[O_X, C_X) on the bar's CT clock minute (lead ruling OC-S); MES: D.1f's RTH "
                    "08:30..14:59 (NULL_CRITERIA 4.1)")

MES = "MES"
MES_DAY_SESSION_CT = (time(8, 30), time(15, 0))  # NULL_CRITERIA 4.1: CT 08:30 to 14:59
MES_D4_START = date(2020, 2, 3)  # D4: "so MES as a leg starts 2020-02-03"
D1F_RECORD = REPORTS_DIR / "stage_d1f_step5_start_rule.json"
D1F_RECORD_SHA256 = "4f2870f51a3551651466e919ba2941d11908c45807ba0ee72be63fb71d9bb11c"


class StartDatesRefusal(RuntimeError):
    """The builder cannot compute this set's start dates as asked; nothing is written."""


class DaySessionUndeclared(StartDatesRefusal):
    """The frozen text leaves a product's day-session window open (a question for the lead)."""


def _runner():  # noqa: ANN202 - the loader's refusal classes live in the runner (no import cycle)
    from screening import stage_e_runner

    return stage_e_runner


def _frozen_tables() -> FrozenTables:
    return load_frozen_tables()


def _display(path: Path, root: Path = REPO_ROOT) -> str:
    path = Path(path)
    try:
        return path.resolve().relative_to(Path(root).resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _hm(t: time) -> str:
    return t.strftime("%H:%M")


# ------------------------------------------------------------- day session ----
def day_session_window(root_symbol: str, tables: FrozenTables | None = None) -> tuple[time, time]:
    """The product's day session [O_X, C_X) in CT: D6's (O_X, C_X) as E.2a recorded it (lead
    ruling OC-S); MES: D.1f's RTH; a root without a record is refused by name."""
    if root_symbol == MES:
        return MES_DAY_SESSION_CT
    try:
        product(root_symbol)
    except UnknownProduct as exc:
        raise StartDatesRefusal(f"{root_symbol}: not in the Stage E product table") from exc
    d6 = (tables or _frozen_tables()).day_session_ct.get(root_symbol)
    if d6 is None:
        raise DaySessionUndeclared(f"{root_symbol}: no D6 (O_X, C_X) in E.2a's sizes table (not a "
                                   "Stage E contract with research bars)")
    if not d6[0] < d6[1]:
        raise DaySessionUndeclared(f"{root_symbol}: D6 (O_X, C_X) {d6} does not run forward")
    return d6


def day_session_monthly_medians(frame: pd.DataFrame, window: tuple[time, time]
                                ) -> dict[str, float]:
    """Per trade-date month, the median volume of the bars whose CT clock minute is in
    [start, end) (bars present; no exclusion)."""
    start, end = window
    lo, hi = start.hour * 60 + start.minute, end.hour * 60 + end.minute
    if not lo < hi:
        raise ValueError(f"day-session window {window} does not run forward within a day")
    local = pd.to_datetime(frame["ts_event"].to_numpy(np.int64), utc=True).tz_convert(CT)
    minute = np.asarray(local.hour * 60 + local.minute)
    inside = frame.loc[(minute >= lo) & (minute < hi)]
    months = inside["trade_date"].astype(str).str.slice(0, 7)
    medians = inside["volume"].astype(float).groupby(months).median()
    return {str(k): float(v) for k, v in medians.items()}


# ------------------------------------------------------------------ stores ----
def _read_columns(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path, columns=list(READ_COLUMNS))


def read_volume_bars(root_symbol: str, path: Path, store: str, *,
                     expected_sha256: str | None) -> tuple[pd.DataFrame, str]:
    """ts_event, volume and trade_date of one store file, every row booked to an allowed trade
    date of the store (data.stage_e_bars.check_bookings). No price column is read."""
    path = Path(path)
    where = f"{store} volume {path.name}"
    if not path.is_file():
        cls = ConfirmationStoreMissing if store == STEP2 else StageEBarRefusal
        raise cls(f"{where}: {path} does not exist")
    digest = sha256_file(path)
    if expected_sha256 is not None and digest != expected_sha256:
        raise ParquetHashMismatch(f"{where}: sha256 {digest[:12]}... is not the recorded "
                                  f"{expected_sha256[:12]}...")
    frame = _read_columns(path)
    frame = frame.sort_values("ts_event", kind="stable").reset_index(drop=True)
    check_bookings(root_symbol, load_group_calendar(product(root_symbol).group), frame, store,
                   where)
    return frame, digest


@dataclass(frozen=True)
class ProductStart:
    root_symbol: str
    entry: Mapping[str, Any]  # the JSON entry of the product
    inputs: tuple[tuple[str, str], ...]  # (path, sha256) of every file read


def _iso(day: date | None) -> str | None:
    return None if day is None else day.isoformat()


def _entry(rule: StartRule, window: tuple[time, time], first: Mapping[str, date],
           source: str, step2_sha256: str) -> dict[str, Any]:
    low, high = rule.sensitivity
    if (low.fraction, high.fraction) != SENSITIVITY_FRACTIONS:
        raise StartDatesRefusal(f"{rule.vehicle}: sensitivity fractions {low.fraction}, "
                                f"{high.fraction} are not {SENSITIVITY_FRACTIONS}")
    return {
        "s_x": _iso(rule.s_x), "s_x_015": _iso(low.s), "s_x_040": _iso(high.s),
        "v_ref": rule.v_ref,
        "monthly_medians": dict(rule.reference_monthly_medians)
        | dict(rule.extension_monthly_medians),
        "m_star": {"0.25": rule.binding.m_star, "0.15": low.m_star, "0.40": high.m_star},
        "first_trade_dates": {m: first[m].isoformat() for m in sorted(first)},
        "day_session_ct": [_hm(window[0]), _hm(window[1])],
        "source": source,
        "step2_sha256": step2_sha256,  # the store the medians came from (review F-3)
    }


def _rule(root_symbol: str, reference: Mapping[str, float],
          extension: Mapping[str, float | None], first: Mapping[str, date]) -> StartRule:
    try:
        return start_rule(root_symbol, reference, extension, first)
    except ValueError as exc:
        raise StartDatesRefusal(f"{root_symbol}: {exc}") from exc


def entry_from_medians(root_symbol: str, reference: Mapping[str, float],
                       extension: Mapping[str, float | None], first: Mapping[str, date], *,
                       window: tuple[time, time], source: str, step2_sha256: str
                       ) -> dict[str, Any]:
    """The JSON entry of one root: D4's rule run on its monthly medians and first trade dates."""
    rule = _rule(root_symbol, reference, extension, first)
    return _entry(rule, window, first, source, step2_sha256)


def product_start_rule(root_symbol: str, *, research_path: Path, step2_path: Path,
                       research_sha256: str, window: tuple[time, time]) -> ProductStart:
    """D4's start rule of one root from its research and step 2 stores."""
    research, r_sha = read_volume_bars(root_symbol, research_path, RESEARCH,
                                       expected_sha256=research_sha256)
    step2, s_sha = read_volume_bars(root_symbol, step2_path, STEP2, expected_sha256=None)
    reference = {m: v for m, v in day_session_monthly_medians(research, window).items()
                 if m in REFERENCE_MONTHS}
    extension = {m: v for m, v in day_session_monthly_medians(step2, window).items()
                 if m in EXTENSION_MONTHS}
    days = (date.fromisoformat(d) for d in step2["trade_date"].astype(str).unique())
    first = first_trade_dates_by_month(days)
    entry = entry_from_medians(root_symbol, reference, extension, first, window=window,
                               source="computed", step2_sha256=s_sha)
    return ProductStart(root_symbol, entry,
                        ((_display(research_path), r_sha), (_display(step2_path), s_sha)))


def mes_from_d1f(root: Path = REPO_ROOT) -> ProductStart:
    """MES's entry from D.1f's pinned record (D4: MES as a leg starts 2020-02-03)."""
    path = Path(root) / D1F_RECORD
    if not path.is_file():
        raise StartDatesRefusal(f"MES: {D1F_RECORD.as_posix()} does not exist")
    digest = sha256_file(path)
    if digest != D1F_RECORD_SHA256:
        raise StartDatesRefusal(f"MES: {D1F_RECORD.as_posix()} sha256 {digest[:12]}... is not the "
                                f"pinned {D1F_RECORD_SHA256[:12]}...")
    record = json.loads(path.read_text(encoding="utf-8"))
    rec = record["start_rule"]
    confirmation = record["run_inputs_sha256"]["confirmation_parquet"]  # the store S came from
    first = {m: date.fromisoformat(d) for m, d in rec["extension_first_trade_dates"].items()
             if d is not None}
    rule = _rule(MES, rec["reference_monthly_medians"], rec["extension_monthly_medians"], first)
    recorded = {"0.25": rec["S"]} | {f"{s['fraction']:.2f}": s["s"] for s in rec["sensitivity"]}
    rerun = {"0.25": _iso(rule.s_x)} | {f"{a.fraction:.2f}": _iso(a.s) for a in rule.sensitivity}
    if rule.s_x != MES_D4_START or recorded != rerun or rule.v_ref != rec["v_ref"]:
        raise StartDatesRefusal(f"MES: D.1f's record {recorded} (v_ref {rec['v_ref']}) does not "
                                f"re-run to itself {rerun} or to D4's {MES_D4_START}")
    entry = _entry(rule, MES_DAY_SESSION_CT, first,
                   f"D.1f record {D1F_RECORD.as_posix()} (D4: MES as a leg starts 2020-02-03); "
                   f"medians from {confirmation['path']}", confirmation["sha256"])
    return ProductStart(MES, entry, ((D1F_RECORD.as_posix(), digest),))


# --------------------------------------------------------------------- sets ----
def check_set(set_id: str) -> str:
    if set_id not in SETS:
        raise StartDatesRefusal(f"set {set_id!r} is not one of {SETS}")
    return set_id


def set_roots(set_id: str, root: Path = REPO_ROOT, tables: FrozenTables | None = None
              ) -> tuple[tuple[str, ...], tuple[tuple[str, str], ...]]:
    """(the set's roots, sorted; the frozen files naming them beyond the E.2a tables)."""
    check_set(set_id)
    if set_id == "ML":
        from ml_route.constants import PRICE_PATH_CONTRACTS

        return tuple(sorted(PRICE_PATH_CONTRACTS)), ()
    from screening.stage_e_freeze import freeze_path, load_cluster_freeze

    freeze = load_cluster_freeze(set_id, root=Path(root))
    vehicles = {v for v, e in (tables or _frozen_tables()).vehicles.items()
                if e.cluster == set_id}
    legs = {leg.root for m in freeze.members for leg in m.legs}
    return (tuple(sorted(vehicles | legs)),
            ((freeze_path(set_id).as_posix(), freeze.sha256),))


def start_rule_path(set_id: str, root: Path = REPO_ROOT) -> Path:
    return Path(root) / REPORTS_DIR / f"stage_e_start_rule_{check_set(set_id)}.json"


def _windows(roots: Sequence[str], tables: FrozenTables) -> dict[str, tuple[time, time]]:
    """Every root's day session; every refused root named at once (before any bar is read)."""
    out: dict[str, tuple[time, time]] = {}
    refused: list[str] = []
    for r in roots:
        try:
            out[r] = day_session_window(r, tables)
        except StartDatesRefusal as exc:
            refused.append(str(exc))
    if refused:
        raise StartDatesRefusal(f"{len(refused)} root(s) refused, the set is refused whole: "
                                + "; ".join(refused))
    return out


def build_set(set_id: str, *, harness_sha256: str, research_root: Path = PROCESSED_ROOT,
              step2_root: Path = STEP2_ROOT, root: Path = REPO_ROOT) -> dict:
    """The set's start-rule document (not written). Preflight first, before any file is read."""
    harness = harness_freeze.preflight(harness_sha256)
    check_set(set_id)
    if start_rule_path(set_id, root).exists():
        raise StartDatesRefusal(f"{_display(start_rule_path(set_id, root), root)} already "
                                "exists; a start-rule file is written once")
    tables = _frozen_tables()
    roots, set_inputs = set_roots(set_id, root=root, tables=tables)
    windows = _windows(roots, tables)
    products: dict[str, Any] = {}
    inputs = [*set_inputs, ("reports/stage_e2a_vehicle_sizes.json", tables.hashes["sizes"]),
              ("reports/stage_e2a_vehicles.json", tables.hashes["vehicles"])]
    for r in roots:
        if r == MES:
            got = mes_from_d1f(root)
        else:
            sha = tables.research_parquet_sha256.get(r)
            if sha is None:
                raise StartDatesRefusal(f"{r}: no recorded research parquet sha256 (E.2a)")
            got = product_start_rule(r, research_path=research_parquet_path(r, Path(research_root)),
                                     step2_path=step2_parquet_path(r, Path(step2_root)),
                                     research_sha256=sha, window=windows[r])
        products[r] = dict(got.entry)
        inputs.extend(got.inputs)
    return {
        "schema": SCHEMA, "set": set_id,
        "rule": "docs/STAGE_E_DESIGN.md D4; docs/NULL_CRITERIA_E.md 4; docs/NULL_CRITERIA.md 4.1",
        "day_session": DAY_SESSION_RULE,
        "products": products,
        "inputs": [{"path": p, "sha256": s} for p, s in inputs],
        "harness_sha256": harness,
        "created_pdt": datetime.now(PDT).isoformat(timespec="seconds"),
    }


def write_start_rule(doc: Mapping[str, Any], root: Path = REPO_ROOT) -> Path:
    """Write the set's file once, read-only; the document must pass the loader's own checks."""
    set_id = check_set(str(doc.get("set")))
    path = start_rule_path(set_id, root)
    _parse_doc(path.name, dict(doc))
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(doc, indent=2, sort_keys=True) + "\n"
    try:
        with path.open("x", encoding="utf-8") as fh:
            fh.write(data)
    except FileExistsError as exc:
        raise StartDatesRefusal(f"{_display(path, root)} already exists; a start-rule file is "
                                "written once") from exc
    path.chmod(0o444)
    return path


def run_set(set_id: str, *, harness_sha256: str, research_root: Path = PROCESSED_ROOT,
            step2_root: Path = STEP2_ROOT, root: Path = REPO_ROOT) -> Path:
    doc = build_set(set_id, harness_sha256=harness_sha256, research_root=research_root,
                    step2_root=step2_root, root=root)
    return write_start_rule(doc, root)


# ------------------------------------------------------------------- loader ----
@dataclass(frozen=True)
class StartDateEntry:
    root_symbol: str
    s_x: date | None  # None: no month qualifies, the confirmation window is empty
    sources: tuple[tuple[str, str], ...]  # (file path relative to the repository, sha256)
    step2_sha256: str  # the step 2 parquet the medians came from; confirmation reads must match


def start_rule_files(root: Path = REPO_ROOT) -> tuple[Path, ...]:
    return tuple(sorted((Path(root) / REPORTS_DIR).glob(FILE_GLOB)))


def _day(name: str, root_symbol: str, what: str, value: object) -> date:
    invalid = _runner().StartRuleInvalid
    try:
        day = date.fromisoformat(str(value))
    except ValueError as exc:
        raise invalid(f"{name}: {root_symbol} {what} {value!r} is not an ISO date") from exc
    if day.isoformat() != value:
        raise invalid(f"{name}: {root_symbol} {what} {value!r} is not in YYYY-MM-DD form")
    return day


def _s_x(name: str, root_symbol: str, value: object) -> date | None:
    if value is None:
        return None
    day = _day(name, root_symbol, "s_x", value)
    if not EARLIEST_START <= day <= LAST_CONFIRMATION_DATE:
        raise _runner().StartRuleInvalid(f"{name}: {root_symbol} s_x {value!r} is outside "
                                         f"{EARLIEST_START}..{LAST_CONFIRMATION_DATE}")
    return day


MONTH_KEY = re.compile(r"^\d{4}-\d{2}$")
SHA256_KEY = re.compile(r"^[0-9a-f]{64}$")
RECORDED_BY_RULE = ("s_x", "s_x_015", "s_x_040", "v_ref", "m_star")


@dataclass(frozen=True)
class _RootValues:
    """What a file says about one root; two files must agree on all of it (ruling on Q-4)."""

    s_x: date | None
    v_ref: float
    monthly_medians: tuple[tuple[str, float | None], ...]
    first_trade_dates: tuple[tuple[str, str], ...]
    step2_sha256: str


def _number(value: object) -> bool:
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(float(value)))


def _medians(name: str, root_symbol: str, entry: dict) -> dict[str, float | None]:
    medians = entry.get("monthly_medians")
    if not isinstance(medians, dict):
        raise _runner().StartRuleInvalid(f"{name}: {root_symbol} has no monthly_medians mapping")
    for month, value in medians.items():
        if not (MONTH_KEY.match(str(month)) and (month in REFERENCE_MONTHS
                                                  or month in EXTENSION_MONTHS)) or not (
                value is None or (_number(value) and float(value) >= 0.0)):
            raise _runner().StartRuleInvalid(
                f"{name}: {root_symbol} monthly median {month!r}: {value!r} is not a reference "
                "or extension month with a finite median >= 0 or null")
    return {str(m): None if v is None else float(v) for m, v in medians.items()}


def _first_dates(name: str, root_symbol: str, entry: dict) -> dict[str, date]:
    first = entry.get("first_trade_dates")
    if not isinstance(first, dict):
        raise _runner().StartRuleInvalid(f"{name}: {root_symbol} has no first_trade_dates mapping")
    return {str(m): _day(name, root_symbol, f"first trade date of {m}", d)
            for m, d in first.items()}


def _check_follows(name: str, root_symbol: str, entry: dict, medians: Mapping[str, float | None],
                   first: Mapping[str, date]) -> None:
    """Review F-3 (a): re-run D4's rule on the entry's own medians and first trade dates; the
    recorded s_x, v_ref, sensitivity dates and M* must be what the rule gives."""
    rt = _runner()
    reference = {m: v for m, v in medians.items() if m in REFERENCE_MONTHS}
    extension = {m: v for m, v in medians.items() if m in EXTENSION_MONTHS}
    try:
        rule = start_rule(root_symbol, reference, extension, first)
    except ValueError as exc:
        raise rt.StartRuleInconsistent(f"{name}: {root_symbol}: its monthly_medians and "
                                       f"first_trade_dates do not re-run D4's rule: {exc}") from exc
    low, high = rule.sensitivity
    rerun = {"s_x": _iso(rule.s_x), "s_x_015": _iso(low.s), "s_x_040": _iso(high.s),
             "v_ref": rule.v_ref,
             "m_star": {"0.25": rule.binding.m_star, "0.15": low.m_star, "0.40": high.m_star}}
    differ = [k for k in RECORDED_BY_RULE if entry.get(k) != rerun[k]]
    if differ:
        shown = ", ".join(f"{k} recorded {entry.get(k)!r}, re-run {rerun[k]!r}" for k in differ)
        raise rt.StartRuleInconsistent(f"{name}: {root_symbol}: {differ} do not follow from its "
                                       f"own monthly_medians and first_trade_dates ({shown})")


def _root_values(name: str, root_symbol: str, entry: object) -> _RootValues:
    invalid = _runner().StartRuleInvalid
    if not isinstance(entry, dict) or "s_x" not in entry:
        raise invalid(f"{name}: {root_symbol} has no s_x")
    s_x = _s_x(name, root_symbol, entry["s_x"])
    v_ref = entry.get("v_ref")
    if not _number(v_ref) or not float(v_ref) > 0.0:
        raise invalid(f"{name}: {root_symbol} v_ref {v_ref!r} is not a finite number > 0")
    medians = _medians(name, root_symbol, entry)
    first = _first_dates(name, root_symbol, entry)
    step2_sha = entry.get("step2_sha256")
    if not isinstance(step2_sha, str) or not SHA256_KEY.match(step2_sha):
        raise invalid(f"{name}: {root_symbol} step2_sha256 {step2_sha!r} is not a sha256")
    _check_follows(name, root_symbol, entry, medians, first)
    return _RootValues(s_x, float(v_ref), tuple(sorted(medians.items())),
                       tuple(sorted((m, d.isoformat()) for m, d in first.items())), step2_sha)


def _parse_doc(name: str, doc: Any) -> dict[str, _RootValues]:
    invalid = _runner().StartRuleInvalid
    match = FILE_PATTERN.match(name)
    if match is None:
        raise invalid(f"{name}: not a stage_e_start_rule_<K1..K8|ML>.json file name")
    if not isinstance(doc, dict) or doc.get("schema") != SCHEMA:
        schema = doc.get("schema") if isinstance(doc, dict) else None
        raise invalid(f"{name}: schema {schema!r} is not {SCHEMA!r}")
    if doc.get("set") != match.group(1):
        raise invalid(f"{name}: set {doc.get('set')!r} is not the file's {match.group(1)!r}")
    products = doc.get("products")
    if not isinstance(products, dict) or not products:
        raise invalid(f"{name}: no products")
    return {str(r): _root_values(name, str(r), e) for r, e in products.items()}


def _parse_file(path: Path) -> tuple[str, dict[str, _RootValues]]:
    raw = path.read_bytes()
    try:
        doc = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise _runner().StartRuleInvalid(f"{path.name}: not valid JSON ({exc})") from exc
    return hashlib.sha256(raw).hexdigest(), _parse_doc(path.name, doc)


def _differences(items: Sequence[tuple[_RootValues, str, str]]) -> list[str]:
    first = items[0][0]
    fields = []
    for name in ("s_x", "v_ref", "monthly_medians", "first_trade_dates", "step2_sha256"):
        if any(getattr(v, name) != getattr(first, name) for v, _, _ in items[1:]):
            fields.append(name)
    return fields


def load_start_entries(root: Path = REPO_ROOT) -> Mapping[str, StartDateEntry]:
    """Every per-set file merged, root by root. Each entry must follow from its own medians
    (review F-3); two files that differ on a root's S_X, V_ref, any monthly median, the first
    trade dates or the step 2 store's sha256 refuse (StartRuleConflict, lead ruling on Q-4)."""
    found: dict[str, list[tuple[_RootValues, str, str]]] = {}
    for path in start_rule_files(root):
        digest, values = _parse_file(path)
        rel = (REPORTS_DIR / path.name).as_posix()
        for root_symbol, value in values.items():
            found.setdefault(root_symbol, []).append((value, rel, digest))
    out: dict[str, StartDateEntry] = {}
    for root_symbol, items in sorted(found.items()):
        differ = _differences(items)
        if differ:
            detail = "; ".join(f"{rel}: s_x {_iso(v.s_x)}, v_ref {v.v_ref}" for v, rel, _ in items)
            raise _runner().StartRuleConflict(f"{root_symbol}: the start-rule files differ on "
                                              f"{differ} ({detail})")
        out[root_symbol] = StartDateEntry(root_symbol, items[0][0].s_x,
                                          tuple((rel, d) for _, rel, d in items),
                                          items[0][0].step2_sha256)
    return MappingProxyType(out)


def load_start_dates(root: Path = REPO_ROOT) -> Mapping[str, date]:
    """S_X of every root a start-rule file gives a date (empty windows left out)."""
    return MappingProxyType({r: e.s_x for r, e in load_start_entries(root).items()
                             if e.s_x is not None})


def _date_of(entries: Mapping[str, StartDateEntry], root_symbol: str) -> date:
    rt = _runner()
    entry = entries.get(root_symbol)
    if entry is None:
        raise rt.StartRuleMissing(f"no frozen S_X for {root_symbol}: no reports/"
                                  "stage_e_start_rule_<SET>.json lists it (built by "
                                  "screening.stage_e_start_dates from the step 2 store)")
    if entry.s_x is None:
        files = ", ".join(p for p, _ in entry.sources)
        raise rt.StartWindowEmpty(f"{root_symbol}: the start rule found no qualifying month "
                                  f"({files}): its confirmation window is empty (D4, "
                                  "NULL_CRITERIA 4.1)")
    return entry.s_x


def start_date(root_symbol: str, root: Path = REPO_ROOT) -> date:
    """The root's frozen S_X; StartRuleMissing (or StartWindowEmpty) when there is none."""
    return _date_of(load_start_entries(root), root_symbol)


def start_dates_for(root_symbols: Iterable[str], root: Path = REPO_ROOT, *,
                    allow_empty: bool = False) -> tuple[dict[str, date], dict[str, dict]]:
    """S_X of each root and, per root, the files (path, sha256) that give it. A root with an
    empty window raises StartWindowEmpty, unless ``allow_empty``: then it is left out of the
    dates and its provenance carries s_x None (the power check's supply of 0 days, ruling Q-3)."""
    wanted = tuple(root_symbols)
    entries = load_start_entries(root)
    missing = [r for r in wanted if r not in entries]
    if missing:
        raise _runner().StartRuleMissing(f"no frozen S_X for {missing}: no reports/"
                                         "stage_e_start_rule_<SET>.json lists them")
    empty = [r for r in wanted if entries[r].s_x is None]
    if empty and not allow_empty:
        files = ", ".join(sorted({p for r in empty for p, _ in entries[r].sources}))
        raise _runner().StartWindowEmpty(f"{empty}: the start rule found no qualifying month "
                                         f"({files}): the confirmation window is empty (D4, "
                                         "NULL_CRITERIA 4.1)")
    dates = {r: entries[r].s_x for r in wanted if entries[r].s_x is not None}
    provenance = {r: {"s_x": _iso(entries[r].s_x), "step2_sha256": entries[r].step2_sha256,
                      "files": [{"path": p, "sha256": s} for p, s in entries[r].sources]}
                  for r in wanted}
    return dates, provenance


# ---------------------------------------------------------------------- CLI ----
def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--harness-sha256", required=True)
    parser.add_argument("--set", required=True, choices=SETS, dest="set_id")
    parser.add_argument("--research-root", type=Path, default=PROCESSED_ROOT)
    parser.add_argument("--step2-root", type=Path, default=STEP2_ROOT)
    args = parser.parse_args(argv)
    from compute.platform import lower_priority

    lower_priority()
    path = run_set(args.set_id, harness_sha256=args.harness_sha256,
                   research_root=args.research_root, step2_root=args.step2_root)
    doc = json.loads(path.read_text(encoding="utf-8"))
    print(f"{args.set_id}: {len(doc['products'])} products -> {_display(path)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
