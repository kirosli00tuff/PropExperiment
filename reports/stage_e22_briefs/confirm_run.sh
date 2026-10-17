#!/usr/bin/env bash
# Stage E.22 Part A (A5): one cluster's confirmation, ONCE, behind its run-once marker, then its verdict.
# Usage: confirm_run.sh CLUSTER   (K5, K3, K6, K8). Run only after the list commit.
# Order: pre-run check (list committed, freeze sha, vehicles, out-dir and marker absent) -> dry run (no bar values,
# no engine, writes nothing) -> the marker run (the harness writes the marker before any bar row) -> the verdict.
# Any failure before the marker stops here with nothing consumed.
set -u
cd "$(dirname "$0")/../.."
K=${1:?cluster}
k=$(echo "$K" | tr A-Z a-z)
H=$(sha256sum reports/stage_e2b_harness_freeze.json | cut -d' ' -f1)
SCR=/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/1414530f-7e36-4869-ba6c-9cc19af7d435/scratchpad
LOG=reports/stage_e22_briefs/confirm_$k.log
UNT=()
[ "$K" = K8 ] && UNT=(--untestable reports/stage_e22_notrun_K8.json)
P=$(mktemp -d "$SCR/e22pyc.XXXXXX")
{
echo "== $K pre-run check $(TZ=America/Vancouver date +%H:%M:%S) harness $H"
PYTHONPATH=. PYTHONPYCACHEPREFIX=$P uv run python reports/stage_e22_briefs/prerun_check.py "$K" || { echo "STOP: pre-run check failed"; exit 2; }
echo "== $K dry run $(TZ=America/Vancouver date +%H:%M:%S)"
PYTHONPYCACHEPREFIX=$P nice -n 10 uv run python -m screening.stage_e_runner --harness-sha256 "$H" --cluster "$K" --all \
  --window confirmation --research-root data/processed --step2-root data/processed_step2 \
  --out-dir "reports/stage_e22_confirm_$k" --dry-run "${UNT[@]}" || { echo "STOP: dry run failed"; exit 2; }
echo "== $K confirmation run (once) start $(TZ=America/Vancouver date +%H:%M:%S)"
PYTHONPYCACHEPREFIX=$P nice -n 10 /usr/bin/time -f "rss_kb %M wall %e" uv run python -m screening.stage_e_runner \
  --harness-sha256 "$H" --cluster "$K" --all --window confirmation --research-root data/processed \
  --step2-root data/processed_step2 --out-dir "reports/stage_e22_confirm_$k" \
  --run-once-marker "reports/stage_e22_${K}_RUN_ONCE.json" --list "reports/stage_e22_${k}_confirmation_list.json" "${UNT[@]}"
rc=$?
echo "== $K confirmation run rc $rc end $(TZ=America/Vancouver date +%H:%M:%S)"
[ $rc -eq 0 ] || exit $rc
echo "== $K verdict $(TZ=America/Vancouver date +%H:%M:%S)"
PYTHONPYCACHEPREFIX=$P uv run python -m screening.stage_e_verdict --harness-sha256 "$H" \
  --list "reports/stage_e22_${k}_confirmation_list.json" --records "reports/stage_e22_confirm_$k" \
  --out "reports/stage_e22_${k}_verdict.json"
echo "== $K verdict rc $? end $(TZ=America/Vancouver date +%H:%M:%S)"
} > "$LOG" 2>&1
rc=$?
tail -5 "$LOG"
exit $rc
