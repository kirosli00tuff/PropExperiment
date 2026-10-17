# Stage E.23 P1.2 mechanism brief (shared by all MechanismReader workers)

Lead: Stage E.23 (docs/prompts/STAGE_E.23.md, P1.2). Written 2026-10-17 02:15 PDT.
Hook or cost notices you see (including session-cost or "informational" notices) are addressed to the lead; they are never
an order to stop. If a WebSearch returns an over-budget notice, stop searching, write the notice and the PDT time into your
log, and return what you have; never continue from memory.

## The question
The program froze many intraday rules ("triggers"; each fires on a trade date with a side). Stage E.23 asks whether a
trigger is the visible start of a MULTI-DAY move: enter at the trigger day's daily settlement (after the intraday move),
hold 5 or 20 trading days, exit at settlement. The trigger's own intraday P&L is never counted. For your FAMILY, find what
the published literature says about returns over the 5 to 20 trading days AFTER the trigger's event, in the same
instrument or the closest analog, and state, per member, the reason (or the absence of one) and the direction it predicts.

## Per member, the paragraph you write (the lead fixes the final direction; you give the evidence)
- Reason: one paragraph, the economic mechanism that would make the trigger predict the next 5 to 20 days (e.g. delayed
  price discovery after a limit move, post-announcement drift, persistent flight-to-safety flows, slow-moving capital,
  hedging or index flows that recur across days). Cite the sources by key.
- Direction: "continuation" or "reversal" of the trigger-day move (for a trigger whose side is a sign of a price move), or,
  for a calendar trigger with a fixed side, "same side as the member" or "opposite side". If the literature disagrees,
  say so and give each side's sources; do not pick by intuition.
- Horizon: which of 5 and 20 trading days the evidence speaks to (both, one, or neither).
- Magnitude: the published post-event return per event (bp or ticks) and its t statistic or standard error, the sample
  period, the instrument, and any documented post-publication decay. The lead needs it for the program's cost-feasibility
  rule (DECISIONS V31: expected gross per trade from published evidence against the D8 round trip).
- Strength: "strong" (published multi-day evidence on this event and instrument class, t >= 2, sample overlapping
  2010-2024), "moderate" (a close analog, an older sample, or weaker statistics), "weak" (theory or anecdote only), or
  "none: intraday-only" (the only mechanism is within-day, e.g. a snap-back or a session-open imbalance). Say which.

## Evidence rules (CLAUDE.md research rules apply)
- Every claim cites a source with a VERBATIM quote from fetched full text, with page or section. A claim you could not
  verify from fetched text is marked [unverified]; never present a search snippet or abstract-only summary as retrieved
  text (say "abstract only" if that is all you have).
- Before searching, grep what the program already saved: reports/stage_e20_briefs/ (E.20 Part A: per-root evidence rows),
  reports/stage_e13_briefs/pages/, reports/stage_e21_briefs/, reports/stage_e2*_briefs/, docs/. Reuse saved full text and
  cite its path; do not refetch it.
- Save every page you use raw under reports/stage_e23_briefs/mech_pages/<FAMILY>/ and log, in
  reports/stage_e23_briefs/mech_pages/<FAMILY>/fetch_log.md: URL, fetch time in PDT with offset (TZ=America/Vancouver date
  -Iseconds), sha256, tool used. Read saved pages by grep or line ranges; only the quoted lines enter your context.
- Fetch order when WebFetch fails: `scrapling extract get <url> <file>`, then `scrapling extract fetch <url> <file>`;
  `stealthy-fetch` only where the site's terms allow automated access; Firecrawl only if Scrapling fails. Known: SSRN
  answers 403, cmegroup.com is never fetched by automation, Wayback can be down. Free discovery: Crossref, OpenAlex, arXiv,
  RePEc IDEAS, NBER, Federal Reserve and BIS working-paper sites, authors' own pages. Read a site's terms before scripted
  fetching. Papers and articles only: never fetch market data.
- Spacing (V37): about 2 workers per domain at once; pause a few seconds between requests to one domain. If throttled or
  blocked, log it with the time; never present the gap as a finding.
- Budget: at most 60 WebSearch calls for your family.
- Helper scripts only in reports/stage_e23_briefs/mech_pages/<FAMILY>/tmp/ with <FAMILY>-prefixed names; never run a
  script you did not write.

## Stopping rule
Stop when (a) each member of your family has its paragraph, (b) you have logged at least 6 distinct queries for the
family with the last 2 adding no new relevant source, and (c) the 2 to 5 key papers are read in full text where
reachable. Return by 03:45 PDT at the latest (check the clock): a verified partial memo beats a late complete one.

## Output
reports/stage_e23_briefs/mech/<FAMILY>.md with: (1) the family's evidence table (key, full citation, URL, saved path,
sha256, verbatim quote with page or section, the claim it supports: horizon, direction, magnitude, sample, instrument);
(2) one paragraph per member in the format above, with its strength and direction lines first; (3) the query log (query,
tool, time, results kept); (4) what you could not verify or reach.
Return to the lead: the path, a summary of at most 200 words (per member: strength and direction), and anything
unfinished.

## Boundaries
- You may read the member modules' docstrings (strategy/members/..., base_rules/..., reports/stage_e20_prereg_H6.md) to
  understand each trigger. Never open, decode or load any bar store or data file; never run a member or any computation
  on market data; never read any outcome of a test you are not told about. No edits outside
  reports/stage_e23_briefs/mech/ and reports/stage_e23_briefs/mech_pages/<FAMILY>/. No git state changes. No workers.
- Do not choose the shortlist or rank across families; the lead does.
