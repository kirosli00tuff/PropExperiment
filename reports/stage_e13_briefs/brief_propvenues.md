# Brief: PropVenues1-OpusHigh and PropVenues2-OpusHigh (Stage E.13 Task 1, prop firms)

Read reports/stage_e13_briefs/research_rules.md first and follow it. Your spawn message says whether you are
Part 1 or Part 2.

## Objective (one)
For each futures prop firm on your list, establish from the firm's own current pages whether an automated or
semi-automated futures system may hold positions overnight and for several days, and record the rules that
decide whether such a system can run there. The program (a solo Canadian trader in Vancouver, BC) is looking
for venues where a trend-and-carry style system holding positions for days (entries and exits a few times a
week, set by code) is allowed.

## Your firms
- Part 1: Topstep, Apex Trader Funding, Tradeify, Take Profit Trader, Elite Trader Funding,
  MyFundedFutures, Bulenox.
- Part 2: Alpha Futures, Lucid Trading, TradeDay, Earn2Trade, FundedNext Futures, Phidias Propfirm, The
  Trading Pit; then, with the time left, other reputable futures prop firms with a current offer that ADVERTISE
  overnight or swing holding (search for them; examples to check if they exist and are current: Aqua Futures,
  Funded Futures Network, Top One Futures, Purdia Capital, DayTraders.com, Leeloo, OneUp Trader, UProfit,
  TickTickTrader). Add at most 6 extra firms; prefer ones that allow overnight holding.

## Per firm, per plan (where plans differ)
1. Overnight and weekend holding: allowed or not, on which plans and account stages (evaluation, funded,
   live), any required flatten time, any news-event or weekend exception. Quote it.
2. Drawdown: type (end-of-day trailing, intraday trailing, static; when it locks) and size per account size.
3. Automation and API policy in the TERMS or rules (quoted): bots, algorithms, EAs, API trading, HFT.
4. The semi-automated, trade-copier or copy-trading wording (quoted), and any "you must actively monitor" text.
5. Platforms (Rithmic, Tradovate, NinjaTrader, TopstepX/ProjectX, etc.) and whether any API is documented.
6. Lot or contract limits (per account size; micros vs minis), scaling rules.
7. Payout rules: frequency, minimum days, consistency rule, caps, split.
8. Fees: evaluation price per account size, activation, monthly or data fees, reset.
9. Whether Canadian residents may join (restricted-country list; quote it, or "not stated").
10. Any news-trading rule.
11. The page date (or "no date shown") of every page used, and whether it is a help-centre/terms page or a
    sales page.

Topstep: the program already has reports/stage_e0_topstep_facts.json (2026-09-23) and
reports/stage_e12_topstep_150k.md (2026-10-03). Read them by grep for the fields above, re-check only the
overnight, automation and Canadian-residency fields against the current help centre, and cite the existing
files for the rest (their own sources and dates). Topstep is known to require flat by the session close; confirm
from the current page.

Phidias (Part 2 only): re-check docs/DECISIONS.md's 2026-09-28 entry (lines 270-309) against the current
Terms of Use and swing-account pages: quote the current automation clause and note any change from the entry.
Then draft reports/stage_e13_phidias_question.md: a short written question for Phidias support, for the USER
to send (you never send it), asking whether each of these counts as permitted "semi-automated software":
(A) software generates a signal and alerts the trader (e.g. by Telegram); the trader reads it and places the
order by hand in the platform; (B) the trader taps "confirm" on the alert, and the software then submits that
one order (with its attached stop and target bracket) through the platform connection; (C) after a confirmed
entry, the software manages the exit (moves the stop, closes at the target or after N days) without a further
tap. Also ask which platform connections allow order submission by the trader's own software on a Phidias
account, whether swing positions may be held over weekends and through scheduled news, and ask for the answer
in writing. Plain, polite, under 250 words. If another firm on either list allows overnight holding but its
automation wording is ambiguous, add a similar short question for that firm in the same file (Part 2 writes
the file; Part 1 lists its candidates in its report and Part 2 does not need to wait for them).

## Output
- Part 1: reports/stage_e13_venues_part1.md. Part 2: reports/stage_e13_venues_part2.md (and the question file).
- Format (both parts identical, so the lead can concatenate):
  1. A summary table, one row per firm and plan, these columns exactly:
     | Firm | Plan / sizes | Overnight + weekend | Drawdown type, size | Automation / API (terms) | Semi-auto / copier wording | Platforms | Lot limits | Payouts | Fees | Canada | News rule | Page dates |
     Each cell a short value plus source keys in brackets: Part 1 uses [P1-01], [P1-02]...; Part 2 uses
     [P2-01].... A cell with no source says UNSOURCED.
  2. A classification line per firm (and plan where it differs), exactly one of:
     PERMITTED (multi-day automated, unambiguous) / HUMAN-IN-THE-LOOP ONLY (multi-day allowed, automation only
     as semi-automated or with active monitoring) / NOT PERMITTED (overnight banned, or automation banned
     outright) / UNCLEAR (terms silent or conflicting), each with the one or two source keys that decide it.
  3. A source list: key | URL | fetched date | page date | page type (terms / help centre / rules / sales) |
     verbatim quote (short).
  4. Gaps and failures: what you could not establish and why.

## Stopping rule
Done when every firm on your list has all 11 fields filled or marked UNSOURCED with the reason, after at
least the firm's rules/help-centre page and its terms page were attempted. Do not spend more than about 6
fetch attempts on one field. Budget: aim for at most 120 WebSearch calls.

## Boundaries
Prop firms only. Brokers for a personal account belong to BrokerVenues; trend/carry evidence and sizing to
TrendCarry. Do not rank the firms beyond the classification line.
