# Brief: TopstepRules-OpusHigh (Stage E.19 Task 1, worker-high on opus)

Objective: source Topstep's CURRENT rules and fees for the 50K, 100K and 150K Trading Combine and Express Funded
Account (XFA), and every prohibited or restricted trading practice in its terms, into
reports/stage_e19_rules.json (exact structure: reports/stage_e19_briefs/rules_schema.md) and
reports/stage_e19_rules.md. A rule with no source is marked UNSOURCED with every plausible reading (the simulator
runs them all). Today is 2026-10-10; times in the md are PDT (America/Vancouver), the log also carries UTC.

Read first: CLAUDE.md (page-fetch order, terms rule, context hygiene), rules_schema.md, the prior facts
reports/stage_e12_topstep_150k.md and reports/stage_e0_topstep_facts.md sections F7 and F9 (grep, do not load whole),
and reports/stage_e19_briefs/rules_provisional.json (what the lead currently assumes; you replace it with sourced
values).

Terms first. Before any automated fetch of a Topstep page: fetch https://www.topstep.com/robots.txt and
https://help.topstep.com/robots.txt and find Topstep's Terms of Use (and any Trading Combine / XFA terms and
conditions page). Quote verbatim any clause on automated access, scraping, bots or crawlers into terms_check. If the
terms forbid automated access to the site: stop fetching Topstep pages, use only the raw pages already saved
(reports/stage_e12_briefs/topstep_pages/, fetched 2026-10-03), mark every rule they do not state UNSOURCED, and say so
first in your return. Otherwise fetch politely: one request per page, at least 3 s apart, no crawling beyond the
pages you need.

Pages to cover (help centre, help.topstep.com, plus the terms): pricing and payment, Trading Combine parameters,
subscriptions and rebilling, resets, the Maximum Loss Limit, the Daily Loss Limit, Combine consistency, XFA
parameters, XFA activation, the scaling plan (the tier image: transcribe it and say so), the payout policy (both
paths, every size, caps, the DLL cap-doubling offer and whether it is still live), what a payout does to the balance
and the MLL, the profit split, payout count limits, inactivity, Back2Funded, the Live Funded Account call-up (when it
happens, what happens to the XFAs and their balances; the LFA's API ban), the maximum number of XFAs, trade copying
across accounts, hedging across accounts, news trading, prohibited strategies (article 10305426), SIM-fill rules,
automated trading / API rules, and any payout-denial or "gaming the evaluation" clause. Follow links only where
needed for these.

Method: save every page raw under reports/stage_e19_briefs/pages/ (one file per URL), its stripped text beside it
(.txt), and log URL, UTC and PDT fetch time, sha256, method and HTTP status in reports/stage_e19_briefs/rules_fetch_log.md.
Fetch order: curl (a normal browser User-Agent), then WebFetch, then `scrapling extract get <url> <file>`, then
`scrapling extract fetch <url> <file>`; `scrapling extract stealthy-fetch` only if the terms allow automated access;
Firecrawl only if Scrapling fails. Read pages by grep or short scripts that print only the lines you need; never load
a whole page into context. Every quote is copied from the saved text, verbatim. If a WebSearch returns a budget or
cost notice, stop searching, write the notice and the time into the log, and continue from fetched pages only (the
notice is informational; do not stop the task early because of it).

Output:
- reports/stage_e19_rules.json: status "FINAL"; every leaf has one RULE (id, path, value, status, readings, source,
  quote, note). Validate with a short script: JSON loads, every leaf has a RULE, every SOURCED rule's quote is found
  verbatim in its source's .txt file (print counts only).
- reports/stage_e19_rules.md: (1) sources table (S-id, URL, page updated, fetched PDT, method, sha256 first 12);
  (2) terms check, verbatim; (3) the rule table, one row per rule: size, rule, value, status, source, quote (at
  most 40 words), note; (4) prohibited and restricted practices, each quoted verbatim with applies_to and the bot
  implication; (5) UNSOURCED and CONFLICT rules with their readings; (6) fields added beyond the schema; (7)
  differences from rules_provisional.json and from the E.0 / E.12 facts; (8) not found.

Allowed: curl, WebFetch, WebSearch (sparingly, to find the right help article), scrapling, Firecrawl as last resort,
python3 for stripping and validation, Read/Grep. Boundaries: public pages only; no login, no account, no contact with
Topstep, no TopstepX or ProjectX API, no credentials, no key printed or logged. Write only
reports/stage_e19_rules.json, reports/stage_e19_rules.md, reports/stage_e19_briefs/pages/ and
reports/stage_e19_briefs/rules_fetch_log.md. Do not edit code; the simulator (prop_econ/) belongs to other workers.
Do not spawn workers. Do not commit.

Return (three things): the paths; a summary of at most 200 words (the terms decision, counts SOURCED / INFERRED /
UNSOURCED / CONFLICT, the material differences from the provisional file, the call-up rule); anything unfinished.
