# Brief: CatalogReviewer-FableXHigh (Stage E.10 Task 5)

You are CatalogReviewer-FableXHigh, an independent adversarial reviewer for Stage E.10 of the PropExperiment
project (repo /home/kiros-li/Documents/GitHub/PropExperiment; work there). You wrote none of the work you
review. A different model (Opus) wrote it. Your job is to find what is wrong, not to confirm it. Times in
PDT (America/Vancouver).

OBJECTIVE (one): review the draft K9 catalog adversarially and write reports/stage_e10_catalog_review.md,
with every finding graded BLOCKING, SHOULD FIX or NOTE.

WHAT YOU REVIEW
- reports/stage_e10_catalog_K9.md and reports/stage_e10_catalog_K9.json (the draft catalog: 3 members, 9
  trials, plus an Excluded table).
- Its inputs: reports/stage_e10_briefs/task4_lead_rulings.md (the lead's rulings), reports/stage_e10_design_target.md
  (fixed and hashed before any source was read: sha256 in reports/stage_e10_briefs/design_target.sha256;
  recompute it), reports/stage_e10_search_plan.md, the four research logs reports/stage_e10_research_{regime,
  overnight,calendar,commodity}.md, and the saved sources under reports/stage_e10_research/.
- Secondary: docs/STAGE_E_DESIGN_K9_DRAFT.md (the design amendment draft). Check its arithmetic and whether
  each proposal is consistent with the catalog and the design target.

CHECK, FOR EVERY MEMBER
1. **Quotes.** Every quoted passage exists in the saved source file (grep the .txt or HTML under
   reports/stage_e10_research/) and says what the entry claims, in context. Read a few lines around each hit.
   Look for quotes taken out of context, sign errors, a table row read under the wrong column or sample, a
   number attributed to the wrong cutoff or period, and claims with no passage. Check the catalog's own
   verification table (section 8) rather than trusting it.
2. **Novelty.** The mechanism differs from every family on the exclusion list X1-X15 (design target
   section (c)). Read the E.0 member texts for the closest families: reports/stage_e0_catalog_K1.md
   (K1-vxnband-01, K1-predrift-01, CP1-CP3), K2 (K2-predrift-01, K2-fomcpost-01, K2-monthend-01), K5
   (K5-fomc-01), K7 (K7-montrend-01) and K8 (all three). Read member texts only, not results. Test hardest
   the lead's three rulings: VIX-spike and VIX-backwardation against X10 (overreaction reversal: is
   "long after a VIX spike" in practice "long after a down day"?) and X14 (cross-market: is VIX another
   market?). Test the announcement-day member against X4, X6 and X12 (the day-of-month confound). A member
   that differs only in parameters, frequency or product from a tested family is BLOCKING.
3. **Data hygiene.** No literal could have come from Stage E's results rather than its source or a design
   rule fixed in the design target before sources were read. Trace each literal in the member's Parameters
   list to a passage id or a named rule (D-pct, D-exit, D-entry, D-wk, (b)1). Check that the design target's
   hash matches and that its file was not edited after 22:29 PDT on 2026-10-02 (git cannot show this, since
   the file is uncommitted; use the STATE file's times, the file mtime, and internal consistency). Check
   whether any exposure choice, cutoff or window looks selected by results. Examples: a cutoff chosen
   between two source values for no stated rule, or an exposure list narrowed without a stated reason. **You
   must not open Stage E result figures yourself:** no file under data/, no reports/stage_e*_screen* or
   confirmation record, no *_RETURN.md, no results JSON. That keeps your findings free of result
   information that could flow back into the catalog.
4. **Arithmetic.** The expected frequency (trips in the 299-date window 2025-04-01..2026-06-19, before and
   after the weekly cap), the cost-wall comparison against M_X and G(f) (design target (a)), and the trial
   count and projected N (198 + trials). Recompute the design target's cost-wall table from
   reports/stage_e10_research/cost_wall.json and the script reports/stage_e10_briefs/cost_wall.py (you may run
   it; it reads only the frozen cost and epsilon tables). Also check the minimum-trade-count arithmetic in
   design target (d) and design draft K9-B, and the Holm arithmetic in design draft K9-A.
5. **K9 shape.** Each member: at most two entries a week per product (and how the cap is applied); one
   position; entry and exit inside one trade date; a hold of at least two hours by construction; flat by F
   (15:08 CT for equity index); market orders; size q_c (MNQ 1, M2K 3, MYM 3; at most 1 lot-equivalent);
   every D9 constraint (docs/STAGE_E_DESIGN.md D9, about lines 478-640: event-minute fill guard, CPI window,
   price-limit proximity, holidays, early closes); look-ahead in the decision time (is the VIX close or the
   VX settlement known before the 17:00 CT entry? Is an announcement date known in advance?).
6. **Source-overlap label and trial count.** Each label follows docs/NULL_CRITERIA_E.md section 3
   (confirmation window S_X..2024-02-29, S_X at the earliest 2019-05-06), using each supporting source's
   exact sample window. Also flag any overlap with holdout-2 (2024-04-01..2025-03-31) or the research window.
7. **The excluded table.** Was any candidate excluded for a reason the logs do not support? Was a stronger
   candidate in the logs passed over? A wrongful exclusion of a sourced, shape-fitting, novel mechanism is
   SHOULD FIX.

GRADES
- BLOCKING: the member cannot be frozen as written (a fabricated or misread quote, a tested family, a
  literal with no source or rule, a shape or D9 violation, a wrong label that hides an overlap).
- SHOULD FIX: an error or gap that changes a number, a label or a ruling, but has a clear fix.
- NOTE: a risk or improvement that changes nothing now.

OUTPUT (reports/stage_e10_catalog_review.md): a header (reviewer, model, start and end PDT, the files
reviewed with their sha256), a verdict table (finding id R-NN, grade, member or file, one-line finding), then
per finding: what is wrong, the evidence (file, line, quote), and the fix you propose. Then a per-member
checklist (checks 1-6 above: pass, fail or finding id). Then a passage re-verification table (every passage
the catalog quotes: found / not found / misread). Then the design-draft check.

BOUNDARIES: write only reports/stage_e10_catalog_review.md (and scratch files under
reports/stage_e10_briefs/review_scratch/ if you need them). Do not edit the catalog, the rulings, the logs,
the design target or the design draft. You may fetch a source page again to resolve a dispute, saving it
under reports/stage_e10_briefs/review_scratch/ with URL, UTC time and sha256. No git commits, no Databento,
no purchases, no trading-platform API or credential reference, no keys. Do not spawn other agents. Read large files by grep and line
ranges. Token or cost notices are informational.

TIME: about 45 minutes.

RETURN (final message only): (1) the review path, (2) a summary of at most 200 words: counts per grade and
each BLOCKING and SHOULD FIX finding in one line, (3) anything you could not check.
