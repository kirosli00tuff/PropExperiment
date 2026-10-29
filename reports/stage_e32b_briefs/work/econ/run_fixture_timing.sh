#!/usr/bin/env bash
# Timing run on 5 pairs of the SYNTHETIC fixture (make_fixture.py): 13 jobs (primary + spread1, E_dir60, and
# E_dir 30/120/240 for topstep|MNQ), under the shared heavy lock. Output: fixture/econ32b_fixture.json (not facts).
set -u
cd /home/kiros-li/Documents/GitHub/PropExperiment
W=reports/stage_e32b_briefs/work/econ
LOG=$W/fixture_timing.log
free -m | awk 'NR==2{print "free -m available: "$7" MB"}' >> "$LOG"
flock reports/stage_e32b_briefs/work/heavy.lock env PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 nice -n 10 \
  /usr/bin/time -v uv run python $W/econ32b.py run --tag fixture \
  --f3 $W/fixture/F3_fixture.json --f4 $W/fixture/F4_fixture.json --edir-pairs $W/fixture/edir_fixture.json \
  --only "topstep|MNQ,lucid|GC,bulenox|MCL,mffu|6E,tradeify|ZC" --workers 6 \
  --out $W/fixture/econ32b_fixture.json >> "$LOG" 2>&1
echo "fixture rc=$? $(TZ=America/Vancouver date)" >> "$LOG"
