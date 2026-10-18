# Briefs: Stage E.24 Fable reviews (worker-xhigh, fable). Independent: you did not write what you review.

Common rules: read files by section (grep, line ranges); keep command output short; run tests with
`uv run pytest -q -p no:cacheprovider <files>`; never modify the code under review (write findings only; the coder
fixes); no network, no broker or data endpoint, no market data, no .env read; never modify any file in
reports/stage_e22_f1_files.sha256 (verify `sha256sum -c --quiet reports/stage_e22_f1_files.sha256`). Label every
finding BLOCKING (wrong result, frozen behaviour changed, a silent failure that can corrupt a ledger or a verdict, a
spec violation), SHOULD FIX (a real defect with limited reach, a missing test of a required case) or NOTE; each with
file:line, the failure scenario (inputs -> wrong output) and the fix you suggest. End with a verdict line: APPROVE,
APPROVE WITH FIXES or BLOCK. Return: the review path, counts per label, the verdict, at most 200 words.

## A2 LoaderReviewer-FableXHigh -> reports/stage_e24_briefs/loader/loader_review.md
Scope: the loader change of reports/stage_e24_briefs/brief_A1_loader.md as reported in
reports/stage_e24_briefs/loader/loader_report.md (pins.md, replay_compare.json). Check: (1) no pinned file changed
(git diff HEAD --stat plus the pin inventory; every freeze line in reports/stage_e24_briefs/start_checks.txt still
holds); (2) the bound is enforced before rows reach memory where the store format allows, and asserted; any
post-load truncation disclosed; (3) the per-unit and per-fill files match E.21's format and content; (4) the replay
equals E.23's recorded discovery numbers (re-run it yourself in your own scratch dir under
/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/c2dca792-060d-4694-91ef-4a6f3f808f1d/scratchpad/
loader_review/, test mode, no marker, only E.23's ext2010 discovery stores, nothing after 2019-04-30, nothing dated
2024-03-01 or later; at nice 10 and only with >= 4 GB available); (5) the E.21, E.23 and base_rules suites pass
unchanged; (6) whether a harness v14 is needed (is any touched file pinned by reports/stage_e2b_harness_freeze.json or
under screening.harness_freeze.HARNESS_DIRS?); (7) whether future multi-day stages will actually use the bounded path
(how a later stage's code reaches it), and what the new module does not cover.

## B5 AdapterReviewer-FableXHigh -> reports/stage_e24_briefs/ibkr/adapter_review.md
Scope: forward/sources_ibkr.py, forward/orders_ibkr.py, forward/daily_f1.py, forward/shadow_f1.json and
tests/test_forward_ibkr_*.py against reports/stage_e24_briefs/brief_B2_ibkr.md, reports/stage_e22_prereg_F1.md
(frozen; sections 5-7) and the facts reports/stage_e24_briefs/facts/ibkr_facts.md + ibkr_factcheck.md. Hunt for silent
failures: contract months and expiry (rolls_f1.json, includeExpired), roll dates (both prices on a switch date), CME
trade date vs local date, the acceptance cutoff, Missing vs SourceUnavailable (a false Missing writes a 0 into E22-F1's
series), reconnects and partial responses, pacing, the warm-up's back-adjustment round trip through
forward.history, the CSV export equal to what the frozen runner reads, the shadow route never touching the E22-F1
ledger (and the byte-identical test really comparing bytes over several days), credentials never logged, ib_async
imported lazily (modules import without it), mock fidelity vs the real ib_async 2.1.0 API (you may run the optional
contract tests with `uv run --frozen --with-requirements forward/requirements_broker.txt pytest -q -p no:cacheprovider
<file>`; no network).

## C4a AlpacaReviewer-FableXHigh -> reports/stage_e24_briefs/alpaca/adapter_review.md
Scope: forward/etf_bars.py, forward/sources_alpaca.py, forward/orders_alpaca.py, forward/shadow_f2.json and their
tests against reports/stage_e24_briefs/brief_C3a_alpaca.md, reports/stage_e24_prereg_F2.md sections 5-7 and the facts
reports/stage_e24_briefs/facts/alpaca_facts.md + alpaca_factcheck.md + fees_facts.md. Hunt for: the total return from
one response (raw vs all, split and distribution days), session dates in America/New_York, the cutoff, Missing vs
SourceUnavailable, pagination and rate limits, paper-only enforcement, fractional longs and whole-share shorts, the
crossing split, the shadow route never touching the E22-F2 ledger, keys never logged, lazy imports, mock fidelity vs
alpaca-py 0.44.0 (optional contract tests under the requirements_broker overlay; no network).

## C4b RegReviewer-FableXHigh -> reports/stage_e24_briefs/f2/reg_review.md
Scope: reports/stage_e24_prereg_F2.md (the registration text, before freeze) and its code forward/strategy_f2.py,
forward/runner_f2.py, forward/evaluate_f2.py, forward/daily_f2.py, forward/config_f2.json, forward/tables_f2.json and
tests/test_forward_f2_*.py. Review adversarially as the registration a stage hinges on: (1) the text is complete and
unambiguous (could two honest implementers produce different ledgers from it?); every constant has a source or a
stated reason; the IDM 2.3293791420997985 recomputes from config_f1.json's frozen correlation without MZL; the FDM
equals E22-F1's; (2) the code equals the text, sentence by sentence (sections 4-8); (3) the P&L in excess of BIL is
correct and conservative (flat book 0; weekend accruals; shorts earn no credit; leverage spread; fees and the daily
rounding up), and the share update q x rawclose(t-1) x (1+r) / rawclose(t) is right on split and distribution days;
(4) the cap and buffer order cannot exceed the cap and cannot churn; shorts toward zero; sign changes; (5) missing
data, declared-closed days, SourceUnavailable writing nothing, ledger chain and re-run semantics mirror E22-F1; (6) the
verdict code equals section 8 with forward/evaluate.py's functions, the 36-month window, no clock-start option; (7)
any look-ahead (a decision at t using data after close(t)); (8) whether E22-F2 changes any frozen E22-F1 file or
behaviour (it must not); (9) the power statement and the expected-behaviour paragraph. Verify the IDM yourself.
