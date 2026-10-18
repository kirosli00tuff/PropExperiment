STAGE E.24 "FORWARD PLUMBING: THE LOADER FIX, THE IBKR AND ALPACA PAPER ADAPTERS, AND THE E22-F2 ETF REGISTRATION"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: A build stage, no outcome read and no market data read (V41,
V42). Four parts, run in parallel where independent:
- Part A: the multi-day loader fix approved in V41 (E.23 VerdictVerifier
  NOTE-2, NOTE-5).
- Part B: an IBKR paper adapter for E22-F1 through IB Gateway (IBC for
  restarts) on this ThinkPad, plugged into forward/ as a source and an
  optional shadow order route. The registered verdict of E22-F1 stays the
  paper book of its freeze (fills at the next settlement); IBKR paper
  orders are a shadow record only.
- Part C: an Alpaca paper adapter and a new frozen registration E22-F2:
  the same trend rule on a US ETF universe, N 538 -> 539.
- Part D: the warm-up read declarations for E22-F1 and E22-F2 (no read
  tonight), and a setup checklist for the user.
No account exists yet; every adapter is built and tested against mocks
and recorded fixtures written by hand, never against a live endpoint.

Decisions in force: docs/DECISIONS.md V20 to V42. Binding: this prompt,
reports/stage_e22_prereg_F1.md (frozen; nothing in it changes), V37.

Lead: Opus 5.5, effort xhigh. Ultracode: on (launched interactively).

Why this lead and effort: broker adapters fail silently on contract
months, rolls, time zones, partial data and reconnects; the ETF
registration is a new frozen test whose sizing, leverage cap and cost
model must be fixed before any price exists. Fable reviews the loader
change, both adapters and the E22-F2 registration before any freeze.

Usage and time: launched about 01:50 PDT on 2026-10-18, in parallel with
Stage E.25 (research only). Work to finish by 07:00 PDT; by 07:30 the
return is written with each part's status, finished or not. Checkpoint
reports/stage_e24_STATE.md after every step so a resume after a usage
limit starts from disk. Compute is light; at most 2 heavy workers, and
E.25 is running beside this session.

Do not stop to ask, and do not use AskUserQuestion. Decide, log the choice
under Open choices in the return document, and continue.

============================================================
PART A: THE LOADER FIX (V41)
============================================================

A1. Read reports/E.23_RETURN.md section 7 item 5 and
reports/stage_e23_briefs/verify/verdict_verify.md NOTE-2 and NOTE-5.
Change base_rules/context.py or multiday/ (whichever the notes name) so
that a multi-day read loads each store only up to the read window's last
bar (no later bar is ever in memory), and multi-day books write per-unit
and per-fill files as E.21 did. No frozen member, freeze or earlier
stage's code path changes behaviour: prove it by re-running the E.21 and
E.23 test suites unchanged and by a replay of E.23's discovery books in a
scratch directory (test mode, no marker, numbers compared to the
recorded ones; this re-reads E.23's own already-read window and is not
an outcome read). If a frozen file must change, stop Part A and log it.
A2. LoaderReviewer-FableXHigh reviews the diff; BLOCKING and SHOULD FIX
fixed first. If the change touches a file pinned by a harness manifest,
write a new harness version (v14) with the manifest, Fable-reviewed and
committed, as E.22 did for v13.

============================================================
PART B: IBKR PAPER ADAPTER FOR E22-F1
============================================================

B1. Facts first (IBKRReader-OpusHigh, read-only, official IBKR pages and
the ib_async or ib_insync docs; each site's terms read before any
automated fetch): IB Gateway and IBC setup on Linux, daily restart and
the weekly re-authentication; paper account requirements; delayed (10
minute) futures data in paper accounts; whether historical daily bars of
CME futures come through the API without a subscription, how far back
for expired contracts, and whether the daily bar's close is the official
settlement or the last trade; the cheapest CME subscription if one is
needed, its price and the funded-account rule.
B2. Build forward/sources_ibkr.py: given the 12 micros of E22-F1, the
contract months from forward/rolls_f1.json, returns each day's price in
the history format of forward/history.py, and the warm-up history
assembled per contract and back-adjusted exactly as E22-F1 section 2
requires. If the IBKR daily close is not the official settlement, do
NOT register anything new: write the evidence and the two options
(a pre-clock amendment as a new registration E22-F1b with N + 1, or a
second source for settlements only) under Decisions for the user.
B3. Build forward/orders_ibkr.py: the shadow route. After each day's
runner step, it places the target positions' changes as paper orders in
the IBKR paper account and records fills in a separate shadow ledger,
never in the E22-F1 ledger. Off by default; a config switch turns it on.
B4. Tests with a mock gateway (no network): contract resolution, rolls
across the anchor date, a missing day, a reconnect, a partial history,
the warm-up assembly, time zones, and a test that the E22-F1 ledger is
byte-identical with the shadow route on and off.
B5. AdapterReviewer-FableXHigh reviews B2 to B4.

============================================================
PART C: ALPACA PAPER ADAPTER AND THE E22-F2 REGISTRATION
============================================================

C1. Facts first (AlpacaReader-OpusHigh, read-only, Alpaca's official
docs; terms read first): paper account, keys, the free IEX data feed,
historical daily bars (depth, adjustment for splits and distributions,
which close), fractional orders (long only), short selling and borrow in
paper, margin and buying power (Reg T), order types at or near the
close, rate limits.
C2. E22-F2 design, written before any ETF price exists: the E22-F1 rule
(forward/core.py, the same speeds, scalars, caps, FDM method, 20%
volatility target, $25,000 notional, fixed capital) on this universe:
QQQ, IWM, GLD, USO, UNG, FXE, SHY, IEF, TLT, CORN, SOYB (the 12th
exposure of E22-F1, soybean oil, has no liquid ETF: record it as not
modelled, or name a substitute with a reason). Fix, with a source or a
stated reason for each: the price series (split- and
distribution-adjusted daily closes), fills (the next session's close,
paper), fractional longs and whole-share shorts, a cost model (half the
quoted spread plus regulatory fees, and a declared borrow cost for
shorts), a gross leverage cap at the account's overnight buying power
with proportional scale-down, the IDM and FDM rule (no ETF history is
read: use E22-F1's frozen FDM and an IDM from a declared correlation
assumption, or Carver's published table, stated), warm-up depth, the
missing-day and ledger rules (mirror E22-F1 sections 6 and 7), the
36-month horizon and the same bar as E22-F1 section 8 with its power
statement. Alpaca paper orders are a shadow record, as in B3.
C3. Build forward/sources_alpaca.py, forward/orders_alpaca.py and
forward/config_f2.json (and any table files), with tests on mocks and
hand-written fixtures, as B4.
C4. RegReviewer-FableXHigh reviews the E22-F2 text and code before the
freeze; BLOCKING and SHOULD FIX fixed first. Freeze
reports/stage_e24_prereg_F2.md with a sha256 file list, commit, then
register: N 538 -> 539 (ledger/trial_registrations.jsonl).

============================================================
PART D: WARM-UP READ DECLARATIONS AND THE USER CHECKLIST
============================================================

D1. reports/stage_e24_warmup_declaration.md: for E22-F1 and E22-F2,
exactly which series and dates the first connection session will read
(E22-F1: daily prices of the 12 micros from 2024-03-01 to the start
date, per V42; E22-F2: ETF daily closes, which were never sealed), what
each read spends (V42: holdout-2 for MGC, MCL and MNG, and the research
window for the 12 micros, spent for trend-type and multi-day hypotheses
only), the files and sha256 the read will write, and the order of
events in that session. No read happens in this stage.
D2. reports/stage_e24_user_checklist.md: what the user does, step by
step: open the IBKR account and its paper account (and fund it only if
B1 shows it is needed, with the amount), install IB Gateway and IBC (or
let the next session do it), create the Alpaca paper account, put both
sets of credentials in .env himself under the variable names this stage
defines (never read or printed by any session; only names and empty or
non-empty status), and approve the first connection session.

============================================================
SCOPE
============================================================

This stage does NOT:
- connect to IBKR, Alpaca or any broker or data endpoint, or read any
  market data (historical or live, owned or not), except the scratch
  replay of E.23's own already-read window in A1
- buy anything, call Databento, or subscribe to any data
- change reports/stage_e22_prereg_F1.md or any file in its section 11
  list (a needed change is logged, not made)
- read holdout-2, the embargo, the research window, MES's sealed stores,
  or anything dated 2024-03-01 or later
- touch live/, ops/, any TopstepX credential or the ProjectX API
- print, copy or log any key; read .env values. REGISTRATION.md stays 0
  bytes.
- push

============================================================
GUARDRAILS
============================================================

- Harness v13 dd2bcc6025144e0debd19be1ca8d43c983872a27c9258895ef55ee3c138609e4
  (or v14 if Part A commits one) verified at start and end.
- Holdout status all_ok, 0 unlocks, at start and end; spend ledger
  unchanged.
- Start and end checks quoted verbatim in the return: `git status
  --short`, `git log --oneline -3`, the holdout status, `wc -c
  REGISTRATION.md`, the freeze verifications (E22-F1's included), the
  ledger line count and sha256, N, and `uv run pytest -q -p
  no:cacheprovider` (stop it if free memory falls below 2 GB and quote
  the last full run on identical code).
- New dependencies (ib_async or ib_insync, alpaca-py) added with uv and
  pinned; nothing installed system-wide.
- Before ending, confirm no worker or background shell is still running.

============================================================
DELEGATION PLAN
============================================================

| Step | Owner | Model | Effort | Parallel or serial | Why this tier |
|---|---|---|---|---|---|
| 0 Startup | lead | opus | xhigh | first | gates the session |
| A1 loader fix | LoaderCoder-OpusXHigh | opus | xhigh | parallel with B and C | frozen-code safety |
| A2 review | LoaderReviewer-FableXHigh | fable | xhigh | after A1 | independent check |
| B1, C1 facts | IBKRReader-OpusHigh, AlpacaReader-OpusHigh | opus | high | at once | official docs |
| B2-B4 IBKR code | IBKRCoder-OpusXHigh | opus | xhigh | after B1 | contracts, rolls, warm-up |
| C2 F2 design | lead | opus | xhigh | after C1 | registration text reserved to the lead |
| C3 Alpaca code | AlpacaCoder-OpusXHigh | opus | xhigh | after C2 | sizing, leverage cap, costs |
| B5, C4 reviews | AdapterReviewer-FableXHigh, RegReviewer-FableXHigh | fable | xhigh | after the code | independent check before freeze |
| D1, D2 | lead | opus | xhigh | after B1, C1 | reserved |
| Return | lead | opus | xhigh | last | reserved |

    DELEGATION PLAN (the lead executes this; it does not do worker tasks)
    1. Decompose each task into subtasks with one objective, inputs, output
       path and format, allowed tools, and boundaries.
    2. Route per CLAUDE.md. State model and effort for each subtask before
       spawning.
    3. Run independent workers at once (V37); heavy compute at most 2.
    4. Collect results as files plus short summaries.
    5. Verify every frozen number and every registration with an
       independent fable xhigh worker.
    6. Synthesize in the lead against this prompt, and write the synthesis
       to disk before ending.
    7. Unattended run: no pauses to ask. Checkpoint to
       reports/stage_e24_STATE.md after each task.

============================================================
DELIVERABLE: ONE RETURN DOCUMENT
============================================================

Write reports/E.24_RETURN.md, one progress.md entry, one docs/STAGES.md
line, and one final commit "Stage E.24 forward plumbing and E22-F2". No
push. Fixed sections:

1. Summary, at most 300 words: each part's status; the IBKR settlement
   finding; E22-F2's registration and N; what the user does next.
2. Guardrail evidence: start and end checks verbatim; order of events.
3. Results: the loader diff and its proofs; both adapters and their
   tests; the E22-F2 design table; the warm-up declarations; the
   checklist.
4. Delegation record.
5. Verification: each Fable finding, the ruling and the fix.
6. Open choices: every decision the lead made on its own, with the reason.
7. Decisions for the user, each with a recommendation.
8. Session cost: the final ETA table and the per-model token table, per
   CLAUDE.md. Never estimated.

The last thing before ending: list every open choice in section 6 of the
return document.

END PROMPT
