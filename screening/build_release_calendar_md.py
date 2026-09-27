"""The summary reports/stage_e2b_release_calendar.md of the release calendar (Stage E.2b).

``render_md(calendar, sha256, built_pdt)`` renders the calendar dict that
screening.build_release_calendar.assemble returns: counts per release x year, products per
release and per root, the word -> roots table, naming members by catalog status, local release
times, exclusions, cancellations, known gaps and the verification counts.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from screening.build_release_calendar import ANNOUNCED, BUILT_BY, OUT_JSON, RELEASE_SOURCE, YEARS


def _table(header: Sequence[str], rows: Iterable[Sequence[Any]]) -> list[str]:
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    return lines


def _counts(cal: Mapping[str, Any]) -> list[str]:
    entries = cal["releases"]
    per = Counter((e["release"], e["date"][:4]) for e in entries)
    ev = Counter((e["release"], e["evidence"]) for e in entries)
    canc = Counter(c["release"] for c in cal["cancellations"])
    rows = [[code, *(per[(code, y)] for y in YEARS), sum(per[(code, y)] for y in YEARS),
             ev[(code, "unverified")], ev[(code, ANNOUNCED)], canc[code]]
            for code in RELEASE_SOURCE]
    return _table(["Release", *YEARS, "Total", "Unverified", "Announced", "Cancelled"], rows)


def _products(cal: Mapping[str, Any]) -> list[str]:
    rows = []
    for code, p in cal["release_products"].items():
        listed = (f"all {len(p['f6_4_listed'])} universe roots" if p["f6_4_row"] == "FOMC Statement"
                  else " ".join(p["f6_4_listed"]) or "-")
        rows.append([code, p["f6_4_row"] or "-", listed, " ".join(p["micro_siblings"]) or "-",
                     " ".join(p["member_named"]) or "-", len(p["products"])])
    return _table(["Release", "F6.4 row", "F6.4 roots (in table)", "Micro siblings",
                   "Member-named roots", "Products"], rows)


def _per_product(cal: Mapping[str, Any]) -> list[str]:
    instants: dict[str, set[str]] = defaultdict(set)
    codes: dict[str, set[str]] = defaultdict(set)
    for e in cal["releases"]:
        for r in e["products"]:
            instants[r].add(e["instant_utc"])
            codes[r].add(e["release"])
    rows = [[r, len(instants[r]), " ".join(c for c in RELEASE_SOURCE if c in codes[r])]
            for r in sorted(instants)]
    return _table(["Root", "Distinct instants", "Releases"], rows)


def _times(cal: Mapping[str, Any]) -> list[str]:
    times: dict[str, Counter] = defaultdict(Counter)
    for e in cal["releases"]:
        times[e["release"]][e["time_local"]] += 1
    return _table(["Release", "Local times (America/New_York): count"],
                  [[c, ", ".join(f"{t}: {n}" for t, n in sorted(times[c].items()))]
                   for c in RELEASE_SOURCE])


def _members(cal: Mapping[str, Any]) -> list[str]:
    rows = [[code, "; ".join(f"{s}: {', '.join(ids)}" for s, ids in
                             p["naming_members_by_status"].items()) or "-"]
            for code, p in cal["release_products"].items()]
    return _table(["Release", "Naming members by catalog status"], rows)


def _totals(cal: Mapping[str, Any]) -> list[str]:
    v = cal["verification"]
    unv, ann = v["unverified"], v["announced_schedule"]
    ngs_total = sum(1 for e in cal["releases"] if e["release"] == "NGS")
    by_source = ", ".join(f"{k} {n}" for k, n in v["by_source"].items())
    return [
        f"- Entries: {v['entries']} ({by_source}); verified {v['verified']['total']}, "
        f"[unverified] {unv['total']}, announced_schedule {ann['total']}. All are kept and carry "
        "products.",
        f"- **NGS (EIA Weekly Natural Gas Storage Report): {unv['by_release'].get('NGS', 0)} of "
        f"{ngs_total} entries are [unverified]** (EIA's standing Thursday 10:30 ET rule, and the "
        "Wednesday 12:00 ET holiday weeks by EIA's documented practice; the per-week WNGSR pages "
        "were unreachable on Wayback). Kept and counted, per the lead's ruling.",
        f"- API bulletin: {ann['by_release'].get('API_WSB', 0)} entries dated from API's announced "
        "annual schedules (publication not confirmed per week); kept and counted.",
        f"- Cancelled (no entry): {sum(v['cancelled'].values())} "
        f"({', '.join(f'{k} {n}' for k, n in v['cancelled'].items())}).",
        f"- Instants shared by more than one entry: {len(cal['shared_instants'])} (e.g. CROP, "
        "WASDE and the January CROP_ANNUAL at 12:00 ET); the loader keeps one instant per "
        "product.",
    ]


def _verification(cal: Mapping[str, Any]) -> list[str]:
    v = cal["verification"]
    return [
        f"- Quotes {v['quotes_ok']}/{v['quotes_checked']}, instants "
        f"{v['instants_ok']}/{v['instants_checked']}, cancellation and move evidence quotes "
        f"{v.get('evidence_quotes_ok', 0)}/{v.get('evidence_quotes_checked', 0)}.",
        f"- Vehicle and price-path roots with equal instant lists: "
        f"{v['vehicle_pricepath_exposures_checked']} exposures.",
        f"- Loader round trip: {json.dumps(v['loader'])}.", f"- Method: {v['method']}.",
    ]


def render_md(cal: Mapping[str, Any], sha256: str, built_pdt: str) -> str:
    universe = cal["product_universe"]
    dropped = "; ".join(f"{c}: {' '.join(p['f6_4_not_in_product_table'])}"
                        for c, p in cal["release_products"].items()
                        if p["f6_4_not_in_product_table"])
    out = [
        "# Stage E.2b release calendar (summary)", "",
        f"File: `{OUT_JSON}` (schema `{cal['schema']}`), sha256 `{sha256}`. Built {built_pdt} "
        f"by `{BUILT_BY}` (`uv run --no-sync python -m screening.build_release_calendar`; "
        "`--check` rebuilds in memory and compares byte for byte). Coverage "
        f"{cal['coverage']['first']}..{cal['coverage']['last']}. Rulings: OC-J, OC-N and the "
        "lead's two commodity rulings (NGS kept as unverified; CROP_ANNUAL kept, instants "
        "de-duplicated per product).", "",
        "## Totals", "", *_totals(cal),
        "", "## Entries per release and year", "", *_counts(cal),
        "", "## Products per release", "",
        "F6.4 roots outside rules/products.py (the loader refuses unknown roots) are not written: "
        f"{dropped}.", "", *_products(cal),
        "", "## Product universe", "",
        f"In the product table ({len(universe['in_product_table'])}): "
        f"{' '.join(universe['in_product_table'])}. Not in it, not written: "
        f"{' '.join(universe['not_in_product_table'])}. MES is added to NFP and FOMC as the micro "
        "sibling of ES.",
        "", "## Distinct release instants per product", "", *_per_product(cal),
        "", "## Word to roots (member-named releases)", "",
        "A member's traded exposures are its catalog `exposures` words; each maps to the "
        "exposure's frozen vehicle root and ML price-path root. Starred products that are neither "
        "(SIL, M6E, M6A) are not added by this rule.", "",
        *_table(["Word", "Exposure (stage_e2a_vehicles.json)", "Roots"],
                [[w, x["exposure"], " ".join(x["roots"])]
                 for w, x in cal["word_to_roots"].items()]),
        "", "## Naming members by status", "",
        "Every catalog status counts (PPI and Crop Progress are named only by members the ML route "
        "superseded, and the lead's list includes them).", "", *_members(cal),
        "", "## Local release times", "", *_times(cal),
        "", "## Excluded by ruling", "",
        *[f"- {x['name']} (named by {', '.join(x['naming_members']) or 'none'}): {x['reason']}."
          for x in cal["excluded_by_ruling"]],
        "", "## Cancellations (no entry)", "",
        *_table(["Source", "Release", "Reference period", "Originally scheduled", "Reason"],
                [[c["source"], c["release"], c["reference_period"], c["originally_scheduled"],
                  c["reason"]] for c in cal["cancellations"]]),
        "", "## Known gaps", "", *[f"- {g}" for g in cal["known_gaps"]],
        "", "## Verification", "", *_verification(cal), "",
    ]
    return "\n".join(out)
