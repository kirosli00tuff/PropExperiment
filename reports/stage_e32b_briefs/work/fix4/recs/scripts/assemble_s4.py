"""F3 (session 4): reports/stage_e32b_recommendations.md from the lead's session-4 sections (verbatim), draft v3 and the
current r3 outputs. Reads only stage files; no market data, no outcomes. Tables are generated from the JSON files.
"""
import collections
import hashlib
import json
import re
import subprocess
from pathlib import Path

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
B = REPO / "reports/stage_e32b_briefs"
HERE = Path(__file__).parent
OUT = REPO / "reports/stage_e32b_recommendations.md"
LEAD = (B / "work/R4/lead_sections.md").read_text()
DRAFT = (B / "work/R4/draft_sections.md").read_text()
S3 = (B / "work/R4/recommendations_s3.md").read_text()
LOG = []


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def block(text, start, end=None, keep_heading=False):
    lines = text.splitlines()
    i = next(k for k, l in enumerate(lines) if l.startswith(start))
    j = len(lines) if end is None else next(k for k, l in enumerate(lines) if k > i and l.startswith(end))
    body = lines[i:j] if keep_heading else lines[i + 1:j]
    return "\n".join(body).strip("\n")


def heading(text, start):
    return next(l for l in text.splitlines() if l.startswith(start))


def rep(text, old, new, n=1):
    c = text.count(old)
    assert c == n, (c, n, old[:90])
    return text.replace(old, new)


# ---- lead blocks (verbatim) ----
L = {
    "base": block(LEAD, "## Base rates used for every prior", "## The candidates"),
    "zl_h": heading(LEAD, "### 1-2."), "zl": block(LEAD, "### 1-2.", "### 3-4."),
    "f08_h": heading(LEAD, "### 3-4."), "f08": block(LEAD, "### 3-4.", "### 5."),
    "eq3_h": heading(LEAD, "### 5."), "eq3": block(LEAD, "### 5.", "### Dropped by LR-Q3b"),
    "rty_h": heading(LEAD, "### Dropped by LR-Q3b"), "rty": block(LEAD, "### Dropped by LR-Q3b", "### Gated"),
    "f01_h": heading(LEAD, "### Gated"), "f01": block(LEAD, "### Gated", "## The non-prop alternative"),
    "nonprop": block(LEAD, "## The non-prop alternative", "## Stop rule"),
    "stop": block(LEAD, "## Stop rule", "## Decisions"),
    "decisions": block(LEAD, "## Decisions for the user"),
}

# ---- draft v3 blocks ----
D = {
    "L": block(DRAFT, "## 0. Facts for lead decisions", "## 1. The R4 list"),
    "r4": block(DRAFT, "## 1. The R4 list", "## 2. Outline skeleton"),
    "skel": block(DRAFT, "## 2. Outline skeleton", "## 3. Program 1"),
    "zl_a": block(DRAFT, "### 3(a) Fact table", "### 3(b)"),
    "zl_b": block(DRAFT, "### 3(b) ", "### 3(c)"),
    "zl_c": block(DRAFT, "### 3(c) Data purchase plan", "### 3(d)"),
    "mnq_a": block(DRAFT, "### 4(a) Fact table", "### 4(b)"),
    "mnq_b": block(DRAFT, "### 4(b) ", "### 4(c)"),
    "mnq_c": block(DRAFT, "### 4(c) Data purchase plan", "### 4(d)"),
    "ym_v31": block(DRAFT, "## 5. Program 3: YM F08", "### 5(a)"),
    "ym_a": block(DRAFT, "### 5(a) Fact table", "### 5(b)"),
    "ym_b": block(DRAFT, "### 5(b) ", "### 5(c)"),
    "ym_c": block(DRAFT, "### 5(c) Data purchase plan", "### 5(d)"),
    "eq3_a": block(DRAFT, "### 6(a) Fact table", "### 6(b)"),
    "eq3_b": block(DRAFT, "### 6(b) ", "### 6(c)"),
    "eq3_c": block(DRAFT, "### 6(c) Data purchase plan", "### 6(d)"),
    "eq3_d": block(DRAFT, "### 6(d) Kill-criteria facts", "## 7. Best own-broker"),
    "own_a": block(DRAFT, "### 7(a) Fact table", "### 7(b)"),
    "own_bc": block(DRAFT, "### 7(b)-(c) Outline and data", "### 7(d)"),
    "own_d": block(DRAFT, "### 7(d) Kill-criteria facts", "## 8. Thresholds"),
    "thr": block(DRAFT, "## 8. Thresholds", "## 9. Sensitivities"),
    "sens": block(DRAFT, "## 9. Sensitivities", "## Appendix A."),
    "appA": block(DRAFT, "## Appendix A.", "## Appendix B."),
    "rty_intro": block(DRAFT, "## Appendix B.", "### B(a)"),
    "rty_a": block(DRAFT, "### B(a) Fact table", "### B(b)"),
    "rty_b": block(DRAFT, "### B(b) ", "### B(c)"),
    "rty_c": block(DRAFT, "### B(c) Data purchase plan", "### B(d)"),
    "rty_d": block(DRAFT, "### B(d) Kill-criteria facts", "## 10. Not done"),
    "limits": block(DRAFT, "## 10. Not done"),
}
assert block(DRAFT, "### 3(b) ", "### 3(c)", keep_heading=True).splitlines()[0] == \
    "### 3(b) Pre-registration outline (draft): one registration, two families, one sealed read"

# ---- renumbering of draft references into this file's numbering ----
SEC = {"1": "4.0", "2": "4.3", "3": "4.5", "4": "4.6.1", "5": "4.6.2", "6": "4.7", "7": "5", "8": "4.4", "9": "3.2"}
LET = {"3": "4.5", "4": "4.6.1", "5": "4.6.2", "6": "4.7"}
PRE = [
    ("sections 4(b), 5 and Appendix B(b) P1", "sections 4.6.1(b), 4.6.2 and Appendix (b) P1"),
    ("sections 4 and 5", "sections 4.6.1 and 4.6.2"),
    ("Sections 4 and 5", "Sections 4.6.1 and 4.6.2"),
    ("assumptions as 3(d)", "assumptions: predictor and 30-minute return bivariate normal, R2_OOS read as a squared\n"
                            "  correlation, a sign rule, gross"),
    ("(3(d), 4(d), 6(d), Appendix A)", "(work/R4/draft_sections.md \u00a73(d) and \u00a74(d), 4.7(d) and section 4.9 here)"),
]
SEC_RE = re.compile(r"(?<![\w.])(?<!seal )(?<!Seal )(?<!E\.29 )(?<!RETURN )(?<!report\.md )(?<!seal\.md )([Ss])ection(\s+)([1-9])(?!\d|\.\d)")
LET_RE = re.compile(r"(?<![\w.\u00a7])([3-6])\(([a-d])\)")


def renum(text, tag):
    for a, b in PRE:
        text = text.replace(a, b)
    text = text.replace("Appendix B(", "Appendix (")
    text = re.sub(r"\bAppendix B\b", "the Appendix", text)
    text = re.sub(r"(?<![\w(])B\(([a-d])\)", r"Appendix (\1)", text)
    text = text.replace("Appendix A", "section 4.9")

    def s(m):
        LOG.append(f"{tag}: section {m.group(3)} -> {SEC[m.group(3)]} | ...{text[max(0, m.start() - 30):m.end() + 10]!r}")
        return f"{m.group(1)}ection{m.group(2)}{SEC[m.group(3)]}"

    def l(m):
        n, x = m.group(1), m.group(2)
        new = f"work/R4/draft_sections.md {n}({x})" if (x == "d" and n in "345") else f"{LET[n]}({x})"
        LOG.append(f"{tag}: {n}({x}) -> {new} | ...{text[max(0, m.start() - 30):m.end() + 10]!r}")
        return new

    text = SEC_RE.sub(s, text)
    text = LET_RE.sub(l, text)
    return text.replace("\u00a7", "")


for k in D:
    D[k] = renum(D[k], k)

r3 = json.loads((B / "r3_out.json").read_text())
combos = json.loads((B / "R2_combinations.json").read_text())
r1 = json.loads((B / "R1_closed_lines.json").read_text())
r1md = (B / "R1_closed_lines.md").read_text().splitlines()


def short(s, n):
    s = s.replace("|", "/")
    return s if len(s) <= n else s[: n - 3].rstrip() + "..."


# ---- section 1 ----
XM = {"R1-11": " Cross-market (session 4): G17 leads NQ, ZN, 6E, CL, GC, ZC (E.12 also MBT from 2024-01-02), never on the "
               "product's own cluster.",
      "R1-15": " Cross-market (session 4): G17 leads NQ, ZN, 6E, CL, GC, ZC, six of the 36 frozen features, never on the "
               "product's own cluster."}
rows = ["| id | type | family | products | horizons | trials | closing |", "|---|---|---|---|---|---|---|"]
for ln in r1["lines"]:
    prods = [p["code"] if isinstance(p, dict) else str(p) for p in ln["products"]]
    ps = ", ".join(prods[:8]) + (f" (+{len(prods) - 8})" if len(prods) > 8 else "")
    cl = ln["closing"]
    cls = (cl.get("decision", "") + ", " + cl.get("source", "")) if isinstance(cl, dict) else str(cl)
    fam = short(ln["family"], 95) + XM.get(ln["id"], "")
    if ln["id"] in XM:
        assert ln.get("cross_market_features", "").startswith("[added 2026-10-29 (session 4, RV2 B1/S6)]")
    rows.append(f"| {ln['id']} | {ln['type']} | {fam} | {ps} | {short(str(ln['horizons']), 70)} | {ln['n_trials']} | "
                f"{short(cls, 80)} |")
R1_TABLE = "\n".join(rows)
assert sum(x["n_trials"] for x in r1["lines"]) == 838 and len(r1["lines"]) == 23
xm_md = [(i + 1, l) for i, l in enumerate(r1md) if l.startswith("- cross-market [added 2026-10-29 (session 4, RV2 B1/S6)]:")]
assert len(xm_md) == 2, xm_md
XM_TEXT = ("Cross-market content of R1-11 and R1-15, added in session 4 for RV2 B1 and S6 (briefs/R1_closed_lines.md lines "
           f"{xm_md[0][0]} and {xm_md[1][0]}; the .json field cross_market_features), verbatim:\n"
           f"- R1-11 {xm_md[0][1][2:]}\n- R1-15 {xm_md[1][1][2:]}")
BIND = S3.split("Lines and readings that bind every combination:\n", 1)[1].split("\n## 2. R2: combinations", 1)[0].rstrip()
BIND = BIND.split("- LR-Q3a and LR-V31 (lead, 06:47-06:49; work/R2/patch_v31_q3_lead.py):", 1)[0].rstrip()
patch_doc = (B / "work/R2/patch_v31_q3_lead.py").read_text().split('"""')[1].strip()
rul = (B / "RULINGS.md").read_text().splitlines()
i0 = next(k for k, l in enumerate(rul) if l.startswith("- LR-Q3b (07:19:57"))
i1 = next(k for k, l in enumerate(rul) if l.startswith("- LR-RV1S1"))
RUL_Q3B = "\n".join(rul[i0:i1])

# ---- section 2 ----
cs = combos["combinations"]
fams = sorted({c["family"][:3] for c in cs})
venues = ["topstep", "bulenox", "lucid", "mffu", "tradeify", "ibkr"]
cnt = collections.Counter((c["venue"], c["family"][:3]) for c in cs)
vt = collections.Counter(c["venue"] for c in cs)
ft = collections.Counter(c["family"][:3] for c in cs)
crow = ["| venue | " + " | ".join(fams) + " | total |", "|---|" + "---|" * (len(fams) + 1)]
for v in venues:
    crow.append(f"| {v} | " + " | ".join(str(cnt[(v, f)]) for f in fams) + f" | {vt[v]} |")
crow.append("| total | " + " | ".join(str(ft[f]) for f in fams) + f" | {len(cs)} |")
COUNT_TABLE = "\n".join(crow)
S2_OLD = S3.split("## 2. R2: combinations\n", 1)[1].split("\n## 3. R3: scores", 1)[0].strip("\n")
old_count = S2_OLD.split("by venue and family:\n\n", 1)[1].split("\n\n", 1)[0]
assert old_count == COUNT_TABLE, "combination counts changed"
pp = collections.Counter((c["product"] or c["pool"]["name"]) for c in cs)
PROD_LINE = ", ".join(f"{k} {v}" for k, v in sorted(pp.items(), key=lambda kv: -kv[1]))
assert f"By product or pool: {PROD_LINE}." in S2_OLD
lp2 = combos["lead_patch_v2"]
assert lp2["q3b_to_1"] == 7 and "LR-Q3b" in lp2["rulings"]
S2_NEW = S2_OLD + (
    "\n- LR-Q3b (lead, 07:19:57, RV2 B1; work/R2/patch_v31_q3_lead.py in every mode): the 7 F09 combinations on RTY and ZL\n"
    "  (C112-C116, C138-C139) set to Q3 1, the rater's 2 kept as Q3_rater (R2_combinations.json lead_patch_v2: q3b_to_1\n"
    "  7); mode q3bleg (session 4) keeps the rater's value (the leg-level reading, work/R2/R2_combinations_q3bleg.json).\n"
    "- R1Fixer (session 4, work/fix4/r1/r1fix_report.md): the G17 facts added to R1-11 and R1-15 (R1_closed_lines.md and\n"
    "  .json); errata blocks added to R2_dossiers.md (session 4 items 4-7, with the catalog rows of R1-11 and R1-15) and\n"
    "  R2_Q_ratings.md (no rating line changed); R2_dossiers_for_rating.md kept as rated. The per-dossier lines that\n"
    "  describe R1-11 and R1-15 without G17 are covered by the errata, not edited (r1fix_report section 3).")

# ---- section 3 ----
ranked = sorted([c for c in r3["combinations"] if c.get("rank")], key=lambda c: c["rank"])
t = ["| rank | id | product or pool | family | venue | band | h_c | C | Q1 | Q2 | Q3 | Q4 | Q5 | Q6 | Q7 |",
     "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for c in ranked[:20]:
    q = " | ".join(str(int(c[f"Q{i}"])) for i in range(1, 8))
    t.append(f"| {c['rank']} | {c['id']} | {c['name']} | {c['family']} | {c['venue']} | {', '.join(c['band'])} | "
             f"{c['h_c']} | {c['C']:.2f} | {q} |")
TOP20 = "\n".join(t)
n_elig = len(ranked)
n_gate = sum(1 for c in r3["combinations"] if c["status"] != "eligible")
n_ge2 = sum(1 for c in ranked if c["C"] >= 2.0)
LRQ3A = {"YM": "E16-H1 on YM (R1-13; V31)", "MYM": "K1-cp1-01 on MYM (R1-03); E16-H1 on the YM path (R1-13)",
         "RTY": "K1-cp1-01 on M2K (R1-03); E16-H1 pooled incl. RTY (R1-13)"}
RATER = {"MNQ": "R1-14 E.20 H6 (NQ path at MNQ cost, C-30 to close; V38)",
         "ZL": "R1-08 K6-cp1-01 (ZL momentum port, decision 12:44 CT; V40)",
         "EQ3": "R1-14 through the MNQ member", "EQ3m": "R1-14 through the MNQ member"}
cq = {c["id"]: c for c in cs}
g = ["| id | product or pool | family | venue | gated by | closed line |", "|---|---|---|---|---|---|"]
for c in sorted([c for c in r3["combinations"] if c["status"] != "eligible"], key=lambda c: c["id"]):
    lead_gate = cq[c["id"]]["Q3"]["reason"].startswith("LR-Q3a")
    assert cq[c["id"]]["Q3"]["value"] == 0
    by = "LR-Q3a (lead)" if lead_gate else "CombinationScorer (flag 1)"
    g.append(f"| {c['id']} | {c['name']} | {c['family'][:3]} | {c['venue']} | {by} | "
             f"{(LRQ3A if lead_gate else RATER)[c['name']]} |")
GATED = "\n".join(g)
S3_RULE = S3.split("## 3. R3: scores\n\n", 1)[1].split("\n\nPrimary run", 1)[0]

# ---- hashes ----
HP = ["reports/stage_e32b_ranking_spec.md", "reports/stage_e32b_briefs/r3_out.json",
      "reports/stage_e32b_briefs/R2_combinations.json", "reports/stage_e32b_briefs/work/R2/r3_out_q3bleg.json",
      "reports/stage_e32b_briefs/work/R2/R2_combinations_q3bleg.json", "reports/stage_e32b_briefs/work/R2/r3_out_q3only.json",
      "reports/stage_e32b_briefs/work/R2/r3_out_nozlw.json", "reports/stage_e32b_briefs/work/R2/r3_out_ts150_v2.json",
      "reports/stage_e32b_briefs/work/R2/R2_combinations_ts150_v2.json", "reports/stage_e32b_briefs/work/R2/r3_out_v1.json",
      "reports/stage_e32b_briefs/work/R2/R2_combinations_v1.json", "reports/stage_e32b_briefs/work/R2/combos_detail.json",
      "reports/stage_e32b_briefs/work/R2/groundwork.json", "reports/stage_e32b_briefs/work/R2/patch_v31_q3_lead.py",
      "reports/stage_e32b_briefs/R2_dossiers.md", "reports/stage_e32b_briefs/R2_Q_ratings.md",
      "reports/stage_e32b_briefs/R1_closed_lines.md", "reports/stage_e32b_briefs/R1_closed_lines.json",
      "reports/stage_e32b_briefs/F5_holding.md", "reports/stage_e32b_briefs/F5_holding.json",
      "reports/stage_e32b_briefs/work/F5/SR80.json", "reports/stage_e32b_briefs/F2_data_access.json",
      "reports/stage_e32b_briefs/score32b_out.json", "reports/stage_e32b_briefs/work/score/score32b_out_run2.json",
      "reports/stage_e32b_briefs/RULINGS.md", "reports/stage_e32b_briefs/REVIEW_recs.md",
      "reports/stage_e32b_briefs/work/fix4/r1/r1fix_report.md", "reports/stage_e32b_briefs/work/fix4/score/score_fix_report.md",
      "reports/stage_e32b_briefs/work/R4/lead_sections.md",
      "reports/stage_e32b_briefs/work/R4/draft_sections.md", "reports/stage_e32b_briefs/work/R4/recommendations_s3.md",
      "reports/stage_e32_discovery_protocol.md", "reports/stage_e32_test_seal.md"]
HASH_TABLE = "\n".join(["| file | sha256 (first 16) |", "|---|---|"] + [f"| {p} | {sha(REPO / p)[:16]} |" for p in HP])
sc_now = json.loads((B / "score32b_out.json").read_text())
sc_run2 = json.loads((B / "work/score/score32b_out_run2.json").read_text())
assert sc_now["primary"]["top15"] == sc_run2["primary"]["top15"]
SC_NOW, SC_RUN2 = sha(B / "score32b_out.json")[:16], sha(B / "work/score/score32b_out_run2.json")[:16]

date = subprocess.run(["date", "+%Y-%m-%d %H:%M %Z"], capture_output=True, text=True,
                      env={"TZ": "America/Vancouver"}).stdout.strip()
SPEC = sha(REPO / "reports/stage_e32b_ranking_spec.md")
SUMMARY = (HERE / "sec0_body.txt").read_text().strip()
LEADCHECK = (HERE / "sec_lc.txt").read_text().strip()


def sub(h):
    return h.replace("### ", "", 1)


doc = f"""# Stage E.32b recommendations (step 3b, R1-R4)

Assembled {date} by RecsAssembler-OpusXHigh (Opus 5.5 xhigh, session 4) from the lead's session-4 sections
(work/R4/lead_sections.md, Opus 5.5 max: base rates, cases, priors, kill criteria, the dropped-RTY and F01 notes, the
non-prop paragraph, stop rule and user decisions, kept verbatim) and the draft v3 (work/R4/draft_sections.md: fact
tables, pre-registration outlines, data purchase plans), after lead ruling LR-Q3b. The session-3 file is kept as
work/R4/recommendations_s3.md. Frozen spec reports/stage_e32b_ranking_spec.md sha256 {SPEC}, section 8. Facts and
arithmetic only: no strategy outcome was computed or read, no Databento call, no market data. Times PDT. N = 838
(ledger r009-E33).

## 0. Summary

{SUMMARY}

## 1. R1: closed lines

The program's 23 closed lines (briefs/R1_closed_lines.md, full fields in R1_closed_lines.json; ledger
ledger/trial_registrations.jsonl). Trials sum to N = 838: baseline 471 (198 screened + 273 Gate 0), then r001-C1 +2,
r002-E16 +5, r003-C1b +2, r004-E20H6 +3, r005-E20S +45, r006-E21 +4, r007-E22 +1, r008-E23 +5, r009-E33 +300.

{R1_TABLE}

{XM_TEXT}

Lines and readings that bind every combination:
{BIND}
- LR-Q3a, LR-V31 and (session 4) LR-Q3b (lead; work/R2/patch_v31_q3_lead.py, docstring):
```
{patch_doc}
```
- LR-Q3b, its detail and LR-OF (lead; briefs/RULINGS.md, "Rulings (session 3 end and session 4)"):
```
{RUL_Q3B}
```

## 2. R2: combinations

{S2_NEW}

## 3. R3: scores

{S3_RULE}

Primary run (briefs/r3_out.json, {r3['generated_pdt']}, after LR-Q3a, LR-Q3b, LR-V31 and LR-ZLW): {len(r3['combinations'])}
combinations, {n_elig} eligible, {n_gate} gated (Q3 = 0), {n_ge2} eligible combinations with C >= 2.00. Top 20 by C:

{TOP20}

### 3.1 Gated combinations ({n_gate}; Q3 = 0, re-tests of closed lines)

{GATED}

LR-Q3b set no gate: it moved 7 F09 combinations from Q3 2 to 1 (section 2).

### 3.2 Sensitivities and their R4 lists

{D['sens']}

## 4. R4: build candidates

### 4.0 The R4 list and grouping

{D['r4']}

### 4.1 Base rates (lead)

{L['base']}

### 4.2 Facts for lead decisions (RecsDrafter record L1-L10 and L11, with the lead's resolutions)

{D['L']}

### 4.3 Outline skeleton shared by every program

{D['skel']}

### 4.4 Thresholds

{D['thr']}

### 4.5 {sub(L['zl_h'])}

{L['zl']}

#### 4.5(a) Fact table

{D['zl_a']}

#### 4.5(b) Pre-registration outline (draft): one registration, two families, one sealed read

{D['zl_b']}

#### 4.5(c) Data purchase plan

{D['zl_c']}

Kill-criteria facts for Program 1 (power, thresholds, published effects, the sibling-leg measurement, prop limits by
horizon) are in work/R4/draft_sections.md 3(d).

### 4.6 {sub(L['f08_h'])}

{L['f08']}

#### 4.6.1 MNQ F08 (C072, Topstep)

#### 4.6.1(a) Fact table

{D['mnq_a']}

#### 4.6.1(b) Pre-registration outline (draft)

{D['mnq_b']}

#### 4.6.1(c) Data purchase plan

{D['mnq_c']}

#### 4.6.2 YM F08 (C021, Topstep), under V31

{D['ym_v31']}

#### 4.6.2(a) Fact table

{D['ym_a']}

#### 4.6.2(b) Pre-registration outline (draft)

{D['ym_b']}

#### 4.6.2(c) Data purchase plan

{D['ym_c']}

Kill-criteria facts for MNQ F08 and YM F08 are in work/R4/draft_sections.md 4(d) and 5(d).

### 4.7 {sub(L['eq3_h'])}

{L['eq3']}

#### 4.7(a) Fact table

{D['eq3_a']}

#### 4.7(b) Pre-registration outline (draft)

{D['eq3_b']}

#### 4.7(c) Data purchase plan

{D['eq3_c']}

#### 4.7(d) Kill-criteria facts

{D['eq3_d']}

### 4.8 {sub(L['rty_h'])}

{L['rty']}

Its fact table, outline, data plan and kill-criteria facts (draft v3 Appendix B, with the closed-line overlap corrected
from R1Fixer's code check) are in the Appendix at the end of this file.

### 4.9 {sub(L['f01_h'])}

{L['f01']}

{D['appA']}

## 5. The non-prop alternative

{L['nonprop']}

### 5.1 Fact table (C141)

{D['own_a']}

### 5.2 Outline and data

{D['own_bc']}

### 5.3 Kill-criteria facts

{D['own_d']}

## 6. Stop rule for the whole directional program

{L['stop']}

## 7. Decisions for the user (with recommendations)

{L['decisions']}

## 8. Sources and scripts

Inputs (sha256 at assembly):

{HASH_TABLE}

Score output: R2 took only the top-15 pair list from score32b_out.json. The R2 files and the session-3 version of this
file record the 05:40:30 run's hash ({SC_RUN2}..., the run kept as work/score/score32b_out_run2.json);
the score was rerun at 08:51:03 for RV1 S1 and S3 (briefs/score32b_out.json, sha256 {SC_NOW}...) with no score, gate or
rank change (work/fix4/score/score_fix_report.md); the top-15 list is identical in both runs (checked by this
assembly).

Scripts: work/score/score32b.py and r3_score.py (ScoreCoder; R3); work/F5/f5_holding.py (F5 bands); work/R2/
build_groundwork.py, build_combos.py, write_dossiers.py, merge_q.py (DossierWriter, lead merge); work/R2/patch_q6p_lead.py
and patch_v31_q3_lead.py (lead patches; LR-Q3b applied in every mode since 07:19, and the q3bleg mode, session 4, which
leaves LR-Q3b out: work/R2/R2_combinations_q3bleg.json and r3_out_q3bleg.json, 08:48:48); reports/stage_e32_briefs/
protocol/p7_final.py with p7_thresholds.py (thresholds, through the RecsDrafter's scratch scripts hurdles.py and
short_test.py in /tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/3860d0d1-cf19-46b3-a4da-6fda65b58c32/
scratchpad/d5/). Draft v3 by build_draft_v3.py and this file by assemble_s4.py, with their text inputs, copied to
work/fix4/recs/scripts/ (written in the session-4 scratchpad).
Decisions cited: docs/DECISIONS.md V28, V31, V32, V33, V38, V43, V45, V49, V50, V51, V52, V56; briefs/RULINGS.md
(LR-Q3a, LR-V31, LR-ZLW, LR-Q3b, LR-OF); reports/stage_e32b_STATE.md. Kill-criteria facts for Programs 1-3 (power,
prop limits by horizon, published effect sizes) stay in work/R4/draft_sections.md 3(d), 4(d) and 5(d); Program 4's
are in section 4.7(d) and the own broker's in 5.3.

Limits (RecsDrafter and RecsAssembler):
{D['limits']}

## Appendix. Dropped by LR-Q3b: RTY F09 (C113, C 2.50)

{D['rty_intro']}

### Appendix (a) Fact table

{D['rty_a']}

### Appendix (b) Pre-registration outline (draft)

{D['rty_b']}

### Appendix (c) Data purchase plan

{D['rty_c']}

### Appendix (d) Kill-criteria facts

{D['rty_d']}

## Lead check

{LEADCHECK}
"""
OUT.write_text(doc)
(HERE / "renum_log.txt").write_text("\n".join(LOG) + "\n")
print("written", OUT, len(doc.splitlines()), "lines;", len(LOG), "renumberings logged")
