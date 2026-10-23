#!/usr/bin/env bash
# E.31 full buy: fresh quote of the 39-month plan (settled canary requests are skipped), approve exactly that quote (spec v2 s9, E.28 RS-08), buy.
set -u
cd /home/kiros-li/Documents/GitHub/PropExperiment
P=reports/stage_e31_briefs/work/pilot
echo "chain start $(TZ=America/Vancouver date '+%F %T %Z')"
nice -n 10 uv run python $P/pull31.py --quote --months 39 || { echo "quote rc=$?"; exit 1; }
A=$(uv run python -c "import json;d=json.load(open('$P/runs/quote31.json'));print(repr(float(d.get('sum_usd') or d.get('total_usd'))))") || exit 1
echo "approved (exact fresh quote sum): $A"
nice -n 10 uv run python $P/pull31.py --buy --months 39 --approved-usd "$A"
echo "buy rc=$?"
