# SpecReaderTrend fetch log (Stage E.21 Step 1)

Times are America/Vancouver local (from `date -Iseconds`).

| id | URL | fetched | method | saved file | sha256 | page date shown | terms status | note |
|---|---|---|---|---|---|---|---|---|
| R01 | (on disk, no fetch) reports/stage_e13_briefs/pages/TrendCarry/mop2012.pdf (E.13 F01, https://pages.stern.nyu.edu/~lpederse/papers/TimeSeriesMomentum.pdf) | read 2026-10-14T03:13:31-07:00 | local grep (pdftotext raw re-extract in private scratch) | (E.13 file) | 7682f8e97eb4b77591dc85e36731ff51ed031970cdde81678108734db9478379 | JFE 104 (2012) 228-250 | n/a (no fetch) | hash matches E.13 log F01 |
| R02 | (on disk, no fetch) reports/stage_e13_briefs/pages/TrendCarry/hop_century_jpm.pdf (E.13 F06, https://fairmodel.econ.yale.edu/ec439/hurst.pdf) | read 2026-10-14T03:14-07:00 | local grep | (E.13 file) | 7b286a9f6cf6925aa9610fc4dcecd15c26c58699c36502938c1e5ec35625b5af | JPM 44(1), Fall 2017 | n/a (no fetch) | hash matches E.13 log F06 |
| R03 | (on disk, no fetch) reports/stage_e13_briefs/pages/TrendCarry/hop_century_tf.pdf (E.13 F05, https://www.TrendFollowing.com/whitepaper/Century_Evidence_Trend_Following.pdf) | read 2026-10-14T03:14-07:00 | local grep | (E.13 file) | f3aa7661b53e3e1e7386f655403e82bea5ca575b7a699d61e06292da55b45a60 | AQR white paper, Fall 2014 (data to Dec 2013) | n/a (no fetch) | hash matches E.13 log F05 |
| R04 | (derived) hop_century_jpm.pdf pages 4-5 rendered with `pdftoppm -r 110` | 2026-10-14T03:16:18-07:00 | pdftoppm render, read as image | hop_jpm_exhibit1_pdfpage4.png ; hop_jpm_exhibit2_pdfpage5.png | a87a32a72131d7c3c2a0e53ee9c64ecd1cc2b97d8bc5059b0a6aa30f525ab25b ; 2d04cf1d2b23b7bd1064d025ce86eaabe0cdca4335754c04b2e31b8f9098595e | JPM Fall 2017 | n/a | Exhibits 1 and 2 are images in the PDF (no text layer); figures transcribed by eye from the render |
| F01 | https://pages.stern.nyu.edu/~lpederse/papers/DemystifyingManagedFutures.pdf | 2026-10-14T03:16:18-07:00 | curl -sL with browser headers | hop2013_demystifying.pdf (+ .txt from pdftotext -layout) | 00155a0a75fa66134637e7288186e887b29425d23c4a088b94ce7f9aa513104f (pdf); 6ab606084b4aaf8414c3e17e9eb6b7c05c5bd1c1bf750457713f1b68f20e9b14 (txt) | "Forthcoming Journal of Investment Management" (data Jan 1985-Jun 2012) | not checked (author's academic page, plain curl) | HTTP 200, 379284 bytes, application/pdf. Hurst, Ooi and Pedersen "Demystifying Managed Futures", cited by HOP 2014 white paper as the methodology source |

No WebSearch, no Firecrawl, no aqr.com fetch. Failed fetches: 0.
