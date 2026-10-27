#!/usr/bin/env bash
# usage: M4_log.sh <url> <method> <file> <note>
P=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32_briefs/pages/M4_models
f="$P/$3"
sha=$(sha256sum "$f" | cut -d' ' -f1)
utc=$(date -u +%Y-%m-%dT%H:%M:%SZ); pdt=$(TZ=America/Vancouver date +%Y-%m-%dT%H:%M:%S%z)
printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\n" "$1" "$utc" "$pdt" "$2" "$sha" "$3" "$4" >> $P/log.tsv
echo "logged $3 $(stat -c %s "$f") bytes"
