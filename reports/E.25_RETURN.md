# Stage E.25 return: untapped sources, a deep research pass for a prop-compatible intraday edge

Prompt: docs/prompts/STAGE_E.25.md (research only; V42). Lead: Opus 5.5, xhigh, ultracode. Session 37fc9660-82d1-49fd-be83-50b822ab0a5b. Times PDT. Every working file is under reports/stage_e25_briefs/; STATE in reports/stage_e25_STATE.md.

## 1. Summary

Stage E.25 read what earlier passes had not (0DTE and dealer gamma, order flow, news, scheduled events, live
records, prop outcome data and rules, practitioner work, communities, podcasts, niche markets, limit-order
execution) and re-dug the E.13 and E.20 sources (user addenda 1-6). No market data was read,
nothing was bought or registered, and N stays 538.

**Shortlist** (published gross clears 1.5 x the D8 round trip; no prior trial duplicated):
- C1: noise-area intraday momentum on MNQ (Zarattini, Aziz, Barbon 2024): about 38 MNQ ticks gross, 4.1-tick RT.
- C2/C3: the 3rd-Friday price spike (reversal leg 31 MES ticks; run-up leg from 17:00 CT).
- C4: pre-refunding-announcement ZN gain.
- C5: pre-FOMC ZN drift.

None can be confirmed on the research window. At the published sizes, power is 0.35 for C1 and 0.11-0.22 for the
event effects (0.06-0.17 at the post-2015 sizes).

**Strongest single lead: C1, and it is weak.** No independent S&P test since publication is distinguishable from
zero, and the latest are negative. The one positive Nasdaq test is a pointer (t 1.37). Third-party results already
cover the research window. Its drawdown at 1 MNQ exceeds the 50K and 100K trailing limits.

**Execution triage:** Group A is empty; Group B has one weak candidate; trade-through fills leave at most about
0.7 MNQ ticks of passive saving per side.

**Re-dig:** supports nearly every earlier closure; weakens V38's sentence (three rare working-paper effects) and
V34's reason for dropping noise-area momentum. Topstep's new Tier 1 news window
overturns E.19's R040.

**For the user to decide:**
- Whether to register a forward paper record of C1 on MNQ (recommended only as a cheap forward test, never as a
  research-window read).
- Register nothing else and buy nothing.
- Amend the wording of V38 and V34.
- Refresh the Topstep rules record.

## 2. Guardrail evidence

Script: reports/stage_e25_briefs/checks.sh (no pytest: E.24 owns the suite). Every line is quoted verbatim; `git status --short` prints its tracked lines and the count of untracked (`??`) lines, which are raw pages of earlier stages and this stage (Open choice 6).

### 2.1 Start checks

```
$ date
Sun Oct 18 01:28:07 PDT 2026
$ git status --short (tracked lines; untracked count)
untracked: 1271
$ git log --oneline -3
0023572 docs: Stage E.24 (forward plumbing) and E.25 (untapped sources) prompts, V42
f36a33a docs: V41 (E.23 accepted, direction closed, loader fix approved)
ef2902d Stage E.23 triggers at multi-day holds
$ uv run python -m data.holdout status (keys)
top all_ok True unlocks_logged 0 unlock_log_ok True
holdout_2 all_ok True unlocks_logged 0 unlock_log_ok True
MCL all_ok True unlocks_logged 0 unlock_log_ok True
MGC all_ok True unlocks_logged 0 unlock_log_ok True
MHG all_ok True unlocks_logged 0 unlock_log_ok True
NG all_ok True unlocks_logged 0 unlock_log_ok True
$ wc -c REGISTRATION.md
0 REGISTRATION.md
$ spend ledger: wc -l; sha256sum
36402 ledger/databento_spend.jsonl
034a454b49f2d9c93f3ff8872a5fb322cd351de57a7d73842d08f5d07d94c700
$ uv run python -m screening.trial_registry status
N = 538 (9 lines)
r008-E23: E23 ['E23-MEZFh5', 'E23-MEZNh5', 'E23-MEZBh5', 'E23-H6NQh5', 'E23-H6NQh20'] N 533 -> 538 at 2026-10-17T03:33:45-07:00
$ trial ledger: wc -l ledger/trial_registrations.jsonl; sha256sum
9
25c04088fed9b1a2bd14a79512bedc8ab9764611aa2abd95e2a29829542aa302
```

### 2.2 End checks

```
$ date
Sun Oct 18 11:54:36 PDT 2026
$ git status --short (tracked lines; untracked count)
 M docs/STAGES.md
 M progress.md
untracked: 1318
$ git log --oneline -3
0023572 docs: Stage E.24 (forward plumbing) and E.25 (untapped sources) prompts, V42
f36a33a docs: V41 (E.23 accepted, direction closed, loader fix approved)
ef2902d Stage E.23 triggers at multi-day holds
$ uv run python -m data.holdout status (keys)
top all_ok True unlocks_logged 0 unlock_log_ok True
holdout_2 all_ok True unlocks_logged 0 unlock_log_ok True
MCL all_ok True unlocks_logged 0 unlock_log_ok True
MGC all_ok True unlocks_logged 0 unlock_log_ok True
MHG all_ok True unlocks_logged 0 unlock_log_ok True
NG all_ok True unlocks_logged 0 unlock_log_ok True
$ wc -c REGISTRATION.md
0 REGISTRATION.md
$ spend ledger: wc -l; sha256sum
36402 ledger/databento_spend.jsonl
034a454b49f2d9c93f3ff8872a5fb322cd351de57a7d73842d08f5d07d94c700
$ uv run python -m screening.trial_registry status
N = 538 (9 lines)
r008-E23: E23 ['E23-MEZFh5', 'E23-MEZNh5', 'E23-MEZBh5', 'E23-H6NQh5', 'E23-H6NQh20'] N 533 -> 538 at 2026-10-17T03:33:45-07:00
$ trial ledger: wc -l ledger/trial_registrations.jsonl; sha256sum
9
25c04088fed9b1a2bd14a79512bedc8ab9764611aa2abd95e2a29829542aa302
```

### 2.3 Order of events (PDT, from `date`, file times and the STATE log)

| Time | Event |
|---|---|
| 01:27-01:28 | Start checks (start_checks.txt): holdout all_ok, unlocks_logged 0; REGISTRATION.md 0 bytes; N 538 |
| 01:29-01:36 | R0 shared brief (lead); R0a mechanism index (MechIndexer-SonnetMed, 01:32-01:38) and R0b prior sources and E.20 evidence index (PriorSources-HaikuMed, 01:32-01:34) |
| 01:33 | User addendum 1 (all research tools; re-dig readers) |
| 01:38 | Wave 1: R1-R13 and RD1-RD7 (two workflows, 20 readers) |
| 01:40-01:56 | User addenda 2-6 (podcasts; niche markets; near-miss triage; Groups A/B; limit-order readers) |
| 01:46-01:47 | OpenAlex daily budget and Firecrawl credits exhausted; brief section 7 updated 01:57 |
| 01:52-01:59 | RD5, R11, R10, R13, RD7, R12 done; NM1, R17, R18, R14, R15, R16 launched as slots freed |
| 01:58-02:01 | First usage limit: every running worker stopped |
| 02:01-06:10 | Pause (usage limit), not work time |
| 06:11-06:17 | Resume: NM1, R14-R18 resumed by message; fresh R1 and R5; all returned 06:15-06:17 |
| 06:18 | Planner: work to 09:00, return by 09:30 |
| 06:19-06:22 | Synthesis v1 and s2_power.py (lead); wave 2 launched (10 agents) |
| 06:28-06:35 | R6, R2 done; RD8 and DF3 (md), R8 (json) written; second usage limit cut the rest at about 06:35 |
| 06:35-11:10 | Pause (usage limit; laptop reboot about 10:50), not work time |
| 11:15-11:18 | Resume (planner 11:16: work to 15:00, return by 15:30, at most 6 workers); wave 3 launched (DF1, DF2, NM2, RD3, RD6, FileFinisher) |
| 11:19-11:30 | FileFinisher, RD6, DF1, RD3, DF2, NM2 done; synthesis v2 written and corrected |
| 11:30 | S4 ShortlistReviewer-FableXHigh launched |

## 3. Results

The synthesis (S1-S3, the execution triage of addenda 4-5, the re-dig section of addendum 1, the prop landscape), as reviewed and fixed (section 5), follows; per-reader source lists close the section.


Written by the lead against docs/prompts/STAGE_E.25.md and the user's six addenda. Inputs (all under
reports/stage_e25_briefs/): complete readers R1 (rerun), R2, R5 (rerun), R6, R8, R9, R10, R11, R12, R13, R14, R15,
R16, R17, R18; second readers DF1, DF2, DF3; re-digs RD3, RD4, RD5, RD6, RD7, RD8; NM1 and NM2 (merged 11:30);
partial files cut by the first usage limit at about 01:58 PDT and cited as cut: R3, R4, R7, RD1, RD2. Arithmetic:
s2_power.py, output s2_power.out (published sizes, then post-2015 sensitivity). Hurdle (V31, V38): published gross
per trade > 1.5 x the D8 round trip (RT). Ratio = gross / RT; the hurdle is ratio > 1.5.

### S1. Candidate table (one row per distinct hypothesis)

Quality: PR peer-reviewed, WP working paper, TH thesis, V vendor, LR live record, P pointer. RW = research window
2025-04-01..2026-06-19 (299 equity trade dates). Prop = Topstep unless stated: flat before 15:10 CT; DLL;
trailing max loss $2,000/$3,000/$4,500 (50K/100K/150K); Tier 1 news window 5 min either side of CPI, NFP, FOMC
decision and press conference (R9: minis blocked, index and metals micros capped, pending orders not filled);
automation via API, no HFT.

| # | Hypothesis (readers) | Best evidence (quality) | Instrument, horizon | Published gross -> micro ticks (conversion) | RT ticks | Ratio | Data; owned; cost | RW testable | Prop | Overlap with the 538 (named) | Lead rank |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Noise-area intraday momentum (R10-C1, DF1) | Zarattini, Aziz, Barbon 2024, v2025-09 (WP): SPY 2007-05..2024-04, $0.09/share net at $247 = 3.64 bp net, about 4.0 bp gross (if the paper's 7,668 "trades" are fills, per round trip about 8 bp: DF1; replications run 0.8-0.9 round trips a day); daily t 5.34 over 2,620 traded days (about 61% of the 17-year sample); futures table S&P SR 1.32, Nasdaq 1.23 (cost unstated). Post-publication (DF1): no independent S&P test is distinguishable from zero and the most recent are negative (Brusco ES -0.61 bp/trade, P; VigorTas ES t -1.21, P; Paz OOS SR 0.39, t 0.54; Delgado SR -0.46 for 2025-09..2026-08 [secondary-only]); VigorTas NQ at MNQ cost about 41 MNQ ticks/trade, t 1.37 (P: code checkable, data not shared) | MNQ (MES ref.), 09:00-15:00 CT | 4.0 bp at NQ 24,000 = 9.6 pts = 38.4 MNQ ticks (NQ 21,000-25,000: 33.6-40.0); at ES 6,000 = 9.6 MES ticks | 4.119 MNQ; 2.03 MES | 9.32 (8.16-9.71); 4.73 | 1-min bars; owned; $0 | yes, but NOT blind: third-party results already cover 2025-2026 (DF1) | intraday; worst drawdown at 1 MNQ $3.4k [secondary-only, Chuk abstract] to $4.25k (VigorTas, P) exceeds the 50K and 100K trailing max loss | never tested; V34 dropped it as "unsized" (the basis is weakened: R10, DF1); nearest K1-vwap-01 (C1's trailing stop uses VWAP), K1-cp2-01, B-H1/RT1-RT4, E20H6-T1 | 1 |
| 2 | 3rd-Friday spike, reversal leg: short MNQ/MES at the 08:30 CT open of the monthly a.m.-settlement Friday (RD4, R12, DF2) | Baltussen, Terstegge, Whelan (WP; January 2024 AFA copy read by DF2; the August 2026 version, sample to 2023, drops the futures table): ES Table II -12.89 bp, t -2.40, sd 80.45 bp, 2003-2021 (verified, DF2); 2015-23 17.6 bp, 2022-23 14.8 bp (digitized, not significant per subperiod); about 70% of the reversal in 08:30-09:00 CT, complete by about 10:30 CT; carried by quarterly expiries (-37 bp vs -6 bp off-quarter, SOQ basis) | MNQ/MES, 08:30 -> 10:30 or close | 12.89 bp x 6,000 / 10,000 / 0.25 = 30.9 MES ticks; NQ (DF2 figure) -12.5 bp in 30 min | 2.03 MES | 15.24 | 1-min bars + expiry calendar; owned; $0 | yes: 15 monthly expiries in the RW, 5 quarterly; 2025-04-17 and 2026-06-18 are Thursday expiries (DF2) | compatible | nearest: A-H4 rth leg (MES 08:30-15:00 every day) and D-H4 (overnight-gap fade at the first bar, 30 min), both unconditional; E-H3 (MES quarterly witching short 14:30-15:00) differs: open window, monthly | 2 |
| 3 | 3rd-Friday spike, run-up leg: long 17:00 CT Thursday -> 08:30 CT Friday (RD4, R12, DF2) | same paper: Thu close -> Fri open +14.30 bp, t 3.54, sd 60.53; none accrues 15:00-17:00 CT (-0.6 bp), +12.75 bp from 17:00 CT (DF2); decayed: 26.2 bp (2003-14), 4.2 (2015-23), 1.6 (2022-23) | MNQ/MES, inside one Topstep day | 14.30 bp -> 34.3 MES ticks (full sample); 4.2 bp -> 10.1; 1.6 bp -> 3.8 | 2.03 | 16.91 (published table, upper bound for a 17:00 CT entry); 15.07 (17:00 CT leg, digitized); 4.97 (2015-23); 1.89 (2022-23) | as row 2 | yes, n 15 (10 if quarterly dates are blacked out) | compatible | nearest: A-H4 eth leg (MES session-open hold about 15.5 h, the same 17:00 CT -> 08:30 CT window, every day, unconditional); E-H1, A-H1 differ in calendar and window | 4 (decayed) |
| 4 | Pre-refunding-announcement Treasury gain: long ZN over the NY session of the trading day before the quarterly refunding announcement (RD2, DF3) | Wang, Zhao 2025 OSF draft (WP): 10-year CASH +12.62 bp, t 3.32, N 129 (verified); 9.40 bp (SE 4.03) with day-of-week and month-end fixed effects; intraday result only as a figure; "present almost exclusively when an FOMC announcement occurs within the preceding five days" (DF3) | ZN, one session | 12.62 x 0.69 (futures/cash) x 111 / 10,000 x 64 = 6.19 ZN ticks; FE 9.40 -> 4.61 | 1.168 | 5.30; FE 3.94 | ZN bars owned; dates public | partial: 5 events, 3 FOMC-conditional (TRAs 2025-11-03, 2026-02-02, 2026-05-04); NOT blind on 2 of the 3 (K2-monthend-01's recorded research-window ZN trades cover the pre-TRA days 2025-10-31 and 2026-01-30) | compatible; 1 ZN = $15.625/tick | nearest K2-monthend-01 (long ZN on month-end dates N-1 and N, 07:20-15:04 CT; WZ's own month-end fixed effect cuts 12.63 to 9.40 bp, so part of the effect is month-end); K2 auction members and E16-H3 use auction dates | 5 |
| 5 | Pre-FOMC Treasury drift: long ZN 18:00 CT day -2 -> 11:00 CT day -1 (RD2, DF3) | Pan, Peng 2026 SAIF draft (WP): 10-year FUTURES +7.26 bp, t 2.82, 2004-01..2025-06 (verified); December 2025 draft 6.9 bp, t 2.24; window read off the authors' figure (Tokyo open to London close) | ZN, 17 h inside one Topstep day | 7.26 x 111 / 10,000 x 64 = 5.16 ZN ticks | 1.168 (D8 book data: same RT at 18:00-18:30 CT, a third of the depth, DF3) | 4.42 | owned | yes, n 10 | compatible | K2-fomcpost-01, K5-fomc-01, E-H1 differ in asset or window | 3 |
| 6 | FOMC pre-announcement reversal, 12:50-14:50 CT (R6-C3, RD6) | Baglioni-Ribeiro thesis (TH): 23.34 bp per event net of spread, 71 events 2011-2020; nothing after 2020-01; zero citers in OpenCitations (RD6; can be an index gap) | MES/MNQ | 23.34 bp (net of spread, used as gross: conservative) -> about 56 MES ticks | 2.03 | about 27 | owned; FOMC dates owned | yes, n 10 | crosses the 13:00 CT statement: Tier 1 window blocks or caps entries 12:55-13:05 CT and pending orders do not fill | E-H1, E-H2, K9-anncday-01 draft differ in window | 6 (thesis grade) |
| 7 | FOMC press-conference fade or continuation (R5-C1, R6-C1) | Narain-Sangani IJCB 2026 (PR): sign reversed across regimes (continuation 2011-2020, reversal after COVID, n about 16) | MES/MNQ, 13:36-15:00 CT | not a per-trade figure (R6 derives about 260 MNQ ticks from a slope) | - | - | owned | yes, n 10 | Tier 1 window moves entry to 13:36 CT | E-H2, K2-fomcpost-01 | not shortlisted (sign unstable, unsized) |
| 8 | Gamma-proxy (5-day RSI) overlay on row 1 (R2-C2) | Beat the Market section 4.5 (WP), in-sample beta -3.25 | MNQ | overlay, no per-trade figure | - | - | owned | yes | as row 1 | as row 1 | not shortlisted (adds a fitted parameter) |
| 9 | First-half-hour momentum on high-volatility or volume days (R12-C3, R4) | Gao, Han, Li, Zhou JFE 2018 (PR): 5.85 bp, t 3.80, SPY 1993-2013, full-sample terciles | MES/MNQ, 14:30-15:00 CT | 14.0 MES ticks | 2.03 | 6.90 | owned | yes | compatible | duplicates K1-cp1-01, E20H6-T1/T2 (FAIL) | not shortlisted (duplicate) |
| 10 | FOMC-day first-30-min momentum into the last 30 min (R12-C4) | R12 source (WP) | MES | 19.1 MES ticks (reader) | 2.03 | 9.41 | owned | partial | compatible | K1-cp1-01, E-H1/E-H2 | not shortlisted (duplicate family) |
| 11 | Conditional overnight drift (buy the dip), 01:30-03:30 ET (R13-C1, R15) | Boyarchenko, Larsen, Whelan RFS 2023 (PR) | MES | about 11.7 MES ticks (reader) | 2.03 | 5.76 | signed close volume not owned | partial | compatible | A-H1 (FAIL) | excluded: authors (2026) "averaged close to zero since 2021" |
| 12 | 5-minute ORB, 10R target (R10-C3) | Zarattini, Aziz 2023 (WP), in-sample, zero slippage | MNQ | at least 23.8 MNQ ticks (derived bound) | 4.119 | at least 5.8 | owned | yes | compatible | duplicates B-H1, RT1-RT4, H1/H3/H4, K1-cp2-01; Mesfin 2026 walk-forward T 0.88 | not shortlisted |
| 13 | ATR-band breakout (R10-C2) | Concretum note 2026 (V) | MES/MNQ | unsized | - | - | owned | yes | compatible | D-H3, B-H4 | not shortlisted |
| 14 | Fixed-percent ORB on crude (R10-C4) | Holmberg et al. FRL 2013 (PR), 1991-2011 | MCL | 13 MCL ticks | 3.167 | 4.10 | owned | yes | compatible | K4-cp2-01 | not shortlisted ("not robust to time") |
| 15 | API-to-EIA crude predictability (RD3-C2) | Alturki-Kurov JFM 2022 (PR), 2011-2019 | MCL | 4.5 MCL ticks | 3.167 | 1.42 | owned | yes | compatible | re-parameterizes K4-apipre-01 (FAIL) | not shortlisted (below hurdle) |
| 16 | Rates-to-gold after FOMC (RD3-C1) | reader's own construction | MGC | upper bound 10.5 MGC ticks at $1,800/oz (14.0 at RD3's higher price level) | 4.086 | 2.57-3.43 (bound) | owned | yes | Tier 1 caps metals micros | K5-fomc-01 | not shortlisted (not a published rule) |
| 17 | GMM regime entries on MNQ (R12-C5/C6, RD1-C1) | Mesfin arXiv 2026 (WP, one unreviewed author, 53+ combinations) | MNQ | 24.4-55.3 MNQ ticks | 4.119 | 5.9-13.4 | owned | yes | compatible | A-H1, C-H1, D-H1/D-H3 | not shortlisted (specification search) |
| 18 | 0DTE-era gamma-conditioned reversal (R1-C1) | Adams et al. 2026 (WP): 1-2 bp, 10 min-2 h, top net-gamma quartile | ES | 2.4-4.8 MES ticks | 2.03 | 1.2-2.4 | Cboe intraday Open-Close: $1,000 per data-month at 10-min (R2), not owned | no | compatible | C2, E20H6-T3 | not shortlisted (authors: not feasible; net gamma unobservable) |
| 19 | SpotGamma Put Wall breach (R2-C1) | vendor (V), +14 bp 1-day, no n | ES | overnight hold | - | - | not owned | no | not Topstep (overnight) | - | not shortlisted |
| 20 | Liquidity-sweep reversal; value-area 80% rule (R11-C1/C2) | communities (P); Osler 2002 points to continuation | MES/MNQ | unsized | - | - | owned | yes | compatible | B-H2, G5.RTH, H5; F6_1, D-H4 | not shortlisted |
| 21 | Minute-scale order-flow imbalance (R3-C1/C2) | CKS 2014, CCZ 2023 (PR); ES OFI shocks die within 1 s | MES/MNQ | no per-trade gross at 1-30 min | - | - | MBP-10 not owned | partial | HFT ban at the working horizon | D.1g C6 | not shortlisted |
| 22 | Signed market-maker SPX position change (RD5-C1) | Egebjerg-Kokholm (WP) [secondary-only] | ES | unsized | - | - | paid | no | compatible | E20H6-T3, C2 | not shortlisted |
| 23 | GEFS forecast revisions traded intraday on NG (RD6-C1) | pointer; no intraday gross published | MNG | unsized | - | - | free (AWS from 2017) | partial | compatible | C1/C1b | not shortlisted (fails V31 gate) |
| 24 | DAX / Nikkei first-half-hour momentum (R15-C1/C2) | Li, Sakkas, Urquhart JFM 2022 (PR), 2005-2017 | FDXS / OSE | 3.9 Micro-DAX ticks; 1.4 OSE ticks | not D8 (IBKR FDXS 0.38 EUR/side fees, spread unverified, R16) | - | not owned (Databento Eurex only from 2025-03-10) | no | Phidias lists Eurex (semi-automated); Topstep CME only | same mechanism as K1-cp1-01/E20H6 | not shortlisted |
| 25 | Expiry-day pinning (R17-C2) | Golez, Jackwerth 2012 (PR), to 2009 | ES | aggregate 11 bp | - | - | owned | yes | compatible | E-H3 | not shortlisted |
| 26 | Large-tick fast trend (RD7-C1) | Kurth et al. 2026 (WP) | rates/ags, multi-day | unsized | - | - | owned | - | not Topstep | E21-T1/T2, E22-F1 | not shortlisted |
| 27 | Collective2 "ares" MNQ intraday (R7) | C2 page (LR, C2 labels it hypothetical; rules private) | MNQ | about 37.6 ticks/contract (crude) | 4.119 | - | - | - | - | K1-cp2-01/K1-vwap-01/E20H6 family | existence only |

### S2. Shortlist

Four hypotheses clear the hurdle on published numbers and duplicate no prior trial (S4 checked rows 1-5 against
the index): C1 (row 1), C2 (row 2), C5 (row 5), C4 (row 4); C3 (row 3) is kept as C2's second leg but its
post-2015 size is near the hurdle. The designs register five trials (C1, C2, C3, C4, C5). Power is at the
PUBLISHED size on the research window (s2_power.out v2), one-sided 5% and the first Holm step for k = 5
(alpha 0.01); the sensitivity column uses the verified post-2015 or later-draft sizes. C1's dispersion is per
traded day (about 183 expected traded days in the window). C2/C3 events: the 15 monthly expiries (two shifted to
Thursday), 10 if the roll blackout removes the 5 quarterly dates.

| S2 | Hypothesis | Ratio | n on RW | E[t] | Power 5% | Power Holm-5 | Post-2015 / later-draft sensitivity |
|---|---|---|---|---|---|---|---|
| C1 | Noise-area momentum, MNQ (MES ref.) | 9.32 at NQ 24,000 (MES 4.73 at ES 6,000) | about 183 traded days of 299 | 1.26 (1.11) | 0.35 (0.30) | 0.14 (0.11) | no independent S&P test after publication distinguishable from zero, the latest negative; NQ pointer +41 ticks, t 1.37 |
| C2 | 3rd-Friday reversal leg | 15.24 | 10-15 | 0.47-0.58 | 0.12-0.14 | 0.03-0.04 | 14.8 bp (2022-23, digitized), n 15: 0.17; off-quarter only -6 bp SOQ basis |
| C3 | 3rd-Friday run-up leg from 17:00 CT | 15.07 (17:00 CT leg, digitized); 16.91 published upper bound | 10-15 | 0.62-0.76 (0.70-0.86) | 0.15-0.19 (0.17-0.22) | 0.04-0.06 (0.05-0.07) | 4.2 bp: 0.08; 1.6 bp: 0.06 |
| C4 | Pre-refunding ZN, as designed (FOMC-conditional) | 5.30 (conditional cell 23.65 bp: 9.93) | 3 | 0.41 (0.85) | 0.11 (0.21) | 0.03 (0.07) | FE 9.40 bp: 0.08; unconditional n 5: 0.13 |
| C5 | Pre-FOMC ZN drift | 4.42 | 10 | 0.53 (sd inferred, N about 171) | 0.13 | 0.04 | 6.9 bp, t 2.24 draft: 0.11 |

**The research window cannot confirm any of them.** The best power is C1's 0.35 at its published size, and DF1
shows that no independent S&P test after publication is distinguishable from zero and that third-party tests
already cover the research window, so a C1 read of it would not be blind. Every event candidate has power of
0.11-0.22 at its published size (0.06-0.17 at the post-2015 or fixed-effects sizes).

Draft test designs (one paragraph each; every parameter is the published one; nothing is chosen from data):

- **C1 noise-area momentum (MNQ).** The rule exactly as published (14-day mean absolute move from the open by
  minute; bands from max/min(open, prior close); checks on the :00 and :30 bars from 09:00 CT; long above the
  upper band, short below the lower; trailing stop at the band or VWAP; flat 15:00 CT), 1 MNQ, market orders at
  D8 cost, roll blackout set, through `screening.screen_candidate`; one registered trial. Because the research
  window is no longer blind for this rule (DF1), the clean read is FORWARD: a frozen paper record from the
  registration date (as E22-F1), with the bar net mean per day t >= 1.645 one-sided after a fixed number of days
  set from the published Sharpe before the first day (at the published size 250 trading days give power about
  0.31 on MNQ and 0.27 on MES; power 0.8 needs about 1,165 trading days on MNQ (4.6 years) and about 1,490 on MES; at the post-publication S&P evidence,
  near zero). The worst drawdown at 1 MNQ ($3.4k [secondary-only] to $4.25k [P], DF1) rules out the 50K and
  100K accounts; only 150K ($4,500) fits, barely.
- **C2/C3 3rd-Friday spike (MNQ).** Monthly a.m.-settlement Fridays from the Cboe calendar (holiday rule: the
  expiry moves to Thursday, 2025-04-17 and 2026-06-18); C3 long 1 MNQ from the 17:00 CT reopen the evening before
  to the 08:30 CT open; C2 short from the 08:30 open to the paper's close (the "complete by about 10:30" remark is
  descriptive and not used to pick an exit). Two trials. Event rule: the 15 monthly expiries in the window, the
  two Thursday-shifted ones included; quarterly expiries carry most of the reversal, and whether the program's roll
  blackout removes the 5 quarterly dates (n 10) must be checked against docs/SCREENING.md before registration (DF2
  did not check the roll splice). The NQ size is from a figure only. 10-15 events give power 0.12-0.19 at the
  published sizes (C3 at the tradable 17:00 CT leg); the owned NQ path's post-sample events (2022-01..2024-02, W_cf, about 26 monthly dates, kept by V41
  "for a hypothesis with a stronger prior") would add power only to about 0.25. Two SEC-approved rule changes in
  the window (GTH trading of expiring a.m. SPX options from 2025-06-10; a.m.-settled SPX dailies from 2026-06-12,
  DF2) could change the mechanism inside the test window.
- **C4 pre-refunding ZN.** Long 1 ZN over the paper's intraday window (07:30-17:00 ET quotes; flat by 15:05 CT)
  on the trading day before each quarterly refunding announcement, only when an FOMC statement fell within the
  preceding five days (the paper's own condition, DF3; the cell labels for the window are as DF3 reads Table 11);
  one trial; 3 eligible events in the research window: power 0.11 at the unconditional 12.62 bp, 0.21 at the
  conditional cell's 23.65 bp (full-sample sd; the cell's sd is not published). Two of the three pre-TRA days
  (2025-10-31, 2026-01-30) are month-end dates whose ZN research-window trades K2-monthend-01 already recorded, so
  a research-window read is not blind on them. The figures are cash-Treasury returns; the futures size is a 0.69
  conversion that E.20 assumed and nobody sourced.
- **C5 pre-FOMC ZN.** Long 1 ZN from 18:00 CT two days before each scheduled FOMC statement to 11:00 CT the day
  before; one trial; 10 events; power 0.13 (the per-event sd is DF3's inference from N about 171, not
  published). The window was read off the authors' average-return figure, and the t-statistic moved from 2.24 to
  2.82 between drafts: both are selection warnings.

#### Execution triage (user addenda 4 and 5): Group A, Group B, one calibration slice

Sources: NM1_nearmiss_table.json (378 rows; 192 positive recorded gross; 119 cover fees) and NM2_exec_triage.md/.json
(ExecTriage-OpusXHigh: 119 rows classified from the 54 distinct rule texts: 52 momentum or breakout, 38 ML-sign,
21 time-based, 8 fade entries; every exit time-based; 17 rows fail mainly on cost under the lead's rule, 11 of
them momentum and 6 Gate 0 ML, none a fade). The lead's rule, fixed before ranking (Open choice 19): Group A needs
(i) an entry against the move, (ii) gross > fee ticks, (iii) RT - gross below the realistic passive saving,
(iv) failure mainly on cost, read as gross t >= 1.0 with net < 0. Realistic passive saving per side under
TopstepX's trade-through fills (NM2's arithmetic from the D8 half-spread and the published adverse-fill shares, not
a published figure): MNQ +0.36 to +0.68 ticks, MES -0.57 to +0.06, MGC +0.39 to +1.17 (no gold source), MCL -0.21
to +0.45, 6E-class -0.52 to +0.26, ZN-class -0.78 to 0.00; touch fills would save 0.2-2.2 ticks but TopstepX does
not give them. Evidence: Lalor-Swishchuk find 65.8-88.8% of passive fills adverse on ES, NQ, CL and ZN in the TT
simulator, which fills only on trade-through (R18); DeLise: a resting ZN fill is followed by a -0.45 tick mid move
(RD8); non-HFT ES market makers lose $0.97 per contract at 1 minute (Baron-Brogaard-Kirilenko, R17). Missed-fill
cost is not quantified in any source.

**Group A: empty (NM2 confirms).** No earlier rule meets all four conditions. Nearest, each failing (iv):
K3-ldnrev-01 6S confirmation (gross 1.91 vs RT 2.65, gross t 0.58, n 55); K4-ovr-01 NG confirmation (0.72 vs
1.67, t 0.42, n 1,091; also fails (iii)); F3_3 opening-30-min to close (MES, 1.20 vs 2.03, gross t about 0.75 by
NM2's approximation; a fade of the 08:30-09:00 move set by the statistic's sign; also fails (iii)). The fades with
gross t >= 1 either already covered their RT and failed on non-cost grounds (K3-ldnrev-01 6E/6J research, n 12-13,
null at confirmation) or sit below the fee line (C-H1, C-H3, G2.ETH, NM2). Momentum near-misses with high gross t
(K2-cp1-01 ZF/ZN, K3-cp1-01 6E/6B) are excluded by addendum 5.

**Group B: one candidate, B1** (R17-C1): C2's mechanism with a resting sell limit at the 08:30 CT open price of
the monthly a.m.-settlement Friday, filled only on trade-through, cancelled if unfilled by a cutoff (the lead's
design parameter, not a published one: it must be fixed in a pre-registration before any data is read; NM2 5b),
covered at the paper's close. Published mechanism: the derivative payoff bias. Since about 70% of the reversal happens in the
first 30 minutes (DF2), a limit that waits for a trade-through above the open fills mainly on days the spike keeps
rising, which is the adverse-selection case R18 measures; the price saving is under 1% of the published move
(NM2). Not testable on owned 1-minute bars. Not proposed: generic slow market making (negative, R17), expiry pinning (unsized, pre-2010),
USO/GSCI roll (multi-day), OBI fades (die within 1 s; HFT ban).

**Shared calibration slice and test data spec (no quote requested, nothing bought).** Databento GLBX.MDP3 schemas
`trades` and `mbp-1` (`mbo` only if queue position matters, which C6 makes moot at Topstep): (a) calibration
2019-05..2024-02-29 only (ending before the March 2024 embargo and holdout-2), MNQ and MES: the monthly expiry
Fridays 2022-01..2024-02 (about 26, post-sample for the paper) and the evening before each, plus 20 second-Friday
(non-expiry) control dates 2019-05..2024-02 (NM2), for the trade-through fill probability and the 1-60-minute
markout of a limit at the open; no rule outcome computed; (b) test: `trades` + `mbp-1` for MNQ on the
15 expiry Fridays in the research window (and Thursday 17:00 CT to Friday 08:30 CT for C3); one registered trial
per rule-execution pair. Published prices on file: TBBO 5 days NQ $3.58, MNQ $8.62 (E.0 log, cited by R4); OPRA
$199/month (R2). A logged quote and the user's approval come first.

### Re-dig findings (user addendum 1): earlier verdicts the deeper reading supports, weakens or overturns

| Verdict or closure | Reader | Effect | Basis (quoted in the reader file) |
|---|---|---|---|
| E20H6 T1-T3 FAIL | RD1, RD5, R1 | supports | Baltussen's equity coefficient decays in-paper; Rosa's out-of-sample disappearance; Mesfin's MNQ families gross 0.07-1.50 NQ points; Adams et al.: market-maker net gamma positive in 88% of intervals, about 0.7 bp, "not a feasible trading strategy" |
| E20H6 as a replica | RD1 | weakens (not the FAIL) | H6 exits 1-2 minutes before the close (14:58 bar, fill about 14:59 CT), inside the last ten minutes where the Aalto thesis places most of the effect |
| E.14 C2 stop | RD5 | supports | SqueezeMetrics GEX matches Baltussen's NGE ("virtually identical results"); most negative-gamma days predate 2011 |
| K1 Tier B; K2 auction cycle; E16-H3 | RD1, RD2 | supports | Lou-Yan-Zhang short holds unprofitable after costs; SR 1188: "do[es] not persist at the same magnitude" |
| K2-predrift-01; V34's drop of pre-announcement drift | RD8 | supports | Kurov et al.'s sizes are sign-adjusted by the unknown surprise; no ex-ante rule; sample ends 2014-03 |
| V34's drop of closing-auction distortions | RD8 | supports | index-level deviation 0.93 bp (2.2 MES ticks), reverting after 16:00 ET |
| V34's reason for dropping noise-area momentum ("unsized") | R10, DF1 | weakens the "unsized" basis (not a result) | the authors' FAQ sizes it; post-publication S&P tests are not distinguishable from zero |
| K3-ldnrev-01, K3-ecbfix-01 nulls | RD4 | supports | Krohn-Mueller-Whelan: futures reversal 0.64 bp, "turn negative once transaction costs are taken into account"; FCA: reversals "disappear from 2015 onwards" |
| K6-limitcont-01 | RD4 | supports | continuation happens in the opening gap (Janardanan-Qiao-Rouwenhorst), before the 08:45 CT entry |
| K4-ngpre-01, K4-eia*, K5-fomc-01, PM fix, C1/C1b | RD3, RD6 | supports | Gu-Kurov-Stan JFM 2026: NG -0.092% from 90 to 5 min before storage (2.8 MNG ticks vs hurdle 8.03); post-2014 decay; HFTs take the first 50 ms |
| K4-apipre-01 | RD3 | weakens slightly | Alturki-Kurov JFM 2022: 4.5 MCL ticks, below the 4.75 hurdle, only in low liquidity |
| E.13 ranking (C1 > C2 > C3) | RD6 | supports | no source argues for reordering; GEFS archive from 2017 and ECMWF CC-BY since 2025-10-01 weaken two cost facts behind weather (C4), which still ranks fourth |
| V38 sentence "no published post-2015 intraday effect on the 17 roots exceeds 1.5 x the D8 round trip" | RD2, DF3, RD4, DF2 | weakens (as far as the evidence goes) | two working papers whose samples run past 2015 report pre-refunding (cash) and pre-FOMC (futures) drifts above the hurdle, but neither publishes a post-2015 estimate (DF3: "WEAKENS only as far as the cash evidence goes"); the only post-2015 estimates (ES 3rd-Friday reversal 14.8-17.6 bp, digitized) are not significant alone |
| V38/V39 trend closure for prop accounts | RD7 | supports | Lou-Polk-Skouras: equity-index TSMOM earns its alpha overnight (1.40%/month, t 3.24); intraday -0.10%, t -0.24 |
| E21 T1-T4 FAIL | RD7 | supports | Hurst-Ooi-Pedersen 2010-2016 gross Sharpe 1-month 0.06, 12-month 0.73; Baltas-Kosowski daily 2.63 -> 0.37 |
| E22-F1 design | RD7 | weakens (small-tick contracts) | Kurth et al.: fast trend collapsed on small-tick contracts (MNQ, M2K, M6E), held on large-tick ones |
| V39 commodity event drift closure | R5, RD3 | supports | Brandt-Gao: geopolitical news enters oil "at once without follow-on momentum" |
| E.19 rule R040 (news flatten not required) | R9 | overturns (the rule changed) | Topstep Tier 1 window (2026-10-10..16) |

### Prop landscape and outcome data (R8, R9, R16)

- No firm found allows both full automation and overnight holds (R9). Automation-friendly firms all flatten daily:
  Topstep (API), FundedNext (terms 2.2.6, 2026-09-25: "automated trading bots ... is allowed"), DayTraders.com,
  MFFU, Lucid, Tradeify, Bulenox (Apex, Lucid, Tradeify and Bulenox facts rest on search summaries [secondary-only],
  R9). Overnight plans allow semi-automation at most (Phidias Premium; The5ers Futures
  Swing, no algorithmic trading; ETF Diamond Hands by written authorization). No firm names British Columbia.
- Non-CME venues (R16): Phidias's rules page lists Eurex (semi-automated only; its terms list CME only); Apex and
  Tradeify Eurex access only from search summaries; no firm found for ICE Europe, OSE, SGX, HKEX, INE or SHFE.
  Databento: Eurex from 2025-03-10; ICE Europe Commodities and ICE US from 2018-12-23; no OSE, HKFE, SGX, INE or
  SHFE futures dataset.
- Outcome data (R8, firm pages unless stated): Topstep 2025: 16.8% of Combines passed, 51.8% of individuals ever
  funded, 33.3% of funded individuals paid at least once (2024: 12.4%, 46.6%, 28.3%); FPFX Tech cross-firm (vendor):
  14% pass, 45% of passers paid, 7% of all participants; FTMO payouts about 35-55% of revenue (pointer).

### S3. Closing assessment

The evidence says an intraday futures edge that survives retail costs and prop rules is possible on paper but not
demonstrable with what the program owns, and the one frequent candidate weakened as soon as others tested it.
(1) The effects with large published sizes are rare events: the 3rd-Friday spike, the refunding and pre-FOMC
Treasury drifts and the FOMC-day reversal come 3 to 15 times in the research window, so power is 0.11-0.22 at
the published sizes and 0.06-0.17 at the post-2015 sizes, and two of them shrank after 2015 or between drafts.
(2) The one frequent candidate, noise-area momentum, had the right size in-sample (power 0.35 on the window at
that size), but no independent S&P test after publication is distinguishable from zero and the latest are
negative, the only positive Nasdaq test is a pointer with t 1.37, third-party results already cover the research
window, and its drawdown at one MNQ exceeds the 50K and 100K trailing limits. (3) Order-flow and headline
information is priced within one to five seconds on ES, NQ, ZN and CL (Takahashi; Chordia et al.; Brandt-Gao;
CEA: "very close to zero" after five minutes), below retail latency and inside the HFT ban. (4) Passive execution
does not rescue the near misses: under TopstepX trade-through fills most passive fills are adverse (R18), the
realistic saving per side is at most about 0.7 MNQ ticks and near or below zero for MES, ZN and FX (NM2), slow
market making in ES loses money (R17), and Group A is empty. (5) The base rates are poor and the terms keep
tightening: Topstep's own 2025 funnel pays about a third of funded individuals; fewer than 1% of Taiwan day
traders and about 3% of persistent Brazilian mini-index day traders profit (R11); no audited multi-year intraday
futures record was found (R7); Topstep added a Tier 1 news window this month (R9); no firm allows automation with
overnight holds. The honest odds that any intraday edge is reachable at retail costs and prop rules are low.
The only clean test left is forward: a frozen paper record of C1 on MNQ, with the expectation that it fails.

### Per-reader source lists

From each reader's JSON evidence rows (fetch counts from its fetch log). R4 and R7 were cut before writing a JSON: their sources are in R4_volume_tradeside.md and R7_live_records.md section 3. R0 lists: r0_prior_sources.md (253 sources earlier passes read), r0_e20_evidence_index.md (157 rows).


#### DF1_noise_area — evidence rows 20, fetches 5 (ok 5, blocked/throttled/forbidden 0), distinct sources 8
- Zarattini, Aziz, Barbon, Beat the Market, WP 2024-05-10, version 2025-09-22
- same
- Paz (Serpa) 2026, SSRN 7290621 (GitHub copy)
- Delgado 2026, SSRN 7323419
- Chuk 2026, SSRN 7609644
- VigorTas 2026 GitHub
- Brusco 2026 GitHub
- cited by Brusco

#### DF2_third_friday — evidence rows 15, fetches 11 (ok 8, blocked/throttled/forbidden 1), distinct sources 5
- Baltussen, Terstegge, Whelan, 'The Derivative Payoff Bias', January 2024 version (AFA program copy)
- Baltussen, Terstegge, Whelan, 'The Third Friday Price Spike', August 2026 version (author page; R&R RFS)
- SEC order SR-CBOE-2025-011
- SEC order SR-CBOE-2026-044
- Cboe Options Expiration Calendars 2025, 2026

#### DF3_treasury_drifts — evidence rows 33, fetches 26 (ok 26, blocked/throttled/forbidden 0), distinct sources 12
- WZ 2025
- Hartley, Rigon, Hoover Economics WP 26112, April 2026
- Hartley, Rigon 2026
- PP26
- PP25 (Dec 26 2025 draft, AFA 2026 program)
- Lucca, Moench, FRBNY SR 512 (J. Finance 2015)
- PP26 (replicating Hillenbrand 2025, RFS)
- Kurov, Wolfe, Gilbert, FRL 40 (2021), accepted draft
- Li, Xinyang, "Two essays on treasury bond risks", Boston University PhD thesis 2022
- Fleming, FRBNY Economic Policy Review, July 1997
- Baker, McPhail, Tuckman, CFTC OCE note, Dec 3 2018
- reports/stage_e2a_costs.md (D8; mbp-1 on 5 dates, 2025-05-14..2026-04-15)

#### R10_practitioner — evidence rows 19, fetches 20 (ok 20, blocked/throttled/forbidden 0), distinct sources 12
- Zarattini, Aziz, Barbon WP 2024/2025
- same
- same (2025-09-22 version)
- Zarattini & Pagani 2026 QuanTips #2
- Concretum 2026 Breaking the Rules of Intraday Trading
- Zarattini & Aziz WP 2023/2025
- Lundström Umeå WP 861
- Holmberg, Lönnbark, Lundström 2013 (WP 845)
- Mesfin 2026, arXiv 2605.04004
- Zarattini & Aziz 2023 VWAP WP
- Chan 2013 Algorithmic Trading ch.7
- Davey 2014 Wiley bio

#### R11_communities — evidence rows 5, fetches 13 (ok 9, blocked/throttled/forbidden 4), distinct sources 5
- Barber, Lee, Liu, Odean, The Cross-Section of Speculator Skill: Evidence from Day Trading, draft 2011; J. Financial Markets 18 (2014) 1-24
- same
- Chague, De-Losso, Giovannetti (2019), Day Trading for a Living?, FEA-USP WP 2019-47 / FGV EESP TD 525 / SSRN 3423101
- Osler (2002), Stop-Loss Orders and Price Cascades in Currency Markets, FRBNY Staff Report 150
- Elite Trader thread 210738

#### R12_regime_filters — evidence rows 14, fetches 10 (ok 9, blocked/throttled/forbidden 1), distinct sources 11
- Baltussen, Terstegge, Whelan 2024
- Gao, Han, Li, Zhou WP 2015 (JFE 2018)
- Gao et al. WP 2015
- Lundström, Umeå Economic Studies 861 (rev. 2017)
- Boyarchenko, Larsen, Whelan, NY Fed SR 917 (RFS 2023)
- Boyarchenko, Larsen, Whelan SR 917
- Boyarchenko, Larsen, Whelan, Liberty Street Economics 2026-07-01
- Mesfin 2026 arXiv 2605.04004
- Mesfin 2026 arXiv 2605.11423
- Grant, Wolf, Yu, JBF 29(5) 2005
- Zarattini, Aziz, Barbon 2024 (R10 owns)

#### R13_leadlag — evidence rows 19, fetches 15 (ok 12, blocked/throttled/forbidden 3), distinct sources 15
- Huth, Abergel (2014), arXiv 1111.7103
- Dobrev, Schaumburg (2015), Liberty Street Economics
- Laughlin, Aguirre, Grundfest (2014), arXiv 1302.5966
- Basnarkov, Stojkoski, Utkovski, Kocarev (2019), arXiv 1906.10388 (Physica A)
- Basnarkov et al. (2019)
- Maier-Paape, Platen (2015), arXiv 1504.06235
- Bangsgaard, Kokholm (2024), J. Financial Markets 67, 100851
- Alsayed, McGroarty (2014), J. Forecasting 33(6) 391-408
- Boyarchenko, Larsen, Whelan, FRBNY SR 917
- Boyarchenko, Larsen, Whelan (2026), The Disappearing Overnight Drift, Liberty Street Economics
- Glasserman, Krstovski, Laliberte, Mamaysky (2025), arXiv 2507.04481
- Indriawan, Jiao, Tse (2019), J. Futures Markets (accepted manuscript)
- Mensi et al. (2025), Rev. Quant. Finance and Accounting
- Ferraro, Rogoff, Rossi (2015), JIMF 54
- De Gooijer, Diks, Gatarek (2009), TI DP 2009-107/4

#### R14_podcasts — evidence rows 12, fetches 28 (ok 28, blocked/throttled/forbidden 0), distinct sources 8
- Chat With Traders ep. 225 (show notes), https://chatwithtraders.com/episode/225-kyle-schultz-the-art-and-science-of-algorithmic-futures-trad
- same
- Chat With Traders ep. 038, https://chatwithtraders.com/episode/038-kevin-davey-the-development-process-of-an-algo-trading-strategy-from-obje
- Chat With Traders ep. 306 (R11 logged the search result; R14 read the page), https://chatwithtraders.com/episode/306-michael-katz-prop-goes-
- Chat With Traders ep. 331, https://chatwithtraders.com/episode/331-jeff-holden
- Better System Trader ep. 112 (show notes), Andrew Swanscott, Aug 6 2017, https://bettersystemtrader.com/112-intraday-trading-with-stefano-se
- Better System Trader ep. 085, https://bettersystemtrader.com/085-intraday-trading-strategies-gary-hart/
- Better System Trader ep. 045, https://bettersystemtrader.com/045-andrea-unger/

#### R15_niche_markets — evidence rows 8, fetches 1 (ok 0, blocked/throttled/forbidden 1), distinct sources 5
- Li, Sakkas, Urquhart (2022), Journal of Financial Markets 57, 100619 (accepted manuscript)
- Boyarchenko, Larsen, Whelan, NY Fed SR 917 (rev. 2022; RFS 2023)
- Boyarchenko, Larsen, Whelan (2026-07-01), Liberty Street Economics
- Jin, Kearney, Li, Yang (2020), J. Futures Markets 40(4) 632-650
- Liu, Tse (2017), Int. Rev. Econ. Finance 48, 440-451

#### R16_niche_access — evidence rows 16, fetches 9 (ok 9, blocked/throttled/forbidden 0), distinct sources 5
- Phidias Propfirm
- Topstep
- damnpropfirms.com (pointer)
- Databento
- Interactive Brokers Canada

#### R17_maker_native — evidence rows 13, fetches 5 (ok 4, blocked/throttled/forbidden 1), distinct sources 4
- Baron, Brogaard, Kirilenko (2014 draft; JFQA 2019) Risk and Return in High Frequency Trading, CFTC OCE
- Golez, Jackwerth (2012) Pinning in the S&P 500 futures, JFE 106(3) 566-585
- Bessembinder, Carrion, Tuttle, Venkataraman (draft June 2015; JFE 121(1) 2016)
- Mou (2011) Columbia thesis

#### R18_queue_fill — evidence rows 10, fetches 4 (ok 4, blocked/throttled/forbidden 0), distinct sources 4
- Lalor and Swishchuk (2024, v3 2026), Market Simulation under Adverse Selection, arXiv:2409.12721
- Albers, Cucuringu, Howison, Shestopaloff (2025), The Market Maker's Dilemma, arXiv:2502.18625
- Albers, Cucuringu, Howison, Shestopaloff (2025), The Market Maker's Dilemma, arXiv:2502.18625 (Lokin-Yu secondary-only)
- Topstep help 8765442 via program record

#### R1_0dte_academic — evidence rows 11, fetches 5 (ok 5, blocked/throttled/forbidden 0), distinct sources 5
- Adams, Dim, Eraker, Fontaine, Ornthanalai, Vilkov, 'Do S&P 500 Options Increase Market Volatility? Evidence from 0DTEs', draft 15 Jul 2026
- Amaya, Garcia-Ares, Pearson, Vasquez, '0DTE Index Options and Market Volatility: How Large is Their Impact?', 25 Jan 2025
- Vilkov, '0DTE Trading Rules: Tail Risk, Implementation, and Tactical Timing' replication package
- Vilkov replication package
- Dim, Eraker, Vilkov, '0DTEs: Trading, Gamma Risk and Volatility Propagation', WFA version 14 May 2024 (SSRN 4692190)

#### R2_0dte_vendor — evidence rows 25, fetches 85 (ok 80, blocked/throttled/forbidden 5), distinct sources 20
- Mandy Xu, Cboe, "Volatility Insights: Much Ado About 0DTEs", 2023-09-07/08, https://www.cboe.com/insights/posts/volatility-insights-evaluati
- same
- Cboe, "0DTEs Decoded: Positioning, Trends and Market Impact", 2025-05-02 (PDF via storage.pardot.com)
- Cboe insights post 2025-05-02, https://www.cboe.com/insights/posts/0-dt-es-decoded-positioning-trends-and-market-impact
- SpotGamma, "SPX Long Gamma Backtest", 2019-12-10, https://spotgamma.com/spx-long-gamma-backtest/
- SpotGamma, https://spotgamma.com/spotgamma-quarterly-report-card/ (fetched 2026-10-18)
- Cboe, 0DTEs Decoded, 2025-05-02
- Cboe, "Market Metrics That Matter: Derivatives September 2026 Volume Highlights", 2026-10-12, https://www.cboe.com/insights/posts/market-met
- Cboe, "Small Caps, Big Momentum: The Rise of 0DTE Trading in Russell 2000 Index & ETF Options", 2026-03-13
- ZeroHedge (Tyler Durden) reposted by SpotGamma, https://spotgamma.com/volmageddon-no-jpm-bofa-say-0-dte-options-are-suppressing-intraday-vol
- ZeroHedge repost on SpotGamma, https://spotgamma.com/no-0dte-will-not-result-in-volmageddon-bofa-derivative-gurus-respond-to-kolanovic/ (202
- Benzinga, 2023-03, https://www.benzinga.com/analyst-ratings/analyst-color/23/03/31230564/jpmorgan-analysts-believe-these-options-could-turn-
- SpotGamma, "Nomura on 0DTE Options Volumes", https://spotgamma.com/nomura-on-0dte-options-volumes/
- SpotGamma Support, "SpotGamma SPX Key Levels Statistics", https://support.spotgamma.com/hc/en-us/articles/31209900542867
- 0.9%
- SqueezeMetrics, "Gamma Exposure (GEX)" white paper, https://squeezemetrics.com/monitor/download/pdf/white_paper.pdf
- SqueezeMetrics note, 2023-12-17, https://mailer.squeezemetrics.com/w/SIIFYZqc14gv41SmeSjRYw?_2023-12-17
- Zarattini, Aziz, Barbon, "Beat the Market: An Effective Intraday Momentum Strategy for S&P500 ETF (SPY)", WP, version 2025-02-03 (owned by R
- FlashAlpha, "Backtesting Futures Gamma (ES & NQ): Historical GEX Done Right", 2026-06, https://flashalpha.com/articles/backtesting-futures-g
- SpotGamma, "0DTE Options Explained", published 2026-06-10, https://spotgamma.com/0dte-options-explained/

#### R3_orderflow — evidence rows 21, fetches 26 (ok 23, blocked/throttled/forbidden 3), distinct sources 20
- Cont, Kukanov, Stoikov (2014), J. Financial Econometrics 12(1); arXiv:1011.6402v3
- Cont, Kukanov, Stoikov (2014)
- Xu, Gould, Howison (2019), arXiv:1907.06230 (multi-level OFI)
- Cont, Cucuringu, Zhang (2023), Quantitative Finance; arXiv:2112.13213
- Cont, Cucuringu, Zhang (2023)
- Takahashi (2025), arXiv:2508.06788 (Returns and Order Flow Imbalances: Intraday Dynamics and Macroeconomic News Effects)
- Takahashi (2025), arXiv:2508.06788
- Dixon (2018), Applied Mathematical Finance; arXiv:1707.05642 (Sequence classification of the LOB using RNNs)
- Kolm, Turiel, Westray (2023), Mathematical Finance 33(4):1044-1081, doi:10.1111/mafi.12413
- Gould, Bonart (2016), Market Microstructure and Liquidity; arXiv:1512.03492
- Briola, Bartolucci, Aste (2024/2025), arXiv:2403.09267 (Deep LOB forecasting: a microstructural guide)
- Lehalle, Mounjid (2017), Market Microstructure and Liquidity; arXiv:1610.00261v4
- Byrd, Palaparthi, Hybinette, Balch (2020), arXiv:2006.08682
- Chordia, Roll, Subrahmanyam (2005), J. Financial Economics 76(2):271-292; UCLA working paper (June 22, 2004)
- Bouchaud group: "Microstructure Modes - Disentangling the Joint Dynamics of Prices & Order Flow" (2024), arXiv:2405.10654
- Andersen, Bondarenko (2014), J. Financial Markets 17; CREATES RP 2011-50 (May 2013 version)
- Andersen, Bondarenko (2014b) "Reflecting on the VPIN dispute", J. Financial Markets; CREATES RP 2013-42
- Databento blog "Building high-frequency trading signals with sklearn"
- Databento pricing page (fetched 2026-10-18)
- PropExperiment Stage D.1e quote run (not a published price)

#### R5_news — evidence rows 17, fetches 49 (ok 47, blocked/throttled/forbidden 1), distinct sources 17
- Chordia, Green, Kottimukkalur (2018) RFS 31(12)
- Bianchi, Kind, Kung (2019/2022) NBER WP 26308
- Gomez-Cram, Grotteria (2022) JFE 143(3)
- Gomez-Cram, Grotteria (2022)
- Swanson, Jayawickrema (2025 draft)
- Lopez-Lira, Tang (2023/2026) JFE
- Brandt, Gao (2019) J Empirical Finance 51
- Ait-Sahalia, Li, Li (2024) NBER WP 32746
- Dai, Ma, Liu, Geng, Wang (2026) arXiv 2603.11408
- Kargarzadeh et al. (2026) arXiv 2608.14014
- Glasserman, Lin (2023) arXiv 2309.17322
- arXiv 2504.14765 (authors not re-read)
- Acharya, Laarits (2026) NBER WP 34640
- GDELT Project
- Tiingo
- Benzinga
- Newsquawk

#### R6_sched_events — evidence rows 33, fetches 18 (ok 16, blocked/throttled/forbidden 2), distinct sources 19
- Narain, Sangani, The Market Impact of Fed Communications: The Role of the Press Conference, IJCB (forthcoming; v22n1 Jan 2026), https://www.
- Gomez-Cram, Grotteria, Real-time price discovery via verbal communication, JFE 143(3) 2022; CEMLA slides Oct 2020
- Boguth, Gregoire, Martineau, Price Pressure and Efficiency on FOMC Announcements, draft 28 Jun 2019, https://ies.keio.ac.jp/upload/20190716m
- Boguth, Fisher, Gregoire, Martineau, Noisy FOMC Returns? (2025), https://www.vincentgregoire.com/
- Baglioni (2023), Essays in Financial Economics, PhD thesis, Insper, ch. 1 with R. M. Ribeiro, https://repositorio.insper.edu.br/handle/11224
- Kurov, Wolfe, Gilbert, The Disappearing Pre-FOMC Announcement Drift, FRL 40 (2021) (E.10 copy, re-used)
- Gao, Han, Li, Zhou, Market intraday momentum, WP Dec 2015 (JFE 129, 2018) (E.20 copy, re-used)
- Kurov, Sancetta, Strasser, Wolfe, ECB WP 1901 (2016) (E.20 copy, re-used)
- Pinchuk, Monetary Uncertainty as a Determinant of the Response of Stock Market to Macroeconomic News, arXiv 2212.04525 (2022); E-mini 1-min,
- Winkelmann, Yao, Breaking news, arXiv 2603.22835 (2026); ES CPI 2020-01..2025-10, 69 releases
- Kroner, How Markets Process Macro News: The Importance of Investor Attention, FEDS 2025-022
- Chatrath, Miao, Ramchander et al., Does the price of crude oil respond to macroeconomic news?, JFM 32(6) 2012 (author manuscript), https://h
- Elder, Miao, Ramchander, Impact of macroeconomic news on metal futures, JBF 36(1) 2012 (manuscript)
- Council of Economic Advisers, The Timing of Market Reactions to Data Releases (for OMB), 14 Feb 2024, https://bidenwhitehouse.archives.gov/w
- Boguth, Fisher, Gregoire, Martineau, Price Informativeness and FOMC Return Reversals, 5 Mar 2023 (SocArXiv/OSF zurfk; later "Noisy FOMC Retu
- Narain, Sangani (IJCB 2026)
- Boguth, Gregoire, Martineau, Internet Appendix to "Shaping Expectations and Coordinating Attention" (JFQA), 5 Sep 2018, https://www.vincentg
- Topstep help 13613539 (dateModified 2026-10-16), read from R9's copy
- Hartley, Rigon, Hoover Economics WP 26112 (2026)

#### R8_prop_outcomes — evidence rows 47, fetches 56 (ok 53, blocked/throttled/forbidden 2), distinct sources 33
- Topstep LLC, site footnote, fetched 2026-10-18
- Topstep LLC, 2026
- Topstep LLC via Internet Archive
- Topstep LLC blog, 2026
- D. Kimberley, TradeInformer, 2025-08-11
- D. Chmiel, Finance Magnates (FPFX Tech data); article date not in saved text
- Finance Magnates (FPFX Tech data)
- D. Chmiel, Finance Magnates, citing CEO A. Ciaramello on Discord; article date not in saved text
- Finance Magnates
- TradeInformer 'What FTMO tells us about prop firm finances'
- Finance Magnates Intelligence (datalab)
- Finance Magnates Intelligence (datalab), D. Chmiel, 2025-11-13
- D. Chmiel, Finance Magnates (FM Intelligence)
- A. Shome, Finance Magnates, 2025-06-03
- TradeInformer 'Are prop payouts real and does it matter?'
- TradeInformer
- TradeInformer 'How does FTMO make money'
- FTMO, 2026
- FTMO blog (single-trader case study)
- FTMO blog
- MyFundedFutures, 2026
- Alpha Futures, 2026
- FundedNext, 2026
- Top One Futures, 2026
- TradeDay, 2026
- Finance Magnates executive interview (Tradeify co-founders)
- Finance Magnates thought-leadership piece on TPT
- M. O. Layaida, master's thesis, HEC Liege, 2025
- W.-Y. Kuo and T.-C. Lin, J. Banking & Finance 37(9) 2013, 3548-3561, doi:10.1016/j.jbankfin.2013.04.036
- Barber, Lee, Liu, Odean, 'Do Day Traders Rationally Learn About Their Ability?', WP 2011-02-17 (author PDF)
- Barber, Lee, Liu, Odean, 'The Cross-Section of Speculator Skill', WP 2011-05-23 (author PDF); R11 holds the <1% and 13.1/-6.8 bp quotes
- SEBI press release, 2024-09-23 (PR No. 22/2024 in the PDF; 37/2024 on the HTML page)
- SEBI, 2024-09-23

#### R9_prop_rules — evidence rows 51, fetches 93 (ok 82, blocked/throttled/forbidden 3), distinct sources 29
- Topstep help 13613539
- same
- Topstep help 8284211
- help 8284206
- help 11187768
- help 10305426
- help 8284116
- help 8284233
- fundednext.com/futures-challenge-terms
- FundedNext
- daytraders.com/help
- the5ers.com/futures-faqs
- help.alpha-futures.com
- help.myfundedfutures.com
- tradeday.freshdesk.com
- phidiaspropfirm.com/rules
- elitetraderfunding.com/terms-of-service
- ETF
- TPT
- Tradeify
- Lucid
- Apex
- Bulenox
- AquaFutures
- reviews
- PropShopTrader
- toponefutures.com
- earn2trade.com
- Leeloo

#### RD1_redig_equity — evidence rows 16, fetches 15 (ok 8, blocked/throttled/forbidden 7), distinct sources 7
- Baltussen, Da, Lammers, Martens, Hedging demand and market intraday momentum, JFE 142 (2021) 377-403
- Baltussen, Da, Soebhag, End-of-Day Reversal, working paper April 2025 (SSRN 5039009)
- Mesfin, Structural Limits of OHLCV-Based Intraday Momentum Signals in MNQ Futures, arXiv 2605.04004v3 (May 2026)
- Mesfin 2026, arXiv 2605.11423 and 2605.17724
- Majorin, Aalto University master's thesis (2025)
- Rosa, J. Futures Markets 42(12) (2022) 2218-2234
- OpenAlex

#### RD2_redig_rates — evidence rows 15, fetches 12 (ok 10, blocked/throttled/forbidden 2), distinct sources 10
- Wang, Zhao, Pre-Refunding Announcement Gains in U.S. Treasurys, draft July 16 2025 (first version March 18 2024), OSF preprint xucf8
- Pan, Peng, The Pre-FOMC Drift in Long-Term Treasury Bonds, SAIF draft June 2 2026 (first draft May 31 2023)
- Fleming, Liu, Nguyen, Intraday Price Pressure and Order Flow Around U.S. Treasury Auctions, NY Fed Staff Report 1188 (2026)
- Lou, Yan, Zhang (2013), Anticipated and Repeated Shocks in Liquid Markets, RFS 26(8) 1891-1912
- Fleming, Nguyen, Rosenberg, How do Treasury dealers manage their positions?, NY Fed SR 299 (rev. 2024); JFE 158 (2024)
- Smales, The effect of treasury auctions on 10-year Treasury note futures, Accounting & Finance 61(S1) 2021
- Hartley, Schwarz (2019), Predictable End-of-Month Treasury Returns, Rodney L. White Center WP 17-19
- Baltussen, Da, Lammers, Martens (2021), Hedging demand and market intraday momentum, JFE 142, 377-403
- Herb, The treasury auction risk premium, JBF 170 (2025) 107316
- Majorin (2025), Aalto MSc thesis

#### RD3_redig_energy_metals — evidence rows 12, fetches 12 (ok 7, blocked/throttled/forbidden 5), distinct sources 9
- Alturki (2020) WVU dissertation
- Alturki (2020)
- Gu, Kurov, Stan (Aug 2025 WP); JFM 2026 doi 10.1002/fut.70104
- Gu, Kurov, Stan (2025 WP)
- Prokopczuk, Wese Simen, Wichmann (2021) Energy Journal 42(2)
- Awartani, Hussain, Virk (2024) IRFA 103486
- Awartani et al. (2024)
- Sobti Gupta (2024) IGPC-IIMA slides; IRFA 105 (2025) 104380
- Osler, Turnbull (2017) Brandeis IBS WP 101R; JBF 2026 doi 10.1016/j.jbankfin.2026.107641

#### RD4_redig_fx_ags — evidence rows 12, fetches 16 (ok 12, blocked/throttled/forbidden 5), distinct sources 9
- Krohn, Mueller, Whelan (2024), Foreign Exchange Fixings and Returns around the Clock, Journal of Finance 79(1); WRAP copy (version January 2
- Osler, Turnbull, Dealer Trading at the Fix, Brandeis WP 101R (published as Dealer misconduct and price dynamics at the fix, JBF 185, 2026)
- Ito, Yamada (2017/2018), Did the reform fix the London fix problem?, JIMF 80; NBER w23327 [secondary-only: E.0 reader's verified quote]
- Evans, O'Neill, Rime, Saakvitne (2018), FCA Occasional Paper 46 [secondary-only: E.0 reader's verified quote]
- Evans (2018), Forex trading and the WMR Fix, JBF 87 (MPRA 81583)
- Janardanan, Qiao, Rouwenhorst, On commodity price limits, WP Feb 2017 (JFM 39(8) 2019)
- He, X. (2022), Essays on extreme events in agricultural futures markets, PhD dissertation, University of Illinois, ch.3
- Anderson, McKenzie, Noyes (2024), NCCC-134 proceedings
- Baltussen, Terstegge, Whelan (2024), The Derivative Payoff Bias, working paper, version September 2024 (AEA 2025 program copy)

#### RD5_redig_gamma — evidence rows 14, fetches 12 (ok 9, blocked/throttled/forbidden 2), distinct sources 12
- Baltussen, Da, Lammers, Martens, JFE 142 (2021)
- Baltussen et al. 2021
- SqueezeMetrics, Gamma Exposure white paper, Dec 2017
- SqueezeMetrics 2017
- Barbon and Buraschi, Gamma Fragility, SoF HSG WP 2020
- Barbon and Buraschi 2020
- Adams, Dim, Eraker, Fontaine, Ornthanalai, Vilkov, draft 2026-07-15 (R1 owns)
- Adams et al. 2026
- Baltussen, Da, Soebhag, End-of-Day Reversal, WP Apr 2025
- Baltussen, Da, Soebhag 2025
- Egebjerg and Kokholm, SSRN 4936978
- Anderegg, Ulmann, Sornette, JIMF 2022

#### RD6_redig_infosources — evidence rows 27, fetches 76 (ok 4, blocked/throttled/forbidden 6), distinct sources 21
- Prokopczuk, Wese Simen, Wichmann (2021), Energy Journal 42(2), doi:10.5547/01956574.42.2.mpro, https://centaur.reading.ac.uk/90003/
- same
- Monteux, Arcuri, Gandolfi, Caselli (2025), NAJEF 80, 102494, doi:10.1016/j.najef.2025.102494
- Hsu, Park, Zhu (2026), "Weather Forecasts, Forecast Revisions, and Natural Gas Price Discovery", SSRN wp, doi:10.2139/ssrn.6985300 (also 10.
- Wen, Indriawan, Lien, Xu (2023), Energy Journal 44(4), doi:10.5547/01956574.44.4.zwen
- Gu, Kurov (2018), J. Futures Markets 38(9), doi:10.1002/fut.21926
- Alturki, Kurov (2021), J. Futures Markets, doi:10.1002/fut.22264
- Brigida, Pratt (2019), Studies in Economics and Finance, doi:10.1108/sef-03-2018-0092
- Fernandez-Perez, Garel, Indriawan (2020), Energy Journal 41(5), doi:10.5547/01956574.41.5.afer
- Ederington, Lin, Linn, Yang (2019), Energy Journal 40(5), doi:10.5547/01956574.40.5.lede
- Huang, Serra, Garcia (2022), AJAE, doi:10.1111/ajae.12356
- Baglioni (2023), Essays in Financial Economics, PhD thesis, Insper, ch. 1 with R. M. Ribeiro, https://repositorio.insper.edu.br/handle/11224
- Dreesmann, Herberger, Charifzadeh (2023), Int. J. Financial Markets and Derivatives 9(1/2) 76-113, doi:10.1504/ijfmd.2023.129093, https://id
- Boucher, Gagnon, Power (2025), The Energy Journal, doi:10.1177/01956574251369707
- Chen, Hartley, Lan (2023), J. Futures Markets, doi:10.1002/fut.22402
- AWS Open Data Registry, https://registry.opendata.aws/noaa-gefs/; https://noaa-gefs-pds.s3.amazonaws.com/
- https://noaa-gfs-bdp-pds.s3.amazonaws.com/
- ECMWF, "Open Data Roadmap", https://www.ecmwf.int/node/29013
- OpenCitations doi:10.1016/j.najef.2025.102494; Crossref 10.2139/ssrn.5975814
- doi:10.5547/01956574.42.2.mpro
- doi:10.2139/ssrn.4182628

#### RD7_redig_trend_carry — evidence rows 19, fetches 18 (ok 14, blocked/throttled/forbidden 5), distinct sources 17
- Lou, Polk, Skouras, A Tug of War (Feb 2018 version; JFE 134, 2019)
- Lou, Polk, Skouras (2018/2019)
- Safari, Schmidhuber (2025), Physica A; arXiv 2501.16772v2
- Safari, Schmidhuber (2025)
- Kurth, Eisler, Rej, Bouchaud (2026), arXiv 2607.01550v1
- Kurth et al. (2026)
- Hurst, Ooi, Pedersen (2017), A Century of Evidence on Trend-Following Investing, JPM
- Hurst, Ooi, Pedersen (2017)
- Baltas, Kosowski (2011 WP), Momentum Strategies in Futures Markets and Trend-following Funds
- Babu, Levine, Ooi, Schroeder, Stamelos (2020), JPM
- Hutchinson, Kyziropoulos, O'Brien, O'Reilly, Sharma (2022), IRFA 83, 102245
- How Overlapping Returns Inflate Measured Time Series Momentum, JRFM 19(1) 46 (2026)
- Xu, Li, Singh, Chen, Li (2025), JIFMIM 105, 102239
- Predicting Commodity ETF Returns with Deep Learning: Overnight Versus Daytime Predictability, Commodities 5(3) 16 (2026)
- Moskowitz, Ooi, Pedersen (2012) JFE
- Huang, Li, Wang, Zhou (2020) JFE
- Koijen, Moskowitz, Pedersen, Vrugt (NBER w19325)

#### RD8_redig_e20_planning — evidence rows 24, fetches 18 (ok 15, blocked/throttled/forbidden 2), distinct sources 9
- Bogousslavsky and Muravyev, "Who Trades at the Close?", AEA 2021 conference draft dated 2020-12-03, https://www.aeaweb.org/conference/2021/p
- same
- Kurov, Sancetta, Strasser, Wolfe, JFQA 54(1) 2019 449-479, doi 10.1017/S0022109018000625 (RePEc abstract page)
- Kurov et al., ECB WP 1901 (May 2016), E.20 copy
- Kurov, Sancetta, Wolfe, "Drift Begone!", J. Int. Money and Finance 128 (2022) 102718 (RePEc abstract)
- api.opencitations.net/index/v2/citations/doi:10.1017/s0022109018000625; titles via Crossref
- Lin, Lo, Qiao, J. Banking and Finance 133 (2021) 106252 (RePEc)
- DeLise, "The Negative Drift of a Limit Order Fill", arXiv 2407.16527 (TT simulator, 10-year note futures)
- Kurov and Zabotina, J. Futures Markets 25 (2005) 79-104 (RePEc)

## 4. Delegation record

One row per spawn (transcripts; times PDT; tokens are each message's final usage, all four fields). Agent 
file: worker-medium, worker-high or worker-xhigh by effort (wave-1 and wave-2 readers ran as workflow agents 
at the same model and effort). The lead's own row is in section 8.

| # | Agent (role name) | Model | Effort | Start | End | Tokens | Status |
|---|---|---|---|---|---|---|---|
| 1 | MechIndexer-SonnetMed | sonnet-5-5 | medium | 01:31 | 01:37 | 5,834,390 | done |
| 2 | PriorSources-HaikuMed | haiku-5-5 | medium | 01:31 | 01:33 | 2,042,557 | done |
| 3 | SourceReader-0DTEAcademic-OpusHigh | opus-5-5 | high | 01:38 | 02:01 | 10,678,059 | cut by the usage limit about 01:58 (partial files on disk) |
| 4 | SourceReader-0DTEVendor-OpusHigh | opus-5-5 | high | 01:38 | 01:58 | 14,004,235 | cut by the usage limit about 01:58 (partial files on disk) |
| 5 | SourceReader-VolumeTradeSide-OpusHigh | opus-5-5 | high | 01:38 | 01:58 | 14,593,310 | cut by the usage limit about 01:58 (partial files on disk) |
| 6 | SourceReader-PropRules-OpusHigh | opus-5-5 | high | 01:38 | 01:58 | 15,820,818 | done |
| 7 | SourceReader-Communities-OpusHigh | opus-5-5 | high | 01:38 | 01:53 | 8,934,782 | done |
| 8 | SourceReader-RegimeFilters-OpusHigh | opus-5-5 | high | 01:38 | 01:57 | 15,697,314 | done |
| 9 | SourceReader-PropOutcomes-OpusHigh | opus-5-5 | high | 01:38 | 01:58 | 14,866,390 | cut by the usage limit about 01:58 (partial files on disk) |
| 10 | SourceReader-OrderFlow-OpusHigh | opus-5-5 | high | 01:38 | 01:59 | 17,703,698 | cut by the usage limit about 01:58 (partial files on disk) |
| 11 | SourceReader-News-OpusHigh | opus-5-5 | high | 01:38 | 01:59 | 14,396,977 | cut by the usage limit about 01:58 (partial files on disk) |
| 12 | SourceReader-SchedEvents-OpusHigh | opus-5-5 | high | 01:38 | 01:59 | 27,824,773 | cut by the usage limit about 01:58 (partial files on disk) |
| 13 | SourceReader-LiveRecords-OpusHigh | opus-5-5 | high | 01:38 | 02:00 | 11,733,083 | cut by the usage limit about 01:58 (partial files on disk) |
| 14 | SourceReader-LeadLag-OpusHigh | opus-5-5 | high | 01:38 | 01:57 | 17,598,648 | done |
| 15 | SourceReader-Practitioner-OpusHigh | opus-5-5 | high | 01:38 | 01:55 | 12,715,339 | done |
| 16 | RedigReader-EquityIndex-OpusHigh | opus-5-5 | high | 01:38 | 01:58 | 14,557,908 | cut by the usage limit about 01:58 (partial files on disk) |
| 17 | RedigReader-Rates-OpusHigh | opus-5-5 | high | 01:38 | 01:59 | 17,691,494 | cut by the usage limit about 01:58 (partial files on disk) |
| 18 | RedigReader-TrendCarry-OpusHigh | opus-5-5 | high | 01:38 | 01:57 | 17,923,544 | done |
| 19 | RedigReader-EnergyMetals-OpusHigh | opus-5-5 | high | 01:38 | 01:59 | 11,204,753 | cut by the usage limit about 01:58 (partial files on disk) |
| 20 | RedigReader-FXAgs-OpusHigh | opus-5-5 | high | 01:38 | 01:58 | 13,617,317 | done |
| 21 | RedigReader-InfoSources-OpusHigh | opus-5-5 | high | 01:38 | 01:58 | 12,142,629 | cut by the usage limit about 01:58 (partial files on disk) |
| 22 | RedigReader-DealerGamma-OpusHigh | opus-5-5 | high | 01:38 | 01:52 | 9,668,684 | done |
| 23 | NearMissExtractor-SonnetMed | sonnet-5-5 | medium | 01:53 | 06:12 | 8,567,134 | cut by the usage limit about 01:58; resumed by message 06:12; done |
| 24 | SourceReader-MakerNative-OpusHigh | opus-5-5 | high | 01:54 | 06:15 | 4,612,407 | cut by the usage limit about 01:58; resumed by message 06:12; done |
| 25 | SourceReader-QueueFill-OpusHigh | opus-5-5 | high | 01:56 | 06:16 | 3,881,034 | cut by the usage limit about 01:58; resumed by message 06:12; done |
| 26 | SourceReader-Podcasts-OpusHigh | opus-5-5 | high | 01:57 | 06:17 | 3,260,228 | cut by the usage limit about 01:58; resumed by message 06:12; done |
| 27 | SourceReader-NicheMarkets-OpusHigh | opus-5-5 | high | 01:58 | 06:16 | 2,541,068 | cut by the usage limit about 01:58; resumed by message 06:12; done |
| 28 | SourceReader-NicheAccess-OpusHigh | opus-5-5 | high | 01:58 | 06:17 | 3,783,035 | cut by the usage limit about 01:58; resumed by message 06:12; done |
| 29 | SourceReader-0DTEAcademic-OpusHigh | opus-5-5 | high | 06:13 | 06:17 | 2,664,791 | done |
| 30 | SourceReader-News-OpusHigh | opus-5-5 | high | 06:13 | 06:16 | 1,238,405 | done |
| 31 | DeepReader-NoiseAreaMomentum-OpusHigh | opus-5-5 | high | 06:21 | 06:33 | 7,773,021 | cut by the usage limit about 06:35 (partial files on disk) |
| 32 | ExecTriage-OpusXHigh | opus-5-5 | xhigh | 06:21 | 06:33 | 10,744,732 | cut by the usage limit about 06:35 (partial files on disk) |
| 33 | DeepReader-TreasuryDrifts-OpusHigh | opus-5-5 | high | 06:21 | 06:35 | 15,123,531 | cut by the usage limit about 06:35 (partial files on disk) |
| 34 | DeepReader-ThirdFriday-OpusHigh | opus-5-5 | high | 06:21 | 06:33 | 11,889,228 | cut by the usage limit about 06:35 (partial files on disk) |
| 35 | SourceReader-SchedEvents-OpusHigh | opus-5-5 | high | 06:21 | 06:30 | 7,929,184 | done |
| 36 | SourceReader-PropOutcomes-OpusHigh | opus-5-5 | high | 06:21 | 06:33 | 9,649,842 | cut by the usage limit about 06:35 (partial files on disk) |
| 37 | RedigReader-InfoSources-OpusHigh | opus-5-5 | high | 06:21 | 06:33 | 8,554,550 | cut by the usage limit about 06:35 (partial files on disk) |
| 38 | RedigReader-EnergyMetals-OpusHigh | opus-5-5 | high | 06:21 | 06:33 | 12,456,717 | cut by the usage limit about 06:35 (partial files on disk) |
| 39 | RedigReader-E20Planning-OpusHigh | opus-5-5 | high | 06:21 | 06:33 | 8,704,329 | cut by the usage limit about 06:35 after its md and json were complete |
| 40 | SourceReader-0DTEVendor-OpusHigh | opus-5-5 | high | 06:21 | 06:32 | 10,557,795 | done |
| 41 | DeepReader-NoiseAreaMomentum-OpusHigh | opus-5-5 | high | 11:16 | 11:24 | 4,697,821 | done |
| 42 | DeepReader-ThirdFriday-OpusHigh | opus-5-5 | high | 11:16 | 11:25 | 7,074,534 | done |
| 43 | ExecTriage-OpusXHigh | opus-5-5 | xhigh | 11:16 | 11:29 | 7,335,560 | done |
| 44 | RedigReader-EnergyMetals-OpusHigh | opus-5-5 | high | 11:16 | 11:24 | 6,034,214 | done |
| 45 | RedigReader-InfoSources-OpusHigh | opus-5-5 | high | 11:16 | 11:23 | 4,989,646 | done |
| 46 | FileFinisher-SonnetMed | sonnet-5-5 | medium | 11:16 | 11:17 | 590,206 | done |
| 47 | ShortlistReviewer-FableXHigh | fable-5-1 | xhigh | 11:30 | 11:51 | 3,721,751 | done |

## 5. Verification

S4: ShortlistReviewer-FableXHigh (fable, xhigh), 11:30-11:45 PDT, reports/stage_e25_briefs/review_S4.md (221 lines).
Verdict on synthesis v2: **BLOCK** until findings 1-2 are corrected; READY WITH FIXES once 1-12 are applied; no
shortlisted candidate duplicates a prior trial (rows 1-5 checked against r0_mechanism_index.md sections 1-16 and
its keyword index); no membership or rank change. Counts: BLOCKING 2, SHOULD FIX 10, NOTE 10. The reviewer also
confirmed the brief's D8 hurdle table against reports/stage_e2a_costs.md and the MES Stage D cost (2.03 ticks).
Every fix below is in synthesis.md v3 (v2 kept as synthesis_v2_prereview.md), s2_power.py/.out v2 and
ret_decisions.md; the lead's recomputed figures match the reviewer's to two decimals.

| # | Severity | Finding (short) | Ruling | Fix |
|---|---|---|---|---|
| 1 | BLOCKING | C1 power used 299 days; the published t 5.34 is over 2,620 TRADED days (about 61% of the sample) | accepted | s2_power.py uses SR per traded day over about 183 expected traded days: MNQ E[t] 1.26, power 0.35 (Holm-5 0.14); MES 1.11, 0.30 (0.11); forward 250 days 0.31 / 0.27; S1 row 1 says "traded days" |
| 2 | BLOCKING | C2 row mixed the 14.8 bp sensitivity into the published-size range; n stated three ways | accepted | one event rule (15 monthly expiries, 10 if the quarterly dates are blacked out); C2 at 12.89 bp: E[t] 0.47-0.58, power 0.12-0.14 |
| 3 | SHOULD FIX | C4 row did not describe the FOMC-conditional design | accepted | C4 row as designed (n 3): 0.11 at 12.62 bp, 0.21 at the conditional cell's 23.65 bp (full-sample sd) |
| 4 | SHOULD FIX | C3's 16.91 is an unlabelled upper bound | accepted | C3 at the tradable 17:00 CT leg 12.75 bp (digitized): ratio 15.07, power 0.15-0.19; 16.91 labelled as the published upper bound |
| 5 | SHOULD FIX | Holm step k = 4 but five trials designed | accepted | k = 5 (alpha 0.01, z 2.326) throughout |
| 6 | SHOULD FIX | overlap cells omitted the nearest prior trials; K2-monthend-01 removes blindness on 2 of C4's 3 events | accepted | rows 1-4 name K1-vwap-01, A-H4 rth/eth legs, D-H4, K2-monthend-01; C4 design states the non-blind dates and the month-end fixed effect |
| 7 | SHOULD FIX | grades missing on Delgado, Chuk, Brusco/VigorTas ES | accepted | [secondary-only] and P labels added |
| 8 | SHOULD FIX | "every independent S&P test at or below zero" contradicts Paz +0.39 | accepted | "no independent S&P test after publication is distinguishable from zero; the latest are negative" (S1, S2, S3, decisions) |
| 9 | SHOULD FIX | re-dig row "E20H6 as a replica" mis-stated H6's exit | accepted | "exits 1-2 minutes before the close (14:58 bar, fill about 14:59 CT)" |
| 10 | SHOULD FIX | V38 row overstated DF3 ("post-2015-inclusive") | accepted | "samples run past 2015 ... neither publishes a post-2015 estimate"; same in decision 4 |
| 11 | SHOULD FIX | per-trade basis caveat missing (fills vs round trips) | accepted | S1 row 1: per round trip about 8 bp if the paper counts fills |
| 12 | SHOULD FIX | S3 power range mislabelled | accepted | 0.11-0.22 at published sizes, 0.06-0.17 at post-2015 sizes |
| 13 | NOTE | C5 sd is DF3's inference | accepted | marked in the S2 row and design |
| 14 | NOTE | RD3-C1 bound depends on the gold price | accepted | 10.5-14.0 MGC ticks |
| 15 | NOTE | MNQ ratio depends on the NQ level | accepted | 8.16-9.71 at NQ 21,000-25,000 |
| 16 | NOTE | V34 row: DF1 grades it "weakens the basis" | accepted | "weakens the 'unsized' basis" |
| 17 | NOTE | header time stamps | accepted | header now v3 |
| 18 | NOTE | C4 condition rests on DF3's reading of Table 11 cell labels | accepted | stated in the C4 design |
| 19 | NOTE | row 6 size is net of spread | accepted | "used as gross: conservative" |
| 20 | NOTE | row 2 source version | accepted | January 2024 AFA copy; August 2026 version drops the futures table |
| 21 | NOTE | B1's cancel time is the lead's parameter | accepted | stated as a design parameter to be fixed in a pre-registration before any data is read |
| 22 | NOTE | Apex/Lucid/Tradeify/Bulenox facts rest on search summaries | accepted | marked [secondary-only] in the prop landscape |

Earlier verification inside the stage: the lead spot-checked the mechanism index's N reconciliation (538); NM2
re-classified NM1's 119 fee-covering rows from the verbatim rule text and confirmed Group A empty; DF1-DF3 re-read
every shortlisted number from full text (DF1 and DF3 confirmed the figures; DF2 verified Table II and digitized the
2026 figures).

**Re-check (ShortlistReviewer-FableXHigh, resumed 11:48, returned by 11:51 PDT per `date`; review_S4.md "Re-check"): READY.** Findings
1-12 applied correctly; NOTEs 13-18 and 20-22 applied; every s2_power.out v2 row re-derived to two decimals; no new
error introduced. Its four remaining NOTEs (an index-gap caveat on row 6, the V34 wording in decision 5, the NQ
level in the S2 C1 ratio, and this line) were applied by the lead at 11:51.

## 6. Open choices

Every decision the lead made on its own, with the reason (user-directed changes are marked).


1. **User-directed change, addendum 1 (01:33 PDT).** The user's planner addendum added every research tool
   at full depth (Firecrawl search, scrape and research_* paper tools; OpenAlex; Semantic Scholar; Playwright;
   WebSearch/WebFetch) and re-dig readers in waves (at most 20 at once, about 2 per domain) on the sources E.13
   and E.20 cited, reported in their own return section and folded into S1/S2. Applied as written.
2. **User-directed change, addendum 2 (01:40 PDT).** Podcasts that publish official transcripts or show notes
   on their own sites, read under each site's terms, pointers only unless a guest cites a checkable public
   record, no YouTube transcripts by any route. R11 was already running inside a workflow and cannot take new
   instructions, so the family went to a spare reader (R14, SourceReader-Podcasts-OpusHigh), launched when a
   wave-1 slot freed (the cap of 20 was full). R11's fetch log is checked for any YouTube transcript.
3. **Semantic Scholar without a key.** SEMANTIC_SCHOLAR_API_KEY in .env has length 1 (checked by length only,
   value never printed), so it is unusable; readers call the public API keyless at most once per 10 s and fall
   back to OpenAlex (polite pool, OPENALEX_EMAIL read into the environment, never echoed).
4. **MES cost in the hurdle table.** MES is not in the frozen D8 table (MES closed after Stage D and enters
   Stage E only as a leg). The brief uses the Stage D MES model (sim/costs.py: $1.22 commission + about 0.53
   tick half-spread per side at 1 lot, sim/slippage_calibration.json), about 2.0 ticks or $2.53 per round
   trip, labelled as such. MNQ, the D8 vehicle, is the primary equity-index hurdle.
5. **"Unread research window".** The Stage E cluster screens (E.3-E.9) and D.1 read the research window
   2025-04-01..2026-06-19 for their own members. The brief reads the prompt's "unread" as: no new hypothesis's
   outcome has been computed on it (V42 keeps intraday registered reads of it possible). Overlap of a new
   rule's trades with earlier members' trades is flagged in S1.
6. **Guardrail quoting.** `git status --short` shows no tracked change at the start; its 1,271 untracked lines
   (raw pages of earlier stages) are counted, not listed, as E.23 did. Both ledgers are quoted: the spend ledger
   (line count, sha256) and the trial ledger (line count, sha256, N from `screening.trial_registry status`).
7. **R0 extraction delegated.** The prompt makes R0 the lead's. The lead wrote the brief (costs, prop rules,
   data, family-level overlap list) and delegated two extractions it feeds: the mechanism index
   (MechIndexer-SonnetMed, a multi-source join) and the prior-sources and E.20 evidence lists
   (PriorSources-HaikuMed). The lead spot-checked the index's N reconciliation (sums to 538; the registry's
   "9 lines" are the baseline line plus r001-r008).
8. **Readers run as dynamic workflows.** Ultracode is on, so wave 1 ran as two parallel workflows (13 topic
   readers; 7 re-dig readers), each agent at model opus, effort high, agent type worker-high, labelled with its
   CLAUDE.md role name. Two workflows keep each under the per-workflow concurrency cap of 16.
9. **Re-dig split.** Wave 1 re-dig readers were split by the E.20 product files' asset classes (equity; rates;
   energy and metals; FX, grains and livestock) and by E.13's three source families (dealer gamma; other
   information sources; trend and carry). E.10's sources (142 groups) were not re-dug in wave 1: the addendum
   names E.13 and E.20.
10. **User-directed change, addendum 3 (01:47 PDT).** Two readers on niche and non-US futures markets. The
    lead split them by query family: R15 (academic evidence of intraday or short-horizon inefficiency on Eurex,
    ICE Europe, OSE, SGX, HKEX, INE/SHFE, thin CME contracts and CME during Asian hours) and R16 (firm, vendor and
    exchange pages: which prop firms allow each market plan by plan with automation rules; tick-data sources and
    published costs per venue; retail access for a Canadian resident). R16 coordinates with R9 on prop-firm
    domains (grep R9's saved pages before fetching). Both queue for free slots under the cap of 20, after R14.
    Spare-reader numbering shifts: wave-2 deep follow-ups are R17-R20.
11. **User-directed change, addendum 4 (01:52 PDT).** Near-miss execution triage from recorded results only.
    The lead split it into an extraction (NM1, NearMissExtractor-SonnetMed: the trial list, recorded gross, the
    D8 fee and slippage split, the shortfall, entry and exit types as written) and an analysis (NM2,
    ExecTriage-OpusXHigh: passive-execution savings against each shortfall using R3/R4's fill-rate and
    adverse-selection evidence, the classification, a top 5 and the Databento data spec), run after R3 and R4.
    The lead rules on what enters S1/S2. The prior closure of passive execution (D.1g/C6: TopstepX fills limits
    only on trade-through; edges resting on SIM fill mechanics are prohibited, P07) is part of NM2's brief and
    of every ranking.
12. **User-directed change, addendum 5 (01:54 PDT).** The triage and S2 keep Group A (up to 5 earlier rules
    that enter against the move and fell short by less than the realistic passive saving) and Group B (1-3 new
    maker-native hypotheses with a published mechanism), excluding breakouts and momentum entries, rules whose
    gross does not cover fees and rules that failed on non-cost grounds, with one shared calibration slice. R3
    and R4 were briefed before this addendum and not on maker-native designs, so the lead added a dedicated
    reader, R17 (SourceReader-MakerNative-OpusHigh), whose output feeds Group B; NM2 builds both groups.
    Launch order under the cap of 20: NM1 (it gates NM2), R17, then R14, R15, R16.
13. **User-directed change, addendum 6 (01:56 PDT).** Two dedicated limit-order readers feeding Group B. R17,
    already queued for addendum 5's maker-native hypotheses, took addendum 6(a) (passive liquidity provision and
    small-scale market making: published strategies, net returns, inventory and adverse-selection handling,
    what survives at retail latency and fees), since the two briefs are one query family. R18
    (SourceReader-QueueFill-OpusHigh) took 6(b) (fill-probability and queue models, adverse selection measured
    on CME or similar futures, data needed, honest limit-order backtest methods, and each prop firm's rules on
    passive or high-frequency order use). New launch order under the cap: R17, R18, R14, R15, R16 (NM1 launched
    01:53 in RD5's slot).
14. **OpenAlex exhausted at 01:47 PDT.** OpenAlex's free daily budget for the machine's IP ran out at 01:46-01:47
    PDT (resets at midnight UTC); the mailto polite pool no longer lifts that cap. The lead added a dated note to
    the shared brief at 01:57: no further OpenAlex calls; forward citations through OpenCitations (free, by DOI),
    Crossref metadata, Semantic Scholar keyless, Firecrawl's related-papers tool and search results. Readers
    already running log the gap and fall back per the brief's rule; a gap is never reported as absence.
15. **Usage-limit cut and scope at resume (06:11 PDT).** The 5-hour usage window ran out at 01:58-02:01 PDT, about
    20 minutes after wave 1's 20 readers started (Stage E.24 shares the account); every running worker stopped.
    The pause (02:01-06:10) is not work time. The prompt's clock was kept (work to 07:00, return by 07:30), so the
    lead resumed only what fits: NM1, R14-R18 by message (06:33 deadline) and fresh R1 and R5 (workflow agents
    cannot be resumed; 06:36 deadline), all told the tool state. R3, R4, R6, R7, RD1, RD2 had substantial partial
    files and are read as left (marked "cut at about 01:58" wherever cited). R2, R8, RD3 and RD6 were not resumed
    (thin partials; R1 and R9 cover the nearest ground), and wave 2 (deep follow-ups R19-R20 and RD8) was dropped.
    NM2 (the execution-triage analysis) was folded into the lead's S2, which owns the shortlist anyway.
16. **Tool exhaustion during wave 1.** Firecrawl's credits ran out at 08:43-08:47 UTC (01:43-01:47 PDT) and OpenAlex's
    daily IP budget at 08:46-08:47 UTC; Playwright's Chrome is not installed (R9). Readers logged each gap; no gap
    is reported as absence.
17. **Planner-approved window change (06:18 PDT).** The planner moved the end of work to 09:00 PDT and the return to
    09:30 PDT, replacing the prompt's 07:00/07:30, and asked that no reader be cut short. The readers resumed at
    06:12 with a 06:33 deadline (choice 15) had already returned by 06:17 with partial lists; with the new window the
    lead ran a second wave for the remaining work (choice 18) instead of re-opening each of them.
18. **Wave 2 composition (06:22 PDT).** With the extended window the lead ran one workflow of 10: three second
    readers on the shortlist (DF1 noise-area momentum, DF2 the 3rd-Friday spike, DF3 the two Treasury drifts; the
    prompt's "second reader on any candidate ranked in the top five"), R6, R2 and R8 finished from their partial
    files, re-digs RD3, RD6 and RD8 (E.20's planning-brief leads), and NM2 (the execution triage at opus xhigh,
    checking the lead's draft Groups A/B). R3, R4, R7, RD1 and RD2 were not rerun: their partial files are
    substantive and are cited as cut. R1, R5, R14, R15, R16 and R18 returned early to the old deadline; their
    unfinished lists stand in their section 10. Ten agents instead of twenty keep the usage burn below wave 1's,
    which exhausted the window in about 20 minutes.
19. **Group A rule (lead, before ranking).** "Failed mainly on cost" was read as gross t >= 1.0 (D5's screen bar)
    with net below zero; "realistic passive saving" as at most the slippage share of the D8 round trip, less under
    TopstepX trade-through fills. Both were fixed before NM1's rows were ranked.
20. **Shortlist vehicles.** C1-C3 are sized on SPY/ES; the program's equity vehicle is MNQ (MES is closed as a
    vehicle since Stage E), so MNQ is the proposed vehicle and MES is shown for reference only; the NQ size of the
    3rd-Friday spike is unverified (NQ appears only in a figure). C4/C5 have no micro (1 ZN).
21. **Second usage-limit cut and planner-approved window (11:16 PDT).** Wave 2 hit the session limit at about
    06:35 PDT (R2 and R6 finished; RD8 finished on disk; DF3 and R8 left near-complete files; DF1, DF2 and NM2 left
    only saved pages); the laptop rebooted at about 10:50. The pause 06:35-11:10 is not work time. The planner set
    work until 15:00 PDT and the return by 15:30 PDT, at most 6 workers at once in this session (two sessions share
    one usage window), finishing started items before opening new ones. The lead re-spawned only the unfinished
    items (DF1, DF2, NM2, RD3, RD6 and a mechanical finisher for DF3's JSON and R8's md), each told to read its own
    files and pages first.
22. **Agent tool instead of a workflow for wave 3.** Ultracode favours workflows, but two usage cuts had already
    discarded the context of every cut workflow agent (workflow agents cannot be resumed by message). Wave 3 used
    the Agent tool so any agent cut by a third limit can be resumed with its context.
23. **What is committed.** The commit holds the return, the STATE file, the progress and STAGES entries, and every
    md, json, py and txt file at the top of reports/stage_e25_briefs/ plus terms/terms_log.md. The raw fetched pages
    (pages/, 273 MB) and saved terms pages (terms/*.html, 12 MB) stay untracked, as in E.13 and E.20: their size,
    and several sites' terms forbid republishing (DO_NOT_COMMIT.txt lists the hosts). Every quote used is in the
    reader files with its URL, fetch time and sha256.
24. **Return sections from parts.** The return was assembled by script (assemble_return.py) from the summary, the
    verbatim check files, the synthesis (v3, after the S4 fixes), the per-reader source lists, the delegation table
    from the transcripts, the verification table, this list, the decisions and the cost section, so that no figure
    was retyped.

## 7. Decisions for the user (each with a recommendation)

1. **Whether to test C1 (noise-area intraday momentum on MNQ), and how.** It is the only frequent candidate that
   clears the hurdle on published numbers and duplicates no trial, but no independent S&P test after
   publication is distinguishable from zero (the latest are negative), the one positive Nasdaq test is a pointer
   (t 1.37), its power on the window is 0.35 at the published size, third-party results already
   cover the research window (so a read of it would not be blind), and its drawdown at 1 MNQ exceeds the 50K and
   100K trailing limits. **Recommendation:** do not register a research-window read. If the user wants one more
   test, register a frozen FORWARD paper record on MNQ (a new registration, N + 1, using the forward plumbing E.24
   builds), with its length and bar fixed from the published Sharpe before day one, and expect it to fail. No
   Combine purchase follows from it unless it passes (V33 stands).
2. **The 3rd-Friday spike (C2/C3) and the Treasury drifts (C4/C5).** Each clears the hurdle on published numbers
   but gives 3-15 events in the research window (power 0.11-0.22 at the published sizes, 0.06-0.17 at the post-2015
   sizes), two shrank after 2015 or between drafts, and
   C4's effect is conditional on a nearby FOMC. **Recommendation:** register nothing now. If the user wants one of
   them kept alive, the cheapest honest option is a forward event log (a few events a year) rather than a test
   that cannot reach power; adding W_cf's post-sample events (V41) lifts C2 only to about 0.25.
3. **Passive execution (Groups A and B).** Group A is empty; B1 would need a Databento purchase (trades and mbp-1)
   and its price saving is under 1% of the published move, with trade-through fills selecting adverse days.
   **Recommendation:** buy nothing; keep the C6 closure; request no quote.
4. **V38's wording.** The re-dig found three working-paper effects above 1.5 x the D8 round trip on the program's
   roots whose samples run past 2015 (pre-refunding ZN, cash returns; pre-FOMC ZN, futures; the ES 3rd-Friday
   reversal), none with a significant post-2015 estimate, each rare and low-powered.
   **Recommendation:** amend V38's sentence to name them as exceptions that cannot be tested with adequate power on
   owned data, leaving the closure of the intraday program in place.
5. **V34's reason for dropping noise-area momentum.** The "unsized" basis is weakened (the authors' FAQ sizes it);
   the post-publication evidence now closes it on the S&P side on other grounds. **Recommendation:** record the
   correction in docs/DECISIONS.md with the post-publication evidence.
6. **Topstep's rules record.** Topstep's Tier 1 news window (2026-10-10..16) overturns E.19's R040 ("news flatten
   not required"). **Recommendation:** refresh reports/stage_e19_rules.json at the next prop-economics stage, before
   any Combine modelling.
7. **Direction.** **Recommendation:** keep the intraday prop program closed (V38); the AiTrader readout
   (2026-10-23) and E.24's forward plumbing remain the next decision points. Prop outcome data (Topstep's 2025
   funnel: about a third of funded individuals paid at least once) and the evidence above give no reason to buy a
   Combine.

## 8. Session cost

Computed at the end from the transcripts (reports/stage_e25_briefs/make_cost.py: the lead's .jsonl and every
subagent transcript under subagents/**, workflow agents included; each message's final usage). Times PDT.
Pauses are their own rows and excluded from work time. These are token counts, not plan-credit percentages.

### Final ETA table (actuals; the initial estimate in the last column)

| # | Task or spawn | Owner / agent | Model | Effort | Start | End | Minutes | Tokens | Status, deviations | Initial estimate |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0 Startup checks | lead | opus | xhigh | 01:27 | 01:28 | 1 | in the lead total | done | done 01:28 |
| 2 | R0 shared brief | lead | opus | xhigh | 01:29 | 01:36 | 7 | in the lead total | done | 25 min, to 02:05 |
| 3 | Wave 1 launch, addenda 1-6 handling, slot launches | lead | opus | xhigh | 01:37 | 02:01 | 24 | in the lead total | cut by the usage limit at 02:01 | R1-R13 60 min, to 03:10 |
| 4 | PAUSE (usage limit) | - | - | - | 02:01 | 06:10 | 249 | - | not work time | - |
| 5 | Resume, synthesis v1, power script, wave 2 launch | lead | opus | xhigh | 06:10 | 06:35 | 25 | in the lead total | cut by the usage limit at about 06:35 | T1 triage 20 min, R14-R20 60 min |
| 6 | PAUSE (usage limit; laptop reboot about 10:50) | - | - | - | 06:35 | 11:15 | 280 | - | not work time | - |
| 7 | Resume, wave 3 launch, synthesis v2, merges | lead | opus | xhigh | 11:15 | 11:30 | 15 | in the lead total | done | S1-S3 60 min, to 05:30 |
| 8 | S4 running: return parts drafted; review fixes, re-check | lead | opus | xhigh | 11:30 | 11:52 | 22 | in the lead total | done | F 20 min, to 06:35 |
| 9 | Cost, progress, STAGES, end checks, assembly, commit | lead | opus | xhigh | 11:52 | 11:54 | 2 | in the lead total | done | Ret 35 min, to 07:10 |
| 10 | spawn | MechIndexer-SonnetMed | sonnet-5-5 | medium | 01:31 | 01:37 | 6 | 5,834,390 | done | - |
| 11 | spawn | PriorSources-HaikuMed | haiku-5-5 | medium | 01:31 | 01:33 | 2 | 2,042,557 | done | - |
| 12 | spawn | SourceReader-0DTEAcademic-OpusHigh | opus-5-5 | high | 01:38 | 02:01 | 23 | 10,678,059 | cut by the usage limit about 01:58 (partial files on disk) | - |
| 13 | spawn | SourceReader-0DTEVendor-OpusHigh | opus-5-5 | high | 01:38 | 01:58 | 20 | 14,004,235 | cut by the usage limit about 01:58 (partial files on disk) | - |
| 14 | spawn | SourceReader-VolumeTradeSide-OpusHigh | opus-5-5 | high | 01:38 | 01:58 | 20 | 14,593,310 | cut by the usage limit about 01:58 (partial files on disk) | - |
| 15 | spawn | SourceReader-PropRules-OpusHigh | opus-5-5 | high | 01:38 | 01:58 | 20 | 15,820,818 | done | - |
| 16 | spawn | SourceReader-Communities-OpusHigh | opus-5-5 | high | 01:38 | 01:53 | 15 | 8,934,782 | done | - |
| 17 | spawn | SourceReader-RegimeFilters-OpusHigh | opus-5-5 | high | 01:38 | 01:57 | 19 | 15,697,314 | done | - |
| 18 | spawn | SourceReader-PropOutcomes-OpusHigh | opus-5-5 | high | 01:38 | 01:58 | 20 | 14,866,390 | cut by the usage limit about 01:58 (partial files on disk) | - |
| 19 | spawn | SourceReader-OrderFlow-OpusHigh | opus-5-5 | high | 01:38 | 01:59 | 21 | 17,703,698 | cut by the usage limit about 01:58 (partial files on disk) | - |
| 20 | spawn | SourceReader-News-OpusHigh | opus-5-5 | high | 01:38 | 01:59 | 21 | 14,396,977 | cut by the usage limit about 01:58 (partial files on disk) | - |
| 21 | spawn | SourceReader-SchedEvents-OpusHigh | opus-5-5 | high | 01:38 | 01:59 | 21 | 27,824,773 | cut by the usage limit about 01:58 (partial files on disk) | - |
| 22 | spawn | SourceReader-LiveRecords-OpusHigh | opus-5-5 | high | 01:38 | 02:00 | 22 | 11,733,083 | cut by the usage limit about 01:58 (partial files on disk) | - |
| 23 | spawn | SourceReader-LeadLag-OpusHigh | opus-5-5 | high | 01:38 | 01:57 | 19 | 17,598,648 | done | - |
| 24 | spawn | SourceReader-Practitioner-OpusHigh | opus-5-5 | high | 01:38 | 01:55 | 17 | 12,715,339 | done | - |
| 25 | spawn | RedigReader-EquityIndex-OpusHigh | opus-5-5 | high | 01:38 | 01:58 | 20 | 14,557,908 | cut by the usage limit about 01:58 (partial files on disk) | - |
| 26 | spawn | RedigReader-Rates-OpusHigh | opus-5-5 | high | 01:38 | 01:59 | 21 | 17,691,494 | cut by the usage limit about 01:58 (partial files on disk) | - |
| 27 | spawn | RedigReader-TrendCarry-OpusHigh | opus-5-5 | high | 01:38 | 01:57 | 19 | 17,923,544 | done | - |
| 28 | spawn | RedigReader-EnergyMetals-OpusHigh | opus-5-5 | high | 01:38 | 01:59 | 21 | 11,204,753 | cut by the usage limit about 01:58 (partial files on disk) | - |
| 29 | spawn | RedigReader-FXAgs-OpusHigh | opus-5-5 | high | 01:38 | 01:58 | 20 | 13,617,317 | done | - |
| 30 | spawn | RedigReader-InfoSources-OpusHigh | opus-5-5 | high | 01:38 | 01:58 | 20 | 12,142,629 | cut by the usage limit about 01:58 (partial files on disk) | - |
| 31 | spawn | RedigReader-DealerGamma-OpusHigh | opus-5-5 | high | 01:38 | 01:52 | 14 | 9,668,684 | done | - |
| 32 | spawn | NearMissExtractor-SonnetMed | sonnet-5-5 | medium | 01:53 | 06:12 | 259 | 8,567,134 | cut by the usage limit about 01:58; resumed by message 06:12; done | - |
| 33 | spawn | SourceReader-MakerNative-OpusHigh | opus-5-5 | high | 01:54 | 06:15 | 261 | 4,612,407 | cut by the usage limit about 01:58; resumed by message 06:12; done | - |
| 34 | spawn | SourceReader-QueueFill-OpusHigh | opus-5-5 | high | 01:56 | 06:16 | 260 | 3,881,034 | cut by the usage limit about 01:58; resumed by message 06:12; done | - |
| 35 | spawn | SourceReader-Podcasts-OpusHigh | opus-5-5 | high | 01:57 | 06:17 | 260 | 3,260,228 | cut by the usage limit about 01:58; resumed by message 06:12; done | - |
| 36 | spawn | SourceReader-NicheMarkets-OpusHigh | opus-5-5 | high | 01:58 | 06:16 | 258 | 2,541,068 | cut by the usage limit about 01:58; resumed by message 06:12; done | - |
| 37 | spawn | SourceReader-NicheAccess-OpusHigh | opus-5-5 | high | 01:58 | 06:17 | 259 | 3,783,035 | cut by the usage limit about 01:58; resumed by message 06:12; done | - |
| 38 | spawn | SourceReader-0DTEAcademic-OpusHigh | opus-5-5 | high | 06:13 | 06:17 | 4 | 2,664,791 | done | - |
| 39 | spawn | SourceReader-News-OpusHigh | opus-5-5 | high | 06:13 | 06:16 | 3 | 1,238,405 | done | - |
| 40 | spawn | DeepReader-NoiseAreaMomentum-OpusHigh | opus-5-5 | high | 06:21 | 06:33 | 12 | 7,773,021 | cut by the usage limit about 06:35 (partial files on disk) | - |
| 41 | spawn | ExecTriage-OpusXHigh | opus-5-5 | xhigh | 06:21 | 06:33 | 12 | 10,744,732 | cut by the usage limit about 06:35 (partial files on disk) | - |
| 42 | spawn | DeepReader-TreasuryDrifts-OpusHigh | opus-5-5 | high | 06:21 | 06:35 | 14 | 15,123,531 | cut by the usage limit about 06:35 (partial files on disk) | - |
| 43 | spawn | DeepReader-ThirdFriday-OpusHigh | opus-5-5 | high | 06:21 | 06:33 | 12 | 11,889,228 | cut by the usage limit about 06:35 (partial files on disk) | - |
| 44 | spawn | SourceReader-SchedEvents-OpusHigh | opus-5-5 | high | 06:21 | 06:30 | 9 | 7,929,184 | done | - |
| 45 | spawn | SourceReader-PropOutcomes-OpusHigh | opus-5-5 | high | 06:21 | 06:33 | 12 | 9,649,842 | cut by the usage limit about 06:35 (partial files on disk) | - |
| 46 | spawn | RedigReader-InfoSources-OpusHigh | opus-5-5 | high | 06:21 | 06:33 | 12 | 8,554,550 | cut by the usage limit about 06:35 (partial files on disk) | - |
| 47 | spawn | RedigReader-EnergyMetals-OpusHigh | opus-5-5 | high | 06:21 | 06:33 | 12 | 12,456,717 | cut by the usage limit about 06:35 (partial files on disk) | - |
| 48 | spawn | RedigReader-E20Planning-OpusHigh | opus-5-5 | high | 06:21 | 06:33 | 12 | 8,704,329 | cut by the usage limit about 06:35 after its md and json were complete | - |
| 49 | spawn | SourceReader-0DTEVendor-OpusHigh | opus-5-5 | high | 06:21 | 06:32 | 11 | 10,557,795 | done | - |
| 50 | spawn | DeepReader-NoiseAreaMomentum-OpusHigh | opus-5-5 | high | 11:16 | 11:24 | 8 | 4,697,821 | done | - |
| 51 | spawn | DeepReader-ThirdFriday-OpusHigh | opus-5-5 | high | 11:16 | 11:25 | 9 | 7,074,534 | done | - |
| 52 | spawn | ExecTriage-OpusXHigh | opus-5-5 | xhigh | 11:16 | 11:29 | 13 | 7,335,560 | done | - |
| 53 | spawn | RedigReader-EnergyMetals-OpusHigh | opus-5-5 | high | 11:16 | 11:24 | 8 | 6,034,214 | done | - |
| 54 | spawn | RedigReader-InfoSources-OpusHigh | opus-5-5 | high | 11:16 | 11:23 | 7 | 4,989,646 | done | - |
| 55 | spawn | FileFinisher-SonnetMed | sonnet-5-5 | medium | 11:16 | 11:17 | 1 | 590,206 | done | - |
| 56 | spawn | ShortlistReviewer-FableXHigh | fable-5-1 | xhigh | 11:30 | 11:51 | 21 | 3,721,751 | done | - |

| Cumulative | whole stage | lead + 47 spawns | | | 01:27 | 11:54 | wall 627 (pauses 529; work 98) | 527,784,311 (lead 58,158,846; workers 469,625,465) | | initial estimate: 01:28-07:10 (342 min of work) |

### Tokens per model

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-fable-5-1 | 484 | 86,100 | 3,319,695 | 315,472 | 3,721,751 |
| claude-haiku-5-5 | 38 | 19,220 | 1,888,042 | 135,257 | 2,042,557 |
| claude-opus-5-5 | 6,028 | 2,323,698 | 494,675,807 | 10,022,740 | 507,028,273 |
| claude-sonnet-5-5 | 188 | 102,092 | 14,090,285 | 799,165 | 14,991,730 |
| all | 6,738 | 2,531,110 | 513,973,829 | 11,272,634 | 527,784,311 |

Delegation share: lead 58,158,846 (11.0%), workers 469,625,465 (89.0%). By model: claude-fable-5-1 0.7%, claude-haiku-5-5 0.4%, claude-opus-5-5 96.1%, claude-sonnet-5-5 2.8%

One line per worker spawn (agent file by effort: worker-medium, worker-high, worker-xhigh): the spawn rows of the
table above and section 4. The lead's last messages after the count (assembly and commit) are not included.
