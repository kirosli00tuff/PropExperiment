"""Stage E.16 F-04 (lead follow-up): announcement dates of the frozen 2019-05..2024-02 2/5/10/30-year
TREASURY_AUCTION rows, and the announcement-vs-t-3 counts for both periods.

Reads only: the saved FiscalData responses (metadata fields), the frozen release calendar's
TREASURY_AUCTION rows, ec_auc_2010_2019.json, and the frozen rates calendars
(data/calendars/hist2010/rates.json via data.hist_calendar.parse_hist_calendar; data/calendars/rates.py).
Writes reports/stage_e16_calendars/ec_auc_announcements_2019_2024.json and prints the t-3 table
(also written to reports/stage_e16_calendars/f04_t3_counts.json).
Run: PYTHONPATH=<repo> <repo>/.venv/bin/python build_ec_auc_announcements.py
"""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
PAGES = REPO / "reports/stage_e16_briefs/pages/fiscaldata"
RAW_JSON = PAGES / "auctions_query_notes_bonds_20190501_20240331.json"
RAW_CSV = PAGES / "auctions_query_notes_bonds_20190501_20240331.csv"
FROZEN = REPO / "reports/stage_e2b_release_calendar.json"
HIST = REPO / "reports/stage_e16_calendars/ec_auc_2010_2019.json"
OUT = REPO / "reports/stage_e16_calendars/ec_auc_announcements_2019_2024.json"
OUT_T3 = REPO / "reports/stage_e16_calendars/f04_t3_counts.json"
BASE = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/auctions_query"
FIELDS = ("auction_date,security_type,security_term,original_security_term,cusip,reopening,"
          "floating_rate,inflation_index_security,announcemt_date,closing_time_comp,closing_time_noncomp")
QUERY = (f"fields={FIELDS}&filter=auction_date:gte:2019-05-01,auction_date:lte:2024-03-31,"
         "security_type:in:(Note,Bond)&sort=auction_date&page[size]=10000")
TENOR = {"2-Year": "2Y", "5-Year": "5Y", "10-Year": "10Y", "30-Year": "30Y"}
H3 = ("2Y", "5Y", "10Y", "30Y")
P_NEW = ("2019-05-01", "2024-02-29")
P_OLD = ("2010-06-01", "2019-04-30")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rates_trade_dates():
    """Rates trade dates: weekdays that are not FULL_CLOSURE. <= 2019-04-30 from the hist2010 file,
    >= 2019-05-01 from data/calendars/rates.py (the overlap month is checked for agreement)."""
    from data.hist_calendar import parse_hist_calendar
    from data.cme_calendar import HolidayKind
    import data.calendars.rates as R
    hp = REPO / "data/calendars/hist2010/rates.json"
    hist = parse_hist_calendar(hp.read_bytes(), "rates", hp)
    h_closed = {d for d, h in hist.holidays.items() if h.kind is HolidayKind.FULL_CLOSURE}
    f_closed = {d for d, h in R.HOLIDAYS.items() if h.kind is HolidayKind.FULL_CLOSURE}
    may = [date(2019, 5, 1) + timedelta(n) for n in range(31)]
    agree = all((d in h_closed) == (d in f_closed) for d in may if d.weekday() < 5)
    days, d = set(), date(2010, 1, 1)
    while d <= date(2024, 3, 31):
        if d.weekday() < 5:
            closed = h_closed if d <= date(2019, 4, 30) else f_closed
            if d not in closed:
                days.add(d)
        d += timedelta(1)
    meta = {"hist_rates_json": str(hp.relative_to(REPO)), "hist_rates_sha256": hist.file_sha256,
            "hist_unsourced_dates_in_2010_2019": len(hist.unsourced),
            "rates_py": "data/calendars/rates.py", "rates_py_sha256": sha(R.__file__),
            "rates_py_coverage": [str(x) for x in R.CALENDAR_COVERAGE],
            "may_2019_closures_agree": agree,
            "rule": "trade date = weekday not a FULL_CLOSURE of the group calendar (early-halt and "
                    "unsourced dates count as trade dates here); hist file for dates <= 2019-04-30, "
                    "rates.py from 2019-05-01"}
    return days, meta


def t_minus(days, t, k):
    d, n = t, 0
    while n < k:
        d -= timedelta(1)
        if d in days:
            n += 1
    return d


def main():
    data = json.loads(RAW_JSON.read_bytes())["data"]
    with RAW_CSV.open(newline="") as fh:
        if [dict(r) for r in csv.DictReader(fh)] != data:
            raise SystemExit("JSON and CSV disagree")
    fetch = json.loads((PAGES / "fetch_times.json").read_text())
    # FiscalData records keyed as the frozen id: (auction_date, tenor from original_security_term),
    # E.0 filter applied (Note/Bond, floating_rate No, inflation_index_security No).
    keyed = defaultdict(list)
    for r in data:
        if (r["security_type"] in ("Note", "Bond") and r["floating_rate"] == "No"
                and r["inflation_index_security"] == "No" and r["original_security_term"] in TENOR):
            keyed[f"TREASURY_AUCTION-{r['auction_date']}-{TENOR[r['original_security_term']]}"].append(r)
    frozen = [x for x in json.loads(FROZEN.read_bytes())["releases"]
              if x["release"] == "TREASURY_AUCTION" and P_NEW[0] <= x["date"] <= P_NEW[1]
              and x["id"].rsplit("-", 1)[1] in H3]
    rows, unmatched, ambiguous = [], [], []
    for x in frozen:
        cands = keyed.get(x["id"], [])
        if not cands:
            unmatched.append(x["id"])
            continue
        if len(cands) > 1:
            ambiguous.append(x["id"])
        r = cands[0]
        rows.append({"id": x["id"], "auction_date": r["auction_date"],
                     "tenor": x["id"].rsplit("-", 1)[1], "announcemt_date": r["announcemt_date"],
                     "cusip": r["cusip"], "original_security_term": r["original_security_term"],
                     "security_term": r["security_term"]})
    # FiscalData H3-tenor records in the window that have no frozen row (e.g. same-day announced)
    frozen_ids = {x["id"] for x in frozen}
    not_in_frozen = sorted(k for k, v in keyed.items()
                           if P_NEW[0] <= v[0]["auction_date"] <= P_NEW[1] and k not in frozen_ids)
    header = {
        "source": {"endpoint": BASE, "query": QUERY, "url_json": f"{BASE}?{QUERY}&format=json",
                   "url_csv": f"{BASE}?{QUERY}&format=csv",
                   "fields_read": FIELDS.split(","), "result_fields_read": "none"},
        "responses": {"json": {"saved_path": str(RAW_JSON.relative_to(REPO)), "sha256": sha(RAW_JSON),
                               "fetched_utc": fetch["json_2019_2024"], "records": len(data)},
                      "csv": {"saved_path": str(RAW_CSV.relative_to(REPO)), "sha256": sha(RAW_CSV),
                              "fetched_utc": fetch["csv_2019_2024"], "identical_to_json": True}},
        "frozen_file": {"path": str(FROZEN.relative_to(REPO)), "sha256": sha(FROZEN),
                        "rows_selected": "TREASURY_AUCTION rows with date 2019-05-01..2024-02-29 "
                                         "and tenor 2Y/5Y/10Y/30Y"},
        "match_rule": "frozen id format 'TREASURY_AUCTION-<YYYY-MM-DD>-<N>Y' with N from "
                      "original_security_term ('2-Year' -> '2Y'); matched to the FiscalData record "
                      "with that auction_date and original_security_term after the E.0 filter "
                      "(security_type Note/Bond, floating_rate No, inflation_index_security No)",
        "counts": {"records_fetched": len(data), "frozen_rows": len(frozen), "rows": len(rows),
                   "by_tenor": dict(Counter(r["tenor"] for r in rows)),
                   "unmatched_frozen_rows": unmatched, "ambiguous_matches": ambiguous,
                   "fiscaldata_h3_records_without_frozen_row": not_in_frozen},
        "built_by": "reports/stage_e16_calendars/scripts/build_ec_auc_announcements.py",
    }
    OUT.write_text(json.dumps({"schema": "stage_e16_ec_auc_announcements/1", "header": header,
                               "rows": rows}, indent=1) + "\n")

    # ---- t-3 counts
    days, meta = rates_trade_dates()
    old = [{"id": x["id"], "auction_date": x["date"], "tenor": x["id"].rsplit("-", 1)[1],
            "announcemt_date": x["announcemt_date"]}
           for x in json.loads(HIST.read_bytes())["releases"]
           if P_OLD[0] <= x["date"] <= P_OLD[1] and x["id"].rsplit("-", 1)[1] in H3]
    table, detail = {}, {}
    for name, rs in (("2010-06..2019-04", old), ("2019-05..2024-02", rows)):
        per = {t: Counter() for t in H3}
        after = []
        not_trade = []
        for r in rs:
            t = date.fromisoformat(r["auction_date"])
            if t not in days:
                not_trade.append(r["id"])
            t3 = t_minus(days, t, 3)
            a = date.fromisoformat(r["announcemt_date"])
            k = "after_t3" if a > t3 else ("on_t3" if a == t3 else "before_t3")
            per[r["tenor"]][k] += 1
            if k == "after_t3":
                after.append({"id": r["id"], "announcemt_date": r["announcemt_date"], "t3": str(t3)})
        table[name] = {t: {k: per[t][k] for k in ("after_t3", "on_t3", "before_t3")}
                       | {"n": sum(per[t].values())} for t in H3}
        table[name]["all"] = {k: sum(table[name][t][k] for t in H3)
                              for k in ("after_t3", "on_t3", "before_t3", "n")}
        detail[name] = {"announced_after_t3": after, "auction_date_not_a_rates_trade_date": not_trade}
    out = {"definition": "t-3 = the third rates-group trade date before the auction date t; "
                         "after = announcemt_date > t-3, on = equal, before = earlier",
           "rates_calendar": meta, "counts": table, "detail": detail}
    OUT_T3.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(header["counts"]))
    print(json.dumps(table))
    print(json.dumps({k: {kk: len(vv) for kk, vv in v.items()} for k, v in detail.items()}), meta["may_2019_closures_agree"])


if __name__ == "__main__":
    main()
