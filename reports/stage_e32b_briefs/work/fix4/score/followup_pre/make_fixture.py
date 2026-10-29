"""make_fixture.py: a small SYNTHETIC fixture for score32b.py and r3_score.py (invented numbers, no real fact).

11 codes (crude MCL QM CL; equity MNQ NQ MYM YM; metals SIL SI; grains MZM ZM), 3 firms (topstep, lucid, bulenox).
Built to exercise: an OC1 transfer (QM, MNQ, MYM, MZM), unknown sigma (SI, SIL), a D1 boundary (YM r_60 = 0.025
exactly), the D4 = 0 gate (QM, SIL), the sigma gate (MZM: 2.9 < 3.0), satellites by rule i and ii, an unknown ADV
with a larger-size sibling (MZM), an unknown attention count, an unsourced spread, A = 0, an unlisted pair, an
unknown listing, Lucid with no DLL, unknown P items and an unknown Rel deduction.
Run: uv run python make_fixture.py [out_dir]  (default: ./fixture)
"""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from s32b_common import SPEC_SHA256, write_json  # noqa: E402

H = ("1", "2", "5", "15", "30", "60", "120", "240")
FIRMS_FX = ("topstep", "lucid", "bulenox")
CODES_FX = ("MCL", "QM", "CL", "MNQ", "NQ", "MYM", "YM", "SIL", "SI", "MZM", "ZM")
FAMILY_FX = {"MCL": "crude", "QM": "crude", "CL": "crude", "MNQ": "equity", "NQ": "equity", "MYM": "equity",
             "YM": "equity", "SIL": "metals", "SI": "metals", "MZM": "grains", "ZM": "grains"}
UNDERLYING_FX = {"MCL": "crude oil", "QM": "crude oil", "CL": "crude oil", "MNQ": "Nasdaq-100", "NQ": "Nasdaq-100",
                 "MYM": "Dow", "YM": "Dow", "SIL": "silver", "SI": "silver", "MZM": "soybean meal",
                 "ZM": "soybean meal"}


def _root(status, tick, sig60, close, rd_med, rd_p99, l_main=390, src=None, factor=None):
    if status == "unknown":
        return {"status": "unknown", "oc1_source": None, "oc1_factor": None, "tick_size": tick, "n_dates": 0,
                "L_main": l_main, "main_session_pt": ["06:30", "13:00"], "h": {k: {} for k in H},
                "OC": {"sigma": None, "m": None, "n": 0}, "overnight": {}, "R_d": {"median": None, "p99": None},
                "main_range_median": None, "median_close": None}
    hs = {}
    for k in H:
        sig = sig60 if k == "60" else round(sig60 * math.sqrt(int(k) / 60), 4)
        hs[k] = {"sigma": sig, "m": round(0.8 * sig, 4), "median_abs": round(0.67 * sig, 4),
                 "p99_abs": round(2.9 * sig, 4), "n": 50000}
    oc = round(sig60 * math.sqrt(l_main / 60), 4)
    return {"status": status, "oc1_source": src, "oc1_factor": factor, "tick_size": tick, "n_dates": 250,
            "L_main": l_main, "main_session_pt": ["06:30", "13:00"], "h": hs,
            "OC": {"sigma": oc, "m": round(0.8 * oc, 4), "n": 250},
            "overnight": {"cc": {"sigma": oc * 1.2, "m": oc, "n": 249}, "on": {"sigma": oc * 0.5, "m": oc * 0.4,
                                                                            "n": 249}},
            "R_d": {"median": rd_med, "p99": rd_p99, "n": 250}, "main_range_median": rd_med * 0.7,
            "median_close": close}


def f3_doc():
    roots = {
        "CL": _root("owned", 0.01, 44.0, 80.0, 250, 700),
        "MCL": _root("owned", 0.01, 44.0, 80.0, 250, 700),
        "QM": _root("OC1", 0.025, 17.6, None, 100, 280, src="CL", factor=0.4),
        "NQ": _root("owned", 0.25, 160.0, 15000.0, 900, 1600),
        "MNQ": _root("OC1", 0.25, 160.0, None, 900, 1600, src="NQ", factor=1.0),
        "YM": _root("owned", 1.0, 60.0, 34000.0, 300, 500),
        "MYM": _root("OC1", 1.0, 60.0, None, 300, 500, src="YM", factor=1.0),
        "SI": _root("unknown", 0.005, None, None, None, None),
        "SIL": _root("unknown", 0.005, None, None, None, None),
        "ZM": _root("owned", 0.1, 5.8, 400.0, 60, 120, l_main=290),
        "MZM": _root("OC1", 0.2, 2.9, None, 30, 60, l_main=290, src="ZM", factor=0.5),
    }
    return {"spec_sha256": SPEC_SHA256, "window": "2022-11-01..2023-10-31", "generated_pdt": "SYNTHETIC",
            "files_opened": [], "roots": roots}


def _code(code, tick, mult, adv, spread=None, touch=None, sibs=(), leader=None, settles=None, da=None):
    return {"family": FAMILY_FX[code], "underlying": UNDERLYING_FX[code], "excluded": code == "NQ",
            "tick_size": tick, "tick_value_usd": round(tick * mult, 10), "multiplier": mult,
            "adv": {"value": adv, "kind": "synthetic", "source": "SYNTHETIC"},
            "spread_S": ({"value": spread, "sourced": True, "item": f"SYN-{code}-S"} if spread is not None
                         else {"value": None, "sourced": False, "item": None}),
            "touch": ({"value": touch, "sourced": True, "item": f"SYN-{code}-T"} if touch is not None
                      else {"value": None, "sourced": False, "item": None}),
            "siblings": list(sibs), "leader": leader or code,
            "settles_off_sibling": settles or {"value": False, "sibling": None, "item": None},
            "main_session_pt": ["06:30", "13:00"], "pauses": [], "listing": "SYNTHETIC",
            "data_access": da or {}}


def _da(start, k, kind, owned, read):
    return {"mbo_start": start, "k_usd_month": k, "k_kind": kind, "o_owned_36m": owned, "p_all_read": read}


def f4_doc():
    codes = {
        "CL": _code("CL", 0.01, 1000, 250000, 1, 15, ("MCL", "QM"), "CL",
                    da=_da("2017-05-21", 8.5, "ledger MBO", True, False)),
        "MCL": _code("MCL", 0.01, 100, 60000, None, None, ("CL", "QM"), "CL",
                     da=_da("2021-07-12", 3.0, "ledger MBO", True, False)),
        "QM": _code("QM", 0.025, 500, 1500, 1, None, ("CL", "MCL"), "CL",
                    settles={"value": True, "sibling": "CL", "item": "SYN-QM-settle"},
                    da=_da("2017-05-21", None, "unknown", True, False)),
        "NQ": _code("NQ", 0.25, 20, 600000, 1, 20, ("MNQ",), "NQ",
                    da=_da("2017-05-21", 40.0, "ledger MBO", True, True)),
        "MNQ": _code("MNQ", 0.25, 2, 900000, 1, 30, ("NQ",), "NQ",
                     da=_da("2019-05-06", 9.0, "ledger MBO", True, True)),
        "YM": _code("YM", 1.0, 5, 120000, 1, 6, ("MYM",), "YM",
                    da=_da("2017-05-21", 20.0, "scaled from mbp-1 (estimate)", True, False)),
        "MYM": _code("MYM", 1.0, 0.5, 100000, None, None, ("YM",), "YM",
                     da=_da("2019-05-06", 4.0, "scaled from mbp-1 (estimate)", True, False)),
        "SI": _code("SI", 0.005, 5000, 50000, None, None, ("SIL",), "SI", da=_da(None, None, "unknown", False, None)),
        "SIL": _code("SIL", 0.005, 1000, 4000, None, None, ("SI",), "SI",
                     da=_da("2017-05-21", 60.0, "ledger MBO", False, False)),
        "ZM": _code("ZM", 0.1, 100, 50000, 1.5, 3, ("MZM",), "ZM",
                    da=_da("2017-05-21", 60.0, "ledger MBO", True, True)),
        "MZM": _code("MZM", 0.2, 10, None, None, None, ("ZM",), "ZM",
                     da=_da("2023-02-27", 12.0, "scaled from tbbo (estimate)", True, True)),
    }
    firms = {
        "topstep": {"dll_50k": 1000, "mll_50k": 2000, "mll_type": "EOD trailing", "bc_accepts": True,
                    "flat_by_close": "13:10 PT", "overnight": {}, "payout": {}, "news_windows": [],
                    "p_inputs": {"native_api": True, "oco_api": True, "vps_chicago": "prohibited",
                                 "api_rate_limit_per_s": 50}, "rel_facts": {}},
        "lucid": {"dll_50k": "none", "mll_50k": 2000, "mll_type": "EOD trailing", "bc_accepts": True,
                  "flat_by_close": "13:45 PT", "overnight": {}, "payout": {}, "news_windows": [],
                  "p_inputs": {"native_api": False, "oco_api": None, "vps_chicago": "unknown",
                               "api_rate_limit_per_s": None}, "rel_facts": {}},
        "bulenox": {"dll_50k": 1100, "mll_50k": 2500, "mll_type": "intraday trailing", "bc_accepts": True,
                    "flat_by_close": "13:59 PT", "overnight": {}, "payout": {}, "news_windows": [],
                    "p_inputs": {"native_api": True, "oco_api": True, "vps_chicago": "allowed",
                                 "api_rate_limit_per_s": "no_limit"}, "rel_facts": {}},
    }
    pairs = {}
    for f in FIRMS_FX:
        for c in CODES_FX:
            listed = not (f == "lucid" and c == "QM")
            if f == "bulenox" and c == "ZM":
                listed = None
            pairs[f"{f}|{c}"] = {"listed_50k": listed, "fee_rt_usd": 1.5, "fee_kind": "stated",
                                 "news_window_items": []}
    return {"spec_sha256": SPEC_SHA256, "codes": codes, "firms": firms, "pairs": pairs}


def _r(v, unknown=False, unverified=False):
    out = {"value": None if unknown else v, "unknown": unknown, "reason": "SYNTHETIC"}
    if unverified:
        out["unverified"] = True
    return out


def blind_doc():
    def cr(a, b, s1, s2, s3, s3i, d6, **kw):
        return {"D2a": a, "D2b": b, "s1": s1, "s2": s2, "s3": s3, "sat_iii": s3i, "D6": d6, **kw}
    codes = {
        "CL": cr(_r(1), _r(1), _r(2), _r(1), _r(1), _r(0), _r(3)),
        "MCL": cr(_r(0, unknown=True), _r(0), _r(1), _r(1), _r(1), _r(0), _r(2)),
        "QM": cr(_r(0), _r(0), _r(1), _r(1), _r(0), _r(0), _r(2)),
        "NQ": cr(_r(1), _r(1), _r(1), _r(2), _r(1), _r(0), _r(4)),
        "MNQ": cr(_r(1), _r(0), _r(1), _r(2), _r(1), _r(0), _r(2)),
        "YM": cr(_r(1), _r(0, unknown=True), _r(1), _r(1), _r(1), _r(0), _r(3)),
        "MYM": cr(_r(0), _r(0), _r(1), _r(1), _r(1), _r(0), _r(1)),
        "SI": cr(_r(0), _r(1), _r(1), _r(1), _r(0), _r(0), _r(0, unknown=True)),
        "SIL": cr(_r(0), _r(0), _r(0), _r(0), _r(0), _r(0), _r(1)),
        "ZM": cr(_r(0), _r(0), _r(2, unverified=True), _r(1), _r(1), _r(0), _r(4, unverified=True)),
        "MZM": cr(_r(0), _r(0), _r(1), _r(1), _r(1), _r(0), _r(2)),
    }
    pairs = {}
    for f in FIRMS_FX:
        for c in CODES_FX:
            r = _r(3) if f == "topstep" else _r(4)
            if f == "bulenox" and c == "CL":
                r = _r(0, unknown=True)
            a = _r(0) if (f == "lucid" and c == "MNQ") else _r(3 if f == "topstep" else 4)
            pairs[f"{f}|{c}"] = {"R": r, "A": a}
    firms = {"topstep": {"rel_age": _r(0), "rel_payout": _r(0), "rel_rules": _r(1), "rel_regulatory": _r(0)},
             "lucid": {"rel_age": _r(1), "rel_payout": _r(0), "rel_rules": _r(0), "rel_regulatory": _r(0)},
             "bulenox": {"rel_age": _r(0), "rel_payout": _r(0, unknown=True), "rel_rules": _r(0),
                         "rel_regulatory": _r(0)}}
    return {"codes": codes, "pairs": pairs, "firms": firms}


M_STAR = {"CL": 0.05, "MCL": 0.08, "QM": 0.12, "MNQ": 0.03, "YM": 0.06, "MYM": 0.098, "ZM": 0.25, "MZM": None}
FIRM_OFF = {"topstep": 0.0, "lucid": 0.01, "bulenox": 0.005}


def _block(code, firm, sig60, scale=1.0):
    base = M_STAR[code]
    if base is None:
        return {"mu_star_mkt": None, "mu10K_mkt": None, "above_cap": {"mu_star": True, "mu10K": True},
                "cost_per_attempt": 40.0, "sigma60": sig60, "m_star": None, "m10K": None, "grid_cap": 4}
    m = round((base + FIRM_OFF[firm]) * scale, 6)
    m10 = round(1.6 * m, 6)
    return {"mu_star_mkt": round(m * sig60, 6), "mu10K_mkt": round(m10 * sig60, 6),
            "above_cap": {"mu_star": False, "mu10K": False}, "cost_per_attempt": 20.0 + 100 * FIRM_OFF[firm],
            "sigma60": sig60, "m_star": m, "m10K": m10, "grid_cap": max(4, math.ceil(0.30 * sig60))}


def econ_doc(f3=None):
    f3 = f3 or f3_doc()
    pairs = {}
    for f in FIRMS_FX:
        for c in CODES_FX:
            if c in ("NQ", "SI", "SIL"):
                continue
            s60 = f3["roots"][c]["h"]["60"]["sigma"]
            pairs[f"{f}|{c}"] = {"primary": _block(c, f, s60), "E_dir60": _block(c, f, s60, 0.5),
                                 "spread1": _block(c, f, s60, 0.8 if c == "ZM" else 1.0), "E_dir": {}}
    return {"spec_sha256": SPEC_SHA256, "grid": {"step": 0.01}, "pairs": pairs}


def attention_doc():
    def u(codes, count, status=200):
        return {"codes": codes, "query_value": "SYNTHETIC", "url_logged": "SYNTHETIC", "status": status,
                "count": count, "phrase_only_count": None, "fetched_utc": None, "fetched_pdt": None, "retries": 0}
    return {"underlyings": {"Nasdaq-100": u(["MNQ", "NQ"], 300), "gold": u(["MGC", "GC"], 200),
                            "crude oil": u(["MCL", "QM", "CL"], 120), "silver": u(["SIL", "SI"], 120),
                            "Dow": u(["MYM", "YM"], 40), "soybean meal": u(["MZM", "ZM"], None, status=503)},
            "notes": ["SYNTHETIC"]}


def data_access_doc(f4=None):
    f4 = f4 or f4_doc()
    return {"codes": {c: dict(v["data_access"]) for c, v in f4["codes"].items()}, "ratios": {},
            "published_prices": [], "for_lead": []}


def rulings_doc():
    return {"rulings": [{"name": "RL-SYN-CL-spread2", "ruling": "SYNTHETIC ruling for the dry run",
                         "description": "CL sourced spread 2 ticks",
                         "params": {}, "patches": [{"file": "F4", "path": ["codes", "CL", "spread_S"],
                                                    "value": {"value": 2, "sourced": True, "item": "SYN-ruling"}}]}]}


def build() -> dict:
    f3, f4 = f3_doc(), f4_doc()
    return {"F3": f3, "F4": f4, "blind": blind_doc(), "econ": econ_doc(f3), "attention": attention_doc(),
            "data_access": data_access_doc(f4)}


def _member(code, c_f, sig, v, k, l_main=390, **kw):
    base = {"code": code, "c_f_ticks": c_f, "sigma_hc_ticks": sig, "tick_value_usd": v, "K_test": k,
            "L_main": l_main, "dll_usd": 1000, "mll_usd": 2000, "payout_threshold_usd": 150, "n_per_day": 1,
            "news_stop_events_per_week": 1, "initial_margin_usd": None, "sigma_day_ticks": None,
            "gate": {"news_window_covers_event_trade": False, "overnight_needed_but_prohibited": False,
                     "holds_past_flat_by_close": False}}
    return {**base, **kw}


def _combo(cid, venue, family, band, h_c, members, q1, q2, q3, data, product=None, pool=None):
    return {"id": cid, "product": product, "pool": pool, "venue": venue, "family": family, "band": band, "h_c": h_c,
            "members": members, "Q1": {"value": q1, "reason": "SYNTHETIC"}, "Q2": {"value": q2, "reason": "SYN"},
            "Q3": {"value": q3, "reason": "SYNTHETIC"}, "data": data}


def combos_doc():
    d0 = {"discovery_cost_usd": 0, "all_data_cost_usd": 120, "clean_test_window_months": 43, "windows": "SYN"}
    d1 = {"discovery_cost_usd": 80, "all_data_cost_usd": 260, "clean_test_window_months": 30, "windows": "SYN"}
    combos = [
        _combo("C01", "topstep", "eia_drift", ["30", "60", "120"], "60",
               [_member("MCL", 2.3, 44, 1, 400)], 3, 2, 3, d0, product="MCL"),
        _combo("C02", "ibkr", "eia_drift", ["30", "60", "120"], "60",
               [_member("MCL", 2.0, 44, 1, 400, initial_margin_usd=1200, sigma_day_ticks=200)], 3, 2, 3, d0,
               product="MCL"),
        _combo("C03", "bulenox", "eia_drift", ["60"], "60",
               [_member("MCL", 2.3, 44, 1, 400), _member("QM", 1.8, 17.6, 12.5, 400)], 3, 2, 3, d0,
               pool={"name": "POOL-energy-eia", "members": ["MCL", "QM"]}),
        _combo("C04", "topstep", "open_drive", ["5", "15", "30"], "15",
               [_member("MNQ", 2.2, 80, 0.5, 17400, n_per_day=20, news_stop_events_per_week=0)], 2, 3, 4, d1,
               product="MNQ"),
        _combo("C05", "lucid", "crush_spread", ["60", "120"], "60",
               [_member("ZM", 2.5, 5.8, 10, 870, l_main=290)], 3, 3, 0, d0, product="ZM"),
        _combo("C06", "mffu", "open_drive", ["15"], "15",
               [_member("MNQ", 2.2, 80, 0.5, 17400, gate={"news_window_covers_event_trade": True})], 2, 3, 4, d1,
               product="MNQ"),
        _combo("C07", "topstep", "close_imbalance", ["OC"], "OC",
               [_member("YM", 1.5, 140, 5, 870, dll_usd=1000)], 2, 1, 4, d0, product="YM"),
    ]
    return {"spec_sha256": SPEC_SHA256, "sr80_test": {"value": 0.137, "source": "SYNTHETIC"},
            "own_account_capital_ceiling_usd": {"value": None, "source": "none recorded in docs/DECISIONS.md"},
            "rho_measured": {"MCL|QM": {"value": 0.9, "source": "SYNTHETIC"}}, "combinations": combos}


FILES = {"F3": "F3_vol.json", "F4": "F4_facts_unmasked.json", "blind": "F4_blind_unmasked.json",
         "econ": "econ32b.json", "attention": "F2_attention.json", "data_access": "F2_data_access.json"}


def write_all(out_dir: str) -> dict:
    docs = build()
    paths = {}
    for name, fname in FILES.items():
        paths[name] = os.path.join(out_dir, fname)
        write_json(paths[name], docs[name])
    paths["rulings"] = os.path.join(out_dir, "rulings.json")
    write_json(paths["rulings"], rulings_doc())
    paths["combos"] = os.path.join(out_dir, "combinations.json")
    write_json(paths["combos"], combos_doc())
    return paths


if __name__ == "__main__":
    d = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixture")
    print(write_all(d))
