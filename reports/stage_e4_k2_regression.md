# Stage E.4 Task H2: K2 regression replay under the fixed harness

Old harness cf939270f0a00be74aa29a43f0c7de964256411a9cdcebc36f22fd3bdc021a45; replay harness 82ae8536738ca43395f43356840c0b799a7925b7b75ddb4fc1353d3ab7491009.
Records compared: 44; field-by-field match (only harness_sha256 and created_utc may differ): 44/44.
Trip lists that sum to their record's daily series (and carry its sha256): 44/44.
Cluster record (tiers, members, refusals): MATCH.
Tiers in the replay: ['B'] over 44 members.

| Trial | Record vs E.3 | n_trips | mean ticks | daily t | coverage | labels | trip list |
|---|---|---|---|---|---|---|---|
| K2-aucpost-01_TN | MATCH | 15 | -0.087149 | -0.811638 | TN:0.9622 | - | ok |
| K2-aucpost-01_UB | MATCH | 15 | -0.199420 | -0.819896 | UB:0.9662 | - | ok |
| K2-aucpost-01_ZB | MATCH | 15 | -0.162545 | -0.825379 | ZB:0.9734 | - | ok |
| K2-aucpost-01_ZF | MATCH | 10 | -0.060388 | -0.774136 | ZF:0.9947 | - | ok |
| K2-aucpost-01_ZN | MATCH | 15 | -0.165683 | -2.02052 | ZN:0.9981 | - | ok |
| K2-aucpost-01_ZT | MATCH | 13 | 0.050036 | 0.839348 | ZT:0.9725 | - | ok |
| K2-aucpre-01_TN | MATCH | 15 | 0.098338 | 0.397251 | TN:0.9821 | - | ok |
| K2-aucpre-01_UB | MATCH | 15 | 0.085469 | 0.484355 | UB:0.9851 | - | ok |
| K2-aucpre-01_ZB | MATCH | 15 | 0.038935 | 0.271226 | ZB:0.9856 | - | ok |
| K2-aucpre-01_ZF | MATCH | 10 | -0.163853 | -1.360682 | ZF:0.9955 | - | ok |
| K2-aucpre-01_ZN | MATCH | 15 | 0.038363 | 0.226383 | ZN:0.9980 | - | ok |
| K2-aucpre-01_ZT | MATCH | 13 | -0.050003 | -0.523387 | ZT:0.9825 | - | ok |
| K2-cp1-01_TN | MATCH | 270 | -0.890496 | -3.689914 | TN:0.9621 | - | ok |
| K2-cp1-01_UB | MATCH | 276 | -1.076514 | -5.193316 | UB:0.9681 | - | ok |
| K2-cp1-01_ZB | MATCH | 272 | -0.866589 | -5.340199 | ZB:0.9782 | - | ok |
| K2-cp1-01_ZF | MATCH | 275 | -0.314140 | -1.123614 | ZF:0.9954 | - | ok |
| K2-cp1-01_ZN | MATCH | 276 | -0.473393 | -2.554656 | ZN:0.9986 | - | ok |
| K2-cp1-01_ZT | MATCH | 264 | -0.580772 | -2.327964 | ZT:0.9844 | - | ok |
| K2-cp2-01_TN | MATCH | 286 | -0.798365 | -1.293993 | TN:0.9731 | - | ok |
| K2-cp2-01_UB | MATCH | 291 | -0.499264 | -0.914781 | UB:0.9762 | - | ok |
| K2-cp2-01_ZB | MATCH | 285 | -0.608458 | -1.359407 | ZB:0.9800 | - | ok |
| K2-cp2-01_ZF | MATCH | 283 | -0.212673 | -0.342713 | ZF:0.9955 | - | ok |
| K2-cp2-01_ZN | MATCH | 278 | -0.976232 | -1.980745 | ZN:0.9982 | - | ok |
| K2-cp2-01_ZT | MATCH | 265 | -0.713846 | -1.365797 | ZT:0.9789 | - | ok |
| K2-cp3-01_TN | MATCH | 136 | -1.157407 | -1.256501 | TN:0.9752 | - | ok |
| K2-cp3-01_UB | MATCH | 134 | -1.184508 | -1.556922 | UB:0.9785 | - | ok |
| K2-cp3-01_ZB | MATCH | 130 | -1.223253 | -1.784604 | ZB:0.9816 | - | ok |
| K2-cp3-01_ZF | MATCH | 127 | -1.197328 | -1.173917 | ZF:0.9956 | - | ok |
| K2-cp3-01_ZN | MATCH | 131 | -0.635759 | -0.881876 | ZN:0.9982 | - | ok |
| K2-cp3-01_ZT | MATCH | 121 | -0.378649 | -0.428015 | ZT:0.9793 | - | ok |
| K2-fomcpost-01_TN | MATCH | 10 | -0.417183 | -1.937702 | TN:0.9611 | - | ok |
| K2-fomcpost-01_UB | MATCH | 10 | -0.280757 | -2.078464 | UB:0.9643 | - | ok |
| K2-fomcpost-01_ZB | MATCH | 10 | -0.253801 | -1.921874 | ZB:0.9737 | - | ok |
| K2-fomcpost-01_ZF | MATCH | 10 | -0.571837 | -1.989312 | ZF:0.9951 | - | ok |
| K2-fomcpost-01_ZN | MATCH | 10 | -0.390256 | -1.99223 | ZN:0.9985 | - | ok |
| K2-fomcpost-01_ZT | MATCH | 10 | -0.565148 | -2.05579 | ZT:0.9794 | - | ok |
| K2-monthend-01_TN | MATCH | 18 | -0.114255 | -0.525601 | TN:0.9732 | - | ok |
| K2-monthend-01_UB | MATCH | 18 | -0.434085 | -1.415467 | UB:0.9764 | - | ok |
| K2-monthend-01_ZB | MATCH | 18 | -0.226174 | -1.161352 | ZB:0.9803 | - | ok |
| K2-monthend-01_ZF | MATCH | 18 | -0.031390 | -0.125874 | ZF:0.9956 | - | ok |
| K2-monthend-01_ZN | MATCH | 18 | -0.087075 | -0.482553 | ZN:0.9982 | - | ok |
| K2-monthend-01_ZT | MATCH | 18 | 0.008744 | 0.043508 | ZT:0.9790 | - | ok |
| K2-predrift-01_ZB | MATCH | 11 | -0.070798 | -1.241194 | ZB:0.9921 | - | ok |
| K2-predrift-01_ZN | MATCH | 12 | -0.030205 | -0.428879 | ZN:0.9976 | - | ok |

## How it was run (lead, Task H2)

- Manifest rebuilt in place, uncommitted, at 02:30 PDT: sha256 82ae8536738ca43395f43356840c0b799a7925b7b75ddb4fc1353d3ab7491009
  (1,034 files). Against cf939270: changed screening/stage_e_runner.py and tests/test_stage_e_runner.py; added
  tests/_stage_e_launch.py and tests/test_stage_e_runner_launch.py; nothing removed; `categories` differs only by the two
  added files. `verify --expected 82ae8536...` printed `preflight OK`. The preflight has no test mode, so this in-place
  build was the scratch manifest (open choice in the return).
- Command (the E.3 command through `python -m`, the path C-1 broke), 02:31:16-02:37:02 PDT, exit 0:
  `PYTHONPYCACHEPREFIX=<fresh> nice -n 10 uv run python -m screening.stage_e_runner --harness-sha256 82ae8536...
  --cluster K2 --all --window research --research-root data/processed --step2-root data/processed_step2 --out-dir
  reports/stage_e4_k2_regression`. Output: `K2 research: 44 members, 0 refused`. 89 files: 44 records, 44 trip lists,
  the cluster record.
- Power field under `python -m`, all 44 records: {('not_run', 'StartRuleMissing'): 44}. So the start-date refusal is now recorded by name on the
  CLI path (in E.3 it escaped and crashed the run).
- Compared by reports/stage_e4_briefs/h2_compare.py (every field of every record and of the cluster record, recursively;
  only harness_sha256 and created_utc skipped; trip nets summed exactly as Fractions per trade date against
  daily_net_usd; trip count against n_trips; the record's sha256 in its trip file).
