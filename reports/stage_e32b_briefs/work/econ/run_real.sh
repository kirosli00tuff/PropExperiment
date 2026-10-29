#!/usr/bin/env bash
# Wave C only, when the lead asks: briefs/econ32b.json on the real F3_vol.json and F4_facts_unmasked.json.
#   Pass 1 (EDIR unset): primary, spread1 and E_dir60 for every computed pair.
#   Pass 2 (EDIR=<file with the top-15 "firm|CODE" keys, a JSON list or {"pairs": [...]}>): adds E_dir 30/120/240
#   for those pairs; pass 1's parts are reused unchanged (same job hash), so only the new curves run.
# Optional: ONLY="firm|CODE,..." (e.g. the Layer 1 survivors' pairs), ALLOW_FIRM_MISMATCH=1 (keep E.28's firm
# models although F4's MLL/DLL differ: a lead decision), N (chunks, default 6), WORKERS (default 6).
# Each chunk runs under the shared heavy lock at nice 10; resumable; a refusal (rc 3: firm mismatch) stops here.
# Detach it: setsid nohup reports/stage_e32b_briefs/work/econ/run_real.sh > /dev/null 2>&1 < /dev/null &
set -u
cd /home/kiros-li/Documents/GitHub/PropExperiment
R=reports/stage_e32b_briefs
W=$R/work/econ
LOG=${LOG:-$W/run_real.log}
N=${N:-6}
WORKERS=${WORKERS:-6}
ARGS=(--tag "${TAG:-real}" --f3 "${F3:-$R/F3_vol.json}" --f4 "${F4:-$R/F4_facts_unmasked.json}")
[ -n "${OUT:-}" ] && ARGS+=(--out "$OUT")  # default: briefs/econ32b.json
[ -n "${EDIR:-}" ] && ARGS+=(--edir-pairs "$EDIR")
[ -n "${ONLY:-}" ] && ARGS+=(--only "$ONLY")
[ -n "${ALLOW_FIRM_MISMATCH:-}" ] && ARGS+=(--allow-firm-mismatch)
PY=(env PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 nice -n 10 uv run python "$W/econ32b.py")
echo "start $(TZ=America/Vancouver date) args: ${ARGS[*]}" >> "$LOG"
for i in $(seq 0 $((N-1))); do
  free -m | awk 'NR==2{print "free -m available: "$7" MB"}' >> "$LOG"
  flock "$R/work/heavy.lock" "${PY[@]}" run "${ARGS[@]}" --chunk "$i/$N" --workers "$WORKERS" >> "$LOG" 2>&1
  rc=$?
  echo "chunk $i/$N rc=$rc $(TZ=America/Vancouver date)" >> "$LOG"
  [ "$rc" -ne 0 ] && exit "$rc"
done
"${PY[@]}" collect "${ARGS[@]}" >> "$LOG" 2>&1
echo "collect rc=$? $(TZ=America/Vancouver date)" >> "$LOG"
