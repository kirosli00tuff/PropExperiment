`uv run pytest -q -p no:cacheprovider`, the full suite, run detached at nice 10 under a memory watchdog
(reports/stage_e29_briefs/run_suite.sh, output pytest_end.out), 10-22 04:20:58 to 04:41:00. Available memory was
8,235 MB at launch, with a minimum of 3,050 MB:

```
FAILED tests/test_h6_rod_run.py::test_the_lead_set_constants_and_the_cli_refuses_a_wrong_freeze_sha
1 failed, 8090 passed, 5 skipped, 3 xfailed, 54 warnings in 1194.76s (0:19:54)
```

The one failure is the known one. It pins harness v12 and has failed by design since v13; E.26's end run had the
same line. No repo code outside reports/, docs/ and progress.md changed during E.29. The E.29 tests live outside
tests/ (OC-9): 11 passed (work/basket/test_e29_basket_final.out).
