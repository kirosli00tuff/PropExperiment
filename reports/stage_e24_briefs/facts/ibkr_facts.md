# IBKR facts for the forward adapter (Stage E.24, IBKRReader-OpusHigh)

Read-only research, 2026-10-18, 01:35 to 02:00 PDT. Every quote below is verbatim from a page saved under
`reports/stage_e24_briefs/pages/ibkr/`. "Row n" points to the fetch table in `facts/ibkr_log.md`, which also holds each
file's sha256. Fetch times are UTC. Grep the `.html.txt` copies for the quotes, not the raw HTML.
"Legacy" means interactivebrokers.github.io/tws-api. Each legacy page carries the banner "This documentation is now
deprecated. Please switch to the IBKR Campus for up-to-date information regarding IBKR's API". It is still IBKR's own
text, but older.

Confidence scale: high = the current official page says it directly; medium = legacy official page, indirect official
wording, or conflicting official pages; low = inference or third party.

---

## I1. IB Gateway on Linux, paper login, ports, daily restart, weekly re-authentication, IBC, 2FA

**Answer.**
- *Install:* IBKR publishes Linux x86_64 and ARM64 standalone installers for "Latest" and "Stable" IB Gateway. Neither updates itself. IBC requires the offline (standalone) build and recommends "stable" for live trading. On Linux, IBC also needs `xterm`.
- *GUI:* a GUI login is required. IBKR does not support a headless TWS or Gateway. (IBC works by driving the login dialog.)
- *Default ports:* TWS live 7496, TWS paper 7497; IB Gateway live 4001, IB Gateway paper 4002. These are defaults and can be changed. API "Read-Only" is on by default and blocks API orders.
- *Daily restart:* both apps are built to restart daily. Auto-restart (v974+) allows Sunday-to-Sunday running without re-authenticating.
- *Weekly re-authentication:* manual authentication is needed once a week. The most specific official page says security tokens are invalidated "each Sunday at 1:00 am ET". Two other official pages conflict with it: one says "after the nightly server reset on Saturday night", the other says "the weekly authentication cycle starts on every Monday".
- *What IBC does (v3.24.2, released 2026-08-21):* logs in, clicks "Accept incoming connection", handles daily auto-restart (authentication only the first time after 01:00 ET Sunday), keeps re-sending IBKR Mobile 2FA alerts, and offers a Sunday "ColdRestartTime". IBC has been retired and its repository archived (1 Sept 2026): bug fixes only, no support on the repo.
- *How IBC takes credentials:* `config.ini` keys `IbLoginId`, `IbPassword`, `TradingMode` (live|paper), `AcceptNonBrokerageAccountWarning`, `SecondFactorDevice`, `ReloginAfterSecondFactorAuthenticationTimeout`, `SecondFactorAuthenticationTimeout`, `OverrideTwsApiPort`, `ReadOnlyApi`, `AutoRestartTime`, `ColdRestartTime`, `ExistingSessionDetectedAction`, `AcceptIncomingConnectionAction`, `CommandServerPort`. `gatewaystart.sh` variables: `TWS_MAJOR_VRSN`, `IBC_INI`, `TRADING_MODE`, `TWOFA_TIMEOUT_ACTION`, `IBC_PATH`, `TWS_PATH`, `TWS_SETTINGS_PATH`, `LOG_PATH`, `TWSUSERID`, `TWSPASSWORD`, `JAVA_PATH`. The script's comments advise against putting credentials in it.
- *Paper 2FA:* not established. IBKR says 2FA is required for all users. No official page found says whether a paper username prompts for 2FA. [unverified]

**Quotes.**
- "With either application (TWS or IBGW), the user must manually enter their username and password into a login window. For security reasons, a headless session of TWS or IBGW without a GUI is not supported." / "Both TWS and IBGW were designed to be restarted daily. ... Beginning in version 974+ both applications offer an autorestart feature that allows the application to restart daily without user intervention. With this option enabled, TWS or IBGW can potentially run from Sunday to Sunday without re-authenticating. After the nightly server reset on Saturday night it will be necessary to again enter security credentials." (tws_architecture_the-trader-workstation_the-ib-gateway.html, row 26, 08:38:53Z; https://www.interactivebrokers.com/docs/tws-api/doc/architecture/the-trader-workstation/the-ib-gateway)
- "This procedure will require manual authentication once a week, the first time you log into the platform after the security tokens have been invalidated. This security process occurs each Sunday at 1:00 am ET." (ibkrguides_tws_auto_restart_considerations.html, row 89, 08:51:41Z; https://www.ibkrguides.com/traderworkstation/auto-restart-considerations.htm)
- "The weekly authentication cycle starts on every Monday. If you receive Login failed = Soft token=0 received instead of expected permanent for zdc1.ibllc.com:4001 (SSL), this means you need to manually login again to complete the weekly reauthentication task." and "For API users, it is recommended to choose “Never lock Trader Workstation” and “Auto restart”." (tws_tws-settings_daily-weekly-reauthentication.html, row 21, 08:38:21Z; https://www.interactivebrokers.com/docs/tws-api/doc/tws-settings/daily-weekly-reauthentication)
- "“Socket Port”- By default, TWS uses socket port 7496 for live sessions and 7497 for paper sessions. IB Gateway by contrast uses 4001 for live sessions and 4002 for paper sessions. However these are just defaults, and can be modified as desired" and "The setting ‘Read-Only’ is enabled by default and will block all API orders. It must be unchecked to allow any orders from the API." (campus_installing-configuring-tws-for-the-api.html, row 90, 08:52:02Z; https://www.interactivebrokers.com/campus/trading-lessons/installing-configuring-tws-for-the-api/)
- Download page: "Version (Stable) A stable IB Gateway version with less frequent updates. It does not update automatically." Linux links: `https://download2.interactivebrokers.com/installers/ibgateway/stable-standalone/ibgateway-stable-standalone-linux-x64.sh` (ibkr_ibgateway_stable.html, row 92, 08:52:18Z; https://www.interactivebrokers.com/en/trading/ibgateway-stable.php)
- IBC: "allows TWS or Gateway to automatically restart each day without need for repeated authentication: authentication is only required the first time during the week that TWS or Gateway run after 01:00 ET on Sunday" ; "you MUST download the OFFLINE version of TWS, not the self-updating version: IBC DOES NOT WORK with the self-updating version" ; "On Linux, you'll need to install xterm" ; "It is safest to use the 'stable' offline version of TWS rather than the 'latest' version for live trading" ; "every time you login to TWS or Gateway (including when IBC does it for you) you'll receive an alert on your device ... Note that IBC cannot itself assist in the process" (ibc_userguide.md, row 83, 08:50:45Z; https://raw.githubusercontent.com/IbcAlpha/IBC/master/userguide.md)
- "This project has been retired, as of 1 September 2026. ... there will be no further development of IBC, other than completing work in progress at that date and fixing any significant newly reported bugs." (ibc_README.md, row 86, 08:50:54Z). Latest release: page title "Release 3.24.2 · IbcAlpha/IBC", datetime "2026-08-21T23:43:59Z" (github_ibc_releases_latest.html, row 93, 08:52:45Z; https://github.com/IbcAlpha/IBC/releases/latest)
- config.ini: "# Your TWS username: IbLoginId=edemo # Your TWS password: IbPassword=demouser" ; "The allowed values are 'live' (the default) and 'paper'. ... If it is set to 'paper', then either the live or the paper-trading credentials may be supplied." ; "Logging in to a paper-trading account results in TWS displaying a dialog asking the user to confirm that they are aware that this is not a brokerage account. Until this dialog has been accepted, TWS will not allow API connections to succeed." ; "IBC can be configured with a Cold Restart Time, which is a time (specified in your local timezone) that is after 01:00 US/Eastern. When this time is reached on Sundays, IBC tidily closes TWS, and the script then reloads IBC ... For a live account, the time chosen should be convenient for you to handle 2FA alerts." (ibc_config_ini.txt, row 87, 08:51:02Z; https://raw.githubusercontent.com/IbcAlpha/IBC/master/resources/config.ini). Quirk: the comment says AcceptNonBrokerageAccountWarning "Setting this to 'yes' (the default)" while the shipped value is `AcceptNonBrokerageAccountWarning=no`. The adapter should set it explicitly.
- gatewaystart.sh: "If your IBKR user id and password are not included in your IBC configuration file, you can set them here. However you are strongly advised not to set them here because this file is not normally in a protected location." Defaults: `TWS_MAJOR_VRSN=1045`, `IBC_INI=~/ibc/config.ini`, `TWOFA_TIMEOUT_ACTION=exit`, `IBC_PATH=/opt/ibc`, `TWS_PATH=~/Jts`. (ibc_gatewaystart_sh.txt, row 88, 08:51:04Z)
- "Two Factor Authentication (2FA) is required for all users at Interactive Brokers." Supported: "IB Key ... SMS / Text Messages ... Digital Security Card+ (DSC+)". (tws_notes-limitations_supported-two-factor-authentication-2-fa.html, row 23, 08:38:34Z)

**Confidence:** high for install, ports, restart and IBC facts. Medium for the weekly re-authentication day (official pages conflict; the Sunday 01:00 ET version is the most specific and IBC agrees with it). Paper 2FA [unverified].

---

## I2. Paper account requirements, free trial, market-data sharing

**Answer.**
- A paper account comes with an approved live account: "New individual account holders automatically receive a paper trading account." Pages differ on whether the live account must be *funded* or only *approved*. The TWS API requirements page lists "A funded and opened IBKR Pro account".
- Paper starts with USD 1,000,000 of equity with loan value. It can be reset to up to 5× the production account's value.
- A separate **Free Trial** account exists. Per IBKR's third-party FAQ, the API can connect to a trial account, but trial logins get no real-time data and no historical candlesticks "for most instruments". A trial is therefore useless for our daily-bar adapter.
- Market data: the paper user has no subscriptions of its own. It can *share* the live user's subscriptions (one paper per live). Real and paper sessions must then run on the same device, or the paper session gets no data. Without sharing, the paper user gets delayed data "as available". Market data needs a funded IBKR Pro account; "Demo accounts cannot subscribe to data".

**Quotes.**
- "New individual account holders automatically receive a paper trading account." / "Trading permissions, market data subscriptions, base currency, and other account configurations are the same as specified for your regular account." / "All paper trading accounts start with USD 1,000,000 of paper trading Equity with Loan Value" / "You may reset your paper cash equity at any time in Client Portal to up to five times your production account's value." / "Only Free Trial accounts can be upgraded from paper to full-access." / "Fills are simulated from the top of the book; no deep book access." / "Stops and other complex order types are always simulated in paper trading" (ibkrguides_cp_aboutpaper.html, row 60, 08:46:57Z; https://www.ibkrguides.com/clientportal/aboutpapertradingaccounts.htm)
- "To open a new paper trading account, log in to your live account ... Accounts are created within 24 hours under normal business circumstances." (ibkrguides_cp_paperaccount.html, row 61, 08:47:08Z; https://www.ibkrguides.com/clientportal/papertradingaccount.htm)
- "IBKR only allows access to its paper trading account after opening an actual, funded account." and, two lines later, "Now, you don’t need to fund your live account straight away, but it must be approved before paper trading is made available." (campus_how-to-open-an-ibkr-paper-trading-account.html, row 63, 08:47:31Z; https://www.interactivebrokers.com/campus/trading-lessons/how-to-open-an-ibkr-paper-trading-account/)
- "If your regular trading account has been approved and funded, you can use your Account Management page to open a Paper Trading Account" (tws_notes-limitations_tws-api-limitations.html, row 24, 08:38:40Z). "A funded and opened IBKR Pro account" (tws_notes-limitations_requirements.html, row 25, 08:38:46Z)
- "While there is no set time limit for use of the free trial account, its purpose is to offer prospective clients the ability to operate the trading system in a simulated environment before making any commitment to open and fund a live account." (IBKR staff reply, campus_request-paper-trading-account.html, row 62, 08:47:26Z)
- "Can the TWS API be used with trial accounts? Yes it is possible to connect an API application to a trial account. However it is not possible to receive real time market data or historical candlesticks for most instruments from the TWS API with a trial account login." and "In order to use third-party platforms, you will need to have a funded IBKR PRO account." (tpi_general_faq.md, row 65, 08:48:00Z; https://www.interactivebrokers.com/docs/third-party-integrations/general-third-party-frequently-asked-questions.md)
- "Market data may also be shared between a live and paper username so that both can retrieve data using the same market data subscription. Each Live user can share data with one (1) Paper account" (gen_mds_market-data-users_market-data-sharing.md, row 46, 08:43:26Z)
- "The paper user, by design, does not have a set of market data subscription on its own but can be configured ... The paper user can be set to share the live market data subscriptions of the real user: In this scenario, if the real and paper trading sessions are running simultaneously, they must reside on the same device in order for the paper to receive live market data. ... The paper user can be set NOT to share ... the paper user will receive delayed data, as available." (ibkrguides_kb1719_rendered2.html, row 58, 08:46:10Z; https://www.ibkrguides.com/kb/article-1719.htm)
- "1. Opened IB Account (Demo accounts cannot subscribe to data). 2. Must use an IBKR PRO account type 3. Clients should have \$500 USD in their account in addition to the cost of all market data subscriptions." (gen_mds_market-data-requirements.md, row 43, 08:42:52Z)
- Error 10197: "Indicates that the user is logged into the paper account and live account simultaneously trying to request live market data using both the accounts. In such a scenario preference would be given to the live account" (tws_error-handling_error-codes.html, row 18, 08:38:03Z)

**Confidence:** high on sharing, the starting balance and the trial-account limits. Medium on "funded vs approved": official pages disagree. The API requirements page says funded, which is the safe assumption.

---

## I3. Delayed market data in paper and via the API

**Answer.** `reqMarketDataType(3)` gives delayed streaming data and `reqMarketDataType(4)` gives delayed-frozen data. Delayed ticks arrive on tick IDs 66 to 76, and Delayed Close (75) is "The prior day’s closing price". IBKR's delay table lists CME, CBOT, COMEX and NYMEX at **10 minutes**. The generic page says "15 – 20 minutes", and the legacy page says "10-15 minute". Delayed data is free. The legacy docs say delayed data covers only streaming quotes, not historical bars (see I4). A non-sharing paper user gets delayed data "as available" (I2).

**Quotes.**
- "Delayed 3 Free, delayed data is 15 – 20 minutes delayed. Delayed market data is returned with delayed Tick Types (Tick ID 66~76)." / "Delayed Frozen 4 Requests delayed “frozen” data for a user without market data subscriptions. If requested during the trading session, the previous days data will be returned. Data for the current day’s trading session is not avialable until 15 minutes after market close." / "The most recent data available with the user’s subscriptions will be returned regardless of the requested market data type." (tws_md_delayed-data.html, row 14, 08:37:41Z; https://www.interactivebrokers.com/docs/tws-api/doc/md/delayed-data)
- Delay table rows: "CBOT | CBOT | 10 minutes | CBOT Real-Time", "CME | CME | 10 minutes | CME Real-Time", "COMEX | COMEX | 10 minutes | COMEX Real-Time", "NYMEX | NYMEX | 10 minutes | NYMEX Real-Time", under "Delayed market data is on a time lag that is usually 10-20 minutes behind real-time quotes." (ibkr_market_data_pricing.html, row 55, 08:44:26Z; https://www.interactivebrokers.com/en/pricing/market-data-pricing.php)
- "74 Delayed Close The prior day’s closing price. *RDD" ; "*RDD: These tick types are provided only when the user makes a request to EClient.reqMarketDataType(3) prior to their market data request." ; "Unless requesting Delayed Watchlist Data, a paid data subscription is required to receive market data through the API." (tws_md_streaming-data.html row 16, 08:37:51Z; tws_md_introduction.html row 17, 08:37:57Z). Note: the current page prints the ID column one row off, so "74" sits next to "Delayed Close"; the legacy tick-type table gives "Delayed Close 75 The prior day's closing price." (legacy_tick_types.html, row 71, 08:48:21Z)
- "10-15 minute delayed streaming data is available for many types of instruments without market data subscriptions. ... It is important to note that historical data still requires market data subscriptions" (legacy_delayed_data.html, row 69, 08:48:16Z)

**Confidence:** high that delayed streaming exists and that the CME-group delay is 10 minutes. High that the API returns delayed ticks.

---

## I4. Historical daily bars of CME futures without a subscription; error codes

**Answer.** **Not allowed** per IBKR's docs. API historical bars need the same Level 1 subscription as live data. The legacy docs say delayed historical bars are not served through the API, even though TWS can draw delayed charts. No current official page offers a "delayed historical data" path. The error codes 162 and 354 are documented. **10167 and 10168 appear on neither the current nor the legacy official error list.** 10186 and 10187 are listed. ib_async treats 10167 as a warning and comments "10167 ? not listed".

**Quotes.**
- "1. Level 1 market data subscriptions provide: live watchlist data, tick-by-tick data, historical bar data, historical tick data." (gen_mds_understanding-market-data-subscriptions.md, row 51, 08:43:51Z)
- "most\* securities require a Level 1, top of book, market data subscription to receive market data. This is required for all users at Interactive Brokers retrieving market data through the API." (gen_mds_introduction.md, row 42, 08:42:47Z)
- "Receiving historical data from the API has the same market data subscription requirement as receiving streaming top-of-book live data ... Unlike TWS, which can create 'delayed charts' for most instruments without any market data subscriptions that have data up until 10-15 minutes prior to the current moment; the API always requires Level 1 streaming real time data to return historical data." (legacy_historical_data.html, row 73, 08:48:26Z; https://interactivebrokers.github.io/tws-api/historical_data.html)
- Error codes (tws_error-handling_error-codes.html, row 18, 08:38:03Z; https://www.interactivebrokers.com/docs/tws-api/doc/error-handling/error-codes):
  - "162 Historical market data Service error message."
  - "166 HMDS Expired Contract Violation. Historical data is not available for the specified expired contract."
  - "200 No security definition has been found for the request."
  - "354 Requested market data is not subscribed. Check API status by selecting the Account menu then under Management choose Market Data Subscription Manager and/or availability of delayed data."
  - "10089 API data requires subscription"
  - "10186 Requested market data is not subscribed. Delayed market data is not enabled"
  - "10187 Failed to request historical ticks:No market data permissions"
  - "2104 Market data farm connection is OK", "2106 A historical data farm is connected." (notifications, not errors)
- Legacy list: "354 Not subscribed to requested market data." (legacy_message_codes.html, row 70, 08:48:19Z). It has no 10167 or 10168 entry. Its 10xxx list goes 10027, 10090, 10148, 10186, 10197 ...
- ib_async: "# 10167 ? not listed" and `warningCodes = frozenset({105, 110, 165, 321, 329, 399, 404, 434, 492, 10167})` (ibasync_wrapper_py.txt, row 99, 08:53:55Z, main branch)
- Texts often attributed to 10167 ("Displaying delayed market data") and 10168 ("Delayed market data is not enabled"): [unverified]. Neither appears on an official page I saved.

**Confidence:** high that a subscription is required. The current official wording is general ("Level 1 ... provide ... historical bar data"), and the legacy page says it explicitly.

---

## I5. Expired futures, how far back, pacing

**Answer.** Set `includeExpired=True` on the Contract. History for expired futures is kept for **2 years after expiry**. Older expired contracts are unavailable on every platform. Pacing limits: the "hard" small-bar rules (no identical request within 15 s; no 6 or more requests for the same contract, exchange and tick type within 2 s; no more than 60 requests in 10 minutes) apply to bars of 30 s or less. The legacy docs say the hard limits for bars of 1 minute and larger were lifted, with a "soft" throttle still in place. The legacy docs cap open historical requests at 50. General API rate: (market data lines ÷ 2) requests per second, which is 50/s by default.

**Quotes.**
- "TWS API users can refer to expired Futures contracts by including the ["IncludeExpired"] field. This will permit users to review historical market data for contracts that have expired within the last 2 years." (tws_contracts_futures.md, row 37, 08:42:02Z; https://www.interactivebrokers.com/docs/tws-api/contracts/futures.md)
- "Expired futures data older than two years counting from the future’s expiration date." and "Pacing Violations for Small Bars (30 secs or less) ... Making identical historical data requests within 15 seconds. Making six or more historical data requests for the same Contract, Exchange and Tick Type within two seconds. Making more than 60 requests within any ten minute period. BID_ASK historical data is counted twice." and "As historical data at IB gets adjusted, compressed and filtered by default, there may be historical data differences if you request historical data at different time points." (tws_md_introduction.html, row 17, 08:37:57Z; https://www.interactivebrokers.com/docs/tws-api/doc/md/introduction)
- "The maximum number of simultaneous open historical data requests from the API is 50." and footnote: "At this time Historical Data Limitations for barSize = "1 mins" and greater have been lifted. However, please use caution ... we still implement a "soft" slow to load-balance client requests vs. server response. Requesting too much historical data can lead to throttling and eventual disconnect of the API client." (legacy_historical_limitations.html, row 66, 08:48:08Z)
- "The maximum number of API requests that can be submitted are equivalent to your Maximum Market Data Lines divided by 2, per second. By default, all users maintain 100 market data lines. Therefore, users have a pacing limitation of (100/2)= 50 requests per second." (tws_pacing-limitations_introduction.html, row 19, 08:38:10Z). "If the pacing limits are broken 3 times, the API session will terminate" (with the reject setting on; otherwise TWS paces requests itself) (tws_pacing-limitations_pacing-behavior.html, row 20, 08:38:16Z)
- Daily bars: the max-duration table gives "1 day" bars a max duration in years (Y). The current page's table cells did not come through as text, so the exact limit is [unverified].
- Continuous futures (`CONTFUT`): "This security type can only be used in the TWS API to request historical data" and "endDateTime must be left as an empty string" (tws_contracts_futures.md, row 37)

**Confidence:** high for the 2-year rule and small-bar pacing. Medium for "1 min+ hard limits lifted" (legacy only).

---

## I6. THE KEY QUESTION: is the daily bar close the CME settlement or the last trade? Date convention and time zone

**Answer.**
- **Current docs:** the close of the TRADES daily bar is "Last traded price", and the close of a MIDPOINT bar is "Last midpoint price". ADJUSTED_LAST does not support futures ("Supported Products: ETFs, Options, Stocks"). No whatToShow value for settlement exists. The current pages never mention a settlement price for daily bars.
- **Legacy docs (deprecated, IBKR's own text):** "For futures, the close price of daily bars **can be** the settlement price if provided by the exchange", and the settlement may arrive hours after the close (Friday's sometimes on Saturday).
- So the close is **sometimes** the settlement, depending on timing and the exchange feed. It is not guaranteed. A bar fetched soon after the session can carry the last trade, and a refetch later can carry the settlement. IBKR also says its historical data "gets adjusted, compressed and filtered", so values can change between requests.
- **Settlement field:** no documented API field or tick type carries the official settlement price. Streaming tick 9 "Close Price" is "The last available closing price for the previous day", and delayed tick 75 is "The prior day’s closing price". Neither page says "settlement" for futures. "Settlement Type" in Contract Details (TWS 10.49.01+) is the settlement *method* field, not a price. The TWS Futures Term Structure window plots "settlement prices" but labels its historical series "Close Price". That suggests IBKR's futures "close" is settlement-based, but it is a GUI page, not the API.
- **Date convention:** "A daily bar will refer to a trading session which may cross calendar days. In that case the date of the bar will correspond to the day on which the bar closes." (legacy). So a CME Globex bar that opens Sunday 17:00 CT is dated Monday, which is the session (trade) date. Daily bars come only as `yyyyMMdd`, and ib_async parses an 8-character date into `datetime.date`. For intraday bars, formatDate=2 gives UTC-aware datetimes. Times otherwise follow the TWS login time zone, or the Global Configuration setting (operator, instrument or UTC). CME's exchange time zone is "US/Central", per `ContractDetails.timeZoneId`.

**Quotes.**
- TRADES: "Bar Values: Open High Low Close Volume First traded price Highest traded price Lowest traded price Last traded price Total traded volume Supported Products: Bonds, ETFs, FOPs, Futures, Indices, Metals, Options, SSFs, Stocks, Structured Products, Warrants TRADES data is adjusted for splits, but not dividends." MIDPOINT: "... Last midpoint price ... Supported Products: ... Futures ...". ADJUSTED_LAST: "Supported Products: ETFs, Options, Stocks ADJUSTED_LAST data is adjusted for splits and dividends." SCHEDULE: "SCHEDULE data returns only on 1 day bars but returns historical trading schedule only with no information about OHLCV." (tws_md_historical_bars.html, row 13, 08:37:35Z; https://www.interactivebrokers.com/docs/tws-api/doc/md/historical-bars). A grep for "settle" in this page and in its .md version (row 77) finds nothing.
- "The daily bar size has several unique characteristics. This is true both in TWS and the API: For futures, the close price of daily bars can be the settlement price if provided by the exchange. Generally the official settlement price is not available until several hours after a trading session closes. The Friday settlement price will sometimes not be available until Saturday. A daily bar will refer to a trading session which may cross calendar days. In that case the date of the bar will correspond to the day on which the bar closes." (legacy_historical_bars.html, row 67, 08:48:11Z; https://interactivebrokers.github.io/tws-api/historical_bars.html)
- "formatDate bool The format in which the incoming bars’ date should be presented. Note that for day bars, only yyyyMMdd format is available." / "The OHLC historical data Bar. The time zone of the bar is the time zone chosen on the TWS login screen." (tws_md_historical_bars.html, row 13)
- "operator timezone ... instrument timezone: refers to the timezone of the requested exchange. ... UTC format: ... YYYYMMDD-hh:mm:ss" / "the CME operates on “US/Central”. This values can be programmatically requested using the EClient.reqContractDetails method, and then received from EWrapper.contractDetails in contractDetails.Time ZoneId." (tws_tws-settings_historical-date-format.html, row 22, 08:38:28Z)
- "Close Price ”The last available closing price for the previous day. For US Equities we use corporate action processing to get the closing price so the close price is adjusted to reflect forward and reverse splits and cash and stock dividends.”" (tws_md_streaming-data.html, row 16)
- "While operating with Trader Workstation or IB Gateway 10.49.01 or greater, Settlement Type will be included in Contract Details." (tws_changelog.md, row 105, 08:55:29Z)
- "This window displays a split chart that shows the real-time and historical settlement prices of the existing futures contracts" / "By default we display "Last Price" for Today and "Close Price" for historical dates." (ibkrguides_tws_futures_term_structure.html, row 78, 08:50:03Z)
- ib_async `parseIBDatetime`: "if len(s) == 8: # YYYYmmdd ... t = dt.date(y, m, d)" (ibasync_util_py.txt, row 100, 08:54:02Z). ib_async reqHistoricalData: "formatDate (int) – For an intraday request setting to 2 will cause the returned date fields to be timezone-aware datetime.datetime with UTC timezone" (ibasync_api.html, row 94, 08:53:04Z)

**Confidence:** medium. The only direct statement is legacy and says "can be". The current docs define TRADES close as the last traded price. **Treat IBKR daily closes as not reliably the settlement.** The date convention (close-day = session date) is also legacy-only: medium.

---

## I7. Contract definitions for the 12 micros

**Answer.** All 12 appear in IBKR's US futures margin table, so IBKR lists them. Exchange (IB code), underlying symbol and trading class:

| Product | IB exchange | Underlying (IB symbol) | Trading class | Margin-table description | Options at IB |
|---|---|---|---|---|---|
| MNQ | CME | MNQ | MNQ | MICRO E-MINI NASDAQ-100 INDEX | Yes |
| M2K | CME | M2K | M2K | MICRO E-MINI RUSSELL 2000 INDEX | No |
| M6E | CME | M6E | M6E | EUROPEAN MONETARY UNION EURO | No |
| MGC | COMEX | MGC | MGC | E-MICRO GOLD | Yes |
| MCL | NYMEX | MCL | MCL | MICRO WTI CRUDE OIL | Yes |
| MNG | NYMEX | **MHNG** | **MNG** | MICRO HENRY HUB NATURAL GAS | No |
| 2YY | CBOT | 2YY | 2YY | 2 YEAR MICRO TREASURY YIELD | No |
| 10Y | CBOT | 10Y | 10Y | 10 YEAR MICRO TREASURY YIELD | No |
| 30Y | CBOT | 30Y | 30Y | 30 YEAR MICRO TREASURY YIELD | No |
| MZC | CBOT | MZC | MZC | MICRO CORN FUTURES | No |
| MZS | CBOT | MZS | MZS | MICRO SOYBEAN FUTURES | No |
| MZL | CBOT | MZL | MZL | MICRO SOYBEAN OIL FUTURES | No |

- **Quirk: Micro Henry Hub has IB symbol `MHNG` and trading class `MNG`.** Contract(symbol="MNG") will likely fail to resolve. Use symbol MHNG, or tradingClass MNG.
- Yield micros are "priced in yield" and cash-settled. The price is a yield, not a bond price.
- **Multiplier and localSymbol format:** not on any IBKR page fetched. [unverified] The adapter must read `multiplier`, `localSymbol`, `lastTradeDateOrContractMonth` and `realExpirationDate` from `reqContractDetails` / `qualifyContracts` at runtime, never hard-code them. The legacy docs define localSymbol as "IB's symbol for the future itself"; their only example is EUREX ("FGBL MAR 23").
- `lastTradeDateOrContractMonth` takes "YYYYMM" (contract month) or a full date. Example: `contract.lastTradeDateOrContractMonth = "202809"`. Futures need Symbol, SecType, Exchange, Currency, LastTradeDateOrContractMonth, Multiplier and TradingClass "generally".
- Margins in the table (USD; overnight initial / maintenance), for information only, as fetched: MNQ 5774.03/4420.85, M2K 1245.45/1083.00, M6E 448.961/352.358, MGC 3982.78/3233.72, MCL 1741.46/1393.17, MNG 755.147/656.649, 2YY 1200.95/1044.31, 10Y 665.802/578.951, 30Y 896.299/779.39, MZC 190.145/165.343, MZS 421.981/366.94, MZL 491.623/427.499.

**Quotes.**
- Header "Exchange | Underlying | Product description | Trading Class | Intraday Initial | Intraday Maintenance | Overnight Initial | Overnight Maintenance | Currency | Has Options | Short Overnight Initial | Short Overnight Maintenance". Rows, for example: "NYMEX | MHNG | MICRO HENRY HUB NATURAL GAS | MNG | 755.147 | N/A | 755.147 | 656.649 | USD | No"; "CBOT | 10Y | 10 YEAR MICRO TREASURY YIELD | 10Y | 665.802 ..."; "CBOT | MZC | MICRO CORN FUTURES | MZC | 190.145 ..." (ibkr_margin_futures_fops_us.html, row 104, 08:54:53Z; https://investors.interactivebrokers.com/en/trading/margin-futures-fops.php?hm=us&ex=us&rgt=0&rsk=1&pm=0&rst=101004100808080101). Rows were pulled from the raw HTML table with a short parser. The `.txt` copy holds the same cells, one per line.
- "Yield futures are cash-settled, priced in yield and linked to a specific on-the-run security." / "5-Year Yield futures An intuitive way to obtain 5-year Treasury exposure. Contracts are priced in yield with a constant BPV for easier spread trading across Yield future tenors." (ibkr_micro_futures_comparison.html, row 103, 08:54:49Z; https://www.interactivebrokers.com/en/trading/micro-futures-comparison.php)
- "Futures contracts may be generally defined with `Symbol`, `SecType`, `Exchange`, `Currency`, `LastTradeDateOrContractMonth`, `Multiplier`, and `TradingClass`." with the example `contract.exchange = "CME"` and `contract.lastTradeDateOrContractMonth = "202809"` (tws_contracts_futures.md, row 37)
- "By contract the 'local symbol' field is IB's symbol for the future itself (the Symbol within the TWS' Contract Description dialog). Since a local symbol uniquely defines a future, an expiry is not necessary." and "Occasionally, you can expect to have more than a single future contract for the same underlying with the same expiry. To rule out the ambiguity, the contract's multiplier can be given" (legacy_basic_contracts.html, row 72, 08:48:24Z)

**Confidence:** high for exchange, symbol, trading class and availability (one official table). Multiplier and localSymbol format [unverified].

---

## I8. Cheapest CME-group market data and the funded-account rule

**Answer (non-professional).**
- **Option A: four L1 feeds.** "CME Real-Time (L1)", "CBOT Real-Time (L1)", "COMEX Real-Time (L1)" and "NYMEX Real-Time (L1)" cost **USD 1.55/month each** for non-pros (Pro: N/A). That is **USD 6.20/month for all four**. Footnote 14: each fee is waived when commissions exceed USD 20.
- **Option B: the bundle.** "US Securities Snapshot and Futures Value Bundle" costs **USD 10.00/month base** plus USD 0.01 per snapshot. It "Includes top of book quotes for CBOT, CME, COMEX, and NYMEX". The waiver table says the fee is waived at USD 30 in commissions. Not available to IBKR Lite. Footnote four on the same bundle reads "Accounts must generate at least USD 30 in commissions per month per each user subscribed", which reads as a requirement. The page is ambiguous: it may only mean the waiver.
- On price alone, Option A is cheapest (USD 6.20 vs USD 10.00). The page does not say whether the single-exchange L1 rows are sold without the bundle. Pros pay USD 145.00/month per exchange (L1+L2).
- All accounts: US futures data "requires clients to have US Futures Trading Permissions". Subscriptions are not pro-rated and are billed per calendar month. By default every user is classified *Professional* until they update their status.
- **Funded-account rule:** USD 500 minimum equity, plus the cost of the subscriptions. Funded status takes effect the next business day. Data is terminated after a violator notice if equity falls below USD 500. Account must be IBKR Pro. Market Data API access must be enabled in Client Portal.

**Quotes** (ibkr_market_data_pricing.html, row 55, 08:44:26Z; https://www.interactivebrokers.com/en/pricing/market-data-pricing.php; rows read from the raw HTML `tr class="mdata non-pro|pro"`):
- Header "Market Data Package | Country | Non-Pro Fees/month | Pro Fees/month"
- "US Securities Snapshot and Futures Value Bundle 1, 2, 3, 4, 23, 24, 31 | United States | USD 10.00 Base Waived for Activity + USD 0.01 per Snapshot"
- "CME Real-Time (L1) 14 | United States | USD 1.55 | N/A" (same for CBOT, COMEX, NYMEX); "CME Real-Time (L2) 3, 14 | USD 12.10" (non-pro); "CME Real-Time (L1, L2) 3, 14 | USD 145.00" (pro row)
- "US Futures Value Bundle PLUS 5, 31 | United States | USD 5.00 | N/A". Footnote five: "Requires a subscription to the US Securities Snapshot and Futures Value Bundle. Includes depth of book quotes for CBOT, CME, COMEX, and NYMEX."
- Footnotes: two "Includes top of book quotes for CBOT, CME, COMEX, and NYMEX"; three "Access to US Futures data requires clients to have US Futures Trading Permissions."; four "Accounts must generate at least USD 30 in commissions per month per each user subscribed."; fourteen "Fee is waived if commissions generated are greater than USD 20.00"; thirty-one "Service not available for IBKR Lite Clients."
- Waiver table: "US Securities Snapshot and Futures Value Bundle | USD 10.00 | USD 30.00" (Subscription | Fee | Commissions Waiver)
- "Clients should have \$500 USD in their account in addition to the cost of all market data subscriptions." / "Please be sure to enable Market Data API access through the Client Portal Market Data Subscriptions Page." (gen_mds_market-data-requirements.md, row 43)
- "Individual Accounts (unless listed below) | USD 500.00 (or non-USD equivalent)" / "the funded status for a given account will not take effect until the next business day" / "Market Data services will be terminated once clients receive Market Data Violator notice provided the equity falls below USD 500.00" (gen_mds_market-data-subscription-minimum-equity-balance-requirements.md, row 44, 08:42:58Z)
- "US Securities Snapshot and Futures Value Bundle | Provides L1 data for US Futures. | ES" (gen_mds_popular-market-data-subscriptions_introduction.md, row 52, 08:43:56Z)
- "By default, all users are classified as Professional Market Data users." (gen_mds_professional-vs-non-professional.md, row 53, 08:44:02Z)
- "Market data subscriptions are paid once, every calendar month. Market data subscriptions are **not** pro-rated." (gen_mds_market-data-costs-and-fees.md, row 50, 08:43:47Z)

**Confidence:** high for prices and minimum equity as published today. Medium on whether the USD 1.55 L1 rows can be bought without the USD 10 bundle (not stated).

---

## I9. ib_async (2.1.0)

**Answer.** The docs site is built for "Release 2.1.0." Changelog: "Version 2.1.0 (2025-12-06)". Python 3.10 or later.
- `IB.connect(host='127.0.0.1', port=7497, clientId=1, timeout=4, readonly=False, account='', raiseSyncErrors=False, fetchFields=...)` is blocking, and clientId must be unique per connection. `IB.disconnect()`. `isConnected()`.
- `reqHistoricalData(contract, endDateTime, durationStr, barSizeSetting, whatToShow, useRTH, formatDate=1, keepUpToDate=False, chartOptions=[], timeout=60)` returns `BarDataList` and is blocking. timeout cancels the request and returns an empty series. `reqHistoricalSchedule(contract, numDays, endDateTime='', useRTH=True)`. `reqHeadTimeStamp(contract, whatToShow, useRTH, formatDate=1)`. `reqMarketDataType(marketDataType)`.
- `qualifyContracts(*contracts)` qualifies in place and returns the successfully qualified list. `reqContractDetails(contract)` returns `list[ContractDetails]`: empty means unknown, more than one means ambiguous.
- Contract classes: `Future(symbol='', lastTradeDateOrContractMonth='', exchange='', localSymbol='', multiplier='', currency='', **kwargs)` and `ContFuture(...)`.
- Events: `connectedEvent()`, `disconnectedEvent()`, `errorEvent(reqId, errorCode, errorString, contract)`, `timeoutEvent(idlePeriod)`, `newOrderEvent(trade)`, `orderStatusEvent(trade)`, `execDetailsEvent(trade, fill)`, `commissionReportEvent(trade, fill, report)`, `positionEvent`, `accountValueEvent`.
- Orders: `placeOrder(contract, order)` returns a live-updated `Trade`. `cancelOrder(order, manualCancelOrderTime='')`. `whatIfOrder(contract, order)` returns `OrderState` (margin and commission without placing).
- Objects: `Trade(contract, order, orderStatus, fills, log, advancedError)`; `OrderStatus(orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice)`; `Fill(contract, execution, commissionReport, time)`; `Execution(execId, time, acctNumber, exchange, side, shares, price, permId, clientId, orderId, liquidation, cumQty, avgPrice, ...)`; `CommissionReport(execId, commission, currency, realizedPNL, yield_, yieldRedemptionDate)`; `BarData(date, open, high, low, close, volume, average, barCount)`.
- Reconnect: no automatic reconnect in `IB`. `ibcontroller.Watchdog(controller, ib, host, port=7497, clientId=1, connectTimeout=2, appStartupTime=30, appTimeout=20, retryDelay=2, ..., probeContract=Forex('EURUSD', ...), probeTimeout=4)` restarts the app through `ibcontroller.IBC(twsVersion, gateway, tradingMode, twsPath, ..., userid, password, ..., on2fatimeout)` and reconnects. It also restarts on errors 1100 and 100.

**Quotes** (ibasync_api.html, row 94, 08:53:04Z; https://ib-api-reloaded.github.io/ib_async/api.html; changelog row 95, 08:53:08Z):
- "connect(host='127.0.0.1', port=7497, clientId=1, timeout=4, readonly=False, account='', raiseSyncErrors=False, fetchFields=<StartupFetch.POSITIONS|ORDERS_OPEN|ORDERS_COMPLETE|ACCOUNT_UPDATES|SUB_ACCOUNT_UPDATES|EXECUTIONS: 63>)" / "clientId (int) – ID number to use for this client; must be unique per connection. Setting clientId=0 will automatically merge manual TWS trading with this client."
- "reqHistoricalData(contract, endDateTime, durationStr, barSizeSetting, whatToShow, useRTH, formatDate=1, keepUpToDate=False, chartOptions=[], timeout=60)" / "endDateTime ... If no timezone is given then the TWS login timezone is used." / "timeout (float) – Timeout in seconds after which to cancel the request and return an empty bar series."
- "qualifyContracts(*contracts) Fully qualify the given contracts in-place. This will fill in the missing fields in the contract, especially the conId. Returns a list of contracts that have been successfully qualified."
- "reqContractDetails(contract) Get a list of contract details that match the given contract. If the returned list is empty then the contract is not known; If the list has multiple values then the contract is ambiguous."
- "placeOrder(contract, order) Place a new order or modify an existing order. Returns a Trade that is kept live updated with status changes, fills, etc."
- "disconnectedEvent (): Is emitted after disconnecting from TWS/gateway." / "execDetailsEvent (trade: Trade, fill: Fill): Emits the fill together with the ongoing trade it belongs to." / "commissionReportEvent (trade: Trade, fill: Fill, report: CommissionReport): The commission report is emitted after the fill that it belongs to."
- Watchdog: "Start, connect and watch over the TWS or gateway app and try to keep it up and running. ... Restarting will also occur directly on errors 1100 and 100." Example: "ibc = IBC(974, gateway=True, tradingMode='paper') ... watchdog = Watchdog(ibc, ib, port=4002)"
- "Version 2.1.0 (2025-12-06)" (changelog); "Python 3.10 or higher" (ibasync_README.md, row 97)

**Confidence:** high (from the 2.1.0 docs build). The source-level details (wrapper.py, util.py) come from the `main` branch, not the 2.1.0 tag: medium.

---

## What this means for the adapter

1. **Settlement close is not guaranteed.** The current docs define the TRADES daily close as the last traded price. The legacy docs say it "can be" the settlement, sometimes not until hours later or Saturday. If the strategy needs CME settlements (as Databento's `statistics` settlement does), the adapter should (a) fetch daily bars well after settlement time and refetch the previous N days on every run, (b) compare IBKR closes against the Databento settlements we already hold for the overlap period before trusting them, and (c) never use ADJUSTED_LAST, which does not support futures. Whether to run that comparison is the lead's call.
2. **No free path to daily bars.** Historical bars need a Level 1 subscription. Delayed data covers streaming quotes only. That means a funded IBKR Pro account with USD 500+ equity and US futures trading permissions, plus a non-professional status update. Cheapest coverage for CME, CBOT, COMEX and NYMEX is about USD 6.20/month (four L1 rows at USD 1.55, each waived above USD 20 commissions) or USD 10/month for the bundle. A free trial account will not return historical candlesticks.
3. **The paper account sees data only through sharing,** and the live and paper sessions must then run on the same machine. Alternatively, run only the paper session (the live user not logged in gets "Live" in the paper session, per KB 1719's Case 1 table, row 58).
4. **Bar dates:** daily bars arrive as `datetime.date` (yyyyMMdd) and are dated by the session's closing day, which matches CME trade dates. Keep the TWS or Gateway time zone fixed (for example US/Central) and request intraday data with formatDate=2 (UTC).
5. **Contracts:** resolve every contract with `qualifyContracts` / `reqContractDetails` and read `multiplier` and `localSymbol` from the result. Use **MHNG** (trading class MNG) for Micro Henry Hub. Yield micros are quoted in yield. Expired months need `includeExpired=True` and go back only 2 years. For longer back-history, use the Databento store.
6. **Pacing:** daily-bar pulls for 12 symbols are far below the limits. Keep at most about 1 request per second, no identical request within 15 s, and handle 162, 166, 200 and 354 as data-unavailable errors, not crashes.
7. **Operations:** IB Gateway stable standalone on Linux, run under IBC 3.24.2 (retired and archived; bug fixes only), xterm installed, paper port 4002. Set `TradingMode=paper`, `AcceptNonBrokerageAccountWarning=yes` and `ReadOnlyApi` as wanted. Expect one manual login per week after Sunday 01:00 ET for live users. Whether paper logins need 2FA is unknown. ib_async's `Watchdog` plus `IBC` handles restarts and reconnects.
8. **Residency:** IBKR Canada bars API order entry for products on *Canadian* exchanges. CME-group futures are not Canadian products, but which IBKR entity holds the account matters (row 24). Lead to check.

## Could not establish

- Whether paper-username logins require 2FA. [unverified]
- Official text for error codes 10167 and 10168. Neither is on the current or legacy official error list.
- A current (non-legacy) IBKR statement on settlement versus last trade for futures daily bars, and any API field carrying the settlement price. None found.
- Multipliers and the localSymbol format for the 12 micros. No IBKR page fetched lists them.
- Whether the USD 1.55 single-exchange L1 subscriptions can be bought without the USD 10 bundle, and whether footnote four (USD 30 commissions) is a requirement or only the waiver condition.
- The exact maximum duration per request for 1-day bars. The current table's cells did not come through as text.
- Whether a funded account is needed before paper access, or only an approved one. Official pages disagree.
