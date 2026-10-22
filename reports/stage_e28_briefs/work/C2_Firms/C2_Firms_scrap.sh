#!/usr/bin/env bash
# C2_Firms_scrap.sh <get|fetch> <url> <outfile_basename(.md or .html)> [note]
set -u
MODE="$1"; URL="$2"; NAME="$3"; NOTE="${4:-}"
DIR=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/pages/C2_Firms
LOG="$DIR/log.tsv"
OUT="$DIR/$NAME"
timeout 120 scrapling extract "$MODE" "$URL" "$OUT" >/dev/null 2>&1
UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ); PDT=$(TZ=America/Vancouver date +%Y-%m-%dT%H:%M:%S%Z)
SIZE=$(stat -c %s "$OUT" 2>/dev/null || echo 0)
if [ "$SIZE" -lt 500 ]; then
  echo "FAIL scrapling-$MODE size=$SIZE $URL"
  printf '%s\t%s\t%s\tscrapling %s\t-\t-\tFAILED size=%s %s\n' "$URL" "$UTC" "$PDT" "$MODE" "$SIZE" "$NOTE" >> "$LOG"
  rm -f "$OUT"; exit 1
fi
SHA=$(sha256sum "$OUT" | cut -d' ' -f1)
printf '%s\t%s\t%s\tscrapling %s\t%s\t%s\t%s\n' "$URL" "$UTC" "$PDT" "$MODE" "$SHA" "$NAME" "$NOTE" >> "$LOG"
echo "OK $NAME $(wc -l < "$OUT") lines"
