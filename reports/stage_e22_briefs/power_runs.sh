#!/usr/bin/env bash
# Stage E.22 A5 power: research re-runs under the harness given (E.5 C2 method), one per cluster, sequential, nice 10.
set -u
cd "$(dirname "$0")/../.."
H=${1:?harness sha256}
SCR=/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/1414530f-7e36-4869-ba6c-9cc19af7d435/scratchpad
for K in K5 K3 K6 K8; do
  k=$(echo $K | tr A-Z a-z)
  P=$(mktemp -d "$SCR/e22pyc.XXXXXX")
  echo "== $K start $(TZ=America/Vancouver date +%H:%M:%S)"
  PYTHONPYCACHEPREFIX=$P nice -n 10 /usr/bin/time -f "rss_kb %M wall %e" uv run python -m screening.stage_e_runner --harness-sha256 "$H" --cluster $K --all --window research --research-root data/processed --step2-root data/processed_step2 --out-dir reports/stage_e22_power_$k > reports/stage_e22_briefs/power_$k.log 2>&1
  echo "$K rc $? end $(TZ=America/Vancouver date +%H:%M:%S)"; tail -2 reports/stage_e22_briefs/power_$k.log
done
