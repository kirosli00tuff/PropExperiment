# Stage E.33 shared interface (lead, 2026-10-27 14:45 PDT)

Every E.33 coder works from this file plus the frozen protocol
reports/stage_e32_discovery_protocol.md (sha256 c4ffb9d79af4bbbf10574ac138668aa49a80b22a8f5fba5879184d357d2c7e05;
cited "P<n>"). The protocol governs; where this file and the protocol differ, the protocol wins and you report the
difference. This file fixes only what the protocol leaves to E.33 (file layout, names, module split).

## 1. Paths

- REPO = /home/kiros-li/Documents/GitHub/PropExperiment
- Pipeline A (the production pipeline): REPO/reports/stage_e33_briefs/work/pipeline/ (flat modules; tests in
  pipeline/tests/). Owners: guard33.py, data33.py, cal33.py (DataCoder); feat33.py, build_features33.py
  (FeatureCoder = Coder-A features); lab33.py, build_labels33.py (LabelCoder = Coder-A labels); search33.py,
  run_search33.py (SearchCoder); select33.py, synth33.py, run_proofs33.py (later workers); cost33.py (later).
- Implementation B (the independent second implementation, B2): REPO/reports/stage_e33_briefs/work/implB/.
  Owners: FeatureCoder2, LabelCoder2. B may import from pipeline/ ONLY guard33.py and data33.py (the raw-record
  loader and the guard), never read any other file under pipeline/. A never reads implB/.
- Large outputs: DERIVED = /mnt/large-storage/market_data/PropExperiment/derived/e33/ with subfolders split/,
  features/, labels/, implB/, proofs/, search/, probes/. Nothing large goes into git.
- E.31 library (allowed by P1.2 (d)): REPO/reports/stage_e31_briefs/work/pilot/ modules mbo_book31, measure31,
  measure31_core, canary_check31, stats31_core, kalgo31. Import them; do not copy-edit them. Never open
  pilot/runs/ (refused, P1.2).

## 2. Rules for every worker

1. No outcomes before registration. On real data (2020-12..2024-02) nobody computes, prints or saves a statistic of
   labels, forward returns, net P&L, markouts or class shares. Allowed on real data: features, book states, counts
   of rows and exclusions, timings, and label VALUES only inside an equality comparison (B3) or a hand check,
   printing only agreement counts and the locations of mismatches. Synthetic data: anything.
2. Every real-data read goes through guard33 (P1.2). No Databento API call, ever. No other root's market data.
3. Never edit anything under data/, screening/, sim/, rules/, funnel/, live/, ops/, ledger/ (harness v14 pins them)
   or the protocol. Never run `uv add` or install a package. Never run git commands that change state.
4. Compute: real-data runs at `nice -n 10`, at most 4 processes, at most 10 minutes per run while coding; the full
   builds and proof runs are launched by the lead. Check `free -m` before a run; stop if available memory < 2 GB.
   For any fit: OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1 unless the protocol says otherwise. No heavy
   run 15:30-16:00 PDT (another service).
5. Context hygiene: read files by section (grep, line ranges); scripts print summaries; logs to files, read tails.
6. Ambiguity: when the protocol leaves open a detail that can change an outcome, implement the most conservative
   reading, mark it in code with `# READING <id>`, and log it in your `<Role>_readings.md` (protocol line quoted,
   readings considered, choice, why conservative). The lead decides each before the freeze. Never change a
   declared choice.
7. Return: the paths you wrote, a summary of at most 200 words, what is unfinished, and your readings file.

## 3. Conventions

- Clock: every record's time is ts_recv (int64 ns UTC). Ordering, look-backs and as-of lookups use ts_recv only
  (P0.3, LT4). A record is known at u iff ts_recv <= u. Records with ts_recv < ts_event stay in ts_recv order.
- CT = America/Chicago (zoneinfo, DST-aware). Trade date D = ts_recv in [D-1 16:00 CT, D 16:00 CT)
  (measure31.day_bounds).
- Decision minutes: minute index i = 0..272 for t = 08:35:00 CT + i minutes on D. G_h(D) = {i : 0 <= i <= 277 - h}
  (13:12 - h; 273, 263, 248, 218 minutes for h = 5, 15, 30, 60).
- Labels: F05, F15, F30, F60 (fixed horizon h = 5, 15, 30, 60), T15, T30 (triple barrier, vertical h = 15, 30).
- L = 1.000 s, f = 0.528 ticks (selection variant). ZM tick = 0.10 USD/short ton.
- Feature column names: the protocol IDs with "." replaced by "_": C_1..C_15, F1_1..F1_8, F2_1..F2_11,
  F3_1..F3_12, F4_1..F4_13 (59 columns), float64, in that order. Sets: S1 = C+F1, S2 = C+F2, S3 = C+F3, S4 = C+F4,
  S5 = all 59.
- Trade-date lists: the 816 dates, the first 20 burn-in, 796 OOF (P1.4).

## 4. Files

### 4.1 Feature table (FeatureCoder; FeatureCoder2 writes the same schema under DERIVED/implB/features/)
DERIVED/features/<code_sha12>/<YYYY-MM-DD>.parquet, one file per OOF date (all 796, excluded dates included;
features are computed on every date). Columns: `date` (str), `i` (int16, 0..272), `t_ns` (int64, UTC ns of the
decision time), then the 59 feature columns. <code_sha12> = first 12 hex of the sha256 of the concatenated feature
code files (listed in the folder's manifest.json with each file's sha256).
Day statistics: DERIVED/features/<code_sha12>/_day/<YYYY-MM-DD>.json for all 816 dates with at least
`sigma_zm`, `sigma_zs`, `sigma_zl` (ticks of each, P0.3; null when undefined) and the front instrument ids.
The label builder and the selection code read sigma_ZM(D) from here (TB barrier width P3.4; G5 (d) terciles).
The builder must accept a cutoff `cutoff_ns` that truncates ALL input streams (ZM MBO, ZS and ZL MBP-1,
definitions) at ts_recv <= cutoff_ns, for LT1 (P4.1).

### 4.2 Label and outcome table (LabelCoder; LabelCoder2 writes the same schema under DERIVED/implB/labels/)
DERIVED/labels/<code_sha12>/<LABEL>/<YYYY-MM-DD>.parquet, one file per (label, OOF date), one row per i in G_h(D)
(every grid minute; on a date excluded by P1.4 every flag is false). Columns:
- `i` (int16), `t_ns` (int64)
- `entry_ok` (bool): the entry rules hold at t (P3.6 first paragraph: rules 1-4, 6, the limit-proximity part of
  rule 5, the ZM book at t has both sides and is not marked bad, D not excluded)
- `row_ok` (bool): the row is kept (P3.6 all rules incl. the locked-book row rule; P3.7 valid M_ZM(t))
- `y` (int8; 0 when not row_ok), `n_long`, `n_short` (float64 ticks net of f; NaN when not row_ok)
- `w` (float64 P3.7 uniqueness weight; NaN when not row_ok), `span_end_ns` (int64; -1 when not row_ok)
- for side s in (long, short): `s_made` (bool), `s_net` (float64 ticks net of f; NaN if not made),
  `s_entry_ns`, `s_exit_ns` (int64 fill times; -1 if not made), `s_flags` (int16 bitmask: 1 entry fallback fired,
  2 exit fallback fired, 4 exit marked at the limit price, 8 exit marked at the last valid touch, 16 entry not made
  (no valid update before the planned exit), 32 TB entry not made (M_ZM undefined at the entry fill update)).
  Filled for every i with entry_ok (the simulation may enter at an entry_ok minute that is not a row).
  Invariant: where row_ok and no fallback fired, s_net equals n_s exactly.
- `mid_move` (float64 ZM ticks; added 15:20 by the lead for P6.2's reported-only mid-sign hit rate) =
  M_ZM(t + L + h) - M_ZM(t + L), mids as of the last book update with ts_recv <= each instant; TB uses the vertical
  h; NaN when either mid is undefined. Never used by P8.
Per-date exclusion counts: DERIVED/labels/<code_sha12>/<LABEL>/_excl/<YYYY-MM-DD>.json (rows and minutes removed
per rule, P3.6 last line).

### 4.3 Search outputs (SearchCoder)
DERIVED/search/<config_id>/fold<k>.npz (k = 1..6): for every grid minute of every evaluation date the class
probabilities (p_-1, p_0, p_+1), the fold's mu_long_k and mu_short_k, fit metadata (seconds, iterations,
convergence, best iteration, seed); then `daily.parquet` (date, X_D, n_trades), `trades.parquet` (date, i, side,
net, entry_ns, exit_ns, flags, ev_long, ev_short), `stats.json` (P6.2) and DONE markers per fold and per config.
The engine reads features and labels only through the schemas above, so the synthetic proofs (P4.2) can feed it
tables written in the same schemas under DERIVED/proofs/seed<s>/.

### 4.4 Registry IDs (P7.1)
E33-<set><label><grid>, set S1..S5, label F05 F15 F30 F60 T15 T30, grid in P7.1 order L001A L001E L010A L010E L100A
L100E G2050 G2200 G3050 G3200. Run order P5 (S5, S1, S3, S2, S4; FH15, FH30, FH05, FH60, TB15, TB30; grid order).
