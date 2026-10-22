# E.29 BasketCoder-OpusXHigh work log (times PDT from `date`)

## Session 1 (cut by the usage limit)
- 19:25 start (`date` read 19:25:53; the declaration header says "about 19:40 PDT", the lead's estimate). Read the
  brief and reports/stage_e29_model.md in full; sha256 f393759f4af712a889646a7a4cdb2c45f2f3b8496a6403be56467de7eb0d8164
  = the declared hash. Read E.28's A3_run.py, A3_funnel.py, A3_gridcheck.py, A3_models.py (firm_models), A3_econ.md
  sections 2 to 4, prop_econ/vec.py (day step, tier caps, simulate_xfas). free -m: 11.0 GB available.
- 19:36-19:37 wrote e29_basket.py and e29_run.py. Cut by the usage limit at about 19:38; the laptop rebooted at
  20:42 (lead). Nothing of mine was running.

## Session 2 (resumed 21:55 on the lead's reduced, ordered scope)
- 21:55 lead's order: (1) finish code, test (a) only, stop if it fails; (2) limit cells by BISECTION ONLY, every
  threshold marked "bisection, unconfirmed", B0 both settings, B1-B4 rho 0 and 0.5, then 0.25 and 0.75, with the
  reporting points and cost per attempt; (3) the extended alone break-evens, the market case (B0 and best basket),
  the Topstep B3 sensitivity; (4) E29_cells.json and E29_tables.md from what exists, missing cells "not run";
  (5) grid confirmation only if all else is done before 22:40; return at 22:40 at the latest.
- 21:55 added the bisection-only mode (E29_MODE=bisection, the default; the mode is part of every cell's spec and
  fingerprint, so confirmed cells would never be mixed with unconfirmed ones) and the lead's task order; repo root on
  sys.path (prop_econ import). free -m: 8.85 GB available.
- 21:56-21:57 tests: `OMP_NUM_THREADS=1 ... nice -n 10 uv run pytest -q -p no:cacheprovider
  reports/stage_e29_briefs/work/basket/test_e29_basket.py` -> 9 passed in 70.3 s (test_e29_basket.out).
  (a) 5 firm cases: B0 setting (ii), bisection, reproduces E.28's QM mu*_lim, mu*_mkt, mu10K and cost per attempt
  exactly at all five firms, and every stored on-lattice evaluation of pairs/<firm>__QM.json that the B0 search
  visits (ev, se, ev_ex_api, p10k) bit for bit, the threshold point included; plus B0's (M, S) equals E.28's
  DayLaw(m, s) bit for bit at 6 grid points x 2 cases x 5 firms. (c) law identity (2 tests: zero-trade member, rho
  limits of S). (d) trade split (7, 7, 6) and lots (B3 2.1). Not written: (b) Monte Carlo check of (M, S), (e) the
  B3 sensitivity wrapper reduction test.
- 21:57:54 first launch failed in the scheduler's status message (KeyError 'checks' in bisection mode, after the
  first cell finished; nothing written). Fixed the message.
- 21:59:33 full run launched: setsid nohup, nice 10, OMP/MKL/OPENBLAS threads 1, 6 workers, log run_main.log,
  scheduler PID 61388 (uv wrapper 61312, bash 61311). Resumable: cells/<id>.json, skipped when the fingerprint
  (code sha + E.28 files + declaration + cell spec) matches. No probe run beforehand (lead's time budget); the
  first cells' runtimes in run_main.log serve as the timing probe.

## E.28 files imported read-only (sha256, first 16 hex)
A3_funnel.py 9b0183b5cc9268d5, A3_models.py f9389bf89c0d13c7, A3_run.py 49c436beeaff3311, A3_inputs.py
0794bc06e242dbe8, A3_gridcheck.py 9a0a4eb6116bbbcd, A3_inputs.json f54246dfe86d87c4, A3_econ.json 6140c7d652370b47.
Full values are written into E29_cells.json (e28_sha256). Not edited (mtimes unchanged, 10:29-16:05); prop_econ/
unchanged (git status clean for it).

## Choices
- C1 Cache key: E.28 cached by d = mu - c for one pair; here evaluations are cached by the law itself,
  (round(M, 9), round(S, 9)) (a pair of laws for the B3 sensitivity). The funnel call is E.28's unchanged.
- C2 Every member term of M is computed as T_i * (mu_i - c_i) * v_i, E.28's operation order, and S = sqrt(sum
  s_i^2 + 2 rho sum s_i s_j); for B0 this equals E.28's (m, s) bit for bit (tested), so B0 = E.28's QM pair.
- C3 Bisection-only mode (lead, 21:55): no A3_gridcheck pass and no per-cell from-scratch recomputation; every
  threshold carries status "bisection, unconfirmed". E.28 found EV non-monotone at low mu for some pairs, so an
  unconfirmed threshold can be too high if a lower grid point also has EV >= 0.
- C4 Limit-case searches compute P10K at every bisection point (E.28's PairEval did); market cells compute EV only
  (no P10K is reported in the market case), which changes no EV.
- C5 Per-attempt pass rate = E.28's p_pass_attempt (passes / attempts over the 20,000 attempt paths of the pool).
- C6 Market case for the best basket is run at every rho (a cell is firm x basket x rho x setting).
- C7 Extended alone break-evens: run for every (firm, member) whose E.28 mu*_lim or mu*_mkt is "> 4": the five of
  section 5 plus MNQ at Topstep and Tradeify (market "> 4" in E.28; needed by section 6's market setting (i) if B4
  is a best basket there). Market thresholds by bisection on their own 0-12 lattice (E.28 walked from a guess).
- C8 Best basket: "> 4" or "n/a" counts as +inf in the section 6 key (k*_i at rho 0.5, then mu*_QM(ii) at 0.5,
  then basket order).
- C9 B3 sensitivity: the 2-lot tier = days whose E.19 tier cap (tier_cap_vec on the previous close; Topstep tiers
  balance <= 1,500: 2, <= 2,000: 3, else 5) is below the basket's 2.1 lots. The Combine is unaffected (5-lot cap).
  The primary-form share of Topstep B3 funded path-days at the 2-lot tier is computed in the primary Topstep B3
  limit cells at the threshold and reporting points (wrapper run with law B = law A, i.e. the primary simulation).

## Progress (session 2, continued)
- 22:00:21-22:00:50 first five cells (B0 setting ii, limit): 47-76 s each, 15-18 evaluations each (the timing
  probe): mu*_QM 0.32 / 0.33 / 0.43 / 0.35 / 0.72 and mu10K 0.54 / 0.77 / 0.75 / 0.9 / 1.06 at Topstep / Lucid /
  Tradeify / MFFU / Bulenox = E.28's values. At about 60 s per limit cell on 6 workers, the 170 limit cells need
  about 30 minutes (to about 22:30), then the alone break-evens, the dependent setting-(i) cells, the market cells
  and the sensitivity (estimate: done about 22:40-22:50).
- 22:01 e29_tables.py written (E29_tables.md from E29_cells.json; mechanical, the declaration's "beats B0" flag
  only; missing cells "not run"); trial collect + tables on the first 10 cells worked. Tests (b) (Monte Carlo of
  (M, S) for B3 at rho 0.5) and (e) (B3 wrapper reduces to prop_econ simulate_xfas when the 2-lot tier is not
  reached: lots 1.1, tiers without a 2-lot level, law B = law A; and differs when it is) appended to
  test_e29_basket.py at 22:02; not run while the 6-process run is going (process cap).
- Rule kept: e29_basket.py and e29_run.py are fingerprinted inputs of the running job and are not edited while it
  runs (an edit would mark every finished cell stale). e29_tables.py is not fingerprinted.
