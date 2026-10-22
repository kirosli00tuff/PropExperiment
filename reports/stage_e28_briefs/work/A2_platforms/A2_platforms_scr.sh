#!/bin/bash
# usage: A2_platforms_scr.sh <url> <outfile.md> [note]  (scrapling extract fetch)
P=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/pages/A2_platforms
timeout 150 scrapling extract fetch "$1" "$P/$2" >/dev/null 2>&1
utc=$(date -u '+%FT%TZ'); pdt=$(TZ=America/Vancouver date '+%F %T %Z')
sha=$(sha256sum "$P/$2" | cut -d' ' -f1)
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$1" "$utc" "$pdt" "scrapling fetch" "$sha" "$2" "${3:-}" >> "$P/log.tsv"
wc -c "$P/$2"
