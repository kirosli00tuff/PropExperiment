"""Stage E.16 Task 3b(b): EC-AUC 2010-01-01..2019-06-30 rows in the frozen TREASURY_AUCTION format.

Reads only the saved FiscalData responses (metadata fields) and the frozen release calendar's
TREASURY_AUCTION rows (for the overlap check). Writes reports/stage_e16_calendars/ec_auc_2010_2019.json.
"""
import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
PAGES = REPO / "reports/stage_e16_briefs/pages/fiscaldata"
RAW_JSON = PAGES / "auctions_query_notes_bonds_20100101_20190630.json"
RAW_CSV = PAGES / "auctions_query_notes_bonds_20100101_20190630.csv"
FROZEN = REPO / "reports/stage_e2b_release_calendar.json"
OUT = REPO / "reports/stage_e16_calendars/ec_auc_2010_2019.json"
OUT_REL = "reports/stage_e16_calendars/ec_auc_2010_2019.json"

BASE = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/auctions_query"
FIELDS = ("auction_date,security_type,security_term,original_security_term,cusip,reopening,"
          "floating_rate,inflation_index_security,announcemt_date,closing_time_comp,closing_time_noncomp")
FILTER = "auction_date:gte:2010-01-01,auction_date:lte:2019-06-30,security_type:in:(Note,Bond)"
QUERY = f"fields={FIELDS}&filter={FILTER}&sort=auction_date&page[size]=10000"
URL_JSON = f"{BASE}?{QUERY}&format=json"
URL_CSV = f"{BASE}?{QUERY}&format=csv"

REQUIRED = ("security_type", "original_security_term", "floating_rate", "inflation_index_security",
            "auction_date", "announcemt_date", "closing_time_comp")
TENOR = {f"{n}-Year": f"{n}Y" for n in (2, 3, 5, 7, 10, 20, 30)}
H3_TENORS = ("2Y", "5Y", "10Y", "30Y")
PRODUCTS = ["TN", "UB", "ZB", "ZF", "ZN", "ZT"]
NY, UTC = ZoneInfo("America/New_York"), ZoneInfo("UTC")
CHECK_WINDOW = ("2010-06-01", "2019-04-30")
OVERLAP = ("2019-05-01", "2019-06-30")


def missing(v):
    return v is None or (isinstance(v, str) and v.strip() in ("", "null"))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


F04_FIELDS = ("announcemt_date", "original_security_term", "security_term", "security_type",
              "floating_rate", "inflation_index_security", "cusip")


def to_row(r, c):
    """r: the JSON record (row content as before); c: the identical CSV record, source of the
    F-04 fields appended after the frozen keys."""
    tenor = TENOR[r["original_security_term"]]
    et = datetime.strptime(r["closing_time_comp"].strip(), "%I:%M %p")
    local = datetime.fromisoformat(r["auction_date"]).replace(hour=et.hour, minute=et.minute,
                                                              tzinfo=NY)
    n = r["original_security_term"].split("-")[0]
    return {
        "id": f"TREASURY_AUCTION-{r['auction_date']}-{tenor}",
        "release": "TREASURY_AUCTION",
        "release_name": f"Treasury {n}-Year {r['security_type'].lower()} auction, competitive close",
        "date": r["auction_date"],
        "time_local": local.strftime("%H:%M"),
        "tz": "America/New_York",
        "instant_utc": local.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "products": list(PRODUCTS),
        "cpi": False,
        "evidence": "verified",
        "source": {"file": OUT_REL, "url": URL_CSV,
                   "saved_path": str(RAW_CSV.relative_to(REPO))},
        **{k: c[k] for k in F04_FIELDS},
    }


def main():
    data = json.loads(RAW_JSON.read_bytes())["data"]
    with RAW_CSV.open(newline="") as fh:
        csv_rows = list(csv.DictReader(fh))
    if [dict(r) for r in csv_rows] != data:
        sys.exit("JSON and CSV responses disagree")
    rows, excl_missing, excl_sameday, skipped_frn, skipped_tips, other_term = [], [], [], 0, 0, []
    keep_identity = []
    for r, c in zip(data, csv_rows):
        gone = [k for k in REQUIRED if missing(r.get(k))]
        ident = {k: r.get(k) for k in ("auction_date", "security_type", "security_term",
                                       "original_security_term", "cusip", "reopening")}
        if gone:
            excl_missing.append({**ident, "missing": gone})
            continue
        if r["security_type"] not in ("Note", "Bond"):
            other_term.append({**ident, "why": "security_type"})
            continue
        if r["floating_rate"] != "No":
            skipped_frn += 1
            continue
        if r["inflation_index_security"] != "No":
            skipped_tips += 1
            continue
        if r["original_security_term"] not in TENOR:
            other_term.append({**ident, "why": "original_security_term not a nominal tenor"})
            continue
        if not r["announcemt_date"] < r["auction_date"]:
            excl_sameday.append({**ident, "announcemt_date": r["announcemt_date"],
                                 "closing_time_comp": r["closing_time_comp"],
                                 "reason": "announcemt_date is not before auction_date"})
            continue
        rows.append(to_row(r, c))
        keep_identity.append(ident)
    ids = Counter(x["id"] for x in rows)
    dup = [i for i, c in ids.items() if c > 1]
    if dup:
        sys.exit(f"duplicate ids {dup}")
    inst = Counter(x["instant_utc"] for x in rows)
    rows.sort(key=lambda x: (x["instant_utc"], x["id"]))

    # counts
    by_year_tenor = defaultdict(Counter)
    for x in rows:
        by_year_tenor[x["date"][:4]][x["id"].rsplit("-", 1)[1]] += 1
    by_tenor = Counter(x["id"].rsplit("-", 1)[1] for x in rows)

    # 2% check: 2/5/10/30 nominal fixed-rate records (pre-guard), 2010-06..2019-04
    def h3_candidate(rec):
        return (rec.get("security_type") in ("Note", "Bond") and rec.get("floating_rate") == "No"
                and rec.get("inflation_index_security") == "No"
                and TENOR.get(rec.get("original_security_term")) in H3_TENORS
                and CHECK_WINDOW[0] <= (rec.get("auction_date") or "") <= CHECK_WINDOW[1])
    cand = [r for r in data if h3_candidate(r)]
    cand_missing = [r for r in cand if any(missing(r.get(k)) for k in REQUIRED)]
    cand_same = [r for r in cand if not any(missing(r.get(k)) for k in REQUIRED)
                 and not r["announcemt_date"] < r["auction_date"]]
    # a record with a missing tenor/flag field cannot be classified; count every missing-field
    # record in the window as a potential drop (conservative)
    win_missing_any = [r for r in excl_missing
                       if CHECK_WINDOW[0] <= (r.get("auction_date") or "") <= CHECK_WINDOW[1]]
    dropped = len(cand_missing) + len(cand_same) + len(
        [r for r in win_missing_any if r not in cand_missing])
    two_pct = {
        "window": list(CHECK_WINDOW),
        "candidates_2_5_10_30_nominal_fixed": len(cand),
        "dropped_missing_field": len(cand_missing),
        "dropped_same_day_announcement": len(cand_same),
        "unclassifiable_missing_field_records_in_window": len(win_missing_any),
        "dropped_total": dropped,
        "share": dropped / len(cand) if cand else None,
        "above_2pct": (dropped / len(cand) > 0.02) if cand else None,
        "candidates_by_tenor": dict(Counter(TENOR[r["original_security_term"]] for r in cand)),
    }

    # overlap check against the frozen file
    frozen = [x for x in json.loads(FROZEN.read_bytes())["releases"]
              if x["release"] == "TREASURY_AUCTION" and OVERLAP[0] <= x["date"] <= OVERLAP[1]]
    mine = [x for x in rows if OVERLAP[0] <= x["date"] <= OVERLAP[1]]
    fkeys = [k for k in frozen[0] if k != "source"]
    strip = lambda x: {k: x[k] for k in fkeys}  # noqa: E731  (frozen keys only)
    fz = {x["id"]: x for x in frozen}
    mz = {x["id"]: x for x in mine}
    overlap = {
        "window": list(OVERLAP),
        "frozen_rows": len(frozen), "my_rows": len(mine),
        "ids_only_frozen": sorted(set(fz) - set(mz)), "ids_only_mine": sorted(set(mz) - set(fz)),
        "rows_equal_excluding_source": sum(strip(fz[i]) == strip(mz[i]) for i in set(fz) & set(mz)),
        "rows_differing_excluding_source": sorted(i for i in set(fz) & set(mz)
                                                  if strip(fz[i]) != strip(mz[i])),
        "key_order_equal": all(list(mz[i])[:len(fz[i])] == list(fz[i])
                               for i in set(fz) & set(mz)),
        "compared": "the frozen row's keys (except source); the F-04 fields appended after "
                    "source are not in the frozen format",
        "source_field": "differs by construction (frozen cites the E.2b 2019-2026 query and "
                        "reports/stage_e2b_release_sources_named.json; these rows cite this "
                        "stage's 2010-2019 query)",
        "frozen_sha256": sha(FROZEN),
    }
    overlap["exact_match_excluding_source"] = (
        not overlap["ids_only_frozen"] and not overlap["ids_only_mine"]
        and not overlap["rows_differing_excluding_source"] and overlap["key_order_equal"])

    fetch = json.loads((PAGES / "fetch_times.json").read_text())
    header = {
        "schema": "e16_ec_auc_hist/1",
        "built_by": "Stage E.16 Task 3b, CalendarBuilder-OpusHigh (scratch script build_ec_auc.py)",
        "row_format": "the TREASURY_AUCTION rows of reports/stage_e2b_release_calendar.json "
                      "(same keys and key order; id TREASURY_AUCTION-<date>-<tenor>, tenor from "
                      "original_security_term; time_local = closing_time_comp ET as HH:MM; "
                      "instant_utc via America/New_York; products, cpi, evidence as frozen)",
        "rule": "E.0 C9 EC-AUC (reports/stage_e0_catalog.md lines 1350-1365): security_type Note or "
                "Bond, floating_rate No, inflation_index_security No, announcemt_date strictly "
                "before auction_date; every nominal coupon tenor (2,3,5,7,10,20,30-year original "
                "term, reopenings included) as the frozen file; H3 subsets 2/5/10/30Y",
        "fields_read": list(FIELDS.split(",")),
        "result_fields_read": "none (no yield, bid-to-cover, price or allotment field requested)",
        "source": {"endpoint": BASE, "query": QUERY, "url_json": URL_JSON, "url_csv": URL_CSV,
                   "terms": "FiscalData API documentation, 'License and Authorization': 'The data "
                            "is offered free, without restriction, and available to copy, adapt, "
                            "redistribute, or otherwise use for non-commercial or commercial "
                            "purposes.' 'Our API is open, meaning that it does not require a user "
                            "account or registration for a token.' (saved: reports/stage_e16_"
                            "briefs/pages/fiscaldata/fiscaldata.treasury.gov_api-documentation_.html)"},
        "responses": {
            "json": {"saved_path": str(RAW_JSON.relative_to(REPO)), "sha256": sha(RAW_JSON),
                     "fetched_utc": fetch["json"], "records": len(data)},
            "csv": {"saved_path": str(RAW_CSV.relative_to(REPO)), "sha256": sha(RAW_CSV),
                    "fetched_utc": fetch["csv"], "records": len(csv_rows),
                    "identical_to_json": True},
        },
        "coverage": {"first": "2010-01-01", "last": "2019-06-30"},
        "counts": {
            "records_fetched": len(data), "rows": len(rows),
            "skipped_frn": skipped_frn, "skipped_tips": skipped_tips,
            "excluded_missing_field": len(excl_missing),
            "excluded_same_day_announcement": len(excl_sameday),
            "other_security_or_term": len(other_term),
            "by_tenor": dict(sorted(by_tenor.items(), key=lambda kv: int(kv[0][:-1]))),
            "by_year_tenor": {y: dict(sorted(c.items(), key=lambda kv: int(kv[0][:-1])))
                              for y, c in sorted(by_year_tenor.items())},
            "rows_sharing_an_instant": sum(c for c in inst.values() if c > 1),
        },
        "excluded_same_day_announcement": excl_sameday,
        "excluded_missing_field": excl_missing,
        "other_security_or_term": other_term,
        "two_pct_check": two_pct,
        "overlap_check_vs_frozen": overlap,
        "f04_fields": {
            "added": list(F04_FIELDS),
            "from": str(RAW_CSV.relative_to(REPO)),
            "position": "appended to every row after 'source'; every frozen-format key and value "
                        "unchanged (lead follow-up F-04, 2026-10-09)",
            "rows_with_all_f04_fields": sum(all(x.get(k) not in (None, "", "null")
                                                for k in F04_FIELDS) for x in rows),
        },
    }
    OUT.write_text(json.dumps({"header": header, "releases": rows}, indent=1) + "\n")
    print(json.dumps({k: header["counts"][k] for k in header["counts"] if k != "by_year_tenor"}))
    print(json.dumps(two_pct))
    print(json.dumps({k: v for k, v in overlap.items() if k != "source_field"}))
    print("sha256", sha(OUT))


if __name__ == "__main__":
    main()
