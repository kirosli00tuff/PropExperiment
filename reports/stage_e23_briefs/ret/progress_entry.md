
## 2026-10-17 — Stage E.23: the program's intraday triggers at multi-day holds; no survivor, all five null; N = 538

Prompt: docs/prompts/STAGE_E.23.md (V40). Lead: Opus 5.5 at xhigh, under ultracode. Session 09fe7046, unattended.
Two gaps, both excluded from work time:
- a pause 03:38-05:21 PDT (usage limit);
- a stall 05:41-07:21 PDT (the verifier's wait for the suite matched its own command line and never fired).

Return: reports/E.23_RETURN.md.

- **Inventory and mechanisms.** 21 opus-high readers covered 208 frozen intraday triggers and wrote 11 mechanism memos with
  verbatim quotes. Most triggers were dropped for one of four reasons:
  - no owned 2010-2019 store (MES, FX, MBT, VXN, the event calendars), or too short a store (TN, RTY, HE, LE);
  - weak or intraday-only mechanisms;
  - duplicates already read (the auction members are E16-H3's long leg; CP1, E16-H1 and E16-H4 are H6 on NQ);
  - books in the market almost every day.
- **Shortlist and registration.** K2-monthend-01 long on ZF, ZN and ZB at 5 days, and E20H6-T1 reversal on NQ at 5 and
  20 days; K = 5.
  - Code: the trigger_hold/ engine (BookCoder: E.21's trend sums and T3 reproduced exactly) and the event extraction
    (TriggerCoder: 0 differences on the W_cf validations).
  - Review: RegReviewer and CodeReviewer (Fable xhigh) each returned APPROVE WITH FIXES with 0 BLOCKING. The four
    SHOULD FIX findings (R-01..R-03, C-01) were fixed before the freeze.
  - Freeze 24dcf4dd... (commits 25bc321, 75874c4); r008-E23, N 533 -> 538.
- **Windows and power.**
  - Discovery: W_ext 2011-07-27..2019-04-30, ext2010 stores. Power 0.27 at t >= 2.0, and 0.17 at Holm step 1.
  - Confirmation: W_cf 2019-05-06..2024-02-29, inconclusive by design (power 0.18).
  - No owned window can power both a discovery and a confirmation at a true Sharpe of 0.5.
- **Discovery** (03:33:54-03:34:35, run once). No survivor; Holm's smallest p was 0.309.
  - Base net Sharpe and alpha t_NW: ZF 0.21 and 0.55, ZN 0.14 and 0.38, ZB 0.02 and 0.10; H6 at 5 days -0.50 and -1.61,
    at 20 days -0.37 and -0.71.
  - With the bonds' buy-and-hold return added, the month-end alpha t falls to 0.12, -0.34 and -0.78: the gain is drift.
  - PBO 0.43; every DSR below 0.04.
- **Confirmation** (03:35:29, run once). 0 survivors, so nothing was computed. All five are NULL. K8-flight-01 and
  K1-vxnband-01 are unconfirmable on owned data.
- **Verification.** VerdictVerifier-FableXHigh: VERIFIED WITH NOTES. It recomputed 343 rows and re-simulated the books from
  the bars exactly. None of its 7 notes changes a number. NOTE-2: the frozen E.21 loader held the W_cf rows in memory
  during discovery, but nothing was computed from them.
- **Guardrails.**
  - Holdout all_ok with 0 unlocks at start and end; REGISTRATION.md 0 bytes.
  - Spend ledger unchanged (36,402 lines, 034a454b...); harness v13 dd2bcc60... verified.
  - Nothing dated 2024-03-01 or later was read. No purchase, no Databento or TopstepX call, no push.
  - The five v13 earlier-freeze failures and the h6 test fail as before.
- **For the user:**
  - close this direction;
  - keep W_cf and holdout-2 for a hypothesis with a stronger prior;
  - buy no data for this line;
  - in the next multi-day prompt, bound the multi-day loader by ctx.last and write unit and fill files;
  - E22-F1's settlement source is still pending.
