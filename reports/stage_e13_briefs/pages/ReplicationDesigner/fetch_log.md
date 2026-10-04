# Fetch log: ReplicationDesigner-OpusXHigh (Stage E.13 Task 4)

Method "curl" = plain `curl -sL` with browser headers (research_rules.md fetch order step 1), via the helper
in the worker's scratch folder. Pages are saved raw in this folder and read by grep only. sha256 is of the
saved file. Terms: databento.com terms page saved (R03) is a script shell; no automated-access clause was
found in its text ("not found"). eia.gov: U.S. government publications are public domain (R04, quote:
"U.S. government publications are in the public domain and are not subject to copyright protection").
cmegroup.com was NOT fetched (its terms forbid automated access, E.12 record); the CME facts used come from
the program's existing records and a news-wire copy of CME's press release (R18).

WebSearch calls: 8 (no budget notice seen). Firecrawl calls: 0. Scrapling: not used.

| id | URL | fetched (UTC) | method | saved file | sha256 | page date shown | terms status | note |
|---|---|---|---|---|---|---|---|---|
| R01 | https://databento.com/datasets/GLBX.MDP3 | 2026-10-03T21:45:15Z | curl | databento_glbx_mdp3.html | 009a856a2461b74c2fcc76731e5817902dc7b74cc89b6ea2da9c2148bc711d6f | no date shown (data_end 2026-09-30 in page data) | not found (R03) | quotes: `"temporalCoverage":"2010-06-06/.."`; `"history_from":[0,"2010-06-06"]`; ohlcv-1m `"start":[0,"2010-06-06T00:00:00.000000000Z"]` |
| R02 | https://databento.com/docs/venues-and-datasets/glbx-mdp3 | 2026-10-03T21:45:16Z | curl | databento_docs_glbx.html | b7721e00e1db5d69f070067f69ea2c45eddaf37974ad96626b14c036c1cd81b9 | no date shown | not found | FAILED for content: script shell, no dataset text; not used |
| R03 | https://databento.com/terms | 2026-10-03T21:45:16Z | curl | databento_terms.html | 5ba3e59b1646ed13ed4aa6f5502957866df3cbca273b2b95f897667601ff523f | no date shown | not found | script shell; no scraping/automated clause in the saved text |
| R04 | https://www.eia.gov/about/copyrights_reuse.php | 2026-10-03T21:45:16Z | curl | eia_copyrights.html | 7f25492108c0654a2c4b89b7ec1593dcfa84ea934eb8a333fdc49b99fd5883af | no date shown | allows (public domain) | terms page for eia.gov |
| R05 | https://www.eia.gov/dnav/ng/hist/rngwhhdA.htm | 2026-10-03T21:46:00Z | curl | eia_henryhub_spot_annual.html | 346f0c22637ab1d05932be63f6a305f6b27cd74442ebbc2dc4dec1d9e0dd256b | release date 9/30/2026 | allows | Henry Hub spot, annual; 2013 cell blank in the table as fetched |
| R06 | https://www.eia.gov/dnav/ng/hist/n9070us2A.htm | 2026-10-03T21:46:09Z | curl | eia_dry_production_annual.html | 4af1cca89d3a7f75279c478e6fcc9e6833bb8549987b32c66f5f24fa48bb1fa0 | release date 9/30/2026 | allows | U.S. dry gas production, annual, MMcf |
| R07 | https://www.eia.gov/dnav/ng/hist/n9133us2A.htm | 2026-10-03T21:46:18Z | curl | eia_lng_exports_annual.html | b6d4eb2106672b4378616647eb06751c66d87846783601a4215f8fbd1b3f806a | release date 9/30/2026 | allows | U.S. LNG exports, annual, MMcf |
| R08 | https://www.eia.gov/outlooks/steo/uncertainty/ | 2026-10-03T21:46:27Z | curl | eia_steo_uncertainty.html | c1a10034379332c98bf97d79bbe903164988c3e093ef1f043db825674901023e | n/a | allows | FAILED: HTTP 404; not used |
| R09 | https://www.eia.gov/todayinenergy/detail.php?id=53579 | 2026-10-03T21:47:04Z | curl | eia_tie_53579_record_volatility_q1_2022.html | ca0efbf8b74be0ddc9a7bf8bcd6878bfbb80937b99f1ae5642627f3cc91eb7da | August 24, 2022 | allows | 2022 volatility; definition of the measure |
| R10 | https://www.eia.gov/todayinenergy/detail.php?id=62203 | 2026-10-03T21:47:12Z | curl | eia_tie_62203_calmed_after_2022.html | 1720bebd9090537dd72c1535ab0ebdca15988a8385565045360f19fdfc034544 | June 4, 2024 | allows | 2022 91%, 2023 69%, 1Q24 80% |
| R11 | https://www.eia.gov/naturalgas/weekly/archivenew_ngwu/2018/12_20/ | 2026-10-03T21:47:57Z | curl | eia_ngwu_2018_12_20.html | 134cbbfc6a6f7858de528d6cc5d6ff9480c3ee4056556b7b5ee0087a06e3b563 | Natural Gas Weekly Update of 2018-12-20 (URL) | allows | "volatility ... was low for most of 2018" |
| R12 | https://www.eia.gov/todayinenergy/detail.php?id=42455 | 2026-10-03T21:48:06Z | curl | eia_tie_42455.html | a476a2bcea5bf627febf295c0ec50c59bb3cbba4abadb34ec6d3a5ba4554e229 | January 9, 2020 | allows | no volatility passage; not used |
| R13 | https://www.eia.gov/todayinenergy/detail.php?id=37713 | 2026-10-03T21:48:14Z | curl | eia_tie_37713.html | 20a7a68beb1975bce062ca61fa6ce1e82a0a385b0e8fb0cde39a8f3630c86a32 | December 7, 2018 | allows | not used |
| R14 | https://www.eia.gov/todayinenergy/detail.php?id=24672 | 2026-10-03T21:48:43Z | curl | eia_tie_24672.html | 6721688d09b2aa8be42564e9949f627db0e0fba87494f6f7b2b555a182a55373 | January 25, 2016 | allows | method only (Black-Scholes implied vol); no figure; not used |
| R15 | https://www.eia.gov/outlooks/steo/archives/Apr19.pdf | 2026-10-03T21:49:05Z | curl | eia_steo_apr19.pdf (+ eia_steo_apr19.txt, pdftotext -layout, sha256 33da85089e4aec186cdabc51748a965bd64fb8f5946170b853d3442b16f8eb6a) | 8353c4e85073d9bccbd474925501761b90f5c57935071a469b6bb6de81aef738 | STEO April 2019 | allows | "implied volatility averaged 21.3% in March, lower than the five-year average of 37.7%" |
| R16 | https://www.eia.gov/naturalgas/weekly/archivenew_ngwu/2022/08_11/ | 2026-10-03T21:49:33Z | curl | eia_ngwu_2022_08_11.html | 1ba3ed267a8ff3e8b3b5a5e7765bddaa25a94add3eb998b3c3654acf195bdb32 | Natural Gas Weekly Update of 2022-08-11 (URL) | allows | "five-year (2017–21) average of 48%" |
| R17 | https://www.eia.gov/todayinenergy/detail.php?id=65784 | 2026-10-03T21:49:42Z | curl | eia_tie_65784_vol_h1_2025.html | 3fbcf4d46cc0a249390b3d25627ed7b23d4721fe7ec44b6a503e6a1370e2290d | July 24, 2025 | allows | 4Q24 81%, mid-2025 69% |
| R18 | https://mondovisione.com/media-and-resources/news/cme-group-to-launch-micro-henry-hub-futures-and-options-on-november-6-2023927/ | 2026-10-03T21:50:11Z | curl | mondovisione_mng_launch_2023-09-27.html | 417386c0848f3e98a66520ed43110770cadcb882aa7c2edd6318164981bc1f4c | 27/09/2023 | not checked | news-wire copy of CME's press release |
| R19 | https://www.eia.gov/todayinenergy/detail.php?id=67224 | 2026-10-03T21:50:26Z | curl | eia_tie_67224_sabine_pass_10yrs.html | a14c8e1a86600a11a48363975eec53aff6491b54f3a4b075bd94c0f1d33d5084 | February 24, 2026 | allows | first Lower-48 LNG cargo 2016-02-24 |
| R20 | https://www.eia.gov/tools/faqs/faq.php?id=907&t=8 | 2026-10-03T21:50:46Z | curl | eia_faq_907_shale_gas.html | b3f13f4a2586b8bbc6650f5a8e6fdf44136109a624703124a7cd6f48195884ab | last updated September 19, 2024 | allows | shale share of 2023 dry production |

In-repository records also used (not fetched in this stage): ledger/databento_spend.jsonl (Databento's own
error text on the 2010-06 quote: "the available start of dataset GLBX.MDP3 ('2010-06-06 00:00:00+00:00')");
reports/stage_e0_topstep_facts.json (F1.4, MNG on Topstep's permitted list); reports/stage_e2a_vehicles.json
(NG and MNG vehicle arithmetic).
