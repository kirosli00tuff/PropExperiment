"""E.32b F5: holding-time scope (spec section 7), facts only, no outcome.

    uv run python reports/stage_e32b_briefs/work/F5/f5_holding.py \
        [--f3 F3_vol.json] [--f4 F4_facts_unmasked.json] [--sr80 SR80.json] [--selection F5_selection.json] \
        [--out F5_holding.json] [--md F5_holding.md] [--venue-file F4_venue_ibkr.json]

Inputs and outputs: SCHEMA.md beside this file. Refuses to run unless the frozen spec's sha256 matches and every input
records that hash. The lead runs it on real facts after the ranking; this wave runs it only on synthetic fixtures.
--venue-file (optional, added 2026-10-29 by F5Runner) adds the own-broker rows "ibkr|<CODE>" for every selected code
under the lead's rulings LR-F5-IBKR and LR-Q6d (f5_venue.py); without it the output is unchanged.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import f5_core as core  # noqa: E402
import f5_venue as venue  # noqa: E402
from f5_core import InputError  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
BRIEFS = REPO / "reports" / "stage_e32b_briefs"
SPEC = REPO / "reports" / "stage_e32b_ranking_spec.md"
FROZEN_SPEC_SHA256 = "09ebe6970fcf027009152fa81a414360a015d535b095138cdf65cf1a4eb58635"
DEFAULTS = {"f3": BRIEFS / "F3_vol.json", "f4": BRIEFS / "F4_facts_unmasked.json", "sr80": HERE / "SR80.json",
            "selection": BRIEFS / "F5_selection.json", "out": BRIEFS / "F5_holding.json",
            "md": BRIEFS / "F5_holding.md"}
TOP_N = 15
EXCLUDED_CODES = {"NQ"}  # V49


class SpecHashError(RuntimeError):
    """The spec or an input does not carry the frozen hash."""


# ---------------------------------------------------------------- loading and validation

def sha256_of(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check_spec(path: Path = SPEC) -> str:
    if not Path(path).is_file():
        raise SpecHashError(f"spec not found: {path}; refusing to run")
    got = sha256_of(path)
    if got != FROZEN_SPEC_SHA256:
        raise SpecHashError(f"spec sha256 {got} != frozen {FROZEN_SPEC_SHA256}; refusing to run")
    return got


def check_doc_hash(doc: dict, name: str) -> None:
    got = doc.get("spec_sha256") if isinstance(doc, dict) else None
    if got != FROZEN_SPEC_SHA256:
        raise SpecHashError(f"{name}: spec_sha256 {got!r} != frozen {FROZEN_SPEC_SHA256}; refusing to run")


def value_of(x):
    """A fact may be a bare value or {"value": ..., <source fields>}; {"unknown": true} is unknown."""
    if isinstance(x, dict):
        if x.get("unknown") is True:
            return None
        return x.get("value")
    return x


def number(x, what: str, positive: bool = False):
    v = value_of(x)
    if v is None:
        return None
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise InputError(f"{what}: not a number: {v!r}")
    if positive and v <= 0:
        raise InputError(f"{what}: must be > 0, got {v}")
    if v < 0:
        raise InputError(f"{what}: must be >= 0, got {v}")
    return float(v)


def load_json(path: Path) -> dict:
    try:
        return json.loads(Path(path).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise InputError(f"cannot read {path}: {exc}") from exc


def check_sr80(doc: dict) -> dict:
    check_doc_hash(doc, "SR80.json")
    if (doc.get("cross_check") or {}).get("pass") is not True:
        raise InputError("SR80.json: cross_check.pass is not true")
    sr = doc.get("SR80") or {}
    out = {}
    for key in core.SR80_KEYS:
        out[key] = number(sr.get(key), f"SR80.{key}", positive=True)
        if out[key] is None:
            raise InputError(f"SR80.json: SR80.{key} missing")
    return out


def normalize_selection(doc: dict) -> dict:
    """The selection as {"spec_sha256", "layer1_survivors": [codes], "top15": [{"rank", "firm", "code"}]}.

    Accepts the minimal F5_selection.json (SCHEMA.md) or ScoreCoder's score output, whose primary.f5_handoff holds
    layer1_survivors as [{"code", ...}] and top15 as [{"rank", "firm", "code", ...}]."""
    check_doc_hash(doc, "selection")
    handoff = (doc.get("primary") or {}).get("f5_handoff") if isinstance(doc.get("primary"), dict) else None
    src = handoff if isinstance(handoff, dict) else doc
    survivors = src.get("layer1_survivors")
    if isinstance(survivors, list):
        survivors = [s.get("code") if isinstance(s, dict) else s for s in survivors]
    top = src.get("top15")
    if isinstance(top, list):
        top = [{"rank": e.get("rank"), "firm": e.get("firm"), "code": e.get("code")} if isinstance(e, dict) else e
               for e in top]
    return {"spec_sha256": doc.get("spec_sha256"), "layer1_survivors": survivors, "top15": top,
            "form": "score output primary.f5_handoff" if handoff is not None else "F5_selection.json"}


def check_selection(sel: dict, f3: dict, f4: dict) -> tuple[list[str], list[dict]]:
    check_doc_hash(sel, "selection")
    survivors = sel.get("layer1_survivors")
    top = sel.get("top15")
    if isinstance(top, list) and not all(isinstance(e, dict) for e in top):
        raise InputError("selection.top15: every entry must be an object with rank, firm and code")
    if not isinstance(survivors, list) or not survivors or len(set(survivors)) != len(survivors):
        raise InputError("selection.layer1_survivors: a non-empty list of distinct codes is required")
    if not isinstance(top, list) or len(top) > TOP_N:
        raise InputError(f"selection.top15: a list of at most {TOP_N} pairs is required")
    ranks = [e.get("rank") for e in top]
    if ranks != list(range(1, len(top) + 1)):
        raise InputError(f"selection.top15: ranks must be 1..{len(top)} in order, got {ranks}")
    for code in survivors:
        if code in EXCLUDED_CODES:
            raise InputError(f"selection: {code} is excluded (V49) and cannot be a survivor")
        if code not in (f3.get("roots") or {}) or code not in (f4.get("codes") or {}):
            raise InputError(f"selection: survivor {code} missing from F3 roots or F4 codes")
    seen = set()
    for e in top:
        key = f"{e.get('firm')}|{e.get('code')}"
        if key in seen:
            raise InputError(f"selection.top15: duplicate pair {key}")
        seen.add(key)
        if e.get("code") not in survivors:
            raise InputError(f"selection.top15: {key} is not a Layer 1 survivor")
        if key not in (f4.get("pairs") or {}) or e.get("firm") not in (f4.get("firms") or {}):
            raise InputError(f"selection.top15: {key} missing from F4 pairs or firms")
    return survivors, top


def check_tick(code: str, f3_root: dict, f4_code: dict) -> float:
    """Tick value v; F3's tick statistics and F4's tick value must refer to the same tick size."""
    t3 = number(f3_root.get("tick_size"), f"F3 {code} tick_size", positive=True)
    t4 = number(f4_code.get("tick_size"), f"F4 {code} tick_size", positive=True)
    if t3 is not None and t4 is not None and abs(t3 - t4) > 1e-9 * max(t3, t4):
        raise InputError(f"{code}: F3 tick_size {t3} != F4 tick_size {t4}")
    v = number(f4_code.get("tick_value_usd"), f"F4 {code} tick_value_usd", positive=True)
    if v is None:
        raise InputError(f"F4 {code}: tick_value_usd is required")
    return v


def spread(f4_code: dict) -> tuple[float, bool]:
    """(c_RT, S unknown): the sourced median spread, else S = 1 (u) (spec 1)."""
    sp = f4_code.get("spread_S")
    if isinstance(sp, dict):
        s = number(sp.get("value"), "spread_S") if sp.get("sourced") is True else None
    else:
        s = number(sp, "spread_S")
    return core.c_rt(s)


def main_session(f3_root: dict) -> tuple[int | None, int | None]:
    ms = f3_root.get("main_session_pt")
    if not ms:
        return None, None
    return core.hhmm_to_min(ms[0]), core.hhmm_to_min(ms[1])


def pause_relations(pauses, main_start: int | None, main_end: int | None) -> list[dict]:
    """Each pause as given, with its relation to the main session where it carries start_pt and end_pt."""
    out = []
    for p in pauses or []:
        rel = None
        if isinstance(p, dict) and p.get("start_pt") and p.get("end_pt") and main_start is not None:
            a, b = core.hhmm_to_min(p["start_pt"]), core.hhmm_to_min(p["end_pt"])
            if a < main_end and b > main_start:
                rel = "inside"
            elif b == main_start or a == main_end:
                rel = "adjacent"
            else:
                rel = "outside"
        out.append({"pause": p, "relation_to_main_session": rel})
    return out


# ---------------------------------------------------------------- blocks

def survivor_block(code: str, f3_root: dict, f4_code: dict, sr80: dict) -> dict:
    if f4_code.get("excluded") is True:
        raise InputError(f"{code}: excluded in F4 but listed as a survivor")
    if ((f3_root.get("h") or {}).get("60") or {}).get("sigma") is None:
        raise InputError(f"{code}: sigma_60 unknown, so it cannot be a Layer 1 survivor (spec 3 gate)")
    v = check_tick(code, f3_root, f4_code)
    crt, s_unknown = spread(f4_code)
    rows, overnight = core.horizon_rows(f3_root, crt, crt, sr80)
    ms, me = main_session(f3_root)
    gmin, argmin = core.g_minimum(rows, overnight)
    return {"code": code, "status": f3_root.get("status"), "oc1_source": f3_root.get("oc1_source"),
            "tick_size": f3_root.get("tick_size"), "tick_value_usd": v,
            "S": crt - core.SLIPPAGE_RT, "S_unknown": s_unknown, "c_RT": crt, "cost_basis": "c_RT",
            "L_main": f3_root.get("L_main"), "main_session_pt": f3_root.get("main_session_pt"),
            "main_session_pt_F4": f4_code.get("main_session_pt"),
            "pauses": pause_relations(f4_code.get("pauses"), ms, me),
            "rows": rows, "overnight_rows": overnight, "G_min": gmin, "G_argmin": argmin,
            "u": ["S: no sourced spread -> 1 tick (u)"] if s_unknown else []}


def firm_limits(firm: str, ff: dict) -> tuple[float | None, float | None, str, list[str]]:
    """(DLL_f, MLL_f, dll source, unknown notes). DLL_f = the MLL where the firm has no daily limit ("none")."""
    dll_raw = value_of(ff.get("dll_50k"))
    mll = number(ff.get("mll_50k"), f"F4 {firm} mll_50k", positive=True)
    u = []
    if isinstance(dll_raw, str) and dll_raw.strip().lower() == "none":
        dll, source = mll, "mll_50k (no daily limit)"
        if mll is None:
            u.append("DLL_f: no daily limit and MLL unknown (u)")
    else:
        dll, source = number(dll_raw, f"F4 {firm} dll_50k", positive=True), "dll_50k"
        if dll is None:
            u.append("DLL_f unknown (u)")
    if mll is None:
        u.append("MLL_f unknown (u)")
    return dll, mll, source, u


def overnight_allowed(ff: dict) -> bool | None:
    on = ff.get("overnight")
    allowed = value_of(on.get("allowed")) if isinstance(on, dict) else None
    return allowed if isinstance(allowed, bool) else None


def pair_block(entry: dict, f3_root: dict, f4: dict, sr80: dict) -> dict:
    firm, code = entry["firm"], entry["code"]
    key = f"{firm}|{code}"
    ff, pf, fc = f4["firms"][firm], f4["pairs"][key], f4["codes"][code]
    if pf.get("listed_50k") is not True:
        raise InputError(f"{key}: listed_50k is not true, so it cannot be a top-15 pair")
    v = check_tick(code, f3_root, fc)
    crt, s_unknown = spread(fc)
    fee = number(pf.get("fee_rt_usd"), f"F4 {key} fee_rt_usd")
    if fee is None:
        raise InputError(f"F4 {key}: fee_rt_usd is required (RR-05 fills Lucid's)")
    cf = core.c_firm(crt, fee, v)
    dll, mll, dll_source, u = firm_limits(firm, ff)
    flat = core.parse_flat_by_close(ff.get("flat_by_close"))
    ms, me = main_session(f3_root)
    allowed = overnight_allowed(ff)
    rows0, on0 = core.horizon_rows(f3_root, cf, crt, sr80)
    rows1, on1 = core.with_prop_columns(rows0, on0, dll, mll, v, ms, me, flat, allowed)
    gmin, argmin = core.g_minimum(rows1, on1)
    b, rows2 = core.band(rows1, gmin)
    if s_unknown:
        u.append("S: no sourced spread -> 1 tick (u)")
    if "(u)" in str(pf.get("fee_kind") or ""):
        u.append(f"fee: {pf.get('fee_kind')}")
    if flat.status == "unknown":
        u.append("flat-by-close unknown (u)")
    if allowed is None:
        u.append("overnight allowed: unknown (u)")
    return {"rank": entry["rank"], "firm": firm, "code": code, "tick_value_usd": v,
            "fee_rt_usd": fee, "fee_kind": pf.get("fee_kind"), "fee_ticks": fee / v,
            "S": crt - core.SLIPPAGE_RT, "S_unknown": s_unknown, "c_RT": crt, "c_f": cf, "cost_basis": "c_f",
            "DLL_f": dll, "dll_source": dll_source, "MLL_f": mll, "mll_type": value_of(ff.get("mll_type")),
            "flat_by_close": {"raw": flat.raw, "status": flat.status, "pt": core.min_to_hhmm(flat.pt_min)},
            "main_session_pt": f3_root.get("main_session_pt"),
            "flat_minus_main_end_min": (flat.pt_min - me) if flat.status == "time" and me is not None else None,
            "overnight": ff.get("overnight"), "overnight_allowed": allowed,
            "news_windows": ff.get("news_windows"), "news_window_items": pf.get("news_window_items"),
            "pauses": pause_relations(fc.get("pauses"), ms, me),
            "rows": rows2, "overnight_rows": on1, "G_min": gmin, "G_argmin": argmin,
            "band": {**b, **core.band_context(rows2)}, "verdict": core.verdict(b["members"], argmin), "u": u}


def own_broker_block(vdoc: dict, codes: list[str], roots: dict, f4: dict, sr80: dict) -> dict:
    """The own-broker venue (spec 8.2) rows "ibkr|<CODE>" for every selected code (LR-F5-IBKR, LR-Q6d).
    A code the venue file lacks, or whose per-side fee is not published, is listed under not_computed."""
    check_doc_hash(vdoc, "venue file")
    venue.check_limits(vdoc)
    vcodes = vdoc.get("codes")
    if not isinstance(vcodes, dict):
        raise InputError("venue file: 'codes' object missing")
    ceiling, ceiling_u = venue.capital_ceiling(vdoc)
    allowed = venue.overnight_allowed(vdoc)
    rows, not_computed = {}, {}
    for code in codes:
        entry = vcodes.get(code)
        if not isinstance(entry, dict):
            not_computed[code] = "code not in the venue file"
            continue
        fee = venue.venue_fee(code, entry)
        if fee is None:
            not_computed[code] = f"all-in fee per side not published (fee_status {entry.get('fee_status')!r})"
            continue
        fc = f4["codes"][code]
        v = check_tick(code, roots[code], fc)
        crt, s_unknown = spread(fc)
        ms, me = main_session(roots[code])
        rows[f"{venue.VENUE_KEY}|{code}"] = venue.venue_block(
            code, roots[code], v, crt, s_unknown, entry, fee, sr80, ms, me, ceiling, ceiling_u, allowed,
            vdoc.get("overnight_position_fee"))
    return {"venue": vdoc.get("venue"), "venue_key": venue.VENUE_KEY, "source": vdoc.get("source"),
            "fee_rule_file": vdoc.get("fee_rule"),
            "rulings": {"LR-F5-IBKR": "c_f = c_RT + F_rt / v, F_rt = 2 x all-in fee per side; " + venue.BAND_RULE
                        + "; intraday holds end by the main session's end; overnight rows report the overnight "
                          "margin",
                        "LR-Q6d": "per code: initial margin (intraday, overnight) vs the capital ceiling; sigma_day "
                                  "= sigma_cc x v vs 2% of the ceiling; sigma_OC x v beside (inputs only)"},
            "capital_ceiling_usd": ceiling, "capital_ceiling_u": ceiling_u, "overnight_allowed": allowed,
            "limits_note": vdoc.get("limits_note"), "rows": rows, "not_computed": not_computed}


# ---------------------------------------------------------------- assembly and output

def pdt_now() -> str:
    return subprocess.run(["date", "+%Y-%m-%d %H:%M:%S %Z"], capture_output=True, text=True,
                          env={"TZ": "America/Vancouver"}, check=True).stdout.strip()


def build(paths: dict, spec_path: Path = SPEC) -> dict:
    spec_sha = check_spec(spec_path)
    f3, f4, sr80_doc, sel_doc = (load_json(paths[k]) for k in ("f3", "f4", "sr80", "selection"))
    for doc, name in ((f3, "F3"), (f4, "F4")):
        check_doc_hash(doc, name)
    sel = normalize_selection(sel_doc)
    sr80 = check_sr80(sr80_doc)
    survivors, top = check_selection(sel, f3, f4)
    roots = f3["roots"]
    vpath = paths.get("venue")
    vdoc = load_json(vpath) if vpath is not None else None
    in_keys = ("f3", "f4", "sr80", "selection") + (("venue",) if vpath is not None else ())
    res = {
        "spec_sha256": spec_sha, "generated_pdt": pdt_now(),
        "generated_by": "reports/stage_e32b_briefs/work/F5/f5_holding.py",
        "inputs": {**{k: {"path": str(paths[k]), "sha256": sha256_of(paths[k])}
                      for k in in_keys}, "selection_form": sel["form"]},
        "SR80": sr80,
        "constants": {"slippage_rt_ticks": core.SLIPPAGE_RT, "S_unknown": core.S_UNKNOWN,
                      "entry_cap": core.ENTRY_CAP, "days_per_year": core.DAYS_PER_YEAR,
                      "normal_factor": core.NORMAL_FACTOR, "band_candidates": list(core.BAND_CANDIDATES),
                      "band_G_factor": core.BAND_G_FACTOR, "band_dll_min": core.BAND_DLL_MIN,
                      "rel_tol": core.REL_TOL},
        "survivors": {c: survivor_block(c, roots[c], f4["codes"][c], sr80) for c in survivors},
        "pairs": {f"{e['firm']}|{e['code']}": pair_block(e, roots[e["code"]], f4, sr80) for e in top},
    }
    if vdoc is not None:
        selected = list(dict.fromkeys(list(survivors) + [e["code"] for e in top]))
        res["own_broker"] = own_broker_block(vdoc, selected, roots, f4, sr80)
    return res


def fmt(x, nd: int = 3) -> str:
    if x is None:
        return "u"
    if isinstance(x, bool):
        return "yes" if x else "no"
    if isinstance(x, float):
        return f"{x:.{nd}f}"
    return str(x)


def render_md(res: dict) -> str:
    s = res["SR80"]
    out = ["# E.32b F5: holding-time scope (script output; facts only, no outcome)", "",
           f"Spec sha256 {res['spec_sha256']}; generated {res['generated_pdt']}; SR80 disc_G3 {s['disc_G3']:.4f}, "
           f"disc_G3G4 {s['disc_G3G4']:.4f}, test {s['test']:.4f}. Ticks unless stated; u = unknown.", "",
           "## Layer 1 survivors (firm-independent rows, cost basis c_RT)", ""]
    for code, b in res["survivors"].items():
        out += [f"### {code} (c_RT {fmt(b['c_RT'], 2)}{' u' if b['S_unknown'] else ''}, L_main {b['L_main']}, "
                f"min G_RT at {'/'.join(b['G_argmin']) or 'u'})", "",
                "| h | sigma | k_RT | p_be emp | n_cap | e80 test | G_RT |", "|---|---|---|---|---|---|---|"]
        for key, r in list(b["rows"].items()) + list(b["overnight_rows"].items()):
            out.append(f"| {key} | {fmt(r['sigma'], 2)} | {fmt(r['k_RT'], 4)} | {fmt(r['p_be_emp'], 3)} | "
                       f"{fmt(r['n_cap'])} | {fmt(r['e80_test'], 2)} | {fmt(r['G'], 4)} |")
        out.append("")
    out += ["## Top-15 pairs (firm rows, cost basis c_f)", ""]
    for key, p in res["pairs"].items():
        b, v = p["band"], p["verdict"]
        members = ", ".join(b["members"]) or "empty"
        out += [f"### {p['rank']}. {key}: B = {members}; prior {v['value']} ({v['reason']})", "",
                f"c_f {fmt(p['c_f'], 2)} (fee {fmt(p['fee_ticks'], 2)} ticks, {p['fee_kind']}); DLL_f "
                f"{fmt(p['DLL_f'], 0)} ({p['dll_source']}); MLL_f {fmt(p['MLL_f'], 0)}; flat-by-close "
                f"{p['flat_by_close']['pt'] or p['flat_by_close']['status']} PT; overnight allowed "
                f"{fmt(p['overnight_allowed'])}; power term exceeds cost from h = "
                f"{b['power_term_exceeds_cost_from'] or 'u'}; u: {'; '.join(p['u']) or 'none'}", "",
                "| h | sigma | k_f | G | G/minG | DLL/(sigma v) | MLL/(sigma v) | latest start PT | fits | in B |",
                "|---|---|---|---|---|---|---|---|---|---|"]
        for hk, r in list(p["rows"].items()) + list(p["overnight_rows"].items()):
            out.append(f"| {hk} | {fmt(r['sigma'], 2)} | {fmt(r['k'], 4)} | {fmt(r['G'], 4)} | "
                       f"{fmt(r.get('G_over_min'), 3)} | {fmt(r['dll_ratio'], 2)} | {fmt(r['mll_ratio'], 2)} | "
                       f"{fmt(r['latest_start_pt'])} | {fmt(r['fits_flat_by_close'])} | {fmt(r.get('in_band'))} |")
        if b["excluded"]:
            out.append("")
            out += [f"- excluded {hk}: {'; '.join(why)}" for hk, why in b["excluded"].items()]
        out.append("")
    if "own_broker" in res:
        out += render_own_broker_md(res["own_broker"])
    return "\n".join(out)


def render_own_broker_md(ob: dict) -> list[str]:
    out = [f"## Own-broker venue ({ob['venue_key']}: {ob['venue']}; rulings LR-F5-IBKR, LR-Q6d)", "",
           f"- LR-F5-IBKR: {ob['rulings']['LR-F5-IBKR']}.", f"- LR-Q6d: {ob['rulings']['LR-Q6d']}.",
           f"- Capital ceiling USD {ob['capital_ceiling_usd']:,.0f}{' (u)' if ob['capital_ceiling_u'] else ''}; "
           f"overnight allowed {fmt(ob['overnight_allowed'])}.",
           f"- Not computed: {'; '.join(f'{c}: {why}' for c, why in ob['not_computed'].items()) or 'none'}.", "",
           "| row | c_f | fee ticks | min G at | B | prior | IM intraday | IM overnight | sigma_day USD (cc) | "
           "sigma_OC USD | u |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for key, p in ob["rows"].items():
        q, b = p["Q6_inputs"], p["band"]
        flag = lambda x: " >" if x else ""  # noqa: E731
        out.append(f"| {key} | {fmt(p['c_f'], 2)} | {fmt(p['fee_ticks'], 2)} | {'/'.join(p['G_argmin']) or 'u'} | "
                   f"{', '.join(b['members']) or 'empty'} | {p['verdict']['value']} | "
                   f"{fmt(q['margin_intraday_initial_usd'], 0)}{flag(q['margin_intraday_exceeds_ceiling'])} | "
                   f"{fmt(q['margin_overnight_initial_usd'], 0)}{flag(q['margin_overnight_exceeds_ceiling'])} | "
                   f"{fmt(q['sigma_day_usd'], 0)}{flag(q['sigma_day_exceeds_limit'])} | {fmt(q['sigma_OC_usd'], 0)} | "
                   f"{'; '.join(p['u']) or 'none'} |")
    out += ["", "'>' marks a margin above the ceiling or a sigma_day above 2% of it.", ""]
    for key, p in ob["rows"].items():
        b = p["band"]
        out += [f"### {key}: B = {', '.join(b['members']) or 'empty'}; prior {p['verdict']['value']} "
                f"({p['verdict']['reason']})", "",
                "| h | sigma | k_f | G | G/minG | latest start PT | in B | overnight IM USD |",
                "|---|---|---|---|---|---|---|---|"]
        for hk, r in list(p["rows"].items()) + list(p["overnight_rows"].items()):
            out.append(f"| {hk} | {fmt(r['sigma'], 2)} | {fmt(r['k'], 4)} | {fmt(r['G'], 4)} | "
                       f"{fmt(r.get('G_over_min'), 3)} | {fmt(r['latest_start_pt'])} | {fmt(r.get('in_band'))} | "
                       f"{fmt(r.get('margin_overnight_initial_usd'), 0) if hk in core.OVERNIGHT_KEYS else ''} |")
        out.append("")
    return out


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    for k, default in DEFAULTS.items():
        parser.add_argument(f"--{k}", type=Path, default=default)
    parser.add_argument("--spec", type=Path, default=SPEC)
    parser.add_argument("--venue-file", type=Path, default=None,
                        help="own-broker venue facts (briefs/F4_venue_ibkr.json): adds rows ibkr|<CODE>")
    args = parser.parse_args(argv[1:])
    paths = {k: getattr(args, k) for k in DEFAULTS}
    if args.venue_file is not None:
        paths["venue"] = args.venue_file
    try:
        result = build(paths, args.spec)
    except (InputError, SpecHashError) as exc:
        print(f"F5 refused: {exc}", file=sys.stderr)
        return 2
    paths["out"].write_text(json.dumps(result, indent=1) + "\n")
    paths["md"].write_text(render_md(result))
    verdicts = [p["verdict"]["value"] for p in result["pairs"].values()]
    print(f"F5: {len(result['survivors'])} survivors, {len(result['pairs'])} pairs; verdicts "
          f"holds {verdicts.count('holds')}, partly {verdicts.count('partly')}, fails {verdicts.count('fails')}; "
          f"wrote {paths['out']} and {paths['md']}")
    if "own_broker" in result:
        ob = result["own_broker"]
        print(f"F5 own broker: {len(ob['rows'])} rows, not computed {sorted(ob['not_computed'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
