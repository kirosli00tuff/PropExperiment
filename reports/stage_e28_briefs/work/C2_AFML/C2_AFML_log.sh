#!/usr/bin/env bash
# usage: C2_AFML_log.sh <url> <file> <method> <note>  (append a log line for an already-saved file)
P=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/pages/C2_AFML
utc=$(date -u +%Y-%m-%dT%H:%M:%SZ); pdt=$(TZ=America/Vancouver date +%Y-%m-%dT%H:%M:%S%Z)
sha=$(sha256sum "$P/$2" | cut -d' ' -f1); sz=$(stat -c%s "$P/$2")
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s (%sB)\n' "$1" "$utc" "$pdt" "$3" "$sha" "$2" "$4" "$sz" >> "$P/log.tsv"
