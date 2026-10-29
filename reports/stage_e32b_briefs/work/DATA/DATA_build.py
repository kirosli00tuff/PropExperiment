#!/usr/bin/env python3
"""DATA_build.py: Stage E.32b DataAccess census (D5 inputs h, k, o, p) for the 47 codes.

Reads: ledger/databento_spend.jsonl (quote events, summaries only), file NAMES under data/vendor (ls),
E.28 A1_*.json listing fields, stage_e16_windows.json, stage_e17_fallback.json, sealed-window facts typed below
(with their sources). Never opens a market-data file. Writes F2_data_access.json.
"""
import glob
import json
import os
import re
import statistics
from collections import defaultdict
from datetime import date, datetime, timedelta

REPO = "/home/kiros-li/Documents/GitHub/PropExperiment"
OUT = f"{REPO}/reports/stage_e32b_briefs/F2_data_access.json"
V = f"{REPO}/data/vendor/databento/GLBX.MDP3"

CODES = {  # family -> codes (spec section 0)
    "crude": ["MCL", "QM", "CL"], "natgas": ["MNG", "QG", "NG"],
    "metals": ["MGC", "GC", "SIL", "SI", "MHG", "HG"], "fx": ["M6E", "6E", "M6A", "6A"],
    "crypto": ["MET", "ETH", "MBT", "BTC"], "equity": ["M2K", "RTY", "MYM", "YM", "MNQ", "NQ"],
    "rates": ["2YY", "5YY", "10Y", "30Y", "ZT", "ZF", "ZN", "ZB"],
    "grains": ["MZC", "MZS", "MZW", "MZL", "MZM", "XC", "XK", "XW", "ZC", "ZS", "ZW", "ZL", "ZM"],
}
UNDERLYING = {  # code -> underlying group (spec section 0; 10Y/ZN etc. are separate underlyings)
    "MCL": "WTI", "QM": "WTI", "CL": "WTI", "MNG": "NG", "QG": "NG", "NG": "NG",
    "MGC": "GOLD", "GC": "GOLD", "SIL": "SILVER", "SI": "SILVER", "MHG": "COPPER", "HG": "COPPER",
    "M6E": "EUR", "6E": "EUR", "M6A": "AUD", "6A": "AUD", "MET": "ETH", "ETH": "ETH", "MBT": "BTC", "BTC": "BTC",
    "M2K": "RUSSELL", "RTY": "RUSSELL", "MYM": "DOW", "YM": "DOW", "MNQ": "NASDAQ", "NQ": "NASDAQ",
    "2YY": "2YY", "5YY": "5YY", "10Y": "10Y", "30Y": "30Y", "ZT": "ZT", "ZF": "ZF", "ZN": "ZN", "ZB": "ZB",
    "MZC": "CORN", "XC": "CORN", "ZC": "CORN", "MZS": "SOYBEAN", "XK": "SOYBEAN", "ZS": "SOYBEAN",
    "MZW": "WHEAT", "XW": "WHEAT", "ZW": "WHEAT", "MZL": "SOYOIL", "ZL": "SOYOIL", "MZM": "SOYMEAL", "ZM": "SOYMEAL",
}
ALL = [c for v in CODES.values() for c in v]
assert len(ALL) == 47 and set(ALL) == set(UNDERLYING)

DB_START = date(2010, 6, 6)      # Databento GLBX.MDP3 dataset 'Available from' (catalog page, saved)
MBO_START = date(2017, 5, 21)    # first MBO-granularity day (docs + blog, saved)
CUTOFF = date(2024, 3, 1)
D_DAYS = 21                      # trading days per month used to scale one sampled day to a month (see for_lead)


def parse_d(s):
    s = s.replace("Z", "")
    if "T" in s:
        s = s.split("T")[0]
    return date.fromisoformat(s)


# ---------------- ledger (quote events only; summaries) ----------------
def load_quotes():
    rows = defaultdict(dict)  # (symbol, schema) -> {date_range: usd}  (deduplicated on range+usd)
    nlines = defaultdict(int)
    for line in open(f"{REPO}/ledger/databento_spend.jsonl"):
        d = json.loads(line)
        if d["event"] != "quote" or d["schema"] not in ("mbo", "mbp-1", "tbbo", "mbp-10"):
            continue
        try:
            q = float(d["quoted_usd"])
        except (TypeError, ValueError):
            continue
        key = (d["symbol"], d["schema"])
        nlines[key] += 1
        rows[key].setdefault(d["date"], set()).add(round(q, 6))
    return rows, nlines


def span_days(rng):
    a, b = rng.split("..")
    fa = datetime.fromisoformat(a.replace("Z", "")) if "T" in a else datetime.fromisoformat(a + "T00:00:00")
    fb = datetime.fromisoformat(b.replace("Z", "")) if "T" in b else datetime.fromisoformat(b + "T00:00:00")
    return (fb - fa).total_seconds() / 86400.0


def split_ranges(rows, key):
    """Return (fullday {range: usd}, month {range: usd}) deduplicated; day = 0.9..1.2 days, month >= 25 days."""
    day, mon = {}, {}
    for rng, usds in rows.get(key, {}).items():
        assert len(usds) == 1, (key, rng, usds)
        u = next(iter(usds))
        sd = span_days(rng)
        if 0.9 <= sd <= 1.2:
            day[rng] = u
        elif sd >= 25:
            mon[rng] = u
    return day, mon


def band(k):
    if k is None:
        return 1
    return 0 if k <= 10 else (1 if k <= 50 else 2)


# ---------------- owned data (names only) ----------------
def vendor_ranges(schema, rootdir):
    out = []
    p = f"{V}/{schema}/{rootdir}"
    if not os.path.isdir(p):
        return out
    for fn in sorted(os.listdir(p)):
        m = re.match(r"range=(\d{4}-\d{2}-\d{2})(?:T\d{6}Z)?_(\d{4}-\d{2}-\d{2})(?:T\d{6}Z)?\.dbn\.zst$", fn)
        if m:
            out.append((date.fromisoformat(m.group(1)), date.fromisoformat(m.group(2))))
    return out


def runs(ivs):
    """Merge [a,b) intervals into contiguous runs."""
    out = []
    for a, b in sorted(ivs):
        if out and a <= out[-1][1] + timedelta(days=1):
            out[-1] = (out[-1][0], max(out[-1][1], b))
        else:
            out.append((a, b))
    return out


# sealed windows (sources typed here; checked 2026-10-28 with the status commands named)
SEALED = [
    {"name": "holdout 1 (MES)", "roots": ["MES"], "start": "2026-06-01", "end": "2026-09-16", "kind": "sealed",
     "source": "uv run python -m data.holdout status (raw_files range=2026-06-01..2026-09-16, state sealed, unlocks_logged 0)"},
    {"name": "holdout 2 (MCL, MGC, MHG, NG; also MES store)", "roots": ["MCL", "MGC", "MHG", "NG", "MES"],
     "start": "2024-03-01", "end": "2025-03-31", "kind": "sealed",
     "source": "uv run python -m data.holdout status (holdout_2 products MCL MGC MHG NG, 13 chunks 2024-03-01..2025-03-01 ranges, sealed, unlocks_logged 0); data/sealed names MES_holdout_v1/v2, MCL/MGC/MHG/NG_holdout_v2"},
    {"name": "soy test (ZM, ZS, ZL, every schema)", "roots": ["ZM", "ZS", "ZL"], "start": "2017-05-01", "end": "2020-11-30",
     "kind": "sealed",
     "source": "uv run python reports/stage_e32_briefs/seal/soy_test_seal.py status (114/114 sealed, unlocks 0); docs/soy_test/SOY_TEST_MANIFEST.json roots/window; docs/DECISIONS.md:1063-1066 and :1147 (stays sealed after E.33c)"},
]
SEAL_BY_ROOT = defaultdict(list)
for s in SEALED:
    for r in s["roots"]:
        SEAL_BY_ROOT[r].append(s)
UNDERLYING_ROOTS = defaultdict(list)  # underlying -> codes
for c, u in UNDERLYING.items():
    UNDERLYING_ROOTS[u].append(c)
SEALED_UNDERLYING = {  # underlying -> sealed windows (a root's seal applies to its underlying)
    "WTI": [SEALED[1]], "GOLD": [SEALED[1]], "COPPER": [SEALED[1]], "NG": [SEALED[1]],
    "SOYBEAN": [SEALED[2]], "SOYOIL": [SEALED[2]], "SOYMEAL": [SEALED[2]],
}


def main():
    rows, nlines = load_quotes()
    # ---- E.28 listing fields ----
    listing = {}
    for f in sorted(glob.glob(f"{REPO}/reports/stage_e28_briefs/A1_*.json")):
        for x in json.load(open(f)):
            c = x.get("candidate") or x.get("code")
            for k in ("launch_date", "launch_trade_date"):
                if k in x and isinstance(x[k], dict):
                    v = x[k]
                    listing[c] = {"raw": v.get("value"), "field": f"{os.path.relpath(f, REPO)}:{k}",
                                  "quote": (v.get("quote") or "")[:200], "src": v.get("source_file")}
    def parse_listing(raw):
        if raw is None:
            return None
        if isinstance(raw, int):
            return date(raw, 1, 1)
        m = re.search(r"(\d{4})-(\d{2})-(\d{2})", str(raw))
        if m:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        m = re.search(r"(\d{4})-(\d{2})", str(raw))
        if m and "before" not in str(raw):
            return date(int(m.group(1)), int(m.group(2)), 1)
        m = re.match(r"\s*(\d{4})", str(raw))
        if m and "before" not in str(raw):
            return date(int(m.group(1)), 1, 1)
        return None

    # ---- vendor ohlcv-1m ranges per ledger root ----
    def rootdir(c):
        return f"{c}_v_0"

    bars = {}
    for c in ALL:
        bars[c] = vendor_ranges("ohlcv-1m", rootdir(c))

    def unsealed_cov(code):
        """Days of ohlcv-1m coverage before CUTOFF outside sealed windows; longest run in days; first start."""
        ivs = []
        for a, b in bars[code]:
            b = min(b, CUTOFF)
            if a >= b:
                continue
            ivs.append((a, b))
        # remove sealed windows of this root (names present in vendor dir should already exclude them)
        for s in SEAL_BY_ROOT.get(code, []):
            sa, sb = date.fromisoformat(s["start"]), date.fromisoformat(s["end"]) + timedelta(days=1)
            cut = []
            for a, b in ivs:
                if b <= sa or a >= sb:
                    cut.append((a, b))
                else:
                    if a < sa:
                        cut.append((a, sa))
                    if b > sb:
                        cut.append((sb, b))
            ivs = cut
        rr = runs(ivs)
        tot = sum((b - a).days for a, b in rr)
        longest = max(((b - a).days for a, b in rr), default=0)
        return tot, longest, rr

    # ---- k: MES ratios ----
    mes_mbo_day, mes_mbo_mon = split_ranges(rows, ("MES.v.0", "mbo"))
    mes_mbp1_day, _ = split_ranges(rows, ("ES.v.0", "mbp-1"))  # ledger has NO MES mbp-1/tbbo quote; ES (same index) is the proxy
    mes_mbp10_day, _ = split_ranges(rows, ("MES.v.0", "mbp-10"))
    mes_tbbo_day, _ = split_ranges(rows, ("ES.v.0", "tbbo"))
    assert set(mes_mbo_day) == set(mes_mbp1_day) == set(mes_tbbo_day), "MES sample days differ"
    r_mbp1 = sum(mes_mbo_day.values()) / sum(mes_mbp1_day.values())
    r_tbbo = sum(mes_mbo_day.values()) / sum(mes_tbbo_day.values())
    mes_month = list(mes_mbo_mon.items())
    mes_mbp1_mean_day = statistics.mean(mes_mbp1_day.values())
    r_month_alt = mes_month[0][1] / (mes_mbp1_mean_day * D_DAYS)
    ratios = {
        "r": round(r_mbp1, 4),
        "r_definition": "sum of MES ledger MBO quotes / sum of ES.v.0 (proxy for MES) ledger mbp-1 quotes, over the same 5 full-day sample days (one per month: "
                        + ", ".join(sorted(m[:7] for m in (k.split('..')[1] for k in mes_mbo_day)))
                        + "); sample days are 23-hour trade-date ranges; RTH sub-window quotes and the month quote excluded so that both schemas cover identical days",
        "mes_mbo_full_day_quotes": {k: v for k, v in sorted(mes_mbo_day.items())},
        "es_mbp1_full_day_quotes_proxy_for_mes": {k: v for k, v in sorted(mes_mbp1_day.items())},
        "es_tbbo_full_day_quotes_proxy_for_mes": {k: v for k, v in sorted(mes_tbbo_day.items())},
        "r_proxy_note": "RULE NOT APPLIABLE AS WRITTEN: the ledger holds no MES mbp-1 or tbbo quote (MES has only mbo and mbp-10). r uses ES.v.0 mbp-1 over the identical 5 sample days as the MES MBO quotes (ES = same index, 10x notional). See for_lead.",
        "r_alt_mbp10": round(sum(mes_mbo_day.values()) / sum(mes_mbp10_day.values()), 4),
        "r_alt_mbp10_definition": "MES MBO / MES mbp-10, same 5 days (MES's own pair; mbp-10 is a deeper schema than mbp-1, so not a substitute for mbp-1 scaling)",
        "r_tbbo": round(r_tbbo, 4),
        "r_tbbo_definition": "sum MES MBO full-day quotes / sum MES tbbo full-day quotes, same 5 days (method 3 factor)",
        "mes_mbo_month_quote": {"range": mes_month[0][0], "usd": mes_month[0][1],
                                "note": "the only whole-month MBO quote in the ledger for a universe-adjacent root (MES, 2025-10-01..2025-10-29, 28 days); stage-D.1e-2026-09-21"},
        "r_month_alt": round(r_month_alt, 4),
        "r_month_alt_definition": f"MES MBO month quote / (ES mean mbp-1 full-day quote x {D_DAYS}); cross-check of r on a month basis",
        "days_per_month_used": D_DAYS,
        "mes_mbo_day_mean_x_days": round(statistics.mean(mes_mbo_day.values()) * D_DAYS, 3),
    }
    # ZM comparison ratio (different months, not used)
    zm_mbo_day, zm_mbo_mon = split_ranges(rows, ("ZM.v.0,ZM.v.1", "mbo"))
    zm_mbp1_day, _ = split_ranges(rows, ("ZM.v.0", "mbp-1"))
    zm_mbo_mean_month = statistics.mean(zm_mbo_mon.values())
    zm_mbp1_month_est = statistics.mean(zm_mbp1_day.values()) * D_DAYS
    ratios["zm_comparison"] = {
        "zm_mbo_mean_usd_per_month": round(zm_mbo_mean_month, 4), "zm_mbo_months": len(zm_mbo_mon),
        "zm_mbo_span": f"{min(zm_mbo_mon)} .. {max(zm_mbo_mon)}",
        "zm_mbo_symbols": "ZM.v.0,ZM.v.1 (front and second contract together)",
        "zm_mbp1_day_mean": round(statistics.mean(zm_mbp1_day.values()), 5),
        "zm_mbp1_month_est": round(zm_mbp1_month_est, 4),
        "ratio_zm_mbo_over_mbp1": round(zm_mbo_mean_month / zm_mbp1_month_est, 3),
        "note": "ZM MBO months are 2020-11..2024-02 (two contracts) and ZM mbp-1 sample days are 2025-05..2026-04: different months and contracts, shown for comparison only, not used",
    }
    # ZS / ZL month-level mbp-1 (2020-11..2024-02) vs ZM mbo same months
    comp = {}
    for sym in ("ZS.v.0", "ZL.v.0"):
        dday, dmon = split_ranges(rows, (sym, "mbp-1"))
        comp[sym] = {"months": len(dmon), "mean_usd_per_month": round(statistics.mean(dmon.values()), 4),
                     "day_mean_x_days": round(statistics.mean(dday.values()) * D_DAYS, 4)}
        same = [rng for rng in dmon if rng in zm_mbo_mon]
        comp[sym]["same_month_ratio_zm_mbo_over_this_mbp1"] = round(
            sum(zm_mbo_mon[r] for r in same) / sum(dmon[r] for r in same), 3)
        comp[sym]["same_months"] = len(same)
    ratios["zm_comparison"]["zs_zl_monthly_mbp1_same_months"] = comp
    ratios["tbbo_note"] = "method (3) is unused: every universe root with a ledger tbbo quote also has mbp-1 quotes"

    # ---- k per code ----
    def k_for(code):
        if code in ("ZM",):
            sym_mbo = ("ZM.v.0,ZM.v.1", "mbo")
        sym = f"{code}.v.0"
        info = {"ledger_symbol": sym}
        # method 1: ledger MBO for the root
        if code == "ZM":
            mon = zm_mbo_mon
            val = statistics.mean(mon.values())
            info.update({"months_covered": len(mon), "span": f"{min(mon)} .. {max(mon)}",
                         "n_quote_lines_raw": nlines[("ZM.v.0,ZM.v.1", "mbo")], "n_distinct_month_ranges": len(mon),
                         "sum_usd_distinct": round(sum(mon.values()), 4),
                         "note": "quotes cover ZM.v.0 and ZM.v.1 together (two contracts), so a front-only month is lower; repeated quote lines deduplicated on range+usd"})
            return val, "ledger MBO", info
        # method 2: ledger mbp-1 x r
        day, mon = split_ranges(rows, (sym, "mbp-1"))
        if mon:  # root with whole-month mbp-1 quotes (ZS, ZL)
            val = statistics.mean(mon.values()) * r_mbp1
            info.update({"mbp1_months_covered": len(mon), "mbp1_span": f"{min(mon)} .. {max(mon)}",
                         "mbp1_usd_per_month_mean": round(statistics.mean(mon.values()), 4), "r": round(r_mbp1, 4),
                         "mbp1_day_samples": len(day), "mbp1_day_mean_x_days": round(statistics.mean(day.values()) * D_DAYS, 4) if day else None,
                         "n_quote_lines_raw": nlines[(sym, "mbp-1")],
                         "note": "mbp-1 USD per month from whole-month quotes (2020-11..2024-02), repeated quote lines deduplicated"})
            return val, "scaled from mbp-1 (estimate)", info
        if day:
            dm = statistics.mean(day.values())
            val = dm * D_DAYS * r_mbp1
            info.update({"mbp1_sample_days": len(day), "mbp1_sample_months": sorted({k.split('..')[1][:7] for k in day}),
                         "mbp1_sum_usd_distinct": round(sum(day.values()), 4), "mbp1_day_mean": round(dm, 5),
                         "days_per_month": D_DAYS, "mbp1_usd_per_month_est": round(dm * D_DAYS, 4), "r": round(r_mbp1, 4),
                         "n_quote_lines_raw": nlines[(sym, "mbp-1")],
                         "note": "5 one-trade-day quotes (one per month, 2025-05..2026-04); month = mean day x 21; repeated quote lines deduplicated"})
            return val, "scaled from mbp-1 (estimate)", info
        # method 3: tbbo
        tday, _ = split_ranges(rows, (sym, "tbbo"))
        if tday:
            val = statistics.mean(tday.values()) * D_DAYS * r_tbbo
            info.update({"tbbo_sample_days": len(tday)})
            return val, "scaled from tbbo (estimate)", info
        info["note"] = "no ledger quote of any of mbo, mbp-1 or tbbo for this root"
        return None, "unknown", info

    # ---- h ----
    first_vendor = {}
    for c in ALL:
        if bars[c]:
            first_vendor[c] = min(a for a, _ in bars[c])
    # ---- read windows (registered searches) ----
    wins = json.load(open(f"{REPO}/reports/stage_e16_windows.json"))["products"]
    fb = json.load(open(f"{REPO}/reports/stage_e17_fallback.json"))
    fb_roots, fb_win = set(fb["roots"]), fb["window"]
    E21_ROOTS = ["ZT", "NQ", "ZF", "NG", "ZN", "UB", "ZL", "ZC", "CL", "6E", "ZB", "TN", "LE", "GC", "HE", "ZS", "RTY"]
    read = {}  # root -> list of dict windows
    for root, w in wins.items():
        if root in fb_roots:
            s, e = fb_win
            src = "reports/stage_e17_fallback.json (fallback window, 'not funded'); E.17_RETURN.md:26"
        else:
            s, e = w["window_start_on_or_after"], w["window_end"]
            src = "reports/stage_e16_windows.json products[%s]" % root
        read.setdefault(root, []).append({
            "registration": "r002-E16 (E16-H1..H5)", "ledger_line": 3, "start": s, "end": e, "bar_based_directional": True,
            "source": src + "; reports/E.16_RETURN.md:27-31 (H1-H5 on 27 markets), :224; docs/STAGES.md:149-158; ledger/trial_registrations.jsonl line 3"})
    for root in E21_ROOTS:
        w = wins[root]
        read[root].append({
            "registration": "r006-E21 (TSMOM-12, trend blend, TOM, book; 17 roots)", "ledger_line": 7,
            "start": w["window_start_on_or_after"], "end": w["window_end"], "bar_based_directional": True,
            "source": "reports/E.21_RETURN.md:1,375-395 (per-root table); reports/stage_e21_freeze.json inputs.windows = reports/stage_e16_windows.json; ledger line 7"})
        read[root].append({
            "registration": "r005-E20S (45-configuration search; 17 roots)", "ledger_line": 6, "start": "2019-05-06", "end": "2024-02-29",
            "bar_based_directional": True, "source": "reports/E.20_RETURN.md:554 (2019-05..2024-02); ledger line 6"})
    for root in ("ZM", "ZS", "ZL"):
        read.setdefault(root, []).append({
            "registration": "r009-E33 (ZM discovery, 300 configurations; ZM MBO, ZS and ZL MBP-1)", "ledger_line": 10,
            "start": "2020-12-01", "end": "2024-02-29", "bar_based_directional": True,
            "source": "docs/DECISIONS.md:1061-1063 (discovery uses owned ZM MBO and ZS and ZL MBP-1, 2020-12 to 2024-02); docs/STAGES.md:241-259; ledger line 10"})
    read.setdefault("NG", []).append({
        "registration": "r001-C1 / r003-C1b (NG backward replication; CL and MBT as feature legs)", "ledger_line": "2 and 4",
        "start": "2010-06-07", "end": "2019-04-30", "bar_based_directional": True,
        "source": "docs/STAGES.md:138-143,159-162; reports/E.18_RETURN.md:301 (NG window 2010-06-07 onward; end not re-read here)"})
    read["NG"][-1]["note"] = "listed for completeness; not needed for p (E16 covers NG 2010-07..2024-02)"

    def merge_read(u):
        iv = []
        for c in UNDERLYING_ROOTS[u]:
            for w in read.get(c, []):
                if w["registration"].startswith(("r002", "r006", "r005", "r009")):
                    iv.append((date.fromisoformat(w["start"]), date.fromisoformat(w["end"]) + timedelta(days=1)))
        return runs(iv)

    # ---- per-underlying history start (earliest sibling listing) ----
    def code_listing_date(c):
        l = listing.get(c)
        d = parse_listing(l["raw"]) if l else None
        return d

    e16w = json.load(open(f"{REPO}/reports/stage_e16_windows.json"))["products"]

    def early_evidence(c):
        """(date, text) if the product demonstrably traded/was priced by 2010-07, else None."""
        fv = first_vendor.get(c)
        if fv is not None and fv <= date(2010, 7, 1):
            return fv, f"file names data/vendor/databento/GLBX.MDP3/ohlcv-1m/{c}_v_0 (first range starts {fv.isoformat()})"
        w = e16w.get(c)
        if w and w["start_month"] <= "2010-07" and w["e12_quoted_usd"] > 0:
            return date(2010, 7, 1), (f"reports/stage_e16_windows.json products[{c}] start_month {w['start_month']}, e12_quoted_usd {w['e12_quoted_usd']} (> 0: Databento priced bars from 2010-07)")
        return None

    codes_out, for_lead = {}, []
    per_code_kband = {}
    for c in ALL:
        u = UNDERLYING[c]
        # h
        ld = code_listing_date(c)
        l = listing.get(c)
        fv = first_vendor.get(c)
        if ld is not None:
            eff = max(ld, MBO_START)
            h_basis = f"listing {ld.isoformat()} (E.28 {l['field']}: '{l['raw']}')"
            listing_src = f"{l['field']}; {l['src']}"
        elif early_evidence(c) is not None:
            ev = early_evidence(c)
            ld = None
            eff = MBO_START
            h_basis = (f"listing date not sourced in E.28 ('{l['raw'] if l else None}'); evidence the product traded by {ev[0].isoformat()}, before the MBO start: {ev[1]}")
            listing_src = f"{ev[1]}; E.28 field {l['field'] if l else 'none'}"
        else:
            eff, h_basis, listing_src = None, "listing unknown and no pre-2017 vendor file", "none"
        if eff is None:
            h = 1
        elif eff <= date(2017, 6, 30):
            h = 0
        elif eff <= date(2020, 12, 31):
            h = 1
        else:
            h = 2
        # k
        kval, kmeth, kinfo = k_for(c)
        kb = band(kval)
        # sensitivity of band to the days-per-month scale
        sens = {}
        if kval is not None and kmeth.startswith("scaled") and "mbp1_sample_days" in kinfo:
            dm = kinfo["mbp1_day_mean"]
            for name, dd in (("literal_1_day", 1.0), ("calibrated_22.03", mes_month[0][1] / statistics.mean(mes_mbo_day.values()))):
                sens[name] = {"k_usd": round(dm * dd * r_mbp1, 4), "band": band(dm * dd * r_mbp1)}
            r10 = sum(mes_mbo_day.values()) / sum(mes_mbp10_day.values())
            sens["r_alt_mbp10_days21"] = {"k_usd": round(dm * D_DAYS * r10, 4), "band": band(dm * D_DAYS * r10)}
            sens["r_1.0_days21"] = {"k_usd": round(dm * D_DAYS, 4), "band": band(dm * D_DAYS)}
        per_code_kband[c] = sens
        # o
        grp = UNDERLYING_ROOTS[u]
        cov = {g: unsealed_cov(g) for g in grp}
        best = max(grp, key=lambda g: cov[g][0])
        o = 0 if cov[best][0] >= 36 * 30.4375 else 1
        owned = []
        for g in grp:
            for schema, rd in (("ohlcv-1m", f"{g}_v_0"), ("mbp-1", f"{g}_v_0")):
                ivs = vendor_ranges(schema, rd)
                if not ivs:
                    continue
                for a, b in runs(ivs):
                    sealed_overlap = [s["name"] for s in SEAL_BY_ROOT.get(g, [])
                                      if not (b <= date.fromisoformat(s["start"]) or a > date.fromisoformat(s["end"]))]
                    owned.append({"schema": schema, "root": g, "first_month": a.isoformat()[:7], "last_month": (b - timedelta(days=1)).isoformat()[:7],
                                  "first_day": a.isoformat(), "end_exclusive": b.isoformat(), "sealed": bool(sealed_overlap),
                                  "overlaps_seal": sealed_overlap})
        if c == "ZM":
            for a, b in runs(vendor_ranges("mbo", "Z1_ZM_v_0-ZM_v_1")):
                owned.append({"schema": "mbo", "root": "ZM", "first_month": a.isoformat()[:7], "last_month": (b - timedelta(days=1)).isoformat()[:7],
                              "first_day": a.isoformat(), "end_exclusive": b.isoformat(), "sealed": False, "overlaps_seal": []})
        o_info = {g: {"unsealed_days_before_2024-03-01": cov[g][0], "months_equiv": round(cov[g][0] / 30.4375, 1),
                      "longest_run_months": round(cov[g][1] / 30.4375, 1)} for g in grp}
        # sealed windows of this code's underlying
        sealed_w = [{"name": s["name"], "start": s["start"], "end": s["end"], "source": s["source"]} for s in SEALED_UNDERLYING.get(u, [])]
        # p
        srl = merge_read(u)
        sibl_listings = [code_listing_date(g) for g in grp if code_listing_date(g)]
        sibl_vendor = [g for g in grp if early_evidence(g) is not None]
        if sibl_vendor or any(d <= DB_START for d in sibl_listings):
            A = DB_START
            a_basis = "an old sibling/product listed before Databento's start 2010-06-06 (listing or ohlcv-1m vendor evidence)"
        elif sibl_listings:
            A = max(min(sibl_listings), DB_START)
            a_basis = f"earliest sibling listing {min(sibl_listings).isoformat()}"
        else:
            A = None
            a_basis = "unknown"
        unread = []
        if A is not None:
            cur = A
            for a, b in srl:
                if a > cur:
                    unread.append((cur, min(a, CUTOFF)))
                cur = max(cur, b)
            if cur < CUTOFF:
                unread.append((cur, CUTOFF))
            unread = [(a, b) for a, b in unread if b > a]
        # remove sealed windows (pre-cutoff) from unread
        for s in SEALED_UNDERLYING.get(u, []):
            sa, sb = date.fromisoformat(s["start"]), date.fromisoformat(s["end"]) + timedelta(days=1)
            cut = []
            for a, b in unread:
                if b <= sa or a >= sb:
                    cut.append((a, b))
                else:
                    if a < sa:
                        cut.append((a, sa))
                    if b > sb:
                        cut.append((sb, b))
            unread = cut
        big = [(a, b, round((b - a).days / 30.4375, 1)) for a, b in unread if (b - a).days >= 36 * 30.4375]
        any_sealed = bool(SEALED_UNDERLYING.get(u))
        if A is None:
            p, p_basis = 0, "unknown history start: p = 0 (unknown 0)"
        else:
            p = 1 if (not big and not any_sealed) else 0
            reasons = []
            if big:
                reasons.append("unread unsealed stretch(es) of 36 months or more before 2024-03-01: " + "; ".join(f"{a}..{b} ({m} months)" for a, b, m in big))
            if any_sealed:
                reasons.append("window(s) of the underlying sealed for a future test: " + "; ".join(f"{s['name']} {s['start']}..{s['end']}" for s in SEALED_UNDERLYING[u]))
            if not reasons:
                tot_hist = round((CUTOFF - A).days / 30.4375, 1)
                reasons.append(f"history {A.isoformat()}..2024-02-29 ({tot_hist} months) fully read by registered searches or no unread stretch of 36 months or more")
            p_basis = "; ".join(reasons)
        tot_hist = round((CUTOFF - A).days / 30.4375, 1) if A else None
        vacuous = bool(A and tot_hist < 36 and not any_sealed)
        # spec reading of p (seal limited to pre-2024-03 windows)
        pre_sealed = [s for s in SEALED_UNDERLYING.get(u, []) if date.fromisoformat(s["end"]) < CUTOFF]
        p_spec = None
        if A is not None:
            p_spec = 1 if (not big and not pre_sealed) else 0
        rw = []
        for g in grp:
            for w in read.get(g, []):
                rw.append({"root": g, **w})
        codes_out[c] = {
            "underlying": u, "siblings": [g for g in grp if g != c],
            "mbo_start": (eff.isoformat() if eff else None),
            "mbo_start_source": f"{h_basis}; Databento GLBX.MDP3 MBO-granularity start 2017-05-21 (pages/DATA/blog_cme_history_2010.txt:98-100 'highest granularity available for this period is MBP-10'; glbx_mdp3_dataset.txt:1172)",
            "listing_date": (ld.isoformat() if ld else None), "listing_source": listing_src,
            "listing_raw_e28": (l["raw"] if l else None),
            "h": h,
            "k_usd_month": (round(kval, 4) if kval is not None else None), "k_method": kmeth, "k_inputs": kinfo,
            "k": kb, "k_band_sensitivity": sens,
            "owned": owned, "o_owned_36m": o, "o": o, "o_inputs": o_info,
            "sealed_windows": sealed_w, "read_windows": rw,
            "p_all_read": p, "p": p, "p_basis": p_basis, "p_history_start": (A.isoformat() if A else None),
            "p_history_start_basis": a_basis, "p_history_months": tot_hist,
            "p_vacuous_short_history": vacuous, "p_spec_reading": p_spec,
            "p_unread_stretches": [{"start": a.isoformat(), "end_exclusive": b.isoformat(), "months": m} for a, b, m in big],
            "D5_informational": max(0, 4 - h - kb - o - p),
        }
    # ---- published prices ----
    published = [
        {"item": "Databento historical pricing basis", "value": "usage-based, $/GB of uncompressed binary size; no per-schema dollar rate stated in saved page text",
         "quote": "Historical data is priced in $/GB. Every month, you pay only for the historical data that you've used.",
         "file": "pages/DATA/faq_usage_pricing.txt:704", "url": "https://databento.com/docs/faqs/usage-pricing-and-data-credits", "status": "verified (saved page)"},
        {"item": "Databento pricing page", "value": "table of $/GB or $/MB rates is rendered client-side; values not in the saved static or Scrapling-rendered page",
         "quote": "The pricing table above lists $/GB or $/MB rates by", "file": "pages/DATA/pricing_rendered.html", "url": "https://databento.com/pricing", "status": "verified (saved page); rate itself NOT retrieved"},
        {"item": "GLBX.MDP3 'from $0.50/GB' (web search snippet)", "value": 0.50, "unit": "USD/GB (floor)", "status": "[unverified] snippet only; not used",
         "source": "WebSearch #2 on 2026-10-28, snippet text, no saved page"},
        {"item": "Ledger-implied effective rate, MES MBO month", "value": round(mes_month[0][1] / 13141722832 * 1e9, 4), "unit": "USD per 1e9 billable bytes",
         "quote": "ledger quote 2026-09-22T01:12:17 MES.v.0 mbo 2025-10-01T00:00:00Z..2025-10-29T00:00:00Z quoted_usd 22.0305 billable_bytes 13141722832",
         "source": "ledger/databento_spend.jsonl (stage-D.1e-2026-09-21)", "status": "program's own quote, not a published price"},
    ]
    out = {
        "stage": "E.32b", "worker": "B4 DataAccess-SonnetHigh", "generated_pdt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "spec": "reports/stage_e32b_ranking_spec.md section 3 D5 (h, k, o, p); universe: 47 codes of section 0",
        "databento_dataset": {"glbx_mdp3_available_from": "2010-06-06", "mbo_granularity_from": "2017-05-21",
                              "sources": ["pages/DATA/catalog_glbx_rendered.html ('Available from' 2010-06-06; 'Data prior to 2017-05-21 ...')",
                                          "pages/DATA/glbx_mdp3_dataset.txt:706-708,1172", "pages/DATA/blog_cme_history_2010.txt:97-100"]},
        "sealed_windows_all": SEALED,
        "codes": codes_out, "ratios": ratios, "published_prices": published,
        "assumptions": {"days_per_month": D_DAYS, "cutoff": "2024-03-01", "p_rule_reading": "brief reading (any sealed window of the underlying, including holdout 2 after 2024-03, makes p = 0); p_spec_reading gives the spec-text reading"},
        "for_lead": [],
    }
    json.dump(out, open(OUT, "w"), indent=1)
    print("wrote", OUT, len(codes_out))


if __name__ == "__main__":
    main()
