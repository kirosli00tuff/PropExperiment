# Stage E.10 Task 2: search plan for K9 (low-frequency, full-session holds)

Lead, 2026-10-02 22:30 PDT. Inputs: reports/stage_e10_design_target.md (sha256 ce798814..., fixed
22:29 PDT before any source was read): the cost wall, the K9 shape, the default definitions and the
exclusion list X1-X15.

## Common rules for every reader

- **What counts as a candidate.** A published effect in futures (or in the underlying index, currency,
  commodity or rate, where the futures inherit it) that (1) trades on a **condition that holds on
  roughly 10% to 40% of trade dates** (one trade every two weeks up to two a week) or can be made so
  by the source's own definition, (2) holds for **hours, up to a whole trade date** (from the 17:00
  CT reopen, or the session open, to the close), (3) is **directional** with a sign stated by the
  source, and (4) differs **in mechanism** from X1-X15. Unconditional daily drifts that would trade
  every day do not fit unless the source itself names a condition that makes them rare. A source
  that gives a mechanism but no condition can still be logged, as context.
- **Sources.** Peer-reviewed papers, working papers (SSRN, NBER, central banks, university
  repositories), and practitioner research with a stated sample and method. Blogs only as pointers,
  never as evidence. Every candidate mechanism needs at least one full-text or abstract quote.
- **Search tools, in this order.** Semantic Scholar Graph API
  (`https://api.semanticscholar.org/graph/v1/paper/search`, key from `.env` SEMANTIC_SCHOLAR_API_KEY as
  the `x-api-key` header, never printed or logged, at most 1 request a second). OpenAlex
  (`https://api.openalex.org/works?search=...&mailto=<OPENALEX_EMAIL from .env>`). Then WebSearch.
  Full text by WebFetch first, then `scrapling extract get`, then `scrapling extract fetch`. Use
  `stealthy-fetch` only where the site's terms allow automated access. Firecrawl only when Scrapling
  fails, and log each Firecrawl use. Load the key with a shell variable read from .env inside the
  same command (for example `KEY=$(grep '^SEMANTIC_SCHOLAR_API_KEY=' .env | cut -d= -f2-)`); never
  echo it.
- **Budgets per reader.** At most 120 WebSearch calls (the session-wide cap is shared). Scholarly API
  calls are not capped, but stay polite. About 70 minutes of work. If WebSearch returns the
  over-budget notice, stop searching, write the notice and the time into the log, and return.
  Never continue from memory.
- **Saturation stop.** Stop a topic when the last 15 records screened add no new candidate mechanism,
  or when the budget is reached. Say which.
- **Raw pages.** Every page or PDF used as evidence is saved raw under
  `reports/stage_e10_research/<reader>/` (`regime`, `overnight`, `calendar`, `commodity`), with a
  `.txt` extraction beside each PDF (pdftotext) for grep. One fetch-log row per file goes in the
  reader's log: URL, UTC fetch time, sha256 of the raw file, size, tool used. Read files by grep,
  never whole.
- **E.0's sources.** reports/stage_e10_briefs/e0_logged_sources.txt lists the 244 sources E.0
  logged (also reports/stage_e0_source_registry.jsonl). Do not re-screen them. If a K9 mechanism
  depends on one, re-fetch it, save it raw and log it under a K9 id with its E.0 id beside it.
- **Log format** (E.0's): per source an id `K9<R|O|C|M>-NNN` and a citation (with DOI). Then the
  retrieval route and file. The mechanism in one or two sentences, the products and horizon, the
  sample window (exact dates), the market and data frequency, and the cost assumptions. Then quality
  tells, verified passages `P-K9x-NNN-a`, `-b`, ... **quoted verbatim from the saved file**, with the
  section or page, and numeric claims each tied to a passage id. Then conflicting evidence (with its
  own passages), and the reader's note: whether it fits the K9 shape, which exclusion it might hit
  (X1-X15), and how its documented move compares with M_X and G(f) in the design target, in the
  source's own units. **A search-result summary is never logged as retrieved text.** If only the
  abstract could be read, say "abstract only".
- **No market data.** Do not open any file under data/, any Stage E screen record or any
  results file. No Databento, no purchases, no trading-platform API or credential reference. The design target and this plan
  are the only program inputs a reader needs.

## Topics, queries, owners

### Reader 1: LitReader-Regime-OpusHigh (log reports/stage_e10_research_regime.md)

**R1. Session drift conditioned on a volatility state** (implied-volatility spikes, realized-volatility
regimes, VIX term-structure inversion) in equity index, rates, FX and commodity futures.
- Cost-wall link: a high-volatility state raises the expected absolute move of the hold. A risk premium
  that scales with volatility then grows relative to a fixed round trip.
- Semantic Scholar / OpenAlex: "VIX spike subsequent returns S&P 500 futures daily"; "volatility regime
  conditional return predictability futures"; "VIX term structure inversion equity returns";
  "intraday returns high volatility days index futures"; "variance risk premium short horizon return
  predictability daily"; "time-varying risk premium after volatility shocks"; "realized volatility
  predicts next day return futures".
- Web: "VIX term structure backwardation next-day S&P returns paper"; "returns after volatility spikes
  daily evidence futures pdf"; "overnight versus intraday returns high VIX".

**R2. Session drift after a large prior-day move, where the mechanism is not a fade** (continuation of
large moves, information diffusion, slow-moving capital, margin-driven deleveraging). Watch X10 and X3.
- Cost-wall link: large-move days select states where the next session's absolute move is also large.
- SS / OA: "large price changes subsequent returns futures markets daily"; "momentum after extreme
  daily returns commodity futures"; "next-day return after large moves stock index futures";
  "price continuation after large daily price changes"; "deleveraging margin calls futures next-day
  returns".
- Web: "large daily price moves continuation futures empirical"; "post-shock drift index futures".

**R3. Range compression and expansion** (narrow-range days, inside days, low realized volatility
followed by directional drift). Watch X2.
- Cost-wall link: an expansion day after compression has a larger expected move. The direction has
  to come from a separately sourced mechanism.
- SS / OA: "narrow range day volatility expansion futures"; "volatility compression subsequent return
  direction"; "inside day breakout futures empirical"; "low volatility regime trend futures".
- Web: "NR7 inside day study futures academic"; "volatility contraction expansion daily futures paper".

### Reader 2: LitReader-Overnight-OpusHigh (log reports/stage_e10_research_overnight.md)

**O1. Overnight-to-day continuation or reversal over full sessions.** The split of futures returns
between the overnight (Globex) and day sessions, and whether one predicts the other over the full
session. Watch X1 (CP1's signal includes the overnight return) and X10 (gap fade).
- Cost-wall link: a full overnight or full day-session hold captures the whole of a session-level
  premium, the largest per-trade move available inside one trade date.
- SS / OA: "overnight returns intraday returns futures markets"; "overnight drift S&P 500 futures";
  "night trading returns versus day trading returns futures"; "overnight return predicts intraday
  return index futures"; "opening gap continuation full day futures"; "returns in trading and
  non-trading hours futures"; "European open overnight drift".
- Web: "overnight drift Boyarchenko Larsen Whelan"; "overnight returns commodity futures paper";
  "Treasury futures overnight returns Asian session".

**O2. Conditional time-series momentum at the daily scale, applied inside one session.** Trend over
days to months (TSMOM) as a session hold, where the profit accrues by session, and conditions
(trend strength, volatility state) that make it rare. Watch X1 and X15.
- Cost-wall link: a multi-week trend signal held for a full session captures one session of a
  persistent drift. The per-trade target is the session's share of the trend premium.
- SS / OA: "time series momentum futures daily returns"; "time series momentum intraday overnight
  decomposition"; "short-term time series momentum futures"; "trend following returns overnight
  intraday"; "momentum returns accrue overnight"; "time series momentum is it there".
- Web: "time series momentum overnight versus intraday futures"; "trend following day session
  returns paper".

### Reader 3: LitReader-Calendar-OpusHigh (log reports/stage_e10_research_calendar.md)

**C1. Day-of-week and turn-of-week effects** in equity index, rates, FX, commodity and bitcoin futures.
Recent evidence, after 2000 and after 2010 where available. Watch X15 (MBT Monday trend) and X14
(weekend bitcoin to the Monday Nasdaq-100).
- Cost-wall link: a calendar member trades a known date set (one day a week, about 60 trips in 299
  dates), so its trip count is fixed in advance and its target is one full session.
- SS / OA: "day of the week effect futures markets"; "Monday effect index futures recent evidence";
  "weekend effect commodity futures"; "day-of-the-week effect bitcoin returns"; "turn of the week
  effect"; "Friday effect futures returns".
- Web: "day of week effect futures 2010s evidence pdf"; "weekend effect disappeared futures".

**C2. Macro-announcement-day premia over a full session** (equity or bond premia earned on CPI, PPI,
employment or FOMC days as a whole). This is distinct from the pre-release drift X4 and the
post-release continuation X6. The frequency must be checked: a union of monthly releases can reach
40 or more trips in 299 dates, while FOMC alone cannot.
- Cost-wall link: the documented announcement-day premium is a large fraction of the annual equity
  premium earned on a few dates, so the per-trade move is large.
- SS / OA: "announcement day returns macroeconomic risk premium"; "stock returns on macroeconomic
  announcement days"; "bond returns announcement days premium"; "pre-FOMC announcement drift
  futures"; "macro announcement premium futures intraday".
- Web: "Savor Wilson announcement day premium"; "announcement premium recent evidence 2020".

**C3. Pre-holiday and other calendar dates not yet tested.** Log the frequency honestly: pre-holiday
alone is about 9 dates a year, below the floor. Also options-expiration effects (watch X13), and
seasonal-month effects only if they reduce to a full-session rule.
- SS / OA: "pre-holiday effect futures"; "option expiration week returns index futures"; "triple
  witching effect futures returns"; "holiday effect commodity futures".
- Web: "pre-holiday effect futures evidence".

### Reader 4: LitReader-Commodity-OpusHigh (log reports/stage_e10_research_commodity.md)

**M1. Term-structure, basis and carry signals read from the futures curve** (backwardation or
contango, roll yield, basis momentum) in energy, metals, grains and livestock, and in FX (rate
differential) and rates (curve slope), at the daily horizon. Also whether the carry premium
accrues in the overnight or the day session. Flag any member needing deferred-contract bars (a data
item).
- Cost-wall link: an extreme curve state (a top-quintile backwardation) marks a high expected-premium
  state. The per-trade target is one session of that premium.
- SS / OA: "term structure commodity futures return predictability daily"; "basis momentum commodity
  futures"; "backwardation contango short horizon returns"; "roll yield predicts returns commodity
  futures"; "carry trade returns intraday overnight currency futures"; "treasury futures returns time
  of day".
- Web: "commodity futures term structure daily return predictability paper"; "currency carry returns
  by trading session".

**M2. Supply, inventory and seasonal regimes** (theory of storage: low inventories, weather markets,
heating season, harvest pressure, livestock seasonals) as rare states that sign a session drift.
Release-timed trades are X7 and X8 and are excluded. The state variable must be a level or a
season, not a release window.
- Cost-wall link: scarcity states carry larger and more persistent moves.
- SS / OA: "inventory levels commodity futures returns theory of storage"; "natural gas storage level
  price drift"; "weather market corn soybean futures seasonal returns"; "harvest pressure futures
  returns seasonal"; "seasonality commodity futures returns daily"; "inventory risk premium futures".
- Web: "commodity seasonality futures academic evidence"; "theory of storage inventory returns
  futures pdf".

## Ownership and boundaries

| Reader | Topics | Log | Raw pages | Must not touch |
|---|---|---|---|---|
| LitReader-Regime-OpusHigh | R1, R2, R3 | reports/stage_e10_research_regime.md | reports/stage_e10_research/regime/ | other readers' topics, any catalog file |
| LitReader-Overnight-OpusHigh | O1, O2 | reports/stage_e10_research_overnight.md | reports/stage_e10_research/overnight/ | same |
| LitReader-Calendar-OpusHigh | C1, C2, C3 | reports/stage_e10_research_calendar.md | reports/stage_e10_research/calendar/ | same |
| LitReader-Commodity-OpusHigh | M1, M2 | reports/stage_e10_research_commodity.md | reports/stage_e10_research/commodity/ | same |

A source that belongs to another reader's topic is noted in one line under "Routed" at the end
of the log and is not read. Overlaps are expected between R2 and O1 (prior-day moves and gaps) and
between O2 and M1 (TSMOM and carry). The lead resolves duplicates in Task 4.
