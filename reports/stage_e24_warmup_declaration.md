# Stage E.24 D1: warm-up read declarations for E22-F1 and E22-F2

STATUS: DECLARED by the Stage E.24 lead (Opus 5.5 xhigh), 2026-10-18, before any connection. No read happens in Stage
E.24: no broker or data endpoint was contacted, and no price, return or quote of any futures contract or ETF was read.
This file declares exactly what the FIRST CONNECTION SESSION (a later stage, approved by the user) reads, what each
read spends, which files it writes and in which order. Approvals: V42 (user, 2026-10-18) approves E22-F1's warm-up
read and E22-F2 on Alpaca paper. The session may not read anything not listed here.

## 1. E22-F1 (micro trend book, registered r007-E22, reports/stage_e22_prereg_F1.md, FROZEN)

| Item | Declaration |
|---|---|
| Series | Daily prices of E22-F1's 12 micros (MNQ, M2K, MGC, MCL, MNG, M6E, 2YY, 10Y, 30Y, MZC, MZS, MZL), one daily bar per contract per CME trade date, from IBKR through IB Gateway (paper login) with forward/sources_ibkr.py |
| Contracts | For each trade date, the reference contract that forward/rolls_f1.json (after any pre-clock correction, F1 section 7) gives, and the next contract on the dates around each roll the frozen runner needs (both prices on a switch date); expired contracts through includeExpired |
| Dates | Trade dates from **2024-03-01** to the trade date before the start date (V42), inclusive. IBKR serves expired contracts only about 2 years after expiry (ibkr_facts.md I5), so for a start in late 2026 the contracts that expired in 2024 are not available and the warm-up will in practice begin later (each instrument's first date is recorded; E22-F1 section 7 needs at least 260 prior trade dates, which the available contracts still give). The spend below is declared for the whole V42 range regardless |
| Field | The close of IBKR's daily TRADES bar (reqHistoricalData, barSizeSetting "1 day", dated by the session's closing day). IBKR documents it as the "Last traded price"; its legacy docs say it "can be the settlement price if provided by the exchange" (reports/stage_e24_briefs/facts/ibkr_facts.md I6). It is therefore NOT declared to be the settlement: this read happens only if the user's settlement-source decision (Precondition row) makes IBKR's close the approved series (an amendment E22-F1b) or keeps IBKR only for the dates a second settlement source does not cover. Requires the Level 1 subscriptions of I4/I8 |
| Not read | Any intraday bar, tick, quote, depth or option; any other root; MES; anything dated on or after the start date except through the ledger's daily steps |
| Precondition | The user's decision on E22-F1's settlement source (E.24 return section 7) is recorded in docs/DECISIONS.md BEFORE this read: E22-F1 section 7 requires the warm-up to be "the approved source's own back history of daily settlements", so IBKR's history is the warm-up only if IBKR is the approved source |

What the read spends (V42, user): **holdout-2** (trade dates 2024-04-01 to 2025-03-31; its sealed chunks begin with the
2024-03 embargo month, docs/HOLDOUT2_MANIFEST.json) **for MGC, MCL and MNG**, and the **research window** (the trade
dates from 2025-04-01 up to holdout-1's first trade date, 2026-06-22, exclusive) **for the 12 micros**; the 2024-03
embargo month is inside V42's approved range ("from 2024-03-01") and is spent with it. The spend is for **trend-type and
multi-day hypotheses only**: after the read, no trend-type or multi-day hypothesis on these roots may use these windows
as untouched confirmation data. Intraday registered reads of the research window stay possible (V42). Nothing sealed is
unlocked: the read takes IBKR's prices, never the program's sealed stores; `data.holdout status` must show all_ok and 0
unlocks before and after.

## 2. E22-F2 (ETF trend book, registered in Stage E.24 as r009, reports/stage_e24_prereg_F2.md)

| Item | Declaration |
|---|---|
| Series | Daily bars of QQQ, IWM, GLD, USO, UNG, FXE, SHY, IEF, TLT, CORN, SOYB and BIL from Alpaca's market data API with forward/sources_alpaca.py, each requested twice: adjustment "raw" and adjustment "all" |
| Feed | "sip"; if SIP daily bars are refused for the account, "iex", fixed before any ledger record (E22-F2 section 6; alpaca_facts.md A2, A4). The close is the last eligible regular-hours trade of the session |
| Dates | NYSE sessions from **2024-03-01** to the session before the start date, inclusive (E22-F2 section 7) |
| Not read | Any intraday bar, trade, quote or option; any other symbol |

What the read spends: nothing. ETF prices were never sealed (V42) and no program window is defined on them.

## 3. Files the session writes (sha256 computed right after each write)

| File | Content | Recorded where |
|---|---|---|
| ledger/forward/E22-F1_warmup_raw.jsonl | Every IBKR bar response of the warm-up: contract, conId, bar date, the delivered fields, request time (UTC) | sha256 in docs/DECISIONS.md and the connection stage's STATE file |
| ledger/forward/E22-F1_warmup.jsonl | The warm-up history in forward.history.load_warmup's format (HistoryRow JSONL, references after rolls, both prices on switch dates) | sha256 in docs/DECISIONS.md and reports/stage_e22_STATE.md (F1 section 6) before the first ledger record; it enters every record's fingerprint |
| ledger/forward/E22-F1_prices.csv | Daily prices in forward.sources' CSV format (the frozen runner's --csv), appended once per trade date | sha256 per day in the ledger record's inputs |
| ledger/forward/E22-F2_warmup_raw.jsonl | Every Alpaca bar response of the warm-up (raw and all), with the request time (UTC) | sha256 in docs/DECISIONS.md and the STATE file |
| ledger/forward/E22-F2_warmup.jsonl | The warm-up in forward.etf_bars' format (close, ret, prev_date per symbol per session) | sha256 in docs/DECISIONS.md and the STATE file before the first E22-F2 record; in every record's fingerprint |
| ledger/forward/E22-F1.jsonl, E22-F2.jsonl | The registered ledgers (append-only sha256 chains), first record on the start date | committed after each session |
| ledger/forward/E22-F1_shadow_ibkr.jsonl, E22-F2_shadow_alpaca.jsonl | Shadow order ledgers, only if the user turns the shadow routes on (off by default) | never part of a verdict |

No credential, key, account number or .env value is written to any file, log or commit.

## 4. Order of events in the first connection session

1. Start checks (verbatim in that stage's return): git status, holdout status (all_ok, 0 unlocks), harness verify,
   `sha256sum -c reports/stage_e22_f1_files.sha256` and `sha256sum -c reports/stage_e24_f2_files.sha256`, the trial
   ledger (N 539) and spend ledger unchanged, `.env` variable NAMES with empty or non-empty status only.
2. E22-F1's pre-clock roll check: forward/rolls_f1.json against the exchanges' published roll and expiry calendars; a
   correction is logged with its new sha256 in docs/DECISIONS.md and the STATE file (F1 section 7; not a new
   registration). E22-F1's settlement-source decision must already be in docs/DECISIONS.md.
3. Connection checks without prices: IB Gateway reachable on the paper port, the 12 micros' contract details resolved
   (contract metadata only); Alpaca account endpoint reports a paper account. Any failure stops the session before a read.
4. Warm-up reads, once each: E22-F2 first (it spends nothing), then E22-F1. Each file of section 3 written and hashed;
   each read logged with its UTC start and end time and the row counts per series.
5. Records in docs/DECISIONS.md and the STATE files (F1 section 6, F2 section 6): source name and terms, approval date,
   warm-up sha256, instruments live on the start date, the start date rule.
6. The first ledger records on the first trade date whose data the sources deliver after the warm-up (the clock
   starts); the shadow routes stay off unless the user's approval of that session turns them on.
7. End checks (as step 1), the holdout status unchanged, a commit of the ledgers and records; no push unless approved.
