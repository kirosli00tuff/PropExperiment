# Brief: StatsCoder-OpusXHigh (Stage E.33b, Part D1-D3)

Objective: turn the finished E.33 search on real discovery data into the Part D statistics. The lead names the
branch at spawn:
- Branch N (Tier A empty): P10's null report items (i)-(vi) plus D1 and D3.
- Branch T (Tier A not empty): D1 and D3 first; then, only after the lead has written and hashed
  reports/stage_e33_finalists.md (P8, last bullet), D2 = the P6.4 execution variants and P6.5 diagnostics for Tier A
  and Tier B, in P10's cut order (first cut first: VECM, SFI, clustered MDA, P6.4 (iii) queue variants, prop
  simulator, Tier B's variants, the rest of P6.5). An item not ready is reported as not done (P10), never rushed.

Read first (by section, not whole):
- reports/stage_e32_discovery_protocol.md (sha256 c4ffb9d7...; refuse if it differs): P3.5, P3.8, P6.2, P6.4,
  P6.5, P7.2, P8, P10.
- docs/prompts/STAGE_E.33.md, Part D (lines 167-193) and Part E (196-222).
- reports/stage_e33_protocol_readings.md: the rulings govern; the Appendix entries S07, S08, P01-P14 and K01-K14
  cover the reported-only statistics.
- docs/NULL_CRITERIA_E.md (branch N item vi).

Inputs (read only):
- Search root /mnt/large-storage/market_data/PropExperiment/derived/e33/search/<cid>/ for the 300 E33 IDs:
  stats.json, daily.parquet (date, X_D, n_trades), trades.parquet, not_made.parquet, fold<k>.npz,
  fold<k>.model.json, DONE.
- The selection output from select33.py, run by the lead (path given at spawn). It is the selection. You report it;
  you do not re-select.
- The null distribution: the null proof seeds 1-20 under derived/e33/proofs/seed<s>/ and
  reports/stage_e33_briefs/work/B5_proofs.md.
- The feature store features/<feat_sha>/ (sigma_ZM(D) in _day/) and label store labels/<label_sha>/ (paths and shas
  given at spawn); the calendar module pipeline/cal33.py (releases, days to expiry).

D1 (reports, never gates; P8 first paragraph):
- For all 300: the G1-G5 values and pass flags as select33 wrote them; the funnel alone and in order G1..G5.
- Per-firm mean net per trade at market, L = 1 s (Topstep 0.528, Lucid 0.560 and 0.920, Bulenox 0.572, MFFU 0.612,
  Tradeify 0.920 ticks per round trip).
- Trade counts and trades per date.
- The DSR at the registered N, with BH and Holm for reference (one-sided p from the daily t; reading P07).
- The discovery PBO via CSCV (reading P08's set).
- The G5 parts, and the largest month's share of the total net.
- If any number you compute disagrees with select33's output, report both values and where they differ. Do not edit
  select33 or any frozen pipeline file.

D3: a histogram of the 300 OOF daily Sharpes beside the null distribution: all 300 x 20 null-seed Sharpes, and
separately the 20 per-seed maxima. Draw lines at SR0 = E[max SR] at N (0.1137 at N 838), G3 0.1724 and the binding
0.2007. Recompute the lines at the registered N with p7_final.py if N is not 838.

Branch N, P10 items:
- (i) the funnel;
- (ii) the 10 best configurations by SR_d with every P6.2 statistic;
- (iii) = D3;
- (iv) the discovery PBO;
- (v) the minimum detectable net edge per trade at 80% power on the OOF dates, per horizon. State the formula and its
  source line in P7.2;
- (vi) per family, whether a null statement in the sense of docs/NULL_CRITERIA_E.md is supportable, or
  "no statement", with the criterion quoted.
- Do not write item (vii); the lead writes it.

Outputs:
- reports/stage_e33_briefs/work/D_stats.md: the tables, each number with its source file.
- reports/stage_e33_briefs/work/D_stats.json: every number, machine-readable.
- Code with tests under reports/stage_e33_briefs/work/stats/.
- Figures as PNG under reports/stage_e33_briefs/work/stats/fig/.

Rules:
- Real outcomes may be read; the C1 registration is on file.
- Never add, drop, re-run or re-select a configuration.
- No test-window data (2017-05-01 to 2020-11-30) and nothing dated 2024-03-01 or later.
- No Databento call; no live/, ops/, TopstepX or ProjectX.
- Run at nice 10, at most 4 processes. Check `free -m` before any job longer than a few minutes, and stop a job if
  free memory falls below 2 GB.
- Large outputs go under derived/e33/stats/, never into git.
- Read files by section; scripts print counts and summaries, not rows.
- Every time from `date`, in PDT.
- Do not end your turn while a job of your own is running. Poll its log with short checks until it finishes.

Not yours: the selection decision, the finalists file, the E.34 draft, the return. Those are the lead's.

Return: the paths; a summary of at most 200 words; failures and non-survivors as well as any passing configuration;
anything not finished.
