## 2026-10-18 — Stage E.25: untapped sources research pass; four hypotheses clear the hurdle on paper, none confirmable on owned data; N = 538

Prompt docs/prompts/STAGE_E.25.md (V42), research only, run in parallel with Stage E.24. Return:
reports/E.25_RETURN.md; working files reports/stage_e25_briefs/; STATE reports/stage_e25_STATE.md. No market data
read, nothing bought, no quote requested, nothing registered; holdout unlocks_logged 0; REGISTRATION.md 0 bytes.

**What ran.** A shared brief (D8 hurdle table, Topstep rules, owned data, an index of every tested mechanism
reconciling N = 538), then 47 worker spawns in three waves: 13 topic readers (0DTE academic and vendor, order flow,
volume and trade side, news, scheduled events, live records, prop outcomes, prop rules, practitioners, communities,
regime filters, lead-lag), the user's six addenda (re-dig readers RD1-RD8 on E.13/E.20 sources; podcasts; niche and
non-US markets; a near-miss execution triage NM1/NM2 with Groups A and B; maker-native and queue/fill readers),
second readers DF1-DF3 on the shortlist, and ShortlistReviewer-FableXHigh. Two usage limits paused the stage
(02:01-06:10 and 06:35-11:15, the second with a laptop reboot); the planner moved the window twice (to 09:00/09:30,
then to 15:00/15:30, at most 6 workers). OpenAlex's daily budget and Firecrawl's credits ran out at about 01:47.

**Results.** Shortlist (published gross > 1.5 x D8, no prior trial duplicated): C1 noise-area intraday momentum on
MNQ (Zarattini, Aziz, Barbon 2024; about 38 MNQ ticks gross, ratio 9.3), C2/C3 the 3rd-Friday price spike
(Baltussen, Terstegge, Whelan; reversal 31 MES ticks; run-up from 17:00 CT, decayed after 2015), C4 the
pre-refunding-announcement ZN gain (Wang, Zhao; cash returns, FOMC-conditional), C5 the pre-FOMC ZN drift (Pan,
Peng). None is confirmable on the research window: power at published sizes 0.35 (C1, MNQ) and 0.11-0.22 (events);
C1's window is no longer blind (third-party tests cover it) and no independent S&P test after publication is
distinguishable from zero. Execution triage: Group A empty (no fade failed mainly on cost; trade-through fills leave
at most about 0.7 MNQ ticks of passive saving per side); Group B one weak candidate (a passive sell at the 3rd-Friday
open). Re-dig: supports nearly every closure; weakens V38's sentence and V34's reason for dropping noise-area
momentum; Topstep's Tier 1 news window (2026-10-10..16) overturns E.19's R040. Prop outcome data: Topstep's 2025
funnel pays about a third of funded individuals at least once.

**Verification.** Fable S4 review: BLOCK (C1 power on traded days; a mixed C2 row), 10 SHOULD FIX, 10 NOTE; all
applied; re-check READY. The lead's recomputed figures match the reviewer's to two decimals.

**For the user.** Whether to register a forward paper record of C1 on MNQ (recommended only as a cheap forward test,
not a research-window read); register nothing else; buy nothing; amend V38's and V34's wording; refresh Topstep's
rules record. Full list in the return, section 7. Open choices: 22, in the return, section 6.
