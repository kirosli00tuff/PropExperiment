# F2_firms: firm facts for Stage E.32b (FirmRules-OpusHigh, 2026-10-28 PDT)

Facts only, no scores. Full entries with value, old value, E.28 path, verbatim quote, file, URL, UTC fetch time and sha256 are
in F2_firms.json. Pages are in pages/FIRMS/ (log.tsv), and helpers are in work/FIRMS/. WebSearch calls: 7 of the 50 budgeted.
Base is E.28 (reports/stage_e28_briefs/A2_firm_*.json, A3_firm_products.json, facts of 2026-10-21).

Access by firm. Topstep and MFFU: live help pages, fetched by targeted curl at least 4 s apart (their terms have no ban on
single-page retrieval). Lucid, Tradeify and Bulenox: their terms forbid robots, so Wayback captures only. Tradeify has no
capture newer than 2026-10-14, so a change there after E.28 cannot be detected by a permitted route.

## Pointer checks (planner_research_notes.md)

- Topstep Tier 1: VERIFIED (live page ts_13613539). Covers CPI 07:30, FOMC decision 13:00, FOMC presser 13:30, NFP 07:30 and
  PPI 07:30 CT, from 5 minutes before to 5 minutes after. The minis ES, RTY, YM, NQ, NKD, GC, SI, HG and PL may not open
  new positions. At 50K, the micros MES, M2K, MYM, MNQ and MGC are capped at 3 and MHG and SIL at 2, so one lot is still
  allowed. "Other products (energies, rates, FX, etc.) are unaffected"; grains are not named. Unchanged from E.28.
  Among the 47 codes, it blocks RTY, YM, NQ, GC, SI and HG.
- MFFU EIA: VERIFIED for Rapid and Pro Sim Funded only. "For Energy Traders: EIA" is a T1 event there (2 minutes before and
  after, flat by 2 minutes before). "All evaluations" and "Builder Plans" are listed as Unrestricted. The rule does not
  bind the Builder 50K plan that E.28 uses. Two wording conflicts on MFFU pages are recorded: "Standard Trading Protocols ...
  apply to all news releases" (2 minutes, no positions) and Fair Play "Tier 1 ... is restricted".

## Topstep (50K Trading Combine, Standard Path; XFA): no change on 18 refetched pages

- Products: the same 31 of the 47 codes. SI and HG are capped at 0. Temporary 50K caps: CL/QM/GC 3; MCL/MGC 30; SIL/MHG 2.
- News: see the Tier 1 check above. The LFA (balance below $3,000) is limited to 1 contract. Separately prohibited: trading the
  full maximum size directly into a major news event.
- Flat by 15:10 CT; no new opens after 15:08 CT; reopen 17:00 CT. CBOT grains trade Sun-Mon 19:00-07:45 and Mon-Fri
  08:30-13:20 CT, with a pause 07:45-08:30 in which no orders are accepted. Flat 15 minutes before an early close. No
  overnight or weekend holds in any stage.
- DLL $1,000, optional, chosen at purchase; hitting it is not a violation. MLL $2,000, trailing on the EOD balance and
  monitored intraday. The Combine MLL locks at $50,000; the XFA MLL starts at -$2,000 and locks at $0 once the balance
  reaches $2,000.
- Payout, Standard path: 5 winning days of $150 or more and positive profit since the last payout; 50% of the balance up to
  $2,000 ($4,000 with DLL). Consistency path: 3 days, best day at most 40%, up to $3,000. Minimum $125; split 90/10.
  Combine: best day at most 55% of the target, no buffer, 2 days minimum.
- Automation is allowed in the Combine and the XFA through the TopstepX/ProjectX API ($29 list, $14.50 a month); not on the
  LFA. HFT is prohibited (no definition). The SIM-abuse text names "hundreds or thousands of trades per day ... durations
  measured in seconds". The API allows 200 requests per 60 s (3.33 a second). VPS is prohibited for order flow; brackets
  are available on the API.
- Fees: all 31 codes unchanged (ZM 5.28, MGC 1.92, QM 3.42, MCL 1.72 USD RT).
- Reliability: firm since 2010/2012. McCrudden v. Topstepfunded (filed 2026-04-09, alleges rule changes used to block
  payouts) is carried from E.28; its docket was not refetched. Rule changes in the last 12 months: payout cap, consistency,
  platforms (E.28 list). No regulatory action found. BC accepted: Canada is on neither restricted list.

## Lucid (LucidPro 50K): no change in captures up to 2026-10-26

- Products: the same 23 codes. No rates, crypto, M6E/M6A, MNG or MHG.
- News: none on Pro, Flex or Direct ("Allowed"). Red-folder news is a hard breach only on LucidDaily.
- Flat by 16:45 ET Mon-Fri, auto-closed with no failure; reopen 18:00 ET Sun-Thu; at the holiday close on early-close days.
  No overnight holds.
- DLL $1,200 (soft). In funded, fixed below $52,100, then 60% of the highest EOD profit. The DLL is optional at purchase.
  MLL $2,000 EOD trailing, locks at $50,100 once the balance passes $52,100.
- Payout: $500 minimum profit per cycle, largest day at most 40%, profits above the $52,100 buffer. Minimum payout $500;
  maximum $2,000, then $2,500; split 90/10. No winning-day count is stated on the firm page.
- Automation: "Automated trading systems and trade copiers are permitted". HFT is prohibited (qualitative). Microscalping is
  flagged when more than 50% of profit comes from holds of 5 s or less. No API, rate limit or VPS rule is documented.
- Fees: "Commission (Per Side)" only. No all-in statement, so the E.28 treatment of RT = 2 x per side stands (ZM 5.60,
  MGC 1.60). Unchanged.
- Reliability: operating since 2025, so under 2 years. Payout disputes: review-site pointers only. Rule changes: E.28 list.
  BC: carried from E.28, since the restricted-countries page has no capture.

## Tradeify (Growth 50K): no change detectable

- Products and fees: carried from E.28, because the captures (2026-07-09) are older than E.28. Same 24 codes; ZM 9.20,
  MGC 2.12 USD RT.
- News: none ("We do not have any rules against or guidelines around trading news events").
- Flat by 16:45 ET, or 12:59 ET on holiday early closes; auto-closed with no failure. No overnight or swing holds.
- DLL $1,250 (Growth evaluation and funded). MLL $2,000 EOD trailing, enforced in real time. Conflict: E.28 recorded "no
  lock in evaluation", but the essential-rules page gives a lock at $50,100 / $52,100 under "All Evaluation Accounts".
- Payout: 5 days with profit above $150; consistency 35%; balance of at least $53,000 to request; caps 1,500, 2,000,
  2,500, 3,000; minimum $500. Funded payout gate: more than 50% of trades and profit from holds over 10 s. At least 1 trade
  a week.
- Automation is allowed if the strategy is owned by the trader, not shared and not HFT. The Tradovate API is for LIVE funded
  accounts only (E.28). No rate limit is published. VPS is conditionally prohibited.
- Reliability: operating since 2022-12 or earlier. Disputes: pointers only. Rule changes: Tradeify 3.0, removal of the
  Growth evaluation consistency rule, and the 53,000 minimum balance from 2025-09-12. BC: carried from E.28.

## MFFU (Builder 50K, Default MLL): no change on 11 refetched pages

- Products: the same 23 codes. SI, HG, PL, NG and QG are restricted. Metals micros are capped at 5 at 50K, and MBT counts
  as a mini. MNG and MHG are absent.
- News: Builder has none in evaluation or sim funded. The burst-strategy ban (straddles, strangles) applies to all accounts.
  T1 rules: see the pointer check above.
- Flat by 16:10 ET (positions auto-closed); open 18:00 ET. On holiday half days there is no auto-liquidation, and an open
  position breaches the account. No overnight holds.
- DLL $1,000 soft pause (evaluation, sim funded and live). MLL $2,000 EOD trailing, locks at the start + $100.
- Payout: 2 trading days per cycle, no per-day minimum, consistency 50%, buffer $2,100. First payout $500 above the
  buffer; minimum $500, maximum $2,000; split 80/20; 5 sim payouts, then live.
- Automation is allowed if it does not exploit sim fills; HFT is prohibited (no definition). No MFFU API is documented
  (Tradovate-based platforms). No rate limit, minimum hold or VPS statement.
- Fees: unchanged ("Total Cost Round Trip": ZM 6.12, MGC 2.20, QM 4.32).
- Reliability: 2023, month unverified. Most payouts are instant; manual review takes 6-12 business hours. Rule changes:
  E.28 list (a 90-to-80 split change on 2026-02-26 has a pointer only). No regulatory action found. BC accepted: Canada is
  not on the list.

## Bulenox (Qualification $50K, Option 1 or 2; Master sim): payout rules changed

- Products: the same 25 codes (no ZC, no rates, no SIL/MHG/MNG).
- News: none (from E.28's FAQ capture of 2026-10-08; not recaptured).
- Flat by 15:59 CT; the trading day runs 17:00-16:00 CT. "Holding positions overnight is strictly prohibited."
- DLL: Option 2 has $1,100 (soft); Option 1 has none. MLL $2,500: Option 1 trails in real time including open profit;
  Option 2 trails at EOD. On the Master account the MLL fixes at $50,100 once the account reaches $52,600.
- Payout, CHANGED between the 2026-09-28 and 2026-10-24 captures:
  - The 10-trading-day cycle, $1,000 minimum, $1,500 cap on payouts 1-3, $2,600 reserve and weekly Wednesday schedule are
    unchanged.
  - New: from the 4th payout, the request must be below 50% of the total profit (previously no cap).
  - New: consistency (40%) now resets after each payout (previously cumulative).
  - The "100% of first $10,000" sentence is gone (90/10 now). This rests on the sentence's absence; third-party sites
    still list the 100% tier.
  - New: at least 1 trade a week on the Master account.
- Automation: user-built bots allowed; third-party algorithms need approval. Rithmic third-party API costs $100 a month.
  The Terms (2026-10-19 copy, unchanged) ban "scalping" algorithms and hundreds or thousands of rapid trades. No rate
  limit or minimum hold is published.
- Fees: per-product commissions unchanged (ZM 5.72, MGC 1.52, QM 3.92, all-in). The professional data fee went from $116
  to $133 a month.
- Reliability: operating since 2021-06 or earlier. Disputes: "flipping" payout denials [unverified, pointers]. Rule changes
  in the last 12 months: E.28's 7 plus this October payout change. BC: carried from E.28.

## Gaps and non-results

- Tradeify: products, fees and BC were not re-verified after 2026-10-21 (no permitted fresher source).
- Lucid: restricted-countries and platforms pages have no Wayback capture, so they are carried from E.28. All Lucid facts
  come from captures dated 2026-09-22 to 2026-10-26.
- Bulenox: FAQ, Rates PDF and Terms PDF have no capture after E.28.
- MFFU Builder news scope has conflicting wording across firm pages; it is recorded, not resolved.
- No regulatory action found at any firm. These are search negatives, at pointer level.
- None of the five firms publishes an order-rate limit in orders per second. Topstep's ProjectX request limit is the only
  number.
