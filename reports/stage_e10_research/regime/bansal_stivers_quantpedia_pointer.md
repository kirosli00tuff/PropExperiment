Time-Varying Equity Premia with a High-VIX Threshold | QuantPedia


[![QuantPedia](https://quantpedia.com/app/themes/quantpedia/img/logo.png)](https://quantpedia.com/ "QuantPedia")




[Pricing](/pricing/)[Product](/screener/)[How it works](/how-it-works/)[About](/quantpedia-mission/)[Blog](/blog/)[Resources](/resources/)[Consulting](/quant-consulting-services/)[Awards](/quantpedia-awards-2027/)

[Sign Up](https://quantpedia.com/pricing/)

Log In

Time-Varying Equity Premia with a High-VIX Threshold
====================================================

29.September 2023

[market timing](https://quantpedia.com/tag/market-timing/)[volatility effect](https://quantpedia.com/tag/volatility-effect/)[volatility premium](https://quantpedia.com/tag/volatility-premium/)

Financial markets have always been fascinating places of modern warfare where bears and bulls fight over the price, which is the only objective value of an asset at any time since it is when the buyer finds the seller and vice versa. During times of high stress and uncertainty of any kind, **market volatility** rises, and prices of different instruments tend to move to unbelievable highs or lows, defining any gravity (meme stocks going to the moon) or, on the other hand, literally having no bottom (crude oil futures for a brief time during coronavirus outbreak). It really looks like financial markets are driven by fear and greed. It will always be interesting to think if computer algorithms utilizing some almost magical machine learning AI feel these emotions as well (however, imagining them market-making a few meters from exchanges in New York and feeling happy or sad arbitraging high-frequency opportunities is hilarious).

**What does one of the most popular and well-known metrics, VIX, tell us about future returns?** Are we able somehow to verify sayings such as “*Buy* when *there’s blood* in the *streets*, even if the *blood* is your own.“ (attributed to Baron Rothschild) or (more mildly put) “to be *fearful* when *others* are *greedy* and to be *greedy* only when *others are fearful*.“ (variations Warren Buffett).

A recent academic paper presents an interesting finding. It shows, that a **common, intuitive 20/80 thumb rule may be introduced: most of the excess returns earned from market-level exposure are realized 20% of the time following the highest VIX values.**

**From 1990 to 2022, scientists show that time-variation in the returns earned from equity-market exposure can be explained well by a simple 2-term risk-return specification, which predicts (1) much higher returns after VIX exceeds a high threshold at around its 80th percentile and (2) lower excess returns following a high market sentiment.** **[Bansal and Stivers (July 2023)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4477652) argue that VIX and market sentiment tend to measure complementary aspects of risk: the level of risk (VIX) and the price of risk or risk appetite (sentiment), and that, thus, both terms should be accounted for when evaluating time variation in the equity market’s risk premium.**

**To evaluate systematic risk, they primarily investigate subsequent excess returns for the aggregate stock market (primarily). For a beta-based position, that is long high-beta stocks and short low-beta stocks. As a result, they consistently found optimal thresholds near the 80th to 85th VIX percentile.**

**Mounting evidence indicates that the VIX threshold and sentiment have complementary, substantial roles in predicting subsequent excess stock returns.** **The model that includes the lagged Treasury implied-volatility index (MOVE) as an additional explanatory term adds appreciable explanatory power in the post-1997 period. That can be nicely seen from the figures below.**

**In closing, our recommended paper for reading is a nice example that shows that the high VIX-threshold pattern fits with the intuition that the equity risk premium can increase dramatically in periods of high economic stress and low liquidity, along with the nonlinear behavior of equity premium in the previous literature.**

**Authors:** [Naresh Bansal](https://papers.ssrn.com/sol3/cf_dev/AbsByAuth.cfm?per_id=506494 "View other papers by this author") and [Chris T. Stivers](https://papers.ssrn.com/sol3/cf_dev/AbsByAuth.cfm?per_id=142290 "View other papers by this author")

**Title:** Time-varying Equity Premia with a High-VIX Threshold and Sentiment

**Link**: <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4477652>

**Abstract:**

Over the 1990 to 2022 period, we show that time-variation in the returns earned from equity-market exposure can be explained well with a simple specification, which predicts: (1) much higher excess returns after the implied volatility from equity-index options exceeds a high threshold at around its 80th percentile; and (2) lower excess returns following a high market sentiment. Our results are robustly evident for 1-, 3-, 6-, and 12-month returns; in subperiod analysis; and for both excess aggregate stock-market returns and beta-based long/short portfolio positions. The predictive R-squared values are substantial at about 20% and 30% for 6-month and 12-month returns, respectively. Comparatively, we show that the VIX-threshold in our specification outperforms other risk explanatory terms suggested by the literature; including the recent high-frequency realized volatility, the equity volatility risk premium, a risk-aversion index measure, stock-market illiquidity, and macroeconomic uncertainty. Our findings remain strongly evident when controlling for the default yield spread and term yield spread. Our findings indicate that the VIX-threshold and sentiment importantly capture complementary risk aspects, suggesting an interpretation where VIX largely indicates the level of risk and sentiment is informative about the market’s risk appetite or price of risk.

As always, we present several interesting figures and tables:

![](https://quantpedia.com/app/uploads/2023/08/SSRN-id4477652_pages-to-jpg-0047-scaled-e1691756833695-730x1024.jpg)

![](https://quantpedia.com/app/uploads/2023/08/SSRN-id4477652_pages-to-jpg-0048-scaled-e1691756881978-735x1024.jpg)

![](https://quantpedia.com/app/uploads/2023/08/SSRN-id4477652_pages-to-jpg-0049-scaled-e1691756935105-769x1024.jpg)

**Notable quotations from the academic research paper:**

“We argue that VIX and sentiment intuitively measure complementary aspects of market risk; in the sense of the level of risk (VIX) and the price of risk or risk appetite (sentiment). Hence, it is important to account for both effects when studying the predictive power of these variables for stock returns. In this paper, over the 1990 to 2022 VIX-available period, we show that time-variation in the returns earned from equity-market exposure can be explained well with a simple 2-parameter risk-return specification, which predicts: (1) much higher excess returns after the implied volatility from equity-index options (VIX) exceeds a high threshold in a non-linear fashion; and (2) lower excess returns following a high market sentiment.  
Specifically, we estimate an optimal high-VIX threshold indicator variable, at around the 80th VIX percentile over our sample, as an explanatory term for the subsequent excess equity-market returns. We show that a simple VIX-threshold approach strongly outperforms a specification with a linear VIX explanatory relation. We then combine this high-VIX- threshold predictive term with sentiment. Following from Lochstoer and Muir (2022) and others, our specifications skip a month between the explanatory terms and subsequent excess market returns. This temporal gap allows some separation between the negative price impact of increasing risk (a largely contemporaneous influence) and the higher premia suggested by elevated risk (a predictive or intertemporal relation).

Figure 1 displays the time-series of monthly observations for VIX (end-of-month) and the Baker-Wurgler sentiment index. As depicted, VIX and sentiment are essentially uncorrelated over our sample period. The two measures have a correlation of 0.038 over our full sample. Approximate one-half subperiod correlations are also quite modest, at +0.150 over 1990:01- 2006:06 and -0.027 over 2006:07 to 2022:06. Further, we highlight that sentiment has prominent local peaks in each one-half subperiod. Sentiment peaked at 2.93 in February 2001 and at 2.28 in December 2021.

Overall, our results in this section demonstrate the impressive explanatory power of our simple 2-parameter model, which includes a high-VIX threshold and a sentiment term, in explaining the time-variation in market-level returns. Our results remain robust, regardless of whether we estimate the high-VIX threshold from optimal threshold regressions or use an adhoc 80th percentile threshold.

To present our results in a different way, Figure 2 graphically presents our primary model estimation results. The figure plots the time-series of the fitted (or conditional) predicted 6-month return over the subsequent six months (the darker, thicker line) from our primary model estimation in Table 1, Panel A.1, row-3. It also plots the actual realized 6-month excess returns (the lighter, thinner line). Since we analyze rolling 6-month returns, observed monthly, the data periodicity is monthly.

In summary, our findings suggest that the implied volatility of Treasury yields can also assist in explaining the risk-return relation in the equity market, particularly in the post-1997 period. However, our two-parameter ‘high-VIX-sentiment and sentiment’ model remains robust to controlling for MOVE, indicating that VIX and sentiment jointly capture complementary aspects of the market’s risk and risk appetite.”

---

**Are you looking for more strategies to read about? [Sign up for our newsletter](https://quantpedia.com/sign-up-for-our-newsletter/) or visit our [Blog](https://quantpedia.com/blog/) or [Screener](http://quantpedia.com/Screener)**.

**Do you want to learn more about Quantpedia Premium service? Check [how Quantpedia works](https://quantpedia.com/how-it-works/), [our mission](http://quantpedia.com/Home/About) and [Premium pricing offer](https://quantpedia.com/pricing/).**

**Do you want to learn more about Quantpedia Pro service? Check its [description](https://quantpedia.com/how-it-works/quantpedia-pro/), watch [videos](https://quantpedia.com/how-it-works/quantpedia-explains/), review [reporting capabilities](https://quantpedia.com/how-it-works/quantpedia-pro-reports/) and visit our [pricing offer](https://quantpedia.com/pricing-pro/).**

**Do you want algorithmic access to the full Quantpedia database via the [API](https://quantpedia.com/api/v1/docs#overview)? Subscribe to [Quantpedia Pro](https://quantpedia.com/pricing/), ask for an API key, and explore the in/out-of-sample statistics, source academic papers, and code snippets — ideal for quantitative research, systematic trading workflows, and AI model training.**

**Are you looking for historical data or backtesting platforms? Check our list of [Algo Trading Discounts](https://quantpedia.com/links-tools/?category=algo-trading-discounts)**.

---

**Or follow us on:**

**Facebook [Group](https://www.facebook.com/groups/quantstrategies), Facebook [Page](https://www.facebook.com/quantpedia/), [Telegram](https://t.me/quantpedia), [Twitter](https://twitter.com/quantpedia), [Linkedin](https://www.linkedin.com/company/quantpedia), [Medium](https://quantpedia.medium.com/) or [Youtube](https://www.youtube.com/channel/UC_YubnldxzNjLkIkEoL-FXg)**

Share on[LinkedIn](https://www.linkedin.com/shareArticle?mini=1&url=https%3A%2F%2Fquantpedia.com%2Ftime-varying-equity-premia-with-a-high-vix-threshold%2F&title=Time-Varying+Equity+Premia+with+a+High-VIX+Threshold&source=https%3A%2F%2Fquantpedia.com%2Ftime-varying-equity-premia-with-a-high-vix-threshold%2F)[Twitter](https://twitter.com/home?status=Time-Varying+Equity+Premia+with+a+High-VIX+Threshold+https%3A%2F%2Fquantpedia.com%2Ftime-varying-equity-premia-with-a-high-vix-threshold%2F)[Facebook](https://www.facebook.com/sharer/sharer.php?u=https%3A%2F%2Fquantpedia.com%2Ftime-varying-equity-premia-with-a-high-vix-threshold%2F)[Refer to a friend](mailto:?to=&subject=Time-Varying+Equity+Premia+with+a+High-VIX+Threshold&body=Time-Varying%20Equity%20Premia%20with%20a%20High-VIX%20Threshold%0Ahttps%3A%2F%2Fquantpedia.com%2Ftime-varying-equity-premia-with-a-high-vix-threshold%2F)

### **Quantpedia** is The Encyclopedia of Quantitative Trading Strategies

**We’ve already analysed tens of thousands of financial research papers and identified more than 700 attractive trading systems together with hundreds of related academic papers.**

[Browse Strategies](https://quantpedia.com/screener/)

Search for:

[![Subscribe to newsletter](https://quantpedia.com/app/uploads/2022/03/newsletter.png)](https://quantpedia.com/sign-up-for-our-newsletter/)**[Sign up for Quantpedia Newsletter!](https://quantpedia.com/sign-up-for-our-newsletter/)**[![Subscribe to RSS Feed](https://quantpedia.com/app/uploads/2022/03/rssfeed.png)](/feed)**[Get updates from our Blog via RSS Feed](/feed)**[![Check offered Algo Trading Discounts!](https://quantpedia.com/app/uploads/2022/03/discount.png)](https://quantpedia.com/links-tools/?category=algo-trading-discounts)**[Check offered Algo Trading Discounts!](/links-tools/?category=algo-trading-discounts)**

### Blog Sponsor

[![](https://quantpedia.com/app/uploads/2025/01/quantpedia_EODHD_banner.gif)](https://eodhistoricaldata.com/pricing-quantpedia?ref=JTS2ZTXQ&utm_source=quantpedia&utm_medium=banner&utm_campaign=all_in_one_gif)

### Recent Posts

* [A New Stage, a New Deadline: Quantpedia Awards 2027 Are Here Again!](https://quantpedia.com/a-new-stage-a-new-deadline-quantpedia-awards-2027-are-here-again/)
* [Quantpedia Premium Update – September 27th](https://quantpedia.com/quantpedia-premium-update-september-27th-2/)
* [Can Weakening Morning Order Flow Predict SPY Reversals?](https://quantpedia.com/can-weakening-morning-order-flow-predict-spy-reversals/)
* [Building and Testing Trend-Following Strategies on One-Minute SPY Data](https://quantpedia.com/building-and-testing-trend-following-strategies-on-one-minute-spy-data/)
* [Do Airline Stocks Take Off Around U.S. Holidays?](https://quantpedia.com/do-airline-stocks-take-off-around-u-s-holidays/)

### Tags

[alternative data](https://quantpedia.com/tag/alternative-data/)
[asset allocation](https://quantpedia.com/tag/asset-allocation/)
[asset class picking](https://quantpedia.com/tag/asset-class-picking/)
[cryptocurrencies](https://quantpedia.com/tag/cryptocurrencies/)
[diversification](https://quantpedia.com/tag/diversification/)
[equity long short](https://quantpedia.com/tag/equity-long-short/)
[factor allocation](https://quantpedia.com/tag/factor-allocation/)
[factor investing](https://quantpedia.com/tag/factor-investing/)
[machine learning](https://quantpedia.com/tag/machine-learning/)
[market timing](https://quantpedia.com/tag/market-timing/)
[momentum](https://quantpedia.com/tag/momentum/)
[momentum in stocks](https://quantpedia.com/tag/momentum-in-stocks/)
[own-research](https://quantpedia.com/tag/own-research/)
[reversal](https://quantpedia.com/tag/reversal/)
[seasonality](https://quantpedia.com/tag/seasonality/)
[smart beta](https://quantpedia.com/tag/smart-beta/)
[stock picking](https://quantpedia.com/tag/stock-picking/)
[trendfollowing](https://quantpedia.com/tag/trendfollowing/)
[value](https://quantpedia.com/tag/value/)
[volatility effect](https://quantpedia.com/tag/volatility-effect/)

### Partners

[![](https://quantpedia.com/app/uploads/2025/01/logo_orange_white.png)](https://eodhd.com/pricing-quantpedia?via=quantpedia)
[![](/app/uploads/2019/07/quantocracy-badge-130.png)](https://www.quantocracy.com)
[![](/app/uploads/2019/07/logo_quantinsti.png)](https://www.quantinsti.com/)
[![](/app/uploads/2019/07/priceactionlab.png)](https://www.priceactionlab.com/Blog/price-action-lab-software/)
[![](/app/uploads/2019/07/multicharts.png)](https://www.multicharts.com/net/)
[![](/app/uploads/2019/07/genovest.png)](https://genovest.com/)
[![](/app/uploads/2019/07/equitieslab.png)](https://www.equitieslab.com/)
[![](/app/uploads/2019/07/buildalpha.png)](https://www.buildalpha.com/)
[![](/app/uploads/2026/05/hispatrading.png)](https://hispatrading.es/)
[![](https://quantpedia.com/app/uploads/2021/02/disruption-banking-1-scaled.jpg)](https://disruptionbanking.com/category/capital-markets/)
[![](/app/uploads/2019/07/arpm_logo.png)](https://www.arpm.co)

### Links

* [Alpha Architect](https://alphaarchitect.com/blog)
* [Analyzing Alpha](https://analyzingalpha.com/)
* [Build Alpha](https://www.buildalpha.com/blog/)
* [Disruption Banking](https://disruptionbanking.com/category/capital-markets/)
* [Dual Momentum](https://www.optimalmomentum.com/blog/)
* [Genovest](https://genovest.com/blog/)
* [Hispatrading](https://hispatrading.es/)
* [Matthew Smith](https://lf0.com/)
* [Meb Faber](https://mebfaber.com/)
* [Price Action Lab](https://www.priceactionlab.com/Blog/)
* [Quant Connect](https://www.quantconnect.com/blog/)
* [QuantInsti](https://www.quantinsti.com/)
* [Quantivity](https://quantivity.wordpress.com/)
* [QuantSavvy](https://quantsavvy.com/quant-trading-blog/)
* [Signal Plot](http://www.signalplot.com/)
* [Spikeet](https://www.spikeet.com/)
* [Trading System Lab](http://www.tradingsystemlab.com/)

[![](https://quantpedia.com/app/uploads/2019/11/Quantitative-and-Algorithmic-Trading-Strategies-facebook-group-150x150.png)](https://www.facebook.com/groups/quantstrategies/) Join our [Facebook Group](https://www.facebook.com/groups/quantstrategies/)

Subscription Form

### **Subscribe for Newsletter**

###### Be first to know, when we publish new content

Select Your ProfessionRetail Trader / Individual InvestorWealth Manager / AdvisorStudent / AcademicsQuant / Trader / Portfolio Manager

I agree that Quantpedia may process my personal information in accordance with Quantpedia [Privacy Policy](https://quantpedia.com/privacy-policy/)

Subscribe

![footerLogo](https://quantpedia.com/app/themes/quantpedia/img/footer-logo.png)

The Encyclopedia of Quantitative Trading Strategies

Product

* [Pricing](/pricing/)
* [Screener](/screener/)
* [Charts](/charts/)
* [Consulting](/quant-consulting-services/)
* [Quantpedia Awards](/quantpedia-awards-2024/)

About us

* [About us](/quantpedia-mission/)
* [How it works](/how-it-works/)
* [Clients & References](/references/)
* [FAQ](/how-it-works/faq/)
* [Blog](/blog/)

Support

* [Contact](/contact/)
* [Privacy Policy](/privacy-policy/)
* [Terms of Service](/terms-of-service/)
* [Affiliate](/affiliate/)
* [Links & Tools](/links-tools/)

Follow us

Risk Disclosure: Futures and forex trading contains substantial risk and is not for every investor. An investor could potentially lose all or more than the initial investment. Risk capital is money that can be lost without jeopardizing ones’ financial security or life style. Only risk capital should be used for trading and only those with sufficient risk capital should consider trading. Past performance is not necessarily indicative of future results.

Hypothetical Performance Disclosure: Hypothetical performance results have many inherent limitations, some of which are described below. No representation is being made that any account will or is likely to achieve profits or losses similar to those shown; in fact, there are frequently sharp differences between hypothetical performance results and the actual results subsequently achieved by any particular trading program. One of the limitations of hypothetical performance results is that they are generally prepared with the benefit of hindsight. In addition, hypothetical trading does not involve financial risk, and no hypothetical trading record can completely account for the impact of financial risk of actual trading. for example, the ability to withstand losses or to adhere to a particular trading program in spite of trading losses are material points which can also adversely affect actual trading results. There are numerous other factors related to the markets in general or to the implementation of any specific trading program which cannot be fully accounted for in the preparation of hypothetical performance results and all which can adversely affect trading results.

Testimonial Disclosure: Testimonials appearing on this website may not be representative of other clients or customers and is not a guarantee of future performance or success.

  

© 2026 Quantpedia.com. All rights reserved.

![logo](https://quantpedia.com/app/themes/quantpedia/img/footer-logo.png)

The Encyclopedia of Quantitative Trading Strategies

×

### Log in

Remember Me

[Forgot Password](https://quantpedia.com/login/?action=forgot_password)

### Sign-up for free to continue

You’ve reached your limit for viewing up to 5 strategies for free

Upgrade your subscription

By signing up you agree with our  [terms & conditions](https://quantpedia.com/terms-of-service/)

Do you have an acount?  [Login here.](javascript:void(0))

**Close** ×

After free sign-up you’ll be able to browse all free strategies in our library for free

We are using cookies to give you the best experience on our website. To learn more, see our [Privacy Policy](https://quantpedia.com/privacy-policy/).

Accept



Close GDPR Cookie Settings

![QuantPedia](https://quantpedia.com/app/plugins/gdpr-cookie-compliance/dist/images/gdpr-logo.png)

* Privacy Overview
* Strictly Necessary Cookies

[Powered by  GDPR Cookie Compliance](https://wordpress.org/plugins/gdpr-cookie-compliance/)

Privacy Overview

This website uses cookies so that we can provide you with the best user experience possible. Cookie information is stored in your browser and performs functions such as recognising you when you return to our website and helping our team to understand which sections of the website you find most interesting and useful.

Strictly Necessary Cookies

Strictly Necessary Cookie should be enabled at all times so that we can save your preferences for cookie settings.

Enable or Disable Cookies


Enabled
Disabled

Enable All
Save Settings