# Stage E.1 freeze audit (Task 3)

- Auditor: FreezeAuditor-FableXHigh (worker-xhigh on fable). Model: Claude Fable 5.1
  (claude-fable-5-1). The auditor wrote none of the work it audits.
- Start: 2026-09-24 17:57 PDT. End of Part 1: 2026-09-24 18:13 PDT (America/Vancouver).
- Inputs read: docs/prompts/STAGE_E.1.md (Task 1 text, U1 to U9, the recount paragraph, the
  failure-path line; Tasks 3 to 5 for what the lead may rule); `git diff 01b259a` on
  docs/STAGE_E_DESIGN.md, docs/NULL_CRITERIA_E.md, docs/DECISIONS.md, reports/stage_e0_catalog.md,
  reports/stage_e0_catalog.json, reports/stage_e0_catalog_K1.md to K8.md (no commit touched these
  files after 01b259a: `git log 01b259a..HEAD -- <files>` is empty); reports/stage_e1_changes.md in
  full; reports/stage_e0_review.md (R-28 and the verdict) and reports/stage_e0_review_rulings.md
  (R-04, R-06, R-15, R-24, R-28); ledger/databento_spend.jsonl (the 5,050 stage-E.0-2026-09-23 quote
  lines, read only); reports/stage_e1_STATE.md (S-1, S-2); reports/stage_e0_liquidity.json (ADV
  presence); data/config.py and data/pull_universe.py (read only, for the U5 statement in D13 and the
  PL dependency check). Scripts and their output are quoted below; they live in the session
  scratchpad and are not part of the repo.
- Boundaries kept: no repo file edited except this one; no test run; no network; no data/, ledger/,
  .env, REGISTRATION.md or TopstepX access; no commit.

## Part 1: freeze audit (Task 3)

### Check 1: every diff hunk maps to a decision, every decision is applied

What I did. A script parsed the 96 markdown entries of reports/stage_e1_changes.md (heading, files,
"Matches replaced per file", Old block, New block) and, for each entry and target file, counted the
Old text at 01b259a, the New text in the working tree, and any Old text left outside the New text.
Then, for every added or removed line in `git diff 01b259a` on the 11 markdown files, it checked
that the line is covered by some entry for that file (allowing entries that replace part of a line
or span a line break). The JSON diff was compared by hand with the log's 32-row JSON table.

Evidence.
- 96/96 entries: Old count at base = stated count, New count now = stated count, no residual Old.
  One flag, resolved: K5-22 ("1 per admitted exposure (at most 4)") occurs 7 times in the base
  assembled catalog; the 3 untouched copies are K4's three ports (reports/stage_e0_catalog.md
  lines 3540, 3600, 3641, inside the K4 section 3260-4355), correctly left alone.
- Diff coverage: 0 uncovered lines in all 11 files (the first pass flagged 10 lines that are
  halves of multi-line entries D-12, D-31, K2-11, K5-25; the second pass matched them).
- JSON: the diff is exactly the log's table plus four bookkeeping additions the table does not
  list: `members_excluded_e1` on each of the 8 clusters, `e1_ruling` on 12 members, `totals.note`,
  and the top-level `e1_patch`. One label is wrong: exposure_table[K4 gas] (K4-ngrev-01 removed,
  trials 6 to 5) is the R-06 carry only, not U6; the log says "U6 (and R-06 carried)". The change
  itself is right (K4-ngrev-01 was excluded in E.0 Task 8; the exposure row was stale).
- Decision coverage: U1 (D-02..D-05, K7-00), U2 (D-01, D-02, D-03, D-05, D-15, D-16, D-21, D-22,
  D-28, D-30, K5-*, A-01, JSON), U3 (D-27, K1-00, K2-00, K8-00), U4 (D-10, D-19, D-25, D-26, D-28,
  D-29, D-31, D-33), U5 (D-32), U6 (D-09, D-12, D-13, D-23, D-24, D-25, D-26, D-34, N-01, every
  K#-01/02/03, K8-04, JSON), U7 (D-06, D-20, K3-00), U8 (D-07, D-08, D-11, D-14, D-17, D-18, D-19),
  U9 (K5-00, K5-14, K5-23, K5-31, K5-32, K5-33, K2-10, K2-11), recount (D-13, A-01, banners, JSON).
  U8's "no edit needed" for D9, D10, D11, D14 checked: a "User decides" line exists only in D1 to
  D8 and D15 (`awk` over the section headings). U9's "K3 CP2 note not found" checked: the K3-cp2-01
  entry has no "latest-entry", "no latest", "unbounded" or "Note for the lead" text.
- Lead glosses that go beyond the decision text, each checked against the draft: D-05 "no exposure
  failed (a) for lack of a figure, since the ADV exists for all 50 products" (reports/
  stage_e0_liquidity.json: `adv` present for all 50); D-07 "as drafted, an exposure with no
  candidate is not traded" (D2 rule bullet: "An exposure with no candidate ... is not traded in
  Stage E"); D-17 "CP1 in the (a) form only" (D6 CP1 row: "(b) is not ported as a separate
  member"). All three are accurate readings of the draft, not new rules.
- docs/DECISIONS.md: U1 to U9 are quoted in substance. Two departures: the U4 item drops the
  prompt's "30" (consistent with F-1); the U2 item carries a "Count note" written by the lead
  inside the user's decision text (lines 65-67), see FA-07.
- The "FROZEN by Stage E.1" header is absent from both docs, as Task 1 requires (added in Task 4).

Result. No silent edit and no missed decision. Log incompleteness on the JSON bookkeeping fields
and one mislabel (FA-12, NOTE); the DECISIONS.md count note (FA-07, SHOULD FIX).

### Check 2: platinum is gone as a traded exposure, nothing depends on it

What I did. `grep -n -i "platinum\|\bPL\b"` over all 13 files; every hit classified as struck,
bracketed, descriptive under a banner, or still binding. Read the K5 residual passages in context.
Checked the catalog JSON for active members with a platinum exposure and the purchase path for PL.

Evidence.
- Design: D1 row OUT with the reason (line 108); result line 31 exposures, 4 out (119-125); "Platinum
  may not serve as a signal leg either (U2)" (128); D6 session row struck (397); D9.11 note (571);
  D9.12 encoded list "GC, SI or HG (~~or PL~~: OUT, U2)" (578); D13 notes (727-736, 748). Topstep's
  quoted text in D9.11/D9.12 (565, 574) is kept as the source, marked so at 571-572. D2, D8 and D10
  name no platinum contract (grep over lines 144-205, 429-476, 615-655: no hit), so the lead's "no
  edit in D2" is right; D13's list is edited.
- docs/NULL_CRITERIA_E.md, K1 to K4, K6 to K8: no hit at all.
- JSON: no active member carries "platinum"; the exposure_table platinum row is gone; the only
  strings left are the four `e1_ruling` notes and K5-preauc-01's E.0 `lead_ruling` (removal).
- K5: every statement that made platinum a traded exposure is struck with a [U2] note (lines 79,
  80, 132, 289, 310, 342, 362, 395, 418, 717, 746-747, 764, 1015-1017, 1021, 1023) and the banner at
  line 5 declares the descriptive facts non-binding. Residuals the banner's carve-out ("auction
  clock times, fees, Topstep's quoted text, question texts") does not cover:
  - K5-preauc-01 "Data needed: ohlcv-1m of the gold, silver and platinum vehicles over 03:00-07:00
    CT" (K5 line 533; assembled 4886). Stale since the E.0 01:47 removal of the platinum leg, and
    after U2 it contradicts D1's "nothing in the catalog needs it": it states a data dependency on
    PL bars. FA-02.
  - K5-ovr-01 "Data needed: ohlcv-1m of all four admitted vehicles" (K5 802; assembled 5155):
    three after U2. FA-03.
  - Descriptive residuals that bind nothing: header D1 row still lists "platinum PL 22,360" among
    admissible vehicles after the U2 note (81); "every platinum trial carries that flag" (86-87);
    C5 clock (116, 120); constraint lines "SI, HG and PL may be suspended" (334), "gold, silver and
    platinum entries start at 07:36" (386), "Platinum may be suspended" (529, 800), C14 remark
    (531), sizing "GC, SI, PL 1" (502), reference-set count "64 of 80 for copper and platinum"
    (754), D9.5a fill times (792, 797), section 7 item 9(f). FA-11.
- Purchase path: data/pull_universe.py REFUSED_ROOTS = ("PL", "MET", "NKD", "6M", "ES", "MES");
  STEP1_ROOTS is 45 contracts. Nothing in the frozen set or the code depends on PL as a leg or
  signal.

Result. PL is out everywhere as a traded exposure and as a leg. Two "Data needed" lines still
name it or count it (SHOULD FIX); the rest is descriptive under the banner (NOTE).

### Check 3: the eight ML entries and D15

What I did. Counted the EXCLUDED banners and their reason string; read the D15 banner; grepped
the design (outside D15), the criteria and the cluster files for any rule that still requires an
ML member or an ML grid; listed every unstruck `| K#-ml-01` table row.

Evidence.
- Eight banners, one per K#-ml-01 heading, in the eight cluster files and eight in the assembled
  copy, each reading "[EXCLUDED: superseded by the Stage E ML route (user decision 2026-09-24,
  U6). ... adds 0 trials ...]"; the text of each entry stays visible below it. JSON: all eight
  `status: excluded_superseded_ml_route`, `trials: 0`, `e1_ruling: "excluded: superseded by the
  Stage E ML route (user decision 2026-09-24, U6)"`.
- D15 (design line 792-800): SUPERSEDED banner, the exact reason string, the pointer to
  docs/STAGE_E_ML_DESIGN.md, the user's purpose statement, "The text below stays for the record".
  The pointed-to file does not exist yet (Task 9 writes it later in E.1); the banner says it is a
  draft for the user's review, frozen in E.2. FA-15 (NOTE).
- Rules that required an ML member, all neutralized: D4 research-window use "ML tuning" struck
  (246-247); D5 Tier A sentence "[U6: superseded; the catalog has no ML member]" (302-303) and the
  accounting clause struck (316-317); D9.9 note (588-589); D11.7 struck (677-679); D12 session 3
  and sessions 4-17 struck (697-698); NULL_CRITERIA_E section 2 bullet superseded (73-76). No other
  "ML member" or "D15" rule text remains in D1 to D14 (grep lines 19, 246, 300-303, 316-326, 587,
  677, 697-698, 732 only).
- Cluster files: the section-6 ML rows are struck in K1 to K7 (K1-02..K7-02) and the "ML grid"
  header rows in all eight (K1-03..K8-03, K2-03). K8's trial table is in its section 5 (line
  829), and its K8-ml-01 row (line 837; assembled 8474) is NOT struck: "| K8-ml-01 | CAD (K3) |
  ... | 1 (48 in screening accounting) | ...". The K8 banner's "section 6 totals below are
  superseded" does not name section 5 (K8's section 6 is "Questions for the lead"). This is the
  only unstruck ML trial row in the frozen set. FA-01.
- Header "Members" rows still read "+ 1 ML member" in K1, K2, K3, K4, K6, K7 and K8 ("4 = 3 new +
  1 ML member"); only K5's got an inline note (K5-13). The banners ("Header and section 6 totals
  below are superseded where they differ") cover them. K5 section 7 item 7 still says K5-ml-01
  "needs silver bars (KF6) ... which E.2 must add to D13's purchase"; K1's header still says MES
  bars "appear only as a signal leg in K1-ml-01". Stale, non-binding. FA-10.
- Non-ML members citing D15: K4-ovr-01 (K4 771), K5-ovr-01 (K5 771), K6-ovr-01 (K6 804, an
  excluded member) and K8-flight-01 (K8 319) cite D15.4 B4 as the origin of their fixed literal 20
  trailing dates; the common-convention sections cite D15.3 for the engine's next-open fill. The
  literals are in the member text; D15 stays visible; no member reads a D15 rule at run time. F-6
  confirmed. FA-16.

Result. Excluded with the stated reason, text visible, D15 banner and pointer in place. One
unstruck K8 table row (SHOULD FIX); stale counts and notes under the banners (NOTE).

### Check 4: the recount, and finding F-1

What I did. Independent recount from reports/stage_e0_catalog.json, then cross-checks against the
cluster files' trial tables (parsed for K1 to K7; K8's section 5 table read by hand), the cluster
banners, the assembled header and D5. Then counted D1's IN rows at 01b259a and now.

Script (scratchpad/check4_recount.py, the recount core):

```python
import json
from collections import defaultdict
d = json.load(open("reports/stage_e0_catalog.json"))
per = defaultdict(lambda: dict(m=0, t=0, pt=0, nt=0))
for m in d["members"]:
    if m["status"] != "active": continue
    c = per[m["cluster"]]; c["m"] += 1; c["t"] += m["trials"]
    c["pt" if m["type"] == "port" else "nt"] += m["trials"]
for k in sorted(per): print(k, per[k])
tm = sum(c["m"] for c in per.values()); tt = sum(c["t"] for c in per.values())
print("members", tm, "trials", tt, "=", sum(c["pt"] for c in per.values()), "port +",
      sum(c["nt"] for c in per.values()), "new; N =", 58 + tt)
```

Output (abridged):

```
members in JSON: 64; status: active 53, excluded_superseded_ml_route 8, excluded_by_lead 3
type (active): new 32, port 21
K1 | 5 (2 new + 3 port) | 11 (9 port + 2 new)   JSON clusters[]: 5 / 11  OK
K2 | 8 (5+3) | 44 (18+26)  OK      K3 | 9 (6+3) | 31 (21+10)  OK
K4 | 8 (5+3) | 19 (12+7)   OK      K5 | 7 (4+3) | 16 (9+7)    OK
K6 | 7 (4+3) | 27 (21+6)   OK      K7 | 6 (3+3) | 6 (3+3)     OK
K8 | 3 (3+0) | 4 (0+4)     OK
TOTAL members 53, trials 158 = 93 port + 65 new; independent projected N = 58 + 158 = 216
active members with 'platinum' in exposures: []; active members of type ml: []
exposure_table trials sum: 158 (K8 gold = 2 is K8-flight-01's exit grid, 2 trials on 1 exposure)
section-6 tables: K1 11, K2 44, K3 31, K4 19, K5 16, K6 27, K7 6 (active rows = JSON active);
K8 (section 5, by hand): K8-flight-01 H30 1 + HEOD 1, K8-oilcad-01 1, K8-wkndbtc-01 1 = 4
banners: K1 5/11, K2 8/44, K3 9/31, K4 8/19, K5 7/16, K6 7/27, K7 6/6, K8 3/4
```

Evidence. My figures equal the lead's in every cell: the assembled header table (A-01), the D5
recount bullet (D-13), the eight banners, JSON clusters[], totals and projected_N. Arithmetic:
61 - 8 = 53 members; 170 - 8 (ML) - 4 (platinum on K5-cp1/cp2/cp3/ovr) = 158; 93 port trials
= 3 x 31 traded exposures; 21 port members = 3 x 7 clusters; N = 58 + 158 = 216.

F-1 (D1 has 32 IN rows before U2, 31 after; the prompt says 30). Verified: `grep -c "| IN |"` on
the D1 table gives 32 at 01b259a (K1 3, K2 6, K3 7, K4 4, K5 4, K6 7, K7 1) and 31 now; the table
has 36 exposure rows (32 IN + NKD, S&P leg only, 6M, MET); E.0's own JSON carried 96 port trials
= 3 x 32. So E.0's "31 traded exposures" was a miscount and the prompt's "30" is that miscount
minus one. The lead is right. Handling: the prompt's failure path is for a decision that conflicts
with a frozen rule or needs a member change. U2 (remove PL) is applied in full; "(30 traded
exposures)" is the user's arithmetic on E.0's figure, not a decision to remove a second exposure,
and no exposure other than PL is named anywhere in U1 to U9. Writing 30 would have misstated the
table; writing 31 with the count note in D1 (D-02), the D6 count note (D-16), the DECISIONS.md
count note and F-1 for the user is the right handling, and leaving the number blank would have
left D1's result line unusable by the purchase. Two things follow: the user has not yet seen
"31", so the return document must put F-1 in front of the user before the number is relied on;
and data/pull_universe.py's docstring (line 6) says "45 admissible contracts of the 30 traded
exposures" while the frozen design says 31 (the contract set, 45, is the same). FA-08.

Result. The recount is right: 53 members, 158 trials (93 port + 65 new), projected N = 216.

### Check 5: D4, D12 and D13 agree on the staged purchase and the order

What I did. Read the three sections in full in the working tree and compared each statement with
U3 and U4; grepped the design for leftover "E.2b", "second purchase" and ML-per-cluster text; re-
summed the D13 dollar figures from the ledger.

Evidence.
- D4 (250-256): holdout-2 "~~bought in E.1~~ bought per cluster in step 2 (D13), just before that
  cluster's confirmation session [U4], and sealed on arrival exactly as MES's was"; holdout-1 not
  bought (U8). Research window use no longer names ML tuning.
- D12 (695-698): session 1 buys "the research window of every admissible contract and the mbp-1
  sample (D13 step 1)"; session 3's "second purchase" struck with "[U4: step 2 is bought per
  cluster, just before that cluster's confirmation session]"; sessions 4-17: "Confirmation: [U4:
  first the cluster's step 2 purchase, its holdout-2 chunks sealed on arrival;] ...". Cluster
  order (700-704): K2, K4, K5, K3, K6, K7, then K1 only if the user decides after K7, K8 last, K1's
  members stay in the frozen catalog. Matches U3 word for word in substance. The E.0 order is
  struck and declared superseded.
- D13 (727-736): step 1 in E.1 = research window of every admissible contract of the 31 exposures
  (45 contracts) plus the mbp-1 sample on the five fixed dates, no tbbo; step 2 = option (b), each
  cluster's 2019-05..2025-03 history of its chosen vehicles bought just before that cluster's
  confirmation session, holdout-2 chunks sealed on arrival; the ML route's data needs may pull
  some step 2 purchases forward. Table step 2 row: "~~E.2b~~ per cluster, before its confirmation
  session (U4)" (743). Caps: "[U4: step 2 is per cluster, so each cluster's step 2 session is
  capped at its own quote plus 10%]" (753-754). Alternatives: "(a) and (b) chosen; (c) not" (769).
  D8's "User decides" carries "[U8 and U4: mbp-1 only, the five dates; no tbbo is bought]" (474).
- Leftover text: the only remaining "E.2b" mentions are the struck one, the caps sentence's
  "E.2b: the chosen vehicles' quote plus 10%" now qualified by the U4 note, and the alternatives
  paragraph (770), which is the option (b) text itself. Consistent.
- One over-broad strike: D12's "The E.0 proposal that follows is superseded:" (703-704) precedes a
  paragraph that also holds still-valid sentences ("About 20 sessions in total", the independence
  of cluster sessions, the thin-cluster remark). Harmless. FA-13.
- Dollar figures (scratchpad/check5_ledger.py over the 5,050 quote lines; 158 failed quotes with
  `quoted_usd: null` skipped): the research window is 15 monthly ohlcv-1m chunks per root, 50
  roots; E.0 also quoted 5 intraday ohlcv-1m "set C" coverage windows per root ($0.31 in all).
  Admissible roots: 46 with PL, 45 without.
  - Monthly chunks only: 46 roots $58.42 (= E.0's D13 table), 45 roots $57.00, PL $1.41.
  - Monthly plus set C: 46 roots $58.70, 45 roots $57.28. The lead's "$57.28" (D13 line 734, STATE
    S-1) therefore includes the 225 set-C coverage quotes, which are not step 1 requests (their
    minutes lie inside the monthly chunks). The like-for-like figure against E.0's $58.42 is
    $57.00. Same for K5: monthly-only without PL $8.95 (the note says $8.99). Cents.
  - mbp-1: 46 roots $46.35, 45 roots $45.95, PL $0.40. Matches the note.
  - Step 2: the lead subtracted PL's history ($6.24, confirmed) from E.0's $170.39-195.55 to get
    $164.15-189.31. A fresh per-exposure min/max re-sum from the ledger gives $170.95-195.55 with
    PL and $164.71-189.31 without: E.0's K4 low end ($15.65) is $0.56 under the ledger ($16.21:
    MCL 4.60 + MNG 0.84 + RB 5.29 + HO 5.49). Cents; the per-cluster fresh quote governs at each
    step 2 session.
  - The two quotes above the $3.00 request cap: MNQ mbp-1 2026-02-11 $4.14 and 2025-11-12 $3.41,
    the only two of 5,050. See FA-05.
  FA-09 (NOTE) for the figures.

Result. D4, D12 and D13 agree with each other and with U3 and U4. The re-summed dollar figures in
the D13 note are off by cents for a stated reason; the fresh quote governs.

### Check 6: no member rule, parameter, threshold or window changed beyond the decisions

What I did. Read every hunk of the eight cluster-file diffs; ran the check-1 coverage script (every
changed line is a logged entry); compared each cluster section of the assembled catalog with its
cluster file (a script cut the sections at the `# Stage E.0 hypothesis catalog, cluster K#`
headings and diffed).

Evidence.
- Cluster-file hunks are exactly: the title banners (K#-00), the EXCLUDED banners (K#-01), the ML
  grid rows (K#-03, K2-03), the section-6 ML rows (K1-02..K7-02), K8's header trials row (K8-04),
  K5's platinum strikes (K5-10..K5-12, K5-15..K5-21, K5-24..K5-30, K5-34), K5's count notes
  (K5-13, K5-14, K5-22, K5-31, K5-32), K5-preauc-01's trials 3 to 2 (K5-23, K5-33; the JSON has
  carried 2 since E.0 Task 8 and the 01:47 ruling), and K2's two superseded-note brackets (K2-10,
  K2-11). K5-15 rewrote the struck C6 PL row's last two cells ("0 (Topstep F12.1c)", "—") inside
  the strike. No signal, threshold, window, clock, sizing, order type, exit or data field of any
  active member changed.
- Assembled copy versus cluster files: identical except the assembler's "---" and "# Cluster K#"
  separators, and one pre-existing gap: the K5, K6, K7 and K8 sections of
  reports/stage_e0_catalog.md lack the E.0 lead-ruling line "[Lead ruling on the Task 6 review,
  06:20 PDT 2026-09-24: R-10: the "release residual" paragraph of C13 is superseded ...]" that the
  four cluster files carry (K5 267, K6 214, K7 229, K8 230). At 01b259a the assembled copy already
  carried that line only in its K4 section (base line 3416); E.1 did not introduce the gap. The
  assembled catalog is a frozen file that a later session may read on its own. FA-04.

Result. No member changed beyond U2 and U9. One pre-existing copy inconsistency (SHOULD FIX).

### Check 7: U5 and U7 are recorded as the decision text says

What I did. Compared D-32 and D-06/D-20 with the prompt's U5 and U7 text; read data/config.py.

Evidence.
- U5, D13 (761-766): "acct-2: $125.00 of credit, used only by this repository; every Stage E
  purchase from E.1 on draws on it. acct-1: the old account, shared with the archived
  MLCryptoEngine, $91.59 spent ...; it is closed to new spend by this program." Both accounts
  recorded, as U5 says. The sentence "data/config.py carries both accounts with their caps
  (acct-1 $120.00 with the external MLCryptoEngine ledger, acct-2 $125.00 with none), and the spend
  gate sums spend per account (Stage E.1 Task 5)" is true of the working tree (config.py lines
  58-98: ACCOUNTS registry, ACTIVE_ACCOUNT = acct-2, E1_REQUEST_CAP_USD = 3.00), but that code is
  committed in the Task 5 commit after the freeze commit. FA-15.
- U7, D2 (176-180) and D9.8 (557-560): "not D2 candidates until Topstep answers the user's support
  email (drafted 2026-09-24, not yet answered)"; "If Topstep clears them before a cluster's
  screening session, a vehicle amendment may be written before that session reads any
  research-window bar, and the amendment is logged in docs/DECISIONS.md". The K3 banner repeats
  it. Matches U7.

Result. Both recorded as decided.

### Check 8: the unapplied items F-1 to F-7

- F-1 (count): correctly handled (check 4). NOTE, with the two follow-ups in FA-08.
- F-2 (D13's "largest single request ... about $2.7"): verified false from the ledger (MNQ mbp-1
  $4.14 and $3.41; the largest monthly ohlcv-1m chunk figure of about $0.12 is right). The lead
  left it and decided in STATE S-2 that the purchase path splits any over-cap request into
  contiguous time pieces, each quoted and gated, the cap not raised (config.py line 92 says the
  same). Leaving the sentence means the frozen D13 states a false fact that its own cap rule
  rests on, and the split handling, which is the only way to meet both the prompt's $3.00 cap and
  its "mbp-1 for every admissible contract", exists nowhere in a frozen file. A bracketed factual
  note at D13 line 754 changes no rule (the cap stays $3.00) and is the kind of fix Task 4 allows
  for a SHOULD FIX finding. The split handling itself is a lead decision the user has not seen;
  it belongs in the rulings and the return document. FA-05.
- F-3 (R-04's "E.1 records every member's source windows before hashing"): not done, and the
  frozen docs/NULL_CRITERIA_E.md line 83 says E.1 does it. The fallback in the same sentence ("a
  member whose source window is not recorded is treated as source-overlap") keeps the program
  well defined, and the user accepted D7 with the source-overlap rule (U8). But the consequence
  is larger than "conservative" suggests: only 16 of the 53 active members carry a SOURCE-OVERLAP
  label with a recorded window (JSON `source_overlap`), and by a heuristic grep only about 20 of
  the 64 member entries carry any source-window text at all, so roughly 34 active members would
  be source-overlap by default, which bars an edge on them from even being discussed for a final
  read without a registered holdout read. That is a program-level effect the freeze would lock in
  without the user having seen it. Two ways to make the frozen text true: record the windows now
  as bracketed lead notes (E.0 Task 8 added them to 15 entries that way; the same mechanism, no
  rule changes), or add a bracketed note at line 83 that E.1 did not record them and the fallback
  applies, and list the affected members for the user. Either is the lead's ruling. FA-06.
- F-4 and F-7 (R-24, K4-ovr-01 and K5-ovr-01 one rule text): checked myself by extracting both
  entries' rule bullets. Same signal r(t) over [t-60, t); same reference set (the same clock times
  on the 20 most recent earlier dates, 80% of the possible values required, P10/P90 with
  `np.percentile(..., method="linear")`); same warm-up (first 20 eligible dates); same entry
  (intent at t-1, fill at the open of t; BUY at <= P10, SELL at >= P90); same exit (intent at
  t+58, fill at t+59); 59-minute hold; one position at a time. Differences are each cluster's
  convention names (K4: "full sessions in EC-CAL" and the C10 denominator guard; K5: "eligible
  trade dates (C4)") and the decision clocks (K4 fixed 09:00-13:00; K5 O+60k while t <= C). R-24
  asked for "one identical rule text"; the two are equivalent, not verbatim. Consistent. FA-14.
- F-5 (R-15, K2-aucpost-01's 5-minute lag on an unquoted passage): correctly carried to the user;
  no decision covers it. NOTE (FA-16).
- F-6 (D15 references in non-ML members): confirmed at K4 771, K5 771, K6 804, K8 319 and the
  common conventions; the literals are fixed in the member text. Correctly left. NOTE (FA-16).

### Anything else that would make the frozen files misstate the decisions

- The DECISIONS.md entry embeds the lead's count note inside the user's U2 text (FA-07).
- The D15 banner and D4/D5/D9/D11/D12/D13 notes point to docs/STAGE_E_ML_DESIGN.md, which does not
  exist at freeze time (Task 9 writes it during the purchase). The banner says it is a draft for
  the user's review, frozen in E.2, so the pointer is a declared forward reference (FA-15).
- Nothing else found that misstates U1 to U9.

### Findings

| ID | Grade | File and line | Finding | Suggested fix |
|---|---|---|---|---|
| FA-01 | SHOULD FIX | reports/stage_e0_catalog_K8.md 837; reports/stage_e0_catalog.md 8474 | K8's trial table (section 5) still carries `\| K8-ml-01 \| ... \| 1 (48 in screening accounting) \|` unstruck; K1 to K7's ML rows were struck (K#-02) and the K8 banner names only "section 6 totals" (K8's section 6 is questions). The only unstruck ML trial row in the frozen set; contradicts the banner, the JSON (0) and D5. | Strike the row as in K1-02..K7-02: `~~K8-ml-01~~ [excluded, U6] ... 0 (E.0: 1)`; log it as K8-02 (U6) in both copies. |
| FA-02 | SHOULD FIX | reports/stage_e0_catalog_K5.md 533; reports/stage_e0_catalog.md 4886 | K5-preauc-01 "Data needed: ohlcv-1m of the gold, silver and platinum vehicles" states a data dependency on PL after U2 (and after E.0's own 01:47 removal of the platinum leg); the banner's carve-out does not cover a data-needed line. | `... of the gold and silver ~~and platinum~~ [U2: platinum OUT] vehicles ...`; log under U2. |
| FA-03 | SHOULD FIX | reports/stage_e0_catalog_K5.md 802; reports/stage_e0_catalog.md 5155 | K5-ovr-01 "Data needed: ohlcv-1m of all four admitted vehicles" (three after U2). | `all ~~four~~ three [U2] admitted vehicles`; log under U2. |
| FA-04 | SHOULD FIX | reports/stage_e0_catalog.md sections K5 (from 4356), K6 (5444), K7 (6611), K8 (7640); the lines exist in K5 267, K6 214, K7 229, K8 230 | The assembled catalog's K5 to K8 sections lack the E.0 R-10 lead-ruling line ("release residual" paragraph of C13 superseded) that the four cluster files carry; pre-existing at 01b259a (the assembled copy has it only in K4). Two frozen copies disagree on a ruling a later session applies. | Insert the four missing lines into the assembled copy at the positions the cluster files have them, and log the copy fix (E.0 ruling R-10 carried; no decision). |
| FA-05 | SHOULD FIX | docs/STAGE_E_DESIGN.md 754 (D13 caps) | "the largest single request is one mbp-1 day of MNQ, about $2.7" is false: the ledger's E.0 quotes are MNQ mbp-1 2026-02-11 $4.14 and 2025-11-12 $3.41, above the $3.00 request cap; the lead's handling (split over-cap requests into contiguous time pieces, cap not raised; STATE S-2, config.py 92) is in no frozen file. | Bracketed note after the sentence: "[E.1, 2026-09-24: the ledger's E.0 quotes give MNQ mbp-1 2026-02-11 $4.14 and 2025-11-12 $3.41, above the cap; the cap is not raised; the purchase path splits such a request into contiguous time pieces, each quoted and gated on its own (STATE S-2).]" Put the split handling before the user in the rulings and the return document. |
| FA-06 | SHOULD FIX | docs/NULL_CRITERIA_E.md 83; reports/stage_e0_review_rulings.md 17 | The frozen criteria say "E.1 records every member's source windows before hashing"; E.1 did not (F-3). By the fallback, every active member without a recorded window (about 34 of 53; 16 are labelled) becomes source-overlap, which bars an edge on it from a final-read discussion without a registered holdout read. The user has not seen this consequence. | Lead's ruling, one of: (a) record the windows now as bracketed lead notes (the E.0 Task 8 mechanism, no rule change), or (b) add "[E.1, 2026-09-24: not done in E.1; every member without a recorded window is source-overlap by this rule until a registered amendment records it]" and list the affected members for the user. |
| FA-07 | SHOULD FIX | docs/DECISIONS.md 65-67 | The lead's count note ("D1's table has 31 traded exposures after U2; E.0's '31' ... the stage prompt's '30' repeats it") sits inside the U2 item, i.e. inside the user's decision text. | Move it out of U2 as its own line: "Lead's count note (F-1, for the user): ...". |
| FA-08 | NOTE | docs/STAGE_E_DESIGN.md 119-125 (D1), 401-402 (D6); reports/stage_e1_changes.md F-1; data/pull_universe.py 6 | F-1 is right (32 IN rows at 01b259a, 31 now; E.0's JSON had 96 = 3 x 32 port trials) and writing 31 with the count notes was the right handling under the failure-path rule (no decision names a second exposure). The user has not seen "31"; pull_universe.py's docstring says "30 traded exposures" (same 45 contracts). | Put F-1 first in the return document; align the docstring in the Task 5 commit. |
| FA-09 | NOTE | docs/STAGE_E_DESIGN.md 733-735, 748 (D13 note) | Re-summed figures: "$57.28" and K5 "$8.99" include E.0's 225 intraday set-C coverage quotes ($0.28), not step 1 requests; monthly-chunk sums are $57.00 (45 roots, PL $1.41) and K5 $8.95. Step 2 "$164.15-189.31" is E.0's range minus PL; a fresh per-exposure re-sum gives $164.71-189.31 (E.0's K4 low end was $0.56 under). mbp-1 $45.95 confirmed. | Optional: correct the cents or state the basis; the fresh Task 6 quote governs. |
| FA-10 | NOTE | K1 85, K2 33, K3 69, K4 67, K6 62, K7 93, K8 77 (header "Members" rows); K5 1060-1061 (s7 item 7); K1 84; K5 1075 (s7 item 9(f)) | Header rows still count "+ 1 ML member" (K5's alone got an inline note); stale ML notes (silver bars for K5-ml-01 "to add to D13's purchase"; MES leg "only in K1-ml-01"; K5-ml-01 coverage check). Covered by the banners' "superseded where they differ". | None required; an inline "[E.1: ... K#-ml-01 excluded, U6]" as in K5-13 would make the seven headers uniform. |
| FA-11 | NOTE | reports/stage_e0_catalog_K5.md 81, 86-87, 116, 120, 334, 386, 502, 529, 531, 754, 792, 797, 800 | Descriptive platinum residuals (admissible-vehicle listing in the header D1 row, "every platinum trial carries that flag", clock times, suspension remarks, sizing and reference-count mentions). Bind nothing under the line-5 banner. | None required. |
| FA-12 | NOTE | reports/stage_e1_changes.md JSON table (1836-1870) | The table omits four bookkeeping fields the JSON gained (`members_excluded_e1` x8, `e1_ruling` x12, `totals.note`, `e1_patch`); exposure_table[K4 gas] is the R-06 carry only (K4-ngrev-01 removed) but is labelled "U6 (and R-06 carried)". | Add four rows and relabel the gas row. |
| FA-13 | NOTE | docs/STAGE_E_DESIGN.md 703-714 (D12) | "The E.0 proposal that follows is superseded:" strikes a paragraph that also holds still-valid sentences (about 20 sessions; cluster sessions independent; thin clusters). | Optional: narrow the strike to the order sentence. |
| FA-14 | NOTE | K4-ovr-01 (K4 ~740-790), K5-ovr-01 (K5 ~714-803) | R-24 asked for "one identical rule text"; the two entries are equivalent (same signal, reference construction, cuts, entry, exit, hold) but not verbatim (cluster convention names, decision clocks). F-7 confirmed. | None required; the rulings may say "equivalent, not verbatim". |
| FA-15 | NOTE | docs/STAGE_E_DESIGN.md 763-766 (D13 U5 sentence), 792-800 (D15 banner) and the other STAGE_E_ML_DESIGN.md pointers; docs/DECISIONS.md 57-58 | The frozen design describes data/config.py's account registry, which is committed in the Task 5 commit after the freeze; the D15 banner and five notes point to docs/STAGE_E_ML_DESIGN.md, which does not exist at hashing time (Task 9); DECISIONS.md forward-references reports/stage_e1_freeze.json. All declared forward references. | State in the rulings that the ML design file and the account code post-date the manifest. |
| FA-16 | NOTE | reports/stage_e1_changes.md F-5, F-6 | F-5 (R-15, K2-aucpost-01's unquoted 5-minute lag) correctly carried to the user; F-6 (D15.4 B4 cited for fixed literals at K4 771, K5 771, K6 804, K8 319) correctly left. | None. |

Counts: BLOCKING 0; SHOULD FIX 7 (FA-01 to FA-07); NOTE 9 (FA-08 to FA-16).

### Verdict

**READY WITH FIXES.** No frozen file misstates a user decision, contradicts another frozen file on
a decision, or changes a member beyond U2 and U9. Seven text fixes before hashing: one unstruck
K8 ML trial row (FA-01), two K5 "Data needed" lines that still name or count platinum (FA-02,
FA-03), the assembled catalog's missing R-10 ruling lines in K5 to K8 (FA-04), D13's false
largest-request figure and the unrecorded split handling (FA-05), the criteria's unfulfilled "E.1
records every member's source windows" (FA-06, the one with a program-level consequence the user
should see), and the lead's count note inside the user's U2 text in DECISIONS.md (FA-07).

Not checked: the research files, source registry, partition, topstep, liquidity, quotes and review
files that Task 4 also hashes (outside this brief); the E.0 per-cluster figures beyond the re-sum
above; whether the Task 5 code's 45-root set equals the design's 45 admissible contracts root by
root (read the count and the refusals only).

## Part 2

(reserved for the spend recomputation, to be written when the auditor is resumed)
