#!/bin/bash
# usage: A2_bulenox_log.sh <url> <method> <file-in-pages-dir or -> <note>
P=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/pages/A2_bulenox
u=$(date -u +%Y-%m-%dT%H:%M:%SZ); p=$(TZ=America/Vancouver date '+%Y-%m-%d %H:%M:%S %Z')
if [ "$3" != "-" ] && [ -f "$P/$3" ]; then s=$(sha256sum "$P/$3" | cut -d' ' -f1); else s=-; fi
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$1" "$u" "$p" "$2" "$s" "$3" "$4" >> $P/log.tsv
