# Smart Money: The Forecasting Ability of CFTC Large Traders in Agricultural Futures Markets

**Dwight R. Sanders, Scott H. Irwin, and Robert P. Merrin**

The forecasting content of the Commodity Futures Trading Commission’s Commitments 
of Traders (COT) report is investigated. Bivariate Granger causality tests show very little 
evidence that traders’ positions are useful in forecasting (leading) returns in 10 agricultural futures markets. However, there is substantial evidence that traders respond to price 
changes. In particular, noncommercial traders display a tendency for trend following. The 
other trader classifications display mixed styles, perhaps indicating those trader categories capture a variety of traders. The results generally do not support use of the COT data 
in predicting price movements in agricultural futures markets.

*Key words:* agricultural futures markets, commitments of traders, forecasting, prices

## Introduction

The Commodity Futures Trading Commission’s (CFTC) Commitments of Traders (COT) 
report highlights the aggregate futures positions held by reporting (large) traders, both 
commercial (hedgers) and noncommercial (speculators). Futures traders often view these data 
as akin to insider information about the positions of “smart money” traders and tout its 
usefulness in predicting price movements (e.g., Upperman, 2006; Briese, 2008). Discussion 
of trader positions has now become routine among market analysts who search for meaning 
within the numbers. This focus contrasts with the CFTC’s intent that the report function as 
one component of its market monitoring and surveillance system (CFTC, 2008).

Academic studies in recent years show commodity futures portfolios can generate returns 
comparable to equities (e.g., Gorton and Rouwenhorst, 2006). As a result, the financial 
industry has developed products allowing institutions to invest in commodities through longonly index funds as well as easily traded commodities through exchange-traded funds and 
other structured products. The rapid growth in these nontraditional futures market participants 
has led to concerns that such trading has altered the price discovery process in traditional 
agricultural commodity markets (Morrison, 2004). Indeed, Domanski and Heath (2007) argue 
that the “financialisation” of commodity markets warrants additional study on the strategies, 
motivation, and the potential market impact of nontraditional traders.

Dwight R. Sanders is associate professor, Department of Agribusiness Economics, Southern Illinois University, Carbondale; Scott H. Irwin 
is Laurence J. Norton Chair of Agricultural Marketing, Department of Agricultural and Consumer Economics, University of Illinois at 
Urbana-Champaign; and Robert P. Merrin is Ph.D. candidate, Department of Finance, Universiteit Maastricht, the Netherlands. Funding 
support from the Aurene T. Norton Trust is gratefully acknowledged.

Review coordinated by George C. Davis.

---

A limited number of studies examine the ability of large trader positions to predict returns 
1
in agricultural futures markets. Kahn (<sup>1</sup>986) uses COT observations to mimic the positions 
of noncommercial traders in corn, soybeans, wheat, and oats futures markets. He finds that 
following noncommercial positions (upon release of the COT reports) does not generate 
statistically significant profits. Examining price behavior during the “market scandal” 
associated with the May 1925 wheat futures contract at the Chicago Board of Trade, Petzel 
(1981) reports that lagged position changes for three groups of speculators are not significantly related to price changes for the contract. In a 2001 study, Wang develops “sentiment” 
indicators based on COT positions in six actively traded agricultural futures markets and finds 
positions of noncommercial traders forecast price continuations, and positions of commercial 
traders forecast price reversals. More recently, Wang (2003) investigates a trading strategy 
based on large trader position changes in corn, soybeans, wheat, and sugar, and reports 
significant profits following noncommercial positions and reversing commercial positions. 
Using causal inference algorithms, Bryant, Bessler, and Haigh (2006) do not find evidence of 
trader positions from COT reports predicting returns in corn and live cattle futures markets. 
Finally, Gorton, Hayashi, and Rouwenhorst (2007) examine a large cross-section of commodity futures markets and find only a few markets with significant correlations between returns 
and lagged commercial positions.

The mixed findings in prior research may be due to several factors, including different 
measures of position size and varying sample periods. For example, Wang (2001) utilizes a 
sentiment index that normalizes positions by the previous three-year range of positions, while 
Gorton, Hayashi, and Rouwenhorst (2007) normalize positions by the current level of open 
interest. The disparity of results suggests empirical findings may be sensitive to alternative 
position measures.

The goal of this research is to explicitly examine the usefulness of COT data in predicting 
agricultural futures returns. In light of the evolving nature of speculative participants in 
futures markets and the attention paid in the industry to the positions held by trader groups, it 
is important to directly address the usefulness of these data in a forecasting framework. This 
study uses bivariate Granger causality to investigate lead-lag dynamics between trader 
positions and agricultural futures returns over a relatively long time period, 1995 through 
2006. Weekly data on 10 grain and livestock futures markets are examined. Importantly, the 
sensitivity of estimation results to several position measures is tested. A variation of the basic 
Granger causality test is used to test for longer-horizon relationships between trader positions 
and returns. A Cumby-Modest test is employed to determine whether trader positions impact 
returns when extreme market positions are reached. Trading styles are also investigated via 
causality tests from returns to positions, revealing if CFTC traders are trend followers or 
adhere to value- or contrarian-type strategies.

The research results will be of interest to academics and market participants alike. 
Academic researchers will gain a more thorough understanding of relationships between agricultural futures price movements and positions of different types of traders. Traders, analysts, 
and other market participants will benefit from a rigorous analysis of the COT data. For

<sup>1</sup>
A large literature has investigated “hedging pressure” effects and/or “risk premiums” using COT data (e.g., Chang, 1985). However, most 
papers in this literature estimate the *contemporaneous* correlation between futures returns and positions. A contemporaneous correlation does 
not necessarily imply a causal relationship, as it may simply reflect the response of traders to futures price movements and/or the common 
reaction of returns and positions to fundamental supply and demand factors (Petzel, 1981). One study (Yang, Bessler, and Fung, 2004) tests 
whether a co-integrating relationship exists between changes in total open interest and subsequent returns for 11 storable and nonstorable 
futures markets. No evidence is found whereby open interest drives futures returns.

---

example, participants may find that the COT data provide little insight as to future price 
direction, in which case their efforts may be more efficiently directed toward alternative 
approaches to predicting market trends.

## Commitments of Traders Reports

The COT report provides a breakdown of each Tuesday’s open interest for futures markets in 
which 20 or more traders hold positions equal to or above the reporting levels established by 
2
the CFTC. The weekly reports for *Futures-Only Commitments of Traders* and for *Futures-*
*and-Options-Combined Commitments of Traders* are released every Friday at 3:30 p.m. Eastern Standard Time.

Reports are available in both a short and long format. The short report shows open interest 
(aggregated across all outstanding contracts) by reportable and nonreportable positions. For 
reportable positions, additional data are provided for commercial and noncommercial holdings, spreading, changes from the previous report, percentage of open interest by category, 
and number of traders. The long report, in addition to the information in the short report, also 
groups the data by crop year, where appropriate, and shows the concentration of positions 
held by the largest four and eight traders.

Starting in early 2007, as a response to complaints by traditional traders about long-only 
index traders (CFTC, 2006a,b), the CFTC released supplemental reports that also break out 
the positions of index traders for agricultural markets. The release of this report offers 
historical data starting in 2006, and it largely confirms the presupposition that index traders 
are almost exclusively long-only traders. For example, in the corn futures market, index 
traders are 96% long and hold roughly 12% of the open interest. As expected, index traders 
seldom alter positions other than to roll contract months, resulting in virtually no variation in 
their directional position. Therefore, we focus here on the combined futures and deltaadjusted options positions held within the traditional CFTC classifications: commercial, noncommercial, and nonreporting traders.

Using the information in the short report, noncommercial open interest is divided into 
long, short, and spreading, whereas commercial and nonreporting open interest is simply 
divided into long or short. The following relation explains how the market’s total open 
interest (TOI) is disaggregated:

(1)

$$
\underbrace{[NCL+NCS+2(NCSP)]+[CL+CS]}_{Reporting}+\underbrace{[NRL+NRS]}_{Nonreporing}=2(TOI)
$$

where *NCL*, *NCS*, and *NCSP* are noncommercial long, short, and spreading positions, 
respectively. *CL* (*CS*) represent commercial long (short) positions, and *NRL* (*NRS*) are long 
(short) positions held by nonreporting traders. Reporting and nonreporting positions must 
sum to the market’s total open interest (*TOI*), and the number of longs must equal the number 
of short positions.

Data on trader positions are collected for each Tuesday from 1995 through 2006, resulting 
in 616 observations. The COT data reflect traders’ positions as of Tuesday’s close, although 
for much of the sample these data are not released until Friday. Following previous studies 
(e.g., Bryant, Bessler, and Haigh, 2006), a matching set of log-relative futures returns,

<sup>2</sup>
 See Hieronymus (1971), McDonald and Freund (1983), and Fenton and Martinaitas (2005) for extensive discussions of the history and 
evolution of the COT report.

---

*R*<sub>t</sub> = ln( *p*<sub>t</sub>/ *p*<sub>t</sub><sub>−1</sub>), is calculated for nearby futures using Tuesday-to-Tuesday settlement prices. 
We make no assumptions about how or why traders’ positions might change over the course 
of a week, and the data are organized whereby the collected prices are coincidental with the 
reported positions. Therefore, the empirical tests are purely for predictive value from the time 
the positions are actually held, and they are not conditioned on the public release date. Failure 
to find predictive value under this test design most certainly precludes the positions from 
having forecasting value after a delayed release.

$$
R_{t}=\ln(p_{t}/p_{t-1})
$$

## Position Indicators

Prior research results have varied, potentially due to alternative measures of position size. De 
Roon, Nijman, and Veld (2000) use the “percent net long” (PNL), which measures the net 
position of the average trader in a CFTC classification. The PNL is calculated as long minus 
the short positions divided by their sum for each trader classification. For instance, the PNL 
for the reporting noncommercials is defined as follows:

(2)

$$
\mathrm{Noncommerical~PNL}_{t}=\frac{\mathrm{NCL}_{t}-\mathrm{NCS}_{t}}{\mathrm{NCL}_{t}+\mathrm{NCS}_{t}}
$$

The PNL for each CFTC classification represents the net position held by the group normalized by its total size.

Wang’s (2001) sentiment index, *SI*<sub>i,t</sub> is also calculated for each market and classification, *i*
(noncommercial, commercial, nonreporting). Wang defines the net long position for each 
trader category, *S*<sub>i,t</sub>, as the total long positions minus the total short positions for that category 
at time *t*. Wang then defines his sentiment index by normalizing the net long position by its 
range over the prior three years:

$$
S I_{i,t}
$$

$$
S_{i,t},
$$

(3)

$$
SI_{i,t}=\frac{S_{i,t}-Min(S_{i,t})}{Max(S_{i,t})-Min(S_{i,t})}
$$

Note that each of the minimum and maximum functions is applied to the prior three years. 
Wang’s sentiment index is essentially an oscillator bound in the range (0, 1). A value of 0 
indicates the net long position is at a three-year low, while a value of 1 occurs when the net 
long position or trader sentiment is at a three-year high.

Not surprisingly, the correlations between the PNL and SI measures are very high. For 
example, using the corn futures positions, the simple correlation coefficients between *PNL*
and *SI* are 0.97, 0.95, and 0.88 for noncommercial, commercial, and nonreporting positions, 
respectively. Other potential position measures are also examined—such as simple net 
position, position changes, and using alternative look-back periods (other than three years) for 
calculating the SI. Again, the correlations are generally very high (around 0.90) across all of 
the alternative position measures.

The following empirical tests are conducted using both the PNL and SI measures of position size. The results do not differ materially based on the position measure; consequently, 
our focus is on the PNL measure. In the next section, we discuss how the PNL position 
measure is used to uncover statistical lead-lag relationships within the data using Granger 
causality (results using the SI measure are available from the authors upon request).

---

## Empirical Methods

Hamilton (1994) suggests the direct, or bivariate, Granger test for examining the lead-lag or 
“causal” relationship between two series. Granger causality is a standard linear technique for 
determining whether one time series is useful in forecasting another. In our case, the two 
time-series variables used are futures returns and trader positions (PNL). The following 
models are estimated:

(4)

$$
R_{t}=\alpha_{t}+\sum_{i=1}^{m}\gamma_{i}R_{t-i}+\sum_{j=1}^{n}\beta_{j}P N L_{t-j}+\varepsilon_{t},
$$

and

$$
P N L_{t}=\phi_{t}+\sum_{i=1}^{n}\lambda_{i}P N L_{t-i}+\sum_{j=1}^{m}\theta_{j}R_{t-j}+\omega_{t}.
$$

(5)

Each model is estimated for lag lengths of 1 to 12 weeks, and the lag structure of the most 
efficient model is selected by minimizing the Akaike information criterion (AIC). The models 
are estimated with OLS. If the residuals demonstrate serial correlation (Breusch-Godfrey 
Lagrange multiplier test), additional lags of the dependent variable are added until the null of 
no serial correlation cannot be rejected. We test for heteroskedasticity (White test), and robust 
standard errors are used to correct the standard errors when necessary.

From equation (4), a number of testable hypotheses emerge. In particular, the null 
hypothesis of interest is that traders’ positions (PNL) cannot be used to predict (do not lead) 
market returns (H₀: β<sub>j</sub> = 0 " *j*). A rejection of this null hypothesis would provide direct evidence trader positions are indeed useful for forecasting market returns. In order to gauge the 
aggregate impact of trader positions, we also test the null hypothesis that 
*n*

$$
\beta_{j}=0\forall j)
$$

$$
\sum_{j=1}^{n}\beta_{j}=0,
$$

which will reveal the cumulative directional impact of traders’ positions on returns (if any). 
Finally, the full rationality (efficiency) in futures returns is tested ( γ<sub>ij</sub>==" β 0, *ij*) as well as 
autocorrelation in returns ( γ<sub>i</sub>=" 0 *i*).

$$
\left(\gamma_{i}=\beta_{j}=0\forall i,j\right)
$$

$$
(\gamma_{i}=0\forall i)
$$

In equation (5) there are two null hypothesis of interest. First, do returns lead traders’ 
positions,  θ<sub>j</sub>=" 0? *j* Second, what is the cumulative impact of past returns on traders’ 
positions, 
n

$$
\sum_{j=1}^{n}\theta_{j}=0?
$$

$$
\theta_{j}=0\forall j?
$$

If we reject θ<sub>j</sub> = 0 " *j* and find

$$
\theta_{j}=0\ \forall j
$$

$$
\sum_{j=1}^{n}\theta_{j}>0,
$$

then the trader group may be classified as trend followers or “positive feedback” traders 
because they increase their long position after prices increase and vice versa. Conversely, 
traders who buck the trend may be called “negative feedback” traders or contrarians, where  
n

$$
\theta_{j}\neq0\forall j\text{and}\sum_{j=1}^{n}\theta_{j}<0.
$$

These traders tend to buy after price declines and sell after price rallies, essentially a countertrend strategy or “value” strategy. The tests outlined for equations (4) and (5) provide the 
basis for the empirical tests which yield important insight with regard to the usefulness of the

---

COT data in predicting agricultural futures price movements and the trading “style” of each 
trader group.

The previous Granger causality tests are designed to detect the relationship, if any, 
between weekly positions and returns. Such tests may have low power to detect relationships 
over longer horizons (Summers, 1986). For example, trader positions or speculative monies 
may flow in “waves” that build slowly—pushing prices higher—and then fade slowly. In this 
scenario, horizons longer than a week may be necessary to capture the predictive component 
of large trader positions. Thus, we implement the long-horizon regression “fads” models of 
Jegadeesh (1991):

$$
R_{t}=\alpha_{t}+\sum_{i=1}^{m}\gamma_{i}R_{t-i}+\beta\sum_{j=1}^{n}\frac{P N L_{t-j}}{n}+\varepsilon_{t}.
$$

(6)

In essence, equation (6) is analogous to (5) except that instead of PNL entering the model at 
alternative lags, it enters the model as a moving average calculated over the most recent *n*
observations. Jegadeesh shows that letting the independent variable enter the equation as an 
average over the most recent *n* observations provides the highest power against a fads-type 
alternative hypothesis using standard OLS estimation and testing procedures. If the estimated 
β is positive (negative), then it indicates a fads-style model where prices tend to increase 
(decrease) slowly over a relatively long time period after widespread buying. The “fads” 
stylization captured in (6) is consistent with the popular notion of speculative pressures 
creating a “bubble” in commodity prices.

It is also possible that traders’ positions have a market impact only when they reach 
extreme levels. Again, this would be somewhat consistent with an investing fad or bubble that 
may reverse when the market reaches a “frenzy.” To test this assertion, we follow the method 
proposed by Sanders, Boris, and Manfredo (2004) by defining an extreme position as the 
upper and lower 20th percentile of the prior three-year range. Let the variable *LO* = 1 if PNL 
is in the lower 20th percentile of its range from the prior three years, and = 0 otherwise. 
Similarly, the variable *HI* = 1 if PNL is in the upper 20th percentile of its three-year range, 
and = 0 otherwise.

The following OLS regression is then used to test the impact of extreme positions on 
market returns:

$$
R_{t}=\alpha_{0}+\alpha_{1}H I_{t-1}+\alpha_{2}L O_{t-1}+\varepsilon_{t}.
$$

(7)

Equation (7) is a version of the market-timing test proposed by Cumby and Modest (1987). It 
is essentially a difference in means test. If the mean return conditioned on extremely short 
positions (α₀ + α₂) or extremely long positions (α₀ + α₁) is different from the unconditional 
mean (α₀), then extreme PNL positions are useful in forecasting market returns. In this 
specification, a negative (positive) α₁ and a positive (negative) α<sub>2</sub> is indicative of price 
reversals (continuation). By using the first three years of the data to define *HI* and *LO*, the 
sample size remaining for estimation is reduced to 459 weeks. As with the Granger causality 
tests, initial estimates of (7) are tested and corrected for heteroskedasticity and autocorrelation 
using the White and Newey-West estimators (Hamilton, 1994, p. 281).

$$
(\alpha_{0}+\alpha_{1})
$$

$$
(\alpha_{0}+\alpha_{2})
$$

$$
\mathbf{a}_{2}
$$

$$
\alpha_ {1}
$$

---

## Results

## Trends in Positions

The data are first examined visually to reveal simple trends and characteristics. In this section, 
we concentrate on a major feed grain—corn, and a major livestock market—live cattle. The 
trends in these futures markets are generally representative of the agricultural futures markets 
included in the study. Figure 1 shows the total open interest (futures plus delta-adjusted 
options) for corn (panel A) and live cattle (panel B). Total open interest for corn is relatively 
steady between 500,000 and 700,000 contracts through mid-2003. Then, open interest 
increases steadily to over 2 million contracts in late 2006. Over the same period, live cattle 
open interest experienced a doubling from 300,000 to 600,000 contracts. Many market 
participants attribute this increase to greater overall speculative activity (e.g., O’Hara, 2006). 
However, as shown in figure 2, the COT trader classifications are unable to confirm (or deny) 
this conjecture. Indeed, over the same time period, the commercial corn positions (panel A) 
are relatively flat at 45%–50% of total open interest. But there is marked increase in 
noncommercial activity from roughly 30% of open interest to more than 35% of open 
positions. However, this increase comes mostly at the expense of nonreporting speculators, 
whose open interest declines from nearly 25% to below 15%. Similar trends are shown for 
live cattle (panel B), where commercial positions are relatively stable and the noncommercial 
position size increases at the expense of the nonreporting group. Since nonreporting traders 
are not classified as commercial or noncommercial, we do not know if there was a relative 
loss of commercial or speculative traders. Still, it is clear from figures 1 and 2 that the 
markets seem to have undergone some changes since 2003.

Traders and market analysts often cite COT positions as a cause of price moves or a 
reason to expect a “sell-off” or “rebound” in prices. Figure 3 reveals an apparent relationship 
between corn futures prices and the PNL for noncommercial corn traders over 1998–2006. 
For instance, in panel A, a high corn price (325 cents per bushel) in early 2004 coincided with 
noncommercial traders being over 40% net long. The contemporaneous correlation between 
noncommercial PNL and corn price levels, 0.62, is in fact relatively high. Yet, as Petzel 
(1981), Sanders, Boris, and Manfredo (2004), and Gorton, Hayashi, and Rouwenhorst (2007) 
point out, this type of evidence can be misleading. High contemporaneous correlations do not 
necessarily imply a causal relationship since the correlation may simply reflect the response 
of traders to futures price movements and/or the common reaction of futures prices and 
positions to fundamental supply and demand factors. In the following section, the “smart 
money” view of COT report data is subjected to a rigorous test for predictive content.

## Do Positions Lead Returns?

Equation (4) is estimated to test if trader positions are indeed useful in forecasting returns at a 
weekly horizon. In particular, a rejection of β<sub>j</sub> = 0 " *j* would provide some evidence that the 
importance placed on the COT data by the trading industry is well-founded. The *p*-values 
(*F*-test) for this and the other null hypotheses of interest are presented in tables 1, 2, and 3 for 
the noncommercial, commercial, and nonreporting trader groups, respectively.

$$
\beta_{j}=0\ \forall\ j
$$

---

**Panel A. Corn**

2.3
2.1
1.9
1.7
1.5
1.3
1.1
Millions of Contracts0.9
0.7
0.5
0.3
1995 1996 1997 1998 1999 2000 2001 2002 2003 2004 2005 2006
Date

**Panel B. Live Cattle**

350
300
250
200
150
Thousands of Contracts  
100
50
1995 1996 1997 1998 1999 2000 2001 2002 2003 2004 2005 2006
Date

**Figure 1. Combined futures and options open interest for two commodity** 
   **markets, 1995–2006**

---

**Panel A. Corn**

60
Noncommercial Commercial Nonreporting
55
50
45
40
35
Percent  
30
25
20
15
10
1995 1996 1997 1998 1999 2000 2001 2002 2003 2004 2005 2006
Date

**Panel B. Live Cattle**

60
Noncommercial Commercial Nonreporting
55
50
45
40
35
Percent 30
25
20
15
10
1995 1996 1997 1998 1999 2000 2001 2002 2003 2004 2005 2006
Date

**Figure 2. Percent of open interest by trader category for two commodity** 
 **markets, 1995–2006**

---

Panel A. Corn
80 525
60 Percent Net Long Futures Price 475
40 425
20 375
Percent 0 325
Cents per Bushel 
-20 275
-40 225
-60 175
1995 1996 1997 1998 1999 2000 2001 2002 2003 2004 2005 2006
Date

**Panel B. Live Cattle**

80 100
Percent Net Long Futures Price
95
60
90
40 85
80
20
Percent 75
0 70
65
-20 Dollars per Hundred Pounds  
60
-40 55
1995 1996 1997 1998 1999 2000 2001 2002 2003 2004 2005 2006
Date

**Figure 3. Noncommercial percent net long and futures prices for two** 
    **commodity markets, 1995–2006**

---

**Table 1. Granger Causality Test Results for CFTC Noncommercial Traders Category** 
**(Null:** **_Positions do not lead returns, 1995–2006_****)**

|  |  | -Values for Hypothesis Tests g = 0 " i i |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
|  | m,n | $\beta_{j}=0$ ∨ j | $\sum\beta_{j}=0$ | $\gamma_{i}=0$ ∨ i | $\gamma_{i}=\beta_{j}=0$ ∨ i,j | Direction ($\sum\beta_{j}\times10^{2}$) |
| Wheat CBOT | 1,2 | 0.177 | 0.649 | 0.035 | 0.156 | -5.261 |
| Wheat KCBOT | 1,6 | 0.237 | 0.382 | 0.299 | 0.319 | 7.462 |
| Wheat MGEX | 1,1 | 0.151 | 0.151 | 0.896 | 0.345 | 0.004 |
| Corn | 4,1 | 0.789 | 0.789 | 0.062 | 0.108 | 3.675 |
| Soybeans | 1,1 | 0.047 | 0.047 | 0.877 | 0.070 | -6.128 |
| Soybean Oil | 1,1 | 0.300 | 0.300 | 0.375 | 0.552 | 5.420 |
| Soybean Meal | 1,1 | 0.929 | 0.929 | 0.687 | 0.921 | 0.000 |
| Lean Hogs | 6,1 | 0.338 | 0.338 | 0.122 | 0.145 | 0.000 |
| Live Cattle | 11,1 | 0.826 | 0.826 | 0.000 | 0.000 | -0.001 |
| Feeder Cattle | 2,1 | 0.160 | 0.160 | 0.025 | 0.042 | -0.005 |

$$
\beta_{j}=0\ \forall j
$$

$$
\Sigma\beta_{j}=0
$$

$$
\gamma_{i}=\beta_{j}=0
$$

$$
\gamma_{i}=0\forall i
$$

$$
(\Sigma\beta_{j}\times10^{2})
$$

mn
  *Note:* Estimated using text equation (4): *RRPNL*<sub>tt</sub>= αγ ++åå <sub>iti</sub>--β<sub>j tjt</sub>+ ε.
*ij* == 11

$$
R_{t}=\alpha_{t}+\sum_{i=1}^{m}\gamma_{i}R_{t-i}+\sum_{j=1}^{n}\beta_{j}P N L_{t-j}+\varepsilon_{t}.
$$

In table 1, the null hypothesis that noncommercial positions (PNL) lead or forecast market 
returns is rejected at the 5% level only in soybeans ( *p*-value = 0.047). In eight of the model 
specifications, lagged position values enter the equation at just a single lag (*n* = 1). In those 
models with more than a single lag, the null hypothesis (β<sub>j</sub> = 0 " *j*) is still not rejected, and 
the cumulative position impact, 
n

$$
(\beta_{j}=0\forall j)
$$

$$
\sum_{j=1}^{n}\beta_{j}
$$

also is not statistically different from zero. Collectively, there is little evidence that noncommercial positions are systematically useful in predicting returns. Interestingly, however, full 
rationality in futures returns (γβ<sub>ij</sub>==" 0,) *ij*is rejected at the 5% level in two markets, 
mostly due to a low-order autocorrelation in returns  (γ<sub>i</sub>= 0). "*i*

$$
\gamma_{i}=\beta_{j}=0\forall i,j
$$

$$
(\gamma_{i}=0\forall i)
$$

The null hypothesis that commercial trader positions do not lead futures returns (table 2) is 
rejected at the 5% level in CBOT wheat, KCBOT wheat, and lean hogs. Thus, in 3 of the 10 
markets, there is some evidence that commercial traders’ positions are useful in forecasting 
returns. In CBOT wheat, we reject 
n

$$
\sum_{j=1}^{n}\beta_{j}=0
$$

and find that the cumulative directional impact is negative, suggesting commercials increase 
long (short) positions prior to price declines (increases). In KCBOT wheat and lean hogs, the 
aggregate impact is not statistically different from zero, suggesting an unusual directional 
impact with some lagged β coefficients positive and others negative. This evidence is far from 
overwhelming, and the mixed nature of the directional impacts makes any systematic impact 
appear unlikely. Again, it is worth noting that full rationality in futures returns (γ<sub>i</sub> = β<sub>j</sub> = 0 
" *i*, *j*) is rejected at the 5% level in six markets, once more primarily due to a low-order 
autocorrelation in returns (γ<sub>i</sub> = 0 " *i*).

$$
\beta
$$

$$
\gamma_{i}=\beta_{j}=0
$$

$$
\forall\;i,j)
$$

$$
(\gamma_{i}=0\forall i)
$$

---

**Table 2. Granger Causality Test Results for CFTC Commercial Traders Category** 
**(Null:** **_Positions do not lead returns, 1995–2006_****)**

|  |  | -Values for Hypothesis Tests |  |  |  | Direction ($\sum \beta_{j}\times10^{2}$) |
| --- | --- | --- | --- | --- | --- | --- |
| Market | m,n | $\beta_{j}=0$ ∨ j | $\sum \beta_{j}=0$ | $\gamma_{i}=0$ ∨ i | $\gamma_{i}=\beta_{j}=0$ ∨ i,j | Direction ($\sum \beta_{j}\times10^{2}$) |
| Wheat CBOT | 1,2 | 0.007 | 0.041 | 0.068 | 0.018 | -0.021 |
| Wheat KCBOT | 4,6 | 0.030 | 0.076 | 0.054 | 0.005 | -15.175 |
| Wheat MGEX | 1,1 | 0.628 | 0.628 | 0.524 | 0.793 | 3.524 |
| Corn | 4,2 | 0.351 | 0.617 | 0.009 | 0.030 | 4.308 |
| Soybeans | 1,1 | 0.829 | 0.829 | 0.611 | 0.827 | -0.002 |
| Soybean Oil | 1,1 | 0.235 | 0.235 | 0.315 | 0.479 | 6.096 |
| Soybean Meal | 1,1 | 0.702 | 0.702 | 0.437 | 0.725 | -1.057 |
| Lean Hogs | 5,7 | 0.049 | 0.872 | 0.086 | 0.023 | -0.000 |
| Live Cattle | 11,1 | 0.748 | 0.748 | 0.000 | 0.000 | -0.003 |
| Feeder Cattle | 5,1 | 0.095 | 0.095 | 0.007 | 0.007 | -0.007 |

$$
\beta_{j}=0\ \forall j
$$

$$
\Sigma\beta_{j}=0
$$

$$
\gamma_{i}=\beta_{j}=0
$$

$$
\gamma_{i}=0\ \forall\ i
$$

$$
(\Sigma\beta_{j}\times10^{2})
$$

mn
  *Note:* Estimated using text equation (4): *RRPNL*<sub>tt</sub>= αγ ++åå <sub>iti</sub>--β<sub>j tjt</sub>+ ε.
*ij* == 11

$$
R_{t}=\alpha_{t}+\sum_{i=1}^{m}\gamma_{i}R_{t-i}+\sum_{j=1}^{n}\beta_{j}P N L_{t-j}+\varepsilon_{t}.
$$

**Table 3. Granger Causality Test Results for CFTC Nonreporting Traders Category** 
**(Null:** **_Positions do not lead returns, 1995–2006_****)**

| Market | m , n | p -Values for Hypothesis Tests |  |  |  | Direction 2 (å b × 10 ) j |
| --- | --- | --- | --- | --- | --- | --- |
| Market | m , n | = 0 &quot; j b j | å b = 0 j | g = 0 &quot; i i | g = b = 0 i j &quot; i, j | Direction 2 (å b × 10 ) j |
| Wheat CBOT | 1,1 | 0.539 | 0.539 | 0.328 | 0.584 | −1.939 |
| Wheat KCBOT | 1,1 | 0.707 | 0.707 | 0.232 | 0.487 | −0.700 |
| Wheat MGEX | 1,1 | 0.764 | 0.764 | 0.619 | 0.862 | 3.262 |
|  | Corn 4,1 0.333 0.333 0.025 0.041 |  |  |  |  | −0.015 |
|  | Soybeans 1,1 0.778 0.778 0.531 0.674 |  |  |  |  | −0.654 |
| Soybean Oil | 1,1 | 0.938 | 0.938 | 0.688 | 0.921 | 6.636 |
| Soybean Meal | 1,1 | 0.610 | 0.610 | 0.936 | 0.840 | −0.001 |
| Lean Hogs | 5,1 | 0.080 | 0.080 | 0.106 | 0.045 | −0.000 |
| Live Cattle | 11,1 | 0.477 | 0.477 | 0.000 | 0.000 | −0.004 |
| Feeder Cattle | 5,1 | 0.226 | 0.226 | 0.012 | 0.010 | 0.005 |

$$
m,n
$$

$$
\beta_{j}=0\ \forall j
$$

$$
\Sigma\beta_{j}=0
$$

$$
\gamma_{i}=\beta_{j}=0
$$

$$
\gamma_{i}=0\ \forall\ i
$$

$$
\forall\ i,j
$$

$$
(\Sigma\beta_{j}\times10^{2})
$$

mn
  *Note:* Estimated using text equation (4): *RRPNL*<sub>tt</sub>= αγ ++åå <sub>iti</sub>--β<sub>j tjt</sub>+ ε.
*ij* == 11

$$
R_{t}=\alpha_{t}+\sum_{i=1}^{m}\gamma_{i}R_{t-i}+\sum_{j=1}^{n}\beta_{j}P N L_{t-j}+\varepsilon_{t}
$$

---

As observed from table 3, the null hypothesis that nonreporting traders’ positions do not 
lead returns is not rejected at the 5% level for any market. There is no substantive evidence 
that nonreporting traders’ positions are useful for forecasting returns. This finding may not be 
surprising given the likely mixed motives of nonreporting traders, who may be speculators or 
hedgers. The results reported in table 3 again show evidence of low-order autocorrelation in 
returns.

Overall, the results do not support widespread causality from trader positions to returns. In 
the few markets where causality is documented—commercial traders’ positions in the lean 
hogs, CBOT, and KCBOT wheat markets—the direction of the causality is mixed. The empirical results do point to one notable finding: weekly futures returns tend to show some loworder positive autocorrelation. This result is consistent with other research (e.g., Yang and 
Brorsen, 1994), and it suggests a failure to model lagged returns when investigating the COT 
data may result in misspecification errors.

Collectively, the results from tables 1, 2, and 3 reveal there is little systematic causality 
from traders’ positions to returns within the agricultural futures markets examined. Given the 
noted shift in market participation in recent years (see figures 1 and 2), causal relationships 
may be masked by structural changes. Quandt likelihood-ratio tests for an unknown break 
point (Quandt, 1960; Andrews, 1993) do not reject the null hypothesis of “no break” at the 
5% level for any of the models for noncommercial traders and for only a single market in 
both the commercial and nonreporting categories (results are available from the authors upon 
request). Hence, despite the rapid increase in open interest documented for these agricultural 
futures markets, there is little evidence that the relationship between traders’ positions and 
returns (if any) has changed.

Long-horizon regressions [equation (6)] are specified by allowing *i* = 1 to 12 weeks, and 
*j* = 1 to 104 weeks, and then selecting the values that minimize the AIC. As an example, if 
*m* = 1 and *n* = 1, (6) reduces to a simple version of (5) with a single lag of returns (*R*) and 
positions (*PNL*). Alternatively, if *m* = 2 and *n* = 4 in (6), then the right-hand side includes two 
lags of returns (*R*) and the average *PNL* over the last four weeks. Allowing the potential 
specification for *j* to range from 1 to 104 weeks allows for the possibility that the impact of 
traders’ positions accumulates over as much as two years before impacting market prices.

As in (4), a number of hypotheses can be tested using equation (6). However, here we 
focus on the most crucial null hypothesis: there is no long-horizon impact from trader 
positions to returns (β = 0). The specified lag selections and *p*-values for the hypothesis 
are presented in table 4. For the group of greatest interest among market participants—
noncommercials or speculators—the null hypothesis is rejected one time at the 5% level in 
KCBOT wheat. For that market, the estimated β coefficient is positive (not shown) and the 
moving average of PNL is calculated over 101 weeks, suggesting that as large (long) 
speculative positions build, the market continues to see positive returns. Other than this single 
rejection, the overall results for the noncommercial category provide very little support for 
large speculators impacting market returns over long horizons.

$$
\beta
$$

The commercial and nonreporting categories likewise provide little statistical evidence for 
rejecting the null hypothesis. In the commercial category, β = 0 is rejected twice at the 5% 
level in feeder cattle and MGEX wheat. The sign on the estimated b coefficient is negative in 
feeder cattle and positive in MGEX wheat (not shown). This inconsistency suggests the 
impact of trader positions (if any) is potentially quite complicated and differs across markets. 
For the nonreporting segment, the null hypothesis is rejected one time at the 5% level 
in CBOT wheat. Importantly, within each category, the markets rejecting the null are not the

$$
\beta=0
$$

$$
\beta
$$

---

**Table 4. Long-Horizon Granger Causality Test Results for CFTC Traders Categories** 
**(Null:** <u>Positions do not lead returns, 1995-2006</u><u>)</u>

(Null: Positions do not lead returns, 1995-2006 )

| Market | Lag Selection and p -Values for Hypothesis Tests |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
| Market | Noncommercial |  | Commercial |  | Nonreporting |  |
| Market | m,n | β=0 | m,n | β=0 | m,n | β=0 |
| Wheat CBOT | 1,1 | 0.465 | 1,1 | 0.372 | 1,1 | 0.033 |
| Wheat KCBOT | 101 | 0.007 | 4,1 | 0.401 | 1,49 | 0.066 |
| Wheat MGEX | 1,1 | 0.138 | 104 | 0.004 | 1,1 | 0.212 |
| Corn | 4,81 | 0.282 | 4,81 | 0.327 | 4,1 | 0.904 |
| Soybeans | 1,69 | 0.419 | 1,75 | 0.342 | 1,73 | 0.327 |
| Soybean Oil | 104 | 0.150 | 104 | 0.102 | 1,12 | 0.318 |
| Soybean Meal | 1,54 | 0.735 | 1,94 | 0.490 | 1,85 | 0.441 |
| Lean Hogs | 12,104 | 0.428 | 12,104 | 0.142 | 12,56 | 0.090 |
| Live Cattle | 11,40 | 0.135 | 11,42 | 0.205 | 11,1 | 0.340 |
| Feeder Cattle | 5,83 | 0.319 | 5,20 | 0.022 | 2,4 | 0.077 |

mn<u>PNL</u>
tj-
  *Note:* Estimated using text equation (6): *RR*tt= αγ β ++åå iti<sup>-</sup>+ εt.
ij == 11*n*

$$
R_{t}=\alpha_{t}+\sum_{i=1}^{m}\gamma_{i}R_{t-i}+\beta\sum_{j=1}^{n}\frac{P N L_{t-j}}{n}+\varepsilon_{t}.
$$

same as the markets in which Granger causality is found (tables 1–3). The relative inconsistency of the results, along with the scarcity of rejection, further erodes any evidence that 
trader positions are useful in predicting futures market returns.

Despite this evidence, it is still possible that traders impact market returns when extreme 
market positions are reached. Equation (7) is used to test this hypothesis, and the estimated 
3
coefficients are presented in table 5. A positive (negative) α₁ coefficient suggests price 
continuation (reversals), while a positive (negative) a₂ indicates reversals (continuation). In 
table 5, there are two rejections of the null hypothesis at the 5% level for noncommercial 
traders, CBOT wheat and soybean oil. Interestingly, these rejections suggest continuation 
when noncommercials’ PNLs reach extreme values. For example, when the PNL is in the 
upper 20th percentile of the three-year range, wheat conditional returns tend to increase by 
1.53% in the following week. Soybean oil shows similar continuation with a 0.81% decline in 
conditional returns following relatively short noncommercial positions. These results generally do not support the idea that noncommercial traders push prices away from fundamental 
values, only later to have prices reverse.

$$
5.^{3}
$$

$$
\boldsymbol{\alpha}_{1}
$$

$$
\alpha_{2}
$$

For the commercial trader category, rejections occur at the 5% level in two markets: 
CBOT wheat and MGEX wheat. CBOT wheat shows return reversals following extreme 
commercial position levels, while MGEX wheat shows continuation at high position levels. 
Notably, CBOT wheat also displayed some evidence of Granger causality in table 2. The 
nonreporting category has one rejection of the null hypothesis (5% level), also in CBOT 
wheat.

<sup>3</sup>
 Equation (7) was also estimated by specifying alternative lag lengths (*i* = 1 to 12) for *HI*<sub>t−i</sub>and *LO*<sub>t−i</sub>and choosing the lag structure that 
minimized the AIC. Only corn (for noncommercial positions) had a lag length other than 1,1, and the null hypothesis was not rejected in this 
case. Hence, the results of this alternative specification process are not materially different from those presented in table 5.

$$
H I_{t-i}
$$

$$
LO_{t-}
$$

---

**Table 5. Cumby-Modest Test (Null:** **_Extreme positions do not predict returns, 1995–2006_****)**

| Market | Noncommercial Coeffic. a₁ |  | Commercial Coeffic. a₂ |  | Nonreporting Coeffic. a₂ −0.0024 |  |
| --- | --- | --- | --- | --- | --- | --- |
| Market | $\alpha_{1}$ | $\alpha_{2}$ | $\alpha_{1}$ | $\alpha_{2}$ | $\alpha_{1}$ | $\alpha_{2}$ |
| Wheat CBOT | 0.0153(0.0002)^{a}$ | 0.0035(0.3108) | -0.0013(0.7110) | 0.0112(0.0201) | 0.0106(0.0090) | -0.0024(0.5049) |
| Wheat KCBOT | 0.0000(0.9924) | 0.0045(0.3069) | 0.0016(0.6733) | 0.0009(0.7854) | -0.0037(0.3663) | -0.0040(0.2248) |
| Wheat MGEX | 0.0056(0.1252) | 0.0026(0.3620) | 0.0061(0.0348) | 0.0033(0.3674) | 0.0004(0.9129) | 0.0040(0.2343) |
| Corn | -0.0033(0.3838) | 0.0020(0.6067) | 0.0069(0.0798) | 0.0049(0.1822) | -0.0016(0.6996) | 0.0046(0.1966) |
| Soybeans | 0.0037(0.3102) | -0.0009(0.7918) | -0.0050(0.1429) | -0.0060(0.1240) | -0.0020(0.6397) | -0.0001(0.9667) |
| Soybean Oil | -0.0049(0.1920) | -0.0081(0.0460) | -0.0047(0.2275) | -0.0048(0.2326) | -0.0005(0.9034) | -0.0009(0.8041) |
| Soybean Meal | 0.0024(0.5856) | 0.0023(0.5630) | -0.0000(0.9893) | 0.0017(0.7221) | -0.0017(0.6976) | -0.0025(0.5371) |
| Lean Hogs | 0.0008(0.8720) | -0.0019(0.6885) | 0.00013(0.7835) | 0.0008(0.8878) | -0.0069(0.2130) | 0.0049(0.2444) |
| Live Cattle | 0.0001(0.9574) | -0.0031(0.2830) | 0.0007(0.7620) | 0.0034(0.1772) | -0.0039(0.3513) | -0.0006(0.7476) |
| Feeder Cattle | 0.0000(0.9928) | -0.0022(0.3826) | 0.0002(0.9389) | 0.0011(0.6369) | -0.0047(0.0857) | -0.0017(0.4174) |

$$
\alpha_{1}
$$

$$
\alpha_ {2}
$$

$$
\alpha_{1}
$$

$$
\alpha_{2}
$$

$$
减 _1
$$

$$
\alpha_ {2}
$$

*Note:* Estimated using text equation (7): *RHILO*<sub>tttt</sub>= αα<sub>01 12</sub>++ +<sub>--</sub>α<sub>1</sub>ε.

$$
R_{t}=\alpha_{0}+\alpha_{1}HI_{t-1}+\alpha_{2}LO_{t-1}+\varepsilon_{t}
$$

<sup>a</sup>
 Numbers in parentheses are *p*-values for two-tailed *t*-test.

Overall, there is some modest evidence of price movement following extreme market 
positions. However, the directional impacts are varied across markets, trader categories, and 
with the market positions. Market impacts (if any) stemming from extreme positions do not 
appear to be systematic across agricultural futures markets.

In total, the evidence that traders’ positions lead futures returns over weekly or longerterm horizons is limited. Indeed, there is almost no systematic evidence to indicate nonreporting traders’ positions are useful for predicting market returns in a Granger sense. 
Likewise, for noncommercials, the null hypothesis of no Granger causality is rejected only 
sporadically across markets and position measures. The long-horizon tests generally do not 
find that trader positions impact returns. Where there are rejections, the directional impacts 
differ across the markets, complicating the interpretation. Likewise, return patterns following 
extreme trader positions are inconsistent at best. The overall lack of statistical evidence—
along with the inconsistencies across methods and markets—does not support a pervasive 
tendency for large trader positions to impact futures market returns.

## Do Returns Lead Positions?

It is important to understand the dynamics of traders’ positions. For instance, behavioral 
finance theories suggest positive feedback traders may be market destabilizing (De Long et

---

**Table 6. Granger Causality Test Results for CFTC Noncommercial Traders Category** 
<u>(Null:</u> <u>Returns do not lead positions, 1995-2006</u><u>)</u>

(Null: Returns do not lead positions, 1995-2006 )

|  |  | p -Values for Hypothesis Tests |  | Direction (å q ) j |
| --- | --- | --- | --- | --- |
| Market | n,m | $\theta_{j}=0$ ∨ j | $\sum \theta_{j}=0$ | Direction (å q ) j |
| Wheat CBOT | 6,2 | 0.000 | 0.000 | -84.57 |
| Wheat KCBOT | 2,1 | 0.000 | 0.000 | 94.67 |
| Wheat MGEX | 12,2 | 0.000 | 0.000 | 159.38 |
| Corn | 5,2 | 0.000 | 0.000 | 70.56 |
| Soybeans | 2,10 | 0.021 | 0.035 | 58.29 |
| Soybean Oil | 10,2 | 0.000 | 0.000 | -122.56 |
| Soybean Meal | 2,9 | 0.000 | 0.001 | 135.29 |
| Lean Hogs | 12,2 | 0.000 | 0.000 | 104.85 |
| Live Cattle | 3,2 | 0.000 | 0.000 | 139.35 |
| Feeder Cattle | 8,1 | 0.000 | 0.000 | -77.65 |

$$
\theta_{j}=0\ \forall j
$$

$$
\Sigma\theta_{j}=0
$$

$$
(\sum\theta_{j})
$$

nm
  *Note:* Estimated using text equation (5):  *PNL*<sub>tt</sub>= f+åål<sub>i</sub>*PNL*<sub>ti</sub><sub>--</sub>+ q<sub>jtjt</sub>*R* +w.
*ij* == 11

$$
P N L_{t}=\phi_{t}+\sum_{i=1}^{n}\lambda_{i}P N L_{t-i}+\sum_{j=1}^{m}\theta_{j}R_{t-j}+\omega_{t}.
$$

al., 1990). To reveal potential trading “styles” among trader groups, equation (5) is estimated 
with the focus on the null that returns do not lead positions (θ<sub>j</sub> = 0 " *j*) and whether or not the 
cumulative directional impact is positive or negative, i.e., 
nn

$$
(\theta_{j}=0\forall j)
$$

$$
\sum_{j=1}^{n}\theta_{j}>0\quad or\quad\sum_{j=1}^{n}\theta_{j}<0.
$$

A positive directional impact is indicative of trend followers or “positive feedback” traders 
because they increase their long position after prices increase and vice versa. A negative 
directional impact suggests “negative feedback” traders or contrarian strategies.

The results from estimating equation (5) are presented in table 6 for the noncommercial 
classification. The null hypothesis that returns do not cause positions is rejected at the 5% 
level across all markets. There is a systematic and pervasive tendency for returns to lead 
positions. Moreover, the aggregate directional impact is statistically different from zero in all 
10 markets at the 5% level, with 7 of those 10 markets clearly displaying positive feedback 
trading on the part of noncommercial traders, 
n

$$
\sum_{j=1}^{n}\theta_{j}>0.
$$

These results are consistent with the findings of most other researchers (e.g., Sanders, Irwin, 
and Leuthold, 2003; Rothig and Chiarella, 2007), suggesting noncommercial traders may be 
utilizing trend-following systems.

The results for commercial traders (table 7) reveal that the null hypothesis (θ<sub>j</sub> = 0 " *j*) is 
rejected in 8 of 10 markets at the 5% level. The cumulative directional impact, 
n

$$
(\theta_{j}=0\forall j)
$$

$$
\sum_{j=1}^{n}\theta_{j},
$$

---

**Table 7. Granger Causality Test Results for CFTC Commercial Traders Category** 
**(Null:** **_Returns do not lead positions, 1995–2006_****)**

|  |  | p -Values for Hypothesis Tests |  | Direction (å q ) j |
| --- | --- | --- | --- | --- |
| Market | n,m | $\theta_{j}=0$ $\forall j$ | $\sum \theta_{j}=0$ | Direction (å q ) j |
| Wheat CBOT | 7,1 | 0.000 | 0.000 | 36.15 |
| Wheat KCBOT | 2,1 | 0.000 | 0.000 | -24.66 |
| Wheat MGEX | 1,4 | 0.000 | 0.039 | -21.92 |
| Corn | 2,5 | 0.044 | 0.127 | -18.59 |
| Soybeans | 11,1 | 0.222 | 0.222 | -8.75 |
| Soybean Oil | 10,1 | 0.000 | 0.000 | 42.49 |
| Soybean Meal | 1,10 | 0.054 | 0.129 | -29.41 |
| Lean Hogs | 12,2 | 0.000 | 0.000 | -40.81 |
| Live Cattle | 2,3 | 0.000 | 0.000 | -62.74 |
| Feeder Cattle | 5,1 | 0.027 | 0.027 | 27.65 |

$$
\theta_{j}=0\ \forall j
$$

$$
\sum\theta_{j}=0
$$

$$
(\sum\theta_{j})
$$

nm
  *Note:* Estimated using text equation (5):  *PNL*<sub>tt</sub>= f+åål<sub>i</sub>*PNL*<sub>ti</sub><sub>--</sub>+ q<sub>jtjt</sub>*R* +w.
*ij* == 11

$$
P N L_{t}=\phi_{t}+\sum_{i=1}^{n}\lambda_{i}P N L_{t-i}+\sum_{j=1}^{m}\theta_{j}R_{t-j}+\omega_{t}
$$

**Table 8. Granger Causality Test Results for CFTC Nonreporting Traders Category** 
**(Null:** **_Returns do not lead positions, 1995–2006_****)**

|  |  | p -Values for Hypothesis Tests |  | Direction ) (å q j |
| --- | --- | --- | --- | --- |
| Market | n,m | $\theta_{j}=0$ ∨ j | $\sum \theta_{j}=0$ | Direction ) (å q j |
| Wheat CBOT | 5,2 | 0.027 | 0.469 | 4.73 |
| Wheat KCBOT | 3,1 | 0.067 | 0.067 | 9.39 |
| Wheat MGEX | 3,1 | 0.851 | 0.851 | 1.30 |
| Corn | 1,1 | 0.003 | 0.003 | -10.77 |
| Soybeans | 1,2 | 0.036 | 0.014 | -13.45 |
| Soybean Oil | 5,4 | 0.000 | 0.000 | -115.99 |
| Soybean Meal | 3,1 | 0.000 | 0.000 | 21.13 |
| Lean Hogs | 1,6 | 0.160 | 0.653 | 4.09 |
| Live Cattle | 3,1 | 0.039 | 0.039 | -13.71 |
| Feeder Cattle | 2,1 | 0.000 | 0.000 | 28.07 |

$$
\theta_{j}=0\ \forall j
$$

$$
\Sigma\Theta_{j}=0
$$

nm
  *Note:* Estimated using text equation (5):  *PNL*<sub>tt</sub>= f+åål<sub>i</sub>*PNL*<sub>ti</sub><sub>--</sub>+ q<sub>jtjt</sub>*R* +w.
*ij* == 11

$$
P N L_{t}=\phi_{t}+\sum_{i=1}^{n}\lambda_{i}P N L_{t-i}+\sum_{j=1}^{m}\theta_{j}R_{t-j}+\omega_{t}
$$ is statistically different from zero at the 5% level in 7 of 10 markets, of which four display a 
negative cumulative impact or “value” strategies. In total, 7 of the 10 directional indicators 
are negative, suggesting short hedgers are scale-up sellers and long hedgers are scale-down 
buyers. However, the directional evidence is not overwhelming toward either style. This 
finding may stem from a heterogeneous group of traders potentially captured in the comercial category.

Perhaps not surprisingly, the results for nonreporting traders also are mixed (table 8). The 
null hypothesis that returns do not lead positions is rejected in 8 of the 10 markets at the 5% 
level. The cumulative impact is different from zero in 7 out of 10 markets (5% level), with 
four of those showing a negative feedback style, somewhat consistent with the commercial 
group.

In total, the above results build a strong case that returns lead positions. While the general 
trading style of noncommercials can be tentatively classified as one of positive feedback 
strategies, the results for the commercial and nonreporting categories are more mixed, with no 
clearly dominant style within each group. These results may reflect that both the commercial 
and nonreporting categories are capturing a diverse group of traders, where the composition 
may change across markets (Ederington and Lee, 2002).

## Conclusions

The goal of this research was to explicitly examine the usefulness of the Commodity Futures 
Trading Commission’s (CFTC’s) Commitments of Traders (COT) data in predicting agricultural futures returns. In light of the evolving nature of speculative participants in futures 
markets and the attention paid in the industry to the positions held by trader groups, it is 
important to directly address the usefulness of these data in a forecasting framework. Here, 
we used a standard bivariate Granger causality approach to investigate the lead-lag dynamics 
between traders’ positions and returns in 10 agricultural futures markets. A variation of the 
Granger approach was used to test for long-horizon impact of trader positions. A Cumby-
Modest test was employed to determine whether trader positions impact returns when extreme 
market positions are reached.

The empirical results suggest two primary findings. First, traders’ positions do not show a 
systematic and pervasive tendency to lead returns. In particular, there is practically no ability 
to forecast market returns using either noncommercial or nonreporting positions. Over weekly 
horizons, there is some weak evidence that commercial positions lead returns in a few 
specific markets (i.e., lean hogs, CBOT, and KCBOT wheat); however, this is not a pervasive 
theme across markets. Long-horizon tests again showed very little and inconsistent support 
for trader positions impacting returns. Market impacts (if any) stemming from extreme 
positions do not appear to be systematic across agricultural futures markets.

Second, the results clearly demonstrate that positions follow returns. In particular, noncommercial traders increase long positions after prices increase, and they therefore appear to 
be trend followers. The directional findings for commercial traders and nonreporting traders 
are more varied, with some markets showing trend-following styles and others showing 
contrarian or value strategies. The mixed directional evidence may reflect a hodgepodge of 
speculators and hedgers captured in these categories.

The results of this study have practical ramifications for academic researchers and market 
participants alike. Academic researchers should take note of the strong case for trading 
styles documented in this work, in particular the trend-following displayed by noncommercial traders. Sanders, Irwin, and Leuthold (2003) document similar styles for market newsletter 
writers and advisors as captured in market sentiment indices. This suggests there may be 
groups of traders who systematically employ simplified trading or hedging rules. Based on 
behavioral finance theories (e.g., De Long et al., 1990), the existence of such traders can have 
implications for market behavior even though it was not captured by the methods specific to 
this study.

For practitioners, the usefulness of the COT data in forecasting returns is suspect. In 
particular, noncommercial, or “fund,” positions provide virtually no forecasting information 
for returns in agricultural futures markets. Indeed, noncommercial positions are basically a 
linear extrapolation of past price changes, consistent with trend-following strategies. If the 
COT data provide any forecasting information, it is likely found in the commercial category 
and in isolated markets. Even in cases where some evidence exists, the direction of the impact 
is varied across horizons and markets. So, if it is possible to utilize COT data to anticipate 
market movements, it is unlikely to be through a simplistic and consistent rule across 
markets. Moreover, the delay from the time the positions are recorded on Tuesday to their 
release on Friday would further erode any predictive power. As an alternative approach, 
practitioners may want to mimic the trading style—e.g., trend-following—displayed by their 
preferred trader group.

Overall, the evidence for predictive power is rather weak. The presented results are 
consistent with those reported by Dale and Zyren (1996) who state, “… noncommercial 
traders follow price trends: they don’t set them” (p. 23). Still, traders and market analysts 
frequently rely on the COT data, as these data are widely used in analyzing market activity. 
Thus, there is a seeming paradox between the predictive power of the COT data as presented 
in this research and its perceived (or real) usefulness to those in the industry. Perhaps the 
COT data simply provide market commentators with convenient talking points or justification 
for otherwise difficult-to-explain market movements. Alternatively, the COT data may indeed 
provide a glimpse of the “smart money” in a fashion not easily captured by standard empirics.

Finally, Streeter and Tomek (1992) argue that if speculator positions do impact returns, it 
is most likely to occur over time horizons much shorter than a week, the observation interval 
for published COT reports. Daily data on trader positions are used to create the weekly COT 
reports, but these disaggregated data have been made available to only a few researchers over 
the years (Hartzmark, 1987; Leuthold, Garcia, and Liu, 1994; Ederington and Lee, 2002). 
Given the important public debate underway about the impact of speculation in agricultural 
futures markets, regulators should strongly consider allowing more researchers access to the 
underlying daily data for COT reports.

[*Received May 2008; final revision received June 2009.*]

## References

Andrews, D. W. K. “Tests for Parameter Instability and Structural Change with Unknown Change Point.” 
*Econometrica* 61,4(1993):821–856. 
Briese, S. *The Commitments of Traders Bible: How to Profit from Insider Market Intelligence.* Hoboken, NJ: 
John Wiley and Sons, Inc., 2008. 
Bryant, H., D. A. Bessler, and M. S. Haigh. “Causality in Futures Markets.” *J. Futures Mkts.* 26,11(2006): 
1039–1057.

---

Chang, E. C. “Returns to Speculators and the Theory of Normal Backwardation.” *J. Finance* 40,1(1985):193–
208. 
Commodity Futures Trading Commission (CFTC). “Comprehensive Review of the Commitments of Traders 
Reporting Program.” *Federal Register* 71(21 June 2006a):FR 35627. 
———. “Commodity Futures Trading Commission Actions in Response to the ‘Comprehensive Review of 
the Commitments of Traders Reporting Program.’” 5 December 2006b. Online. Available at http://cftc/ 
gov/stellent/groups/public/@commitmentsoftraders/documents/file/noticeonsupplementalcotrept.pdf. 
———. “About the Commitments of Traders.” 2008. Online. Available at http://www.cftc.gov/market 
reports/commitmentsoftraders/cot_about.html. 
Cumby, R. E., and D. M. Modest. “Testing for Market Timing Ability: A Framework for Forecast Evaluation.” *J. Finan. Econ.* 19,1(1987):169–189. 
Dale, C., and J. Zyren. “Noncommercial Trading in the Energy Futures Market.” *Petroleum Marketing* 
*Monthly.* Energy Information Administration, U.S. Department of Energy, Washington, DC, May 1996. 
De Long, J. B., A. Shleifer, L. H. Summers, and R. J. Waldmann. “Positive Feedback Investment Strategies 
and Destabilizing Rational Speculation.” *J. Finance* 45,2(1990):379–395. 
De Roon, F. A., T. E. Nijman, and C. Veld. “Hedging Pressure Effects in Futures Markets.” *J. Finance*
55,3(2000):1437–1456. 
Domanski, D., and A. Heath. “Financial Investors and Commodity Markets.” *Bank for International Settle-*
*ments Quarterly Review* (March 2007):53–67. 
Ederington, L., and J. H. Lee. “Who Trades Futures and How? Evidence from the Heating Oil Market.” *J.* 
*Business* 75,4(2002):353–373. 
Fenton, J., and G. Martinaitas. “Large Trader Reporting: The Great Equalizer.” *Futures Industry* (July/ 
August 2005):34–39. 
Gorton, G. B., F. Hayashi, and K. G. Rouwenhorst. “The Fundamentals of Commodity Futures Returns.” 
Work. Pap. No. 13249, National Bureau of Economic Research, Washington, DC, July 2007. 
Gorton, G., and K. G. Rouwenhorst. “Facts and Fantasies About Commodity Futures.” *Financial Analysts J.*
62,2(2006):47–68. 
Hamilton, J. D. *Time Series Analysis*. Princeton, NJ: Princeton University Press, 1994. 
Hartzmark, M. L. “Returns to Individual Traders of Futures: Aggregate Results.” *J. Polit. Econ.* 95,6(1987): 
1292–1306. 
Hieronymus. T. A. *Economics of Futures Trading for Commercial and Personal Profit*. New York: Commodity Research Bureau, 1971. 
Jegadeesh, N. “Seasonality in Stock Price Mean Reversion: Evidence from the U.S. and the U.K.” *J. Finance*
46,4(1991):1427–1444. 
Kahn, A. D. “Conformity with Large Speculators: A Test of Efficiency in the Grain Futures Market.” *Atlantic* 
*Econ. J.* 14(1986):51–55. 
Leuthold, R. M., P. Garcia, and R. Lu. “The Returns and Forecasting Ability of Large Traders in the Frozen 
Pork Bellies Futures Market.” *J. Business* 67,3(1994):459–473. 
McDonald, W. E., and S. K. Freund. “The CFTC’s Large Trader Reporting System: History and Development.” *Business Lawyer* 38(1983):917–953. 
Morrison, K. “Commodities Lure Funds Investors.” *Financial Times* (28 December 2004). Online. Available 
at http://www.ft.com. 
O’Hara, N. “Mutual Funds Tap into Commodities.” *Futures Industry* (May/June 2006):19–22. 
Petzel, T. E. “A New Look at Some Old Evidence: The Wheat Market Scandal of 1925.” *Food Research* 
*Institute Studies* 18,1(1981):117–128. 
Quandt, R. “Tests of the Hypothesis that a Linear Regression System Obeys Two Different Regimes.” *J.* 
*Amer. Statis. Assoc.* 55,290(1960):324–330. 
Rothig, A., and C. Chiarella. “Investigating Nonlinear Speculation in Cattle, Corn, and Hog Futures Markets 
Using Logistic Smooth Transition Regression Models.” *J. Futures Mkts.* 27,8(2007):719–737. 
Sanders, D. R., K. Boris, and M. Manfredo. “Hedgers, Funds, and Small Speculators in the Energy Futures 
Markets: An Analysis of the CFTC’s Commitments of Traders Reports.” *Energy Econ.* 26,3(2004):425–
445. 
Sanders, D. R., S. H. Irwin, and R. M. Leuthold. “The Theory of Contrary Opinion: A Test Using Sentiment 
Indices in Futures Markets.” *J. Agribusiness* 21,1(2003):39–64.

---

Streeter, D. H., and W. G. Tomek. “Variability in Soybean Futures Prices: An Integrated Framework.” *J.* 
*Futures Mkts.* 12,12(1992):705–728. 
Summers, L. H. “Does the Stock Market Rationally Reflect Fundamental Values?” *J. Finance* 41,3(1986): 
591–601. 
Upperman, F. *Commitments of Traders: Strategies for Tracking the Market and Trading Profitably*. 
Hoboken, NJ: John Wiley and Sons, Inc., 2006. 
Wang, C. “Investor Sentiment and Return Predictability in Agricultural Futures Markets.” *J. Futures Mkts.*
21,10(2001):929–952. 
———. “The Behavior and Performance of Major Types of Futures Traders.” *J. Futures Mkts.* 23,1(2003): 
1–31. 
Yang, J., D. A. Bessler, and H. G. Fung. “The Informational Role of Open Interest in Futures Markets.” *Appl.* 
*Econ. Letters* 11,11(2004):569–573. 
Yang, S. R., and B. W. Brorsen. “Daily Futures Price Changes and Non-Linear Dynamics.” *Structural* 
*Change and Econ. Dynamics* 5,1(1994):111–132.