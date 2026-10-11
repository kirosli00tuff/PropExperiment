# Brief: RulesReviewer-FableXHigh (Stage E.19 Task 5a, worker-xhigh on fable)

Objective: independently check the Topstep rule table that every E.19 number rests on, and the terms constraints on
the modelled bot. You did not write it; assume it may be wrong. Grade findings BLOCKING (a wrong or unsupported value
or reading that changes a modelled cash flow or rule, or a prohibited practice the model or the recommendations
would breach), SHOULD FIX, or NOTE.

Inputs: reports/stage_e19_rules.json and reports/stage_e19_rules.md (TopstepRules-OpusHigh); the raw pages it saved,
reports/stage_e19_briefs/pages/ (and their .txt), with its fetch log reports/stage_e19_briefs/rules_fetch_log.md;
the schema reports/stage_e19_briefs/rules_schema.md; the model reports/stage_e19_briefs/sim_spec.md (what the
simulator does with each rule) and the lead's decisions in reports/stage_e19_STATE.md.

Checks:
1. Quotes: for every SOURCED rule, the quote appears verbatim in the cited saved page (script it; print counts and
   the failures only), and the value follows from the quote for that account size (read the failures and a stratified
   sample of at least 30 passes by hand, including every fee, target, MLL, cap, split, scaling tier and payout-path
   rule).
2. Coverage: every item of the prompt's Task 1 list (Combine price and billing, reset price, profit target, MLL and
   its trailing rule, DLL, Combine consistency, minimum days, activation fee and options, the XFA trailing drawdown and
   lock, scaling plan, winning-day definition, Standard and Consistency paths, caps, split, payout count limits, what a
   payout does to balance and drawdown, inactivity, Back2Funded, the Live Funded call-up, the maximum number of XFAs)
   has a rule; INFERRED and UNSOURCED statuses are justified; every plausible reading of an UNSOURCED rule is listed.
3. Freshness and authority: each value comes from Topstep's help centre or terms (not a marketing page or a third
   party); conflicts between pages are recorded with the stricter reading first.
4. Terms: the terms check (robots.txt, automated-access clause) is quoted and the fetch method respected it.
5. Prohibited practices: the list is complete against the saved terms and help pages (search them for: stacking,
   hedg, copy, multiple accounts, news, HFT, high-frequency, automat, algorithm, bot, API, simulat, exploit, gaming,
   abuse, gambl, consistency, payout denial, Live Funded). Then judge the modelled bot against each: a day-session
   hold of one product, 1 to 3 round trips a day, risk f x D with f in 0.05..0.25 (0.35 and 0.50 diagnostic only),
   new Combines bought after failures, up to five XFAs, possibly the same bot on several accounts. Say for each
   practice whether the model or a plausible recommendation could breach it, and how a bot avoids it.
6. Spot re-fetch: re-fetch at most 5 key pages yourself (pricing, payout policy, XFA parameters, the call-up page,
   prohibited strategies), politely, by the CLAUDE.md fetch order, saved under reports/stage_e19_verify/pages/, and
   diff the key figures against the saved copies.

Output: reports/stage_e19_review_rules.md (findings table: id RR-n, grade, rule or practice, finding, evidence with
the quote and file, suggested fix; then a section per check). Write nothing else outside reports/stage_e19_verify/.
Boundaries: public pages only; no login, account, contact with Topstep, TopstepX or ProjectX API, or credentials; no
edits to code or to the files you review. If a WebSearch returns a budget or cost notice, log it with the time and
continue from the saved pages. Do not spawn workers. Do not commit.

Return (three things): the path; a summary of at most 200 words (counts by grade, every BLOCKING finding in one
line each); anything unfinished.
