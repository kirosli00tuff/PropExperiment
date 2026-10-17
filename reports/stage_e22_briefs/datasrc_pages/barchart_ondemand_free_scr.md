Market Data APIs | Barchart OnDemand
[![Barchart](https://www.barchart.com/ondemand/img/barchart-grey-logo.svg)](https://www.barchart.com/ondemand "Barchart")




* [APIs](https://www.barchart.com/ondemand/api)
* [Data Coverage](https://www.barchart.com/ondemand/data)
* [Case Studies](https://www.barchart.com/ondemand/../solutions/resources/case-studies)

* [Resources](https://www.barchart.com/ondemand/faq)

  [FAQ](https://www.barchart.com/ondemand/faq)
  [Excel Integration](https://www.barchart.com/ondemand/excel-integration)
  [Legal](https://www.barchart.com/legal)
* [Contact](https://www.barchart.com/ondemand/contact)

Market Data APIs
================

Barchart features a diverse set of market data APIs that can be easily integrated into your website. Whether you're looking for a small, medium, large or enterprise solution, we'll create a custom package for you that exceeds your expectations. Explore our Market Data APIs below.

Connect for more info

Categories

[Price Data](#price-data)
[Cryptocurrency Data](#cryptocurrency-data)
[Profiles and Financial Data](#profiles-and-financial-data)
[Splits, Dividends, and Earnings](#splits-dividends-and-earnings)
[Leaderboards and Lists](#leaderboards-and-lists)
[Charts and Analytics](#charts-and-analytics)
[ETFs](#etfs)
[News and Filings](#news-and-filings)
[Metadata](#metadata)
[Other Data](#other-data)

Tools

[Event-Based API - Contact Us For Access](#)  

Barchart's Event-Based API provides developers REST API and/or Socket.IO endpoints for implementing market data and news based real-time alerts when their user-defined conditions occur.

Clients:  
[Java](https://github.com/barchart/barchart-ondemand-client-java)  /  
[JavaScript](https://github.com/barchart/barchart-ondemand-client-js)  /  
[PHP](https://github.com/barchart/barchart-ondemand-client-php)  /  
[Python](https://github.com/barchart/barchart-ondemand-client-python)  /  
[MATLAB](https://www.mathworks.com/matlabcentral/fileexchange/68211-barchart-ondemand-for-matlab?s_tid=prof_contriblnk)

Price Data

[getQuote(s)](https://www.barchart.com/ondemand/api/getQuote)

The getQuote API is used to request price data, either real-time, delayed or end-of-day, by symbol on stocks, indexes, mutual funds, ETFs, futures, foreign exchange, or cryptocurrencies.

[getHistory](https://www.barchart.com/ondemand/api/getHistory)

The getHistory API is used to request historical time series data on stocks, indexes, mutual funds, ETFs, futures, foreign exchange, or cryptocurrencies. Historical data is available as tick, minute bars or end-of-day data.

getData

Custom Data. The getData API is a custom query to request any combination of market data fields we make available. Contact us to design a custom getData API.

[getClosePrice](https://www.barchart.com/ondemand/api/getClosePrice)

The getClosePrice API provides the close price for given instruments for the given date.

[getQuoteEod](https://www.barchart.com/ondemand/api/getQuoteEod)

The getQuoteEod API is used to request end-of-day price data, by combined exchange and symbol, on stocks, indexes, mutual funds, ETFs, futures, foreign exchange, or cryptocurrencies. Historical data is available as tick, minute bars or end-of-day data.

[getEquitiesByExchange](https://www.barchart.com/ondemand/api/getEquitiesByExchange)

Receive all real-time or delayed equities market data by exchange through a single onDemand query with the getEquitiesByExchangeAPI from Barchart OnDemand.

[getFuturesByExchange](https://www.barchart.com/ondemand/api/getFuturesByExchange)

Receive all real-time or delayed, or end-of-day futures data by exchange through a single onDemand query with the get FuturesByExchange API from Barchart OnDemand.

[getFuturesOptions](https://www.barchart.com/ondemand/api/getFuturesOptions)

The getFuturesOptions API provides intraday options data such as strike price, closing price, expiration date, volume, volatility etc on futures contracts.

[getFuturesOptionsEOD](https://www.barchart.com/ondemand/api/getFuturesOptionsEOD)

The getFuturesOptionsEOD API provides end-of-day options data such as strike price, closing price, expiration date, volume, volatility etc on futures contracts.

[getFuturesSpreads](https://www.barchart.com/ondemand/api/getFuturesSpreads)

The getFuturesSpreads API returns all active futures spread for the requested commodity.

[getSpecialOptions](https://www.barchart.com/ondemand/api/getSpecialOptions)

The getSpecialOptionsClassification API provides the classification for weekly and special options by commodity.

[getEquityOptions](https://www.barchart.com/ondemand/api/getEquityOptions)

The getEquityOptions API from Barchart OnDemand provides intraday or end-of-day options data such as strike price, closing price, expiration date, volume and volatility, etc.

[getEquityOptionsHistory](https://www.barchart.com/ondemand/api/getEquityOptionsHistory)

The getEquityOptionsHistory API from Barchart OnDemand allows users to get historical prices for equity options.

[getEquityOptionsOverviewHistory](https://www.barchart.com/ondemand/api/getEquityOptionsOverviewHistory)

The getEquityOptionsOverviewHistory API provides implied volatility (IV) options metrics for a single equity symbol at a time. It returns historical daily values such as weighted implied volatility, IV rank and percentile, total volume, open interest, and put/call ratios.

[getEquityOptionsOverviewSummary](https://www.barchart.com/ondemand/api/getEquityOptionsOverviewSummary)

The getEquityOptionsOverviewSummary API provides implied volatility option metrics for equity symbols intraday. It delivers current-day values such as weighted implied volatility, IV rank and percentile, total volume, open interest, and put/call ratios.

[getOptionsScreener](https://www.barchart.com/ondemand/api/getOptionsScreener)

The getOptionsScreener API allows a user to screen for specific equity and ETF option strikes using a variety of filters and parameters that highlight where unusual options activity may be occuring. Users can build powerful market scanners to implement professional trading strategies.

[getAmeriborRate](https://www.barchart.com/ondemand/api/getAmeriborRate)

AMERIBOR® is an interbank interest rate reflecting the borrowing rates based on actual transactions of the members of the American Financial Exchange (AFX). AMERIBOR® is a transaction-based short-term interest rate based on loans executed between U.S. depositories on the American Financial Exchange Electronic Trading System. The rate is calculated using the 30 trading day rolling average of the weighted average daily volume in the AFX overnight unsecured market. The rate is denoted as a 360-day annualized percentage rate up to the fifth decimal.

[getRestrictedSessionHistory](https://www.barchart.com/ondemand/api/getRestrictedSessionHistory)

The getRestrictedSessionHistory API is used to request historical time series data on stocks, indexes, mutual funds, ETFs, futures, foreign exchange, or cryptocurrencies. Historical data is available as minute bars data. This API also requests startMinute and endMinute parameter and will return price data for the requested date ranges for timestamp between the requested start and end minutes.

[getRestrictedSessionOHLCPrices](https://www.barchart.com/ondemand/api/getRestrictedSessionOHLCPrices)

The getRestrictedSessionOHLCPrices API is used to request open,high,low and close data n stocks, indexes, mutual funds, ETFs, futures, foreign exchange, or cryptocurrencies for the time range between the startMinute and endMinute parameters for the given date range. Historical data is available as minute bars data.

Cryptocurrency Data

[getCrypto](https://www.barchart.com/ondemand/api/getCrypto)

The getCrypto API provides price data by symbol for spot market cryptocurrencies, including Bitcoin, Ethereum, Ripple, Litecoin and more. [Bitcoin futures](https://www.barchart.com/futures/bitcoin) are available through [getQuote](https://www.barchart.com/ondemand/api/getQuote). In addition to last price, other fields such as open, high, low, close, price change, percent change are available.

[getCryptoHistory](https://www.barchart.com/ondemand/api/getCryptoHistory)

The getCryptoHistory API provides historical price data for spot cryptocurrencies, including Bitcoin, Ethereum, Ripple, Litecoin and more. Bitcoin futures historical data is available through the getHistory API.

Profiles and Financial Data

[getProfile](https://www.barchart.com/ondemand/api/getProfile)

The getProfile API is used to request information about a publicly traded company, such as sector, industry, company description, CEO, recent earnings, P/E ratio, and address, based on symbol.

[getFinancialHighlights](https://www.barchart.com/ondemand/api/getFinancialHighlights)

The getFinancialHighlights API provides key financial highlights, ratios and statistics for equities based on symbol. Fields include market capitalization, revenue, net income, revenue growth and earnings per share.

[getFinancialRatios](https://www.barchart.com/ondemand/api/getFinancialRatios)

The getFinancialRatios API provides key financial ratios for equities based on symbol. The fields include earnings per share, return on equity and price to earnings.

[getIncomeStatements](https://www.barchart.com/ondemand/api/getIncomeStatements)

The getIncomeStatements API from Barchart OnDemand provides access to public company financial income statements based on symbol.

[getBalanceSheets](https://www.barchart.com/ondemand/api/getBalanceSheets)

The getBalanceSheets API from Barchart OnDemand provides access to public company financial balance sheet data based on symbol.

[getCompetitors](https://www.barchart.com/ondemand/api/getCompetitors)

Barchart OnDemand's getCompetitors API provides a list of related stock symbols (competitors) for an underlying stock input.

[getRatings](https://www.barchart.com/ondemand/api/getRatings)

Barchart OnDemand's getRatings API provides analysts ratings on stocks (strong buy, moderate buy, hold, moderate sell or strong sell) based on symbol.

[getIndexMembers](https://www.barchart.com/ondemand/api/getIndexMembers)

The getIndexMembers API from Barchart OnDemand returns the constituents comprising an index.

[getCashFlow](https://www.barchart.com/ondemand/api/getCashFlow)

Barchart OnDemand's getCashFlow API provides information about cash flow, income and cash equivalents of publicly traded companies.

Splits, Dividends, and Earnings

[getCorporateActions](https://www.barchart.com/ondemand/api/getCorporateActions)

The getCorporateActions API from Barchart OnDemand provides corporate actions data on equities including splits, dividends and earnings, based on a symbol.

[getEarningsEstimates](https://www.barchart.com/ondemand/api/getEarningsEstimates)

The getEarningsEstimates API from Barchart OnDemand provides per share earnings estimates on public companies for quarterly and annual periods based on symbol.

[getDividendData](https://www.barchart.com/ondemand/api/getDividendData)

The getDividendData API from Barchart OnDemand provides the most recent dividend data for requested instruments.

[getDividendStocks](https://www.barchart.com/ondemand/api/getDividendStocks)

The getDividendStocks API returns dividend info for all US instruments.

[getCorporateActionsByExchange](https://www.barchart.com/ondemand/api/getCorporateActionsByExchange)

The getCorporateActions API from Barchart OnDemand provides splits or dividends data for US equities, mutual funds and Canadian equities by exchange.

[getEarningsCalendar](https://www.barchart.com/ondemand/api/getEarningsCalendar)

The getEarningsCalendar API provides the total number of upcoming earnings by date. And will also return the earnings data for the requested date. Please note that the output of this API will change based on the type of data requested. When requesting 'totals' (default type), it will return the date and total earnings for that date. And when requesting 'earnings' it will return earnings data for all symbols for the requested start date.

[getDividendsCalendar](https://www.barchart.com/ondemand/api/getDividendsCalendar)

The getDividendsCalendar API provides the total number of upcoming dividends by date. And will also return the dividends data for the requested date. Please note that the output of this API will change based on the type of data requested. When requesting 'totals' (default type), it will return the date and total dividends for that date. And when requesting 'dividends' it will return dividend data for all symbols for the requested start date.

[getEarningsAndDividendsCalendar](https://www.barchart.com/ondemand/api/getEarningsAndDividendsCalendar)

The getEarningsAndDividendsCalendar API provides the total number of upcoming earnings and dividends by date. And will also return the earnings and dividends for the requested date. Please note that the output of this API will change based on the type of data requested. When requesting 'totals' (default type), it will return the date and total earnings and dividends for that date, when requesting 'earnings' it will return earnings data for all symbols for the requested start date, when requesting 'dividends' it will return dividend data for all symbols for the requested start date. And if the request type is 'earnings-dividends' then the output will be and earnings attribute that will have an array of objects with earnings data and a dividends attribute with an array of objects with the dividends data.

Leaderboards and Lists

[getLeaders](https://www.barchart.com/ondemand/api/getLeaders)

Barchart OnDemand's getLeaders API provides leaderboard lists for equities, futures, forex, mutual funds and ETFs, including most active, gainers, losers, what's hot and what's not hot.

[getHighsLows](https://www.barchart.com/ondemand/api/getHighsLows)

The getHighsLows API from Barchart OnDemand provides lists for new 52-week highs or 52-week lows based on exchange and asset type.

[getSectors](https://www.barchart.com/ondemand/api/getSectors)

The getSectors API from Barchart OnDemand provides returns using weighted alpha on sectors covering multiple periods, including 1-day, 1-month, 3-month, 6-month, 9-month, 12-month and year-to-date.

Charts and Analytics

[getChart](https://www.barchart.com/ondemand/api/getChart)

The getChart API from Barchart OnDemand is used to request a custom chart image with variables such as chart type, size, period and technical indicators, based on a symbol.

[getTechnicals](https://www.barchart.com/ondemand/api/getTechnicals)

Barchart OnDemand's getTechnicals API provides technical data and statistics for equities, indices, futures, currencies, cryptocurrencies and mutual funds based on symbol. Fields include moving averages, percent changes over different time periods and stochastics.

[getSignal](https://www.barchart.com/ondemand/api/getSignal)

The getSignal API provides the Barchart Technical Opinion / Signal (buy, sell or hold) based on a variety of short, medium and long-term technical indicators based on a symbol.

[getMomentum](https://www.barchart.com/ondemand/api/getMomentum)

The getMomentum API provides a daily summary on the number of advancing, declining and unchanged stocks, as well as the percentage of stocks above moving averages of different lengths.

[getTechnicalIndicatorData](https://www.barchart.com/ondemand/api/getTechnicalIndicatorData)

The getTechnicalIndicatorData API from Barchart OnDemand provides the requested technical indicators data for the requested symbol.

ETFs

[getETFDetails](https://www.barchart.com/ondemand/api/getETFDetails)

Barchart OnDemand's getETFDetails API provides ETF profile information including descriptions, fund family, underlying index, inception date, alpha, beta, shares outstanding, management fee, assets under management, top 10 holdings and more.

[getETFConstituents](https://www.barchart.com/ondemand/api/getETFConstituents)

The getETFConstituents API from Barchart OnDemand provides the complete list of constituents for a given ETF.

News and Filings

[getNews](https://www.barchart.com/ondemand/api/getNews)

Barchart OnDemand's getNews API returns news headlines, articles and related photos based upon news sources, category, sub-category and/or keyword.

[getNewsSources](https://www.barchart.com/ondemand/api/getNewsSources)

The getNewsSources API from Barchart OnDemand provides access to public news sources and your authorization status per source.

[getNewsCategories](https://www.barchart.com/ondemand/api/getNewsCategories)

Barchart OnDemand's getNewsCategories API provides access to news source category and sub-category data.

[getSECFilings](https://www.barchart.com/ondemand/api/getSECFilings)

Barchart OnDemand's getSECFilings API provides access to quarterly, annual and other required regulatory/SEC filings for U.S. publicly traded companies based on symbol.

Metadata

[getInstrumentDefinition](https://www.barchart.com/ondemand/api/getInstrumentDefinition)

The getInstrumentDefinition API from Barchart OnDemand is available to request metadata on financial instruments by symbol, exchange, or exchange MIC. Metadata includes instrument names, exchange codes, tick increments, base codes, expiration dates and more.

[getFuturesSpecifications](https://www.barchart.com/ondemand/api/getFuturesSpecifications)

Barchart OnDemand's getFuturesSpecifications API provides contract information such as trading hours, contract size and tick size for futures contracts.

[getFuturesExpirations](https://www.barchart.com/ondemand/api/getFuturesExpirations)

The getFuturesExpiration API from Barchart OnDemand provides first notice and last trade dates for futures contracts.

[getFuturesOptionsExpirations](https://www.barchart.com/ondemand/api/getFuturesOptionsExpirations)

The getFuturesOptionsExpirations API provides last trade dates for options on futures contracts.

[getSpecialOptionsClassification](https://www.barchart.com/ondemand/api/getSpecialOptionsClassification)

The getSpecialOptionsClassifications API from Barchart OnDemand provides the classification for weekly and special options by commodity.

[getForexForwardCurves](https://www.barchart.com/ondemand/api/getForexForwardCurves)

The getForexForwardCurves API from Barchart OnDemand provides the bid, ask, and mid price data for all available forward curves (forward rates) for a given forex symbol.

[getSymbolChange](https://www.barchart.com/ondemand/api/getSymbolChange)

The getSymbolChange API from Barchart OnDemand provides the list of symbols that have gone through a change.

[getRelatedInstruments](https://www.barchart.com/ondemand/api/getRelatedInstruments)

The getRelatedInstruments API from Barchart OnDemand provides the list of all symbols for a given company across different countries and exchanges.

Other Data

[getWeather](https://www.barchart.com/ondemand/api/getWeather)

Barchart OnDemand's getWeather API provides current conditions and forecasts based on zip code. As well as weather maps based on type or region.

[getGrainBids](https://www.barchart.com/ondemand/api/getGrainBids)

The getGrainBids API provides cashbid data for 30 closest locations in relation to the requested zip code. Learn more about Barchart's proprietary [commodity data](https://www.barchart.com/cmdty) and grain [cmdtyIndexes](https://www.barchart.com/cmdty/indexes).

[getUSDAGrainPrices](https://www.barchart.com/ondemand/api/getUSDAGrainPrices)

Barchart OnDemand's getUSDAGrainPrices API provides daily cash grain bids and prices for grain buying locations throughout the United States covering corn, wheat, oats and soybeans sourcing from USDA reports. This API refreshes on an hourly basis, so bids and prices from USDA reports would be available within an hour after the report is released.

[getCmdtyStatsId](https://www.barchart.com/ondemand/api/getCmdtyStatsId)

The getCmdtyStatsId API is used identify instrument identifiers that can be passed to getCmdtyStats in order to request data on the applicable series. Users can search for data series based on search parameters covering content, source, area, frequency, and more.

[getCmdtyStats](https://www.barchart.com/ondemand/api/getCmdtyStats)

The getCmdtyStats API is used to request information on various fundamentals, commodity statistics, and economic data. Users can request information by data series with historical information available through to inception for most series. cmdtyStats™ is the premier source of aggregated commodity statistics – all made available in one easy to use API.

[getGrainInstruments](https://www.barchart.com/ondemand/api/getGrainInstruments)

The getGrainInstruments API is used to request symbol and metadata information regarding physical grain instruments across Barchart's cash bids and grain indexes. Users can request information based on crop type / root symbol, geo-location, or areas that are codified by FIPS standards. Returned instruments and their corresponding symbols can be passed to getQuote or getHistory to retrieve the associated price data - as requested by the end user. Find our more about our [commodity data](https://www.barchart.com/cmdty) offerings here.

[getBLSIndexes](https://www.barchart.com/ondemand/api/getBLSIndexes)

The getBLSIndexes API provides historical price data for our cmdty BLS Commodity Price Index Family. The cmdty BLS Commodity Price Indexes measure price movements of 22 basic commodities whose markets are among the first to be influenced by changes in economic conditions. Sub-indices for six major asset classes are calculated.

[getCmdtyCalendar](https://www.barchart.com/ondemand/api/getCmdtyCalendar)

The getCmdtyCalendar API provides user the latest updates of US economic activity and commodity trading events, including previous, revised, and actual values, updated 3 times a day. Users can request calendar events for desired period, and filter the output via various methods - category, importance, event country, and event symbol.

[getFuelPrices](https://www.barchart.com/ondemand/api/getFuelPrices)

The getFuelPrices API provides refined fuel price data and reference data. Refined fuel data can be requested for fuel selling locations, for geographic coordinates and radius, for zip code and radius, and for a specified county. Refined fuel data can be filtered by product name(s), and by number of locations will be returned. Reference data contains fuel selling locations and product names, providing valid values in use for requesting refined fuel data. Reference data can be requested for geographic coordinates and radius. If no geographic coordinates are given, reference data will return all valid values by default.

[getCropFactors](https://www.barchart.com/ondemand/api/getCropFactors)

The getCropFactors API provides weather data/factors specific to Ag Industry. With this API, you can retrieve satellite imagery derived weather factors, like Normalized Difference Vegetation Index (**NDVI**), Normalized Difference Water Index (**NDWI**), and Land Surface Temperature(**LSTD** & **LSTN**), and station collected weather data, like air temperature(**TMAX** & **TMIN**), and accumulated precipitation(**PRCP**).  
Data can be requested for a combination of counties and observation windows.

[getUniqueIdentifier](https://www.barchart.com/ondemand/api/getUniqueIdentifier)

The getUniqueIdentifier provides the Financial Instrument Global Identifier (FIGI) information for all available instruments. For more information on FIGI, please [click here](https://www.openfigi.com/about/figi).

[getYieldForecastPlanet](https://www.barchart.com/ondemand/api/getYieldForecastPlanet)

The getYieldForecast API provides Barchart proprietary grain yield forecast data. Yield Index data can be filtered by commodity, by indexGroup, by state, by district, and by county. The unit is in Bushel per Acre.

[![Barchart OnDemand](https://www.barchart.com/ondemand/img/barchart-logo-white.svg)](https://www.barchart.com/ondemand)

[APIsAPIs](https://www.barchart.com/ondemand/api)
[Data CoverageData Coverage](https://www.barchart.com/ondemand/data)
[Case StudiesCase Studies](https://www.barchart.com/ondemand/../solutions/resources/case-studies)
[ContactContact](https://www.barchart.com/ondemand/contact)
[AboutAbout](https://www.barchart.com/ondemand/../solutions/company/about)

222 S. Riverside Plaza, Suite 810

Chicago, IL 60606

[solutions@barchart.com](mailto:solutions@barchart.com)

312-566-9235

Get updates on fintech and new products:

By submitting this form you are opting in to receive email communications from Barchart for related product, service or company information, updates and announcements. You can unsubscribe at anytime. View our [Privacy Policy](https://www.barchart.com/about/privacy).

© 2026 [Barchart.com](https://www.barchart.com/), Inc. All Rights Reserved.
  
[Terms of Use](https://www.barchart.com/ondemand/../terms)
|
[Privacy Policy](https://www.barchart.com/ondemand/../terms#privacy-policy)
|
[Do Not Sell My Personal Information](https://www.barchart.com/ondemand/../terms#do-not-sell)

Barchart is committed to ensuring digital accessibility for individuals with disabilities. We are continuously working to improve our web experience, and encourage users to [Contact Us](https://www.barchart.com/ondemand/contact) for feedback and accommodation requests.

Here is an example to help guide your inquiry

`I am a web developer who is creating a mobile app for my users to track the stock market. I’m looking to access an API that can provide me with 15-minute delayed and historical equities data for Cboe BZX, Nasdaq, and NYSE.`

Close

Here is an example to help guide your inquiry

`My firm is looking for a data feed that can power our algo trading platform. We're looking to access daily data for all U.S. equities including open, high, low, close, and volume. We are also interested in accessing Options data for these markets.`

Close

Here is an example to help guide your inquiry

`I work at a financial media firm and we have a website and mobile app for customers to follow the markets. We are looking into adding charting widgets, portfolio, and watchlist tools to our web properties for US and European Equities. Could you please provide us with monthly pricing for these various digital solutions?`

Close

Contact Us

Please submit the form below and someone will contact you shortly.

First Name\*

Last Name\*

Email Address\*

Phone\*

Company\*

Role\*
Select Role...Advisory ServicesBrokerBusiness DevelopmentData ManagerData ScientistDeveloperExecutiveFarmerFinanceIndividualMarketingMerchandiserProcurementProduct ManagerQuant/Research AnalystRisk ManagerSupportTraderOther

Industry\*
Select industry...AcademicAg MediaAg TechAg ServicesAgribusinessAsset ManagementBankingBiofuelsCorporateEnergyEquity BrokerageExchangeFinancial PublishingFinancial ServicesFood & BeverageForex / CryptoFutures BrokerageIndividualMarket DataMedia (Financial)Media (Traditional)MetalsMetals (Scrap)OtherProprietary TradingSoftware (Other)Software (Trading)Transportation

Country\*
United StatesCanadaAfghanistanAland IslandsAlbaniaAlgeriaAmerican SamoaAndorraAngolaAnguillaAntarcticaAntigua And BarbudaArgentinaArmeniaArubaAustraliaAustriaAzerbaijanBahamasBahrainBangladeshBarbadosBelarusBelgiumBelizeBeninBermudaBhutanBoliviaBonaireBosnia and HerzegowinaBotswanaBouvet IslandBrazilBritish Indian Ocean TerritoryBrunei DarussalamBulgariaBurkina FasoBurundiCambodiaCameroonCape VerdeCayman IslandsCentral African RepublicChadChileChinaChristmas IslandCocos (Keeling) IslandsColombiaComorosCongoCongo, the Democratic Republic of theCook IslandsCosta RicaCote d'IvoireCroatiaCubaCuracaoCyprusCzech RepublicDenmarkDjiboutiDominicaDominican RepublicEcuadorEgyptEl SalvadorEquatorial GuineaEritreaEstoniaEthiopiaFalkland Islands (Malvinas)Faroe IslandsFijiFinlandFranceFrench GuianaFrench PolynesiaFrench Southern TerritoriesGabonGambiaGeorgiaGermanyGhanaGibraltarGreeceGreenlandGrenadaGuadeloupeGuamGuatemalaGuernseyGuineaGuinea-BissauGuyanaHaitiHeard and McDonald IslandsHoly See (Vatican City State)HondurasHong KongHungaryIcelandIndiaIndonesiaIran, Islamic Republic ofIraqIrelandIsle of ManIsraelItalyJamaicaJapanJapanJerseyJordanKazakhstanKenyaKiribatiKorea, Democratic People's Republic ofKorea, Republic ofKuwaitKyrgyzstanLao People's Democratic RepublicLatviaLebanonLesothoLiberiaLibyan Arab JamahiriyaLiechtensteinLithuaniaLuxembourgMacaoMacedonia, The Former Yugoslav Republic OfMadagascarMalawiMalaysiaMaldivesMaliMaltaMarshall IslandsMartiniqueMauritaniaMauritiusMayotteMexicoMicronesia, Federated States ofMoldova, Republic ofMonacoMongoliaMontenegroMontserratMoroccoMozambiqueMyanmarNamibiaNauruNepalNetherlandsNetherlands AntillesNew CaledoniaNew ZealandNicaraguaNigerNigeriaNiueNorfolk IslandNorthern Mariana IslandsNorwayOmanPakistanPalauPalestinian Territory, OccupiedPanamaPapua New GuineaParaguayPeruPhilippinesPitcairnPolandPortugalPuerto RicoQatarReunionRomaniaRussian FederationRwandaSaint BarthelemySaint HelenaSaint Kitts and NevisSaint LuciaSaint Pierre and MiquelonSaint Vincent and the GrenadinesSamoaSan MarinoSao Tome and PrincipeSaudi ArabiaSenegalSerbiaSeychellesSierra LeoneSingaporeSlovakiaSloveniaSolomon IslandsSomaliaSouth AfricaSouth Georgia and the South Sandwich IslandsSouth SudanSpainSri LankaSudanSurinameSvalbard and Jan MayenSwazilandSwedenSwitzerlandSyrian Arab RepublicTaiwanTajikistanTanzania, United Republic ofThailandTimor-LesteTogoTokelauTongaTrinidad and TobagoTunisiaTurkeyTurkmenistanTurks and Caicos IslandsTuvaluUgandaUkraineUnited Arab EmiratesUnited KingdomUnited States Minor Outlying IslandsUruguayUzbekistanVanuatuVenezuelaViet NamVirgin Islands, BritishVirgin Islands, U.S.Wallis and FutunaWestern SaharaYemenZambiaZimbabwe

What you are looking for?\*

Please provide as much information as possible (e.g. exchanges, markets or other data sources) and/or required services (e.g. APIs, web hosting, software, charting), and your use case.

Here are some examples: [Example #1](#), [Example #2](#), [Example #3](#).

By submitting this form you are opting in to receive email communications from Barchart for related product, service or company information, updates and announcements. You can unsubscribe at anytime. View our [Privacy Policy](https://www.barchart.com/about/privacy).

Close

By clicking “Accept All Cookies”, you agree to the storing of cookies on your device to enhance site navigation, analyze site usage, and assist in our marketing efforts. [For more information see our Cookie Policy.](https://www.barchart.com/cookie-notice)[View our Terms and Privacy Policy.](https://www.barchart.com/terms)

Accept All Cookies

![Company Logo](https://cdn.cookielaw.org/logos/b59bf43c-074f-4144-b2bb-b19717d3ae4a/018dd783-09a6-7958-870c-35c70e887384/3d416bac-73c0-4455-a6f3-19fcf76d57a4/Barchart_Corporate_Logo_Blue.png)

Privacy Preference Center
-------------------------

Your Opt Out Preference Signal is Honored

* ### Your Privacy
* ### Strictly Necessary Cookies
* ### Targeting Cookies
* ### Functional Cookies
* ### Performance Cookies

#### Your Privacy

When you visit any website, it may store or retrieve information on your browser, mostly in the form of cookies. This information might be about you, your preferences or your device and is mostly used to make the site work as you expect it to. The information does not usually directly identify you, but it can give you a more personalized web experience. Because we respect your right to privacy, you can choose not to allow some types of cookies. Click on the different category headings to find out more and change our default settings. However, blocking some types of cookies may impact your experience of the site and the services we are able to offer.
  
[More information see our Cookie Policy.](https://www.barchart.com/cookie-notice)

#### Strictly Necessary Cookies

Always Active

These cookies are necessary for the website to function and cannot be switched off in our systems. They are usually only set in response to actions made by you which amount to a request for services, such as setting your privacy preferences, logging in or filling in forms. You can set your browser to block or alert you about these cookies, but some parts of the site will not then work. These cookies do not store any personally identifiable information.

View Vendor Details‎

#### Targeting Cookies

Targeting Cookies Active

These cookies may be set through our site by our advertising partners. They may be used by those companies to build a profile of your interests and show you relevant adverts on other sites. They do not store directly personal information, but are based on uniquely identifying your browser and internet device. If you do not allow these cookies, you will experience less targeted advertising.

View Vendor Details‎

#### Functional Cookies

Functional Cookies Active

These cookies enable the website to provide enhanced functionality and personalisation. They may be set by us or by third party providers whose services we have added to our pages. If you do not allow these cookies then some or all of these services may not function properly.

View Vendor Details‎

#### Performance Cookies

Performance Cookies Active

These cookies allow us to count visits and traffic sources so we can measure and improve the performance of our site. They help us to know which pages are the most and least popular and see how visitors move around the site. All information these cookies collect is aggregated and therefore anonymous. If you do not allow these cookies we will not know when you have visited our site, and will not be able to monitor its performance.

View Vendor Details‎

Back Button

### Vendors List

Filter Button

Consent Leg.Interest

checkbox label label

checkbox label label

checkbox label label

Clear

checkbox label label

Apply Cancel

Confirm My Choices

Reject All Allow All

[![Powered by Onetrust](https://cdn.cookielaw.org/logos/static/powered_by_logo.svg "Powered by OneTrust Opens in a new Tab")](https://www.onetrust.com/products/cookie-consent/)