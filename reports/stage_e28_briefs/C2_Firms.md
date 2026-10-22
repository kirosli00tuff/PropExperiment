# C2_Firms: how top trading firms run the research process (Stage E.28 methods brief, deep dive)

Worker: C2_Firms (opus, high). Started 2026-10-21 02:49 PDT. Pages ROOT: reports/stage_e28_briefs/pages/C2_Firms/
(log.tsv there lists every fetch with URL, UTC and PDT time, method, sha256). Helper scripts:
reports/stage_e28_briefs/work/C2_Firms/.

Scope and evidence rules. Everything below is what the firms themselves have published (websites, research
libraries, technical blogs, talks with a published abstract, regulatory filings) plus a few firm-affiliated papers.
Each claim carries an evidence ID (E-numbers) that points to the evidence table at the end, which holds the verbatim
quote and the saved file. Podcasts and interviews appear only as pointers and are marked so. Anything not verified
from saved full text is marked [unverified]. Most top firms publish very little about their internal research
process. A blank cell below means "nothing public found", not "the firm does not do this".

Status: complete (sections 1 to 6); finished 2026-10-21. See the "Completion" note at the end.

---

## 1. Firm-by-firm: what is public

Each firm block uses the same headings where something is public: idea generation; data; tooling; simulation and
backtest discipline; multiple-testing and overfitting controls; holdouts and paper (test) trading; staged deployment
and capital; monitoring and decay; team structure; role of machine learning.

### 1.1 Man AHL (Man Group, Man Institute)

The richest public record of any firm in scope, mostly through the Man AHL Academic Advisory Board write-up on
overfitting (May 2015), with Man AHL's CIO (Matthew Sargaison), the head of the AHL Dimension programme (Nick
Granger), its Chief Scientist (Anthony Ledford) and a former CERN researcher present (E1).

- Overfitting definition used in-house: a model that "describes noise rather than signal" with "little or no
  predictive power on new data" (E2).
- Controls named by the board: a range of models instead of one (model confidence set), complexity penalties,
  stability under parameter variation, an independent review process, and monitoring the rejection rate of
  strategies through review (E3). The parameter "heat map" test, which Campbell Harvey (board member) calls "a common approach" rather than an AHL practice: "If your parameter choice is an isolated point
  sticking out, then this is a red flag" (E4).
- Rejection-rate monitoring as a process metric: count how many strategies are proposed, how many die in the
  initial research phase, how many are killed in review, and how many fail test trading (E5).
- Data partitioning written down in advance: after looking at the probability of backtest overfitting (Bailey et
  al.), the CIO said AHL had "used the ideas to enforce data partitioning with in-samples and out-of-samples more
  strongly. You now have to write down the data partitioning and the methodology and expectations" (E6). This is the
  closest public statement by any firm in scope to a pre-registration rule.
- Test trading on the firm's own capital before client money: "all strategies are first traded with the firm's
  capital" (E7). The test-trading window is short and is explicitly not a significance test: "the 2-3 months we
  would typically test trade a new model is not enough time to demonstrate any kind of statistical significance",
  but it has caught research or implementation mistakes; a model "immediately going into a large drawdown would
  certainly be a warning sign", for example "a 20% drawdown over the first three months would certainly look
  inconsistent with an assumed SR of 3" (E8, Nick Granger).
- Regime shift versus overfit: if the same breaking point shows across a range of strategies at once, a regime
  shift is likely; if only one strategy breaks, overfitting is more likely (E9).
- Expected live-versus-backtest gap as a band: "If I'm trading with a Sharpe of one, and I think my overfitting/
  model error consensus Sharpe is +/-0.2, then ... I would be surprised if I didn't achieve 0.8 in trading" (E10;
  Neil Shephard, board member, not Man staff).
- Culture and incentives (Harvey, on the board): reward high-quality research that ends in a negative result, or
  researchers will mine data; safeguards such as tracking "the number of times that researchers access the data or
  run different models" exist but can be bypassed (E11).
- The particle-physics analogy, offered by the board: CERN uses artificial data sets, control regions, strict
  in-sample and out-of-sample enforcement and replication by other teams (E12).

Firm research relevant to this program (Man-affiliated authors). Harvey and Liu (2015), "Backtesting", Journal of
Portfolio Management (Harvey sat on the Man AHL Academic Advisory Board, E1): the industry rule of thumb is a 50%
haircut to backtested Sharpe ratios (E13); the authors call that "a serious mistake" because the multiple-testing
haircut is nonlinear: the highest Sharpe ratios are only moderately penalized while marginal ones are heavily
penalized (E14). Method: take the strategy's t-ratio, adjust its p-value for the number of tests M by Bonferroni,
Holm or BHY, and convert back to a Sharpe ratio; the haircut is 1 - HSR/SR (E15). Worked example in the paper:
annualized SR 1.0 over 120 months, monthly autocorrelation 0.1, 100 tests, average correlation 0.4: the
autocorrelation-corrected SR is 0.912 and the BHY-adjusted SR is 0.438, a 52.0% haircut (E16). Their own caveat:
"we need some judgment specifying the number of tests" (E17). This is the same family of correction the program
already applies (Holm, DSR at N = 538); the paper adds the Sharpe-to-haircut mapping and the profit-hurdle function
(the minimum mean return needed at a given significance, number of tests and correlation, E94).

Man AHL on machine learning (Man Institute articles). ML "can play beneficial roles ... especially in
applications where there is a relative abundance of data", including "faster speed (e.g. daily and intra-day)"
strategies and "algorithms for trade execution and smart order-routing" (E71). The key passage for this program:
faster signals "exhibit greater non-linear structure, however such effects are hard to capture as alpha in the
client-scale funds ... they are just too fast. However, when applied in trade execution, such effects may offer
significant advantage in reducing transaction costs" (E72). The entry conditions Man states for ML: "ample amounts
of representative data, and effects that are not easily described using simpler models"; otherwise ML is "needless
and pointless complications" (E73). Bayesian ML is named as the robust choice for noisy data (E74). ML systems have
traded in AHL's multi-strategy client portfolio "since early 2014" (E75).

Pointer-grade (trade-press interview with AHL's co-CEO (its CIO at the time of E1), Risk.net 2018; journalism, not firm publication): "fewer
than one in 10 ideas make it past test trading", with a record internal reject rate (E89); an ML order router that
sends more trades to whichever route (internal algorithms, dealer algorithms, the desk) achieves better execution
(E90); and AHL has "been meticulous in recording every point at which" it has interacted with the market (E91).

Not found public for Man AHL in this pass: the internal backtest engine, the capital-allocation formula for new
models after test trading, and the decay monitoring rule beyond the board's remarks. Further Man Institute pieces on
machine learning and execution are pointers only unless listed in the evidence table.

### 1.2 Two Sigma

- Idea generation and the scientific method: the co-founder's stated principle is to ground "the entire investment
  process, from data ingestion to trade execution" on "the formulation of carefully crafted hypotheses, followed by
  a recurring process of measurement, learning, and adjustment" (E18; a Two Sigma summary of David Siegel's WSJ
  op-ed).
- Negative results as output: a well-designed experiment that disproves a hypothesis is called valuable because "it
  narrows the search space"; falsifiability is "a hallmark of good science" (E19).
- Holdout discipline, in a senior quantitative research manager's words: "We typically have an in-sample of data
  that we're studying, and then an out-sample of data that we've hidden from ourselves ... there's one day where you
  say, okay: I'm ready to open the out-sample" (E20). Failure modes he names: "I did something wrong, or I overfit,
  or the world has changed" (E21).
- Tooling and validation: researchers rely on "high-quality datasets, robust back-testing mechanisms, and sound
  validation techniques"; engineers build minimum viable products before committing to an unproven idea (E22).
- Team structure: shared feature libraries; researchers "collaborate to build models together, leveraging the data
  moat and compute power of the shared platform" (E23). Orthogonality is a stated goal: new features correlated with
  existing signals are "not usually the most valuable" (E24). Post-hoc rationalizing is named as the thing to avoid
  (E25). Source: Two Sigma's own summary of a podcast with its Head of Complex Feature Engines, so these are Two
  Sigma's published words; the podcast itself is a pointer only.
- Role of ML and AI: LLMs widen what can be studied as text; AI should "amplify" researchers' own ideas (E26).

Not found public: Two Sigma's multiple-testing rule, staged deployment and capital allocation process, and decay
monitoring.

### 1.3 Optiver

Optiver publishes the most specific public material on order-book machine learning of any firm in scope, through
its technology blog (2025-2026).

- Data and the order-book research question: the main driver of Optiver's high-frequency strategies is "the raw
  stream of order inserts, cancellations, modifications and trades"; prediction horizons are "typically seconds to
  minutes" (E27).
- The classical pipeline, and why each idea is expensive: hand-made features, then "regenerate the dataset, train
  new models from scratch and then evaluate via a backtest whether the idea adds value" (E28). Optiver's stated move
  is to learned feature extraction from raw events, while keeping domain expertise: "The shift is from engineering
  each feature by hand towards designing architectures" (E29).
- Level 1 to Level 3: at Level 1 a weighted-average price "is probably one of the most useful signals"; deep
  learning on a single snapshot is "Probably not worth it"; the case for learned features grows with sequences and
  with Level 3 queue data, where "A 200-lot order at the front of the queue therefore contains different information
  from the same order at the back" (E30).
- Four stated difficulties, each relevant to this program: low signal-to-noise ("a great model may have an accuracy
  of 52%" and "overfitting a serious concern"), non-stationarity, irregular event sampling, and long sequences (a
  100,000-event window "might cover only a minute of wall-clock time") (E31).
- Data sourcing and quality: Optiver found historical Level 3 vendor data "lacking" and became a customer, then an
  investor, of BMLL (E32). It names data defects that matter for any order-book study: 30+ near-duplicate auction
  flags, venue-specific field names, and the value of sequence numbers over timestamps for true ordering (E33).
  Backtests across "a vast range of market conditions" before live deployment are the stated purpose of the data
  (E34).
- Tooling: the research platform's single goal is to "shorten the loop from idea to validated result", and
  "Reproducibility and traceability are nonnegotiable" (E35). The research cycle is stated as "form a hypothesis,
  run experiments, evaluate results, then either refine the hypothesis or translate the results into production
  decisions" (E36). Feature generation is sharded by day (E37).
- Simulation-to-production parity: "Keeping simulation honest relative to production matters here too, so research
  does not 'work' in a way production cannot reproduce" (E38).
- Public ML competitions (pointer): Optiver ran Kaggle competitions on realized-volatility prediction and on the
  Nasdaq closing cross (2023); [unverified beyond search snippets]; Kaggle's own competition pages were not fetched; Optiver's post on the 2023 closing-cross competition was saved (optiver_kaggle_closing_cross.html) but is not used as evidence.

Not found public: Optiver's multiple-testing rule, holdout protocol, staged deployment or capital-allocation rule.

### 1.4 Hudson River Trading (HRT)

- Role of ML: "For over a decade" HRT has integrated AI research into trading; "Deep learning is core to our
  trading" (E39). Models "drive a significant fraction of HRT's trading" (E40).
- The firm's own statement of the problem: "Market data contains very little signal, making it easy to overfit to
  noise. Our models must be robust to distributional shifts caused by a rapidly evolving world and adversarial
  actors who adapt to our behavior and train against our latest models" (E41).
- Data and methods (NeurIPS 2023 expo talk abstract): data that are "massive, heterogeneous, unevenly spaced,
  noisy, and bursty"; tools named are multi-task learning, sequence modeling and large language models, with
  Bayesian optimization, quasi-Newton methods and portfolio optimization for trading decisions (E42).
- Team and tooling: a "strong common technological platform", a "substantial compute cluster outfitted with
  modern GPUs", "high GPU-to-researcher ratios" (E43).

Not found public: any HRT statement on holdouts, multiple testing, staged deployment or decay monitoring.

### 1.5 XTX Markets

- Role of ML and model history: XTX "uses state-of-the-art machine learning technology to produce price forecasts
  for over 53,000 financial instruments"; its models evolved "from econometric methods ... to trees, to neural
  networks, to modern deep learning architectures" over about 10 years (E44).
- Compute: "over 25,000 GPUs with more than 1 exabyte of usable storage" (E45; a job posting, the firm's own
  recruitment text).
- Tooling history: "The firm started out with a couple of desktops and an NFS server", and ten years later ran
  "tens of thousands of high-end GPUs" (E87; XTX's own tech blog). Its storage holds everything from "'cold'
  storage of raw market data" to short-lived data between GPU jobs (same file).

Not found public: research-process controls of any kind. XTX's UK Companies House accounts were not fetched in this
pass.

### 1.6 Virtu Financial (SEC filings)

- Trading-day statistic (S-1, March 2014): "we had only one losing trading day during the period depicted, a total
  of 1,238 trading days" (2009-2013), attributed to "our real-time risk management strategy and technology" (E46).
  The same filing describes its trading as "designed to be non-directional, non-speculative and market neutral",
  with minimal capital at risk and "nearly instantaneous hedging" (E47). Context for this program: that P&L shape
  comes from very many small trades across many instruments with immediate hedging ("small amounts earned on
  millions of trades", E48) and co-location; it is not a benchmark a single-contract, tens-of-milliseconds retail
  program can expect. The same filing credits "top tiers of favorable brokerage, clearing and exchange fees" (E92),
  and the 10-K describes connections "through a network of co-location facilities around the world" (E93).
- Monitoring and kill rules (S-1): if the risk system "detects that a trading strategy is generating revenues
  outside of our preset limits, it will lockdown that strategy and alert management" (E49). Note: revenue outside
  limits in either direction, not only losses.
- Monitoring and kill rules (10-K FY2025): every outbound message passes preset pre-trade risk controls; "Certain
  risk controls, when triggered, result in a strategy lockdown, which requires a manual reset"; model-level limits
  on position size and exposure, with automatic exposure reduction at limits; continuous monitoring by trading and
  risk teams; daily P&L and position reconciliations; "after event reviews" of operational issues (E50).
- Adverse selection, stated as a risk factor: "We may at times trade with others who have information that may be
  more accurate or complete than the information we have", which can leave unfavorable positions before large moves
  (E51). Competition: competitors "range from sole proprietors with very limited resources to highly sophisticated
  groups" (E52).

### 1.7 Citadel Securities

Public material is recruitment copy only.
- Scientific framing: "Avoiding untested assumptions, we treat market problems as scientific questions"; "When the
  data supports a hypothesis, we build out large-scale strategies" (E53). Researchers "identify market signals with
  potential predictive power" with proprietary tools and large datasets, and model "the impact of trading on market
  signals" (E54).
- An FX example: a team used "machine-learning algorithms and statistical models to scrutinize a data set of
  trades", then presented to management and got "the green light" for a client proof of concept (E55): a staged,
  management-gated path, without public detail of the gate.
- Skills stressed: statistics first ("a robust statistical intuition") (E56).

Not found public: holdouts, multiple testing, deployment or monitoring rules.

### 1.8 AQR (research library and AQR-affiliated papers)

AQR publishes papers, not process manuals. What bears on this program:
- ML in asset management (Israel, Kelly, Moskowitz 2020, "Can Machines 'Learn' Finance?"): the abstract says ML in
  asset management faces "a unique set of challenges that differ markedly from other domains" and stresses
  "economic theory and human expertise" (E68). Only the abstract was fetched; the full text (JOIM, SSRN) was not
  reachable [body unverified].
- Kelly and Xiu (2023, NBER; Kelly is at AQR and Yale): the three named difficulties are the "small data" reality
  of economic time series, weak signal-to-noise ratios, and structural instability, which "compounds" both (E69).
  These describe monthly and daily asset pricing; at order-book horizons the sample count is far larger, but the
  signal-to-noise and instability points carry over (compare Optiver E31, HRT E41).
- Replication and multiple testing (Jensen, Kelly, Pedersen 2023, Journal of Finance; AQR authors): a Bayesian
  model of factor replication finds most factors replicate and work out of sample in 93 countries, and that the
  evidence is "strengthened (not weakened) by the large number of observed factors" (E66). The paper quotes McLean
  and Pontiff: factor returns "are 26% lower out-of-sample and 58% lower post-publication" (E67). This is the
  opposing view to Harvey, Liu and Zhu (E57, E58): a Bayesian shrinkage approach to many related tests rather than a
  frequentist family-wise haircut. Its premise (economically motivated factors with a shared prior) does not hold
  for a free search over order-book configurations, so it does not license dropping the program's N-based
  corrections.
- Costs measured from the firm's own fills (Israel, Jiang, Ross 2017, citing Frazzini, Israel, Moskowitz): AQR's
  cost model is fitted on "real world execution data"; cost rises with participation rate, about 17 bps at 2% of
  daily volume versus about 28 bps at 6% (E70). The relevant practice is the method (fit the cost model on your own
  executions), not the equity numbers.

Not found public: AQR's internal holdout or staged deployment rules.

### 1.9 Jane Street

- Role of ML: "We believe deep learning is the future of quantitative trading"; data are "mostly noise",
  "regime-y", and "our own actions influence the data we're trying to model" (E76). Models have been used "since our
  founding in 2000" and reliance has grown sharply (E78).
- Method choice is problem-driven: "large-scale machine learning, domain expertise, or pen-and-paper mathematics"
  (E78).
- Tooling: almost all software in-house, "including our critical trading and risk management systems"; team lines
  between trading, research and technology "intentionally porous" (E79). Compute went from "6 Dells stacked on the
  floor" to a 4,032-GPU data center (E77).
- Feedback loop: "Trading serves as a unique, rapid-feedback platform for ML experimentation" (E78). This is a
  firm with live capital and flow; it is not a statement about validation without live trading.

Not found public: holdouts, multiple-testing rules, deployment gates. (A 2025 SEBI interim order concerning Jane
Street's index-options trading in India exists; it concerns market conduct, not research process, and was not
fetched [pointer only].)

### 1.10 Jump Trading

- Process statement: "Every trading strategy is grounded in research, stress-tested in real markets, and engineered
  to scale" (E80).
- The modeling problem in Jump's words: "low signal-to-noise ratio", which "demands an adaptable modeling process,
  carefully refined data, rigorous signal validation, and seamless execution" (E81).
- Decay, adverse selection and self-deception, stated as principles: "Any single source of edge erodes over time";
  "Every time you trade, it's because someone thought you were wrong"; "It's incredibly easy to fool yourself. Data
  not pristine? You'll fit the noise"; and the notebook-versus-production gap ("making it 99.9% accurate on real
  data, parsed on the fly") (E82).
- Team structure: some ML staff embedded in trading teams by market, others central (E83).

Not found public: any quantitative rule behind "rigorous signal validation" or "stress-tested in real markets".

### 1.11 Others where public

- Capital Fund Management (CFM, Paris). Two public technical pieces bear directly on this program. (a) Rej, Seager
  and Bouchaud (2019) give a framework "to model and quantify in-sample PnL overfitting" and "compute the factor
  appropriate for discounting PnLs" (E84). (b) A 2018 technical note on execution: CFM measures implementation
  shortfall against the decision price; its rules are to benchmark against expected cost, normalize costs by trading
  activity, and accept that "conclusions should only be drawn based on sufficient data" (E85). CFM runs competing
  execution strategies live and compares their cost savings over months, framed as a multi-armed bandit where "you
  will only have your own experience" (E86). This is the clearest public example of measuring fill and cost models
  from one's own live orders, which a fill-model pilot on historical data approximates but cannot replace.
- Research Affiliates and Harvey (Arnott, Harvey, Markowitz 2018/2019, "A Backtesting Protocol in the Era of
  Machine Learning"): a seven-category checklist (research motivation; multiple testing; data and sample choice;
  cross-validation; model dynamics; complexity; research culture) (E59-E63). Items that matter most here: keep track
  of every model and variable tried, successful or not (E59); "true out-of-sample tests are only possible in live
  trading", no out-of-sample "iterations", and out-of-sample analysis must include trading costs (E60); data
  transformations and winsorization rules chosen before research starts, and only one tried (E61); minimize
  tweaking a live model; simplest practicable specification; interpret the ML model (E62); "most tests will fail"
  (E63). Also: "tuning 10 different hyperparameters using k-fold cross-validation is a terrible idea if you are
  trying to predict returns with 50 years of data", and "out of sample is not really out of sample" because
  researchers have lived through the holdout period (E64); complexity widens the gap between backtest and live
  results (E65).
- Harvey, Liu and Zhu (2016): the source of the t > 3 hurdle the program already uses: "A new factor needs to clear
  a much higher hurdle, with a t-statistic greater than 3", with the authors' own caveat that 3.0 should "probably
  not" be used for every future factor (E57); and the false-discovery counts among 296 published factors (E58).
- Not covered in this pass (nothing fetched): Renaissance Technologies, D. E. Shaw, DRW, IMC, Tower Research,
  Winton. Public process material on these is believed to be sparse, but that belief is [unverified].

---

## 2. Cross-firm view: which practices are public, and where

E-numbers are evidence IDs; "-" means nothing public was found in this pass (not that the firm lacks the practice).
"AHM" is the Arnott-Harvey-Markowitz protocol; "HL/HLZ" are Harvey-Liu (2015) and Harvey-Liu-Zhu (2016).

| Practice | Where public (evidence) | Firms with nothing public found |
|---|---|---|
| Hypothesis-first, scientific framing | Two Sigma E18-E20; Citadel Securities E53; Optiver E36; Jump E80; AHM E59 | HRT, XTX, Virtu |
| Data partition, method and expectations written down in advance | Man AHL E6 (the only explicit firm statement) | all others |
| Hidden holdout, opened once | Two Sigma E20; Man AHL E6; caution that the holdout is "not really out of sample": AHM E64 | all others |
| Count every trial; track the rejection funnel | Man AHL E5, E11 (pointer: E89); AHM E59 | all others |
| Multiple-testing haircut or shrinkage | HL E13-E17; HLZ E57-E58; JKP (AQR) E66; CFM E84 | trading firms (HRT, Jane Street, Jump, Optiver, XTX, Citadel Securities) |
| Parameter-stability ("heat map") checks | Man AHL board write-up (Harvey) E4; the write-up's own summary lists "model stability under parameter variation" (E3); AHM E61 | all others |
| Prefer the simplest model; ML only where simple models leave structure | Man AHL E3, E73; AHM E62, E65; Optiver E30; Jane Street E78 | - |
| Reproducibility; simulation honest relative to production | Optiver E35, E38; Jump E82 | - |
| Data-quality work on raw order data | Optiver E32-E33; Jump E82; Man AHL E91 (pointer) | - |
| Test trading on own capital before scale | Man AHL E7-E8; Jump E80 ("stress-tested in real markets") | - |
| Cost and fill models from own executions; live comparison of execution styles | AQR E70; CFM E85-E86; Man AHL E90 (pointer) | - |
| Real-time risk, lockdown and reconciliation | Virtu E46-E50 | - |
| Decay and regime monitoring | Man AHL E9; Jump E82; HRT E41; Jane Street E76; Optiver E31; JKP E67 | - |
| Culture that rewards good negative results | Man AHL E11; Two Sigma E19, E21; AHM E63 | - |
| ML as the traded model at short horizons | HRT E39-E42; Jane Street E76; XTX E44; Optiver E27-E31; Jump E81; Citadel Securities E55 | - |
| Shared platform, shared features, orthogonality to existing signals | Two Sigma E23-E24; HRT E43; Optiver E35 | - |

Three patterns stand out.
1. The trading firms (HRT, Jane Street, Jump, Optiver, XTX) all say, unprompted, that market data has very little
   signal, that overfitting is the central risk, and that distributions shift because other traders adapt (E31,
   E41, E76, E81, E82). None of them publishes a multiple-testing rule. Their public discipline is engineering:
   reproducibility, simulation-production parity, data quality, and fast live feedback on their own capital and
   flow.
2. The statistical controls (haircuts, written partitions, trial counts, protocols) are published by the asset
   managers and their academic circle (Man AHL, AQR, Research Affiliates, CFM, Harvey). This program already uses
   that family (Holm, DSR at N, PBO/CSCV, a sealed holdout).
3. The firms that do order-book ML at scale do it with resources this program does not have: tens of thousands of
   GPUs (XTX E45), sequence models over 100,000-event windows (Optiver E31), co-location (Virtu E93; [unverified] for the ML firms), FPGA inference (HRT E95; Optiver E96), years of
   Level 3 data across many correlated instruments (Optiver E31, E33). Two of them started small: XTX on "a couple
   of desktops and an NFS server" (E87), Jane Street on "6 Dells stacked on the floor" (E77). Neither says what
   research process it ran at that size.

---

## 3. What transfers to a one-person retail program on a laptop, and what does not

### 3.1 Transfers (process, not resources)

| Practice (source) | Why it transfers | Program status and gap |
|---|---|---|
| Write down data partition, methodology and expectations before looking (Man AHL E6; AHM E59-E61) | Costs nothing; the main protection a single researcher has | Already done (frozen and hashed pipeline, sealed holdout, REGISTRATION). Extend to the order-book search: labels, horizons, transforms, winsorization and the hyperparameter grid fixed before the first fit (AHM E61) |
| Count every configuration; keep a rejection funnel (Man AHL E5; AHM E59) | One person can keep a ledger; the funnel shows where ideas die | N is counted (538). Add the funnel by stage (proposed, fails CV, fails costs, fails test), which also documents nulls |
| Investigate everything on the agenda; no stop at the first good model (AHM E59) | A stopping rule is a selection rule | Declare the full grid and run all of it |
| Multiple-testing haircut at N (HL E13-E16; HLZ E57) | Arithmetic only | Holm and DSR in use. HL's mapping turns a raw Sharpe into a haircut Sharpe and a profit hurdle at N; at N = 538, marginal Sharpe ratios are cut hardest (E14) |
| Parameter heat maps; an isolated optimum is a red flag (Man AHL board write-up, Harvey E4) | Cheap on a grid already run | Report neighbors of the chosen configuration, not just its score |
| Simplest model first; ML only for structure simple models miss (Man AHL E73; Optiver E30; AHM E62) | It cuts the configuration count and the GPU need | Baseline ladder: weighted mid or imbalance, then linear or logistic, then trees, then a small sequence model |
| Simulation honest relative to production; one code path (Optiver E38; Jump E82) | Matters more for one person, with no second team to catch the gap | Build features from raw events through the same functions used live; order by exchange sequence number, not timestamp (Optiver E33) |
| Data-quality checks on raw book data (Optiver E33; Jump E82) | Defects are large relative to a weak signal | Run checks on the pilot data (flags, gaps, crossed books, sequence breaks) before any label is built |
| Expected live band, and inconsistency rules (Shephard E10; Granger E8) | A predeclared band lets a short live record falsify the model | Declare before any trading: the band and the drawdown that would be "inconsistent with" the claimed Sharpe |
| Lockdown with manual reset, including revenue outside the expected range (Virtu E49, E50) | Software only | Prop platforms enforce loss limits. Add own pre-trade limits, plus a lockdown on P&L outside the band in either direction; an unexpected gain can also mean a bug |
| Reward good negative results (Man AHL E11; Two Sigma E19) | A one-person program decides what it reports | Already the practice (nulls reported in progress.md) |
| Shard feature generation by day; resumable (Optiver E37) | The same idea at laptop scale | Matches the CLAUDE.md compute rules |

### 3.2 Does not transfer, and why

| Practice (source) | Why not | What to do instead |
|---|---|---|
| Deep sequence models on Level 3 data across many correlated instruments (Optiver E30-E31; HRT E42; XTX E44-E45) | 4 GB VRAM and one contract over about 4 months (the USD 100 pilot cap) give far less data and compute than these firms use. Optiver's own case for deep learning rests on L3 queues and many correlated assets (E30-E31) | Small models on MBP-10 features. Deep models only if the pilot data and a larger machine allow, and only after a simple baseline shows structure |
| Alpha at horizons of milliseconds to seconds (Optiver E27, E31; HRT E41) | About tens of milliseconds to Aurora, no co-location, and a back-of-queue fill assumption. Man AHL says very fast effects are "too fast" to capture as alpha even for it, but useful in execution (E72) | Target horizons where tens of milliseconds do not decide the fill. Treat very short predictability first as an execution aid (when to post, when to pull), measured in the pilot's markouts |
| Virtu-style daily P&L (1 losing day in 1,238) (E46-E48) | Market neutral across many instruments, with immediate hedging, co-location (E93) and top fee tiers (E92) | No benchmark value for a single contract; cite only as the monitoring design |
| Test trading on own capital for 2-3 months before scale (Man AHL E7-E8) | V43 and the 2026-10-18 record: no paper trading for now, and no model trades before it passes | After a pass (the lead's decision), the prop evaluation account plays the same role: a mistake-catcher with a predeclared inconsistency rule, not a significance test (E8) |
| Live A/B and bandit comparison of execution styles (CFM E86; Man AHL E90) | Needs many of one's own orders; a 1-lot, low-frequency program fills few orders, and CFM says "conclusions should only be drawn based on sufficient data" (E85) | The pilot's historical fill and markout model, under a conservative queue rule, until there is a live record. Log every order and fill from day one (E91) |
| Independent review by other teams; CERN-style replication (Man AHL E3, E12) | One person | Already substituted: independent fable verification of every verdict number, and adversarial review of declarations |
| Shared feature libraries, orthogonality to the firm's signals (Two Sigma E23-E24) | No signal book | Partial: check new order-book features against the program's own 64-feature library and earlier failed rules, so the search does not re-find a known null |
| Bayesian replication across factor families (JKP E66) | Assumes economically motivated factors with a shared prior; a configuration search over order-book models has no such structure | Keep frequentist N-based control (Holm, DSR, PBO); a Bayesian layer could be added only as a reported extra, never in place of them |
| Proprietary execution history (Man AHL E91) | None exists yet | The pilot purchase is the substitute; live logs, once trading starts, are the only route to it |

---

## 4. Minimum research process for the order-book ML search under V43 (draft for the lead)

This is a worker's draft for the lead to accept, change or reject. It sets no thresholds, selection rules or
verdicts: those are the lead's to pre-register. Each step cites the firm practice it borrows. V43's binding
conditions (frozen and hashed model, features, labels, window, hyperparameters and code before any outcome read;
every configuration in N; purged and embargoed CV on discovery data; one test on data that never selected the
model; Holm, net Sharpe, DSR at N and PBO; costs from the pilot's measured fill and adverse-selection model, never
touched-means-filled; no trading before a pass) are taken as given and not restated as options.

1. Economics gate before any model (AHM E59 research motivation; Optiver E31 low signal-to-noise). From the Part B
   pilot, state per state of the book what a 1-lot passive order earns before prediction: spread captured, minus
   the adverse-selection markout at 1, 10 and 60 s, minus fees. The model's job is then defined as a required edge
   over that baseline. Illustration (a worker's derivation, not from any source): if a trade wins or loses one tick
   with probability p and 1 - p, and the round-trip cost is c ticks, the expected value per trade is
   (2p - 1 - c) ticks, so the break-even p is p* = (1 + c)/2. A "great model" at 52% accuracy (Optiver E31) breaks
   even only when c <= 0.04 ticks. The real payoff of a passive order is not symmetric, so the lead should define
   the edge from the pilot's measured markouts, not from this toy.
2. A written protocol, frozen before the first fit (Man AHL E6; AHM E59-E62): discovery months, CV folds with purge
   and embargo lengths, the untouched test period; labels and horizons; the feature list and every transform and
   winsorization rule (one each, AHM E61); the model ladder and the full hyperparameter grid; the N accounting
   rule; and a commitment to run the whole grid, with no stop at the first good result (AHM E59).
3. Data-quality pass on the pilot data before labels (Optiver E33; Jump E82): ordering by sequence number, gap and
   crossed-book checks, flag inventory, session and roll handling. Defects found are fixed in code, versioned, and
   frozen with the pipeline.
4. Baseline ladder, simplest first (Man AHL E73; Optiver E30; AHM E62): (a) no-model passive baseline (step 1);
   (b) one-feature rules such as weighted mid or queue imbalance; (c) linear or logistic on a small hand-built set;
   (d) gradient-boosted trees; (e) a small sequence model sized to 4 GB of VRAM, only if (c) or (d) show structure
   net of costs in CV. Every rung counts into N. A rung advances only by a margin declared in step 2.
5. Cost-aware labels and evaluation (V43; AQR E70; CFM E85): fills from the frozen back-of-queue rule; P&L net of
   fees and markouts; costs normalized by trading activity (CFM rule 2, E85). Report gross accuracy and net P&L
   side by side, so a model that predicts well but loses to adverse selection shows up as such.
6. Robustness inside discovery data only (Man AHL board write-up, Harvey E4; Man AHL E9): neighbor heat maps around the chosen configuration;
   stability by month and by volatility regime; if every configuration breaks at the same date, record a regime
   change, not a model failure (E9).
7. Statistics at N (program bar; HL E15-E16; Shephard E10): Holm, DSR at N, PBO/CSCV as now, plus, as reported
   extras, the Harvey-Liu haircut Sharpe and profit hurdle at N with an estimated average correlation, and an
   expected live band (claimed Sharpe plus or minus a model-error margin) declared before the test.
8. One test, no iterations (V43; AHM E60; Two Sigma E20): open the untouched period once. A failure ends that
   model; no retuning on the test and no "small fix" rerun. Record the result in the funnel (Man AHL E5).
9. After a pass only (the lead's call, outside this brief): the smallest size on a prop account as a 2-3 month
   mistake-catcher with the inconsistency rule declared in advance (Man AHL E8); pre-trade limits and a lockdown
   with manual reset, including P&L outside the band in either direction (Virtu E49-E50); every order, fill and
   cancel logged to refit the fill model from own executions (AQR E70; CFM E86; Man AHL E91); decay judged against
   the declared band, never by eye (Jump E82).
10. Compute on the laptop (Optiver E37; CLAUDE.md compute rules): shard by day, resumable, nice 10, one GPU job;
    the deep rung of the ladder may need the "more powerful machine" noted in the 2026-10-18 record, which is a
    reason to keep rungs (b) to (d) first.

What the firms' public record cannot supply: none of the firms in scope publishes a holdout length, a fold
design, a multiple-testing threshold or a capital-allocation rule for short-horizon ML. Those parameters have to
come from the program's own pre-registration and the statistical briefs (C2_AFML, C2_StatsRMT), not from firm
practice.

---

## 5. Evidence table

Every quote below was checked as a verbatim substring (whitespace and curly-quote normalized) of the saved file's
text by reports/stage_e28_briefs/work/C2_Firms/C2_Firms_verify.py (94 of 94 pass). Files are under
reports/stage_e28_briefs/pages/C2_Firms/; URLs, fetch times and sha256 are in log.tsv there. "..." joins
separate verbatim segments from the same file. Rows marked POINTER-GRADE are trade-press interviews, not firm
publications.

| ID | Claim | Source | Verbatim quote | Saved file |
|---|---|---|---|---|
| E1 | Board participants include Man AHL CIO, Dimension head, Chief Scientist, ex-CERN analyst; Harvey on the board | Man Group, "Overfitting and Its Impact on the Investor", Man AHL Academic Advisory Board, May 2015 | "These distinguished academics* were joined by Matthew Sargaison, Chief Investment Officer of Man AHL, Nick Granger, Head of Man AHL Dimension Programme, Anthony Ledford, Chief Scientist of Man AHL ... Quantitative Analyst at Man AHL (and previously researcher at CERN) ... Campbell Harvey" | man_overfitting_investor_2015.html |
| E2 | Overfitting definition | same | "Overfitting is when a model describes noise rather than signal. The model may have good performance on the data on which it was tested, but little or no predictive power on new data in the future." | man_overfitting_investor_2015.html |
| E3 | Controls named: range of models, complexity penalty, parameter stability, independent review, rejection rate | same (overview) | "Common methods to deal with overfitting include: using a range of models instead of relying on a single one (model confidence set), penalizing models for complexity, considering model stability under parameter variation, an independent review process, and monitoring the rejection rate of strategies through the review process" | man_overfitting_investor_2015.html |
| E4 | Parameter heat-map test | same (Campbell Harvey, board member, describing "a common approach") | "you modify the model parameters and look at the corresponding ‘heat maps', and assess how performance changes when varying the parameters. If your parameter choice is an isolated point sticking out, then this is a red flag and suggests the parameter choice was a result of data mining." | man_overfitting_investor_2015.html |
| E5 | Rejection-rate monitoring across research, review, test trading | same (Jamil Baz, Man GLG) | "There's the concept of the rejection rate, so basically monitoring how many strategies are proposed originally, and how far they make it through the process. How many don't survive the initial research phase, how many are killed during review, and how many don't make it past test trading - monitoring this rate can be an important asset." | man_overfitting_investor_2015.html |
| E6 | Written-in-advance data partitioning, methodology and expectations at AHL | same (Matthew Sargaison, CIO Man AHL, replying to Harvey on Bailey et al.) | "Yes we have looked at that. The assumption of mean reversion is a bit strong, but we have used the ideas to enforce data partitioning with in-samples and out-of-samples more strongly. You now have to write down the data partitioning and the methodology and expectations." | man_overfitting_investor_2015.html |
| E7 | Strategies first traded with firm capital | same (MS) | "A key message we try to give people is that all strategies are first traded with the firm's capital." | man_overfitting_investor_2015.html |
| E8 | Test trading 2-3 months, not a significance test; catches mistakes; drawdown inconsistency | same (Nick Granger) | "the 2-3 months we would typically test trade a new model is not enough time to demonstrate any kind of statistical significance around the performance. However there have been a number of occasions where this process has caught ‘bad' strategies. This could uncover a mistake in the research or the implementation. A model immediately going into a large drawdown would certainly be a warning sign. For models with high expected Sharpe ratios we can be more certain: for example a 20% drawdown over the first three months would certainly look inconsistent with an assumed SR of 3." | man_overfitting_investor_2015.html |
| E9 | Common break across strategies = regime shift; single break = overfit | same (Anthony Ledford, Chief Scientist, Man AHL) | "If you have a range of strategies, and you see the same breaking point across all of them simultaneously, then a regime shift is likely. If, however, the breaking point only appears for one strategy then it is more likely due to overfitting." | man_overfitting_investor_2015.html |
| E10 | Expected live Sharpe band from model error | same (Neil Shephard) | "If I'm trading with a Sharpe of one, and I think my overfitting/ model error consensus Sharpe is ±0.2, then as a professional I would be surprised if I didn't achieve 0.8 in trading, but I would also be surprised if I surpassed a Sharpe ratio of 1.2." | man_overfitting_investor_2015.html |
| E11 | Reward high-quality negative results; data-access tracking safeguards can be bypassed | same (Campbell Harvey) | "the company tracks the number of times that researchers access the data or run different models. However, researchers can often bypass these safeguards if they want to mine the data. ... it is important to have a culture that rewards research failure given the work was high quality." | man_overfitting_investor_2015.html |
| E12 | CERN practices: artificial datasets, control regions, strict IS/OOS, replication | same | "CERN takes a range of measures, including artificial datasets, control regions, strict enforcement of in-sample and out-of-sample, and a rigorous review processes with other teams replicating the results." | man_overfitting_investor_2015.html |
| E13 | 50% haircut is the industry rule of thumb | Harvey, C. R. and Liu, Y. (2015), "Backtesting", Journal of Portfolio Management, Fall 2015 (Duke-hosted reprint) | "The 50% haircut is only a rule of thumb. ... the 50% haircut is generally considered the industry standard." | harvey_liu_2015_backtesting.pdf |
| E14 | Haircut is nonlinear; top Sharpe ratios lightly penalized, marginal heavily | same | "We argue that it is a serious mistake to use the usual 50% haircut. Our results show that the multiple testing haircut is nonlinear. ... The highest Sharpe ratios are only moderately penalized, while the marginal Sharpe ratios are heavily penalized." | harvey_liu_2015_backtesting.pdf |
| E15 | Method uses Bonferroni, Holm, BHY on p-values; t-ratio 3.0 may not survive multiple tests | same | "Although a t-ratio of 3.0 is highly significant in a single test, it may not be if we take multiple tests into account. ... Bonferroni's method adjusts each p-value equally. ... Holm's method relies on the sequence of p-values" | harvey_liu_2015_backtesting.pdf |
| E16 | Worked example: SR 1.0, 120 months, 100 tests, rho 0.4 -> BHY SR 0.438, haircut 52.0% | same | "suppose that we have an investment strategy that generates an annualized Sharpe ratio of 1.0 over 120 months. ... We allow for 100 tests in multiple testing and assume the average level of correlation is 0.4 among strategy returns. ... autocorrelationcorrected Sharpe ratio of 0.912 ... under BHY, the adjusted, annualized Sharpe ratio is 0.438 and the associated haircut is 52.0%." | harvey_liu_2015_backtesting.pdf |
| E17 | Number of tests needs judgment | same | "Finally, we need some judgment specifying the number of tests." | harvey_liu_2015_backtesting.pdf |
| E18 | Two Sigma: hypotheses then measurement, learning, adjustment across whole process | Two Sigma, "WSJ op-ed by David Siegel: Investing and the scientific method" (Two Sigma insights page) | "ground the entire investment process, from data ingestion to trade execution, on “the formulation of carefully crafted hypotheses, followed by a recurring process of measurement, learning, and adjustment.”" | twosigma_siegel_scientific_method.html |
| E19 | Negative results narrow the search space; falsifiability | Two Sigma, "Why Failure Is an Option—in Science" | "That kind of negative result is valuable: it narrows the search space, saves time, and raises confidence in what remains. ... A hallmark of good science is falsifiability, so a negative outcome still advances understanding." | twosigma_failure_option.html |
| E20 | Hidden out-sample opened once | same (senior quantitative research manager) | "We typically have an in-sample of data that we’re studying, and then an out-sample of data that we’ve hidden from ourselves ... So we’ll build a model and we’ll do all of our ideas and we’ll train it, and there’s one day where you say, okay: I’m ready to open the out-sample." | twosigma_failure_option.html |
| E21 | Named failure modes | same | "Sometimes you have to say, well, it didn’t work. I did something wrong, or I overfit, or the world has changed." | twosigma_failure_option.html |
| E22 | Datasets, back-testing, validation; MVPs before commitment | same | "Two Sigma researchers rely on elements like high-quality datasets, robust back-testing mechanisms, and sound validation techniques to assess experiment results. Similarly, our engineers scope, build, and rigorously evaluate minimum viable products (MVPs) before committing substantial time to an unproven idea" | twosigma_failure_option.html |
| E23 | Shared feature libraries and shared platform | Two Sigma, page on Ben Wellington (Head of Complex Feature Engines) on the Flirting with Models podcast | "Researchers use shared feature libraries and collaborate to build models together, leveraging the data moat and compute power of the shared platform." | twosigma_wellington_feature_engines.html |
| E24 | Orthogonality: correlated features are less valuable | same | "it is relatively easy to create features that are correlated with signals already in use, but those are not usually the most valuable. The goal is to find new predictions that are meaningfully different from what already exists." | twosigma_wellington_feature_engines.html |
| E25 | Test rigorously, avoid post-hoc rationalizing | same | "Researchers need to generate novel hypotheses, but they also need to test those hypotheses rigorously and avoid rationalizing results after the fact. If a feature does not behave as expected, the discipline is to recognize that and move on, rather than force a story around the data." | twosigma_wellington_feature_engines.html |
| E26 | AI amplifies researcher ideas | same | "Ben emphasizes that AI should amplify what makes researchers distinctive, rather than push them toward the same answers." | twosigma_wellington_feature_engines.html |
| E27 | Optiver HFT driven by raw order events; horizons seconds to minutes | Optiver technology blog, K. Rao, "The trading problem: why market data is a deep learning challenge", 6 Oct 2026 | "At Optiver, the main driver of our high-frequency trading strategies is market data: the raw stream of order inserts, cancellations, modifications and trades flowing from exchanges. ... In high-frequency trading, prediction horizons are typically seconds to minutes." | optiver_blog_why-market-data-is-a-deep-learning-challenge.html |
| E28 | Classical feature pipeline: each idea requires dataset regen, retrain, backtest | same | "If you wanted to try a new idea, you had to write the feature, regenerate the dataset, train new models from scratch and then evaluate via a backtest whether the idea adds value." | optiver_blog_why-market-data-is-a-deep-learning-challenge.html |
| E29 | Shift to architecture design, domain expertise kept | same | "It’s not that we want to use deep learning to automate the research process; we still very much make use of domain expertise. The shift is from engineering each feature by hand towards designing architectures best capable of extracting structure from the data directly." | optiver_blog_why-market-data-is-a-deep-learning-challenge.html |
| E30 | L1 weighted mid useful; DL on one snapshot not worth it; L3 queue position informative | same | "A simple weighted-average price is probably one of the most useful signals at this level. Deep learning on a single snapshot like this? Probably not worth it. ... A 200-lot order at the front of the queue therefore contains different information from the same order at the back." | optiver_blog_why-market-data-is-a-deep-learning-challenge.html |
| E31 | Four difficulties: SNR (52% accuracy), non-stationarity, irregular sampling, long sequences | same | "Financial data contains a large amount of noise, and a great model may have an accuracy of 52%. ... The narrow margin between signal and noise also makes overfitting a serious concern. ... A model that works well in one period may behave differently in the next. ... a context window of 100,000 events might cover only a minute of wall-clock time on average" | optiver_blog_why-market-data-is-a-deep-learning-challenge.html |
| E32 | Optiver found vendor L3 data lacking; became BMLL customer then investor | Optiver, "Optiver and BMLL: A new approach to Level 3 market data", 13 May 2025 | "Historical data at a high level of granularity isn’t easy to manage, and we found the datasets offered by vendors lacking. ... Here’s the story of how we became customers of BMLL’s Level 3 historical data and, eventually, investors." | optiver_bmll_level3.html |
| E33 | L3 data defects: 30+ auction flags; venue field names; sequence numbers | Optiver/BMLL case study PDF (download linked from E32 page) | "the data can contain 30+ auction flags that mean very similar things. ... The best bid price, for instance, can be called ‘best bid’, ‘bid1’ or ‘top bid,’ depending on the venue. ... Sequence numbers (which provide the true ordering, rather than just timestamps)" | optiver_bmll_case.pdf |
| E34 | Backtests across many conditions before live | same | "Extensive datasets allow us to backtest strategies across a vast range of market conditions, ensuring they’re sufficiently robust before we deploy them in live trading." | optiver_bmll_case.pdf |
| E35 | Platform goal: shorten idea-to-validated-result loop; reproducibility nonnegotiable | Optiver technology blog, "Research at scale: Orchestrating ML for systematic trading" (R. Hahn talk), 18 Dec 2025 | "We keep one goal in front of everything else: shorten the loop from idea to validated result. ... Reproducibility and traceability are nonnegotiable. If results can’t be recreated, you’re burning cycles, not doing research." | optiver_blog_research-at-scale.html |
| E36 | Research cycle stated | same | "The research cycle is simple to state: form a hypothesis, run experiments, evaluate results, then either refine the hypothesis or translate the results into production decisions." | optiver_blog_research-at-scale.html |
| E37 | Feature generation sharded by day | same | "If feature generation for a single market day takes one hour, about 1,000 trading days will take roughly six weeks of end-to-end runtime. Shard feature generation by day and the runtime drops back down to about an hour" | optiver_blog_research-at-scale.html |
| E38 | Simulation honest relative to production | Optiver technology blog, Daniel B., "Designing for latency and research iteration", 20 Jul 2026 | "Keeping simulation honest relative to production matters here too, so research does not “work” in a way production cannot reproduce." | optiver_blog_designing-for-latency-and-iteration.html |
| E39 | HRT: AI for over a decade; deep learning core | Hudson River Trading, "Machine Learning at HRT" page | "For over a decade, Hudson River Trading has made a deep, sustained commitment to integrating cutting-edge AI research and infrastructure into our trading strategies. Deep learning is core to our trading" | hrt_machine_learning.md |
| E40 | Models drive a significant fraction of HRT trading | same | "accelerate the development of models that drive a significant fraction of HRT’s trading." | hrt_machine_learning.md |
| E41 | Low signal, overfit risk, distribution shift, adversarial adaptation | same | "Market data contains very little signal, making it easy to overfit to noise. Our models must be robust to distributional shifts caused by a rapidly evolving world and adversarial actors who adapt to our behavior and train against our latest models." | hrt_machine_learning.md |
| E42 | HRT data properties and methods (NeurIPS 2023 expo abstract) | NeurIPS 2023 Expo Talk Panel, "Machine Learning and Optimization for Automated Trading at HRT" (abstract page) | "A fundamental challenge is the massive, heterogeneous, unevenly spaced, noisy, and bursty nature of financial datasets. Researchers at HRT use tools like multi-task learning, sequence modeling, and large language models ... HRT employs a variety of optimization techniques spanning from Bayesian optimization to quasi-newton methods to portfolio optimization to make trading decisions." | neurips2023_hrt_expo.html |
| E43 | Common platform, GPU cluster, GPU-to-researcher ratio | HRT ML page | "strong common technological platform ... substantial compute cluster outfitted with modern GPUs ... high GPU-to-researcher ratios" | hrt_machine_learning.md |
| E44 | XTX forecasts for 53,000 instruments; models evolved econometrics->trees->NNs->DL | XTX Markets job posting (Greenhouse), firm boilerplate | "uses state-of-the-art machine learning technology to produce price forecasts for over 53,000 financial instruments ... The models that drive our trading strategies have evolved considerably over the last 10 years, from econometric methods that gave our company its name, to trees, to neural networks, to modern deep learning architectures." | xtx_greenhouse_job.html |
| E45 | XTX compute scale | same | "a growing research cluster currently containing over 25,000 GPUs with more than 1 exabyte of usable storage." | xtx_greenhouse_job.html |
| E46 | Virtu one losing day in 1,238 (2009-2013) | Virtu Financial, Form S-1, March 2014 (SEC EDGAR via Wayback) | "As a result of our real-time risk management strategy and technology, we had only one losing trading day during the period depicted, a total of 1,238 trading days." | virtu_s1_2014.htm |
| E47 | Market-neutral, minimal capital at risk, instantaneous hedging | same | "Our trading is designed to be non-directional, non-speculative and market neutral. ... designed to put minimal capital at risk at any given time by limiting the notional size of our positions. Our strategies are also designed to lock in returns through precise and nearly instantaneous hedging" | virtu_s1_2014.htm |
| E48 | Income from small amounts on millions of trades | same | "comprised of small amounts earned on millions of trades on various exchanges" | virtu_s1_2014.htm |
| E49 | Lockdown when revenue outside preset limits | same | "If our risk management system detects that a trading strategy is generating revenues outside of our preset limits, it will lockdown that strategy and alert management." | virtu_s1_2014.htm |
| E50 | Pre-trade controls, lockdown with manual reset, model limits, continuous monitoring, reconciliation, after-event reviews | Virtu Financial, Form 10-K FY2025 (SEC EDGAR via Wayback) | "Messages that leave our trading environment must first pass through a series of preset risk controls, which are intended to minimize the likelihood of unintended activities by our algorithms. Certain risk controls, when triggered, result in a strategy lockdown, which requires a manual reset in order to restart the strategy. ... Trading strategies are designed to automatically reduce exposures when limits are reached. The models are monitored continuously by the trading team and the risk managers. ... Software developed to support our market making systems performs daily profit and loss and position reconciliations. ... we conduct after event reviews where operational issues are evaluated and risk mitigations are identified and subsequently implemented." | virtu_10k_fy2025.htm |
| E51 | Adverse selection risk factor | same | "We may at times trade with others who have information that may be more accurate or complete than the information we have, and as a result we may accumulate unfavorable positions preceding large price movements in a given instrument." | virtu_10k_fy2025.htm |
| E52 | Competitors range from sole proprietors to sophisticated groups | same | "Our competitors range from sole proprietors with very limited resources to highly sophisticated groups" | virtu_10k_fy2025.htm |
| E53 | Citadel Securities: market problems as scientific questions | Citadel Securities careers, Quantitative Research page (via Wayback) | "Avoiding untested assumptions, we treat market problems as scientific questions. ... When the data supports a hypothesis, we build out large-scale strategies to implement our ideas." | citsec_qr_careers.html |
| E54 | Signals and market impact modelling | same | "they identify market signals with potential predictive power. ... They model the impact of trading on market signals." | citsec_qr_careers.html |
| E55 | FX ML project, management green light | Citadel Securities career perspectives, FX liquidity provision profile (via Wayback) | "Using machine-learning algorithms and statistical models to scrutinize a data set of trades ... The team presented their findings to management, receiving the green light to package and present the concept to additional clients." | citsec_fx_mm.html |
| E56 | Statistics intuition stressed | Citadel Securities, Candidate FAQs: Quantitative Research (via Wayback) | "you’ll be spending a lot of time modeling and forecasting, using statistics as a launching point. We can teach you everything you need to know about finance, but you should already have a robust statistical intuition." | citsec_qr_faq.html |
| E57 | t > 3 hurdle for new factors; not universal | Harvey, C. R., Liu, Y. and Zhu, H. (2016), "...and the Cross-Section of Expected Returns", Review of Financial Studies 29(1) (Duke copy) | "A new factor needs to clear a much higher hurdle, with a t-statistic greater than 3. ... Should a t-statistic of 3.0 be used for every factor proposed in the future? Probably not." | hlz_2016_cross_section.pdf |
| E58 | Most claimed findings likely false; counts of false discoveries | same | "We argue that most claimed research findings in financial economics are likely false. ... of the 296 published significant factors, 158 would be considered false discoveries under Bonferonni, 142 under Holm" | hlz_2016_cross_section.pdf |
| E59 | Protocol: keep track of everything tried; investigate full agenda | Arnott, R., Harvey, C. R. and Markowitz, H. (2018/2019), "A Backtesting Protocol in the Era of Machine Learning", SSRN 3275654 / J. Financial Data Science 1(1); Exhibit 2 (third-party-hosted SSRN copy) | "Did the researcher keep track of all models and variables that were tried (both successful and unsuccessful) and are the researchers aware of the multiple-testing issue? ... Did the researchers investigate all variables set out in the research agenda or did they cut the research as soon as they found a good model?" | arnott_harvey_markowitz_2018_protocol.pdf |
| E60 | Protocol: OOS only in live trading; no OOS iterations; OOS must include costs | same, Exhibit 2 | "Are the researchers aware that true out-of-sample tests are only possible in live trading? ... Are steps in place to eliminate the risk of out-of-sample “iterations” (i.e., an in-sample model that is later modified to fit out-of-sample data)? ... Is the out-of-sample analysis representative of live trading? For example, are trading costs and data revisions taken into account?" | arnott_harvey_markowitz_2018_protocol.pdf |
| E61 | Protocol: transformations, winsorization chosen in advance | same, Exhibit 2 | "Do the data transformations, such as scaling, make sense? Were they selected in advance? ... Was the winsorization rule chosen before the research was started? Was only one winsorization rule tried (as opposed to many)?" | arnott_harvey_markowitz_2018_protocol.pdf |
| E62 | Protocol: minimize tweaking live model; simplest specification; interpret ML | same, Exhibit 2 | "Do researchers take steps to minimize the tweaking of a live model? ... Have the researchers taken steps to produce the simplest practicable model specification? ... Is an attempt made to interpret the predictions of the machine learning model rather than using it as a black box?" | arnott_harvey_markowitz_2018_protocol.pdf |
| E63 | Protocol: culture; most tests fail | same, Exhibit 2 | "Does the research culture reward quality of the science rather than finding the winning strategy? ... Do the researchers and management understand that most tests will fail?" | arnott_harvey_markowitz_2018_protocol.pdf |
| E64 | k-fold tuning of 10 hyperparameters on 50 years is a terrible idea; OOS not really OOS | same, body text | "[T]uning 10 different hyperparameters using k-fold cross-validation is a terrible idea if you are trying to predict returns with 50 years of data (it might be okay if you had millions of years of data). ... Acknowledge out of sample is not really out of sample. Researchers have lived through the hold-out sample" | arnott_harvey_markowitz_2018_protocol.pdf |
| E65 | Complexity widens backtest-live slippage | same, body text | "The greater the complexity, and the greater the reliance on nonintuitive relationships, the greater the likely slippage between backtest simulations and live results." | arnott_harvey_markowitz_2018_protocol.pdf |
| E66 | JKP (AQR authors): factors replicate; Bayesian; strengthened by number of factors | Jensen, T. I., Kelly, B. and Pedersen, L. H. (2023), "Is There a Replication Crisis in Finance?", Journal of Finance 78(5) (CBS publisher version) | "We develop and estimate a Bayesian model of factor replication that leads to different conclusions. The majority of asset pricing factors (i) can be replicated; (ii) can be clustered into 13 themes ... (iii) work out-of-sample in a new large data set covering 93 countries; and (iv) have evidence that is strengthened (not weakened) by the large number of observed factors." | jkp_2023_replication_crisis.pdf |
| E67 | McLean-Pontiff decay figures as quoted by JKP | same | "are 26% lower out-of-sample and 58% lower post-publication." | jkp_2023_replication_crisis.pdf |
| E68 | AQR (Israel, Kelly, Moskowitz) ML in asset management: unique challenges; theory and expertise [abstract only] | AQR, "Can Machines 'Learn' Finance?", Journal of Investment Management 2020 (AQR abstract page; full text not fetched) | "Machine learning for asset management faces a unique set of challenges that differ markedly from other domains where machine learning has excelled. ... emphasize the importance of economic theory and human expertise for achieving success through financial machine learning." | aqr_can_machines_learn_finance.html |
| E69 | Small data, weak SNR, structural instability | Kelly, B. (Yale, AQR) and Xiu, D. (2023), "Financial Machine Learning", NBER WP 31502 | "many foundational questions in finance are frustrated by the decidedly “small data” reality of economic time series. ... Second, financial research often faces weak signal-to-noise ratios. ... Structural instability makes finance an especially complex learning domain and compounds the challenges of small data and low signal-to-noise ratios." | kelly_xiu_2023_financial_ml_nber.pdf |
| E70 | AQR cost model from live execution data; participation rate drives cost | Israel, R., Jiang, S. and Ross, A. (AQR) (2017), "Craftsmanship Alpha: An Application to Style Investing", SSRN 3034472 (third-party-hosted copy) | "Using real world execution data, Frazzini, Israel, and Moskowitz (2012) observe that the greater the participation rate (shares traded/market trading volume) the costlier it is to trade. ... trading 2% of a stock’s daily volume results in roughly 17 basis points (bps) of market impact; in contrast, trading 6% costs roughly 28 bps per dollar traded on average." | aqr_craftsmanship_alpha_2017.pdf |
| E71 | Man AHL: ML useful where data abundant; used in faster strategies and execution/smart order routing | Man Institute, "An Introduction to Machine Learning" (Man AHL) | "The experience of Man AHL over the last decade is that AI, and in particular machine learning (‘ML’), can play beneficial roles within investment management, especially in applications where there is a relative abundance of data. For example, our research and development in faster speed (e.g. daily and intra-day) systematic investment strategies, together with algorithms for trade execution and smart order-routing, have all made extensive use" | man_intro_machine_learning.html |
| E72 | Man AHL: very fast effects too fast for alpha at scale, valuable in execution | same | "Faster signals than that certainly exhibit greater non-linear structure, however such effects are hard to capture as alpha in the client-scale funds typical of large systematic managers like us. In a nutshell, they are just too fast. However, when applied in trade execution, such effects may offer significant advantage in reducing transaction costs" | man_intro_machine_learning.html |
| E73 | Man AHL: ML needs ample representative data and effects simple models miss | same | "For ML to have an impact, you need a few things: ample amounts of representative data, and effects that are not easily described using simpler models. ... you are just undertaking needless and pointless complications if you use a ML model when a simpler model will do." | man_intro_machine_learning.html |
| E74 | Man AHL: Bayesian ML for noisy data | same | "For ‘noisy’ data, a suite of modelling techniques that goes by the name Bayesian Machine Learning is particularly robust at dealing with the statistical uncertainty implicit with such noise." | man_intro_machine_learning.html |
| E75 | Man AHL trading ML systems in client multi-strategy portfolio since early 2014 | Man Institute, "The Rise of Machine Learning" | "At Man AHL (‘AHL’) we have been successfully trading Machine Learning based systems in our multi-strategy client portfolio since early 2014" | man_rise_of_ml.html |
| E76 | Jane Street: deep learning future; data mostly noise; regime-y; own actions influence data | Jane Street, "Machine Learning at Jane Street" page | "We believe deep learning is the future of quantitative trading. ... Financial markets produce a torrent of data, mostly noise. ... Market data is “regime-y,” in that it undergoes frequent structural changes ... our own actions influence the data we’re trying to model" | janestreet_machine_learning.html |
| E77 | Jane Street compute history | same | "Twenty years ago, our "cluster" was just 6 Dells stacked on the floor of our office. Today, come tour our new Texas datacenter: 4,032 GPUs, liquid cooled." | janestreet_machine_learning.html |
| E78 | Jane Street: rigorous and pragmatic; ML vs domain expertise vs pen-and-paper; rapid feedback; models since 2000 | Jane Street, "What we do" overview | "Our style is both rigorous and pragmatic. Depending on the problem, we might draw on large-scale machine learning, domain expertise, or pen-and-paper mathematics. ... Trading serves as a unique, rapid-feedback platform for ML experimentation ... we’ve leveraged a variety of modeling techniques since our founding in 2000. The depth of our reliance on these models has grown dramatically in the last few years." | janestreet_what_we_do.html |
| E79 | Jane Street: in-house software incl. risk systems; porous team lines | same | "We build almost all of our software in-house, including our critical trading and risk management systems ... The lines between trading, research, and technology are intentionally porous, both at the organizational and individual level." | janestreet_what_we_do.html |
| E80 | Jump: strategies grounded in research, stress-tested in real markets | Jump Trading home page | "Every trading strategy is grounded in research, stress-tested in real markets, and engineered to scale." | jump_home.html |
| E81 | Jump: low SNR; adaptable modeling, refined data, rigorous signal validation | Jump Trading, AI/ML page | "Our core focus is finding alpha in high-volume, low-latency environments with low signal-to-noise ratio. This demands an adaptable modeling process, carefully refined data, rigorous signal validation, and seamless execution." | jump_ai-ml.html |
| E82 | Jump: edge decays; adverse selection; fooling yourself; notebook vs real data | same | "Any single source of edge erodes over time as the market grows more efficient. Adapt or lose. ... Every time you trade, it’s because someone thought you were wrong. ... It’s incredibly easy to fool yourself. Data not pristine? You’ll fit the noise, but not the signal. ... It’s easy to demo your idea in a notebook. What’s valuable is making it 99.9% accurate on real data, parsed on the fly." | jump_ai-ml.html |
| E83 | Jump team structure: embedded and central ML | same | "Some of our ML and AI experts sit directly with trading teams to specialize in specific markets. Others work centrally to build scalable systems" | jump_ai-ml.html |
| E84 | CFM: framework to quantify in-sample PnL overfitting and discount | Rej, A., Seager, P. and Bouchaud, J.-P. (Capital Fund Management) (2019), "How should you discount your backtest PnL?", arXiv:1902.01802 | "In this article we propose a simple framework that allows one to model and quantify in-sample PnL overfitting. This allows us to compute the factor appropriate for discounting PnLs of in-sample investment strategies." | cfm_rej_seager_bouchaud_2019_discount_backtest.pdf |
| E85 | CFM execution: implementation shortfall metric; rules: benchmark, normalize by activity, need time | CFM Technical Note, "Improving Trade Execution Systematically", May 2018 | "CFM uses the metric known as implementation shortfall (IS). ... Rule #1: Use benchmarks for your expectations. ... Rule #2: Compare costs relative to trading activity. ... Rule #3: You need time to learn. The performance of the different strategies has to be followed over time, and conclusions should only be drawn based on sufficient data." | cfm_2018_improving_execution.pdf |
| E86 | CFM: live competing execution strategies, bandit framing, own experience only | same | "Thus you will only have your own experience, your own losses and gains to learn from. ... we will show the actual cost savings generated by CFM’s execution strategies competing on the UK equity market ... In early 2014 the UK market was executed using two competing strategies" | cfm_2018_improving_execution.pdf |
| E87 | XTX started on two desktops and an NFS server | XTX Tech Blog, "TernFS: an exabyte scale, multi-region distributed filesystem" | "The firm started out with a couple of desktops and an NFS server, and 10 years later ended up with tens of thousands of high-end GPUs, hundreds of thousands of CPUs, and hundreds of petabytes of storage." | xtx_ternfs.html |
| E88 | XTX storage spans raw market data to GPU job data | XTX Tech Blog, TernFS | "going from relatively 'cold' storage of raw market data to short-lived random-access data used to communicate between GPU jobs running on our cluster." | xtx_ternfs.html |
| E89 | POINTER-GRADE (trade-press interview): fewer than 1 in 10 ideas pass test trading at AHL; record reject rate | Risk.net, "Quant hedge fund of the year: Man AHL", Risk Awards 2018 (journalist quoting M. Sargaison) | "At the same time, fewer than one in 10 ideas make it past test trading. “Recently, we’ve had a higher internal reject rate for research than at any time in our history, and I feel good about that,” he says." | risknet_man_ahl_2018.html |
| E90 | POINTER-GRADE (trade press): ML order router allocates trades to routes by achieved execution | same | "Making the call on which route each trade takes is a machine learning algorithm launched by AHL this year ... The better the execution achieved by each route, the more trades get sent that way." | risknet_man_ahl_2018.html |
| E91 | POINTER-GRADE (trade press): AHL records every market interaction | same | "What we are doing is interacting with the market, and we’ve been meticulous in recording every point at which we’ve done that" | risknet_man_ahl_2018.html |
| E92 | Virtu fee tiers | Virtu S-1, March 2014 | "top tiers of favorable brokerage, clearing and exchange fees for venues that provide tiered pricing structures" | virtu_s1_2014.htm |
| E93 | Virtu co-location network | Virtu 10-K FY2025 | "to exchanges and other electronic venues through a network of co-location facilities around the world" | virtu_10k_fy2025.htm |
| E94 | Profit hurdle function: required mean return at given significance, tests, correlation | Harvey and Liu (2015), "Backtesting" | "The Matlab function Profit_Hurdle lets the user calculate the required mean return for a strategy at a given level of significance. ... The fourth input is the number of tests assumed. Lastly, the fifth input is the assumed average level of correlation among strategy returns." | harvey_liu_2015_backtesting.pdf |
| E95 | HRT: FPGA inference devices (job posting) | HRT, machine learning page (HAIL inference research engineer posting) | "novel inference devices like ASICs and FPGAs (both off-the-shelf and in-house)" | hrt_machine_learning.md |
| E96 | Optiver: production latency may require FPGA inference hardware | Optiver blog, "Why market data is a deep learning challenge" | "which may require custom inference hardware designed with FPGA engineers. In high-frequency trading, every nanosecond matters." | optiver_blog_why-market-data-is-a-deep-learning-challenge.html |

---

## 6. Failures, gaps and negative evidence

Negative evidence (searched for, not found in public firm material):
- No firm in scope publishes a holdout length, a cross-validation design, a multiple-testing threshold, a
  capital-allocation formula for new models, or a quantitative decay rule. The closest are Man AHL's written
  partition rule (E6), its 2-3 month test-trading window (E8), and Virtu's lockdown rules (E49-E50).
- The HFT and market-making firms (HRT, Jane Street, Jump, Optiver, XTX, Citadel Securities) publish nothing on
  multiple testing. Their public statements are about low signal, overfitting risk, non-stationarity and
  engineering discipline.
- Two Sigma: nothing public found on multiple testing, staged deployment or capital allocation.

Fetch failures and routes taken (all logged in pages/C2_Firms/log.tsv):
- hudsonrivertrading.com: curl 403 and `scrapling extract get` failed. robots.txt was read first (it allows general
  crawling except /wp-json/ and named AI bots; decision logged), then `scrapling extract fetch` succeeded.
- sec.gov: 403 to curl. Virtu's S-1 (2014) and 10-K (FY2025) came from Wayback raw (id_) captures of the EDGAR
  URLs. The first Wayback attempt saved a frame page, which was deleted (noted in the log).
- citadelsecurities.com: 403 to curl; the three pages used are Wayback raw captures.
- Not obtained in full text: AQR "Can Machines 'Learn' Finance?" (SSRN blocked per READER_RULES; JOIM needs a
  login), so only its abstract is cited (E68); Frazzini, Israel and Moskowitz "Trading Costs" (SSRN), so its figures
  are cited only as quoted in Israel, Jiang and Ross (E70); Suhonen, Lennkh and Perez (2017) on 215 bank
  alternative-beta strategies (a reported median 73% fall in Sharpe from backtest to live): secondary summaries
  only, [unverified], not used in the text.
- Third-party hosting: the Arnott-Harvey-Markowitz and Craftsmanship Alpha PDFs are SSRN working-paper copies on
  smallake.kr. The text carries SSRN's "Electronic copy available" footer, but it was not cross-checked against the
  published journal versions.
- Paywalled or not fetched: Risk.net (one profile was readable and is cited as POINTER-GRADE only, E89-E91), a 2016
  Bloomberg piece on Man AHL's ML (not used), The Pragmatic Engineer's Optiver profile (subscription), the Optiver
  Kaggle competition pages, XTX's Companies House accounts, and the SEBI order on Jane Street.
- Firms not researched in this pass: Renaissance Technologies, D. E. Shaw, DRW, IMC, Tower Research, Winton.

Budget: WebSearch 21 of 60 calls, with no budget notice received. No Firecrawl calls. Scrapling was used once
(HRT), after the robots check. No market data, keys, Databento, broker or TopstepX access.

Completion: sections 1 to 6 are written. The section 4 process is a draft for the lead's decision. It sets no
thresholds or selection rules.

## Corrections after review (Stage E.28, MathReviewer G6)

- MG6-15: E4 speaker changed from "same (NS)" to Campbell Harvey (board member, "a common approach"); the section 1.1 sentence, the section 2 table row, the section 3 row and the section 4 step 6 cite now read "Man AHL board write-up (Harvey) E4", with the write-up's own summary item "model stability under parameter variation" (E3) in the section 2 row. The "Man AHL E4" practice claim is no longer made.
- MG6-16: "co-location" cites Virtu E93 and is marked [unverified] for the ML firms; "FPGA inference" cites new rows E95 (HRT) and E96 (Optiver). The two quotes were checked by grep against the saved pages (hrt_machine_learning.md, optiver_blog_why-market-data-is-a-deep-learning-challenge.html.txt); they are not in C2_Firms_verify.py, so the "94 of 94" statement in section 5 covers E1-E94 only.
- MG6-17: the Kaggle sentence now says Kaggle's own pages were not fetched and Optiver's saved closing-cross post is not used as evidence; the pointer stays [unverified beyond search snippets].
- MG6-18: "AHL's CIO" changed to "AHL's co-CEO (its CIO at the time of E1)".
- MG6-19: E32 quote extended with the "customers ... and, eventually, investors" sentence (the saved text splits it across lines; E32 is therefore also outside the earlier 94-of-94 script check in its extended form).
- MG6-20: E78 quote extended with "The depth of our reliance on these models has grown dramatically in the last few years."
- MG6-21: E9 speaker set to Anthony Ledford, Chief Scientist, Man AHL.
