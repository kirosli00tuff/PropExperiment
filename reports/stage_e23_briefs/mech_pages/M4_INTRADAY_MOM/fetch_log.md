# M4_INTRADAY_MOM fetch and query log (MechanismReaderM4_INTRADAY_MOM-OpusHigh, Stage E.23 P1.2)

All times America/Vancouver (PDT, -07:00). sha256 of the raw file as saved.

## Reused saved full text (not refetched)
| key | path | sha256 |
|---|---|---|
| BDLM2021 | reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md | 18cb436e9d18cb3eff3565cddfe85b35fa1c5d5d8bf2afb85df42b6ab49e0465 |
| BDLM2021-pdf | reports/stage_e10_research/overnight/baltussen_intramom.txt (clean JFE text; pdf 623ba824...ec57) | 2f4381fb36833b7406d899c4961b31accac53387991f67cf326b74416c3527c4 |
| BK2012 | reports/stage_e10_research/overnight/baltas_kosowski_momf.txt (pdf alongside: f48c15bb...a5a) | 36807a569a69dde96834e8e97cdf3620c502de968a6701bf74b2a247732d1936 |
| BBBM2021 | reports/stage_e20_briefs/shared/barbon_beckmeyer_buraschi_moerke_letf.pdf.txt | c3a725db9e1fd4a4268af8742e46cc422de2b34a65e960988f285c2198f1fd01 |
| BDS2024 | reports/stage_e20_briefs/pages/ZC/baltussen_da_soebhag_eod_reversal_2024.pdf.txt | 64b43ec66a1ba618d8e19a877d3bdff506b0eaa989a3ba33caebdb390b443585 |

## Fetches
| time (PDT) | URL | saved as | sha256 | tool |
|---|---|---|---|---|
| 2026-10-17T02:18:53-07:00 | https://www3.nd.edu/~zda/Indexing.pdf | bvd_2019_jfe_indexing.pdf (+ .pdf.txt via pdftotext) | 05333bbdbe54c931c52338680255de171edbe86f76129201bce041b3637c6010 | curl (author's own page) |
| 2026-10-17T02:20:08-07:00 | https://c.mql5.com/forextsd/forum/173/intraday_momentum_-_the_first_half-hour_return_predicts_the_last_half-hour_return.pdf | ghlz_2015_wp_mql5.pdf (+ .pdf.txt) | 050d5680d1424a5f53aeb175de283bc796b130be3874abf319aa1980941cc374 | curl (third-party host of the authors' Dec 2015 working paper; static file) |
| 2026-10-17T02:20:47-07:00 | https://www3.nd.edu/~zda/commodity.pdf | dtty_2024_commodity_serial.pdf (+ .pdf.txt) | 1677446a35f31ca247e8d23f0f4f319dc7a25223b5fb402e67141a5a1fcc36ae | curl (author's own page) |
| 2026-10-17T02:22:24-07:00 | https://verso.uidaho.edu/esploro/outputs/journalArticle/Intraday-market-momentum-in-coffee-futures/996867269001851 | uidaho_coffee_intraday_mom.html (2.3 kB JS shell, no text) | af1743206dc653d1e48304d896aa243be2755efd6ca1937752ee5f90cf72a52f | curl: FAILED (JS-rendered) |
| 2026-10-17T02:22:32-07:00 | same URL | uidaho_coffee_intraday_mom.md (162 bytes, empty) | d8206175998107aa1712d7590e3ccc18ee47d8275c2b57b67710529e19f7f6c8 | scrapling extract fetch: FAILED (no content) |
| 2026-10-17T02:22:41-07:00 | https://api.openalex.org/works?search=intraday%20market%20momentum%20coffee%20futures&per-page=3 | openalex_coffee.json (no abstract, no OA link; DOI 10.1016/j.jcomm.2025.100537) | ae6cbd7d80d896f0933198adbd856fca2881c12966b4740c996de43240ddafce | curl (OpenAlex API) |
| ~2026-10-17T02:22:50-07:00 | https://www.sciencedirect.com/science/article/pii/S2405851325000534 (guessed PII) | not saved | n/a | WebFetch: HTTP 403; not retried (Firecrawl not used: guessed URL, paywalled publisher) |
| 2026-10-17T02:23:06-07:00 | https://www.nbim.no/en/news-and-insights/publications/discussion-notes/2014/momentum-in-futures-market/ | nbim_2014_momentum_futures.html | 77129e00e615feedafa0f8fb0a571dacb1b868062ebe78e55b830e8efd0f2c5c | curl |
| 2026-10-17T02:23:18-07:00 | https://www.nbim.no/globalassets/documents/dicussion-paper/2014/discussionnote_time_series_momentum_latest.pdf | nbim_2014_tsmom_note.pdf (+ .pdf.txt) | 1ab4e7bfc49b8211dd71a3bd909da7770291373d6c183b1b8fa6c158067d061a | curl |
| 2026-10-17T02:24:01-07:00 | https://arxiv.org/abs/2606.29591 | arxiv_2606.29591_abs.html (abstract page only) | 6ac40ab7fc3b35ba414e4ba745a9296bbe571878aa26d1cd831a225e4c82ddb2 | curl |

Figure readings (rendered locally from saved PDFs with pdftoppm, read visually; not text): tmp/M4_INTRADAY_MOM_bdlm_p17-17.png (BDLM2021 Fig. 5 and Table 11, page 393, from reports/stage_e10_research/overnight/baltussen_intramom.pdf sha256 623ba82490acd01546f568cf582de5a9b45dfbd97731cd548cb119d7a0acec57); tmp/M4_INTRADAY_MOM_nbim_p8-08.png (NBIM2014 Chart 2, page 8).

## Queries
| # | time (PDT) | tool | query | kept |
|---|---|---|---|---|
| 1 | 2026-10-17T02:18-07:00 | WebSearch | Baltussen van Bekkum Da "Indexing and stock market serial dependence around the world" pdf | BvD2019 (nd.edu copy fetched) |
| 2 | 2026-10-17T02:19-07:00 | WebSearch | Gao Han Li Zhou "market intraday momentum" next day reversal last half-hour return subsequent days | none new (abstract-level summaries only) |
| 3 | 2026-10-17T02:20-07:00 | WebSearch | "Market intraday momentum" Gao Han Li Zhou pdf olin.wustl.edu | GHLZ working paper (mql5 copy fetched) |
| 4 | 2026-10-17T02:20-07:00 | WebSearch | Barbon Buraschi "gamma fragility" daily autocorrelation index returns dealer gamma pdf | none kept (stock-level, intraday; abstract-level only) |
| 5 | 2026-10-17T02:20-07:00 | WebSearch | commodity futures daily return autocorrelation short-term reversal one-day lagged return predicts next week returns time series | DTTY2024 (nd.edu copy fetched) |
| 6 | 2026-10-17T02:22-07:00 | WebSearch | intraday momentum futures persistence over following days weekly horizon "intraday momentum" multi-day holding continuation reversal study | coffee futures paper (JCM 2025): full text unreachable, [unverified] |
| 7 | 2026-10-17T02:22-07:00 | WebSearch | short-term trend following futures lookback one week decay after 2010 time series momentum short horizon performance study pdf | NBIM2014 (fetched) |
| 8 | 2026-10-17T02:23-07:00 | WebSearch | E-mini S&P 500 futures daily return negative autocorrelation 2010-2023 short-term reversal index level evidence paper | arXiv 2606.29591 (abstract only) |
| 9 | 2026-10-17T02:24-07:00 | WebSearch | "last half-hour" OR "end-of-day" futures return predicts next week returns continuation close-to-close 5-day 20-day horizon | none new |
| 10 | 2026-10-17T02:25-07:00 | WebSearch | futures "daily" time-series momentum one-day lookback return predictability next 5 to 20 days commodities bonds currencies post-2010 evidence | none new (MOP 2012 and NBIM again) |

Local greps (no web): reports/stage_e13_briefs/pages/, reports/stage_e10_research/overnight/, reports/stage_e20_briefs/ (pages, shared), reports/stage_e21_briefs/ for: serial dependence, Korajczyk, Gao/Han, gamma fragility, van Bekkum, next day, revers. Kept: BDLM2021 (two copies), BK2012, BBBM2021, BDS2024; Li-Sakkas-Urquhart and the MNQ arXiv 2605.04004 had no multi-day content.
No WebSearch over-budget notice seen (10 of 60 used). No throttling or blocks except the coffee-paper failures above.
