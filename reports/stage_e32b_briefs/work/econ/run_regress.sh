#!/usr/bin/env bash
# E.32b econ regression against E.28: 4 chunks, each under the shared heavy lock (other workers can take the lock
# between chunks); resumable (one part per pair under parts/regress/). Then REGRESSION.md from the parts.
set -u
cd /home/kiros-li/Documents/GitHub/PropExperiment
W=reports/stage_e32b_briefs/work/econ
L=reports/stage_e32b_briefs/work/heavy.lock
LOG=$W/regress_run.log
N=4
WORKERS=${WORKERS:-6}
for i in $(seq 0 $((N-1))); do
  free -m | awk 'NR==2{print "free -m available: "$7" MB"}' >> "$LOG"
  flock "$L" env PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 nice -n 10 uv run python $W/econ32b.py regress \
      --chunk "$i/$N" --workers "$WORKERS" >> "$LOG" 2>&1
  echo "chunk $i/$N rc=$? $(TZ=America/Vancouver date)" >> "$LOG"
done
env PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 nice -n 10 uv run python $W/econ32b.py regress --collect-only \
    >> "$LOG" 2>&1
echo "collect rc=$? $(TZ=America/Vancouver date)" >> "$LOG"
