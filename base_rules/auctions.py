"""The EC-AUC Treasury auctions of H3 (lead_spec section 4 H3; freeze review F-04, lead ruling).

Rows: Task 3b's reports/stage_e16_calendars/ec_auc_2010_2019.json before 2019-05-01 (every row
carries announcemt_date, original_security_term, security_term, security_type, floating_rate,
inflation_index_security and cusip) and the frozen reports/stage_e2b_release_calendar.json
TREASURY_AUCTION rows from 2019-05-01, whose announcement dates come from
reports/stage_e16_calendars/ec_auc_announcements_2019_2024.json (schema
"stage_e16_ec_auc_announcements/1": rows {id, auction_date, tenor, announcemt_date, cusip,
original_security_term, security_term}, joined on the frozen row's id; auction date and tenor must
agree). E.0's filter applies wherever the fields exist (Note or Bond, not floating, not
inflation-indexed, announced strictly before the auction date). The tenor map: 2Y ZT, 5Y ZF,
10Y ZN, 30Y ZB; others ignored. H3 then counts an auction only if it was announced on or before
t-3 (base_rules.h3.windows; "announced after entry", "no announcement date").
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from base_rules import constants as K
from base_rules.inputs import InputError, _day, read_json


@dataclass(frozen=True)
class Auction:
    id: str
    tenor: str  # 2Y, 5Y, 10Y, 30Y
    root: str
    day: date
    instant_utc: str
    announced: date | None = None  # announcemt_date; None: not on file


ECAUC_FIELDS = ("security_type", "floating_rate", "inflation_index_security", "announcemt_date")


def _tenor(row: dict, where: str) -> str | None:
    suffix = str(row.get("id", "")).rsplit("-", 1)[-1]
    term = row.get("original_security_term")
    if term is not None:
        by_term = next((t for t, s in K.H3_TENOR_TERM.items() if str(term).strip() == s), None)
        if by_term is not None and suffix in K.H3_TENOR_ROOT and by_term != suffix:
            raise InputError(f"{where}: id tenor {suffix} != original_security_term {term!r}")
        return by_term
    return suffix if suffix in K.H3_TENOR_ROOT else None


def e0_filter(row: dict, where: str) -> str | None:
    """E.0's EC-AUC rule, each criterion where its field exists (a field present but empty
    drops the row). Returns a drop reason."""
    missing = [f for f in ECAUC_FIELDS if f in row and row.get(f) in (None, "")]
    if missing:
        return f"missing {missing}"
    if "security_type" in row and row["security_type"] not in ("Note", "Bond"):
        return "security_type"
    if any(f in row and str(row[f]) != "No" for f in ("floating_rate",
                                                      "inflation_index_security")):
        return "floating or inflation-indexed"
    if "announcemt_date" in row and not _day(row["announcemt_date"], where) < _day(
            row.get("date"), where):
        return "announced on or after the auction date"
    return None


def auctions_from_rows(rows: Iterable[dict], source: str, *, first: date | None = None,
                       before: date | None = None,
                       announcements: Mapping[str, dict] | None = None
                       ) -> tuple[list[Auction], dict[str, int]]:
    """``announcements``: id -> the announcement row (fields merged into the row first)."""
    out, dropped = [], {}
    for i, raw in enumerate(rows):
        where = f"{source} row {i}"
        if raw.get("release") != K.AUCTION_RELEASE:
            continue
        day = _day(raw.get("date"), where)
        if (first is not None and day < first) or (before is not None and day >= before):
            continue
        row = dict(raw)
        extra = (announcements or {}).get(str(row.get("id")))
        if extra is not None:
            if _day(extra.get("auction_date"), where) != day:
                raise InputError(f"{where}: announcement row {row['id']} has another auction date")
            row.update({k: v for k, v in extra.items() if k not in ("id", "auction_date",
                                                                    "tenor")})
        reason = e0_filter(row, where)
        tenor = _tenor(row, where)
        if extra is not None and tenor is not None and extra.get("tenor") != tenor:
            raise InputError(f"{where}: announcement row {row['id']} has another tenor")
        if reason is None and tenor is None:
            reason = "tenor not 2Y, 5Y, 10Y or 30Y"
        if reason is not None:
            dropped[reason] = dropped.get(reason, 0) + 1
            continue
        announced = row.get("announcemt_date")
        out.append(Auction(str(row["id"]), tenor, K.H3_TENOR_ROOT[tenor], day,
                           str(row.get("instant_utc")),
                           None if announced in (None, "") else _day(announced, where)))
    return out, dropped


def _rows_of(raw: object, source: str) -> list[dict]:
    rows = raw.get("releases", raw.get("rows")) if isinstance(raw, dict) else None
    if not isinstance(rows, list):
        raise InputError(f"{source}: no 'releases' (or 'rows') list")
    return rows


def load_announcements(path: Path) -> tuple[dict[str, dict], str]:
    raw, digest = read_json(K.repo_path(path))
    if not isinstance(raw, dict) or raw.get("schema") != K.ANNOUNCEMENTS_SCHEMA:
        raise InputError(f"{path}: schema is not {K.ANNOUNCEMENTS_SCHEMA!r}")
    out: dict[str, dict] = {}
    for i, row in enumerate(raw.get("rows") or []):
        where = f"{path} row {i}"
        missing = [k for k in ("id", "auction_date", "tenor", "announcemt_date") if not row.get(k)]
        if missing:
            raise InputError(f"{where}: missing {missing}")
        if row["id"] in out:
            raise InputError(f"{where}: id {row['id']} listed twice")
        _day(row["announcemt_date"], where)
        out[str(row["id"])] = dict(row)
    return out, digest


def load_auctions(hist_path: Path | None = K.ECAUC_HIST_PATH,
                  frozen_path: Path = K.RELEASE_FROZEN_PATH,
                  announcements_path: Path | None = K.ANNOUNCEMENTS_PATH
                  ) -> tuple[list[Auction], dict]:
    """EC-AUC auctions: the hist file's rows before 2019-05-01 and the frozen calendar's from
    2019-05-01 with their announcement dates (``announcements_path`` None: no dates for them)."""
    frozen, fsha = read_json(K.repo_path(frozen_path))
    ann, asha = ({}, None) if announcements_path is None else load_announcements(
        announcements_path)
    rows, drops = auctions_from_rows(_rows_of(frozen, str(frozen_path)), str(frozen_path),
                                     first=K.FROZEN_CAL_FIRST, announcements=ann)
    record = {"frozen": {"path": str(frozen_path), "sha256": fsha, "rows": len(rows),
                         "dropped": drops},
              "announcements": {"path": str(announcements_path), "sha256": asha,
                                "rows": len(ann)}}
    if hist_path is not None:
        hist, hsha = read_json(K.repo_path(hist_path))
        h_rows, h_drops = auctions_from_rows(_rows_of(hist, str(hist_path)), str(hist_path),
                                             before=K.FROZEN_CAL_FIRST)
        rows = h_rows + rows
        record["hist"] = {"path": str(hist_path), "sha256": hsha, "rows": len(h_rows),
                          "dropped": h_drops}
    ids = [a.id for a in rows]
    if len(set(ids)) != len(ids):
        raise InputError("duplicate EC-AUC row ids across the two files")
    return sorted(rows, key=lambda a: (a.day, a.tenor)), record


__all__ = ["ECAUC_FIELDS", "Auction", "auctions_from_rows", "e0_filter", "load_announcements",
           "load_auctions"]
