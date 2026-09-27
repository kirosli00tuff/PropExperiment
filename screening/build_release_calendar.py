"""Stage E release calendar: the assembler (Stage E.2b, lead rulings OC-J and OC-N).

    uv run --no-sync python -m screening.build_release_calendar           # build, write once
    uv run --no-sync python -m screening.build_release_calendar --check   # rebuild in memory,
                                                                           # compare to the file

Writes reports/stage_e2b_release_calendar.json (schema "stage_e_release_calendar/1", read by
screening.stage_e_rules.load_release_calendar and, through it, ml_route.inputs.load_event_calendar)
and its summary reports/stage_e2b_release_calendar.md. Both are written once, read-only; an
existing file is never overwritten. The JSON has no timestamp, so ``--check`` reproduces it byte
for byte from the same inputs.

Sources (every release instant 2019-05-01..2026-06-21): reports/stage_e2b_release_sources_macro.json
(NFP, CPI, FOMC), ..._commodity.json (WPSR, NGS, CROP, CROP_ANNUAL, WASDE), ..._named.json (PPI,
ISM_SERVICES, G17, API_WSB, CROP_PROGRESS, TREASURY_AUCTION). A source whose log still says
"STATUS: DRAFT" is refused.

Which products a release concerns (design D8: "Topstep's release table, F6.4, plus the releases the
product's catalog members name"; lead ruling OC-N):
- F6.4 (reports/stage_e0_topstep_facts.json, fact F6.4, verbatim in ``F6_4_QUOTE`` and checked
  against the file): Unemployment Rate = NFP, FOMC Statement = FOMC, Crude Oil Inventories (EIA) =
  WPSR, Natural Gas Inventories (EIA) = NGS, Crop Production = CROP and CROP_ANNUAL (NASS titles
  the annual summary "Crop Production"; lead ruling: keep both entries). The listed roots, and
  FOMC's "All products" = every root of the product universe: reports/stage_e2a_vehicles.json
  (admissible contracts, vehicles, contracts), reports/stage_e0_liquidity.json (products) and the
  ML route's 31 price-path contracts (ml_route.constants.PRICE_PATH_CONTRACTS).
- F6.4's note "**Micro contracts also apply": every F6.4 row also concerns each listed root's micro
  siblings, read from rules/products.py: the products with the same ``exposure`` whose
  ``contract_type`` is MICRO or SIL (Micro Silver) (e.g. NQ -> MNQ, ES -> MES, SI -> SIL).
- Member-named releases (reports/stage_e2b_release_names.json, cross-checked against the frozen
  reports/stage_e0_catalog.json): a release concerns every product traded by a member that names it
  (signal or mentioned, any catalog status: PPI and Crop Progress are named only by members the ML
  route superseded, and the lead's list includes them). A member's traded exposures are the
  catalog's "exposures" words; each word maps to its exposure in reports/stage_e2a_vehicles.json
  and from there to the exposure's frozen vehicle root and its ML price-path root.
- CPI entries carry "cpi": true (D9.12).
- Excluded by ruling (not releases of information, and daily, so already inside E.2a's
  time-of-day cost buckets): the ECB, London 4pm and Tokyo fixes, the LBMA auctions, CME CF BRR.
Roots outside the engine's product table (rules.products.PRODUCTS) are not written, because the
loader calls rules.products.product on every root and refuses an unknown one; they are listed
under "not_in_product_table".

Checks (any failure raises CalendarBuildRefused naming the case; nothing is written):
- frozen inputs match their recorded sha256 (E.1 freeze manifest; E.2a's vehicles hash);
- each source's coverage is 2019-05-01..2026-06-21; every coverage-table row (release x year)
  has expected = found + unverified + cancelled, and found / unverified / cancelled recount from
  the entries and cancellation records;
- every entry's quote occurs verbatim (whitespace normalised) in its saved page, and every
  cancellation's and move's evidence quote in its page; every instant_utc equals date +
  time_local in tz; ids unique; dates inside the coverage; instants on a minute;
- every release has at least one product; each exposure's vehicle and ML price-path root get the
  same instant list (ml_route refuses otherwise); the runner's loader reads the result.
[unverified] entries and the API bulletin's "announced_schedule" entries are kept (dropping them
would understate the event-window cost) and counted in "verification".
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import sys
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from types import MappingProxyType
from typing import Any
from zoneinfo import ZoneInfo

from data.config import REPO_ROOT
from ml_route.constants import PRICE_PATH_CONTRACTS
from rules.products import PRODUCTS, ContractType
from screening.build_release_calendar_checks import (  # noqa: F401 (re-exported)
    ANNOUNCED,
    COVERAGE_FIRST,
    COVERAGE_LAST,
    DRAFT_MARK,
    UNVERIFIED_MARK,
    YEARS,
    CalendarBuildRefused,
    Pages,
    _refuse,
    check_source,
    evidence_of,
    instant_matches,
    verify_entries,
    verify_evidence,
)
from screening.stage_e_frozen import E2A_TABLES
from screening.stage_e_rules import (
    RELEASE_CALENDAR_PATH,
    RELEASE_CALENDAR_SCHEMA,
    release_calendar_from_dict,
)

OUT_JSON = RELEASE_CALENDAR_PATH
OUT_MD = "reports/stage_e2b_release_calendar.md"
BUILT_BY = "screening/build_release_calendar.py"
PDT = ZoneInfo("America/Vancouver")

# source name -> (entries file, its log)
SOURCES: Mapping[str, tuple[str, str]] = MappingProxyType({
    "macro": ("reports/stage_e2b_release_sources_macro.json",
              "reports/stage_e2b_release_sources_macro_log.md"),
    "commodity": ("reports/stage_e2b_release_sources_commodity.json",
                  "reports/stage_e2b_release_sources_commodity_log.md"),
    "named": ("reports/stage_e2b_release_sources_named.json",
              "reports/stage_e2b_release_sources_named_log.md"),
})
NAMES_PATH = "reports/stage_e2b_release_names.json"
FREEZE_MANIFEST = "reports/stage_e1_freeze.json"
FACTS_PATH = "reports/stage_e0_topstep_facts.json"
LIQUIDITY_PATH = "reports/stage_e0_liquidity.json"
CATALOG_PATH = "reports/stage_e0_catalog.json"
E0_FROZEN: tuple[str, ...] = (FACTS_PATH, LIQUIDITY_PATH, CATALOG_PATH)  # hashes: E.1 manifest
VEHICLES_PATH, VEHICLES_SHA256 = E2A_TABLES["vehicles"]

# release code -> the source file that lists it (lead ruling OC-N)
RELEASE_SOURCE: Mapping[str, str] = MappingProxyType({
    "NFP": "macro", "CPI": "macro", "FOMC": "macro",
    "WPSR": "commodity", "NGS": "commodity", "CROP": "commodity", "CROP_ANNUAL": "commodity",
    "WASDE": "commodity",
    "PPI": "named", "ISM_SERVICES": "named", "G17": "named", "API_WSB": "named",
    "CROP_PROGRESS": "named", "TREASURY_AUCTION": "named",
})
CPI_CODES = frozenset({"CPI"})

# ---- Topstep F6.4 (reports/stage_e0_topstep_facts.json), verbatim ------------------------------
F6_4_ID = "F6.4"
F6_4_QUOTE = (
    "Unemployment Rate 7:30 AM CT - ES, NKD, NQ, 6A, 6B, 6C, 6E, 6J, 6S, E7, GE, YM, UB, ZT, ZF, "
    "ZN, ZB, GC, RTY, SI, HG, TN, 6M, M6A, M6E, 6N, MBT, MET. FOMC Statement 1:00 PM CT - All "
    "products. Crude Oil Inventories (EIA) 9:30 AM / 10:00 AM* CT - CL, QM, MCL, RB. Natural Gas "
    "Inventories (EIA) 9:30 AM CT - NG, QG. Crop Production 11:00 AM CT - ZC, ZS, ZW, ZM, ZL.")
F6_4_MICRO_NOTE = "**Micro contracts also apply."
ALL_PRODUCTS = "All products"
F6_4_CODES: Mapping[str, tuple[str, ...]] = MappingProxyType({
    "Unemployment Rate": ("NFP",),
    "FOMC Statement": ("FOMC",),
    "Crude Oil Inventories (EIA)": ("WPSR",),
    "Natural Gas Inventories (EIA)": ("NGS",),
    "Crop Production": ("CROP", "CROP_ANNUAL"),
})
_F6_4_ROW = re.compile(
    r"(?P<name>[A-Z][A-Za-z ()]*?) (?P<time>\d{1,2}:\d{2} [AP]M(?: / \d{1,2}:\d{2} [AP]M\*)?) CT"
    r" - (?P<listed>[^.]+)\.(?: |$)")
# "**Micro contracts also apply": the contract types rules/products.py marks as micro
MICRO_TYPES = frozenset({ContractType.MICRO, ContractType.SIL})

# ---- member-named releases (reports/stage_e2b_release_names.json), lead ruling OC-N -----------
NAMED_CODES: Mapping[str, tuple[str, ...]] = MappingProxyType({
    "API weekly petroleum inventory bulletin": ("API_WSB",),
    "CPI release": ("CPI",),
    "Crude Oil Inventories (EIA WPSR)": ("WPSR",),
    "Employment Situation / Unemployment Rate release (NFP)": ("NFP",),
    "FOMC Statement": ("FOMC",),
    "G.17 Industrial Production and Capacity Utilization release (Federal Reserve)": ("G17",),
    "ISM Services (Non-Manufacturing) PMI release": ("ISM_SERVICES",),
    "Natural Gas Inventories (EIA)": ("NGS",),
    "PPI release": ("PPI",),
    "Treasury note/bond auction": ("TREASURY_AUCTION",),
    "USDA NASS Crop Progress release": ("CROP_PROGRESS",),
    "WASDE / Crop Production release": ("WASDE", "CROP", "CROP_ANNUAL"),
})
EXCLUSION_REASON = ("lead ruling OC-N: not a release of information, and daily, so already inside "
                    "E.2a's time-of-day cost buckets")
EXCLUDED_BY_RULING: frozenset[str] = frozenset({
    "CME CF Bitcoin Reference Rate (BRR) final settlement",
    "ECB reference-rate fix (WM/Reuters)",
    "LBMA gold PM auction",
    "LBMA gold/silver AM auction",
    "London 4pm fix (WM/Reuters)",
    "Tokyo 9:55 fix (gotobi)",
})
# Catalog words that are neither an exposure name nor an admissible root of
# reports/stage_e2a_vehicles.json: reports/stage_e0_catalog_K4.md line 65, "WTI crude {CL, QM,
# MCL}; Henry Hub gas {NG, QG, MNG}".
WORD_ALIASES: Mapping[str, str] = MappingProxyType({"crude": "WTI crude", "gas": "Henry Hub gas"})

KNOWN_GAPS: tuple[str, ...] = (
    "G.17's 2025-11-24 annual revision (a standalone publication quoted on the 2025-12-03 G.17 "
    "release page) is not entered (lead list, ruling OC-N); the named source did not audit whether "
    "other years' annual revisions were published on separate dates "
    "(reports/stage_e2b_release_sources_named_log.md).",
)
RULINGS: tuple[str, ...] = (
    "OC-J: the release calendar is a harness input (D8 event window, D9.5a fill guard, "
    "D9.12 CPI window).",
    "OC-N (13:52 PDT): the release list, F6.4 products plus micro siblings, FOMC = all products, "
    "member-named products via exposure words, CPI flag, kept [unverified] and "
    "announced_schedule entries, exclusions, the G.17 gap.",
    "Lead, commodity file: NGS [unverified] entries (EIA's standing Thursday 10:30 ET rule, and "
    "the documented holiday-week practice) are kept and counted as unverified.",
    "Lead, commodity file: CROP_ANNUAL keeps its own entries although it always shares the January "
    "CROP instant; a product's instants are a de-duplicated set (shared_instants lists both ids).",
)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ------------------------------------------------------------------ inputs ----
@dataclass(frozen=True)
class BuildInputs:
    sources: Mapping[str, Mapping[str, Any]]  # source name -> parsed entries file
    source_logs: Mapping[str, str]  # source name -> log text
    names: Mapping[str, Any]
    vehicles: Mapping[str, Any]
    liquidity: Mapping[str, Any]
    catalog: Mapping[str, Any]
    facts: Mapping[str, Any]
    hashes: Mapping[str, str]  # repository-relative path -> sha256 of every input read


def _read(root: Path, rel: str, hashes: dict[str, str], expected: str | None = None) -> str:
    path = root / rel
    if not path.is_file():
        raise _refuse(f"input {rel} does not exist")
    data = path.read_bytes()
    digest = _sha256_bytes(data)
    if expected is not None and digest != expected:
        raise _refuse(f"{rel}: sha256 {digest} differs from the recorded {expected}")
    hashes[rel] = digest
    return data.decode("utf-8")


def load_inputs(repo_root: Path = REPO_ROOT) -> BuildInputs:
    """Every input file, the frozen ones checked against their recorded sha256."""
    root = Path(repo_root)
    hashes: dict[str, str] = {}
    manifest = json.loads(_read(root, FREEZE_MANIFEST, hashes))
    frozen = {}
    for rel in E0_FROZEN:
        try:
            frozen[rel] = manifest["files"][rel]["sha256"]
        except KeyError:
            raise _refuse(f"{FREEZE_MANIFEST} records no sha256 for {rel}") from None
    loaded = {rel: json.loads(_read(root, rel, hashes, frozen[rel])) for rel in E0_FROZEN}
    vehicles = json.loads(_read(root, VEHICLES_PATH, hashes, VEHICLES_SHA256))
    names = json.loads(_read(root, NAMES_PATH, hashes))
    sources, logs = {}, {}
    for name, (rel, log_rel) in SOURCES.items():
        sources[name] = json.loads(_read(root, rel, hashes))
        logs[name] = _read(root, log_rel, hashes)
    return BuildInputs(MappingProxyType(sources), MappingProxyType(logs), names, vehicles,
                       loaded[LIQUIDITY_PATH], loaded[CATALOG_PATH], loaded[FACTS_PATH],
                       MappingProxyType(hashes))


# ------------------------------------------------------------------- F6.4 ----
@dataclass(frozen=True)
class F64Row:
    name: str
    time_text: str
    listed: tuple[str, ...] | None  # None: "All products"

    @property
    def codes(self) -> tuple[str, ...]:
        try:
            return F6_4_CODES[self.name]
        except KeyError:
            raise _refuse(f"F6.4 row {self.name!r} has no release code") from None


def parse_f6_4(quote: str) -> tuple[F64Row, ...]:
    """F6.4's rows; the matches must tile the quote exactly (nothing skipped)."""
    rows, pos = [], 0
    for m in _F6_4_ROW.finditer(quote):
        if m.start() != pos:
            raise _refuse(f"F6.4: unparsed text {quote[pos:m.start()]!r}")
        text = m.group("listed").strip()
        listed = None if text == ALL_PRODUCTS else tuple(r.strip() for r in text.split(","))
        rows.append(F64Row(m.group("name"), m.group("time"), listed))
        pos = m.end()
    if pos != len(quote) or not rows:
        raise _refuse(f"F6.4: unparsed text {quote[pos:]!r}")
    return tuple(rows)


def check_f6_4(facts: Mapping[str, Any]) -> tuple[F64Row, ...]:
    """The facts file's F6.4 must be the quote this module encodes, with the micro note."""
    matches = [f for f in facts["facts"] if f.get("id") == F6_4_ID]
    if len(matches) != 1:
        raise _refuse(f"{FACTS_PATH}: {len(matches)} facts with id {F6_4_ID}")
    fact = matches[0]
    if fact["quote"] != F6_4_QUOTE:
        raise _refuse(f"{FACTS_PATH} {F6_4_ID}: the quote differs from the encoded table")
    if F6_4_MICRO_NOTE not in fact.get("note", ""):
        raise _refuse(f"{FACTS_PATH} {F6_4_ID}: the note lacks {F6_4_MICRO_NOTE!r}")
    rows = parse_f6_4(fact["quote"])
    if {r.name for r in rows} != set(F6_4_CODES):
        raise _refuse(f"F6.4 rows {[r.name for r in rows]} differ from {sorted(F6_4_CODES)}")
    return rows


def micro_siblings(root: str) -> tuple[str, ...]:
    """The micro contracts of ``root``'s exposure in rules/products.py (none for an unknown
    root, a micro itself excluded)."""
    if root not in PRODUCTS:
        return ()
    exposure = PRODUCTS[root].exposure
    return tuple(sorted(p.root for p in PRODUCTS.values()
                        if p.exposure == exposure and p.contract_type in MICRO_TYPES
                        and p.root != root))


# ---------------------------------------------------------------- universe ----
def product_universe(vehicles: Mapping[str, Any], liquidity: Mapping[str, Any]
                     ) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """(roots in the product table, roots outside it) of vehicles + liquidity + ML paths."""
    roots: set[str] = set(PRICE_PATH_CONTRACTS)
    for exp in vehicles["exposures"]:
        roots.update(exp["admissible"])
        if exp.get("vehicle"):
            roots.add(exp["vehicle"])
    roots.update(vehicles["contracts"])
    roots.update(p["symbol"] for p in liquidity["products"])
    return (tuple(sorted(r for r in roots if r in PRODUCTS)),
            tuple(sorted(r for r in roots if r not in PRODUCTS)))


def exposure_roots(vehicles: Mapping[str, Any]) -> dict[str, tuple[str, ...]]:
    """exposure name -> (its frozen vehicle root if any, its ML price-path root)."""
    out = {}
    for exp in vehicles["exposures"]:
        paths = [p for p in PRICE_PATH_CONTRACTS if p in exp["admissible"]]
        if len(paths) != 1:
            raise _refuse(f"exposure {exp['exposure']!r}: price-path contracts {paths}")
        roots = {paths[0]} | ({exp["vehicle"]} if exp.get("vehicle") else set())
        out[exp["exposure"]] = tuple(sorted(roots))
    return out


def exposure_of_word(word: str, vehicles: Mapping[str, Any]) -> str:
    """The exposure a catalog word names: an alias, an exposure name, or its only root."""
    names = {e["exposure"] for e in vehicles["exposures"]}
    name = WORD_ALIASES.get(word, word)
    if name in names:
        return name
    owners = [e["exposure"] for e in vehicles["exposures"] if word in e["admissible"]]
    if len(owners) == 1 and len(next(e for e in vehicles["exposures"]
                                     if e["exposure"] == owners[0])["admissible"]) == 1:
        return owners[0]
    raise _refuse(f"catalog exposure word {word!r} maps to no single exposure of {VEHICLES_PATH}")


def _exposure_of_root(root: str, vehicles: Mapping[str, Any]) -> str:
    owners = [e["exposure"] for e in vehicles["exposures"] if root in e["admissible"]]
    if len(owners) != 1:
        raise _refuse(f"root {root!r} belongs to exposures {owners}")
    return owners[0]


# ----------------------------------------------------------- member-named ----
@dataclass(frozen=True)
class MemberNamed:
    roots: Mapping[str, tuple[str, ...]]  # code -> roots
    members: Mapping[str, tuple[str, ...]]  # code -> naming member ids
    members_by_status: Mapping[str, Mapping[str, tuple[str, ...]]]  # code -> status -> ids
    excluded: Mapping[str, tuple[str, ...]]  # excluded release name -> naming member ids
    words: Mapping[str, tuple[str, tuple[str, ...]]]  # word -> (exposure, roots)


def check_names_against_catalog(names: Mapping[str, Any], catalog: Mapping[str, Any],
                                vehicles: Mapping[str, Any]) -> None:
    """Each extraction row repeats its member's frozen catalog fields; starred products lie in
    the member's exposures."""
    by_id = {m["id"]: m for m in catalog["members"]}
    for row in names["members"]:
        member = by_id.get(row["member_id"])
        if member is None:
            raise _refuse(f"{NAMES_PATH}: member {row['member_id']} is not in {CATALOG_PATH}")
        for ours, theirs in (("read_products", "exposures"), ("traded_products",
                                                                "starred_products"),
                             ("status", "status")):
            if row[ours] != member[theirs]:
                raise _refuse(f"{NAMES_PATH}: {row['member_id']} {ours} {row[ours]!r} differs "
                              f"from the catalog's {theirs} {member[theirs]!r}")
        exposures = {exposure_of_word(w, vehicles) for w in row["read_products"]}
        for root in row["traded_products"]:
            if _exposure_of_root(root, vehicles) not in exposures:
                raise _refuse(f"{row['member_id']}: starred {root} is outside its exposures")
    listed = {r["name"] for r in names["distinct_releases"]}
    if listed != {r["release_name_verbatim"] for r in names["members"]}:
        raise _refuse(f"{NAMES_PATH}: distinct_releases differ from the member rows")


def member_named(names: Mapping[str, Any], vehicles: Mapping[str, Any]) -> MemberNamed:
    table = exposure_roots(vehicles)
    roots: dict[str, set[str]] = defaultdict(set)
    members: dict[str, set[str]] = defaultdict(set)
    by_status: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    excluded: dict[str, set[str]] = defaultdict(set)
    words: dict[str, tuple[str, tuple[str, ...]]] = {}
    for row in names["members"]:
        name = row["release_name_verbatim"]
        if name in EXCLUDED_BY_RULING:
            excluded[name].add(row["member_id"])
            continue
        if name not in NAMED_CODES:
            raise _refuse(f"member-named release {name!r} ({row['member_id']}) has no ruling")
        for word in row["read_products"]:
            exposure = exposure_of_word(word, vehicles)
            words[word] = (exposure, table[exposure])
            for code in NAMED_CODES[name]:
                roots[code].update(table[exposure])
        for code in NAMED_CODES[name]:
            members[code].add(row["member_id"])
            by_status[code][row["status"]].add(row["member_id"])
    return MemberNamed(
        MappingProxyType({c: tuple(sorted(v)) for c, v in roots.items()}),
        MappingProxyType({c: tuple(sorted(v)) for c, v in members.items()}),
        MappingProxyType({c: MappingProxyType({s: tuple(sorted(i)) for s, i in v.items()})
                          for c, v in by_status.items()}),
        MappingProxyType({n: tuple(sorted(v)) for n, v in excluded.items()}),
        MappingProxyType(dict(sorted(words.items()))))


# --------------------------------------------------------- release products ----
@dataclass(frozen=True)
class ReleaseProducts:
    code: str
    f6_4_row: str | None
    f6_4_listed: tuple[str, ...]  # listed (or universe) roots in the product table
    f6_4_not_in_table: tuple[str, ...]  # listed roots the loader would refuse
    micro_siblings: tuple[str, ...]  # added by "**Micro contracts also apply"
    member_named: tuple[str, ...]
    naming_members: tuple[str, ...]
    naming_by_status: Mapping[str, tuple[str, ...]]  # catalog status -> naming member ids
    products: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {"f6_4_row": self.f6_4_row, "f6_4_listed": list(self.f6_4_listed),
                "f6_4_not_in_product_table": list(self.f6_4_not_in_table),
                "micro_siblings": list(self.micro_siblings),
                "member_named": list(self.member_named),
                "naming_members": list(self.naming_members),
                "naming_members_by_status": {s: list(i) for s, i in
                                             sorted(self.naming_by_status.items())},
                "products": list(self.products)}


def release_products(rows: Sequence[F64Row], universe: Sequence[str],
                     universe_out: Sequence[str], named: MemberNamed
                     ) -> dict[str, ReleaseProducts]:
    out = {}
    for code in RELEASE_SOURCE:
        f64 = [r for r in rows if code in r.codes]
        if len(f64) > 1:
            raise _refuse(f"{code}: in {len(f64)} F6.4 rows")
        listed_in, listed_out, siblings = [], [], set()
        if f64:
            listed = f64[0].listed
            listed_in = list(universe) if listed is None else [r for r in listed if r in PRODUCTS]
            listed_out = list(universe_out) if listed is None else [r for r in listed
                                                                   if r not in PRODUCTS]
            for root in listed_in:
                siblings.update(micro_siblings(root))
            siblings -= set(listed_in)
        by_members = named.roots.get(code, ())
        products = tuple(sorted(set(listed_in) | siblings | set(by_members)))
        if not products:
            raise _refuse(f"release {code} concerns no product (neither F6.4 nor a naming member)")
        out[code] = ReleaseProducts(code, f64[0].name if f64 else None, tuple(sorted(listed_in)),
                                    tuple(sorted(listed_out)), tuple(sorted(siblings)),
                                    tuple(by_members), named.members.get(code, ()),
                                    named.members_by_status.get(code, MappingProxyType({})),
                                    products)
    return out


# ---------------------------------------------------------------- assemble ----
def _output_entry(e: Mapping[str, Any], source_file: str, products: Sequence[str]
                  ) -> dict[str, Any]:
    evidence = evidence_of(e)
    out = {"id": e["id"], "release": e["release"], "release_name": e["release_name"],
           "date": e["date"], "time_local": e["time_local"], "tz": e["tz"],
           "instant_utc": e["instant_utc"], "products": list(products),
           "cpi": e["release"] in CPI_CODES, "evidence": evidence,
           "source": {"file": source_file, "url": e["url"], "saved_path": e["saved_path"]}}
    if evidence != "verified":
        out["note"] = e.get("note")
    return out


def _entries(inputs: BuildInputs, products: Mapping[str, ReleaseProducts]
             ) -> list[dict[str, Any]]:
    out, seen = [], set()
    for name, source in inputs.sources.items():
        for e in source["entries"]:
            if e["id"] in seen:
                raise _refuse(f"release id {e['id']} appears twice")
            seen.add(e["id"])
            if not COVERAGE_FIRST <= e["date"] <= COVERAGE_LAST:
                raise _refuse(f"{e['id']}: date {e['date']} is outside the coverage")
            out.append(_output_entry(e, SOURCES[name][0], products[e["release"]].products))
    missing = set(RELEASE_SOURCE) - {e["release"] for e in out}
    if missing:
        raise _refuse(f"releases {sorted(missing)} of the lead's list have no entry")
    return sorted(out, key=lambda x: (x["instant_utc"], x["id"]))


def _by_root(entries: Sequence[Mapping[str, Any]]) -> dict[str, set[str]]:
    out: dict[str, set[str]] = defaultdict(set)
    for e in entries:
        for root in e["products"]:
            out[root].add(e["instant_utc"])
    return out


def check_vehicle_parity(entries: Sequence[Mapping[str, Any]], vehicles: Mapping[str, Any]
                         ) -> int:
    """Each exposure's vehicle and ML price-path root carry the same instants (ml_route's
    ReleaseListMismatch otherwise); returns the number of exposures checked."""
    by_root, checked = _by_root(entries), 0
    for exposure, roots in exposure_roots(vehicles).items():
        sets = {r: by_root.get(r, set()) for r in roots}
        if len({frozenset(s) for s in sets.values()}) > 1:
            sizes = ", ".join(f"{r} {len(s)}" for r, s in sets.items())
            raise _refuse(f"exposure {exposure}: {sizes} instants; the vehicle and the price-path "
                          "root must match")
        checked += 1
    return checked


def _shared_instants(entries: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, list[str]] = defaultdict(list)
    for e in entries:
        groups[e["instant_utc"]].append(e["id"])
    return [{"instant_utc": k, "ids": v} for k, v in sorted(groups.items()) if len(v) > 1]


def _counts_by(entries: Sequence[Mapping[str, Any]], evidence: str) -> dict[str, Any]:
    c = Counter(e["release"] for e in entries if e["evidence"] == evidence)
    return {"total": sum(c.values()), "by_release": dict(sorted(c.items()))}


def _cancellations(inputs: BuildInputs) -> list[dict[str, Any]]:
    return [{"source": name, "release": c["release"], "reference_period": c["reference_period"],
             "originally_scheduled": c["originally_scheduled"], "reason": c["reason"]}
            for name, s in inputs.sources.items() for c in s["cancellations"]]


def _loader_roundtrip(calendar: Mapping[str, Any]) -> dict[str, Any]:
    loaded = release_calendar_from_dict(dict(calendar), "in-memory", "build_release_calendar")
    cpi = {e["instant_utc"] for e in calendar["releases"] if e["cpi"]}
    if len(loaded.cpi) != len(cpi):
        raise _refuse(f"the loader reads {len(loaded.cpi)} CPI instants, the build has {len(cpi)}")
    if (loaded.first.isoformat(), loaded.last.isoformat()) != (COVERAGE_FIRST, COVERAGE_LAST):
        raise _refuse("the loader reads a different coverage")
    return {"roots": len(loaded.by_root), "cpi_instants": len(loaded.cpi),
            "instants_per_root_min": min(len(v) for v in loaded.by_root.values()),
            "instants_per_root_max": max(len(v) for v in loaded.by_root.values())}


def _mappings(rows: Sequence[F64Row], universe: Sequence[str], universe_out: Sequence[str],
              named: MemberNamed, products: Mapping[str, ReleaseProducts]) -> dict[str, Any]:
    """The calendar's record of how products were assigned (read by people, not the loader)."""
    return {
        "product_universe": {"in_product_table": list(universe),
                             "not_in_product_table": list(universe_out),
                             "from": [VEHICLES_PATH, LIQUIDITY_PATH,
                                      "ml_route.constants.PRICE_PATH_CONTRACTS"]},
        "f6_4": {"id": F6_4_ID, "source": FACTS_PATH, "quote": F6_4_QUOTE,
                 "note": F6_4_MICRO_NOTE,
                 "rows": [{"name": r.name, "time_ct": r.time_text,
                           "listed": ALL_PRODUCTS if r.listed is None else list(r.listed),
                           "codes": list(r.codes)} for r in rows]},
        "word_to_roots": {w: {"exposure": x, "roots": list(r)} for w, (x, r) in
                          named.words.items()},
        "release_products": {c: p.as_dict() for c, p in products.items()},
        "excluded_by_ruling": [{"name": n, "naming_members": list(named.excluded.get(n, ())),
                                "reason": EXCLUSION_REASON} for n in sorted(EXCLUDED_BY_RULING)],
        "known_gaps": list(KNOWN_GAPS),
    }


def _verification(calendar: Mapping[str, Any], inputs: BuildInputs, counts: Mapping[str, int],
                  parity: int) -> dict[str, Any]:
    entries = calendar["releases"]
    cancelled = Counter(c["release"] for c in calendar["cancellations"])
    return {
        "entries": len(entries),
        "by_source": {n: len(s["entries"]) for n, s in inputs.sources.items()},
        **counts,
        "verified": _counts_by(entries, "verified"),
        "unverified": _counts_by(entries, "unverified"),
        "announced_schedule": _counts_by(entries, ANNOUNCED),
        "cancelled": dict(sorted(cancelled.items())),
        "vehicle_pricepath_exposures_checked": parity,
        "loader": _loader_roundtrip(calendar),
        "method": ("quotes: whitespace-normalised substring of the strict-UTF-8 saved page; "
                   "instants: date + time_local in tz via zoneinfo equals instant_utc; coverage "
                   "tables recounted from entries and cancellations; loader: "
                   "screening.stage_e_rules.release_calendar_from_dict on the built dict"),
    }


def assemble(inputs: BuildInputs, page_root: Path = REPO_ROOT) -> dict[str, Any]:
    """The calendar as a dict, after every check (CalendarBuildRefused otherwise)."""
    for name in SOURCES:
        check_source(name, inputs.sources[name], inputs.source_logs[name], RELEASE_SOURCE)
    rows = check_f6_4(inputs.facts)
    check_names_against_catalog(inputs.names, inputs.catalog, inputs.vehicles)
    universe, universe_out = product_universe(inputs.vehicles, inputs.liquidity)
    named = member_named(inputs.names, inputs.vehicles)
    products = release_products(rows, universe, universe_out, named)
    entries = _entries(inputs, products)
    pages = Pages(page_root)
    all_source_entries = [e for s in inputs.sources.values() for e in s["entries"]]
    counts = verify_entries(all_source_entries, pages) | verify_evidence(inputs.sources, pages)
    parity = check_vehicle_parity(entries, inputs.vehicles)
    calendar: dict[str, Any] = {
        "schema": RELEASE_CALENDAR_SCHEMA, "built_by": BUILT_BY, "rulings": list(RULINGS),
        "coverage": {"first": COVERAGE_FIRST, "last": COVERAGE_LAST},
        "inputs": dict(sorted(inputs.hashes.items())),
        **_mappings(rows, universe, universe_out, named, products),
        "cancellations": _cancellations(inputs),
        "releases": entries,
        "shared_instants": _shared_instants(entries),
    }
    calendar["verification"] = _verification(calendar, inputs, counts, parity)
    return calendar


def calendar_json(calendar: Mapping[str, Any]) -> str:
    return json.dumps(calendar, indent=1, ensure_ascii=False) + "\n"


# ------------------------------------------------------------------ writing ----
def write_once(path: Path, text: str) -> None:
    """Write a new file and make it read-only; an existing file is refused."""
    try:
        with open(path, "x", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    except FileExistsError:
        raise _refuse(f"{path} exists; the calendar is written once and never "
                      "overwritten") from None
    path.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)


@dataclass(frozen=True)
class BuildResult:
    calendar: Mapping[str, Any]
    json_text: str
    md_text: str
    sha256: str


def build(repo_root: Path = REPO_ROOT, write: bool = True) -> BuildResult:
    """Load, assemble and check; with ``write``, write the JSON and the .md once each."""
    from screening.build_release_calendar_md import render_md  # imports this module's constants

    root = Path(repo_root)
    inputs = load_inputs(root)
    calendar = assemble(inputs, root)
    text = calendar_json(calendar)
    digest = _sha256_bytes(text.encode("utf-8"))
    md = render_md(calendar, digest, datetime.now(PDT).strftime("%Y-%m-%d %H:%M %Z"))
    if write:
        targets = (root / OUT_JSON, root / OUT_MD)
        existing = [str(t) for t in targets if t.exists()]
        if existing:
            raise _refuse(f"{existing} exist; the calendar is written once and never overwritten")
        write_once(targets[0], text)
        write_once(targets[1], md)
    return BuildResult(calendar, text, md, digest)


def main(argv: Sequence[str] | None = None, repo_root: Path = REPO_ROOT) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true",
                        help="rebuild in memory and compare with the written calendar")
    args = parser.parse_args(argv)
    try:
        result = build(repo_root, write=not args.check)
    except CalendarBuildRefused as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    v = result.calendar["verification"]
    summary = (f"entries {v['entries']}, unverified {v['unverified']['total']}, announced "
               f"{v['announced_schedule']['total']}, roots {v['loader']['roots']}, "
               f"cpi {v['loader']['cpi_instants']}, sha256 {result.sha256}")
    if not args.check:
        print(f"wrote {OUT_JSON} and {OUT_MD}: {summary}")
        return 0
    path = Path(repo_root) / OUT_JSON
    if not path.is_file():
        print(f"CHECK: {OUT_JSON} does not exist", file=sys.stderr)
        return 1
    same = path.read_bytes() == result.json_text.encode("utf-8")
    print(f"CHECK {'identical' if same else 'DIFFERS'}: {summary}")
    return 0 if same else 1


if __name__ == "__main__":
    raise SystemExit(main())
