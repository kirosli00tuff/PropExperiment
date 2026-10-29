"""score32b.py: the Stage E.32b ranking (spec sections 3, 4 and 5) from the fact files.

Run (wave C, never before the real fact files exist):
    uv run python reports/stage_e32b_briefs/work/score/score32b.py \
        --f3 reports/stage_e32b_briefs/F3_vol.json --f4 reports/stage_e32b_briefs/F4_facts_unmasked.json \
        --blind reports/stage_e32b_briefs/F4_blind_unmasked.json --econ reports/stage_e32b_briefs/econ32b.json \
        --attention reports/stage_e32b_briefs/F2_attention.json \
        --data-access reports/stage_e32b_briefs/F2_data_access.json \
        [--rulings <lead rulings JSON>] --out <out.json> [--md <out.md>]
Refuses to run unless the spec's sha256 is the frozen one. Inputs and fields: SCHEMA.md in this folder.
"""
from __future__ import annotations

import argparse
import os
import sys
from dataclasses import asdict, fields, replace
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from s32b_common import (  # noqa: E402
    ALL_CODES,
    BASELINE,
    DECLARED_VARIANTS,
    E28_TABLE,
    FAMILY_OF,
    FIRM_SORT_NAME,
    FIRMS,
    INF,
    NQ,
    SPEC_PATH,
    InputError,
    Params,
    SpecHashError,
    apply_patches,
    check_doc_hash,
    check_spec,
    file_sha256,
    load_json,
    now_pdt,
    params_from,
    q,
    round2,
    write_json,
)
from s32b_layer1 import layer1_rows  # noqa: E402
from s32b_layer2 import W_L2, layer2_rows  # noqa: E402

TIE_LEVELS = ("S rounded", "m*", "L1", "cost per attempt", "contract code", "firm name")
W_L2_E28 = {"E": 0.40, "D": 0.10, "R": 0.10, "A": 0.15, "F": 0.10, "P": 0.05, "Rel": 0.10}   # E.28 spec line 106
ECON_BLOCKS = ("primary", "E_dir60", "spread1")
DA_KEYS = ("mbo_start", "k_usd_month", "o_owned_36m", "p_all_read")
TOP_N, VARIANT_TOP_N = 15, 5
MOVE_NAME_MIN = 0.0005   # a criterion is named as moving a pair if it changed S by at least this much


# ------------------------------------------------------------------------------------------------ validation
def _require_dict(doc, key, name):
    v = (doc or {}).get(key)
    if not isinstance(v, dict):
        raise InputError(f"{name}: '{key}' object missing")
    return v


def validate(docs: dict, allow_partial: bool = False) -> list:
    """Fatal contract breaks raise InputError or SpecHashError; soft cross-check findings are returned."""
    for name in ("F3", "F4", "econ", "data_access"):
        if docs.get(name) is not None:
            check_doc_hash(docs[name], name)
    f3 = _require_dict(docs["F3"], "roots", "F3_vol.json")
    codes = _require_dict(docs["F4"], "codes", "F4_facts_unmasked.json")
    firms = _require_dict(docs["F4"], "firms", "F4_facts_unmasked.json")
    pairs = _require_dict(docs["F4"], "pairs", "F4_facts_unmasked.json")
    _require_dict(docs["attention"], "underlyings", "F2_attention.json")
    econ = (docs.get("econ") or {}).get("pairs") or {}
    checks = []
    for c, cf in codes.items():
        if c not in FAMILY_OF:
            raise InputError(f"F4: code {c} is not one of the spec's 47 codes")
        if cf.get("family") not in (None, FAMILY_OF[c]):
            raise InputError(f"F4: {c} family {cf.get('family')} != spec family {FAMILY_OF[c]}")
        if (cf.get("excluded") is True) != (c == NQ):
            raise InputError(f"F4: excluded must be true for NQ only (V49); {c} has {cf.get('excluded')}")
        if c != NQ and c not in f3:
            raise InputError(f"F3: no root for {c}")
    missing = sorted(set(ALL_CODES) - set(codes))
    if missing and not allow_partial:
        raise InputError(f"F4: {len(missing)} spec codes missing: {missing}")
    if missing:
        checks.append(f"partial universe (allowed by flag): {len(missing)} spec codes absent")
    for key in pairs:
        parts = key.split("|")
        if len(parts) != 2 or parts[0] not in FIRMS or parts[1] not in codes or parts[0] not in firms:
            raise InputError(f"F4 pairs: bad key {key!r} (firm|CODE with a known firm and code)")
    need = []
    for key, pf in sorted(pairs.items()):
        code = key.split("|")[1]
        if code == NQ or pf.get("listed_50k") is not True:
            continue
        if (f3.get(code) or {}).get("status") not in ("owned", "OC1"):
            continue
        blocks = econ.get(key) or {}
        lack = [b for b in ECON_BLOCKS if not isinstance(blocks.get(b), dict)]
        if lack:
            need.append(f"{key} {lack}")
    if need:
        raise InputError(f"econ32b.json lacks blocks for {len(need)} rankable pairs: {'; '.join(need[:12])}")
    checks += _cross_checks(docs, f3, codes, econ)
    checks += unconfirmed_searches(econ)
    return checks


def _econ_search_blocks(blocks: dict):
    """(block name, block) for every econ block of a pair that carries a search record; nested horizon blocks
    (E_dir.<h>) included, the pair's `inputs` record excluded."""
    for name, blk in sorted((blocks or {}).items()):
        if not isinstance(blk, dict) or name == "inputs":
            continue
        if "search" in blk:
            yield name, blk
            continue
        for h, sub in sorted(blk.items()):
            if isinstance(sub, dict) and "search" in sub:
                yield f"{name}.{h}", sub


def unconfirmed_searches(econ: dict) -> list:
    """RV1 S3 (2026-10-29): one soft finding per econ threshold search whose grid confirmation records
    confirmed != true (pair, block, search name, recorded value, number of violations). The recorded value is then
    econ32b_core.confirm()'s k_final (the smallest grid point with f >= 0 after the dense fill), not the bisection."""
    out = []
    for key, blocks in sorted((econ or {}).items()):
        for name, blk in _econ_search_blocks(blocks):
            for sname, rec in sorted((blk.get("search") or {}).items()):
                if not isinstance(rec, dict) or rec.get("confirmed") is True:
                    continue
                out.append(f"econ {key} {name}: search {sname} confirmed {rec.get('confirmed')!r}, recorded value "
                           f"{blk.get(sname)!r} (k_bisection {rec.get('k_bisection')!r}), "
                           f"{len(rec.get('violations') or [])} violations of {rec.get('n_checked')!r} checked")
    return out


def _cross_checks(docs, f3, codes, econ) -> list:
    out = []
    for c, cf in sorted(codes.items()):
        t3, t4 = (f3.get(c) or {}).get("tick_size"), cf.get("tick_size")
        if t3 is not None and t4 is not None and q(t3) != q(t4):
            out.append(f"tick_size: F3 {c} {t3} != F4 {t4}")
        m, tv = cf.get("multiplier"), cf.get("tick_value_usd")
        if None not in (m, t4, tv) and q(m) * q(t4) != q(tv):
            out.append(f"F4 {c}: multiplier x tick_size = {float(q(m) * q(t4))} != tick_value_usd {tv}")
    for key, blocks in sorted(econ.items()):
        code = key.split("|")[-1]
        s60 = (((f3.get(code) or {}).get("h") or {}).get("60") or {}).get("sigma")
        e60 = ((blocks or {}).get("primary") or {}).get("sigma60")
        if s60 is not None and e60 is not None and abs(float(e60) - float(s60)) > 1e-6 * max(1.0, abs(float(s60))):
            out.append(f"econ {key}: sigma60 {e60} != F3 sigma_60 {s60}")
    da = (docs.get("data_access") or {}).get("codes") or {}
    for c, cf in sorted(codes.items()):
        a, b = cf.get("data_access") or {}, da.get(c)
        if b is None:
            continue
        for k in DA_KEYS:
            if k in b and a.get(k) != b.get(k):
                out.append(f"data access {c}.{k}: F4 {a.get(k)!r} != F2_data_access {b.get(k)!r}")
    return out


# ------------------------------------------------------------------------------------------------ ranking
def rank_key(row: dict) -> tuple:
    """Spec 5: S rounded half-up to 2 decimals (higher first); then lower m*; higher L1; lower cost per attempt;
    contract code; firm name (alphabetical)."""
    m = row["m_star"] if row["m_star"] is not None else INF
    cost = row["cost_per_attempt"] if row["cost_per_attempt"] is not None else INF
    return (-round2(row["S"]), m, -row["L1"], cost, row["code"], FIRM_SORT_NAME[row["firm"]])


def find_ties(ranked: list) -> list:
    """Groups of consecutive ranked pairs with equal rounded S, with the tie level that ordered each neighbour."""
    groups, cur = [], []
    for r in ranked:
        if cur and round2(r["S"]) != round2(cur[-1]["S"]):
            groups.append(cur)
            cur = []
        cur.append(r)
    if cur:
        groups.append(cur)
    out = []
    for g in groups:
        if len(g) < 2:
            continue
        steps = []
        for a, b in zip(g, g[1:], strict=False):
            ka, kb = rank_key(a), rank_key(b)
            lvl = next((i for i in range(len(ka)) if ka[i] != kb[i]), len(ka) - 1)
            steps.append({"higher": a["key"], "lower": b["key"], "decided_by": TIE_LEVELS[lvl]})
        out.append({"S_rounded": round2(g[0]["S"]), "ranks": [r["rank"] for r in g],
                    "pairs": [r["key"] for r in g], "steps": steps})
    return out


def brief_row(r: dict) -> dict:
    return {"rank": r["rank"], "firm": r["firm"], "code": r["code"], "S": r["S"], "S_rounded": r["S_rounded"],
            "L1": r["L1"], "L2": r["L2"]}


def run_variant(docs: dict, params: Params) -> dict:
    """Score every code and pair under one Params and rank the eligible pairs."""
    l1 = layer1_rows(docs, params)
    rows = layer2_rows(docs, params, l1)
    eligible = sorted((r for r in rows if r["status"] == "ranked"), key=rank_key)
    rank_of = {r["key"]: i for i, r in enumerate(eligible, 1)}
    rows = [{**r, "rank": rank_of.get(r["key"]),
             "S_rounded": None if r.get("S") is None else round2(r["S"])} for r in rows]
    ranked = sorted((r for r in rows if r["rank"] is not None), key=lambda r: r["rank"])
    rest = sorted((r for r in rows if r["rank"] is None), key=lambda r: (r["code"], FIRM_SORT_NAME[r["firm"]]))
    return {
        "params": params, "layer1": l1, "pairs": ranked + rest, "ties": find_ties(ranked),
        "top15": [brief_row(r) for r in ranked[:TOP_N]], "n_ranked": len(ranked),
        "layer1_survivors": sorted(c for c, r in l1.items() if r.get("gate_pass")),
        "L1_below_2": sorted(c for c, r in l1.items() if r.get("L1_below_2")),
        "MNQ_ranks": mnq_ranks(rows),
    }


def mnq_ranks(rows: list) -> dict:
    return {r["firm"]: (r["rank"] if r["rank"] is not None else r["status"]) for r in rows if r["code"] == BASELINE}


def params_diff(p: Params) -> dict:
    base = Params()
    return {f.name: getattr(p, f.name) for f in fields(Params) if getattr(p, f.name) != getattr(base, f.name)}


def variant_summary(res: dict, primary: dict) -> dict:
    top = [brief_row(r) for r in res["pairs"] if r["rank"] is not None][:VARIANT_TOP_N]
    ptop = [r["firm"] + "|" + r["code"] for r in primary["top15"][:VARIANT_TOP_N]]
    return {"params_changed": params_diff(res["params"]), "top5": top,
            "top5_same_as_primary": [r["firm"] + "|" + r["code"] for r in top] == ptop,
            "MNQ_ranks": res["MNQ_ranks"], "n_ranked": res["n_ranked"], "layer1_survivors": res["layer1_survivors"]}


# ------------------------------------------------------------------------------------------------ E.28 moves
def moves_vs_e28(res: dict, e28: dict | None, source: str) -> dict:
    """Rank in E.28's v2 order (A3_ranking_table.json, variant primary) against the rank here, with each
    criterion's contribution to the change in S; the criteria named are those that moved S by >= 0.0005."""
    if e28 is None:
        return {"available": False}
    old = {(r["firm"], r["code"]): r for r in e28["variants"]["primary"]["pairs"]}
    new = {(r["firm"], r["code"]): r for r in res["pairs"]}
    keys = {k for k, r in old.items() if r.get("rank") is not None} | {k for k, r in new.items() if r["rank"]}
    rows = []
    for k in keys:
        o, n = old.get(k), new.get(k)
        row = {"firm": k[0], "code": k[1], "rank_e28": o.get("rank") if o else None,
               "status_e28": _e28_status(o), "rank_here": n["rank"] if n else None,
               "status_here": n["status"] if n else "not in F4 pairs"}
        if row["rank_e28"] is not None and row["rank_here"] is not None:
            row["rank_change"] = row["rank_e28"] - row["rank_here"]   # positive = moved up
        needed = ("S", "L1", "E", "D", "R", "A", "F", "P", "Rel")
        if o and n and n.get("S") is not None and all(o.get(c) is not None for c in needed):
            contrib = {"L1": (float(n["L1"]) - o["L1"]) / 2}
            for c in ("E", "D", "R", "A", "P", "Rel"):
                contrib[c] = (float(W_L2[c]) * float(n[c]) - W_L2_E28[c] * float(o[c])) / 2
            contrib["F (dropped)"] = -W_L2_E28["F"] * float(o["F"]) / 2
            row["S_e28"], row["S_here"] = o["S"], float(n["S"])
            row["contrib"] = contrib
            row["moved_by"] = [c for c, v in sorted(contrib.items(), key=lambda kv: -abs(kv[1]))
                               if abs(v) >= MOVE_NAME_MIN]
        rows.append(row)
    rows.sort(key=lambda r: (r["rank_here"] is None, r["rank_here"] or 0, r["rank_e28"] or 10**6, r["code"]))
    return {"available": True, "source": source, "e28_variant": "primary (v2 rulings)",
            "note": "E.28 Layer 1 used C1..C6, so Layer 1 moves are shown as one L1 contribution", "rows": rows}


def _e28_status(o: dict | None) -> str:
    if o is None:
        return "not an E.28 pair"
    if o.get("rank") is not None:
        return "ranked"
    if not o.get("L1_gate_pass", True):
        return "not ranked: Layer 1 gate"
    return "not ranked: " + ("; ".join(o.get("L2_gate_reasons") or []) or "excluded")


# ------------------------------------------------------------------------------------------------ run
def collect_lead_notes(res: dict) -> list:
    """Cases the spec does not settle, one entry per note text with every code or pair it applies to."""
    by_note: dict = {}
    for c, r in sorted(res["layer1"].items()):
        for n in r.get("lead", []):
            by_note.setdefault(n, []).append(c)
    for r in res["pairs"]:
        for n in r.get("lead", []):
            by_note.setdefault(n, []).append(r["key"])
    return [{"note": n, "where": sorted(set(w))} for n, w in by_note.items()]


def run_all(docs: dict, rulings: dict | None = None, e28: dict | None = None, allow_partial: bool = False,
            spec_path=SPEC_PATH, input_meta: dict | None = None, e28_source: str = str(E28_TABLE)) -> dict:
    spec = check_spec(spec_path)
    checks = validate(docs, allow_partial)
    primary = run_variant(docs, Params())
    variants = {}
    for name, overrides in DECLARED_VARIANTS.items():
        variants[name] = {"kind": "declared", **variant_summary(run_variant(docs, replace(Params(), **overrides)),
                                                                primary)}
    for rv in (rulings or {}).get("rulings", []):
        name = rv.get("name")
        if not name or name in variants or name == "primary":
            raise InputError(f"ruling variant name {name!r} missing or clashing with a declared variant")
        patched = apply_patches(docs, rv.get("patches", []))
        validate(patched, allow_partial)
        base_unc = set(unconfirmed_searches((docs.get("econ") or {}).get("pairs")))
        checks += [f"ruling {name} (patched econ): {c}" for c in
                   unconfirmed_searches((patched.get("econ") or {}).get("pairs")) if c not in base_unc]
        res = run_variant(patched, params_from(rv.get("params", {})))
        variants[name] = {"kind": "lead ruling", "ruling": rv.get("ruling"), "description": rv.get("description"),
                          "patches": rv.get("patches", []), **variant_summary(res, primary)}
    return {
        "spec_sha256": spec, "generated_pdt": now_pdt(), "script": "score32b.py", "inputs": input_meta or {},
        "input_checks": checks, "for_lead": collect_lead_notes(primary),
        "primary": {**{k: v for k, v in primary.items() if k != "params"}, "params": asdict(Params()),
                    "f5_handoff": {"layer1_survivors": [{"code": c, "family": FAMILY_OF[c],
                                                         "f3_status": primary["layer1"][c]["f3_status"]}
                                                        for c in primary["layer1_survivors"]],
                                   "top15": primary["top15"]}},
        "moves_vs_e28": moves_vs_e28(primary, e28, e28_source),
        "variants": variants,
    }


# ------------------------------------------------------------------------------------------------ markdown
def _f(x, nd=3):
    if x is None:
        return "-"
    if isinstance(x, (F, float, int)) and not isinstance(x, bool):
        return "inf" if x == INF else f"{float(x):.{nd}f}"
    return str(x)


def write_md(out: dict, path) -> None:
    p = out["primary"]
    lines = [f"# score32b output ({out['generated_pdt']})", "", f"spec sha256 {out['spec_sha256']}", "",
             "## Layer 1", "", "| code | status | D1 | D2 | D3 | D4 | D5 | D6 | L1 | gate | arithmetic |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for c, r in sorted(p["layer1"].items()):
        if r["status"] != "scored":
            lines.append(f"| {c} | {r['status']} |  |  |  |  |  |  |  | not ranked |  |")
            continue
        gate = "pass" if r["gate_pass"] else "FAIL: " + "; ".join(r["gate_reasons"])
        lines.append(f"| {c} | {r['f3_status']} | " + " | ".join(_f(r[k], 2) for k in
                     ("D1", "D2", "D3", "D4", "D5", "D6", "L1")) + f" | {gate} | {r['gate_arithmetic']} |")
    lines += ["", "## Pairs", "",
              "| rank | firm | code | S | S 2dp | L1 | L2 | E | R | A | D | Rel | P | m* | status |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in p["pairs"]:
        lines.append("| " + " | ".join([_f(r["rank"], 0) if r["rank"] else "-", r["firm"], r["code"]]
                     + [_f(r.get(k), 3) for k in ("S", "S_rounded", "L1", "L2", "E", "R", "A", "D", "Rel", "P",
                                                  "m_star")]
                     + [r["status"] + ("" if not r.get("gate_reasons") else ": " + "; ".join(r["gate_reasons"]))])
                     + " |")
    lines += ["", "## Ties", ""] + [f"- S {_f(t['S_rounded'], 2)}: {t['pairs']} {t['steps']}" for t in p["ties"]]
    lines += ["", "## Variants (top 5, MNQ ranks)", ""]
    for name, v in out["variants"].items():
        top = ", ".join(f"{t['rank']} {t['firm']} {t['code']} {_f(t['S'], 3)}" for t in v["top5"])
        lines.append(f"- {name} ({v['kind']}): {top}; MNQ {v['MNQ_ranks']}; same top 5: {v['top5_same_as_primary']}")
    mv = out["moves_vs_e28"]
    if mv.get("available"):
        lines += ["", "## Moves against E.28 v2", "", "| firm | code | E.28 rank | rank here | moved by |",
                  "|---|---|---|---|---|"]
        lines += [f"| {r['firm']} | {r['code']} | {r['rank_e28'] or r['status_e28']} | "
                  f"{r['rank_here'] or r['status_here']} | {', '.join(r.get('moved_by', []))} |" for r in mv["rows"]]
    lines += ["", "## For the lead", ""] + [f"- {n['note']} [{', '.join(n['where'])}]" for n in out["for_lead"]]
    lines += ["", "## Input checks", ""] + [f"- {c}" for c in out["input_checks"]]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


# ------------------------------------------------------------------------------------------------ CLI
def load_docs(args) -> tuple[dict, dict]:
    paths = {"F3": args.f3, "F4": args.f4, "blind": args.blind, "econ": args.econ, "attention": args.attention,
             "data_access": args.data_access}
    docs, meta = {}, {}
    for name, path in paths.items():
        if path is None:
            docs[name] = None
            continue
        docs[name] = load_json(path)
        meta[name] = {"path": path, "sha256": file_sha256(path)}
    return docs, meta


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for name in ("f3", "f4", "blind", "econ", "attention"):
        ap.add_argument(f"--{name}", required=True)
    ap.add_argument("--data-access", default=None)
    ap.add_argument("--rulings", default=None, help="lead-ruling variants JSON (SCHEMA.md)")
    ap.add_argument("--e28", default=str(E28_TABLE), help="E.28 A3_ranking_table.json (read-only)")
    ap.add_argument("--no-e28", action="store_true")
    ap.add_argument("--out", required=True)
    ap.add_argument("--md", default=None)
    ap.add_argument("--allow-partial-universe", action="store_true", help="synthetic fixtures only")
    ap.add_argument("--spec", default=str(SPEC_PATH))
    args = ap.parse_args(argv)
    try:
        check_spec(args.spec)
        docs, meta = load_docs(args)
        rulings = load_json(args.rulings) if args.rulings else None
        if args.rulings:
            meta["rulings"] = {"path": args.rulings, "sha256": file_sha256(args.rulings)}
        e28 = None if args.no_e28 else load_json(args.e28)
        out = run_all(docs, rulings, e28, args.allow_partial_universe, args.spec, meta, args.e28)
    except (SpecHashError, InputError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    write_json(args.out, out)
    if args.md:
        write_md(out, args.md)
    p = out["primary"]
    print(f"survivors {len(p['layer1_survivors'])}, ranked pairs {p['n_ranked']}, "
          f"top 5: {[t['firm'] + ' ' + t['code'] for t in p['top15'][:5]]}; MNQ {p['MNQ_ranks']}; "
          f"lead notes {len(out['for_lead'])}; input checks {len(out['input_checks'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
