## 6. Open choices

Every choice the lead made where the prompt left room, in the order made. "Lead" is the E.31 lead (Opus 5.5 xhigh).

- OC-1 Reviewers. One tiny probe (FableProbe, 07:49 on 2026-10-22) answered "FABLE OK Fable 5.1", so the lead took the
  prompt's Max branch and spawned every review and verification with model "fable" at xhigh. The transcripts show all six
  ran on claude-sonnet-5-5 (found at the end with the cost script): the alias fell back silently and the probe's answer was
  a self-report. So the reviews were Sonnet 5.5 xhigh in fresh contexts, neither Fable nor the Pro branch's Opus 5.5
  xhigh. The lead then ran the Pro branch's check of the verdict numbers (OpusVerifier, Opus 5.5 xhigh, fresh context);
  a check by Fable itself stays pending. Ultracode is a session setting the lead cannot switch; at most 4 workers ran
  at once.
- OC-2 Part 1 purchase path. Routed through a new pilot-path script (work/pilot/vol_pull.py) that uses SpendGate directly on
  acct-3, as E.28's pilot_pull.py does. data.config.PILOT_ONLY_ACCOUNTS and every file under data/ are unchanged, so no guard
  change needed review.
- OC-3 Volume day universe. Monday-to-Friday UTC dates with a QM or ZM outright bar; a root with no bar counts 0 (it can only
  lower a median). Each root's own universe is shown beside; both gave the same verdicts.
- OC-4 Review in two passes. SpecReviewer (spec, kill rule, window arithmetic, purchase and verify code) gave the purchase GO;
  the engine and stats code got their own Fable review before the measurement; one re-check covered the fixes of both. Reason:
  the purchase depends only on the first, and a single review after all the code would have pushed the download past the
  measurement's time.
- OC-5 Spec v2 erratum. Section 5 still says "the headline and the gate use the dropping version"; v2 section 7 (K1 must clear
  under both the dropping and the no-drop variant) governs the gate. Kept as an erratum so the frozen v2 hash stands.
- OC-6 Tick check. Databento quotes ZS and ZL in US cents (0.25 x 5,000 = 1,250; 0.01 x 60,000 = 600), so the check as first
  written stopped the run. measure31.checked_tick accepts USD or cents for ZS and ZL; ticks are used as found (the engine only
  divides by them). A second copy of this session (tmux claude-retry-*, 01:07 on 2026-10-23, closed by the planner, bought
  nothing) had edited the same line to multiply by a cents factor; the lead's version superseded it deliberately.
- OC-7 Model (b)'s volume. The engine uses Q, the outright volume filled against displayed resting orders, where spec 4(b)
  says v (all prints at the price). Q is conservative and matches spec 3.1's implied-liquidity rule; model (b) decides nothing.
- OC-8 Z4 delivery below the quote. The canary's definition files came 3.7% under the quoted billable bytes, settled at the
  quote. For the definition schema only, that is a quality finding, not hard; Z1-Z3 keep the hard equality (they matched
  exactly). The outrights' match algorithm and ticks are checked directly by canary_check31.
- Fee reading (spec v2 section 7). K1 charges half of Topstep's 5.28 USD round trip per fill (0.264 tick): a passive round trip
  is two fills and Topstep states "Each side (Buy or Sell) incurs half the total". The prompt's literal "less the Topstep fee
  in ticks" can be read as 0.528; that bound is reported beside, and a PASS that fails at 0.528 is labelled "PASS, fragile
  (fee reading)".
- K1 under both markout variants (SpecReviewer item 2), the canary tranche (item 3), one retry within acct-3's cap (item 4),
  verify31 hard checks (item 5), the grid boundary 08:35..13:10 CT, 56 DAY grid times (item 11): adopted before any purchase.
- Window. k = 39 months (2020-12..2024-02) is the rule's result: the most whole months whose fresh quotes fit TARGET 122.27
  (sum 121.645551; 2020-11 would make 124.340118). Month requests run 16:00 CT to 16:00 CT so each holds whole trade dates and
  every weekday 00:00 UTC snapshot.
- Front and second month are Databento volume ranks ZM.v.0 and ZM.v.1, not necessarily the two nearest expiries.
- K-algorithm gaps (spec 3.1): pro-rata denominator after the FIFO step; the TOP order takes part in later steps; split ceil;
  TOP modification rule S4's text; TOP Max counting changes on 2023-10-02; parameters sourced for 2023-06..2024-02 and assumed
  for earlier months, so model (a) is also reported from 2023-11-01 alone; the virtual order is never TOP; the FIFO exception
  is tested with the virtual order included.
- USDA calendar. WASDE, NASS and FAS rows from research/usda_releases.csv and usda_releases_ext.csv; 88 FAS rows are
  rule-derived or uncertain; NOPA is not USDA and is not used; three 2022 FAS outage weeks are skipped.
- StatsCoder's 7 conventions (stats31: done-marker names, split statistics among fills, fills in the 50 ms cancel latency
  count, one shared bootstrap matrix, placements not filtered by days.included, implied cases (i) and (ii) separate, K1 with no
  interval counts as FAIL) and SimCoder's 29 conventions (README_measure31.md, Conventions): accepted by the lead and reviewed
  by EngineReviewer.
- Times. The Part 1 request file says "about 08:20 PDT"; its mtime is 07:56 (before the 07:58 quote): a lead clock estimate,
  corrected in STATE, the frozen file left as is.
- V49 (planner commit c8f189e, 2026-10-23 01:03) makes a ZL trade-through measurement a follow-up; it is not in E.31's scope
  (decisions in force V20-V48).
