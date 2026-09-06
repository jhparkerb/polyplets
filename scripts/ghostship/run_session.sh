#!/bin/bash
# Ghost Ship session launcher -- cron: 0 4,12,20 * * * (dalby, EDT).
# Protocol: docs/ghostship-preregistration.md (deleted) (repo; NOT in the sandbox).
set -u
BASE="$HOME/var/ghostship"
cd "$BASE" || exit 1

[ -f HALT ] && exit 0
NOW=$(date +%s)
NB=$(cat NOT_BEFORE 2>/dev/null || echo 0)
[ "$NOW" -lt "$NB" ] && exit 0

N=$(grep -c . MANIFEST 2>/dev/null || echo 0)
[ "$N" -ge 14 ] && { echo "run complete" > HALT; exit 0; }
NN=$(printf '%02d' $((N + 1)))
REPORT="sandbox/reports/session-$NN.md"

{
  cat instructions.md
  echo
  echo "You are session $NN of 14. Your report file: reports/session-$NN.md"
  echo
  echo "## Operator bulletin (verbatim)"
  cat BULLETIN.md
} > "logs/prompt-$NN.md"

export CLAUDE_CONFIG_DIR="$BASE/claude-config"
[ -f "$BASE/token" ] && export CLAUDE_CODE_OAUTH_TOKEN="$(cat "$BASE/token")"
cd sandbox
timeout 7200 "$HOME/.local/bin/claude" -p "$(cat "../logs/prompt-$NN.md")" \
  --model claude-fable-5 \
  --output-format json \
  --permission-mode bypassPermissions \
  --disallowedTools "Task,WebFetch,WebSearch" \
  > "../usage/session-$NN.json" 2> "../logs/session-$NN.err"
RC=$?
cd "$BASE"

if [ -f "$REPORT" ]; then
  SHA=$(sha256sum "$REPORT" | cut -d' ' -f1)
  echo "$NN $(date -Is) rc=$RC sha=$SHA" >> MANIFEST
else
  echo "$NN $(date -Is) rc=$RC report-missing" >> logs/failures.log
  FAILS=$(grep -c "^$NN " logs/failures.log)
  # one re-run allowed (next cron slot retries the same NN); second miss counts
  [ "$FAILS" -ge 2 ] && echo "$NN $(date -Is) rc=$RC sha=MISSING" >> MANIFEST
  exit 0
fi

# stop rule: arms at session 6; two consecutive reports with no CLAIM and
# no VERIFY line end the run (checked by grep, never by reading).
DONE=$((N + 1))
if [ "$DONE" -ge 6 ]; then
  Z=0
  for i in $((DONE - 1)) "$DONE"; do
    F=$(printf 'sandbox/reports/session-%02d.md' "$i")
    [ -f "$F" ] && ! grep -q -E '^(CLAIM|VERIFY):' "$F" && Z=$((Z + 1))
  done
  [ "$Z" -eq 2 ] && echo "stop-rule: sessions $((DONE - 1)),$DONE zero-output" > HALT
fi
exit 0
