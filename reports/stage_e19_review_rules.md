# Stage E.19 Task 5a: independent review of the Topstep rule table and terms (RulesReviewer-FableXHigh)

Worker: RulesReviewer-FableXHigh (fable, xhigh), spawned 2026-10-10 17:43 PDT per reports/stage_e19_STATE.md; report written
2026-10-10 17:55 PDT (closing time stamped at the end). Brief: reports/stage_e19_briefs/brief_rules_review.md. Reviewed: reports/stage_e19_rules.json
(schema e19-rules-1, FINAL, 214 rules, 42 practices, 41 sources) and reports/stage_e19_rules.md, the saved pages under
reports/stage_e19_briefs/pages/ (.html and BeautifulSoup .txt), rules_fetch_log.md, rules_schema.md, sim_spec.md and the lead's
rulings L-11 to L-17 in stage_e19_STATE.md. I did not write any of it. Scripts ran from the session scratchpad with `python3 -I`;
nothing under reports/stage_e19_briefs/, prop_econ/ or reports/stage_e19_runs/ was modified. My own artefacts: this file and
reports/stage_e19_verify/ (5 re-fetched pages, their stripped .txt, refetch_log.md).

Grades: BLOCKING = a wrong or unsupported value or reading that changes a modelled cash flow or rule, or a prohibited practice the model
or the recommendations would breach; SHOULD FIX; NOTE.

Counts: BLOCKING 1 (RR-1), SHOULD FIX 4 (RR-2 to RR-5), NOTE 14 (RR-6 to RR-19).

Cost notices: the session hook printed "COST CRITICAL: session total ~$81.36 ... Informational only" at 2026-10-10 17:53 PDT (after the
re-fetch comparison). Logged; work continued. No WebSearch was used, so no search-budget notice arose.

## Findings table

| ID | Grade | Rule or practice | Finding | Evidence (quote, file) | Suggested fix |
|---|---|---|---|---|---|
| RR-1 | BLOCKING | P01 Account stacking (S23), P29 Excessive purchases (S24), P30 FTP churn (S34), ToU section 3 purchase-rate clause (S04 line 82), R049/R061 | The modelled funnel is, at high churn, the practice Topstep names: sequential Combine purchases and resets after MLL breaches, up to 60 attempts per cycle and 400 purchases per campaign (sim_spec section 5), with f up to 0.25 in the policy band and 0.35 / 0.50 as diagnostics. "Expected net cash per Combine purchase" and "P50 / P80 purchases to reach $5,000 / $10,000" treat resets as a free, unlimited action; Topstep's pages make a high reset rate Prohibited Conduct (Prohibited Conduct page dateModified 2026-09-30) with consequences from a Slowdown Path (no new Combines, Resets or B2F) to all accounts closed and pending payouts denied. No threshold is published, so the exposure cannot be simulated away; a recommendation of f or of a purchase count K without a churn constraint recommends a prohibited practice. The lead's L-14 carries this as a terms constraint in the recommendations but no configuration-level churn measure exists in the grid outputs (sim_spec section 6). | S23: "Repeatedly trading aggressively, hitting the Maximum Loss Limit (MLL) in one account, then switching to another account and repeating. The goal is to run high-risk attempts until a large win occurs. This exploits risk parameters and is not permitted." (pages/art_10305426.html.txt). S24: "Excessive purchases of Trading Combines or Resets" under "What Is Prohibited Conduct?" (pages/art_10296582.html.txt). S34: "Activating and losing many Express Funded Accounts in a short period of time" (pages/art_10551016.html.txt). S10: "Limits exist to protect you from account churning" (pages/art_10370307.html.txt). S04 line 82: "if you place an unusually large number of orders for the Services within an unreasonably short period of time, as determined in the sole discretion of Topstep, we reserve the right to suspend any further orders of the Services by you." (pages/ts_terms_of_use.html.txt). | Add per-configuration churn metrics to the grid outputs: expected resets per 30 calendar days per subscription, expected MLL breaches per 30 days across all slots, P(cycle needs more than N attempts), share of cycles ending at the attempt cap. The lead sets the policy band on churn (a candidate: at most the one Reset Credit per rebill period that S09 provides, i.e. about 1 reset per 21 trading days, plus one paid reset) and labels every configuration outside it "prohibited-conduct exposure" in the results and the return; the headline f and K recommendations must come from inside the band. Add a forfeiture sensitivity (P14: a finding forfeits withdrawals on every account and closes them). |
| RR-2 | SHOULD FIX | P06 full Maximum Position Size into scheduled news (S23), P33 RTP trigger "max position a majority of your trades" (S31), sim_spec section 2 step 3 | The simulator cuts n to the lot cap (Combine max_minis or the XFA scaling tier) whenever f x D / sigma exceeds it, so on those days the bot holds the full Maximum Position Size through every scheduled release inside the day session (7:30 CT CPI / employment inside the rates, fx, energy and gold windows that open 7:20 or 8:00 CT; 9:30 CT EIA inside energy; 13:00 CT FOMC inside equity, rates and fx). The share of days at the cap is also the measure of the RTP trigger. Not a cash-flow error; a feasibility constraint on the recommended f. | S23: "Purposefully trading your full Maximum Position Size directly into a scheduled major news event." (pages/art_10305426.html.txt). S31: "You max position a majority of your trades" under "You may need the Responsible Trading Program if:" (pages/art_13620045.html.txt). S22 (R040): flattening for releases is not required (pages/art_8284211.html.txt). D6 windows: screening/vehicles.py lines 50-60 (read only). | Report the share of trading days on which n is cut to the cap, per configuration; in the policy band cap n below the MPS (one mini-equivalent below, or 80% of the tier) or flatten before releases; exclude from the recommendation any configuration where the cap binds on a majority of days. |
| RR-3 | SHOULD FIX | P18 Cross-account hedging (S24), P19 overlap even if brief or unintentional (S21), R039; sim_spec section 5 "slots independent" | The 5-slot campaign draws each slot's product (pooled, per 5-day block) and direction (fair coin per day) independently, so two slots hold the same product in opposite directions on roughly 1/10 of slot-pair days; S21 bans this across one trader's accounts "even if the overlap is brief or unintentional" and extends it to correlated instruments. The i.i.d. 5-slot campaign is therefore not a configuration a bot can run; the feasible ones are one product per slot (same direction rule per product) or copy-traded same-direction fills. Means are unchanged (sum of expectations); the P50 / P80 purchases-to-target figures depend on the cross-slot correlation and change. | S21: "Cross-account hedging means simultaneously going long and short the same or correlated instrument across multiple accounts — such as MES/ES, MNQ/NQ." and "Opposing positions are prohibited even if the overlap is brief or unintentional." (pages/art_13747047.html.txt). S24: "Cross-account hedging (single-user) — holding opposite positions across multiple accounts simultaneously" (pages/art_10296582.html.txt). | Label the i.i.d. 5-slot campaign as a diversification upper bound, not a feasible configuration; add the one-product-per-slot campaign (five distinct products, one bot direction per product per day) as the feasible multi-slot case next to the copy-traded 5 x one-cycle case. |
| RR-4 | SHOULD FIX | P35 "Unusually large number of orders (Terms)" bot_implication | The clause is about orders for the Services, i.e. purchases of Combines and Resets (ToU "Services" = the Trading Combine and related services; the sentence sits in the ordering section and continues "suspend any further orders of the Services by you"). The practice's bot_implication ("Keep order rates low; Topstep can suspend orders at its discretion") reads it as trading-order rate, which is wrong; the clause belongs with P29 / P30 as the contractual basis for suspending purchases. | S04 line 82 (full sentence quoted under RR-1), pages/ts_terms_of_use.html.txt; ToU definitions: "Services" means, as applicable, the Trading Combine® or other services (line 48). | Reword P35's bot_implication to "Topstep may suspend further Combine or Reset purchases when it judges the purchase rate unusual; the churn constraint of P29/P30 is contractual"; cite it under RR-1's churn constraint. |
| RR-5 | SHOULD FIX | P32 Multiple MLL hits in one day (S31), R059/R060; sim_spec section 5 "copy-traded case ... five times one cycle" | Copy-traded accounts breach the MLL on the same day; S31 lists that as an RTP trigger, after which new Combines and XFAs get a forced DLL and only the Consistency XFA path is available. The "five times one cycle" figure (DLL off, Standard path) is therefore not reachable twice in a row; L-14 carries the constraint but the results table must say so beside the number. | S31: "Multiple accounts hit the Maximum Loss Limit in one day" and "All new Trading Combines® and XFAs automatically get a Daily Loss Limit (DLL )" (pages/art_13620045.html.txt). | Footnote the copy-traded figure with the RTP consequence and show the DLL-on, Consistency-path copy-traded case as the steady-state value. |
| RR-6 | NOTE | R066 / R115 / R166 dll_discount_monthly_usd.standard = null (INFERRED) | S06's sentence names "Express Funded Account Activations" among the DLL-discount-eligible purchases, but S06's discount table lists only the No Activation Fee Combine ($10/$20/$30) and Back2Funded ($50), and the S38 widget with the Responsible Trading toggle on still shows "Express Funded Activation Fee: $149" and the Standard monthly price unchanged ($49). The worker flagged it unresolved (rules.md section 7). The null is the conservative reading; if an activation discount exists it lowers DLL-on Standard-path fees by an unpublished amount. | S06: "Discount when you add a DLL at purchase for No Activation Fee Trading Combines, Express Funded Account Activations, and Back2Funded Reactivations." (pages/art_14289835.html.txt line 120); S38 lines 46-80 (pages/ts_no_activation_fee.html.txt). | Keep null; state in the results that DLL-on Standard-path fees may be overstated by an unpublished activation discount. |
| RR-7 | NOTE | R002 profit_split_trader = 0.9 | Verified. The "100% of your first $10,000" clause on S17 is a note "for traders who joined the new Topstep dashboard before January 12, 2026"; a new account gets 90/10 from the first dollar. | S17: "90/10 split" (XFA and LFA columns) and "Note for traders who joined the new Topstep dashboard before January 12, 2026: You receive 100% of your first $10,000 in lifetime profits. After that, the 90/10 split applies." (pages/art_8284233.html.txt lines 62-66). | None. |
| RR-8 | NOTE | R046 / R047 payout fee $0 (Wise, Aeropay), L-12 headline | Wise is available for Canada (the user's region) since August 2026 and carries no Topstep fee, so the $0 headline holds for Topstep's side; Wise's own currency-conversion fee applies to a CAD account, Aeropay and ACH are US-only, wire is $30 plus bank fees. The availability note calls Wise "restored for select regions", so the $30 sensitivity is the right fallback. | S17: "Wise is available again as a payout method for traders in China, Canada, and the United Kingdom." and "No Topstep fee for Aeropay or Wise, but your bank or those services may charge their own fees." (pages/art_8284233.html.txt lines 296-304). | State in the results that $0 is Topstep's fee only and that Wise conversion costs are the user's. |
| RR-9 | NOTE | R074 / R075 Combine consistency type and frac; R029 boundary (CONFLICT) | The two wordings are one rule. "Best day at or below 55% of the Profit Target, else the target rises to best day / 0.55" (S13) and "no single day exceeds 55% of your total profit and your Profit Target is met" (S13) give the same EOD pass condition: B >= max(T, best_day / 0.55) is the same as B >= T and best_day <= 0.55 B. The simulator's type best_day_max_frac_of_profit is right and the S13 worked example ($1,800 best day gives a $3,273 target) reproduces. The strict / inclusive boundary (R029, loader reads strict) is immaterial for continuous P&L. S13 also fixes that the raise can only be resolved on a later day, so an EOD-only pass check is right. | S13: "Best Day ÷ 0.55 = Total Profit Needed." and "To resolve a Consistency Target increase, the remaining profit must be earned on a separate trading day" (pages/art_8284208.html.txt lines 72-81). | None. |
| RR-10 | NOTE | R058 xfa_min_payout_balance_after_first_required = true (CONFLICT, stricter first) | The structured JSON value is true but the rule cannot be simulated (no amount published) and prop_econ/rules.py does not read the field (checked by grep, read only), so the model runs the help-centre reading (false) per L-14. The JSON's structured value and the modelled reading disagree; the results should say which was run. | S35: "After the first payout, a Minimum Payout Balance must be met for subsequent payouts." (www, Last updated June 26, 2025; pages/ts_express_funded_account_rules.html.txt); S17: "$.01 or more" rule (pages/art_8284233.html.txt). | State in the results that R058 was run as false (the only modelable reading) and why. |
| RR-11 | NOTE | sim_spec section 5 "A pass ends the subscription (unused credits are lost)" vs S09 | S09 says Reset Credits stay on the profile after the subscription ends and can be applied to an existing active subscription of the same size and type, so a credit unused at a pass could serve the next Combine of that size. The simulator's loss of the credit is conservative and small (credits arrive only at a rebill, which resets push out). | S09: "Reset Credits stay on your profile, even if you cancel the associated subscription." and "Can't use credits to buy a new Trading Combine — only on an existing active subscription" (pages/art_8284128.html.txt lines 58, 66); S08: "The subscription tied to the passed Trading Combine will auto-cancel" (pages/art_8284121.html.txt line 82). | None required; mention as a conservative simplification. |
| RR-12 | NOTE | Terms check (ToU section 28, robots.txt), L-11 | The clause and both robots files are quoted verbatim and correctly. The ban is on processes that "crawl" or "spider" pages; Task 1 fetched 41 named URLs once each, 3.5 s apart, after reading the Terms, and used the two sitemaps (which the robots files themselves advertise) only to find article URLs. That is targeted retrieval, not traversal; help.topstep.com's Crawl-delay 1 was respected. Two caveats: a browser User-Agent string is impersonation (not a terms breach, since robots.txt applies to every agent, but not transparent), and Section 28 also bars use "to gain competitive intelligence ... to compete with Topstep", which a prospective customer's rules check does not engage. The lead's reading holds; it was flagged for the user, as it should be. My five re-fetches used the same method, 4 s apart. | S04 line 273: "Using any manual or automated software, devices, or other processes to “crawl” or “spider” any web pages contained in the Sites or Services;" (pages/ts_terms_of_use.html.txt); S02: "Crawl-delay: 1" (pages/help_robots.txt); S01: "Disallow: /api / Disallow: /design-pages" (pages/topstep_robots.txt). | Record the UA choice in the return; otherwise none. |
| RR-13 | NOTE | R056 / R057 voluntary-close payout (S35), L-15 | The only source is the www XFA rules page dated June 26, 2025, which is stale elsewhere (7-day Back2Funded window, superseded 2026-05-29 per S18). Sensitivity-only treatment (L-15) is right. The same page's "Minimum Payout Balance" and the S38 widget's "Maintain your balance between payouts" are the R058 conflict. | S35: "you may receive up to 50% of your current Reward Balance, capped at $5,000." (pages/ts_express_funded_account_rules.html.txt); S18: "On May 29th, 2026, the Reactivation window increased from 7 days to 30 days!" (pages/art_12060405.html.txt). | None. |
| RR-14 | NOTE | R009, R033; sim_spec section 4 payout timing | The simulator requests at the start of the next trading day, so the request day never counts and the next window starts the day after. A real request after the 4:00 PM CT lock on the fifth winning day would let the following day count toward the next window, so each simulated payout cycle is one trading day longer than the fastest legal cycle. Conservative. | S17: "A day locks in at 4:00 PM CT. The trading day your Payout is requested doesn't count toward your next 5." (pages/art_8284233.html.txt); S13: "The new window starts on the trading day after your Payout was requested." (pages/art_8284208.html.txt). | None. |
| RR-15 | NOTE | R092 / R143 / R196 scaling_boundary (UNSOURCED), R034 | Both readings are listed and run (L-16). The S32 hint toward "upper" is recorded. The tier-from-prior-close rule (R034) is supported. | S16: "Your max contracts do not increase mid-session." (pages/art_8284223.html.txt). | None. |
| RR-16 | NOTE | Prohibited-practices completeness (check 5) | The keyword census over all 39 saved text pages found no bot-relevant practice missing from the 42. Items in the sources and not listed are not bot-relevant: bad-faith disputes and chargebacks, promo-code abuse, Discord conduct, profile content, identity verification, new profiles after a ban. The ToU one-Account rule (line 184) is covered by P40's help-centre form; purchase limits (S10: no limit on Combines, 2 Resets per account per calendar day) are R049 / R006. | pages/ts_terms_of_use.html.txt line 184: "you are only permitted to have one Account". | None beyond RR-4. |
| RR-17 | NOTE | P36 flat by 3:10 PM CT, R032; D6 windows | All five modelled day sessions close before 15:10 CT (equity 15:00, rates and fx 14:00, energy 13:30, gold 12:30 CT) and ReturnsCoder skips early-close days (L-10), so the hold never meets the flatten rule or the 15:09:50 auto-flatten. | S04 line 264: "All positions MUST be closed prior to 3:10 PM CT or prior to the market close, whichever is sooner." (pages/ts_terms_of_use.html.txt); screening/vehicles.py lines 50-60. | None. |
| RR-18 | NOTE | Spot re-fetch (check 6) | 5 of 5 pages returned 200. S19 and S23 are byte-identical to Task 1's copies; S06, S17 and S14 differ only in dynamic Intercom markup: every one of the 84 quotes sourced to the five pages is present verbatim in the fresh text, the multisets of dollar and percent figures are identical, and JSON-LD dateModified is unchanged on all five. | reports/stage_e19_verify/refetch_log.md; reports/stage_e19_verify/pages/*.html and .txt. | None. |
| RR-19 | NOTE | R043 API fee 14.5 | The $14.50 depends on the "topstep" code (list $29, billed by a third party); both readings are in the rule. The wallet applies it post hoc per 21 trading days (L-12). | S26: "Topstep Traders get 50% off with code topstep — that's $14.50/month" (pages/art_11187768.html.txt). | None. |

## Check 1: quotes verbatim and values following from them

Scripted check (scratchpad qcheck.py, `python3 -I`): JSON loads; 214 rules, 42 practices, 41 sources; status counts SOURCED 198,
INFERRED 6, UNSOURCED 7, CONFLICT 3 (matches rules.md). Every saved raw file's sha256 matches the sources table (0 mismatches). All 207
rules with a quote (SOURCED, INFERRED, CONFLICT) and all 42 practice quotes are found verbatim in the cited source's stripped .txt
after collapsing whitespace runs to one space: 0 failures, 0 rules missing a quote or source. The 24 scaling rules (S40) are checked
against the worker's transcription file; I viewed the image myself (Read tool) and every one of the 12 tiles (50K: below $1,500 2 lots,
$1,500-$2,000 3, above $2,000 5; 100K: 3, 4, 5, above $3,000 10; 150K: 3, 4, 5, $3,000-$4,500 10, above $4,500 15) matches the
transcription and the 24 rule values. Structured consistency: the 214 leaves of `global` and `sizes` map one-to-one onto the 214
rule paths, no duplicates, every structured value equals its rule's value and readings[0].

Hand read: 120 rules (82 distinct quotes, deduplicated), covering every fee (R062-R067, R078-R079, R106-R107, R111-R116, R127,
R157, R162-R167, R178, R210-R211, R043-R047, R003-R006, R048), every target (R068, R117, R168), every MLL rule (R069-R071,
R081-R084, R118, R130, R133, R169, R181, R184) and DLL amount (R072-R073, R085, R122, R134, R173, R185), every cap (R096-R097,
R102-R103, R147-R148, R153-R154, R200-R201, R206-R207), the split and payout minimum (R002, R008, R009), all 24 scaling-tier rules,
every payout-path rule (R093-R095, R098-R101, R104, R030, R029, R074-R076, R099-R100), the globals R001, R010-R042, R049-R061, and
the Back2Funded block. In every case the value follows from the quote for the stated account size. Table-row quotes (for example
"50K | $49/month | $95/month") carry their column header in the rule note; I confirmed the price-table columns against the S38
widget ($49 / $95, $99 / $149, $199 / $229; with the DLL toggle $85 / $129 / $199) and the S17 cap-table header against the DLL
"Limited Time Offering" rows. One clarification worth recording: the Combine consistency rule's two wordings are equivalent (RR-9).

## Check 2: coverage of the prompt's Task 1 list

| Task 1 item | Rules |
|---|---|
| Combine price and billing (monthly) | R062-R063, R111-R112, R162-R163; R003 (30-day rebill), R004-R005, R007 (no time limit) |
| Reset price | R064-R065, R113-R114, R164-R165; R006, R048 |
| Profit target | R068, R117, R168 |
| MLL and its trailing rule | R069-R071, R118-R120, R169-R171 (EOD trailing, locks at start; breach monitored in real time) |
| DLL | R072-R073, R121-R122, R172-R173 (optional, chosen at checkout, fixed: R028) |
| Combine consistency | R074-R075, R123-R124, R174-R175; boundary R029 (CONFLICT) |
| Minimum days | R076, R125, R176 (2) |
| Activation fee and options | R078-R079, R127-R128, R178-R179; R026 (path fixed at purchase) |
| XFA trailing drawdown and lock | R081-R084, R130-R133, R181-R184 (starts at -MLL, trails EOD, locks at $0, set to $0 after the first payout) |
| Scaling plan | R086-R091, R135-R142, R186-R195; boundary R092/R143/R196 (UNSOURCED, both readings); R034-R036 |
| Winning-day definition | R093-R094 (five days of $150+ net P&L, lock 4:00 PM CT, R033) |
| Standard and Consistency paths | R093-R104 and the 100K/150K twins; R027 (fixed at activation); R030 |
| Caps | R096-R097, R102-R103 and twins; R024-R025 (DLL doubling, CONFLICT on eligibility) |
| Split | R002 |
| Payout count limits | R105 / R156 / R209 (UNSOURCED, only reading: none; R012 "Do I need 5 payouts... No") |
| What a payout does to balance and drawdown | R084 / R133 / R184 (MLL to $0); balance reduced by the gross amount per the S17 worked example ($6,000, take $3,000, new balance $3,000); R009 |
| Inactivity | R010 (30 days, "may be closed") |
| Back2Funded / reset options | R106-R110 and twins; R051-R052 |
| Live Funded call-up | R011-R023 (discretionary, closes all XFAs, cannot decline, balance conversion with cap) |
| Maximum number of XFAs | R001 (5); R050 (pass at the limit goes on hold) |

INFERRED (6): R066/R115/R166 null Standard-path DLL discount (RR-6: conservative, justified by the S06 table and the S38 widget);
R104/R155/R208 Consistency-path net-positive requirement (justified: the general FAQ applies, and the 40% ratio needs positive
window net). UNSOURCED (7): R061 threshold (none published, correctly null); R092/R143/R196 both readings listed; R105/R156/R209 "no
limit" is the only plausible reading (S19 denies a 5-payout trigger; no page caps XFA payouts; the discretionary call-up is the
lead's sensitivity). CONFLICT (3): R025, R029, R058 each carry both quotes with the stricter reading first.

## Check 3: freshness and authority

All 198 SOURCED rules cite Topstep's help centre (S06-S34, S41; JSON-LD dateModified 2026-06-10 to 2026-10-08) or the Terms of Use
(S04, last updated 2026-09-21), except R056/R057, whose only source is the www XFA rules page S35 (June 26, 2025, stale: RR-13).
No third-party source is cited; the www marketing pages S37-S39 appear only in notes as corroboration. The three CONFLICT rules
record both pages with the stricter reading first. Superseded wordings (S35's 7-day B2F window; S11 "liquidated immediately" vs
S14 "closed at the end of the day") are correctly recorded as not live. Check 6's re-fetch found no change on the five key pages.

## Check 4: terms

Quoted and verified: ToU section 28 crawl/spider clause (line 273 of the saved text), the VPN/VPS clause (line 274), both robots.txt
files. Task 1's fetch log shows the order (robots, www sitemap, Terms, then rule pages), one request per URL, 3.5 s spacing. My
judgment is in RR-12: targeted retrieval, inside the Terms and both robots files; the help centre's own Crawl-delay contemplates
automated fetching. Caveat recorded: browser User-Agent string. No login, account, API or credential was used by Task 1 or by me.

## Check 5: prohibited practices against the modelled bot

Completeness: see RR-16 (keyword census over 39 pages for stacking, hedg, copy, multiple accounts, news, HFT, high-frequency,
automat, algorithm, bot, API, simulat, exploit, gaming, abuse, gambl, consistency, denial, Live Funded, VPS, VPN, data feed, spoof,
opposite, in concert, excessive, recycl, discretion). The modelled bot: a day-session hold of one product, 1 to 3 round trips a day,
risk f x D with f in 0.05..0.25 (0.35 and 0.50 diagnostic), new Combines bought after failures, up to five XFAs, possibly the same bot
on several accounts.

| Practice | Could the model or a recommendation breach it? | How a bot avoids it |
|---|---|---|
| P01 account stacking, P29 excessive purchases, P30 FTP churn, P31 excessive XFA use, P35 (purchase-rate clause, RR-4) | Yes (RR-1): the buy-after-fail funnel at high f and uncapped resets is the named practice; no threshold is published. | Keep resets near the one-credit-per-rebill cadence, size so that MLL breaches are rare, never rotate immediately after a breach; report churn with every result. |
| P06 full MPS into major news, P33 max position on most trades | Yes (RR-2): n is cut to the cap, then held through in-session releases. | Size below the MPS; flatten before scheduled releases; keep days-at-cap a minority. |
| P18/P19 cross-account hedging, P16 opposite positions | Yes for the i.i.d. 5-slot campaign (RR-3); no for copy-traded same-direction slots. | One direction per product across all accounts at every moment; one product per slot or a copier; flatten before reversing. |
| P32 multiple MLL hits in one day (RTP) | Yes for copy-traded slots (RR-5). | Stagger products across accounts or accept forced DLL and Consistency-only XFAs. |
| P20/P21 coordinated trading with others, P28 trading for others | No: one user's accounts under one profile (P40, R001). | Never share the bot's signals with other Topstep traders. |
| P03/P07-P12/P13/P15/P17 unfair technology, SIM-fill exploitation, HFT | No: 1-3 round trips a day with holds of hours, D8 live-cost model (L-3). | Keep trade counts low and holds long; no edge from fills, queue or slippage. |
| P05 outside the BBO, P22/P23 price or feed exploitation, P24 spoofing, P25 platform deficiencies | No in the model; an implementation risk. | Marketable orders at the touch; signals may use external data, orders at TopstepX prices; no resting orders without intent. |
| P26 VPS/VPN, R042 | No (L-14: the bot runs on the user's machine). | Orders originate from the personal device; a server may only log. |
| P27 2% price-limit proximity | Rare for MES; not modelled. | Flatten when price is within 2% of the limit. |
| P34 position-size consistency | No: f x D sizing is proportional, not bursty (NOTE). | Keep sizing a smooth function of the drawdown distance. |
| P36 flat by 3:10 PM CT | No (RR-17). | Day-session windows all close by 15:00 CT. |
| P37 scaling-plan exceedance | No: the simulator caps at the tier read from the prior close (R034). | Correct any overage within 10 s. |
| P38/P39 discretionary rulings, payout denial; P14 cross-account forfeiture | A residual risk on every configuration; grows with churn (RR-1). | Carry a non-zero ruling risk in the recommendations. |
| P02, P41, P42, LFA items (R020-R023) | Not applicable or already consistent (no API on Live; copier lead = smallest MPS). | None. |

## Check 6: spot re-fetch

Five pages re-fetched 2026-10-10 17:52:10 to 17:52:28 PDT (00:52Z) by curl with a browser User-Agent, one request each, 4 s apart,
no link-following: pricing (S06), payout policy (S17), XFA parameters (S14), call-up (S19), prohibited strategies (S23). WebFetch was
not used because it cannot save a raw copy with a sha256 for the diff; the method is Task 1's, accepted in L-11. Log with UTC and PDT
times, HTTP codes and sha256: reports/stage_e19_verify/refetch_log.md; raw pages and my stdlib-stripped .txt under
reports/stage_e19_verify/pages/. Result in RR-18: S19 and S23 byte-identical to Task 1's copies (same sha256); S06, S17, S14 differ
in bytes but all 84 rule and practice quotes sourced to the five pages are present verbatim in the fresh text, the dollar and percent
figure multisets are identical, and dateModified is unchanged on all five.

## Unfinished or not verifiable

- No numeric threshold exists for "excessive" purchases, resets or XFA churn, for "high-frequency", or for the call-up; RR-1's policy
  band is a lead decision, not something the pages settle.
- The Express Funded Account Agreement and the Trading Combine terms are behind the activation flow (login); not fetched by Task 1 or
  by me, so any rule stated only there is unseen.
- The DLL discount on the $149 activation fee (RR-6) cannot be settled from public pages.

Closing time (from date): 2026-10-10 17:59:53 PDT (2026-10-11 00:59:53Z).
