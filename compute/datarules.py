"""What data may leave the ThinkPad for a compute job, checked at both ends (Stage E.2b, V10-4/5).

The send side (compute.remote) refuses, before any byte is sent, and the far side (compute.agent)
checks again before a job starts:
- anything in a sealed holdout store (data/sealed/), any file with the sealed suffix or whose
  bytes start with the sealing magic;
- any bar booked to a holdout-1 trade date (>= 2026-06-22), a holdout-2 trade date
  (2024-04-01..2025-03-31) or the March 2024 embargo, and any bar outside its store's window,
  judged from the rows, never from the name: first the trade_date column and the metadata's
  trade_date_range, then every row's timestamp booked by its product's CME group calendar with
  the Stage E loader's own check (data.stage_e_bars.check_bookings, ruling L-9), so a bar the
  file labels 2026-06-19 but CME books to 2026-06-22 (MBT's case) is refused too;
- the Databento key: a .env file, or any file whose bytes contain the key's value (send side
  only: the far side never holds the key, so its re-check is the sha256 binding every received
  file to the file the send side scanned);
- the ledger (ledger/, the external ledgers of data.config, any *spend*.jsonl).
Only two bar stores travel, each by its exact file-name allowlist: the step 2 (training-window)
store and the Stage E research store. An ML training job's data root holds only step 2 files;
the research store goes to the separate backtest root, which a training job is never given. A
training root holding anything else refuses the job (M7.4, ML-A23, V10-5).

Every refusal raises ``DataRuleRefused`` naming its kind and the file; nothing is skipped.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from compute.files import CHUNK_BYTES, sha256_file
from data.research_bars import EMBARGO2, HOLDOUT1, HOLDOUT2, trade_date_class

# The sealing magic of data.holdout (pinned equal by tests/test_compute_datarules.py; the far
# side does not import the ThinkPad-only sealing module).
SEALED_MAGIC = b"PROPEXP-SEALED-1\n"
SEALED_SUFFIX = ".sealed"
FORBIDDEN_DATE_CLASSES = (HOLDOUT1, HOLDOUT2, EMBARGO2)
PRODUCT_RE = re.compile(r"^[0-9A-Z]+$")

STEP2 = "step2"
RESEARCH = "research"
# store -> (file name pattern, first and last trade date allowed). Names and windows are those of
# data.step2_store.step2_parquet_path and data.build_bars.research_parquet_path (pinned by tests).
STORES: dict[str, tuple[re.Pattern[str], date, date]] = {
    STEP2: (re.compile(r"^ohlcv-1m_([0-9A-Z]+)_v_0_2019-05-06_2024-02-29_step2\.parquet$"),
            date(2019, 5, 6), date(2024, 2, 29)),
    RESEARCH: (re.compile(r"^ohlcv-1m_([0-9A-Z]+)_v_0_2025-04-01_2026-06-19_research\.parquet$"),
               date(2025, 4, 1), date(2026, 6, 19)),
}

TRAINING = "training"
BACKTEST = "backtest"
NO_DATA = "none"
DATA_ROOT_KINDS = (TRAINING, BACKTEST, NO_DATA)
# data root kind -> the stores it may hold. A training root holds the step 2 store only.
ROOT_STORES = {TRAINING: (STEP2,), BACKTEST: (RESEARCH, STEP2), NO_DATA: ()}
DATA_DIR = "data"  # under the far side's agent root: data/training/..., data/backtest/...

META_KEY = b"propexperiment"
LEDGER_NAME_RE = re.compile(r".*spend.*\.jsonl$", re.IGNORECASE)


class DataRuleRefused(RuntimeError):
    """A file may not be sent to, or used on, the far side. ``kind`` names the rule."""

    def __init__(self, kind: str, path: object, detail: str) -> None:
        super().__init__(f"REFUSED [{kind}] {path}: {detail}")
        self.kind = kind
        self.path = str(path)


@dataclass(frozen=True)
class DataRules:
    """Where the forbidden things live on the send side."""

    sealed_roots: tuple[Path, ...]
    ledger_paths: tuple[Path, ...]
    env_files: tuple[Path, ...]


def default_rules() -> DataRules:
    from data.config import ACCOUNTS, DATA_ROOT, ENV_FILE, EXTERNAL_LEDGER_PATHS, LEDGER_PATH

    external = tuple(p for account in ACCOUNTS.values() for p in account.external_ledger_paths)
    return DataRules(
        sealed_roots=(DATA_ROOT / "sealed",),
        ledger_paths=(LEDGER_PATH.parent, LEDGER_PATH, *EXTERNAL_LEDGER_PATHS, *external),
        env_files=(ENV_FILE,),
    )


@dataclass(frozen=True)
class DataFile:
    """One bar file of a job, as the send side checked it."""

    store: str
    product: str
    name: str
    sha256: str
    bytes: int
    first_trade_date: str
    last_trade_date: str
    trade_dates: int

    def dest(self, data_root_kind: str) -> str:
        """The file's path under the far side's agent root (POSIX)."""
        return dest_relpath(data_root_kind, self.store, self.product, self.name)

    def as_dict(self) -> dict[str, object]:
        return dict(self.__dict__)

    @classmethod
    def from_dict(cls, raw: dict) -> DataFile:
        return cls(**{k: raw[k] for k in cls.__dataclass_fields__})


def data_root_relpath(data_root_kind: str) -> str:
    if data_root_kind not in (TRAINING, BACKTEST):
        raise DataRuleRefused("data-root", data_root_kind, "has no data root")
    return f"{DATA_DIR}/{data_root_kind}"


def dest_relpath(data_root_kind: str, store: str, product: str, name: str) -> str:
    if store not in ROOT_STORES.get(data_root_kind, ()):
        raise DataRuleRefused("not-allowlisted", name, f"a {store} file may not go to a "
                              f"{data_root_kind} data root")
    base = data_root_relpath(data_root_kind)
    return f"{base}/{product}/{name}" if data_root_kind == TRAINING else \
        f"{base}/{store}/{product}/{name}"


def store_of(name: str) -> tuple[str, str] | None:
    """(store, product) for an allowlisted bar-file name, else None."""
    for store, (pattern, _, _) in STORES.items():
        match = pattern.match(name)
        if match:
            return store, match.group(1)
    return None


def _inside(path: Path, root: Path) -> bool:
    return path == root or path.is_relative_to(root)


def check_location(path: Path, rules: DataRules | None) -> None:
    """Refuse by where a file lives and what it is called (both spellings: as given, resolved)."""
    given = Path(path).absolute()
    resolved = Path(path).resolve()
    for candidate in (given, resolved):
        name = candidate.name
        if name.endswith(SEALED_SUFFIX):
            raise DataRuleRefused("sealed-suffix", path, "a sealed holdout file")
        if "sealed" in candidate.parts:
            raise DataRuleRefused("sealed-store", path, "inside a directory named 'sealed'")
        if name == ".env" or name.startswith(".env."):
            raise DataRuleRefused("secret-env", path, "an environment file (the key's home)")
        if LEDGER_NAME_RE.match(name) or "ledger" in candidate.parts:
            raise DataRuleRefused("ledger", path, "a spend ledger")
        if rules is None:
            continue
        for root in rules.sealed_roots:
            if _inside(candidate, root.absolute()) or _inside(candidate, root.resolve()):
                raise DataRuleRefused("sealed-store", path, f"inside the sealed store {root}")
        for ledger in rules.ledger_paths:
            if _inside(candidate, ledger.absolute()):
                raise DataRuleRefused("ledger", path, f"the ledger {ledger}")
        for env in rules.env_files:
            if candidate == env.absolute() or candidate == env.resolve():
                raise DataRuleRefused("secret-env", path, "the repository's .env")


def file_contains(path: Path, needle: bytes) -> bool:
    if not needle:
        raise ValueError("an empty needle matches everything")
    overlap = len(needle) - 1
    tail = b""
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(CHUNK_BYTES), b""):
            window = tail + block
            if needle in window:
                return True
            tail = window[-overlap:] if overlap else b""
    return False


def check_content_head(path: Path) -> None:
    with Path(path).open("rb") as handle:
        head = handle.read(len(SEALED_MAGIC))
    if head == SEALED_MAGIC:
        raise DataRuleRefused("sealed-content", path, "its bytes are a sealed holdout blob")


def _as_date(value: object, path: Path) -> date:
    if isinstance(value, datetime):
        raise DataRuleRefused("no-trade-date", path, "trade_date holds timestamps, not dates")
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError as exc:
            raise DataRuleRefused("no-trade-date", path, f"trade_date {value!r} is not "
                                  "YYYY-MM-DD") from exc
    raise DataRuleRefused("no-trade-date", path, f"trade_date value {value!r} is not a date")


def parquet_trade_dates(path: Path) -> tuple[list[date], dict | None]:
    """The distinct trade dates of a parquet, read from its trade_date column, and its
    'propexperiment' metadata (None when absent)."""
    import pyarrow as pa
    import pyarrow.compute as pc
    import pyarrow.parquet as pq

    try:
        handle = pq.ParquetFile(path)
    except (pa.ArrowException, OSError) as exc:
        raise DataRuleRefused("not-parquet", path, f"not a readable parquet ({exc})") from exc
    schema = handle.schema_arrow
    if "trade_date" not in schema.names:
        raise DataRuleRefused("no-trade-date", path, "no trade_date column; its dates cannot "
                              "be checked")
    column = handle.read(columns=["trade_date"]).column("trade_date")
    if column.null_count:
        raise DataRuleRefused("no-trade-date", path, f"{column.null_count} rows have no "
                              "trade date")
    days = sorted({_as_date(v, path) for v in pc.unique(column).to_pylist()})
    raw_meta = (schema.metadata or {}).get(META_KEY)
    meta = None
    if raw_meta is not None:
        try:
            meta = json.loads(raw_meta)
        except json.JSONDecodeError as exc:
            raise DataRuleRefused("metadata", path, f"unreadable {META_KEY!r} metadata") from exc
    return days, meta


def check_trade_dates(path: Path, store: str, days: list[date], meta: dict | None) -> None:
    if not days:
        raise DataRuleRefused("empty", path, "no rows")
    for day in days:
        cls = trade_date_class(day)
        if cls in FORBIDDEN_DATE_CLASSES:
            raise DataRuleRefused("holdout-date", path, f"a bar booked to {cls} trade date {day}")
    _, first, last = STORES[store]
    if days[0] < first or days[-1] > last:
        raise DataRuleRefused("outside-window", path, f"trade dates {days[0]}..{days[-1]} "
                              f"leave the {store} window {first}..{last}")
    if not isinstance(meta, dict) or "trade_date_range" not in meta:
        raise DataRuleRefused("metadata", path, "no 'propexperiment' trade_date_range metadata")
    if list(meta["trade_date_range"]) != [days[0].isoformat(), days[-1].isoformat()]:
        raise DataRuleRefused("metadata", path, f"metadata trade_date_range "
                              f"{meta['trade_date_range']} differs from the rows' "
                              f"{days[0]}..{days[-1]}")
    if store == STEP2 and meta.get("store") != STEP2:
        raise DataRuleRefused("metadata", path, "a step 2 file whose metadata store is "
                              f"{meta.get('store')!r}, not 'step2'")


def check_calendar_bookings(path: Path, store: str, product: str) -> None:
    """Book every row's timestamp on the product's CME group calendar and refuse any row booked
    to a holdout, embargo or out-of-store trade date, any unbookable row and any row whose
    trade_date label differs from its booking: the Stage E loader's own check."""
    import pandas as pd

    from data import stage_e_bars as loader
    from data.group_session import load_group_calendar
    from rules.products import UnknownProduct
    from rules.products import product as product_spec

    try:
        group = product_spec(product).group
    except UnknownProduct as exc:
        raise DataRuleRefused("unknown-product", path, str(exc)) from exc
    try:
        frame = pd.read_parquet(path, columns=["ts_event", "trade_date"])
    except (KeyError, ValueError) as exc:
        raise DataRuleRefused("no-timestamps", path, f"no ts_event column ({exc})") from exc
    frame = frame.sort_values("ts_event", kind="stable").reset_index(drop=True)
    where = f"{store} file {Path(path).name}"
    try:
        loader.check_bookings(product, load_group_calendar(group), frame, store, where)
    except loader.HoldoutRowRefused as exc:
        text = str(exc)
        kind = "holdout-date" if ("holdout" in text or "embargo" in text) else "outside-window"
        raise DataRuleRefused(kind, path, text) from exc
    except loader.TradeDateUnbookable as exc:
        raise DataRuleRefused("unbookable", path, str(exc)) from exc
    except loader.TradeDateMismatch as exc:
        raise DataRuleRefused("label-mismatch", path, str(exc)) from exc


def check_bar_file(path: Path, *, allowed_stores: tuple[str, ...],
                   rules: DataRules | None, key: bytes | None) -> DataFile:
    """Every rule for one bar file; returns its record. ``key`` None skips the key scan (the far
    side, which never holds the key); ``rules`` None skips the ThinkPad location rules."""
    path = Path(path)
    check_location(path, rules)
    if path.is_symlink() or not path.is_file():
        raise DataRuleRefused("not-a-regular-file", path, "missing, a link or not a file")
    check_content_head(path)
    if key is not None and file_contains(path, key):
        raise DataRuleRefused("secret-key", path, "its bytes contain the Databento key")
    found = store_of(path.name)
    if found is None:
        raise DataRuleRefused("not-allowlisted", path, "not a step 2 or research store file name")
    store, product = found
    if store not in allowed_stores:
        raise DataRuleRefused("not-allowlisted", path, f"a {store} file; this data root takes "
                              f"{', '.join(allowed_stores) or 'no data'}")
    days, meta = parquet_trade_dates(path)
    check_trade_dates(path, store, days, meta)
    check_calendar_bookings(path, store, product)
    return DataFile(store, product, path.name, sha256_file(path), path.stat().st_size,
                    days[0].isoformat(), days[-1].isoformat(), len(days))


def check_data_root(root: Path, data_root_kind: str) -> list[DataFile]:
    """The far side's whole data root of one kind: every entry must be an allowlisted store file
    at its layout path and pass the content rules. Anything else refuses the job."""
    root = Path(root)
    kind = "training-root" if data_root_kind == TRAINING else "backtest-root"
    if not root.is_dir():
        raise DataRuleRefused(kind, root, "the data root does not exist")
    out = []
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if path.is_dir() and not path.is_symlink():
            depth_ok = len(rel.parts) <= (1 if data_root_kind == TRAINING else 2)
            if not depth_ok:
                raise DataRuleRefused(kind, rel.as_posix(), "an unexpected directory")
            continue
        found = store_of(rel.name)
        expected = None
        if found is not None and found[0] in ROOT_STORES[data_root_kind]:
            expected = dest_relpath(data_root_kind, found[0], found[1], rel.name)
        actual = f"{data_root_relpath(data_root_kind)}/{rel.as_posix()}"
        if expected != actual:
            raise DataRuleRefused(kind, rel.as_posix(), f"not on the {data_root_kind} root's "
                                  "allowlist (only " + " and ".join(ROOT_STORES[data_root_kind])
                                  + " store files at their layout paths)")
        out.append(check_bar_file(path, allowed_stores=ROOT_STORES[data_root_kind], rules=None,
                                  key=None))
    return out
