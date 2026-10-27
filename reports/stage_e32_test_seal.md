# Stage E.32 Part 0: the soybean-complex test window is sealed

Sealed 2026-10-26 22:54:51 to 22:55:11 PDT, before any other reading in this stage (no reader was spawned and no
source was read before it). Lead: Opus 5.5 xhigh. Tool: reports/stage_e32_briefs/seal/soy_test_seal.py; tests:
tests/test_e32_soy_test_seal.py (26 passed). Times are America/Vancouver.

## 1. The rule

1. The one-shot test window of the ZM directional program (V51) is **ZM, ZS and ZL, CME trade dates 2017-05-01 to
   2020-11-30** (43 calendar months).
2. **No stage may buy, download or open ZM, ZS or ZL data of any schema dated in that window until a registered test
   stage reads it once.** "Open" means load, decompress, decode, plot, summarise or derive anything from it, by any
   tool. The rule covers every vendor and every frequency (tick, book, bar, daily settlement), free sources included
   (exchange settlement pages, chart sites, Yahoo-style daily series), and data rebuilt from any other file. Literature
   that discusses the period may be read; no data series is extracted from it.
3. The only permitted steps before the test are a cost quote for the test purchase, and only after a funded Databento
   account exists (P9 of reports/stage_e32_discovery_protocol.md), then registration, then the one read.
4. **2024-03-01 onward stays closed** to this program (program embargo; V48 gives no approval). The owned files dated
   2024-03-01 or later (section 3) are closed by rule, not sealed.
5. Window boundaries used for files:
   - Raw vendor files: the UTC span in the file name overlaps [2017-04-30T21:00Z, 2020-11-30T22:00Z). The start is
     16:00 CT on Sunday 2017-04-30, before any pre-open message of trade date 2017-05-01 (its session opens at 19:00
     CT that Sunday); the end is 16:00 CT on 2020-11-30, after that trade date's 13:20 CT close and settlement, and
     before trade date 2020-12-01's pre-open. The rule is conservative: it pulls in the April 2017 ZS and ZL monthly
     ohlcv-1m chunks (range=2017-04-01_2017-05-01), whose last three UTC hours are pre-open time of 2017-05-01.
   - Processed stores and caches: their first..last trade dates overlap 2017-05-01..2020-11-30.
6. E.31's first purchased chunk, range=2020-11-30T220000Z_2020-12-31T220000Z, starts at 16:00 CT on 2020-11-30, after
   trade date 2020-11-30 closed; every record in it belongs to trade date 2020-12-01 or later. It is outside the
   window and stays in plaintext as discovery data.

## 2. What was sealed, and how

Mechanism: data.holdout's own (the program's seal, used for MES holdouts 1 and 2 and the step 2 products' holdout 2),
called from a stage script because harness v14 pins data/holdout.py and refuses any unlisted *.py under data/. For
each file, in order: encrypt and prove the round trip in memory; write the sealed blob (exclusive create, fsync);
read it back and prove the round trip from disk; append the manifest record (path, bytes, sha256 of plaintext and of
the sealed blob); log SEALED; pin the log's prefix in the manifest; only then remove the plaintext.

- Sealed store: data/sealed/SOY_test_v1/ (on /mnt/large-storage through the data/sealed symlink).
- Manifest: docs/soy_test/SOY_TEST_MANIFEST.json (fixed target list of 114 paths, cipher, salt, the phrase's sha256,
  one record per file, the log pin).
- Unlock log: docs/SOY_TEST_UNLOCK_LOG.md, append-only, kept apart from docs/HOLDOUT_UNLOCK_LOG.md on purpose:
  data.holdout.prior_unlocks counts every UNLOCK heading in the shared log that lacks the holdout-2 mark as a
  holdout-1 unlock, so a soybean unlock logged there would raise holdout 1's count.
- Phrase: the store has its own (soy_test_seal.ACKNOWLEDGEMENT), which is also the key material.
- Unseal ceremony (soy_test_seal.unseal_file): refuses unless REGISTRATION.md is non-empty (at least 200 characters,
  naming a metric, a threshold and a decision), the stage fullmatches "E.<n> soy test", a reason of at least 20
  characters is given, the phrase matches, and the caller states the number of prior unlocks. It logs the unlock
  (with the registration's sha256) before any byte is decrypted, and restores each file read-only.
- Guard: `soy_test_seal.py status` (run by reports/stage_e32_briefs/checks.sh at every start and end check) reports
  any in-window ZM, ZS or ZL plaintext that reappears (a re-buy or a rebuilt store) and any ZM, ZS or ZL file whose
  dates cannot be read from its name, and turns all_ok false. `seal` refuses to extend its fixed plan silently.

Sealed files (full list with paths and sha256 in the appendix):

| Class | Root | Files | Span |
|---|---|---|---|
| raw ohlcv-1m monthly chunks | ZS | 44 | 2017-04 to 2020-11 |
| raw ohlcv-1m monthly chunks | ZL | 44 | 2017-04 to 2020-11 |
| raw ohlcv-1m monthly chunks | ZM | 19 | 2019-05 to 2020-11 (no earlier ZM file is owned) |
| step 2 bar store | ZM, ZS, ZL | 3 | trade dates 2019-05-06 to 2024-02-29 |
| ext2010h bar store | ZS, ZL | 2 | trade dates 2010-07-01 to 2019-04-30 |
| E.22 microbook daily cache | ZS, ZL | 2 | dates 2010-07-01 to 2024-02-29 (read from the date column's min and max only) |
| **Total** | | **114** | **117,607,910 bytes** |

The five stores and two caches span the window boundary and were sealed whole, so no script read in-window rows to
split them. Their out-of-window parts (ZS and ZL bars 2010-07 to 2017-04; ZM, ZS and ZL bars 2020-12 to 2024-02) can
be rebuilt from the plaintext raw chunks outside the window if a later stage needs them; E.33 does not (it works
from the MBO and MBP-1 files).

Checks before and after (verbatim key fields; full JSON in reports/stage_e32_briefs/seal/):

```
before (22:54:51)  data.holdout status: all_ok true, unlocks_logged 0 (holdout 1, holdout 2, MCL, MGC, MHG, NG)
before (22:54:51)  soy_test_seal.py status: state not_yet_sealed, all_ok false (exit 1)
seal (22:54:51-22:55:11): {"sealed": 114, "expected": 114}
after  (22:55:11)  soy_test_seal.py status: state sealed, files_expected 114, files_sealed 114, files_ok 114,
                   plaintext_in_window_present [], unclassified_files [], unlock_log_ok true, unlocks_logged 0,
                   all_ok true
after  (22:55:11)  data.holdout status: identical to before (compared as sorted JSON)
```

The 59 store-related test files passed before (1840 passed, 1 skipped) and after the seal (1866 passed, 1 skipped,
the 26 new tests included), and harness v14 still verifies (2e908c81...).

## 3. What stays in plaintext, and why

| Class | Files | Why it is not sealed |
|---|---|---|
| E.31 purchase, 2020-12 to 2024-02: ZM MBO (Z1), ZS MBP-1 (Z2), ZL MBP-1 (Z3), definitions (Z4) | 39 each, plus manifests | Discovery data for E.33; outside the window (section 1, item 6) |
| ohlcv-1m 2020-12 to 2024-02, ZM, ZS, ZL | 39 each | Discovery period |
| ohlcv-1m before the window, ZS and ZL 2010-07 to 2017-03 | 81 each | Before the window |
| ohlcv-1d QM.FUT and ZM.FUT parent, 2023-01-01 to 2026-10-22 | 1 | Outside the window; its 2024-03+ part is closed by rule |
| 2024-03 onward: ohlcv-1m 2025-04 to 2026-06 (15 each), single-day MBP-1 files 2025-05 to 2026-04 (5 each), the research bar stores 2025-04-01 to 2026-06-19 (3) | 63 | Closed by rule (section 1, item 4), not sealed; they were the main program's research period |
| data/vendor/databento/rolls/: ZS and ZL 2010-07-01..2019-05-01 and ZM, ZS, ZL 2019-05-01..2024-03-01 symbology (.json and .jsonl) | 10 spanning the window (16 for the three roots in all) | Reference data: dates mapped to instrument ids and raw symbols, no prices and no volumes. The roll dates of a volume-ranked continuous series do say which contract led volume on a date; judged to carry no directional information, and needed to rebuild out-of-window stores. Open choice OC-0.4 |
| Records of earlier trials on window data (section 4) | see section 4 | They are the audit trail of N = 538; several are pinned by harness v14 (the E.2a funnel files) or by stage freezes. They are exposure, named honestly, not data to re-read: no stage of this program opens them for design purposes |
| Derived files holding window information (X1Verifier row M4): trip, units and per-root result files of E.17, E.20, E.21 and E.22 under reports/ (95 git-tracked files, 84,894,741 bytes), and the E.12, E.14 and E.20 ML caches under ~/.cache/propexp_e12_phase1, propexp_e14_c1 and propexp_e20_search (111 files, 292,738,230 bytes; multi-product panels and fitted states that include ZM, ZS and ZL rows dated in the window) | 206, listed with bytes and sha256 in reports/stage_e32_briefs/seal/derived_unsealed_files.tsv (bytes hashed, nothing decoded) | The report files are tracked by git, so a working-tree seal would not stop a read from history, and they are the audit trail of registered trials; the caches are the fitted state of registered trials (E.12 Gate 0, C1, C1b, E20S). Instead of a seal, the guard is the discovery protocol's data allowlist (P1): E.33 reads only the 156 hashed discovery files and refuses any other data path. Open choice OC-0.5 |
| reports/stage_e20_briefs/pages/ZL/fred_PSOILUSDM.csv | 1 | A monthly IMF global soybean-oil price from FRED, not CME data; not used by this program |

No copy of any sealed file exists elsewhere: the repo's data directories are symlinks to /mnt/large-storage (same
inodes checked), the agent worktrees under .claude/worktrees hold report JSONs only, and a search of
/mnt/large-storage (market_data and Archive) found no other ZM, ZS or ZL data file.

## 4. Earlier exposure to the window

Source: reports/stage_e32_briefs/X1_exposure.md (ExposureInventory-SonnetMed, pure extraction from the E.23
inventory, the stage returns, the trial registry and a counts-only summary of the spend ledger; every row there carries
its file and line), re-verified row by row by X1Verifier-OpusHigh (reports/stage_e32_briefs/X1_verify.md: 311 rows
checked, 303 confirmed, 8 corrected, 0 unsourced, 4 missing rows added), with its corrections applied below. X1 ran
on Sonnet before the user's rule "never Sonnet, for any worker" (2026-10-26 23:15 PDT); the re-verification ran on
claude-opus-5-5 (confirmed from its transcript). The lead's reading of it:

**What earlier stages read in the window.** Only one-minute bars (and stores and caches built from them), for ZS and
ZL from 2017-05 (through the ext2010h store and its raw chunks) and for ZM, ZS and ZL from 2019-05-06 (through the
step 2 store). Records derived from them also remain unsealed on disk: the E.22 K6 trip files, the E.17 H1/H4 units
files, the E.21 per-root results, the E.20 search outputs and the E.12/E.14/E.20 ML caches (section 3, last rows).
No order-book data (MBO, MBP, trades) for the window was ever bought or read: the first mbo, mbp-1 and definition
purchase starts at 2020-11-30T22:00:00Z, the window's exclusive end in soy_test_seal.py (2020-11 was quoted, never
bought).

| Stage | Read | What was computed on window dates | Trials | Outcome |
|---|---|---|---|---|
| E.12 | step 2 stores (2019-05-06..) | store build and raw checks; c/sigma admissibility filter (81 pairs); Gate 0: 273 tests, of which 201 use soy rows (all 192 family-A pooled tests, including the three K6-derived signals (crush gap, limit continuation, WASDE pre-drift) x 3 horizons, and the 9 ZS/ZL/ZM family-B pairs); ridge models fitted out of fold on the panel | 273 Gate 0 tests (in the 471 baseline) | FAIL, 0 passing pairs |
| E.14 | E.12 panel (step 2, 2019-05-06..) | M1: one ridge per horizon (h60, hF) fitted once on the whole panel (27 products incl. ZS, ZL, ZM; 67,797 and 64,695 rows), later applied to NG 2010-2019 | C1-T1/T2, C1b-T1/T2 | C1 stopped at C10 (no statistic); C1b FAIL |
| E.17 | ext2010h (ZS, ZL 2010-07..2019-04) and step 2 (ZS, ZL; ZM on the fallback window from 2019-05-06) | store build; H1 settlement-window momentum (S_p-30 to S_p), H4 intraday reversal of the prior day's H1 move (O_p+1 to S_p-31), pooled over 27 price paths (14 from 2010-07, 10 incl. ZM from 2019-05-06, TN, RTY, HE later); ZM traded 1,043 units in H1 and 998 in H4; H5 combines the H1-H4 result files (no bar read) | E16-H1, H4, H5 | FAIL |
| E.20 | step 2 (ZS, ZL among 17 vehicles; not ZM) | ML search (ridge, LightGBM depth 2) on 36 late-session bar features, horizons h60, h120 and to the close, nested CPCV; ZS and ZL never traded out of sample | E20S-01..45 | FAIL (all 45 negative; DSR 0.00001 at N 528) |
| E.21 | ext2010h and step 2 (ZS, ZL) | 12-month time-series momentum and a trend blend, per-root contributions | E21-T1, T2 (T4 through T2) | FAIL |
| E.22 Part A | step 2 (ZS, ZM, ZL) | confirmation of the K6 members: CP1 momentum into the close (12:45 to 13:14), CP2 opening-range breakout (08:45..13:14, 75-bar hold), CP3 prior-close location at the 08:30 open, the overnight crush-margin-gap change (ZS traded, ZM and ZL legs), WASDE pre-release drift (ZS) | 11 soy K6 members (in the 471 baseline) | all null (theta_hat negative on every soy member) |
| E.25 | E.22 K6 trip files (2019-05-06..2024-02-29) | derived gross per trade and gross t for the 11 soy K6 members; execution triage | none | descriptive (e.g. K6-cp1-01 ZM +0.37 ticks gross, t 1.14) |
| E.22 Part B | ext2010h, step 2, the two caches | micro trend book design: weekly correlations, returns, costs (MZS, MZL) | E22-F1 (forward, never run on data) | design study |
| E.28 A0 | raw ohlcv-1m chunks to 2023-10 | counts of big-move days per calendar year (for example ZM 2019 0 of 161, 2020 0 of 239) | none | descriptive |
| E.26, E.32 Part 0 | all files | byte-level move with checksums; this seal (no row decoded) | none | n/a |

**What this means, named honestly.** The window is not virgin for the program: several mechanisms close to the
candidate families were already tried on its bar data, all at one-minute bar resolution and all with negative or null
results: momentum into the settlement and the next-day reversal (close to a late-session family), prior-close location
at the 08:30 open (close to an overnight-to-day handoff family), the overnight change in the crush-margin gap traded
in ZS (close to a crush-residual family), WASDE pre-release drift (close to a post-USDA family), and two pooled ML
passes on bar features (the E.12 Gate 0 ridge with its M1 refit, 64 signals; the E.20 search, 36 late-session
features). The exposure was trend, seasonal, calendar-time and settlement-window work on bars; it was
not order-book features, not minutes-scale crush residuals in ZM, and not any E.33 configuration. Two consequences,
carried into the protocol (P1, P2, P9): (1) the window still never selected any configuration E.33 will run, which is
what V43 requires of a test; (2) a family that repeats one of the failed bar-level mechanisms is not a new idea, and
the protocol says for each family how it differs from them. Earlier failures on the window are part of the prior, not
a reason to expect a pass.

**Disclosure from this stage.** While extracting Table B, X1 printed once, in its own context, the pooled daily result
series of the E.17 H1 trial (a recorded trial output over 27 roots, not raw bars). Nothing from it enters the protocol;
X1 did not open the bar-level units file. X1's re-verification read only per-product exclusion and traded-unit counts
from the H1 and H4 result files (no series).

**The discovery dates' own exposure** (E.31, 2020-12..2024-02) is not a window matter; it is stated in P1 of
reports/stage_e32_discovery_protocol.md with X1's Table C (every statistic E.31 computed that could steer a feature
choice).

## Appendix: the 114 sealed files

Paths are repo-relative as the program spells them (symlinks unresolved). The sha256 is of the plaintext; the
manifest also records the sealed blob's sha256.

| # | Kind | Root | Path (repo-relative) | Span | Bytes | sha256 (plaintext) |
|---|---|---|---|---|---|---|
| 1 | cache | ZL | reports/stage_e22_microbook/cache/ZL.parquet | trade dates 2010-07-01..2024-02-29 | 56,920 | 32c5a9f8c50d3bc49d8a2454dc06949130800486cb406cb6aa28e5e38e85a023 |
| 2 | cache | ZS | reports/stage_e22_microbook/cache/ZS.parquet | trade dates 2010-07-01..2024-02-29 | 51,840 | a1ec1648b4b4e19ce1bc884faaa18fd5c9e8071651abb1e7abea18844b7aca1b |
| 3 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2017-04-01_2017-05-01.dbn.zst | 2017-04-01T00:00:00+00:00..2017-05-01T00:00:00+00:00 (UTC) | 177,786 | 9a8232d6d73a7ab05a8292e43bd8cdc133a5be3d1401e5eb79a42c2a665478fe |
| 4 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2017-05-01_2017-06-01.dbn.zst | 2017-05-01T00:00:00+00:00..2017-06-01T00:00:00+00:00 (UTC) | 211,372 | f49768910d672f9b3eb757880375b725f3a7bd9121012bfd213153b480588f59 |
| 5 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2017-06-01_2017-07-01.dbn.zst | 2017-06-01T00:00:00+00:00..2017-07-01T00:00:00+00:00 (UTC) | 182,386 | 7181745e11b2f50c8cf5ea87795356b49fcc3e663a59fab9734c6f4373a13e21 |
| 6 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2017-07-01_2017-08-01.dbn.zst | 2017-07-01T00:00:00+00:00..2017-08-01T00:00:00+00:00 (UTC) | 205,826 | 0ef3403d4d84de38297120c30822ac5182d29ff02cd71aba479cfb05012273ef |
| 7 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2017-08-01_2017-09-01.dbn.zst | 2017-08-01T00:00:00+00:00..2017-09-01T00:00:00+00:00 (UTC) | 228,992 | e879c90cf129e205bd5906df07691e87e4a8b02974569e3474ca3050d48b5773 |
| 8 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2017-09-01_2017-10-01.dbn.zst | 2017-09-01T00:00:00+00:00..2017-10-01T00:00:00+00:00 (UTC) | 197,231 | d4fb7b762eeeda02a8c1ae43ed0169717ad8471e6527746c1d7e0a380d0d22ab |
| 9 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2017-10-01_2017-11-01.dbn.zst | 2017-10-01T00:00:00+00:00..2017-11-01T00:00:00+00:00 (UTC) | 196,042 | ce0174002b6c7f9d086c902b6f80b1e0a95c3cbedeffd23c7314db2f267147c8 |
| 10 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2017-11-01_2017-12-01.dbn.zst | 2017-11-01T00:00:00+00:00..2017-12-01T00:00:00+00:00 (UTC) | 186,488 | a25c80112c3bb88b67e8e13a0c62e2a1fc5abcbd865ce88e0cc82bce82f410d4 |
| 11 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2017-12-01_2018-01-01.dbn.zst | 2017-12-01T00:00:00+00:00..2018-01-01T00:00:00+00:00 (UTC) | 169,438 | b9eeac6d66f561a5af38d4369dd80ae11832e14e1c55a092e4b222fb673a5c3e |
| 12 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2018-01-01_2018-02-01.dbn.zst | 2018-01-01T00:00:00+00:00..2018-02-01T00:00:00+00:00 (UTC) | 187,099 | 0d735b3443d02f8ff736c7ae152abeabdf5df57d2a5cd9f70a165c2b065d62f2 |
| 13 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2018-02-01_2018-03-01.dbn.zst | 2018-02-01T00:00:00+00:00..2018-03-01T00:00:00+00:00 (UTC) | 174,905 | 04d9610ffb43fa526cb85d4afefd4b3b895fab87a1ea6f626ed604b469dae538 |
| 14 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2018-03-01_2018-04-01.dbn.zst | 2018-03-01T00:00:00+00:00..2018-04-01T00:00:00+00:00 (UTC) | 197,170 | 51df09823a41a819138dfdecf5199d298517654ac19b179ba52c7c70b04f0c1c |
| 15 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2018-04-01_2018-05-01.dbn.zst | 2018-04-01T00:00:00+00:00..2018-05-01T00:00:00+00:00 (UTC) | 180,176 | ef05cb6943f70813c35c7bfbd134b1b3ee7d5b12f71af45eeae2f57932b44ba5 |
| 16 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2018-05-01_2018-06-01.dbn.zst | 2018-05-01T00:00:00+00:00..2018-06-01T00:00:00+00:00 (UTC) | 185,728 | c399628e1dd8d1f23c45d37f10671cb9075c0a527edc43d320e3cbaaa641cb48 |
| 17 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2018-06-01_2018-07-01.dbn.zst | 2018-06-01T00:00:00+00:00..2018-07-01T00:00:00+00:00 (UTC) | 173,343 | 92d4758ac14348b3e055ec17abd40adea7879eed35b53b85ef7cca60119cef35 |
| 18 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2018-07-01_2018-08-01.dbn.zst | 2018-07-01T00:00:00+00:00..2018-08-01T00:00:00+00:00 (UTC) | 167,685 | 9f304a1fc4b8ad5ab61003fd264c0df4626ae1cd068b1bcfd31ed4bcfa66d697 |
| 19 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2018-08-01_2018-09-01.dbn.zst | 2018-08-01T00:00:00+00:00..2018-09-01T00:00:00+00:00 (UTC) | 189,766 | c7df99db9a463014a48ffb91660c832642cafdaeb36ac5c98b228478840be3d2 |
| 20 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2018-09-01_2018-10-01.dbn.zst | 2018-09-01T00:00:00+00:00..2018-10-01T00:00:00+00:00 (UTC) | 159,359 | c7d76b194a712aadc1ef9e8613df62521ddcf755538f09265656986cfe075a61 |
| 21 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2018-10-01_2018-11-01.dbn.zst | 2018-10-01T00:00:00+00:00..2018-11-01T00:00:00+00:00 (UTC) | 190,193 | 8ff1c896ce1a152b1ce5e5c9c40f4f833cd01e16d65980834d3ebc307ff0dda2 |
| 22 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2018-11-01_2018-12-01.dbn.zst | 2018-11-01T00:00:00+00:00..2018-12-01T00:00:00+00:00 (UTC) | 156,491 | 9ae9cc5b06fff433176d9975b5149c7f19ea5d0cb42fdb429165ec5a2dd920e9 |
| 23 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2018-12-01_2019-01-01.dbn.zst | 2018-12-01T00:00:00+00:00..2019-01-01T00:00:00+00:00 (UTC) | 148,929 | 85a1334153bd2ccb4301d5390194acb956f93d098eba0ca23798b182723183f0 |
| 24 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2019-01-01_2019-02-01.dbn.zst | 2019-01-01T00:00:00+00:00..2019-02-01T00:00:00+00:00 (UTC) | 158,542 | 7936121f28d782207be27f75ab1de8973a93f4fba0110c638d6d9fd7f6a1ceed |
| 25 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2019-02-01_2019-03-01.dbn.zst | 2019-02-01T00:00:00+00:00..2019-03-01T00:00:00+00:00 (UTC) | 154,116 | 39b793628abeefa8d67ef051b34afa60e3db6520875f6d7367d08ef7f17d9a2f |
| 26 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2019-03-01_2019-04-01.dbn.zst | 2019-03-01T00:00:00+00:00..2019-04-01T00:00:00+00:00 (UTC) | 172,216 | 3122a5b48ac41ca541eebd49c067379c9d99fa1a7004bc5a3291a508e669e84b |
| 27 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2019-04-01_2019-05-01.dbn.zst | 2019-04-01T00:00:00+00:00..2019-05-01T00:00:00+00:00 (UTC) | 157,339 | b430f01834d917d5373995bb0a38f12410b9b50a71cbda394910b3a3135d1f39 |
| 28 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2019-05-01_2019-06-01.dbn.zst | 2019-05-01T00:00:00+00:00..2019-06-01T00:00:00+00:00 (UTC) | 205,638 | 00830b938fda418535a1ce406d4f6941494bbab38fe8eb75ba4d5e92364b01aa |
| 29 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2019-06-01_2019-07-01.dbn.zst | 2019-06-01T00:00:00+00:00..2019-07-01T00:00:00+00:00 (UTC) | 153,035 | dc87c5378251210a0428a31a906bf109f6f67ccc3b7d8c7bd6c0e9858de0376d |
| 30 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2019-07-01_2019-08-01.dbn.zst | 2019-07-01T00:00:00+00:00..2019-08-01T00:00:00+00:00 (UTC) | 181,072 | d367a48504aab6a1cbfebb8db97966d345dbbe3091e9d0baed253489f0d9660b |
| 31 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2019-08-01_2019-09-01.dbn.zst | 2019-08-01T00:00:00+00:00..2019-09-01T00:00:00+00:00 (UTC) | 208,584 | 2cbf7c5d8302de61fb5aed29305ef7e883491906fbdb63032c03a05322d3b582 |
| 32 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2019-09-01_2019-10-01.dbn.zst | 2019-09-01T00:00:00+00:00..2019-10-01T00:00:00+00:00 (UTC) | 185,432 | 342ce1b1efaf1183d14942eb840a939b7e0ce6a1568daf1f04efe9cadd923124 |
| 33 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2019-10-01_2019-11-01.dbn.zst | 2019-10-01T00:00:00+00:00..2019-11-01T00:00:00+00:00 (UTC) | 208,147 | d259f1158fbd096e36f3da1528f5acd0c9228db3cd3eadcedb1eb2aafee8ebad |
| 34 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2019-11-01_2019-12-01.dbn.zst | 2019-11-01T00:00:00+00:00..2019-12-01T00:00:00+00:00 (UTC) | 188,888 | 05dc165d33db0b6eef6719ae5b3de6f80e1aa0185cb1290a3ff71760de3312eb |
| 35 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2019-12-01_2020-01-01.dbn.zst | 2019-12-01T00:00:00+00:00..2020-01-01T00:00:00+00:00 (UTC) | 204,841 | 8c1102b4858761213b2f824e7a929a6fd81a2d1f8ceb607e989844a984188ae8 |
| 36 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2020-01-01_2020-02-01.dbn.zst | 2020-01-01T00:00:00+00:00..2020-02-01T00:00:00+00:00 (UTC) | 232,560 | aa6648c4bb7f4e4990e94eabdd62b2796025bff480f6e5c329f875c6f3452b25 |
| 37 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2020-02-01_2020-03-01.dbn.zst | 2020-02-01T00:00:00+00:00..2020-03-01T00:00:00+00:00 (UTC) | 206,456 | add216b064bdf486f62145bc0068b14558fd85a34041d1ea1cc4fd01a0a72f02 |
| 38 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2020-03-01_2020-04-01.dbn.zst | 2020-03-01T00:00:00+00:00..2020-04-01T00:00:00+00:00 (UTC) | 280,735 | c5f1a6d81fb4b526f5d177cdb4c8d7f0ae69a40411c843b030a8d95bb2079510 |
| 39 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2020-04-01_2020-05-01.dbn.zst | 2020-04-01T00:00:00+00:00..2020-05-01T00:00:00+00:00 (UTC) | 230,410 | aafd0b6c754f68783a0d02e39606662770b2bd046b5b3897c06f8abee911fc0c |
| 40 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2020-05-01_2020-06-01.dbn.zst | 2020-05-01T00:00:00+00:00..2020-06-01T00:00:00+00:00 (UTC) | 218,219 | cfc5924321c16a726a0cf192514a5c337d73cd8bef068f7e98ba8d0773648049 |
| 41 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2020-06-01_2020-07-01.dbn.zst | 2020-06-01T00:00:00+00:00..2020-07-01T00:00:00+00:00 (UTC) | 204,116 | 86203bc0d5df7c5f6a2ccd8fff53282c24cd8f8190aad61dcdbb8714262650cc |
| 42 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2020-07-01_2020-08-01.dbn.zst | 2020-07-01T00:00:00+00:00..2020-08-01T00:00:00+00:00 (UTC) | 237,315 | 781708b71c86ba717de477ddb46d03a5c9ca0a451043397f4b9817ceaef8373b |
| 43 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2020-08-01_2020-09-01.dbn.zst | 2020-08-01T00:00:00+00:00..2020-09-01T00:00:00+00:00 (UTC) | 237,822 | c5673c9caaec026616869dfc98a0657a55833c8b9a7bfb43257240a48d329f8a |
| 44 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2020-09-01_2020-10-01.dbn.zst | 2020-09-01T00:00:00+00:00..2020-10-01T00:00:00+00:00 (UTC) | 258,771 | 9c0cfc37de987434bded3a92612d0b226966a9267e7e6dd62a35dab31abe97c8 |
| 45 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2020-10-01_2020-11-01.dbn.zst | 2020-10-01T00:00:00+00:00..2020-11-01T00:00:00+00:00 (UTC) | 274,120 | b95ca40eaec8d3cd55d5d9e79d2180e3c04f0c6b0bb10a2853bbcdf20c667c39 |
| 46 | raw ohlcv-1m | ZL | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2020-11-01_2020-12-01.dbn.zst | 2020-11-01T00:00:00+00:00..2020-12-01T00:00:00+00:00 (UTC) | 242,058 | e4db5a31e7baa6024c2b3ef47cc1c04bd44ef47bafb16a2cd7da6ffa365d14a3 |
| 47 | raw ohlcv-1m | ZM | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0/range=2019-05-01_2019-06-01.dbn.zst | 2019-05-01T00:00:00+00:00..2019-06-01T00:00:00+00:00 (UTC) | 206,829 | 514878c83ae7bba343a1f23adb5ef9aa509c0071f4e726b65a6d20cdf17de8fd |
| 48 | raw ohlcv-1m | ZM | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0/range=2019-06-01_2019-07-01.dbn.zst | 2019-06-01T00:00:00+00:00..2019-07-01T00:00:00+00:00 (UTC) | 164,006 | 974561bd126479a78de05e11b523484246a632ae05f01b05e18fa22ed51c6c53 |
| 49 | raw ohlcv-1m | ZM | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0/range=2019-07-01_2019-08-01.dbn.zst | 2019-07-01T00:00:00+00:00..2019-08-01T00:00:00+00:00 (UTC) | 168,360 | 80993923f31bec51ad4ef3b48b4ddc107b5d7a76c88d8c522be04b740dee5cea |
| 50 | raw ohlcv-1m | ZM | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0/range=2019-08-01_2019-09-01.dbn.zst | 2019-08-01T00:00:00+00:00..2019-09-01T00:00:00+00:00 (UTC) | 180,372 | 61d567e39c74a376762aa46d0362c800cab80fad0c3982e6c98ff73e4afc7d50 |
| 51 | raw ohlcv-1m | ZM | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0/range=2019-09-01_2019-10-01.dbn.zst | 2019-09-01T00:00:00+00:00..2019-10-01T00:00:00+00:00 (UTC) | 157,250 | f5d17346d7c4569d1d1857026b6aa2b3068ec31ca25f34f8d4e1037528a849b8 |
| 52 | raw ohlcv-1m | ZM | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0/range=2019-10-01_2019-11-01.dbn.zst | 2019-10-01T00:00:00+00:00..2019-11-01T00:00:00+00:00 (UTC) | 183,418 | 7befa359ac65a07d957b31c0370f63edefb8b4cd56ab32bc1aea584db2c76b1a |
| 53 | raw ohlcv-1m | ZM | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0/range=2019-11-01_2019-12-01.dbn.zst | 2019-11-01T00:00:00+00:00..2019-12-01T00:00:00+00:00 (UTC) | 141,609 | d167a52de8524063474185b505b6a12cd991a35173ee0c7027e085ecd690b4e0 |
| 54 | raw ohlcv-1m | ZM | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0/range=2019-12-01_2020-01-01.dbn.zst | 2019-12-01T00:00:00+00:00..2020-01-01T00:00:00+00:00 (UTC) | 162,924 | 03a8997e6452ffa13a290cdf6528ecded8b4a1f85d4644474fd576f9a90857a0 |
| 55 | raw ohlcv-1m | ZM | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0/range=2020-01-01_2020-02-01.dbn.zst | 2020-01-01T00:00:00+00:00..2020-02-01T00:00:00+00:00 (UTC) | 168,675 | d00f9afca2515e14a19f47624c63d165f3442cf9080b5e8853572af6b3bb4042 |
| 56 | raw ohlcv-1m | ZM | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0/range=2020-02-01_2020-03-01.dbn.zst | 2020-02-01T00:00:00+00:00..2020-03-01T00:00:00+00:00 (UTC) | 145,113 | d15e871cdf4f7a9713f66566991d529e1e5f325e8d7111ee4be4f07b320fbce6 |
| 57 | raw ohlcv-1m | ZM | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0/range=2020-03-01_2020-04-01.dbn.zst | 2020-03-01T00:00:00+00:00..2020-04-01T00:00:00+00:00 (UTC) | 227,141 | 4abf5d75bcf794840691d1505aa0449276e9e46831e6044befb4953bf4763815 |
| 58 | raw ohlcv-1m | ZM | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0/range=2020-04-01_2020-05-01.dbn.zst | 2020-04-01T00:00:00+00:00..2020-05-01T00:00:00+00:00 (UTC) | 177,856 | 6fb1521058450b1c772eb29db789be9c6f770f86d9cbeac9356dd5924cd5c36d |
| 59 | raw ohlcv-1m | ZM | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0/range=2020-05-01_2020-06-01.dbn.zst | 2020-05-01T00:00:00+00:00..2020-06-01T00:00:00+00:00 (UTC) | 164,823 | d7aad0408a846b1cf3432f9c2eb8fca67b2a0213c1ca6023f91b0cb8b5ff8e90 |
| 60 | raw ohlcv-1m | ZM | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0/range=2020-06-01_2020-07-01.dbn.zst | 2020-06-01T00:00:00+00:00..2020-07-01T00:00:00+00:00 (UTC) | 159,118 | 4ffb509f3157247344a77f8f676ce120e09e0470bd6788f8304f57af238a63d8 |
| 61 | raw ohlcv-1m | ZM | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0/range=2020-07-01_2020-08-01.dbn.zst | 2020-07-01T00:00:00+00:00..2020-08-01T00:00:00+00:00 (UTC) | 182,185 | 725ce1c1e100919bdc480216422bc140cb54440060038306ad145bf3f28c5fe9 |
| 62 | raw ohlcv-1m | ZM | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0/range=2020-08-01_2020-09-01.dbn.zst | 2020-08-01T00:00:00+00:00..2020-09-01T00:00:00+00:00 (UTC) | 178,563 | 14fc8582b071120baf91d27da60dab024f21acb8ccbaaf656ca326e18efddf44 |
| 63 | raw ohlcv-1m | ZM | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0/range=2020-09-01_2020-10-01.dbn.zst | 2020-09-01T00:00:00+00:00..2020-10-01T00:00:00+00:00 (UTC) | 209,357 | a091ad55270f102e700c6222ab4dcc707b427a488f4c9690e19de351e164035c |
| 64 | raw ohlcv-1m | ZM | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0/range=2020-10-01_2020-11-01.dbn.zst | 2020-10-01T00:00:00+00:00..2020-11-01T00:00:00+00:00 (UTC) | 247,695 | a1e466b47e30dca053bc7d3fea7978a21343711649cb1b41556e8b6040e218ef |
| 65 | raw ohlcv-1m | ZM | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0/range=2020-11-01_2020-12-01.dbn.zst | 2020-11-01T00:00:00+00:00..2020-12-01T00:00:00+00:00 (UTC) | 198,224 | 3ceef124e06011529b916e6f6fced2f11fcf2889840e30365a47f56f7ba52755 |
| 66 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2017-04-01_2017-05-01.dbn.zst | 2017-04-01T00:00:00+00:00..2017-05-01T00:00:00+00:00 (UTC) | 178,503 | 026f9c460136eed4fc92713d3a92bdfb09ccd16ec228cac513b9bea8a632f05c |
| 67 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2017-05-01_2017-06-01.dbn.zst | 2017-05-01T00:00:00+00:00..2017-06-01T00:00:00+00:00 (UTC) | 217,633 | 74b0d8f0b3f6c758d10907d08007ee24440097028b5bca027bf9ce68ec59da85 |
| 68 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2017-06-01_2017-07-01.dbn.zst | 2017-06-01T00:00:00+00:00..2017-07-01T00:00:00+00:00 (UTC) | 201,306 | 9e16ecf393bdae48f0af5aaa1b2de52b8c326032ad3c43de7d6bfe974ce4fecd |
| 69 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2017-07-01_2017-08-01.dbn.zst | 2017-07-01T00:00:00+00:00..2017-08-01T00:00:00+00:00 (UTC) | 237,737 | 802f879deb4b7d7721bf1b90a8085eb04839cc7546403fb24127de16a65ae0b3 |
| 70 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2017-08-01_2017-09-01.dbn.zst | 2017-08-01T00:00:00+00:00..2017-09-01T00:00:00+00:00 (UTC) | 241,774 | 7e8e3f922582b2eb9b8e8b22de0a9b802b44f223dc6a1508c493107250d34498 |
| 71 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2017-09-01_2017-10-01.dbn.zst | 2017-09-01T00:00:00+00:00..2017-10-01T00:00:00+00:00 (UTC) | 205,601 | e01638022a7e3503ecaf8148c79f10da02078dde9100c461e97c92d6532df15d |
| 72 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2017-10-01_2017-11-01.dbn.zst | 2017-10-01T00:00:00+00:00..2017-11-01T00:00:00+00:00 (UTC) | 195,256 | d37819652b5c062e65a3236d4a19cea837a9733c8cf199f6df24f698e676b780 |
| 73 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2017-11-01_2017-12-01.dbn.zst | 2017-11-01T00:00:00+00:00..2017-12-01T00:00:00+00:00 (UTC) | 194,920 | 67f81d152f7dfdf3a62d09cb5b3b7706718368b74622842ad259df643e29474c |
| 74 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2017-12-01_2018-01-01.dbn.zst | 2017-12-01T00:00:00+00:00..2018-01-01T00:00:00+00:00 (UTC) | 177,337 | 1b6396f54b0f8ac32efe096c473f3f7ef9bedbe57add11253bbb5b209a5e5335 |
| 75 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2018-01-01_2018-02-01.dbn.zst | 2018-01-01T00:00:00+00:00..2018-02-01T00:00:00+00:00 (UTC) | 195,210 | 85473ab60201d2cb3bec1b12a233813d57e0986f2004cbf8ca8263057261d51d |
| 76 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2018-02-01_2018-03-01.dbn.zst | 2018-02-01T00:00:00+00:00..2018-03-01T00:00:00+00:00 (UTC) | 191,916 | b334385f5efa797586a365466c3e92da99b3b5d097494f6cf932e6bf250d1ebf |
| 77 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2018-03-01_2018-04-01.dbn.zst | 2018-03-01T00:00:00+00:00..2018-04-01T00:00:00+00:00 (UTC) | 236,227 | d78a1bb1e30684b5fe54141b3bb214dc7518a86b8172ba07ef0b5d3665e8e0e9 |
| 78 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2018-04-01_2018-05-01.dbn.zst | 2018-04-01T00:00:00+00:00..2018-05-01T00:00:00+00:00 (UTC) | 223,278 | f5f58a3b524ce3b8e2e59dde257cb99bf222d39ce8906535b6092306fbb51a43 |
| 79 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2018-05-01_2018-06-01.dbn.zst | 2018-05-01T00:00:00+00:00..2018-06-01T00:00:00+00:00 (UTC) | 239,407 | 4c603646e7d4823575a7b68dd55c6bacde2858e4fcae88c6e2fa681684be73b1 |
| 80 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2018-06-01_2018-07-01.dbn.zst | 2018-06-01T00:00:00+00:00..2018-07-01T00:00:00+00:00 (UTC) | 226,127 | a1b7832c76bb86fca34a5c55851fc44280bf3dcad5bade77b88b705c37868a6a |
| 81 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2018-07-01_2018-08-01.dbn.zst | 2018-07-01T00:00:00+00:00..2018-08-01T00:00:00+00:00 (UTC) | 226,945 | b289fde8dc60a6e5783dee1f4a4eb369c562305d6b2274c8135fab66b887febc |
| 82 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2018-08-01_2018-09-01.dbn.zst | 2018-08-01T00:00:00+00:00..2018-09-01T00:00:00+00:00 (UTC) | 259,275 | 1c49c9da3fd3ccfc7ad49c69e6ede2791b6a568ffb917df0b3c2f9e8e893ff82 |
| 83 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2018-09-01_2018-10-01.dbn.zst | 2018-09-01T00:00:00+00:00..2018-10-01T00:00:00+00:00 (UTC) | 197,834 | dc2e09a6f67b95650fa2bb45d80a6ab08c9d4fe8f30cdce09248cd90c1f5d81c |
| 84 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2018-10-01_2018-11-01.dbn.zst | 2018-10-01T00:00:00+00:00..2018-11-01T00:00:00+00:00 (UTC) | 213,421 | 67aaa3ebd6d6618f429b33175b28ee7853f5ea2969ef175046fe0e2c93def7b4 |
| 85 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2018-11-01_2018-12-01.dbn.zst | 2018-11-01T00:00:00+00:00..2018-12-01T00:00:00+00:00 (UTC) | 200,246 | 4ecd1651955523f28d23f52fc51f16902b4a7539b932e5d7d3abd88a259d68ac |
| 86 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2018-12-01_2019-01-01.dbn.zst | 2018-12-01T00:00:00+00:00..2019-01-01T00:00:00+00:00 (UTC) | 179,040 | b08b3f070c0a592aef26d848c251b38d9899a97c1caa88ecbc5d05ba82d97266 |
| 87 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2019-01-01_2019-02-01.dbn.zst | 2019-01-01T00:00:00+00:00..2019-02-01T00:00:00+00:00 (UTC) | 177,292 | dc9052a4c53f6ed54e7b577db0bea828112eaf65b41bbbd857a3cf79c4a54d19 |
| 88 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2019-02-01_2019-03-01.dbn.zst | 2019-02-01T00:00:00+00:00..2019-03-01T00:00:00+00:00 (UTC) | 160,332 | d5bbe24e5d2682a94eb457130437cf21629b033108c36409df479fd6dce2387d |
| 89 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2019-03-01_2019-04-01.dbn.zst | 2019-03-01T00:00:00+00:00..2019-04-01T00:00:00+00:00 (UTC) | 190,368 | f0c3e3457693f43f83f6af133e16d8cbda98ee2b0488c522fcb903ad18fe1714 |
| 90 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2019-04-01_2019-05-01.dbn.zst | 2019-04-01T00:00:00+00:00..2019-05-01T00:00:00+00:00 (UTC) | 170,101 | da19f6d64c4367edf8c8516d0b7022ba2dba96e3420802d1bef5d3f18be1d077 |
| 91 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2019-05-01_2019-06-01.dbn.zst | 2019-05-01T00:00:00+00:00..2019-06-01T00:00:00+00:00 (UTC) | 241,716 | 217496d0d84fd2544c72eab3a87aca42cf54b5b75d31dd5d2673e74204b0dd6c |
| 92 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2019-06-01_2019-07-01.dbn.zst | 2019-06-01T00:00:00+00:00..2019-07-01T00:00:00+00:00 (UTC) | 196,063 | 6de29dbe5ed2e5bcf20d2ffaffe82b65dbb6b43e390f8aee13dd1a90f5ed735c |
| 93 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2019-07-01_2019-08-01.dbn.zst | 2019-07-01T00:00:00+00:00..2019-08-01T00:00:00+00:00 (UTC) | 214,946 | f56b01862a5e24196982844d2c1c89214eb5c91211c4b902298476f374fc6cc6 |
| 94 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2019-08-01_2019-09-01.dbn.zst | 2019-08-01T00:00:00+00:00..2019-09-01T00:00:00+00:00 (UTC) | 221,915 | fd2485ee4090f3a0bbf148a3e8c4a7df06c601ee1f0a5c2e043dc1f6f2b4bc49 |
| 95 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2019-09-01_2019-10-01.dbn.zst | 2019-09-01T00:00:00+00:00..2019-10-01T00:00:00+00:00 (UTC) | 195,152 | a77bd7864f16489b3311d3f123d442affb44265ae3993c1cecca0a808c899e31 |
| 96 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2019-10-01_2019-11-01.dbn.zst | 2019-10-01T00:00:00+00:00..2019-11-01T00:00:00+00:00 (UTC) | 216,792 | 9d69818a99117fb380917d494543154886de595c6c803c114b6ba84298f5272a |
| 97 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2019-11-01_2019-12-01.dbn.zst | 2019-11-01T00:00:00+00:00..2019-12-01T00:00:00+00:00 (UTC) | 185,150 | a03495aee3a66865e0c25458b577b5fd8c6624758cdfec2af3f58c1f97a80fc7 |
| 98 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2019-12-01_2020-01-01.dbn.zst | 2019-12-01T00:00:00+00:00..2020-01-01T00:00:00+00:00 (UTC) | 186,524 | 4410311806c77808264eed1f1dfe1649a846a34fe81a834efbb38a22db6cf659 |
| 99 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2020-01-01_2020-02-01.dbn.zst | 2020-01-01T00:00:00+00:00..2020-02-01T00:00:00+00:00 (UTC) | 202,219 | db47c95502972662df4d1d32f58fd08a981b6f42085cedcbda853eb98bf05d55 |
| 100 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2020-02-01_2020-03-01.dbn.zst | 2020-02-01T00:00:00+00:00..2020-03-01T00:00:00+00:00 (UTC) | 173,879 | 393d937570ff9b758758ca55a8e31f35f4683972d15c9b021c1c9116e64a3d83 |
| 101 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2020-03-01_2020-04-01.dbn.zst | 2020-03-01T00:00:00+00:00..2020-04-01T00:00:00+00:00 (UTC) | 260,060 | a389b837b4b830a540b5afa406a1559d479c27c7eb7b60db9b279b618821622a |
| 102 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2020-04-01_2020-05-01.dbn.zst | 2020-04-01T00:00:00+00:00..2020-05-01T00:00:00+00:00 (UTC) | 217,850 | 98dd72569cd76ef9d7a5b148618ceb0562d7939b961c96c1e31ab8f0d760ab5c |
| 103 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2020-05-01_2020-06-01.dbn.zst | 2020-05-01T00:00:00+00:00..2020-06-01T00:00:00+00:00 (UTC) | 203,967 | f5ae12cf38fefa1e54c659a1f02b608762a3f278160ac4222e936ca2d8bcb689 |
| 104 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2020-06-01_2020-07-01.dbn.zst | 2020-06-01T00:00:00+00:00..2020-07-01T00:00:00+00:00 (UTC) | 195,175 | 5c9ed890982a9189f407196fa9dfc13635b3c5aa0373fce870e6c60c40480d22 |
| 105 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2020-07-01_2020-08-01.dbn.zst | 2020-07-01T00:00:00+00:00..2020-08-01T00:00:00+00:00 (UTC) | 225,358 | 1cfcda51b93963630ca23351487fb85902c00dd185cc553b62a188d35c8e96ac |
| 106 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2020-08-01_2020-09-01.dbn.zst | 2020-08-01T00:00:00+00:00..2020-09-01T00:00:00+00:00 (UTC) | 216,496 | 4c620b558a542600f26626ec54accda992b807afded9e7194d7d567c29a7b528 |
| 107 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2020-09-01_2020-10-01.dbn.zst | 2020-09-01T00:00:00+00:00..2020-10-01T00:00:00+00:00 (UTC) | 247,883 | 5c9d085fdc806fdc6669c575fdb47c31f6dd4b8e22d3f22b9dde6200d744818a |
| 108 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2020-10-01_2020-11-01.dbn.zst | 2020-10-01T00:00:00+00:00..2020-11-01T00:00:00+00:00 (UTC) | 264,071 | 37227d7dde840d6c0abd3b57e4b95bdfec97fcd98530712547bca1b8a7407e87 |
| 109 | raw ohlcv-1m | ZS | data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2020-11-01_2020-12-01.dbn.zst | 2020-11-01T00:00:00+00:00..2020-12-01T00:00:00+00:00 (UTC) | 245,308 | f563c5a657f40392c4b382b2de16e3fbfa943c35f4c106c23daaf63efec16bd4 |
| 110 | store | ZL | data/processed_hist/ext2010h/ZL/ohlcv-1m_ZL_v_0_2010-07-01_2019-04-30_ext2010h.parquet | trade dates 2010-07-01..2019-04-30 | 23,609,808 | 58bab10295af02267c1226770217053423651e8cb143593b8589bfcaca020812 |
| 111 | store | ZL | data/processed_step2/ZL/ohlcv-1m_ZL_v_0_2019-05-06_2024-02-29_step2.parquet | trade dates 2019-05-06..2024-02-29 | 16,163,190 | d863413e75c01c59ea802a9225bc39b7439e3bca5e57841ead9aeb4602000bb0 |
| 112 | store | ZM | data/processed_step2/ZM/ohlcv-1m_ZM_v_0_2019-05-06_2024-02-29_step2.parquet | trade dates 2019-05-06..2024-02-29 | 13,669,823 | 422d70575c74acf9825908f3b38384457595a382ef3cbbdcda4e36ffcbf0aac0 |
| 113 | store | ZS | data/processed_hist/ext2010h/ZS/ohlcv-1m_ZS_v_0_2010-07-01_2019-04-30_ext2010h.parquet | trade dates 2010-07-01..2019-04-30 | 26,560,627 | ac1fb0bafe34fdcba89a64709a38069d5dcdd103951dd4e3ac1ca8cd00176f74 |
| 114 | store | ZS | data/processed_step2/ZS/ohlcv-1m_ZS_v_0_2019-05-06_2024-02-29_step2.parquet | trade dates 2019-05-06..2024-02-29 | 16,157,737 | bc46610d4b99ae4bf6808d12ba05cd4193f4c1e3423c84f58c29549f7a3d30ef |
