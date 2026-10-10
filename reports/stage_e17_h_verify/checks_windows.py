"""Windows, fallbacks, listing, store boundary, holdout/embargo and header assertions over the
units files, the RUN_ONCE markers and the H1-H5 result headers (verdict.json is read later, in
compare.py). Prints counts only."""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from vv_common import OUT, REPO, RUNS, iter_units, write_json  # noqa: E402

FALLBACK_ROOTS = {"6A", "6B", "6C", "6J", "6N", "6S", "HG", "YM", "ZM", "ZW"}
FALLBACK_START = "2019-05-06"
WINDOW_END = "2024-02-29"
LISTING = {"RTY": "2017-07-10", "TN": "2016-01-11", "HE": "2017-07-03"}
DEFAULT_START = "2010-07-01"
LE_WEAK_END = "2014-12-14"  # R-S3: no H1/H4 unit for LE on or before this date
BOUNDARY_GAP = ("2019-05-01", "2019-05-03")
HIST_LAST, STEP2_FIRST = "2019-04-30", "2019-05-06"
HOLDOUT2 = ("2024-03-01", "2025-03-31")  # the March 2024 embargo and holdout-2's trade dates
RESEARCH_FROM = "2025-04-01"
NEVER_FROM = "2026-06-21"
FREEZE_SHA = "5274aa97f3359d7dcfaae15cb0590b6147d1624e6056ea396df08c6215209ad4"
MANIFEST_SHA = "256a5410c03065a746d229c2cddbc85240de8fe57db2e8fe77467c1483ffa74d"
REGISTRY_PATH = "ledger/trial_registrations.jsonl"


def sha256(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def row_dates(row: dict) -> list[str]:
    dates = [row["date"], row["entry_date"], row["exit_date"]]
    dates += row.get("open_dates", [])
    for extra in ("d5", "t_minus", "t_plus"):
        if row.get(extra):
            dates.append(row[extra])
    return dates


def check_units(test: str) -> dict:
    viol = Counter()
    first_by_key: dict[str, str] = {}
    last_by_key: dict[str, str] = {}
    n = 0
    for row in iter_units(test, traded_only=False):
        n += 1
        key = row["key"]
        dates = row_dates(row)
        lo, hi = min(dates), max(dates)
        first_by_key[key] = min(first_by_key.get(key, lo), lo)
        last_by_key[key] = max(last_by_key.get(key, hi), hi)
        if hi > WINDOW_END:
            viol["after_window_end"] += 1
        if any(HOLDOUT2[0] <= d <= HOLDOUT2[1] for d in dates):
            viol["holdout2_or_embargo_date"] += 1
        if any(d >= RESEARCH_FROM for d in dates):
            viol["research_window_date"] += 1
        if any(d >= NEVER_FROM for d in dates):
            viol["date_from_2026_06_21"] += 1
        if any(BOUNDARY_GAP[0] <= d <= BOUNDARY_GAP[1] for d in dates):
            viol["date_in_store_gap_2019_05_01_03"] += 1
        if row["entry_date"] <= HIST_LAST and row["exit_date"] >= STEP2_FIRST:
            viol["unit_spans_store_boundary"] += 1
        if key in FALLBACK_ROOTS and lo < FALLBACK_START:
            viol["fallback_root_before_2019_05_06"] += 1
        if key in LISTING and lo < LISTING[key]:
            viol[f"{key}_before_listing"] += 1
        if key not in FALLBACK_ROOTS and key not in LISTING and lo < DEFAULT_START:
            viol["before_2010_07_01"] += 1
        if test in ("H1", "H4") and key == "LE" and row["date"] <= LE_WEAK_END:
            viol["LE_weak_settlement_period_unit"] += 1
        if test == "H2" and row["status"] == "traded" and row["date"] < "2016-01-01":
            viol["H2_traded_before_2016"] += 1
        if row["status"] == "traded" and row["direction"] not in (-1, 1):
            viol["direction_not_pm1"] += 1
    return {"rows": n, "violations": dict(viol), "first_date_by_key": dict(sorted(first_by_key.items())),
            "last_date_by_key": dict(sorted(last_by_key.items()))}


def check_headers() -> dict:
    registry_sha = sha256(REPO / REGISTRY_PATH)
    result_sha = {t: sha256(RUNS / f"{t}_result.json") for t in ("H1", "H2", "H3", "H4")}
    out = {"registry_sha256_computed": registry_sha, "result_sha256_computed": result_sha,
           "freeze_sha256_computed": sha256(REPO / "reports/stage_e16_freeze.json"),
           "manifest_sha256_computed": sha256(REPO / "reports/stage_e17_run_manifest.json"),
           "files": {}}
    for test in ("H1", "H2", "H3", "H4", "H5"):
        for kind in ("RUN_ONCE", "result"):
            with open(RUNS / f"{test}_{kind}.json", encoding="utf-8") as handle:
                raw = json.load(handle)
            rec = {"registry_path_ok": raw.get("registry", {}).get("path") == REGISTRY_PATH,
                   "registry_sha_ok": raw.get("registry", {}).get("sha256") == registry_sha,
                   "freeze_sha_ok": raw.get("freeze_sha256") == FREEZE_SHA,
                   "registration": raw.get("registration"), "test_id": raw.get("test_id")}
            if test == "H5":
                rec["manifest_null"] = raw.get("manifest_sha256") is None
                comps = raw.get("components") or {}
                rec["components_sha_ok"] = all(
                    comps.get(t, {}).get("sha256") == result_sha[t]
                    and comps.get(t, {}).get("path") == f"reports/stage_e17_runs/{t}_result.json"
                    for t in result_sha)
            else:
                rec["manifest_sha_ok"] = raw.get("manifest_sha256") == MANIFEST_SHA
            if kind == "result":
                rec["status"] = raw.get("status")
            out["files"][f"{test}_{kind}"] = rec
    with open(REPO / REGISTRY_PATH, encoding="utf-8") as handle:
        entries = [json.loads(l) for l in handle if l.strip()]
    out["registry"] = {"entries": len(entries), "n_after_last": entries[-1]["n_after"],
                       "ids_sum_from_baseline": entries[0]["n_after"] + sum(len(e["test_ids"]) for e in entries[1:]),
                       "e16_entry": {k: entries[-1][k] for k in ("entry_id", "test_ids", "n_before", "n_after",
                                                                 "freeze_sha256", "time_local")}}
    return out


def main() -> None:
    out = {"units": {t: check_units(t) for t in ("H1", "H2", "H3", "H4")}, "headers": check_headers()}
    for t, rec in out["units"].items():
        print(t, "rows", rec["rows"], "violations", rec["violations"])
    for name, rec in out["headers"]["files"].items():
        bad = [k for k, v in rec.items() if k.endswith("_ok") or k == "manifest_null" if v is not True]
        print(name, "OK" if not bad else f"FAILED {bad}", rec.get("status", ""))
    print("registry:", out["headers"]["registry"])
    write_json(OUT / "checks_windows.json", out)


if __name__ == "__main__":
    main()
