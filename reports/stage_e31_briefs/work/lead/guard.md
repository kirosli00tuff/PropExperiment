Start checks (2026-10-22 07:47, reports/stage_e31_briefs/start_checks.txt, script checks.sh), verbatim, with the 1,434
untracked `??` lines and the older trial-registry rows left out (they are in the file):

```
# E.31 checks: start
$ date
Thu Oct 22 07:48:26 PDT 2026
$ git status --short
$ git status --short | wc -l
1434
$ git log --oneline -3
403fd7c docs: V48 (keys, ZM pilot replaces QM) and the Stage E.31 prompt
d485f34 Stage E.29 basket simulation
60eb6b6 Stage E.28 methods brief, ranking and pilot
$ uv run python -m data.holdout status (keys)
top all_ok True unlocks_logged 0 unlock_log_ok True
holdout_2 all_ok True unlocks_logged 0 unlock_log_ok True
MCL all_ok True unlocks_logged 0 unlock_log_ok True
MGC all_ok True unlocks_logged 0 unlock_log_ok True
MHG all_ok True unlocks_logged 0 unlock_log_ok True
NG all_ok True unlocks_logged 0 unlock_log_ok True
$ wc -c REGISTRATION.md
0 REGISTRATION.md
$ uv run python -m screening.harness_freeze verify --expected 2e908c81e01d0aad835b30ab7b95f628182666dd8d76301cdd4ea465bb41edd1
preflight OK: 2e908c81e01d0aad835b30ab7b95f628182666dd8d76301cdd4ea465bb41edd1
$ ledger
36402 ledger/databento_spend.jsonl
034a454b49f2d9c93f3ff8872a5fb322cd351de57a7d73842d08f5d07d94c700
$ ledger total per account (SpendGate.account_spent_usd)
acct-1: spent 118.390020 cap 120.00 headroom 1.609980
acct-2: spent 353.455228 cap 355.38 headroom 1.924772
acct-3: spent 0.000000 cap 125.00 headroom 125.000000
$ uv run python -m screening.trial_registry status (N)
r008-E23: E23 ['E23-MEZFh5', 'E23-MEZNh5', 'E23-MEZBh5', 'E23-H6NQh5', 'E23-H6NQh20'] N 533 -> 538 at 2026-10-17T03:33:45-07:00
.env DATABENTO_API_KEY: absent
.env DATABENTO_API_KEY2: absent
.env DATABENTO_API_KEY3: non-empty
```

End checks (2026-10-23, reports/stage_e31_briefs/end_checks.txt), verbatim, same omissions:

```
# E.31 checks: end
$ date
Fri Oct 23 13:14:40 PDT 2026
$ git status --short
 M ledger/databento_spend.jsonl
$ git status --short | wc -l
1439
$ git log --oneline -3
c8f189e docs: V49 (NQ dropped from the passive candidates; ZL follow-up)
403fd7c docs: V48 (keys, ZM pilot replaces QM) and the Stage E.31 prompt
d485f34 Stage E.29 basket simulation
$ uv run python -m data.holdout status (keys)
top all_ok True unlocks_logged 0 unlock_log_ok True
holdout_2 all_ok True unlocks_logged 0 unlock_log_ok True
MCL all_ok True unlocks_logged 0 unlock_log_ok True
MGC all_ok True unlocks_logged 0 unlock_log_ok True
MHG all_ok True unlocks_logged 0 unlock_log_ok True
NG all_ok True unlocks_logged 0 unlock_log_ok True
$ wc -c REGISTRATION.md
0 REGISTRATION.md
$ uv run python -m screening.harness_freeze verify --expected 2e908c81e01d0aad835b30ab7b95f628182666dd8d76301cdd4ea465bb41edd1
preflight OK: 2e908c81e01d0aad835b30ab7b95f628182666dd8d76301cdd4ea465bb41edd1
$ ledger
37290 ledger/databento_spend.jsonl
42589d7bc02696383cbf5d800ceb922491a4dea90fb2c3d3e2f82da36834c9bb
$ ledger total per account (SpendGate.account_spent_usd)
acct-1: spent 118.390020 cap 120.00 headroom 1.609980
acct-2: spent 353.455228 cap 355.38 headroom 1.924772
acct-3: spent 122.370573 cap 125.00 headroom 2.629427
$ uv run python -m screening.trial_registry status (N)
r008-E23: E23 ['E23-MEZFh5', 'E23-MEZNh5', 'E23-MEZBh5', 'E23-H6NQh5', 'E23-H6NQh20'] N 533 -> 538 at 2026-10-17T03:33:45-07:00
.env DATABENTO_API_KEY: absent
.env DATABENTO_API_KEY2: absent
.env DATABENTO_API_KEY3: non-empty
```
