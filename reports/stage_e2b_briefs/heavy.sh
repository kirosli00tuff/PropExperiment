#!/usr/bin/env bash
# Stage E.2b heavy-job gate: at most two heavy jobs at once across the lead and all workers
# (CLAUDE.md overnight profile). Usage: heavy.sh <command...>. Waits for a free slot, runs at nice 10.
S=/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/0d3e5a56-56e0-4685-ae6b-02b6cf7efbe7/scratchpad
while true; do
  for slot in 1 2; do
    exec {fd}>"$S/heavy_slot_$slot.lock"
    if flock -n "$fd"; then
      echo "[heavy.sh] slot $slot acquired $(TZ=America/Vancouver date +%H:%M:%S) avail_mem_MB=$(free -m | awk '/Mem:/{print $7}')" >&2
      nice -n 10 "$@"; rc=$?
      flock -u "$fd"; exec {fd}>&-
      exit $rc
    fi
    exec {fd}>&-
  done
  sleep 15
done
