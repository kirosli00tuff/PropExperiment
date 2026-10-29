"""F3: work/R4/draft_sections.md version 3 from version 2 (work/R4/draft_sections_v2.md) and the new sections.

Reads only stage files (JSON and markdown); no market data, no outcomes. Every replacement is exact and counted.
"""
import json
from pathlib import Path

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
B = REPO / "reports/stage_e32b_briefs"
HERE = Path(__file__).parent
V2 = (B / "work/R4/draft_sections_v2.md").read_text()
OUT = B / "work/R4/draft_sections.md"
lines = V2.split("\n")


def sec(start, end=None):
    """Lines from the line starting with `start` to (excluding) the next line starting with `end`."""
    i = next(k for k, l in enumerate(lines) if l.startswith(start))
    j = len(lines) if end is None else next(k for k, l in enumerate(lines) if k > i and l.startswith(end))
    return "\n".join(lines[i:j]).rstrip("\n")


def rep(text, old, new, n=1):
    c = text.count(old)
    assert c == n, (c, n, old[:80])
    return text.replace(old, new)


S0 = sec("## 0. Facts for lead decisions", "## 1. The R4 list")
S2 = sec("## 2. Outline skeleton", "## 3. Program 1")
S3 = sec("## 3. Program 1", "## 4. Program 2")
S4 = sec("## 4. Program 2", "## 5. Program 3")
S5 = sec("## 5. Program 3", "## 6. Program 4")
S6 = sec("## 6. Program 4", "## 7. Best own-broker")
S8 = sec("## 8. Thresholds", "## 9. Sensitivities")
SA = sec("## Appendix A.", "## 10. Not done")
S10 = sec("## 10. Not done")

HEADER = (HERE / "header_v3.md").read_text().rstrip("\n")

# ---- section 0 ----
S0 = rep(S0, "## 0. Facts for lead decisions (version 1 record, with the lead's resolutions)",
         "## 0. Facts for lead decisions (version 1 record and L11, with the lead's resolutions)")
S0 = rep(S0, "would both need post-2024-03 data (sections 4-5);\ntheir only unread post-2024-03 stretch today is "
             "2024-03-01..2025-03-31 (13 months), so two programs reading it would\nshare it.",
         "would both need post-2024-03 data (Appendix B and\nsection 4); their longest unread post-2024-03 span today is "
         "2024-03-01..2025-03-31 (13 months; 2026-06-17 onward,\nabout 4 months to date, is also neither owned nor read), "
         "so two programs reading it would share it. [Version 3: C113\nleft the R4 under LR-Q3b (L11); the EQ3 pool C147 "
         "(section 6) would read the same NQ and RTY span through its MNQ\nand RTY members.]")
S0 = rep(S0, "(arithmetic; the topstep150\nsensitivity file predates LR-Q3a and LR-V31 and was not rerun)",
         "(work/R2/r3_out_ts150_v2.json,\non the corrected base: C072 2.40, rank 22; C147 2.40 through its MNQ member)")
S0 = S0 + "\n\n" + (HERE / "s0_L11.md").read_text().rstrip("\n")

S1 = (HERE / "s1_r4list.md").read_text().rstrip("\n")

# ---- section 2 ----
S2 = rep(S2, "Programs 2 and 3 have no test window without that approval (L10 (i)); Program 4 has none under LR-V31 (section 6).",
         "Program 2 (MNQ) and Program 4's MNQ and RTY members have no test window without that approval (L10 (i));\n"
         "  Program 3 (YM) and Program 4's YM member have none under LR-V31 (section 5).")

# ---- section 3 (Program 1) ----
S3 = rep(S3, "## 3. Program 1: ZL F09 cross-market lead-lag and ZL F10 order-book state (C138, C140; one sealed read)",
         "## 3. Program 1: ZL F10 order-book state and ZL F09 cross-market lead-lag (C140, C138; one sealed read)")
r2 = {c["id"]: c for c in json.loads((B / "R2_combinations.json").read_text())["combinations"]}
q3b_reason = r2["C138"]["Q3"]["reason"]
q3_rater = r2["C138"]["Q3_rater"]["reason"]
assert q3b_reason.startswith("LR-Q3b") and r2["C138"]["Q3"]["value"] == 1 and r2["C138"]["Q3_rater"]["value"] == 2
c140_q3 = r2["C140"]["Q3"]["reason"]
assert r2["C140"]["Q3"]["value"] == 2 and "Q3_rater" not in r2["C140"]

t_lines = S3.split("\n")
ti = t_lines.index("| item | C138 ZL F09 topstep | C140 ZL F10 topstep | source |")
tj = next(k for k in range(ti, len(t_lines)) if not t_lines[k].startswith("|"))
new_rows = ["| item | C140 ZL F10 topstep | C138 ZL F09 topstep | source |", t_lines[ti + 1]]
for row in t_lines[ti + 2:tj]:
    cells = row.split("|")
    assert len(cells) == 6 and cells[0] == "" and cells[5] == "", row[:80]
    item, a, b, src = (x.strip() for x in cells[1:5])
    if item == "C (r3 rank)":
        a, b = "2.65 (2; Q3 1 under LR-Q3b; 2.75 under q3bleg)", "2.75 (1)"  # a = C138's column before the swap
    elif item == "Q3":
        a = (f'2: "{c140_q3}" [R1-11 and R1-15 also held G17 cross-market leads on ZL (R1 file, session 4): other '
             f'families for F10 (LR-OF: no order-book features in either library)]')
        b = (f'1: "{q3b_reason}" (live on ZL: NQ, ZN, 6E, CL, GC; r1fix_report F3-F4). The rater\'s 2, kept as '
             f'Q3_rater: "{q3_rater}"')
        src = "R2_combinations Q3 (LR-Q3b), Q3_rater; ruling (5) 06:21 (rater's value)"
        a, b = b, a  # swapped back below
    elif item == "Q4; Q5; Q6; Q7":
        a = "2 (x 0.0847); 3 (q 0.0645); 4; 4 (discovery USD 19.48, all USD 40.96, estimates; clean 43.04 months, sealed)"
        b = "2; 3; 4; 4 (discovery USD 0, all USD 0, clean 43.04 months, sealed)"
        a, b = b, a
    elif item == "queue-limit variant":
        a, b = "not computed (Topstep)", "not computed (Topstep)"
    elif item == "same pair elsewhere":
        a = "C139 ibkr 2.50 (LR-Q3b)"
        b = "C141 ibkr 2.60 (section 7, best own broker); MZL: no combination (not a top-15 code)"
    # swap to C140 first; keep a full value first where the other cell says "same"
    na, nb = b, a
    if na == "same":
        na, nb = a, "same"
    new_rows.append(f"| {item} | {na} | {nb} | {src} |")
S3 = "\n".join(t_lines[:ti] + new_rows + t_lines[tj:])

S3 = rep(S3, "- ZL in other families' closed lines: R1-08 CP ports (ZL F01 gated at Q3 0), R1-11, R1-13, R1-15, R1-16.",
         "- Same family for F09 at a neighbouring horizon (LR-Q3b): R1-11, R1-15 (G17 leads NQ, ZN, 6E, CL, GC at h60-hF).\n"
         "- Other families: R1-08 CP ports (ZL F01 gated at Q3 0), R1-13, R1-16; for F10 also R1-11 and R1-15 (no order-book\n"
         "  features in either library).")
S3 = rep(S3, "- **P1 data.** ZL, ZS, ZM ohlcv-1m (crush legs) and ZL MBO plus definitions (book).",
         "- **P1 data.** ZL MBO plus definitions (book) and ZL, ZS, ZM ohlcv-1m (crush legs).")
S3 = rep(S3, "incl. the crush gap, E.12, E.17, E.20). Test",
         "incl. the crush gap, E.12, E.17, E.20; E.12 and E.20 with G17 cross-market leads NQ, ZN, 6E, CL, GC on ZL\n"
         "  at h60-hF, R1-11 and R1-15). Test")
# P2: F10 first, and the G17 difference for F09
p2_old_f09 = (S3.split("- **P2 families.** ", 1)[1].split(" F10 on ZL: ", 1)[0])
p2_rest = S3.split(" F10 on ZL: ", 1)[1]
p2_f10 = p2_rest.split(" Stated differences: ", 1)[0]
assert p2_old_f09.startswith("F09 on ZL: ") and p2_f10.endswith("protocol's F3).")
S3 = rep(S3, "- **P2 families.** " + p2_old_f09 + " F10 on ZL: " + p2_f10 + " Stated differences: ",
         "- **P2 families.** F10 on ZL: " + p2_f10 + " " + p2_old_f09 + " Stated differences: ")
S3 = rep(S3, "overnight gap traded in ZS. E.33's context block C",
         "overnight gap traded in ZS; for F09, from R1-11 and R1-15's G17 features, the leaders (ZS and ZM, never G17 leads) and\n"
         "  the 15-60 minute band against h60-hF. E.33's context block C")
# 3(c): F10 rows first
c_lines = S3.split("\n")
ci = next(k for k, l in enumerate(c_lines) if l.startswith("| use | schema | symbols | dates | status |"))
rows = c_lines[ci + 2:ci + 10]
assert rows[0].startswith("| discovery, F09 |") and rows[1].startswith("| discovery, F10 |") and rows[2].startswith(
    "| discovery, F10 (alternative) |") and rows[3].startswith("| test, F09 |") and rows[6].startswith("| definitions |")
c_lines[ci + 2:ci + 10] = [rows[1], rows[2], rows[0], rows[4], rows[5], rows[3], rows[6], rows[7]]
S3 = "\n".join(c_lines)

# ---- RTY -> Appendix B ----
r3 = {c["id"]: c for c in json.loads((B / "r3_out.json").read_text())["combinations"]}
assert (r3["C113"]["C"], r3["C113"]["rank"]) == (2.5, 18)
assert [r3[i]["C"] for i in ("C112", "C115", "C114", "C116")] == [2.5, 2.5, 2.35, 2.05]
SB = S4
SB = rep(SB, "## 4. Program 2: RTY F09 cross-market lead-lag (C113, Topstep)",
         "## Appendix B. Dropped by LR-Q3b: RTY F09 (C113, C 2.50)\n\n"
         "RTY F09 (C113, Topstep) left the R4 under LR-Q3b (L11): Q3 2 -> 1, C 2.60 -> 2.50, r3 rank 3 -> 18; under the\n"
         "leg-level reading (q3bleg) it is R4 3 at 2.60. Version 2's tables are kept below with the R3 values updated and the\n"
         "closed-line overlap corrected from R1Fixer's code check (work/fix4/r1/r1fix_report.md F1-F5).")
for a, b in (("### 4(a) Fact table", "### B(a) Fact table"), ("### 4(b) Pre-registration outline (draft)",
             "### B(b) Pre-registration outline (draft)"), ("### 4(c) Data purchase plan", "### B(c) Data purchase plan"),
             ("### 4(d) Kill-criteria facts", "### B(d) Kill-criteria facts")):
    SB = rep(SB, a, b)
SB = rep(SB, "| C (r3 rank) | 2.60 (3) | r3_out.json |",
         "| C (r3 rank) | 2.50 (18) under LR-Q3b; 2.60 (3) in version 2 and under q3bleg | r3_out.json; r3_out_q3bleg.json |")
rty_rater = r2["C113"]["Q3_rater"]["reason"]
assert r2["C113"]["Q3"]["value"] == 1 and rty_rater.endswith("no cross-market configuration closed on RTY or M2K.")
old_q3 = next(l for l in SB.split("\n") if l.startswith("| Q3 | 2: "))
SB = rep(SB, old_q3,
         f'| Q3 | 1: "{r2["C113"]["Q3"]["reason"]}" (live on M2K/RTY: ZN, 6E, CL, GC, ZC; E.12 also MBT from '
         "2024-01-02; r1fix_report F3-F4). The rater's 2, kept as Q3_rater, named family overlap only (R1-10 K8 "
         "cross-market with MGC, 6C and MNQ legs, R1-13 E16-H2 NQ vs ZN pair, R1-21 S1/S2 on ZM); its statement that no "
         "closed line held a cross-market feature on RTY or M2K is corrected by LR-Q3b | R2_combinations Q3 (LR-Q3b), "
         "Q3_rater |")
SB = rep(SB, "C112 bulenox 2.60, C115 mffu 2.60, C114 tradeify 2.45, C116 ibkr 2.15 (Q6 1: margin)",
         "C112 bulenox 2.50, C115 mffu 2.50, C114 tradeify 2.35, C116 ibkr 2.05 (Q6 1: margin)")
old_ov = SB.split("Closed-line overlap: ", 1)[1].split("\n\n", 1)[0]
assert old_ov.startswith("no cross-market configuration on RTY or M2K.") and "late-session" in old_ov
SB = rep(SB, "Closed-line overlap: " + old_ov, (HERE / "rty_overlap.md").read_text().rstrip("\n"))
SB = rep(SB, "E.12 Gate 0 (M2K). Test:",
         "E.12 Gate 0 (M2K); E.12 and E.20 held G17 cross-market leads ZN, 6E, CL, GC\n"
         "  and ZC on M2K/RTY at h60-hF (R1-11, R1-15). Test:")
SB = rep(SB, "the pair (NQ to\n  RTY) and minutes-scale continuous trading.",
         "the pair (NQ to\n  RTY) and minutes-scale continuous trading; from R1-11 and R1-15's G17 features, the leader (NQ, never a\n"
         "  live feature on RTY or M2K) and the 15-30 minute band against h60-hF (the leg-level reading, q3bleg).")

# ---- MNQ -> section 4 ----
assert (r3["C072"]["C"], r3["C072"]["rank"]) == (2.55, 4)
assert [r3[i]["C"] for i in ("C075", "C074", "C073", "C076")] == [2.55, 2.55, 2.4, 2.4]
S4n = S5
S4n = rep(S4n, "## 5. Program 3: MNQ F08", "## 4. Program 2: MNQ F08")
for x in "abcd":
    S4n = rep(S4n, f"### 5({x})", f"### 4({x})")
S4n = rep(S4n, "| C (r3 rank) | 2.55 (8) | r3_out.json |", "| C (r3 rank) | 2.55 (4) | r3_out.json |")
S4n = rep(S4n, "post-2024-03 as in 4(b) P1", "post-2024-03 as in Appendix B(b) P1")
S4n = rep(S4n, "If Program 2 is also run, the same NQ request serves both (L7).",
          "The same NQ request serves Program 4's MNQ member (section 6) and RTY F09 (Appendix B; L7).")

# ---- YM -> section 5 ----
assert (r3["C021"]["C"], r3["C021"]["rank"]) == (2.55, 5)
S5n = S6
S5n = rep(S5n, "## 6. Program 4: YM F08", "## 5. Program 3: YM F08")
for x in "abcd":
    S5n = rep(S5n, f"### 6({x})", f"### 5({x})")
S5n = rep(S5n, "| C (r3 rank) | 2.55 (9); 2.85 under q3only (rank 1) |", "| C (r3 rank) | 2.55 (5); 2.85 under q3only (rank 1) |")
S5n = rep(S5n, "the CLV rule quoted in 5(a)", "the CLV rule quoted in 4(a)")
S5n = rep(S5n, "As Program 3 on YM's path", "As Program 2 on YM's path")
S5n = rep(S5n, "Published effect: as 5(d)", "Published effect: as 4(d)")
S5n = rep(S5n, "MYM F08 C049 mffu (q3only 2.70) |", "MYM F08 C049 mffu (q3only 2.70); EQ3 pool C147 2.55 (section 6) |")

S6n = (HERE / "s6_eq3.md").read_text().rstrip("\n")
S7n = (HERE / "s7_c141.md").read_text().rstrip("\n")

S8 = rep(S8, "Short test window (Programs 2 and 3 on the 13-month unread post-2024-03 span, about 273 dates as an approximation):",
         "Short test window (Program 2, Program 4's MNQ and RTY members and RTY F09 in Appendix B, on the 13-month unread\n"
         "post-2024-03 span, about 273 dates as an approximation):")


def r4row(name, f, what):
    x = json.loads((B / f).read_text())
    b = x["best_own_broker"]
    import hashlib
    h = hashlib.sha256((B / f).read_bytes()).hexdigest()[:16]
    lst = "; ".join(f"{c['id']} {c['product_or_pool']} {c['family'][:3]} {c['best_venue']} {c['C']:.2f}"
                    for c in x["R4"]["candidates"])
    return (f"| {name} | {f} ({h}) | {what} | {lst} | {b['id']} {b['name']} {b['family'][:3]} {b['venue']} {b['C']:.2f} "
            f"({b['rank']}) | {x['R4']['n_reaching_2']} |")


RUNS = (("primary", "r3_out.json", "LR-Q3a, LR-Q3b, LR-V31, LR-ZLW"),
        ("q3only", "work/R2/r3_out_q3only.json", "LR-Q3a, LR-Q3b (V31 narrow reading; user decision D1)"),
        ("nozlw", "work/R2/r3_out_nozlw.json", "primary plus no ZL window (user decision D2)"),
        ("ts150_v2", "work/R2/r3_out_ts150_v2.json", "primary with Topstep's Standard Path $150 in Q6"),
        ("q3bleg", "work/R2/r3_out_q3bleg.json", "primary without LR-Q3b (leg-level F09 reading)"),
        ("v1", "work/R2/r3_out_v1.json", "before LR-Q3a, LR-Q3b and LR-V31 (LR-Q6p primary)"))
SENS = "\n".join(["| run | file (sha256, first 16) | rulings | R4 (1-5) | best own broker (r3 rank) | reach 2.00 |",
                  "|---|---|---|---|---|---|"] + [r4row(*r) for r in RUNS])
S9 = (HERE / "s9_sens.md").read_text().rstrip("\n").replace("{SENS_TABLE}", SENS)

S10 = rep(S10, "- The published-effect translations (3(d), 5(d), Appendix A)",
          "- The published-effect translations (3(d), 4(d), 6(d), Appendix A)")
S10 = rep(S10, "(4(b) P1).", "(Appendix B(b) P1).")
S10 = S10 + ("\n- Version 3: the EQ3 pool's cut to MNQ and RTY (6(b) P9), its K_eff on 273 dates and the members' combined one-day\n"
             "  sigma (6(a)) are arithmetic by the scorer's formulas at rho 0.5, not a re-score; how a pooled test would be read over\n"
             "  disjoint member windows (YM before 2019-05, MNQ and RTY after 2024-03) is not worked out.")

S4n = rep(S4n, "| owned (NQ 2010-06..2024-02); read (5(b) P1) | 0 |", "| owned (NQ 2010-06..2024-02); read (4(b) P1) | 0 |")
SB = rep(SB, "| owned; read (4(b) P1) | 0 |", "| owned; read (B(b) P1) | 0 |")

doc = "\n\n".join([HEADER, S0, S1, S2, S3, S4n, S5n, S6n, S7n, S8, S9, SA, SB, S10]) + "\n"
OUT.write_text(doc)
print("written", OUT, len(doc.splitlines()), "lines")
