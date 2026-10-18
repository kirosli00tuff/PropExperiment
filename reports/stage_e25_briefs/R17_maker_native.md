# R17 Maker-native liquidity provision (Stage E.25, research only)

Reader: R17-MakerNative-OpusHigh. Started 2026-10-18 01:54 PDT; cut by the usage limit at about 02:00 PDT;
resumed 06:12 PDT; written 06:13-06:15 PDT (date) under the lead's 06:33 deadline. Overlap checked against
r0_mechanism_index.md (grep), RD4_redig_fx_ags.md, RD2_redig_rates.md, R3_orderflow.md, RD5/R1 (no pinning
source there). Tool state: OpenAlex exhausted, Firecrawl out of credits, WebSearch session limit hit after
7 calls, Semantic Scholar keyless 429 nine times (section 9). Five full texts fetched; four read.

## 1. Answer (at most 250 words)

Generic slow market making in E-mini futures does not pay. The CFTC audit-trail study of ES (Baron,
Brogaard, Kirilenko 2014) marks every account's trades one minute later: Passive HFTs net only +$0.08 per
contract (0.006 ES ticks), and the non-HFT market makers, a class defined by low aggressiveness and
flat end-of-day inventory, which is the profile a retail maker would have, LOSE $0.97 per contract
(-0.08 ticks). Small traders lose $3.67 per contract (-0.29 ticks). Passive HFTs make money over 1 to
1,000 transactions and lose it over longer intervals, so inventory held for minutes is the losing part.
A maker at retail latency, filled only on trade-through (D.1g/C6), sits on the losing side of this split.
The only maker-native ideas that survive are ones where the price pressure itself is large, timed and
published, and the limit order is just the entry: (C1) fading the 3rd-Friday SOQ spike with a resting sell
limit above the 08:30 CT open (Baltussen-Terstegge-Whelan via RD4: +14.30 bp into the open, -12.89 bp
reversal by noon ET; about 31 MES ticks); (C2) expiry-day pinning in ES serial options months (Golez and
Jackwerth 2012: at least 11 bp aggregate shift Thursday PM to Friday PM, about half of it in the last 30
minutes; no per-trade gross, pre-2010 sample). The commodity-ETF/GSCI roll (Bessembinder et al. 2016)
gives a 25 bp calendar-spread widening per roll that reverses over the following days. Topstep does not
allow overnight holds, so it is listed as C3 for other venues only. Its intraday imbalance reverses within
1 to 3 minutes, which is HFT-scale.

## 2. Candidate hypotheses

| id | hypothesis | instruments | window CT | hold | published effect | gross/trade | grade | data | owned | testable | overlap |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R17-C1 | Maker-side fade of the 3rd-Friday SOQ spike: rest a sell limit k ticks above the 08:30 CT Friday open (monthly 3rd Friday, quarterly and serial); fill only on trade-through; cover by 11:00 CT (reversal complete "by 12:00" ET) | MES, MNQ, MYM | Fri 08:30 to 11:00 | up to 2.5 h | ES futures reversal -12.89 bp (t -2.40, sd 80.45), 2003-2021, as quoted in RD4 from Baltussen, Terstegge, Whelan (2024) | 12.89 bp x 6000 / 10000 = 7.73 ES pt = 30.9 MES ticks (gross, published at close-to-noon marks, not at a limit fill) | working-paper (via RD4, not refetched by R17) | 1-min bars, 3rd-Friday calendar | yes | yes | RD4-C1 / R12-C1/C2 (same paper; this is the limit-entry variant of their short leg); E-H3 (quarterly witching short) |
| R17-C2 | Expiry-day pinning in ES: on serial ES-options expiry Fridays (non-quarterly months), rest limits that fade moves away from the nearest 5-point strike in the last 30 min (14:30-15:00 CT); flat by 15:05 | MES (ES options strikes) | 14:30 to 15:05 | under 35 min | futures pulled to ATM strike; abs-return shift "at least 11.00 bps" Thu PM to Fri PM, "$59 million" of $115 million in the last 30 min (1992-2009) | not published per trade; 11 bp is a lower-bound aggregate distribution shift (= 6.6 ES pt at 6000), NOT a trade P&L | peer-reviewed (JFE 2012) | 1-min bars + strike grid (computable, 5-pt grid) + serial-expiry calendar | partial (no open interest; strike grid inferable) | yes, at low power (8 days/yr) | none in the index; not in RD5/R1 |
| R17-C3 | Provide liquidity to the commodity ETF / GSCI roll: on preannounced roll dates, take the far-month side against the roll at limit, hold until the spread narrows (days) | CL front/second (MCL) | roll days (USO: 4 days; GSCI 5th-9th business day) | multi-day | calendar spread widens "25 basis points per roll" before and during, narrows "26 basis points per roll" after (2008-2009 sample) | 25 bp of CL at $70 = $0.175/bbl = 17.5 CL/MCL ticks on the SPREAD, multi-day | working-paper draft of JFE 2016 | 1-min bars for two contract months | partial (front/second paths need checking) | partial | none (K4 members are WPSR/storage; K2-rollspread-01 excluded in E.0 is rates) |

Why each is weak:
- R17-C1: the effect is the reversal itself. A resting limit only saves about half a spread (~0.5 MES tick)
  against a ~31-tick move. At trade-through fills it is filled only if price rises further after 08:30,
  which selects the days the spike continues (adverse selection inside the event). It belongs with RD4-C1,
  and the lead merges them. 12 events a year; t -2.40 on 2003-2021.
- R17-C2: the sample (1992-2009) is from before weeklies and 0DTE, and ES option open interest has since
  moved to weekly and daily expiries. The paper publishes no trading rule and no per-trade P&L. It needs
  open interest by strike, which the program does not own. About 8 events a year.
- R17-C3: Topstep requires flat before 15:10 CT, so this is prop-incompatible there (PropEd allows
  overnight holds per section 3; automation is unclear). The sample is 12 rolls in 2008-2009. The paper
  finds market quality improves on roll days ("no evidence of the systematic use of predatory
  strategies"), so the edge was probably competed away. Mou (2011) reports Sharpe up to 4.4 for
  front-running the roll [secondary-only: Columbia repository blocked by a bot challenge].

## 3. Evidence table

| claim | number | verbatim quote | location | source | grade | saved path |
|---|---|---|---|---|---|---|
| Passive HFTs barely earn per contract at 1-min marks in ES | +$0.08/contract | "HFTᴾ ... -$1.93 -$0.94 $0.00 $0.75 -$0.62 $1.79 $5.05 $0.08" | Table 7 Panel B "Profit/Loss Per Trade", Aug 2010 | Baron, Brogaard, Kirilenko, "Risk and Return in High Frequency Trading", CFTC OCE draft Apr 2014 (later JFQA 2019), cftc.gov | working-paper (regulator-hosted) | pages/R17/bbk_riskreturn_2014.pdf/.txt |
| Slow (non-HFT) market makers lose | -$0.97/contract | "Non-HFT MM -$2.64 -$1.95 -$0.75 $0.00 -$1.59 $1.11 $4.25 -$0.97" | Table 7 Panel B | same | working-paper | same |
| Non-HFT MM definition = retail-maker profile | aggr. < 20%, EOD inventory < 15%, >= 20 contracts/day | "Non-HFT market makers are non-HFT market participants who have a (1) aggressiveness ratio less than 20%, (2) end-of-day inventory ratio less than 15%, and (3) median trading volume of at least 20 contracts (about $1 million) per day." | Sec. 2 data | same | working-paper | same |
| Small traders lose most per contract | -$3.67/contract | "Small Trader -$3.49 -$4.42 -$5.05 -$4.25 -$2.87 -$2.05 $0.00 -$3.67" | Table 7 Panel B | same | working-paper | same |
| Passive HFTs lose over longer horizons (inventory) | sign flip beyond ~1,000 transactions | "Passive HFTs show the opposite, making money at short horizons and losing money over longer intervals." Table 6: "HFTᴾ $5,236 $12,991 $11,408 -$7,917 -$9,774 -$3,428" | Intro; Table 6 spectral (1-10 ... 100,000+ transactions) | same | working-paper | same |
| Liquidity taking, not providing, pays | daily $74,000 vs $12,600 | "the average Aggressive HFT firm earns a daily profit of $74,000 in gross trading revenues, while average Mixed and Passive firms earn $27,910 and $12,600" ... "suggesting a stronger profit motive for liquidity taking than liquidity providing." | Sec. on Table 2 | same | working-paper | same |
| Fee level in the sample | $0.15/contract | "such direct costs of trading as trading fees ($0.15 per contract)" | Sec. 2 | same | working-paper | same |
| Pinning in ES on serial expiries; mechanism | at least $115M/expiry | "S&P 500 futures are pulled toward the at the money strike price on days when serial options on the S&P 500 futures expire (pinning) ... driven by the interplay of market makers' rebalancing of delta hedges" | Abstract | Golez, Jackwerth (2012), JFE 106(3) 566-585, KOPS open-access copy | peer-reviewed | pages/R17/golez_jackwerth_2012.pdf/.txt |
| Size and timing of pinning | >= 11.00 bp; $59M of $115M in last 30 min | "We find in the long sample (November 1992 until November 2009) a shift of at least 11.00 bps from Thursday PM to expiration Friday PM. ... An amazing $59 million shifts solely within the last 30 min of trading." | Sec. 5.1, p. ~572 | same | peer-reviewed | same |
| Pinning stronger 1998-2009, mostly from below | 22.47% within $0.375; 14.71% from below | "The result is slightly stronger at 22.47% if the focus is on the short sample from October 1998 to November 2009" ... "pinning from below the strike price is 14.71%" | Sec. 5.1 | same | peer-reviewed | same |
| Roll cost to ETF = gross to its counterparty, multi-day | 25 bp/roll; 26 bp after | "widening of the calendar spread between the second- and the front month contract prices in the days before and during the USO roll, which averages 25 basis points per roll." ... "This differential of 3.16% per year equates to 26 basis points per roll" | Sec. on daily settlement returns (l.1625-1645 of txt) | Bessembinder, Carrion, Tuttle, Venkataraman, draft June 2015 (JFE 121(1) 2016) | working-paper | pages/R17/bctv_predictable_2015.pdf/.txt |
| Intraday roll pressure reverses in 1-3 minutes (HFT scale) | 1 min front, 3 min second | "imbalance is almost entirely reversed within one minute in the expiring contract and within three minutes in the second nearest-to-expiration contract on roll days" | Intro p. 3 | same | working-paper | same |
| More liquidity providers, no predation on roll days | | "a larger number of individual trading accounts provide liquidity on roll days, and do not find evidence of the systematic use of predatory strategies" | Abstract | same | working-paper | same |
| Roll trades executed via TAS, timing unknown | | "capture the settlement price for its trades while effectively outsourcing the actual execution of the roll trades to the TAS contract counterparty ... will not know the exact time at which the TAS counterparties will execute" | Sec. 4 | same | working-paper | same |
| Sample is 12 rolls, 2008-09 | | "spans the period March 1, 2008 to February 28, 2009, and therefore includes twelve monthly rolls" | Sec. 3 | same | working-paper | same |
| Front-running the GSCI roll profitable (pre-2010) | Sharpe up to 4.4 | "Mou (2011) reports that significant profits can be earned by investors who trade in advance of the dates that the SP-GSCI index begins to track the second- rather than nearest-to-expiration futures contract." (citing source); Sharpe 4.4 from a search summary of the thesis abstract | BCTV Sec. 2 | Mou (2011) Columbia thesis | thesis [secondary-only] | bctv txt; Columbia copy blocked |
| 3rd-Friday SOQ spike and reversal (owner RD4) | +14.30 / -12.89 bp | "The average overnight cumulative return in the active futures contract is equal to 14 bps which completely reverses by 12:00." (as quoted in RD4) | RD4 evidence row | Baltussen, Terstegge, Whelan (2024) AEA 2025 paper | working-paper (RD4's fetch) | pages/RD4/baltussen_terstegge_whelan_2024_aea.pdf |

## 4. Negative evidence

- BBK Table 7: in ES, the trader class whose behaviour a retail maker would copy (passive, flat at
  day end, non-HFT) loses $0.97 per contract at the one-minute mark, before fees ($0.15 then). Passive HFTs,
  who have queue priority and speed, earn $0.08. In tick units both are under 0.1 tick, an order of
  magnitude below the MES hurdle of about 3 ticks.
- BBK Table 6: passive profits turn negative from about 1,000 transactions upward (-$7,917, -$9,774,
  -$3,428 median per firm-day). Holding inventory for minutes, the retail maker's horizon, is where
  passive liquidity providers lose.
- Program record: C-H4, a MES reversal entered with resting limits, ran at UCB95 -177.18 net ticks per
  micro per day under trade-through fills (DECISIONS.md, C6 closed). That agrees with BBK: passive entry
  with no timed flow behind it does not pay.
- Bessembinder et al.: predictable roll flow drew more liquidity providers, and spreads narrowed (front
  effective spread 2.03 to 1.95 bp, "t-statistic = -4.11"), so maker rent shrinks when flow is
  predictable. Its intraday reversal (1-3 min) is too fast for retail latency.
- Golez-Jackwerth: no trading rule is published, the sample is pre-2010, and pinning concerns where the
  price settles, not a per-trade edge.

## 5. Data and cost

C1 and C2 need only owned 1-minute bars plus calendars: the 3rd-Friday and serial-expiry calendars are
computable, the ES strike grid is 5 points, and the program owns no open interest data. C2's
open-interest conditioning (Golez-Jackwerth regressions use OI and volume at the ATM strike) needs
options data, which is not owned, and no price was gathered in this pass. C3 needs two contract-month
paths per root on roll dates (check the 27 owned price paths) and the USO/GSCI roll calendars (public
schedules, not fetched). No Databento pages were read: price unknown, no spend.

## 6. Prop compatibility

C1 and C2 are intraday and flat by 15:05 CT. They place 1 to 3 orders per event with holds of minutes
to hours. That is not HFT, and it does not use SIM queue position: fills are assumed at trade-through
only. No P06 conflict, though C1's Friday can coincide with a release such as CPI or retail sales at
07:30 CT, before the 08:30 entry. C3 needs overnight holds, which Topstep forbids. Of the venues in
section 3 only PropEd allows overnight holds, and its automation status is unclear.

## 7. Overlap with tested mechanisms

- E16-H1 (settlement-window momentum), E16-H4 (next-day reversal), E20H6-T1..T3: market-order momentum
  or reversal around the settlement. None of R17's candidates enters at the settlement window.
- E16-H2 (month-end NQ/ZN pair), K2-monthend-01, E23-MEZ*: month-end flows. R17 found no intraday
  month-end maker evidence and adds no candidate (RD2 owns month-end).
- E16-H3, K2-aucpre/aucpost-01: the auction cycle. R17 did not refetch Lou-Yan-Zhang (multi-day, RD2's
  source) and has no candidate.
- E-H3 (quarterly witching short) and RD4-C1/R12-C1/C2: same family as C1. C1 differs only in using a
  resting sell limit above the SOQ open instead of a market order, so it is a variant for the lead to
  merge, not a new mechanism.
- C-H4: a generic reversal with resting limits, which failed. C1 and C2 differ in being tied to a dated
  flow with a published mechanism.
- R3 owns order-book imbalance fades. Its finding that OFI effects decay within seconds on ES agrees with
  BBK and Bessembinder et al.

## 8. Re-dig: not a re-dig reader. Verdict checks: BBK supports the C6 closure (passive liquidity
provision without a speed or queue edge loses per contract in ES).

## 9. Fetch log

| url | UTC | sha256 | path | status | tool |
|---|---|---|---|---|---|
| https://www.cftc.gov/idc/groups/public/@economicanalysis/documents/file/oce_riskandreturn0414.pdf | 2026-10-18T08:56:24Z | 5623cb18d74e677cac8a234e0fe8e6de7b650ec9e0728d4f32f77c3a567e6173 | pages/R17/bbk_riskreturn_2014.pdf | ok | curl |
| https://www.bankofcanada.ca/wp-content/uploads/2012/11/Brogaard-Jonathan.pdf | 2026-10-18T08:56:29Z | 5a92c9aca4b2156456628cc6af95ea9853dece1597f423de56580af5780eb2ce | pages/R17/bbk_tradingprofits_2012.pdf | ok (saved, not read; 2012 version) | curl |
| https://kops.uni-konstanz.de/bitstreams/b9492112-cab3-4217-a7d0-d2c4f5ba7825/download | 2026-10-18T08:56:39Z | 07fabf4aa169abe42c79f63c1780e691ca885be59a5326361d4583fff0fe0cdb | pages/R17/golez_jackwerth_2012.pdf | ok (KOPS open access green) | curl |
| https://www.ou.edu/content/dam/price/Finance/energyfinanceconference/Liquidity%20and%20Market%20Quality%20around%20Predictable%20Trades.pdf | 2026-10-18T08:57:37Z | b914ca1a92b8ee4993f9bfbaaaf611bdee5bfae8e4772e49167bf59feed40fb9 | pages/R17/bctv_predictable_2015.pdf | ok | curl |
| https://academiccommons.columbia.edu/doi/10.7916/D8DR32JG/download | 2026-10-18T08:57:47Z | aa326dd18ad061b31df6c814a754832c7d0cee0ce2bcf3d818450a6c6878e29d | pages/R17/mou_thesis_blocked_anubis.html | blocked (bot challenge) | curl |

Terms: cftc.gov cited from terms_log (allowed, government information). Terms pages for
bankofcanada.ca, kops.uni-konstanz.de and ou.edu were not read or logged before these single PDF
fetches: a gap, see section 10. Budget notices (UTC): 08:5x OpenAlex "Rate limit exceeded ... $0
remaining"; 08:58 WebSearch "You've hit your session limit · resets 6:10am (America/Vancouver)";
08:58 Firecrawl "Insufficient credits"; about 09:05 Semantic Scholar 429 x9, throttled. The session then
hit the usage limit at about 02:00 PDT and resumed at 06:12 PDT.

## 10. Unfinished and unverified

- Not fetched (tools exhausted): Menkveld (2013) maker P&L decomposition; Kirilenko-Kyle-Samadi-Tuzun
  Flash Crash intermediaries; Silber (1984) and Kuserk-Locke (1993) on pit scalpers' per-trade profits
  and holding times; Linnainmaa (2010) on retail limit-order adverse selection; LETF close rebalancing
  (Cheng-Madhavan, Shum et al., Ivanov-Lenkey); settlement-window/TAS studies; Harvey-Mazzoleni-Melone
  full text (RD2 notes its terms block).
- The BBK 2012 Bank of Canada version was saved but not read.
- Terms for bankofcanada.ca, kops.uni-konstanz.de and ou.edu were not checked before the single PDF
  fetches; the lead may want them logged or the files excluded from commits.
- C1's numbers come from RD4's file, not from R17's own read of the paper.
- Mou's Sharpe 4.4 is [secondary-only].
