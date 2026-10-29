#!/usr/bin/env bash
# S_mean variant econ (lead, session 3): HG and MNG listed pairs only, own tag and output; queued on the heavy lock.
cd /home/kiros-li/Documents/GitHub/PropExperiment
B=reports/stage_e32b_briefs
LOG=$B/work/econ_smean/run_smean.log
ONLY="lucid|HG,tradeify|HG,bulenox|HG,topstep|MNG"
echo "start $(TZ=America/Vancouver date)" >> "$LOG"
flock "$B/work/heavy.lock" env PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 nice -n 10 uv run python $B/work/econ/econ32b.py run \
  --tag smean --f3 $B/F3_vol.json --f4 $B/work/econ_smean/F4_facts_smean.json --only "$ONLY" --workers 8 \
  --out $B/econ32b_smean.json >> "$LOG" 2>&1
echo "smean rc=$? $(TZ=America/Vancouver date)" >> "$LOG"
