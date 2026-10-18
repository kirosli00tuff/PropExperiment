# Stage E.24 D2: the user's setup checklist for the forward tests

Written by the Stage E.24 lead, 2026-10-18. No session opens an account, enters a credential or connects to a broker
for you. Facts are cited from reports/stage_e24_briefs/facts/ (ibkr_facts.md I1-I9, alpaca_facts.md A1-A10); items
marked [unverified] are open in those files. Steps 1-4 are yours; step 5 is the approval the next session needs.

## 0. Decide E22-F1's settlement source first (E.24 return, section 7, decision 1)

IBKR's daily futures close is the last traded price and only "can be" the settlement (I6). Before the IBKR steps below
matter for E22-F1, choose one of the two options in the return (a pre-clock amendment E22-F1b, N + 1, or a second
source for settlements only). The IBKR account is still useful for the shadow orders and as a price source either way.

## 1. IBKR account, paper account and market data (for E22-F1)

1. Open an IBKR Pro individual account. A paper account comes with it: "New individual account holders automatically
   receive a paper trading account" (I2). IBKR's pages disagree on whether the live account must be funded or only
   approved before paper access [unverified]; the market data rule below needs funding anyway.
2. Check which IBKR entity holds your account (as a Canadian resident it may be IBKR Canada) and that it can trade CME,
   CBOT, NYMEX and COMEX futures; request US futures trading permissions ("requires clients to have US Futures Trading
   Permissions", I8). IBKR Canada's API restriction concerns products on Canadian exchanges (I8 note); confirm with
   IBKR if unsure.
3. Fund it with at least **USD 500 plus the subscription cost** (likely needed): IBKR's docs say API historical bars
   need the same Level 1 subscription as live data (I4), but the fact check found two official pages describing a
   delayed path (request delayed data, reqMarketDataType(3), before the historical request; ibkr_factcheck.md C1), so
   this is medium confidence: the next session probes the delayed path first and you subscribe only if it fails.
   Market data needs USD 500 of equity on an IBKR Pro account (I8). Set your market data status to
   **non-professional** (everyone is professional until they change it, I8) and enable Market Data API access in
   Client Portal.
4. Subscribe to the cheapest coverage: "CME Real-Time (L1)", "CBOT Real-Time (L1)", "COMEX Real-Time (L1)" and
   "NYMEX Real-Time (L1)" at **USD 1.55 per month each, USD 6.20 in total** (non-professional; each waived above USD 20
   of monthly commissions), or the "US Securities Snapshot and Futures Value Bundle" at USD 10.00 a month (I8). Whether
   the single-exchange rows can be bought without the bundle is [unverified]; take the bundle if the portal requires it.
5. Share the live user's market data with the paper user (Client Portal, paper trading settings). The paper user has
   no subscriptions of its own, and with sharing the live and paper sessions must not run on different machines (I2).

## 2. IB Gateway and IBC on the ThinkPad (or let the next session do it)

1. Install the **stable, offline (standalone)** IB Gateway for Linux x86_64 (IBC needs the offline build, I1); install
   xterm. A graphical login is required: IBKR does not support a headless Gateway (I1).
2. Install IBC 3.24.2 (the project was retired on 1 September 2026 and gets bug fixes only, I1). In IBC's own
   config.ini (outside this repository, never committed): `TradingMode=paper`, `IbLoginId` and `IbPassword` of the
   **paper** username, `AcceptNonBrokerageAccountWarning=yes`. Alternatively leave them out of config.ini and export
   them from .env when you start IBC (step 4); IBC advises against putting them in gatewaystart.sh (I1).
3. API settings in Gateway: socket port **4002** (paper), "Read-Only API" off only if the shadow orders will be used,
   trusted IP 127.0.0.1.
4. Expect one manual login (with two-factor authentication, which IBKR requires for all users; whether a paper username
   prompts for it is [unverified]) each week, the first start after Sunday 01:00 ET; IBC restarts the Gateway daily
   without re-authenticating (I1).

## 3. Alpaca paper account (for E22-F2)

1. Create a **paper-only** account at alpaca.markets with an email address; no funding is needed (A1). The paper
   balance defaults to $100,000; E22-F2's book uses its own fixed $25,000 regardless.
2. Generate a paper API key id and secret in the paper dashboard (A1). alpaca-py reads no environment variables itself
   (A1); forward/sources_alpaca.py and forward/orders_alpaca.py read the names in step 4.
3. Market data: the free Basic plan (IEX real time, history back to 2016) is assumed; Alpaca's pages conflict on whether
   a paper-only account may read SIP history older than 15 minutes (A2). E22-F2 section 6 fixes what happens either way;
   no paid plan ($99 a month, A2) is needed for E22-F2.

## 4. Put the credentials in .env yourself

Add these lines to .env in the repository root (it is git-ignored). No session reads, prints, copies or logs their
values; sessions report only each name and whether it is empty or non-empty (reports/stage_e24_briefs/checks.sh).

| Variable | Used by | Value |
|---|---|---|
| IBKR_GATEWAY_HOST | forward/ibkr_gateway.py | 127.0.0.1 |
| IBKR_GATEWAY_PORT | forward/ibkr_gateway.py | 4002 (paper) |
| IBKR_CLIENT_ID | forward/ibkr_gateway.py | any integer you reserve for these scripts, e.g. 17 |
| IBKR_ACCOUNT_ID | forward/orders_ibkr.py (shadow orders only) | your paper account id (starts with DU) |
| IBKR_PAPER_USERNAME, IBKR_PAPER_PASSWORD | your IBC start command only (never read by Python) | the paper login, only if you choose not to keep it in IBC's config.ini |
| ALPACA_PAPER_KEY_ID | forward/sources_alpaca.py, forward/orders_alpaca.py | the paper key id |
| ALPACA_PAPER_SECRET_KEY | same | the paper secret |

## 5. Approve the first connection session

When steps 0-4 are done, approve a stage that: runs the start checks; corrects forward/rolls_f1.json before the clock
if needed; checks both connections without reading prices; reads the warm-ups exactly as
reports/stage_e24_warmup_declaration.md declares (E22-F2 first, then E22-F1); records sources, approval dates and
warm-up sha256 values in docs/DECISIONS.md; and writes the first ledger records. Say in that approval whether the
shadow order routes (off by default) are to be turned on, and whether the broker libraries may be installed through the
pinned overlay (forward/requirements_broker.txt, `uv run --frozen --with-requirements ...`).
