"""FactTable outputs 4 and 5: briefs/F4_masked_contracts.json, briefs/F4_masked_firms.json (the BlindScorer's only
inputs) and briefs/F4_mask_key.json. Labels come from the secrets module (fresh each run). Facts only: masking,
relation words and mechanical keyword flags; no rating. Run after build_f4.py (reads F4_facts_unmasked.json)."""
from __future__ import annotations

import json
import re
import secrets
import string
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import f4_rulings as R  # noqa: E402
import mask_vocab as V  # noqa: E402
from build_f4 import B, E28, FAMILY_OF, FIRMS, Items, load, now_pdt  # noqa: E402

LETTERS = string.ascii_uppercase
WB0, WB1 = r"(?<![A-Za-z0-9])", r"(?![A-Za-z0-9])"
CODES = list(FAMILY_OF)
REL = {"this": "this contract", "sib": "a same-underlying sibling", "group": "the product group",
       "cousin": "a close cousin (same asset class on CME Globex)",
       "broad": "the asset class broadly or a multi-asset study",
       "venue": "another venue of the same underlying"}
SECTIONS = {"T2a": "D2a_automated_share", "T2b": "D2b_programs", "T3": "D3_s1_relationships",
            "T4": "D3_s2_scheduled_releases", "T7": "D3_s3_session_structure", "T5": "Sat_iii_price_discovery",
            "T6": "D6_directional_evidence"}
SPOT_WORDS = re.compile(r"\b(spot|cash (index|market|treasur|close)|ETF|EBS|BrokerTec|GovPX|London OTC|"
                        r"exchanges|Coinbase|Bitstamp|Binance|Deribit|interdealer|SIRCA|\.SPX|S&P 500 cash|LBMA|LME|"
                        r"SHFE|Shanghai)\b", re.I)
COUSIN_WORDS = re.compile(r"\b(cousin|E-mini S&P|ES\b|S&P 500 futures|Ultra Bond)", re.I)


# ---------------------------------------------------------------- labels
def fresh_labels(prefix: str, n: int, banned: set[str]) -> list[str]:
    out: set[str] = set()
    bad_sub = [c for c in CODES + V.OTHER_CODES if c.isalpha() and len(c) >= 2]
    while len(out) < n:
        s = "".join(secrets.choice(LETTERS) for _ in range(4))
        lab = f"{prefix}-{s}"
        if lab in banned or lab in out or any(b in s for b in bad_sub):
            continue
        out.add(lab)
    lst = list(out)
    secrets.SystemRandom().shuffle(lst)
    return lst


class Ids:
    def __init__(self) -> None:
        self.used: set[str] = set()
        self.key: dict[str, dict] = {}

    def new(self, src: str, code_or_firm: str) -> str:
        while True:
            s = "I-" + "".join(secrets.choice(string.digits) for _ in range(7))
            if s not in self.used:
                self.used.add(s)
                self.key[s] = {"source_item": src, "for": code_or_firm}
                return s


# ---------------------------------------------------------------- text masking
class Masker:
    def __init__(self, clab: dict[str, str], flab: dict[str, str], plab: dict[str, str]) -> None:
        self.clab, self.flab, self.plab = clab, flab, plab
        names = sorted(V.PRODUCT_NAMES, key=len, reverse=True)
        self.name_re = [(re.compile(WB0 + re.escape(n) + WB1, re.I), V.PRODUCT_NAMES[n]) for n in names]
        self.code_re = re.compile(r"(?<![A-Za-z0-9_])(" + "|".join(sorted(map(re.escape, CODES), key=len,
                                                                          reverse=True))
                                  + r")(?:[FGHJKMNQUVXZ]\d{1,2})?(?![A-Za-z0-9_])")
        alt = sorted(V.ALT_TICKERS, key=len, reverse=True)
        self.alt_re = re.compile(r"(?<![A-Za-z0-9_/])(" + "|".join(alt) + r")(?![A-Za-z0-9_])")
        oth = sorted(set(V.OTHER_CODES) - set(CODES) - set(V.ALT_TICKERS), key=len, reverse=True)
        self.oth_re = re.compile(r"(?<![A-Za-z0-9_])(" + "|".join(map(re.escape, oth))
                                 + r")(?:[FGHJKMNQUVXZ]\d{1,2})?(?![A-Za-z0-9_])")
        self.firm_re = [(re.compile(WB0 + re.escape(n) + WB1, re.I), f) for f in V.FIRM_NAMES for n in
                        sorted(V.FIRM_NAMES[f], key=len, reverse=True)]
        self.firm_re.sort(key=lambda x: -len(x[0].pattern))
        self.plat_re = [(re.compile(WB0 + re.escape(p) + WB1, re.I), p) for p in sorted(V.PLATFORMS, key=len, reverse=True)]
        self.ref_res = [
            re.compile(r"https?://\S+"), re.compile(r"\bwww\.\S+"),
            re.compile(r"\b[\w.-]+\.(?:com|org|net|gov|edu|io|ca|co\.uk|eu|nl|au)\b(?:/\S*)?", re.I),
            re.compile(r"(?:reports|pages|work|docs)/[\w./\-]+"),
            re.compile(r"\b[\w\-]+\.(?:json|md|txt|html|pdf|py|tsv|tbl|js|csv)\b", re.I),
            re.compile(r"\b(?:CRUDE|NATGAS|METALS|GRAINS|RATES|EQUITY|FX|CRYPTO|CFTC|SB|R1|R2|FL|LR|OC|RR|S)"
                       r"-(?:[A-Z]\d+-)?\d+[a-z]?\b"),
            re.compile(r"\b[CFPX]\d{2}\b"),
        ]

    def text(self, s, firm_ctx: str | None = None, crypto: bool = False, size: bool = False) -> str | None:
        if s is None:
            return None
        if not isinstance(s, str):
            s = json.dumps(s, ensure_ascii=False)
        for pat, rep in V.LITIGATION:
            s = re.sub(pat, rep, s)
        for r in self.ref_res:
            s = r.sub("[ref]", s)
        s = re.sub(r"\b(?:ETHUSD_?RR|ETHUSDRRR|ETHEURRR|BTCUSD_?RR|BRRNY|BRR)\b", "[reference rate]", s)
        s = re.sub(r"https?", "web", s, flags=re.I)
        if not crypto:
            s = re.sub(r"(?<![A-Za-z])ETH(?![A-Za-z])", "extended-hours", s)
        if firm_ctx:
            for f in V.PLAN_NAMES:
                for name, lab in sorted(V.PLAN_NAMES[f], key=lambda x: -len(x[0])):
                    rep = lab if f == firm_ctx else "[another firm's plan]"
                    s = re.sub(r"(?<![A-Za-z])" + re.escape(name) + r"(?![A-Za-z])", rep, s)
        for r, f in self.firm_re:
            s = r.sub(self.flab[f], s)
        for r, p in self.plat_re:
            s = r.sub(f"platform {self.plab[p]}", s)
        for r, c in self.name_re:
            s = r.sub(self.clab[c], s)
        s = self.code_re.sub(lambda m: self.clab[m.group(1)], s)
        s = self.alt_re.sub(lambda m: self.clab[V.ALT_TICKERS[m.group(1)]], s)
        s = self.oth_re.sub("[other product]", s)
        if size:  # contract sheets: contract-size class words that hint at a code
            s = re.sub(r"(?<![A-Za-z])(?:Micro E-mini|E-micros?|E Micros|Micros?|micros?|E-minis?|e-minis?|"
                       r"Mini-sized|mini-sized|Mini|minis?|E-nano|nano|full-size|full size|Full Size|"
                       r"Full-size|standard-size)(?![A-Za-z])", "[size class]", s)
        return s


# ---------------------------------------------------------------- relations
# The micro yields are not price-transfer siblings of the Treasury futures (spec 2.4) but share their economic
# underlying (spec 0 calls them siblings "not for price transfer"); for the relation words they group with them.
ECON_UND = {"2YY": "ZT", "5YY": "ZF", "10Y": "ZN", "30Y": "ZB"}
# Per-item relation overrides (reader text read by the FactTable): Krohn et al. report a CME futures dollar
# portfolio across currencies, not a single-contract result.
REL_OVERRIDE = {"FX-38": "broad"}
FUTURES_WORDS = re.compile(r"futures|\bCME\b|Globex|Tick Data symbol", re.I)


def underlying_of(codes4: dict) -> dict[str, str]:
    return {c: codes4[c]["underlying"] for c in CODES}


def subjects(item: dict, und: dict, leader: dict) -> set[str]:
    cs = [c for c in item.get("codes") or [] if c in und]
    groups: dict[str, list[str]] = {}
    for c in cs:
        groups.setdefault(ECON_UND.get(c, und[c]), []).append(c)
    subj = set()

    def names(text: str, members: list[str]) -> list[str]:
        return [c for c in members if re.search(r"(?<![A-Za-z0-9])" + re.escape(c) + r"(?![A-Za-z0-9])", text)]

    for g, members in groups.items():
        named_v = names(str(item.get("value")), members)
        named = names(f"{item.get('value')} {item.get('detail')} {item.get('window')}", members)
        leaders = [c for c in members if leader.get(c) == c and c not in ECON_UND]
        if len(members) == 1:
            subj.add(members[0])
        elif len(named_v) == 1:
            subj.add(named_v[0])
        elif len(named) == 1:
            subj.add(named[0])
        elif leaders:
            subj.update(leaders)
        else:
            subj.update(members)
    return subj


def relation(item: dict, code: str, und: dict, leader: dict) -> str:
    sc = item.get("scope")
    txt = f"{item.get('value')} {item.get('detail')} {item.get('window')}"
    if code not in (item.get("codes") or []):
        return REL["broad"]
    if sc == "product_group":
        return REL["group"]
    if sc in ("asset_class", "futures_broad"):
        return REL["broad"]
    if sc == "other_venue":
        return REL["venue"]
    if sc == "sibling":
        return REL["sib"]
    if sc == "other":
        return REL["cousin"] if COUSIN_WORDS.search(txt) else REL["broad"]
    if item.get("id") in REL_OVERRIDE:
        return REL[REL_OVERRIDE[item["id"]]]
    if sc == "underlying" and SPOT_WORDS.search(txt):
        return REL["venue"]
    if sc == "underlying" and FAMILY_OF.get(code) == "crypto" and not FUTURES_WORDS.search(txt):
        return REL["venue"]  # crypto studies that name no futures market are spot-exchange studies
    return REL["this"] if code in subjects(item, und, leader) else REL["sib"]


# ---------------------------------------------------------------- D6 keyword flags
YEAR = re.compile(r"(?<!\d)(19[5-9]\d|20[0-3]\d)(?!\d)")


def d6_flags(item: dict) -> dict:
    w = str(item.get("window") or "")
    d = f"{item.get('value')} {item.get('detail')}"
    yrs = [int(y) for y in YEAR.findall(w)] or [int(y) for y in YEAR.findall(d)][:2]
    if not yrs:
        after = None
    elif min(yrs) >= 2010:
        after = True
    elif max(yrs) > 2010:
        after = "partly (data period spans 2010)"
    else:
        after = False
    low = d.lower()
    oos = (True if re.search(r"out[- ]of[- ]sample|\boos\b|r2_oos|recursive", low) else
           False if re.search(r"in[- ]sample", low) else None)
    net = (False if re.search(r"\bgross\b|not net|before costs|no costs|costs not", low) else
           True if re.search(r"net of (?:costs|spread|half|transaction)|after (?:bid-ask |transaction )?costs|"
                             r"after spreads|net of", low) else None)
    hm = re.search(r"horizons?[: ]+([^;.]{1,80})", d, re.I) or re.search(
        r"(\d+(?:\.\d+)?[- ]?(?:min|minute|hour|h\b)[^;.,]{0,30})", d, re.I)
    return {"after_2010": after, "out_of_sample": oos, "net_of_costs": net,
            "horizon": hm.group(1).strip() if hm else None,
            "flags_note": "keyword flags derived mechanically from the reader's window and detail; the detail text "
                          "is authoritative"}


def verified_level(item: dict) -> str:
    v = item.get("verified")
    d = str(item.get("detail") or "").lower()
    if v == "full_text":
        return "full text"
    if v == "abstract":
        return "abstract [unverified]"
    if v == "snippet":
        return "snippet [unverified]"
    if "abstract only" in d or "abstract read" in d or "(abstract" in d:
        return "abstract [unverified] (reused from an earlier stage)"
    if "snippet" in d:
        return "snippet [unverified] (reused from an earlier stage)"
    return "reused from an earlier stage's full-text fact (level as stated in the text)"


# ---------------------------------------------------------------- sheets
def contract_sheets(items: Items, f4: dict, M: Masker, ids: Ids, clab: dict) -> tuple[dict, dict]:
    und = underlying_of(f4["codes"])
    leader = {c: f4["codes"][c]["leader"] for c in CODES}
    out, rel_log = {}, {}
    for code in CODES:
        sheet = {"label": clab[code]}
        for sec in SECTIONS.values():
            sheet[sec] = []
        for iid, it in items.by_id.items():
            top = it.get("topic")
            if top not in SECTIONS:
                continue
            named = code in (it.get("codes") or [])
            iip = iid == "RATES-11" and code in R.IIP_CODES
            if not (named or iip):
                continue
            if top == "T5" and it.get("field") in ("settlement_basis", "settlement", "settlement_method"):
                continue
            if top == "T5" and "settle" in str(it.get("field")):
                continue
            crypto = FAMILY_OF.get(code) == "crypto" or iid.startswith("CRYPTO")
            rel = relation(it, code, und, leader) if named else REL["group"]
            mid = ids.new(iid, code)
            mt = lambda x: M.text(x, crypto=crypto, size=True)  # noqa: E731
            rec = {"id": mid, "applies_to": rel, "field": it.get("field"),
                   "value": mt(it.get("value")), "window": mt(it.get("window")),
                   "detail": mt(it.get("detail")), "quote": mt(it.get("quote")),
                   "verified": verified_level(it), "pointer_only": bool(it.get("pointer")),
                   "negative_finding": bool(it.get("negative"))}
            if iip:
                rec["detail"] = (rec["detail"] or "") + " | This contract falls under the fee-table line '" + \
                    mt(R.IIP_CODES[code]) + "'."
            if top == "T6":
                rec.update(d6_flags(it))
                rec["horizon"] = mt(rec["horizon"])
            sheet[SECTIONS[top]].append(rec)
            rel_log.setdefault(code, []).append({"masked": mid, "source": iid, "applies_to": rel,
                                                 "scope": it.get("scope")})
        for sec in SECTIONS.values():
            if not sheet[sec]:
                sheet[sec + "_note"] = "no sourced item recorded by the readers for this section"
        out[clab[code]] = sheet
    return out, rel_log


def firm_items(firm: str, e28: dict, f2: dict) -> list[tuple[str, str, dict]]:
    """(section, source ref, record) for A, Rel and R facts of one firm."""
    recs = []
    for sec in ("A", "Rel", "R"):
        for k, v in (e28["firms"][firm].get(sec) or {}).items():
            recs.append((sec, f"E28:A3_firm_products.firms.{firm}.{sec}.{k}",
                         {"what": k, "value": v.get("value") if isinstance(v, dict) else v,
                          "quote": v.get("quote") if isinstance(v, dict) else None,
                          "note": v.get("note") if isinstance(v, dict) else None,
                          "date": "as of E.28 lookup 2026-10-21 (FirmRules 2026-10-28: unchanged unless a "
                                  "later item says so)"}))
    t = f2["firms"][firm]
    sec_of = {"automation": "A", "news_windows": "R", "news_other_rules": "R", "flat_by_close": "R",
              "session_cutoffs": "R", "overnight": "R", "product_caps_50k": "R", "plan": "plan",
              "rel_founded": "Rel", "rel_payout_disputes_12m": "Rel", "rel_rule_changes_12m": "Rel",
              "rel_regulatory": "Rel", "payout_qualification": "Rel_context"}
    for k, sec in sec_of.items():
        if k not in t:
            continue
        v = t[k]
        src = v.get("source") or {}
        recs.append((sec, f"F2_firms.json:firms.{firm}.{k}",
                     {"what": k, "value": v.get("value"), "old_value_e28": v.get("old_value"),
                      "changed_since_e28": v.get("changed"), "quote": v.get("quote"), "note": v.get("note"),
                      "date": ("fetched " + str(src.get("fetched_utc")) + " UTC") if src.get("fetched_utc")
                      else "reused from E.28 (lookup 2026-10-21)"}))
    return recs


def binds(rec: dict) -> str:
    s = f"{rec.get('what')} {rec.get('value')} {rec.get('quote')}".lower()
    ev = any(w in s for w in ("combine", "evaluation", "eval", "qualification"))
    fu = any(w in s for w in ("xfa", "funded", "master", "lfa", "live"))
    if ev and fu:
        return "evaluation and funded stages (as the text states)"
    if ev:
        return "evaluation stage (as the text states)"
    if fu:
        return "funded stage(s) (as the text states)"
    return "plan-wide: no stage distinction stated (applies to the modelled plan's evaluation and funded stages)"


def firm_sheets(f4: dict, M: Masker, ids: Ids, flab: dict, clab: dict) -> dict:
    e28 = load(E28 / "A3_firm_products.json")
    f2 = load(B / "F2_firms.json")
    out = {}
    for firm in FIRMS:
        lab = flab[firm]
        sheet = {"label": lab, "modelled_plan": V.MODELLED_PLAN[firm],
                 "lookup_date": {"F2_refetch": "2026-10-28 (FirmRules, PDT; page fetch times per item)",
                                 "E28": "2026-10-21", "firm_note": M.text(
                                     (f2.get("change_summary") or {}).get(firm), firm_ctx=firm)},
                 "A_facts": [], "Rel_facts": [], "R_facts_firm_wide": [], "plan_facts": [], "payout_context": []}
        for sec, ref, rec in firm_items(firm, e28, f2):
            mid = ids.new(ref, firm)
            what = re.sub(r"combine", "evaluation", rec["what"], flags=re.I)
            what = re.sub(r"\bxfa|_xfa|xfa_", lambda m_: m_.group(0).lower().replace("xfa", "funded"), what,
                          flags=re.I)
            what = re.sub(r"lfa", "live", what, flags=re.I)
            what = re.sub(r"_pro\b", "_plan", what)
            m = {"id": mid, "what": M.text(what, firm_ctx=firm),
                 "value": M.text(rec.get("value"), firm_ctx=firm), "quote": M.text(rec.get("quote"), firm_ctx=firm),
                 "note": M.text(rec.get("note"), firm_ctx=firm), "date": rec["date"],
                 "verified": "full text (firm page)"}
            if "old_value_e28" in rec:
                m["old_value_e28"] = M.text(rec.get("old_value_e28"), firm_ctx=firm)
                m["changed_since_e28"] = rec.get("changed_since_e28")
            if sec in ("A", "R"):
                m["binds"] = binds(rec)
            dest = {"A": "A_facts", "Rel": "Rel_facts", "R": "R_facts_firm_wide", "plan": "plan_facts",
                    "Rel_context": "payout_context"}[sec]
            sheet[dest].append(m)
        out[lab] = sheet
    return out


def pair_sheets(f4: dict, M: Masker, ids: Ids, flab: dict, clab: dict) -> dict:
    f2 = load(B / "F2_firms.json")["firms"]
    out = {}
    for key, p in f4["pairs"].items():
        firm, code = key.split("|")
        r = []
        for nw in p.get("news_window_items") or []:
            r.append({"what": "news window", "rule": nw.get("rule"), "effect": nw.get("effect"),
                      "stages": nw.get("stages"), "class": nw.get("class")})
        if p.get("position_or_cap"):
            r.append({"what": "product cap or position limit at 50K", "rule": p.get("position_or_cap")})
        if p.get("restrictions_text"):
            r.append({"what": "restrictions recorded for this product", "rule": p.get("restrictions_text")})
        if FAMILY_OF[code] == "grains":
            sc = (f2[firm].get("session_cutoffs") or {}).get("value")
            r.append({"what": "trading hours for this product", "rule":
                      sc or "grain Globex hours 19:00-07:45 and 08:30-13:20 CT (exchange schedule); the firm's "
                            "flat-by time applies"})
        fb = (f2[firm].get("flat_by_close") or {}).get("value")
        r.append({"what": "daily flat-by time (firm-wide)", "rule": fb})
        masked = []
        for x in r:
            mid = ids.new(f"F4_facts_unmasked.json:pairs.{key}", key)
            masked.append({"id": mid, **{k: M.text(v, firm_ctx=firm) if isinstance(v, (str, dict, list)) else v
                                         for k, v in x.items()},
                           "binds": "plan P1 (modelled 50K plan); stages as the rule states"})
        out[f"{flab[firm]}|{clab[code]}"] = {"listed_on_modelled_plan": p.get("listed_50k"), "R_facts": masked}
    return out


FORMAT_CONTRACTS = (
    "Masked contract sheet (Stage E.32b). Keys of 'contracts' are random contract labels (K-xxxx); the same label "
    "names the same contract everywhere in both sheets. Each contract has seven evidence lists: D2a_automated_share "
    "(automated or HFT share of volume for the product, its group or a related market), D2b_programs "
    "(market-maker, lead market-maker and volume-incentive programs), D3_s1_relationships (spread, cointegration, "
    "lead-lag relationships with horizon), D3_s2_scheduled_releases (scheduled releases, timing, absorption speed), "
    "D3_s3_session_structure (session handoffs, pauses, settlement windows), Sat_iii_price_discovery "
    "(information-share or price-discovery studies) and D6_directional_evidence (intraday directional studies). "
    "Every item has a fresh id (I-xxxxxx), 'applies_to' (one of: this contract; a same-underlying sibling; the "
    "product group; a close cousin (same asset class on CME Globex); the asset class broadly or a multi-asset "
    "study; another venue of the same underlying), the reader's value, window (data period or dates in force), "
    "detail and verbatim quote with product codes, product names, firm and platform names replaced by labels or "
    "'[other product]', references replaced by '[ref]', and 'verified': full text; abstract [unverified]; snippet "
    "[unverified]; or reused from an earlier stage (level as its text states). D6 items also carry keyword flags "
    "after_2010, out_of_sample, net_of_costs and horizon, derived mechanically from the reader's text (the text is "
    "authoritative; null = not stated). pointer_only = the reader marked it a pointer, never a source alone; "
    "negative_finding = a null or negative result. 'extended-hours' replaces the abbreviation for electronic or "
    "extended trading hours. Asset-class words (for example 'crude oil', 'weekly inventory report') are kept. "
    "The sheet carries no ADV, contract size, multiplier, tick, fee, settlement method, sibling or leader facts.")
FORMAT_FIRMS = (
    "Masked firm sheet (Stage E.32b). Keys of 'firms' are random firm labels (V-xxxx); 'pairs' keys are "
    "'<firm label>|<contract label>' with the contract labels of the contract sheet. Plan and stage names are "
    "replaced by neutral labels (plan P1, P2 ... within each firm; 'evaluation stage', 'funded stage'); "
    "'modelled_plan' names the standard 50K plan the program models. Per firm: A_facts (automation and API rules, "
    "order-rate, minimum-hold and scalping rules, evaluation and funded stages), Rel_facts (operating age, payout "
    "delays, denials or disputes, rule changes, regulatory actions against the firm itself), R_facts_firm_wide, "
    "plan_facts and payout_context, each item with its date (E.28 lookup 2026-10-21, or the page fetch time of the "
    "2026-10-28 refetch) and, for A and R facts, 'binds' (which plan and stages the rule binds, as its text "
    "states). 'lookup_date' gives the lookup date for the 12-months-before-lookup rule. Per pair: R_facts (news "
    "windows and product restrictions for that contract at that firm, trading-hour limits, the flat-by time) and "
    "whether the modelled plan lists it. Verified levels: full text (firm page) unless stated. The strategy "
    "profile being rated: a directional one-lot strategy run by an automated retail system, entering and exiting "
    "by market order (or a limit order priced under the trade-through rule), at most 20 round trips a trading day, "
    "holds from 5 minutes to the session close, latency of tens of milliseconds to one second, no co-location, "
    "no rebates.")


def main() -> int:
    if (B / "F4_masks_FINAL.txt").exists():
        raise SystemExit("refused: F4_masks_FINAL.txt exists; the mask set is final")
    f4 = load(B / "F4_facts_unmasked.json")
    e28key = load(E28 / "A3_mask_key.json")
    banned = set(e28key["contracts"]) | set(e28key["firms"]) | set(e28key["platforms"]) | set(
        e28key["other_products"])
    clab = dict(zip(CODES, fresh_labels("K", len(CODES), banned)))
    flab = dict(zip(FIRMS, fresh_labels("V", len(FIRMS), banned)))
    plab = dict(zip(V.PLATFORMS, fresh_labels("W", len(V.PLATFORMS), banned)))
    M, ids, items = Masker(clab, flab, plab), Ids(), Items()
    contracts, rel_log = contract_sheets(items, f4, M, ids, clab)
    firms = firm_sheets(f4, M, ids, flab, clab)
    pairs = pair_sheets(f4, M, ids, flab, clab)
    gen = now_pdt()
    (B / "F4_masked_contracts.json").write_text(json.dumps(
        {"format": FORMAT_CONTRACTS, "generated_pdt": gen, "contracts": contracts}, indent=1, ensure_ascii=False))
    (B / "F4_masked_firms.json").write_text(json.dumps(
        {"format": FORMAT_FIRMS, "generated_pdt": gen, "firms": firms, "pairs": pairs}, indent=1,
        ensure_ascii=False))
    key = {"generated_pdt": gen, "method": "secrets module: 4 random capital letters per label (K- contracts, V- "
                                           "firms, W- platforms), I- + 6 random characters per masked item",
           "contracts": {v: k for k, v in clab.items()}, "firms": {v: k for k, v in flab.items()},
           "platforms": {v: k for k, v in plab.items()},
           "pairs": {f"{flab[f]}|{clab[c]}": f"{f}|{c}" for f in FIRMS for c in CODES},
           "items": ids.key, "relations": rel_log}
    (B / "F4_mask_key.json").write_text(json.dumps(key, indent=1, ensure_ascii=False))
    n_c = sum(len(v) for s in contracts.values() for k, v in s.items() if isinstance(v, list))
    n_f = sum(len(v) for s in firms.values() for k, v in s.items() if isinstance(v, list))
    n_p = sum(len(v["R_facts"]) for v in pairs.values())
    print(f"masked items: contracts {n_c}, firms {n_f}, pairs {n_p}, total ids {len(ids.key)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
