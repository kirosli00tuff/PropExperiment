Historical Data API | Barchart OnDemand
[![Barchart](https://www.barchart.com/ondemand/img/barchart-grey-logo.svg)](https://www.barchart.com/ondemand "Barchart")




* [APIs](https://www.barchart.com/ondemand/api)
* [Data Coverage](https://www.barchart.com/ondemand/data)
* [Case Studies](https://www.barchart.com/ondemand/../solutions/resources/case-studies)

* [Resources](https://www.barchart.com/ondemand/faq)

  [FAQ](https://www.barchart.com/ondemand/faq)
  [Excel Integration](https://www.barchart.com/ondemand/excel-integration)
  [Legal](https://www.barchart.com/legal)
* [Contact](https://www.barchart.com/ondemand/contact)

Historical Data API
===================

`getHistory`

The getHistory API is used to request historical time series data on stocks, indexes, mutual funds, ETFs, futures, foreign exchange, cash commodities or cryptocurrencies. Historical data is available as tick, minute bars or end-of-day data.

[View All APIs](https://www.barchart.com/ondemand/api)

Contact Us to Get Access

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

Please provide as much information as possible (e.g. exchanges, markets or other data sources), the APIs you are interested in (e.g. getQuote, getHistory, getChart, getCorporateActions, etc.), and your use case.

Here are some examples: [Example #1](#), [Example #2](#), [Example #3](#).

By submitting this form you are opting in to receive email communications from Barchart for related product, service or company information, updates and announcements. You can unsubscribe at anytime. View our [Privacy Policy](https://www.barchart.com/about/privacy).

* [Summary](#nav-summary)
* [Sample Queries](#nav-sample-queries)
* [Sample Code](#nav-sample-code)

Inputs

symbol*required*

A symbol or code that identifies a financial instrument.

Type

string (A sequence of characters. (example: GOOG))

Example

`AAPL`

type*required*

The type of historical data to return, including tick data, minute data, and end-of-day data.

Type

enum (A type which includes a list of valid possible values.)

Example

`minutes`

Valid Values

ticks, minutes, nearbyMinutes, formTMinutes, daily, dailyNearest, dailyContinue, weekly, weeklyNearest, weeklyContinue, monthly, monthlyNearest, monthlyContinue, quarterly, quarterlyNearest, quarterlyContinue, yearly, yearlyNearest, yearlyContinue

startDate*optional*

The start date of the historical data query. This parameter should be set to the desired start date/time for the query (the result set will include records back to, and including, this value). If not set, the value will default to the beginning of the day specified in the end parameter, if end is specified, or to the beginning of the current day, if end is not specified. The value should conform to the format yyyymmdd[hhmm[ss]], where fields in brackets are optional (Do not include the brackets themselves). Any optional fields that are not explicitly set will default to 0 (i.e. 20090203 will default to 20090203000000 or February 3, 2009 at 00:00:00).

Type

dateTime (A date and time in the format of YYYY-MM-DD HH:MI:SS<TIMEZONE\_OFFSET>.)

Example

`20100101`

endDate*optional*

The end data of the historical data query. This parameter should be set to the desired end date/time for the query (the result set will include records up to, but not including, this value). If not set, the value will default to the end of the day specified in the start parameter, if specified, or to the end of the current day, if start is not specified. The value should conform to the format yyyymmdd[hhmm[ss]], where fields in brackets are optional (Do not include the brackets themselves). Any optional fields that are not explicitly set will default to 0 (i.e. 20090203 will default to 20090203000000 or February 3, 2009 at 00:00:00).

Type

dateTime (A date and time in the format of YYYY-MM-DD HH:MI:SS<TIMEZONE\_OFFSET>.)

Example

`20130101`

maxRecords*optional*

The maximum amount of records returned. This parameter should be set to the maximum number of records desired. If not specified, there number of records returned will be determined by the date/time parameters specified as well as any defaults that apply to the query.

Type

int (A numeric type defining a whole number. (example: 2))

Example

`10`

interval*optional*

The number of minutes for a minute query.

Type

int (A numeric type defining a whole number. (example: 2))

Example

`60`

Default

1

order*optional*

An arrangement of fields within a particular record (ascending or descending). This parameter can be set to one of two values ("asc" and "desc") in order to specify the chronological order of the result set returned. If this parameter is not specified, the order results is not guaranteed.

Type

enum (A type which includes a list of valid possible values.)

Example

`asc`

Default

asc

Valid Values

asc, desc

sessionFilter*optional*

This parameter modifies the default session codes/sale conditions used to return ticks for each exchange. For NYSE and AMEX, the default session filter is "@EFKX56V9" (meaning all ticks with sale conditions corresponding to one of the characters in the filter are included in the results), for NASDAQ the default is "@ABDEFKOSXY156", and for everything else all session codes/sale conditions are returned except the settle (session code '\*'). If the session filter is set to a string of valid session codes (i.e. "EFK"), only ticks with the specified session codes are included in the results. If the string is prefixed with character '!' (i.e."!EFK"), all session codes except those in the string are included in the results. If the string is prefixed with character '+' (i.e. "+T"), then all the default session codes in addition to the ones specified in the string are included in the results. And if the string is prefixed with character '-' (i.e. "-EF") then all default session codes except the ones specified are included in the results. Please note that the '+' character should be escaped (to %2B) when entering the URL in a web browser or executing the query in an API that does not escape it by default.

Type

string (A sequence of characters. (example: GOOG))

Example

`EFK`

splits*optional*

An adjustment of stock value due to corporate action. This parameter only applies to stocks and specifies whether the data returned should be adjusted for splits or not. Set to true to query for adjusted the data, or to false for non-adjusted data. If not specified, the default is true. In order to guarantee the same adjustment settings in the future, this parameter should be specified.

Type

boolean (A logical type representing the truth of a value as 'true' or 'false'.)

Example

`true`

Default

1

dividends*optional*

A distribution of a portion of a company's earnings. This parameter only applies to stocks and specifies whether the data returned should be adjusted for dividends or not. Set to true to query for adjusted the data, or to false for non-adjusted data. If not specified, the default is true. In order to guarantee the same adjustment settings in the future, this parameter should be specified.

Type

boolean (A logical type representing the truth of a value as 'true' or 'false'.)

Example

`true`

Default

1

volume*optional*

The quantity of shares or contracts traded. For futures, this parameter can be set to one of two values (contract and total) in order to specify whether the volume returned should be the contract volume or the total volume. For aggregates (such as weekly, monthly or yearly), this returns the average volume for the period specified. If the value is preceded by 'sum' (sumcontract and sumtotal), then it returns the sum of the volumes in each daily bar during the period specified. If not specified, the value will default to contract. For aggregate equities queries (such as weekly, monthly or yearly), this parameter can be set to sum to return the sum of the volumes in each daily bar during the period specified. If not specified, then the average volume is returned.

Type

enum (A type which includes a list of valid possible values.)

Example

`sum`

Valid Values

total, sum, contract, sumcontract, sumtotal

nearby*optional*

This parameter specifies the offset from the front month for 'nearest' queries (data parameter set to dailynearest, weeklynearest, monthlynearest, quarterlynearest and yearlynearest). The default value for this parameter is 1, which sets nearest queries to the most current front month. If set to a value greater than 1, then the nth front month is used (for example, in August of 2010, ESU10 would be the current front month, so nearby=2 would use ESZ10, nearby=3 would use ESH11, etc.) This parameter is ignored for all other queries. Alternatively, the same functionality provided by the nearby parameter can be achieved using the symbol notation symbol=RS\*n, where RS is the root symbol and n is the nth front month (i.e. symbol=ES\*1, symbol=YM\*3, etc.). When using this notation on the symbol parameter, the nearby parameter should be omitted.

Type

int (A numeric type defining a whole number. (example: 2))

Example

`1`

jerq*optional*

Whether to merge with JERQ data.

Type

boolean (A logical type representing the truth of a value as 'true' or 'false'.)

Example

`true`

Default

1

exchange*optional*

The list of valid exchange codes to limit symbol search.

Type

list (A comma or semi-colon delimited string.)

Example

`NYSE,AMEX,NASDAQ`

backAdjust*optional*

This parameter specifies whether the contracts in the series will be adjusted based on the roll-gap between the closing prices of the current contract and the previous contract on the day of the switch. Valid values are true and false. If not specified, the default value is false resulting in a non-adjusted query. This parameter only applies to multi-contract futures queries and is ignored for all other queries.

Type

enum (A type which includes a list of valid possible values.)

Example

`false`

Default

false

Valid Values

true, false

daysToExpiration*optional*

This parameter specifies the number of calendar days prior to a contract expiration when the series of contracts will be switched to the next contract in the series. Valid values are 0 through 60. A value of 0 will tell the system to use the day of expiration. If not specified, the default value (1) is used, resulting in each contract in the series to run until (and including) the day prior to its expiration. This parameter only applies to multi-contract futures queries and is ignored for all other queries.

Type

enum (A type which includes a list of valid possible values.)

Example

`1`

Default

1

Valid Values

0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60

contractRoll*optional*

For futures, multi-contract nearest queries (data parameter set to dailynearest, weeklynearest, monthlynearest, quarterlynearest or yearlynearest), this parameter can be set to one of two values (expiration, combined), and determines how the switch from one contract to the next in the series is calculated. When the value specified is 'expiration', the switch from one contract to the next in the series will be based on the expiration date (and the value of the 'daysToExpiration' parameter if specified). When the value specified is 'combined', a combination of volume and openinterest will be used to determine when to switch from one contract to the next in the series (when using this value, the 'daysToExpiration' parameter is ignored).

Type

enum (A type which includes a list of valid possible values.)

Example

`expiration`

Default

expiration

Valid Values

expiration, combined

Outputs

symbol
  
always returned

A symbol or code that identifies a financial instrument.

*string*  
A sequence of characters. (example: GOOG)

timestamp
  
always returned

The exchange time of the price. Format: HH:MM:SS.FFF

*dateTime*  
A date and time in the format of YYYY-MM-DD HH:MI:SS<TIMEZONE\_OFFSET>.

tradingDay
  
always returned

The date of the trade. Format: YYYY-MM-DD

*date*  
A date in the format of YYYY-MM-DD.

sessionCode

A code used to differentiate between composite market prices, overnight session prices, and day session prices for futures. Not all futures exchanges use session codes. "G" is electronic session and "R" is pit session.

*string*  
A sequence of characters. (example: GOOG)

tickPrice

The price traded for a single transaction.

*double*  
A numeric type defining a number with fractional parts. (example: 2.14)

tickSize

The volume traded for a single transaction.

*int*  
A numeric type defining a whole number. (example: 2)

open

The opening (first) price for the period.

*double*  
A numeric type defining a number with fractional parts. (example: 2.14)

high

The highest traded price for the period.

*double*  
A numeric type defining a number with fractional parts. (example: 2.14)

low

The lowest traded price for the period.

*double*  
A numeric type defining a number with fractional parts. (example: 2.14)

close

The last traded price for the period.

*double*  
A numeric type defining a number with fractional parts. (example: 2.14)

volume

The quantity of shares or contracts traded per the period.

*int*  
A numeric type defining a whole number. (example: 2)

openInterest

The total number of options and/or futures contracts that have not been offset.

*int*  
A numeric type defining a whole number. (example: 2)

Status Code Responses

200

OK

Success

400

Bad Request

The request was invalid, please see the message for more information.

500

Internal Server Error

Something is not working correctly, please contact support.

JSON

GET

```
GET https://ondemand.websol.barchart.com/getHistory.json?apikey=YOUR_API_KEY&symbol=AAPL&type=minutes&startDate=20100101&endDate=20130101&maxRecords=10&interval=60&order=asc&sessionFilter=EFK&splits=true&dividends=true&volume=sum&nearby=1&jerq=true&exchange=NYSE%2CAMEX%2CNASDAQ&backAdjust=false&daysToExpiration=1&contractRoll=expiration  
Host: ondemand.websol.barchart.com
```

POST

```
POST https://ondemand.websol.barchart.com/getHistory.json  
Host: ondemand.websol.barchart.com  
Content-Type: application/x-www-form-urlencoded  
Content-Length: length  
  
apikey=YOUR_API_KEY&symbol=AAPL&type=minutes&startDate=20100101&endDate=20130101&maxRecords=10&interval=60&order=asc&sessionFilter=EFK&splits=true÷nds=true&volume=sum&nearby=1&jerq=true&exchange=NYSE%2CAMEX%2CNASDAQ&backAdjust=false&daysToExpiration=1&contractRoll=expiration
```

Response

```
{
    "status": {
        "code": 200,
        "message": "Success."
    },
    "results": [
        {
            "symbol": "AAPL",
            "timestamp": "2012-12-28T13:00:00-05:00",
            "tradingDay": "2012-12-28",
            "open": 15.4562,
            "high": 15.4674,
            "low": 15.4297,
            "close": 15.4391,
            "volume": 30926625
        },
        {
            "symbol": "AAPL",
            "timestamp": "2012-12-28T14:00:00-05:00",
            "tradingDay": "2012-12-28",
            "open": 15.4386,
            "high": 15.4457,
            "low": 15.4067,
            "close": 15.4279,
            "volume": 38544950
        },
        {
            "symbol": "AAPL",
            "timestamp": "2012-12-28T15:00:00-05:00",
            "tradingDay": "2012-12-28",
            "open": 15.4277,
            "high": 15.5193,
            "low": 15.334,
            "close": 15.3735,
            "volume": 120344964
        },
        {
            "symbol": "AAPL",
            "timestamp": "2012-12-31T09:00:00-05:00",
            "tradingDay": "2012-12-31",
            "open": 15.4067,
            "high": 15.8253,
            "low": 15.3606,
            "close": 15.8111,
            "volume": 113161874
        },
        {
            "symbol": "AAPL",
            "timestamp": "2012-12-31T10:00:00-05:00",
            "tradingDay": "2012-12-31",
            "open": 15.8111,
            "high": 15.9104,
            "low": 15.7423,
            "close": 15.848,
            "volume": 126384544
        },
        {
            "symbol": "AAPL",
            "timestamp": "2012-12-31T11:00:00-05:00",
            "tradingDay": "2012-12-31",
            "open": 15.8494,
            "high": 15.8856,
            "low": 15.7562,
            "close": 15.8476,
            "volume": 72055899
        },
        {
            "symbol": "AAPL",
            "timestamp": "2012-12-31T12:00:00-05:00",
            "tradingDay": "2012-12-31",
            "open": 15.8509,
            "high": 15.9505,
            "low": 15.7493,
            "close": 15.8802,
            "volume": 88741519
        },
        {
            "symbol": "AAPL",
            "timestamp": "2012-12-31T13:00:00-05:00",
            "tradingDay": "2012-12-31",
            "open": 15.8793,
            "high": 15.9792,
            "low": 15.8235,
            "close": 15.8591,
            "volume": 79615370
        },
        {
            "symbol": "AAPL",
            "timestamp": "2012-12-31T14:00:00-05:00",
            "tradingDay": "2012-12-31",
            "open": 15.8615,
            "high": 16.1543,
            "low": 15.8585,
            "close": 16.1218,
            "volume": 101928423
        },
        {
            "symbol": "AAPL",
            "timestamp": "2012-12-31T15:00:00-05:00",
            "tradingDay": "2012-12-31",
            "open": 16.1171,
            "high": 16.1572,
            "low": 16.016,
            "close": 16.0842,
            "volume": 134440689
        }
    ]
}
```

XML

GET

```
GET https://ondemand.websol.barchart.com/getHistory.xml?apikey=YOUR_API_KEY&symbol=AAPL&type=minutes&startDate=20100101&endDate=20130101&maxRecords=10&interval=60&order=asc&sessionFilter=EFK&splits=true&dividends=true&volume=sum&nearby=1&jerq=true&exchange=NYSE%2CAMEX%2CNASDAQ&backAdjust=false&daysToExpiration=1&contractRoll=expiration  
Host: ondemand.websol.barchart.com
```

POST

```
POST https://ondemand.websol.barchart.com/getHistory.xml  
Host: ondemand.websol.barchart.com  
Content-Type: application/x-www-form-urlencoded  
Content-Length: length  
  
apikey=YOUR_API_KEY&symbol=AAPL&type=minutes&startDate=20100101&endDate=20130101&maxRecords=10&interval=60&order=asc&sessionFilter=EFK&splits=true÷nds=true&volume=sum&nearby=1&jerq=true&exchange=NYSE%2CAMEX%2CNASDAQ&backAdjust=false&daysToExpiration=1&contractRoll=expiration
```

Response

```
<?xml version="1.0" encoding="utf-8"?>
<getHistory>
  <status>
    <code>200</code>
    <message>Success.</message>
  </status>
  <item>
    <symbol>AAPL</symbol>
    <timestamp>2012-12-28T13:00:00-05:00</timestamp>
    <tradingDay>2012-12-28</tradingDay>
    <open>15.4562</open>
    <high>15.4674</high>
    <low>15.4297</low>
    <close>15.4391</close>
    <volume>30926625</volume>
  </item>
  <item>
    <symbol>AAPL</symbol>
    <timestamp>2012-12-28T14:00:00-05:00</timestamp>
    <tradingDay>2012-12-28</tradingDay>
    <open>15.4386</open>
    <high>15.4457</high>
    <low>15.4067</low>
    <close>15.4279</close>
    <volume>38544950</volume>
  </item>
  <item>
    <symbol>AAPL</symbol>
    <timestamp>2012-12-28T15:00:00-05:00</timestamp>
    <tradingDay>2012-12-28</tradingDay>
    <open>15.4277</open>
    <high>15.5193</high>
    <low>15.334</low>
    <close>15.3735</close>
    <volume>120344964</volume>
  </item>
  <item>
    <symbol>AAPL</symbol>
    <timestamp>2012-12-31T09:00:00-05:00</timestamp>
    <tradingDay>2012-12-31</tradingDay>
    <open>15.4067</open>
    <high>15.8253</high>
    <low>15.3606</low>
    <close>15.8111</close>
    <volume>113161874</volume>
  </item>
  <item>
    <symbol>AAPL</symbol>
    <timestamp>2012-12-31T10:00:00-05:00</timestamp>
    <tradingDay>2012-12-31</tradingDay>
    <open>15.8111</open>
    <high>15.9104</high>
    <low>15.7423</low>
    <close>15.848</close>
    <volume>126384544</volume>
  </item>
  <item>
    <symbol>AAPL</symbol>
    <timestamp>2012-12-31T11:00:00-05:00</timestamp>
    <tradingDay>2012-12-31</tradingDay>
    <open>15.8494</open>
    <high>15.8856</high>
    <low>15.7562</low>
    <close>15.8476</close>
    <volume>72055899</volume>
  </item>
  <item>
    <symbol>AAPL</symbol>
    <timestamp>2012-12-31T12:00:00-05:00</timestamp>
    <tradingDay>2012-12-31</tradingDay>
    <open>15.8509</open>
    <high>15.9505</high>
    <low>15.7493</low>
    <close>15.8802</close>
    <volume>88741519</volume>
  </item>
  <item>
    <symbol>AAPL</symbol>
    <timestamp>2012-12-31T13:00:00-05:00</timestamp>
    <tradingDay>2012-12-31</tradingDay>
    <open>15.8793</open>
    <high>15.9792</high>
    <low>15.8235</low>
    <close>15.8591</close>
    <volume>79615370</volume>
  </item>
  <item>
    <symbol>AAPL</symbol>
    <timestamp>2012-12-31T14:00:00-05:00</timestamp>
    <tradingDay>2012-12-31</tradingDay>
    <open>15.8615</open>
    <high>16.1543</high>
    <low>15.8585</low>
    <close>16.1218</close>
    <volume>101928423</volume>
  </item>
  <item>
    <symbol>AAPL</symbol>
    <timestamp>2012-12-31T15:00:00-05:00</timestamp>
    <tradingDay>2012-12-31</tradingDay>
    <open>16.1171</open>
    <high>16.1572</high>
    <low>16.016</low>
    <close>16.0842</close>
    <volume>134440689</volume>
  </item>
</getHistory>
```

CSV

GET

```
GET https://ondemand.websol.barchart.com/getHistory.csv?apikey=YOUR_API_KEY&symbol=AAPL&type=minutes&startDate=20100101&endDate=20130101&maxRecords=10&interval=60&order=asc&sessionFilter=EFK&splits=true&dividends=true&volume=sum&nearby=1&jerq=true&exchange=NYSE%2CAMEX%2CNASDAQ&backAdjust=false&daysToExpiration=1&contractRoll=expiration  
Host: ondemand.websol.barchart.com
```

POST

```
POST https://ondemand.websol.barchart.com/getHistory.csv  
Host: ondemand.websol.barchart.com  
Content-Type: application/x-www-form-urlencoded  
Content-Length: length  
  
apikey=YOUR_API_KEY&symbol=AAPL&type=minutes&startDate=20100101&endDate=20130101&maxRecords=10&interval=60&order=asc&sessionFilter=EFK&splits=true÷nds=true&volume=sum&nearby=1&jerq=true&exchange=NYSE%2CAMEX%2CNASDAQ&backAdjust=false&daysToExpiration=1&contractRoll=expiration
```

Response

```
symbol,timestamp,tradingDay,open,high,low,close,volume
"AAPL","2012-12-28T13:00:00-05:00","2012-12-28","15.4562","15.4674","15.4297","15.4391","30926625"
"AAPL","2012-12-28T14:00:00-05:00","2012-12-28","15.4386","15.4457","15.4067","15.4279","38544950"
"AAPL","2012-12-28T15:00:00-05:00","2012-12-28","15.4277","15.5193","15.334","15.3735","120344964"
"AAPL","2012-12-31T09:00:00-05:00","2012-12-31","15.4067","15.8253","15.3606","15.8111","113161874"
"AAPL","2012-12-31T10:00:00-05:00","2012-12-31","15.8111","15.9104","15.7423","15.848","126384544"
"AAPL","2012-12-31T11:00:00-05:00","2012-12-31","15.8494","15.8856","15.7562","15.8476","72055899"
"AAPL","2012-12-31T12:00:00-05:00","2012-12-31","15.8509","15.9505","15.7493","15.8802","88741519"
"AAPL","2012-12-31T13:00:00-05:00","2012-12-31","15.8793","15.9792","15.8235","15.8591","79615370"
"AAPL","2012-12-31T14:00:00-05:00","2012-12-31","15.8615","16.1543","15.8585","16.1218","101928423"
"AAPL","2012-12-31T15:00:00-05:00","2012-12-31","16.1171","16.1572","16.016","16.0842","134440689"
```

PHP

```
<?php

$ondemand = new SoapClient('https://ondemand.websol.barchart.com/service?wsdl');

$params = [
    'apikey' => 'YOUR_API_KEY',
    'symbol' => 'AAPL',
    'type' => 'minutes',
    'startDate' => '20100101',
    'endDate' => '20130101',
    'maxRecords' => '10',
    'interval' => '60',
    'order' => 'asc',
    'sessionFilter' => 'EFK',
    'splits' => 'true',
    'dividends' => 'true',
    'volume' => 'sum',
    'nearby' => '1',
    'jerq' => 'true',
    'exchange' => 'NYSE,AMEX,NASDAQ',
    'backAdjust' => 'false',
    'daysToExpiration' => '1',
    'contractRoll' => 'expiration',
];

$result = $ondemand->getHistory($params);
var_dump($result);
```

Classic ASP

```
Dim ondemand
Dim result

Set ondemand = Server.CreateObject("MSSOAP.SoapClient30")
ondemand.ClientProperty("ServerHTTPRequest") = True
ondemand.MSSoapInit("https://ondemand.websol.barchart.com/service?wsdl")

Set result = ondemand.getHistory("YOUR_API_KEY", "AAPL", "minutes", "20100101", "20130101", "10", "60", "asc", "EFK", "true", "true", "sum", "1", "true", "NYSE,AMEX,NASDAQ", "false", "1", "expiration")
```

Perl

```
use SOAP::Lite;
use SOAP::WSDL;

my $ondemand = SOAP::Lite
    -> service('https://ondemand.websol.barchart.com/service?wsdl');

my $result = $ondemand->getHistory('YOUR_API_KEY', 'AAPL', 'minutes', '20100101', '20130101', '10', '60', 'asc', 'EFK', 'true', 'true', 'sum', '1', 'true', 'NYSE,AMEX,NASDAQ', 'false', '1', 'expiration');

print $result;
```

Python

```
from suds.client import Client
ondemand = Client('https://ondemand.websol.barchart.com/service?wsdl')

result = ondemand.service.getHistory('YOUR_API_KEY', 'AAPL', 'minutes', '20100101', '20130101', '10', '60', 'asc', 'EFK', 'true', 'true', 'sum', '1', 'true', 'NYSE,AMEX,NASDAQ', 'false', '1', 'expiration')

print(result)
```

Ruby

```
require 'savon'

ondemand = Savon.client(wsdl: 'https://ondemand.websol.barchart.com/service?wsdl')

response = ondemand.call(
    :getHistory,
    message: {
        apikey: 'YOUR_API_KEY',
        symbol: 'AAPL',
        type: 'minutes',
        startDate: '20100101',
        endDate: '20130101',
        maxRecords: '10',
        interval: '60',
        order: 'asc',
        sessionFilter: 'EFK',
        splits: 'true',
        dividends: 'true',
        volume: 'sum',
        nearby: '1',
        jerq: 'true',
        exchange: 'NYSE,AMEX,NASDAQ',
        backAdjust: 'false',
        daysToExpiration: '1',
        contractRoll: 'expiration',
    }
)

response.body
```

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