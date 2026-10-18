#!/usr/bin/env bash
# Stage E.24: full suite detached at nice 10 with a memory watchdog (kills the suite if MemAvailable < 2048 MB).
# Usage: run_suite.sh <out file>. Writes "rc N end HH:MM:SS" or "KILLED low memory ..." as the last line.
set -u
cd "$(dirname "$0")/../.."
OUT=${1:?out file}
echo "start $(TZ=America/Vancouver date '+%H:%M:%S') avail_mb $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)" > "$OUT"
nice -n 10 uv run pytest -q -p no:cacheprovider >> "$OUT" 2>&1 &
PID=$!
MIN=999999
while kill -0 "$PID" 2>/dev/null; do
  A=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
  [ "$A" -lt "$MIN" ] && MIN=$A
  if [ "$A" -lt 2048 ]; then
    pkill -TERM -P "$PID"; kill -TERM "$PID"; sleep 2; pkill -KILL -P "$PID"; kill -KILL "$PID" 2>/dev/null
    echo "KILLED low memory avail_mb $A at $(TZ=America/Vancouver date '+%H:%M:%S')" >> "$OUT"; exit 3
  fi
  sleep 5
done
wait "$PID"; RC=$?
echo "min_avail_mb $MIN" >> "$OUT"
echo "rc $RC end $(TZ=America/Vancouver date '+%H:%M:%S')" >> "$OUT"
