#!/usr/bin/env bash
# E.31 canary: fresh quote of the 2-month plan, approve exactly that quote (spec v2 s9, E.28 RS-08), buy.
set -u
cd /home/kiros-li/Documents/GitHub/PropExperiment
P=reports/stage_e31_briefs/work/pilot
echo "chain start $(TZ=America/Vancouver date '+%F %T %Z')"
nice -n 10 uv run python $P/pull31.py --quote --months 2 || { echo "quote rc=$?"; exit 1; }
A=$(uv run python -c "import json;d=json.load(open('$P/runs/quote31.json'));print(repr(float(d.get('sum_usd') or d.get('total_usd'))))") || exit 1
echo "approved (exact fresh quote sum): $A"
nice -n 10 uv run python $P/pull31.py --buy --months 2 --approved-usd "$A"
echo "buy rc=$?"
